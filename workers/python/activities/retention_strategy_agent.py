"""
Retention Strategy Agent Activity.

This agent specializes in developing personalized customer retention strategies
based on customer intelligence and operational investigation results.
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
async def retention_strategy_agent(
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
    Retention Strategy Agent that develops personalized customer retention strategies.
    
    Responsibilities:
    - Analyze customer intelligence and operational findings
    - Develop comprehensive retention strategy
    - Calculate appropriate compensation and incentives
    - Plan retention execution and success metrics
    
    Args:
        case_id: ID of the retention case
        customer_id: ID of the customer
        complaint_details: Customer complaint description
        ollama_*: LLM configuration
        redis_url: Redis connection for case state
        postgres_*: Database connection parameters
        
    Returns:
        Dictionary with strategy results and success status
    """
    
    # Validate required parameters - minimal validation since we mainly use case management tools
    if temperature is None:
        raise ValueError("Missing required parameter: temperature")
    
    try:
        activity.logger.info(f"Retention Strategy Agent processing case {case_id} for customer {customer_id}")
        
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
        
        # Create specialized toolset for retention strategy
        tools = (
            [think_step_by_step, analyze_text] +
            create_case_management_tools(redis_url)  # Primary focus on case state and strategy
        )
        
        activity.logger.info(f"Retention Strategy Agent initialized with {len(tools)} tools")
        
        # Create agent
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Specialized prompt for retention strategy development
        prompt = f"""
        You are a Retention Strategy Agent developing a comprehensive retention plan for customer {customer_id} in case {case_id}.
        
        ORIGINAL COMPLAINT: {complaint_details}
        
        YOUR MISSION:
        Develop a data-driven, personalized retention strategy that addresses the customer's specific issues while maximizing retention probability and ROI.
        
        REQUIRED TASKS:
        1. Use get_case_state("{case_id}") to review ALL previous agent results:
           - Customer intelligence analysis (value, risk, behavior)
           - Operations investigation findings (root causes, issues)
           - Current case context and priority level
        
        2. Analyze the data to understand:
           - Customer value and retention priority
           - Specific issues that need addressing
           - Root causes that must be fixed
           - Customer's emotional state and expectations
        
        3. Develop a comprehensive retention strategy including:
           - Immediate response actions
           - Compensation/incentive package
           - Process improvements to address root causes
           - Future relationship management plan
           - Success metrics and follow-up schedule
        
        4. Calculate appropriate investment level based on customer value
        
        5. Use update_case_context to escalate urgency if this is a high-value at-risk customer
        
        6. Use update_case_state to save your complete strategy under agent_name "strategy"
        
        STRATEGY COMPONENTS TO INCLUDE:
        
        IMMEDIATE ACTIONS:
        - Acknowledgment and apology approach
        - Immediate issue resolution steps
        - Emergency escalation if needed
        
        COMPENSATION PACKAGE:
        - Financial compensation (refunds, credits, discounts)
        - Service upgrades or premium features
        - Exclusive offers or early access
        - Justification based on customer value
        
        PROCESS IMPROVEMENTS:
        - Fixes to prevent similar issues
        - Communication improvements
        - Quality assurance measures
        
        RELATIONSHIP MANAGEMENT:
        - VIP treatment considerations
        - Dedicated support arrangements
        - Proactive communication schedule
        - Loyalty program enhancements
        
        SUCCESS METRICS:
        - Retention indicators to track
        - Follow-up schedule and checkpoints
        - Long-term relationship goals
        
        DELIVERABLES:
        Provide a comprehensive retention strategy that includes:
        - Executive summary of the strategy
        - Detailed action plan with timelines
        - Compensation package with ROI justification
        - Process improvement recommendations
        - Success metrics and KPIs
        - Total estimated cost vs customer lifetime value
        
        Make data-driven decisions based on the intelligence gathered by other agents.
        """
        
        # Configure for retention strategy thread
        config = {
            "configurable": {"thread_id": f"strategy_{case_id}"},
            "recursion_limit": 12
        }
        
        # Execute retention strategy development
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )
        
        # Extract final response
        ai_message = result["messages"][-1]
        strategy_response = ai_message.content
        
        # Extract structured response components (following langchain_agent.py pattern)
        thinking_steps = []
        tool_calls = []
        case_updates = []
        
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
                    
                    # Track case state updates
                    if tool_name in ['update_case_state', 'update_case_context']:
                        case_updates.append(f"{tool_name}: {tool_args}")
        
        # Clean up the final response (remove any remaining <think> blocks)
        clean_response = re.sub(r'<think>.*?</think>', '', strategy_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Retention Strategy Agent completed strategy development for case {case_id}")
        activity.logger.info(f"Made {len(case_updates)} case state updates")
        
        return {
            "query": f"Retention Strategy Development for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"strategy_{case_id}",
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls,
            "metadata": {
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls) > 0,
                "agent_type": "retention_strategy",
                "case_id": case_id,
                "customer_id": customer_id,
                "total_case_updates": len(case_updates),
                "case_updates_made": case_updates
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in Retention Strategy Agent: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Retention Strategy Development for case {case_id}, customer {customer_id}: {complaint_details}",
            "model_used": model_name,
            "thread_id": f"strategy_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Retention Strategy Agent failed: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False,
                "agent_type": "retention_strategy",
                "case_id": case_id,
                "customer_id": customer_id,
                "total_case_updates": 0,
                "case_updates_made": []
            }
        } 