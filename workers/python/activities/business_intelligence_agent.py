"""
Business Intelligence Agent Activity.

This agent specializes in generating executive reports, ROI analysis,
and strategic insights based on the complete retention case data.
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
async def business_intelligence_agent(
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
    Business Intelligence Agent that generates executive reports and strategic insights.
    
    Responsibilities:
    - Generate comprehensive executive reports
    - Analyze ROI of retention efforts
    - Identify strategic insights and patterns
    - Provide recommendations for policy improvements
    
    Args:
        case_id: ID of the retention case
        customer_id: ID of the customer
        complaint_details: Customer complaint description
        ollama_*: LLM configuration
        redis_url: Redis connection for case state
        postgres_*: Database connection parameters
        
    Returns:
        Dictionary with BI report results and success status
    """
    
    # Validate required parameters - minimal validation since we mainly use case management tools
    if temperature is None:
        raise ValueError("Missing required parameter: temperature")
    
    try:
        activity.logger.info(f"Business Intelligence Agent processing case {case_id} for customer {customer_id}")
        
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
        
        # Create specialized toolset for business intelligence
        tools = (
            [think_step_by_step, analyze_text] +
            create_case_management_tools(redis_url)  # Focus on case analysis and reporting
        )
        
        activity.logger.info(f"Business Intelligence Agent initialized with {len(tools)} tools")
        
        # Create agent
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Specialized prompt for business intelligence and reporting
        prompt = f"""
        You are a Business Intelligence Agent generating executive reporting and strategic insights for retention case {case_id}.
        
        CASE CONTEXT:
        - Customer ID: {customer_id}
        - Original Complaint: {complaint_details}
        - Case ID: {case_id}
        
        YOUR MISSION:
        Generate a comprehensive executive report that summarizes the retention case, justifies the business investment, and provides strategic insights for leadership.
        
        REQUIRED TASKS:
        1. Use get_case_state("{case_id}") to review the COMPLETE case including all agent results:
           - Customer intelligence analysis (value, CLV, risk assessment)
           - Operations investigation findings (root causes, systemic issues)
           - Retention strategy recommendations (actions, compensation, ROI)
           - Case progression and decision points
        
        2. Use get_case_summary("{case_id}") to get a formatted overview of the case
        
        3. Analyze the business impact and generate insights on:
           - Financial impact of customer loss vs retention cost
           - ROI analysis of the retention strategy
           - Systemic issues that need executive attention
           - Policy recommendations to prevent similar cases
           - Strategic insights for customer experience improvement
        
        4. Generate an executive summary suitable for C-level reporting
        
        EXECUTIVE REPORT STRUCTURE:
        
        EXECUTIVE SUMMARY (2-3 paragraphs):
        - High-level overview of the case and outcome
        - Key business impact and financial considerations
        - Strategic recommendations for leadership
        
        CASE OVERVIEW:
        - Customer profile and value assessment
        - Nature of the complaint and operational issues
        - Timeline of events and case progression
        
        FINANCIAL ANALYSIS:
        - Customer lifetime value (historical and projected)
        - Estimated cost of customer loss
        - Retention strategy investment cost
        - ROI calculation and payback period
        - Cost-benefit analysis
        
        OPERATIONAL INSIGHTS:
        - Root cause analysis summary
        - Systemic issues identified
        - Process improvements implemented
        - Quality assurance recommendations
        
        STRATEGIC RECOMMENDATIONS:
        - Policy changes needed
        - Process improvements for scale
        - Customer experience enhancements
        - Preventive measures
        - Investment priorities
        
        LESSONS LEARNED:
        - Key insights from this case
        - Best practices identified
        - Areas for organizational improvement
        - Future retention strategy refinements
        
        NEXT STEPS:
        - Follow-up actions required
        - Success metrics to track
        - Timeline for implementation
        - Accountability assignments
        
        DELIVERABLES:
        Generate a professional executive report that includes:
        - Data-driven financial analysis
        - Strategic insights and recommendations
        - Actionable next steps for leadership
        - Clear ROI justification for retention investment
        - Systemic improvements to prevent future issues
        
        Write in a professional, executive-level tone suitable for board presentations.
        """
        
        # Configure for business intelligence thread
        config = {
            "configurable": {"thread_id": f"business_intel_{case_id}"},
            "recursion_limit": 10
        }
        
        # Execute business intelligence analysis
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )
        
        # Extract final response
        ai_message = result["messages"][-1]
        report_response = ai_message.content
        
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
        clean_response = re.sub(r'<think>.*?</think>', '', report_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Business Intelligence Agent completed report generation for case {case_id}")
        activity.logger.info(f"Case data retrieved: {case_data_retrieved}")
        
        return {
            "query": f"Business Intelligence Report for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"business_intel_{case_id}",
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls,
            "metadata": {
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls) > 0,
                "agent_type": "business_intelligence",
                "case_id": case_id,
                "customer_id": customer_id,
                "case_data_retrieved": case_data_retrieved
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in Business Intelligence Agent: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Business Intelligence Report for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"business_intel_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Business Intelligence Agent failed: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False,
                "agent_type": "business_intelligence",
                "case_id": case_id,
                "customer_id": customer_id,
                "case_data_retrieved": False
            }
        } 