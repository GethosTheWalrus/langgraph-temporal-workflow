"""
Operations Investigation Agent Activity.

This agent specializes in investigating operational issues, root cause analysis,
and identifying systemic problems affecting customer experience.
"""

import asyncio
import json
import logging
import re
import traceback
from typing import Dict, Any, Optional, List

import redis.asyncio as redis
from temporalio import activity
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

# Import specialized tools for this agent
from tools.general import think_step_by_step, analyze_text
from tools.database import create_database_tools
from tools.case_management import create_case_management_tools


@activity.defn
async def operations_investigation_agent(
    case_id: str,
    customer_id: int,
    complaint_details: str,
    order_ids: Optional[List[int]],
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
    Operations Investigation Agent that analyzes operational issues and root causes.
    
    Responsibilities:
    - Investigate specific order issues
    - Identify operational root causes
    - Analyze systemic problems
    - Update case with investigation findings
    
    Args:
        case_id: ID of the retention case
        customer_id: ID of the customer
        complaint_details: Customer complaint description
        order_ids: List of order IDs to investigate (if any)
        ollama_*: LLM configuration
        redis_url: Redis connection for case state
        postgres_*: Database connection parameters
        
    Returns:
        Dictionary with investigation results and success status
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
        activity.logger.info(f"Operations Investigation Agent processing case {case_id} for customer {customer_id}")
        if order_ids:
            activity.logger.info(f"Investigating specific orders: {order_ids}")
        
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
        
        # Create specialized toolset for operations investigation
        tools = (
            [think_step_by_step, analyze_text] +
            create_database_tools(db_config) +  # Primary tools for data investigation
            create_case_management_tools(redis_url)  # For case state management
        )
        
        activity.logger.info(f"Operations Investigation Agent initialized with {len(tools)} tools")
        
        # Create agent
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Specialized prompt for operations investigation
        order_focus = f"Focus on orders: {order_ids}" if order_ids else "Investigate recent orders for this customer"
        
        prompt = f"""
        You are an Operations Investigation Agent investigating issues for customer {customer_id} in retention case {case_id}.
        
        CUSTOMER COMPLAINT: {complaint_details}
        ORDER INVESTIGATION: {order_focus}
        
        YOUR MISSION:
        Conduct a thorough operational investigation to identify root causes of customer issues and provide actionable solutions.
        
        REQUIRED TASKS:
        1. Use get_case_state("{case_id}") to check current case information
        2. Use query_database to investigate specific order details:
           - If order_ids provided: investigate those specific orders
           - If no order_ids: find and investigate recent orders for customer {customer_id}
        3. Use query_database to analyze order tracking and delivery issues
        4. Use query_database to check for patterns in delays, cancellations, or quality issues
        5. Use analyze_table_relationships if needed to understand data connections
        6. Use update_case_state to save your investigation results under agent_name "operations"
        
        INVESTIGATION FOCUS:
        - Root cause analysis of specific customer issues
        - Identification of systemic operational problems
        - Timeline reconstruction of what went wrong
        - Impact assessment on customer experience
        - Recommended operational fixes and process improvements
        
        SPECIFIC QUERIES TO CONSIDER:
        - Order status and tracking history
        - Shipping and delivery performance
        - Inventory and fulfillment issues
        - Payment and processing problems
        - Communication and notification failures
        
        DELIVERABLES:
        Provide a comprehensive operations investigation report including:
        - Detailed timeline of what happened
        - Root cause analysis (immediate and systemic causes)
        - Operational failures and process breakdowns
        - Recommended immediate fixes
        - Systemic improvements to prevent recurrence
        
        Be thorough and data-driven. Use SQL queries to get specific facts and evidence.
        """
        
        # Configure for operations investigation thread
        config = {
            "configurable": {"thread_id": f"operations_{case_id}"},
            "recursion_limit": 15  # Higher limit for complex investigations
        }
        
        # Execute operations investigation
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )
        
        # Extract final response
        ai_message = result["messages"][-1]
        investigation_response = ai_message.content
        
        # Extract structured response components (following langchain_agent.py pattern)
        thinking_steps = []
        tool_calls = []
        sql_queries_executed = []
        
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
                    
                    # Track SQL queries for investigation reporting
                    if tool_name == 'query_database':
                        sql_queries_executed.append(tool_args.get('sql', 'Unknown query'))
        
        # Clean up the final response (remove any remaining <think> blocks)
        clean_response = re.sub(r'<think>.*?</think>', '', investigation_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Operations Investigation Agent completed investigation for case {case_id}")
        activity.logger.info(f"Executed {len(sql_queries_executed)} database queries during investigation")
        
        return {
            "query": f"Operations Investigation for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"operations_{case_id}",
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls,
            "metadata": {
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls) > 0,
                "agent_type": "operations_investigation",
                "case_id": case_id,
                "customer_id": customer_id,
                "order_ids_investigated": order_ids,
                "total_sql_queries": len(sql_queries_executed),
                "sql_queries_executed": sql_queries_executed
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in Operations Investigation Agent: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Operations Investigation for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"operations_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Operations Investigation Agent failed: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False,
                "agent_type": "operations_investigation",
                "case_id": case_id,
                "customer_id": customer_id,
                "order_ids_investigated": order_ids,
                "total_sql_queries": 0,
                "sql_queries_executed": []
            }
        } 