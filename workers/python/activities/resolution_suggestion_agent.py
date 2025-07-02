import asyncio
import json
import re
import traceback
from typing import Dict, Any, List, Optional
from temporalio import activity
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import redis.asyncio as redis

# Import tools for resolution planning
from tools.case_management import create_case_management_tools
from tools.general import think_step_by_step, analyze_text


@activity.defn
async def suggest_resolution(
    case_id: str,
    feedback: str,
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
    Generate actionable resolution suggestions based on comprehensive case analysis.
    Takes feedback from previous attempts to refine suggestions.
    
    Args:
        case_id: The retention case ID
        feedback: Human feedback from previous resolution attempt (empty string for first attempt)
        ollama_base_url: Ollama server URL
        model_name: Model to use for analysis  
        temperature: Model temperature
        redis_url: Redis connection URL
        postgres_host: PostgreSQL host
        postgres_port: PostgreSQL port
        postgres_db: PostgreSQL database
        postgres_user: PostgreSQL username
        postgres_password: PostgreSQL password
        
    Returns:
        Structured resolution suggestion with concrete action items
    """
    
    # Validate required parameters
    required_params = {
        'case_id': case_id,
        'ollama_base_url': ollama_base_url,
        'model_name': model_name,
        'redis_url': redis_url,
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

    try:
        activity.logger.info(f"Starting resolution suggestion for case {case_id}")
        if feedback:
            activity.logger.info(f"Incorporating feedback: {feedback}")
        
        # Set up model
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature,
            timeout=180,
            request_timeout=180
        )
        
        # Create Redis-based memory
        redis_client = redis.from_url(redis_url)
        memory = AsyncRedisSaver(redis_client=redis_client)
        try:
            await memory.asetup()
        except Exception as e:
            if "already exists" in str(e).lower():
                activity.logger.info("Redis indices already exist, continuing...")
            else:
                raise e
        
        # Create resolution agent with case management tools
        tools = (
            [think_step_by_step, analyze_text] +
            create_case_management_tools(redis_url)
        )
        agent = create_react_agent(model, tools, checkpointer=memory)
        
        # Build the prompt for resolution suggestion
        base_prompt = f"""
You are a Resolution Suggestion Agent tasked with creating concrete, actionable resolution plans for customer retention cases.

Your mission: Analyze all available case data and propose a specific, implementable resolution that addresses the customer's concerns and maximizes retention probability.

CASE ID: {case_id}

REQUIRED TASKS:
1. Use get_case_state to retrieve comprehensive case details
2. Use get_case_summary to get formatted case overview
3. Synthesize findings from all previous agents (Customer Intelligence, Operations Investigation, Retention Strategy, Business Intelligence, Case Analysis)
4. Create a specific, actionable resolution plan with:
   - Immediate actions (next 24 hours)
   - Short-term actions (next week)
   - Long-term preventive measures
   - Specific compensation/incentives if applicable
   - Communication strategy
   - Success metrics

RESOLUTION REQUIREMENTS:
- Be specific and actionable (not vague suggestions)
- Include concrete timelines and responsible parties
- Address the root cause identified in operations investigation
- Align with retention strategy recommendations
- Consider financial impact from business intelligence analysis
- Include customer communication plan with specific messaging
- Provide fallback options if primary resolution fails

DELIVERABLES:
Your response must be a comprehensive resolution plan structured as follows:

## RESOLUTION PLAN SUMMARY
Brief overview of the proposed solution

## IMMEDIATE ACTIONS (Next 24 Hours)
- Specific action 1 with timeline and owner
- Specific action 2 with timeline and owner
- etc.

## SHORT-TERM ACTIONS (Next 7 Days)  
- Specific action 1 with timeline and owner
- Specific action 2 with timeline and owner
- etc.

## CUSTOMER COMMUNICATION PLAN
- Communication method and timing
- Key messages to convey
- Compensation/incentives offered
- Follow-up schedule

## LONG-TERM PREVENTIVE MEASURES
- Process improvements to prevent recurrence
- Policy changes needed
- System enhancements

## SUCCESS METRICS
- How to measure resolution success
- Customer satisfaction indicators
- Financial impact tracking

## FALLBACK OPTIONS
- Alternative approaches if primary plan fails
- Escalation procedures
- Contingency measures

Use the tools provided to gather all necessary case information before creating your resolution plan.
"""

        # Add feedback incorporation if this is a retry
        if feedback and feedback.strip():
            base_prompt += f"""

IMPORTANT: This is a retry attempt. The previous resolution suggestion was declined with this feedback:
"{feedback}"

Please take this feedback into account and propose a different approach that addresses the concerns raised.
"""
        else:
            base_prompt += """

This is the first resolution attempt. Create a comprehensive plan based on all available case data.
"""

        # Configure thread for conversation
        thread_id = f"resolution_{case_id}"
        config = {"configurable": {"thread_id": thread_id}}
        config["recursion_limit"] = 15
        
        activity.logger.info(f"Invoking resolution agent with thread_id: {thread_id}")
        
        # Invoke the agent
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": base_prompt}]},
            config=config
        )
        
        activity.logger.info("Resolution agent completed analysis")
        
        # Extract structured response components
        thinking_steps = []
        tool_calls_data = []
        
        for i, msg in enumerate(result["messages"]):
            if i == 0:  # Skip initial user message
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
                    
                    # Find corresponding tool result
                    tool_result = None
                    for j in range(i + 1, len(result["messages"])):
                        next_msg = result["messages"][j]
                        if (hasattr(next_msg, 'tool_call_id') and 
                            getattr(next_msg, 'tool_call_id', '') == tool_id):
                            tool_result = getattr(next_msg, 'content', '')
                            break
                    
                    tool_call_entry = {
                        'tool_name': tool_name,
                        'arguments': tool_args,
                        'result_summary': tool_result[:200] + '...' if tool_result and len(tool_result) > 200 else tool_result
                    }
                    tool_calls_data.append(tool_call_entry)
        
        # Get the final response and clean it
        ai_message = result["messages"][-1]
        final_response = ai_message.content
        clean_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL).strip()
        
        activity.logger.info(f"Resolution suggestion generated with {len(tool_calls_data)} tool calls")
        
        return {
            "query": f"Resolution suggestion for case {case_id}" + (f" (retry with feedback: {feedback})" if feedback else ""),
            "model_used": model_name,
            "thread_id": thread_id,
            "success": True,
            "response": clean_response,
            "thinking_steps": thinking_steps,
            "tool_calls": tool_calls_data,
            "metadata": {
                "agent_type": "resolution_suggestion", 
                "case_id": case_id,
                "is_retry": bool(feedback and feedback.strip()),
                "feedback_incorporated": feedback if feedback else None,
                "total_thinking_steps": len(thinking_steps),
                "total_tool_calls": len(tool_calls_data),
                "has_reasoning": len(thinking_steps) > 0,
                "has_tool_usage": len(tool_calls_data) > 0
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in resolution suggestion: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        
        return {
            "query": f"Resolution suggestion for case {case_id}" + (f" (retry with feedback: {feedback})" if feedback else ""),
            "model_used": model_name,
            "thread_id": f"resolution_{case_id}",
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Error generating resolution suggestion: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "agent_type": "resolution_suggestion",
                "case_id": case_id,
                "is_retry": bool(feedback and feedback.strip()),
                "feedback_incorporated": feedback if feedback else None,
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False
            }
        } 