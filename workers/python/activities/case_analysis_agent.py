"""
Case Analysis Agent Activity.

This agent specializes in analyzing the complete case state and extracting
real outcomes, metrics, and success indicators from the accumulated agent data.
"""

import asyncio
import json
import logging
import re
import traceback
from typing import Dict, Any, Optional

import redis.asyncio as redis
from temporalio import activity
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

# Import specialized tools for this agent
from tools.general import think_step_by_step, analyze_text
from tools.case_management import create_case_management_tools


@activity.defn
async def case_analysis_agent(
    case_id: str,
    customer_id: int,
    complaint_details: str,
    ollama_base_url: str,
    model_name: str,
    temperature: float,
    redis_url: str,
    postgres_host: str,
    postgres_port: str,
    postgres_db: str,
    postgres_user: str,
    postgres_password: str
) -> Dict[str, Any]:
    """
    Case Analysis Agent that extracts real case outcomes and metrics.
    
    Responsibilities:
    - Analyze complete case state from all agents
    - Extract actual customer lifetime value
    - Determine retention probability/success
    - Calculate total strategy investment
    - Provide final case metrics
    
    Args:
        case_id: ID of the retention case
        customer_id: ID of the customer
        complaint_details: Customer complaint description
        ollama_*: LLM configuration
        redis_url: Redis connection for case state
        postgres_*: Database connection parameters
        
    Returns:
        Dictionary with real case outcomes and metrics
    """
    
    # Validate required parameters
    if temperature is None:
        raise ValueError("Missing required parameter: temperature")
    
    try:
        activity.logger.info(f"Case Analysis Agent extracting real outcomes for case {case_id}")
        
        # Set up model
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature,
            timeout=180,
            request_timeout=180
        )
        
        # Set up Redis memory with error handling for concurrent index creation
        redis_client = redis.from_url(redis_url)
        memory = AsyncRedisSaver(redis_client=redis_client)
        try:
            await memory.asetup()
        except Exception as e:
            # Ignore "index already exists" errors - this happens during parallel execution
            if "already exists" in str(e).lower():
                activity.logger.info("Redis indices already exist, continuing...")
            else:
                raise e
        
        # Create specialized toolset for case analysis
        tools = (
            [think_step_by_step, analyze_text] +
            create_case_management_tools(redis_url)  # Focus on case state analysis
        )
        
        activity.logger.info(f"Case Analysis Agent initialized with {len(tools)} tools")
        
        # Create agent
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Specialized prompt for final case analysis
        prompt = f"""
        You are a Case Analysis Agent extracting REAL outcomes and metrics from the completed retention case {case_id}.
        
        CASE CONTEXT:
        - Customer ID: {customer_id}
        - Original Complaint: {complaint_details}
        - Case ID: {case_id}
        
        YOUR MISSION:
        Extract actual case outcomes, metrics, and success indicators from the accumulated agent data instead of making assumptions.
        
        REQUIRED TASKS:
        1. Use get_case_state("{case_id}") to retrieve the COMPLETE case state with all agent results
        2. Use get_case_summary("{case_id}") to get a formatted overview
        
        3. EXTRACT REAL VALUES from the case data:
        
        CUSTOMER LIFETIME VALUE:
        - Find the actual CLV calculated by the Customer Intelligence Agent
        - Extract historical value and projected future value
        - Note the confidence level of the CLV calculation
        
        RETENTION PROBABILITY:
        - Analyze the retention strategy's likelihood of success
        - Consider customer risk score and strategy comprehensiveness
        - Determine if the customer is likely to be retained (high/medium/low probability)
        
        STRATEGY INVESTMENT COST:
        - Extract compensation costs from the retention strategy
        - Include operational fix costs if mentioned
        - Calculate total investment in retention efforts
        
        CASE SUCCESS INDICATORS:
        - Check if all agents completed successfully
        - Assess strategy completeness and feasibility
        - Evaluate if root causes were properly addressed
        
        BUSINESS METRICS:
        - ROI calculation: CLV vs retention investment
        - Payback period for retention investment
        - Risk mitigation value
        
        OUTPUT FORMAT:
        Provide your analysis as a structured response that includes:

        **CUSTOMER VALUE METRICS:**
        - Historical CLV: $X,XXX
        - Projected CLV: $X,XXX
        - CLV Confidence: High/Medium/Low
        
        **RETENTION ASSESSMENT:**
        - Retention Probability: XX% (High/Medium/Low)
        - Risk Level: High/Medium/Low
        - Strategy Quality: Comprehensive/Adequate/Basic
        
        **FINANCIAL ANALYSIS:**
        - Total Strategy Investment: $X,XXX
        - ROI Ratio: X.XX (CLV/Investment)
        - Payback Period: X months
        
        **CASE COMPLETION:**
        - All Agents Successful: Yes/No
        - Strategy Feasibility: High/Medium/Low
        - Root Causes Addressed: Yes/Partially/No
        
        **FINAL RECOMMENDATION:**
        - Customer Likely Retained: Yes/No/Uncertain
        - Business Justification: Strong/Moderate/Weak
        
        Extract ACTUAL numbers and assessments from the case data. Do not make assumptions or use placeholder values.
        If specific metrics are not available, clearly state "Not Available" or "Not Calculated".
        """
        
        # Configure for case analysis thread
        config = {
            "configurable": {"thread_id": f"case_analysis_{case_id}"},
            "recursion_limit": 8
        }
        
        # Execute case analysis
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )
        
        # Extract final response
        ai_message = result["messages"][-1]
        analysis_response = ai_message.content
        
        # Parse the structured response to extract metrics
        def extract_metric(text: str, pattern: str, default: Any = None) -> Any:
            """Extract a metric value from the analysis text"""
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
                return default
            except:
                return default
        
        def extract_dollar_amount(text: str, pattern: str) -> float:
            """Extract dollar amount and convert to float"""
            try:
                value_str = extract_metric(text, pattern, "0")
                if isinstance(value_str, str):
                    # Remove $ and commas, extract numbers
                    numbers = re.findall(r'[\d,]+\.?\d*', value_str.replace('$', '').replace(',', ''))
                    if numbers:
                        return float(numbers[0].replace(',', ''))
                return 0.0
            except:
                return 0.0
        
        def extract_percentage(text: str, pattern: str) -> float:
            """Extract percentage value"""
            try:
                value_str = extract_metric(text, pattern, "0")
                if isinstance(value_str, str):
                    numbers = re.findall(r'\d+\.?\d*', value_str.replace('%', ''))
                    if numbers:
                        return float(numbers[0])
                return 0.0
            except:
                return 0.0
        
        # Extract metrics from the analysis
        historical_clv = extract_dollar_amount(analysis_response, r"Historical CLV:\s*\$?([\d,]+\.?\d*)")
        projected_clv = extract_dollar_amount(analysis_response, r"Projected CLV:\s*\$?([\d,]+\.?\d*)")
        retention_probability = extract_percentage(analysis_response, r"Retention Probability:\s*(\d+\.?\d*)%?")
        strategy_investment = extract_dollar_amount(analysis_response, r"Total Strategy Investment:\s*\$?([\d,]+\.?\d*)")
        roi_ratio = extract_metric(analysis_response, r"ROI Ratio:\s*([\d.]+)", 0.0)
        
        # Extract qualitative assessments
        clv_confidence = extract_metric(analysis_response, r"CLV Confidence:\s*(\w+)", "Unknown")
        retention_assessment = extract_metric(analysis_response, r"Customer Likely Retained:\s*(\w+)", "Uncertain")
        strategy_quality = extract_metric(analysis_response, r"Strategy Quality:\s*([\w/]+)", "Unknown")
        
        # Determine retention success (convert text to boolean)
        customer_retained = None
        if retention_assessment and retention_assessment.lower() in ['yes', 'true', 'likely', 'high']:
            customer_retained = True
        elif retention_assessment and retention_assessment.lower() in ['no', 'false', 'unlikely', 'low']:
            customer_retained = False
        else:
            customer_retained = None  # Uncertain
        
        # Use the higher of historical or projected CLV for total estimated value
        total_estimated_value = max(float(historical_clv or 0), float(projected_clv or 0))
        
        # Extract structured response components (following langchain_agent.py pattern)
        thinking_steps = []
        tool_calls = []
        case_data_retrieved = False
        
        for i, msg in enumerate(result["messages"]):
            # Skip the initial user message
            if i == 0:
                continue
            
            # Extract thinking steps from the conversation
            if hasattr(msg, 'content') and msg.content:
                content = msg.content
                # Look for thinking patterns
                if ('<think>' in content and '</think>' in content):
                    # Extract content between <think> tags
                    think_matches = re.findall(r'<think>(.*?)</think>', content, re.DOTALL)
                    for think_content in think_matches:
                        cleaned_content = think_content.strip()
                        if cleaned_content:
                            # Split long thinking content into logical steps
                            # Split by double newlines (paragraphs) or numbered steps
                            if '\n\n' in cleaned_content:
                                # Split by paragraphs
                                steps = [step.strip() for step in cleaned_content.split('\n\n') if step.strip()]
                                thinking_steps.extend(steps)
                            elif re.search(r'\d+\.\s', cleaned_content):
                                # Split by numbered points
                                steps = re.split(r'\n(?=\d+\.\s)', cleaned_content)
                                thinking_steps.extend([step.strip() for step in steps if step.strip()])
                            else:
                                # Keep as single step if no clear separation
                                thinking_steps.append(cleaned_content)
                elif (content.startswith('I need to') or 
                      content.startswith('Let me') or 
                      content.startswith('First,') or
                      'step' in content.lower()[:50]):
                    # This looks like a reasoning step
                    sentences = [s.strip() for s in content.split('.') if s.strip()]
                    thinking_steps.extend(sentences[:3])  # Limit to avoid too much noise
            
            # Extract tool calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id', '')
                    else:
                        tool_name = getattr(tool_call, 'name', 'unknown')
                        tool_args = getattr(tool_call, 'args', {})
                        tool_id = getattr(tool_call, 'id', '')
                    
                    # Find the corresponding tool result
                    tool_result = None
                    for j in range(i + 1, len(result["messages"])):
                        next_msg = result["messages"][j]
                        if (hasattr(next_msg, 'tool_call_id') and 
                            getattr(next_msg, 'tool_call_id', '') == tool_id):
                            tool_result = getattr(next_msg, 'content', '')
                            break
                    
                    tool_calls.append({
                        'tool_name': tool_name,
                        'arguments': tool_args,
                        'result_summary': tool_result[:200] + '...' if tool_result and len(tool_result) > 200 else tool_result
                    })
                    
                    # Track case data retrieval
                    if tool_name in ['get_case_state', 'get_case_summary']:
                        case_data_retrieved = True
        
        # Clean up the final response (remove any remaining <think> blocks)
        clean_response = re.sub(r'<think>.*?</think>', '', analysis_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Case Analysis Agent completed extraction for case {case_id}")
        activity.logger.info(f"Extracted CLV: ${total_estimated_value:,.2f}, Retention Probability: {retention_probability}%")
        
        return {
            "query": f"Case Analysis for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"case_analysis_{case_id}",
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls,
            "metadata": {
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls) > 0,
                "agent_type": "case_analysis",
                "case_id": case_id,
                "customer_id": customer_id,
                "case_data_retrieved": case_data_retrieved,
                "metrics_extracted": len([k for k, v in {
                    "historical_clv": historical_clv,
                    "projected_clv": projected_clv,
                    "retention_probability": retention_probability,
                    "strategy_investment": strategy_investment
                }.items() if v and float(v or 0) > 0]),
                "extracted_metrics": {
                    "historical_clv": float(historical_clv or 0),
                    "projected_clv": float(projected_clv or 0),
                    "total_estimated_value": total_estimated_value,
                    "retention_probability_percent": float(retention_probability or 0),
                    "strategy_investment": float(strategy_investment or 0),
                    "roi_ratio": float(roi_ratio or 0),
                    "clv_confidence": clv_confidence,
                    "retention_assessment": retention_assessment,
                    "strategy_quality": strategy_quality,
                    "customer_retained": customer_retained
                }
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in Case Analysis Agent: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Case Analysis for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"case_analysis_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Case Analysis Agent failed: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False,
                "agent_type": "case_analysis",
                "case_id": case_id,
                "customer_id": customer_id,
                "case_data_retrieved": False,
                "metrics_extracted": 0,
                "extracted_metrics": {
                    "historical_clv": 0.0,
                    "projected_clv": 0.0,
                    "total_estimated_value": 0.0,
                    "retention_probability_percent": 0.0,
                    "strategy_investment": 0.0,
                    "roi_ratio": 0.0,
                    "clv_confidence": "Unknown",
                    "retention_assessment": "Failed",
                    "strategy_quality": "Unknown",
                    "customer_retained": False
                }
            }
        } 