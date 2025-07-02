"""
Customer Intelligence Agent Activity.

This agent specializes in customer data analysis, lifetime value calculation,
and risk assessment for retention workflows.
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
from tools.database import create_database_tools
from tools.case_management import create_case_management_tools
from tools.customer_intelligence import create_customer_intelligence_tools


@activity.defn
async def customer_intelligence_agent(
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
    Customer Intelligence Agent that analyzes customer data and value.
    
    Responsibilities:
    - Analyze customer profile and behavior
    - Calculate customer lifetime value
    - Assess churn risk
    - Update case with customer intelligence data
    
    Args:
        case_id: ID of the retention case
        customer_id: ID of the customer to analyze
        complaint_details: Customer complaint description
        ollama_*: LLM configuration
        redis_url: Redis connection for case state
        postgres_*: Database connection parameters
        
    Returns:
        Dictionary with analysis results and success status
    """
    
    # Validate required parameters
    required_params = {
        'postgres_host': postgres_host,
        'postgres_port': postgres_port,
        'postgres_db': postgres_db,
        'postgres_user': postgres_user,
        'postgres_password': postgres_password
    }
    
    missing_params = [name for name, value in required_params.items() if not value]
    if missing_params:
        raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
    
    if temperature is None:
        raise ValueError("Missing required parameter: temperature")
    
    # Build database configuration
    db_config = {
        'host': postgres_host,
        'port': postgres_port,
        'database': postgres_db,
        'user': postgres_user,
        'password': postgres_password
    }
    
    try:
        activity.logger.info(f"Customer Intelligence Agent processing case {case_id} for customer {customer_id}")
        
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
        
        # Create specialized toolset for customer intelligence
        tools = (
            [think_step_by_step, analyze_text] +
            create_customer_intelligence_tools(db_config) +
            create_case_management_tools(redis_url) +
            create_database_tools(db_config)  # For additional queries if needed
        )
        
        activity.logger.info(f"Customer Intelligence Agent initialized with {len(tools)} tools")
        
        # Create agent
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Specialized prompt for customer intelligence
        prompt = f"""
        You are a Customer Intelligence Agent analyzing customer {customer_id} for retention case {case_id}.
        
        CUSTOMER COMPLAINT: {complaint_details}
        
        YOUR MISSION:
        Analyze this customer's value, behavior, and retention priority to help the business make informed retention decisions.
        
        REQUIRED TASKS:
        1. FIRST: Use create_retention_case({customer_id}, "{complaint_details}", "{case_id}") to initialize the case state
        2. Use get_customer_profile({customer_id}) to get comprehensive customer information
        3. Use calculate_customer_lifetime_value({customer_id}) to determine customer value and future potential
        4. Use get_customer_risk_score({customer_id}) to assess churn risk and urgency
        5. Use update_case_context to update estimated_value based on your CLV analysis
        6. Use update_case_state to save your complete analysis under agent_name "customer_intelligence"
        
        ANALYSIS FOCUS:
        - Quantify the financial impact of losing this customer
        - Assess retention priority (high/medium/low value)
        - Identify factors that make this customer worth retaining
        - Provide data-driven recommendations for retention investment
        
        DELIVERABLES:
        Provide a comprehensive customer intelligence report including:
        - Customer value assessment (historical and predicted)
        - Risk analysis and churn indicators
        - Retention priority recommendation
        - Maximum justifiable retention investment
        
        Make data-driven decisions and quantify everything with specific numbers.
        """
        
        # Configure for customer intelligence thread
        config = {
            "configurable": {"thread_id": f"customer_intel_{case_id}"},
            "recursion_limit": 12
        }
        
        # Execute customer intelligence analysis
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )
        
        # Extract final response
        ai_message = result["messages"][-1]
        analysis_response = ai_message.content
        
        # Extract structured response components (following langchain_agent.py pattern)
        thinking_steps = []
        tool_calls = []
        
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
        
        # Clean up the final response (remove any remaining <think> blocks)
        clean_response = re.sub(r'<think>.*?</think>', '', analysis_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Customer Intelligence Agent completed analysis for case {case_id}")
        
        return {
            "query": f"Customer Intelligence Analysis for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"customer_intel_{case_id}",
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls,
            "metadata": {
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls) > 0,
                "agent_type": "customer_intelligence",
                "case_id": case_id,
                "customer_id": customer_id
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in Customer Intelligence Agent: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Customer Intelligence Analysis for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"customer_intel_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Customer Intelligence Agent failed: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False,
                "agent_type": "customer_intelligence",
                "case_id": case_id,
                "customer_id": customer_id
            }
        } 