import logging
import asyncio
from typing import Dict, Any, Optional
from temporalio import activity
import redis.asyncio as redis

# LangChain/LangGraph imports
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

# Import tools from the new tools modules
from tools.general import think_step_by_step, analyze_text
from tools.database import create_database_tools


@activity.defn
async def process_with_agent(
    messages: str,  # Can be a single message or conversation
    thread_id: Optional[str],
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
    Simple Temporal activity that uses LangGraph agent to process messages.
    LangGraph handles all the conversation state, memory, and complexity for us.
    Uses Redis for distributed state persistence across worker instances.
    
    All configuration parameters are required and must be provided by the workflow.
    
    Args:
        messages: The user's message(s) - can be single query or part of conversation
        thread_id: Optional thread ID for conversation memory (LangGraph manages this)
        ollama_base_url: Ollama server URL (required)
        model_name: Ollama model to use (required)
        temperature: Model temperature (required)
        redis_url: Redis connection URL for persistent state storage (required)
        postgres_host: PostgreSQL host (required)
        postgres_port: PostgreSQL port (required)
        postgres_db: PostgreSQL database (required)
        postgres_user: PostgreSQL user (required)
        postgres_password: PostgreSQL password (required)
        
    Returns:
        Dict with the agent's response and metadata
    """
    
    # Validate all required parameters are provided
    required_params = {
        'messages': messages,
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
    
    # Build database configuration from workflow parameters
    db_config = {
        'host': postgres_host,
        'port': postgres_port,
        'database': postgres_db,
        'user': postgres_user,
        'password': postgres_password
    }
    
    try:
        activity.logger.info(f"Processing with agent (model: {model_name}, thread: {thread_id})")
        activity.logger.info(f"Database: {postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}")
        
        # Set up model with timeout handling
        activity.logger.info(f"Creating Ollama model: {model_name} at {ollama_base_url}")
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature,
            timeout=180,  # 3 minute timeout for individual model calls
            request_timeout=180  # 3 minute request timeout
        )
        activity.logger.info("Ollama model created successfully")
        
        # Create agent with Redis-based persistent memory for distributed systems
        activity.logger.info(f"Connecting to Redis at {redis_url}")
        
        # Create Redis client and AsyncRedisSaver
        redis_client = redis.from_url(redis_url)
        memory = AsyncRedisSaver(redis_client=redis_client)
        activity.logger.info("Setting up Redis checkpointer...")
        await memory.asetup()  # Initialize Redis indices for checkpointing (async)
        activity.logger.info("Redis checkpointer setup complete")
        
        activity.logger.info("Creating LangGraph agent with reasoning tools...")
        # Create database tools configured with the provided db_config
        db_tools = create_database_tools(db_config)
        
        # Combine static tools with configured database tools
        tools = [think_step_by_step, analyze_text] + db_tools
        agent = create_react_agent(model, tools, checkpointer=memory)
        activity.logger.info(f"LangGraph agent created successfully with {len(tools)} reasoning tools")
        
        # Configure thread for conversation memory with iteration limit
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        config["recursion_limit"] = 10  # Limit reasoning loops to prevent infinite cycles
        activity.logger.info(f"Invoking agent with config: {config} (max 10 iterations)")
        
        # Let LangGraph handle the conversation - it's that simple!
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": messages}]},
            config=config
        )
        activity.logger.info("Agent invocation completed")
        
        # Extract the response (LangGraph gives us a clean format)
        activity.logger.info(f"Result structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        
        # Extract structured response components
        try:
            # Get the final AI response
            ai_message = result["messages"][-1]
            final_response = ai_message.content
            
            # Extract thinking steps from the conversation
            thinking_steps = []
            tool_calls_data = []
            
            for i, msg in enumerate(result["messages"]):
                # Skip the initial user message
                if i == 0:
                    continue
                
                # Extract thinking steps (usually in <think> tags or standalone reasoning)
                if hasattr(msg, 'content') and msg.content:
                    content = msg.content
                    # Look for thinking patterns
                    if ('<think>' in content and '</think>' in content):
                        # Extract content between <think> tags
                        import re
                        think_matches = re.findall(r'<think>(.*?)</think>', content, re.DOTALL)
                        for think_content in think_matches:
                            thinking_steps.append(think_content.strip())
                    elif (content.startswith('I need to') or 
                          content.startswith('Let me') or 
                          content.startswith('First,') or
                          'step' in content.lower()[:50]):
                        # This looks like a reasoning step
                        # Split into sentences and clean up
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
                        
                        # Structure the tool call data
                        tool_call_entry = {
                            'tool_name': tool_name,
                            'arguments': tool_args,
                            'result_summary': tool_result[:200] + '...' if tool_result and len(tool_result) > 200 else tool_result
                        }
                        tool_calls_data.append(tool_call_entry)
            
            # Clean up the final response (remove any remaining <think> blocks)
            import re
            clean_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL).strip()
            
            # Structure the response as JSON
            structured_response = {
                "response": clean_response,
                "thinking_steps": thinking_steps,
                "tool_calls": tool_calls_data,
                "metadata": {
                    "total_thinking_steps": len(thinking_steps),
                    "total_tool_calls": len(tool_calls_data),
                    "has_reasoning": len(thinking_steps) > 0,
                    "has_tool_usage": len(tool_calls_data) > 0
                }
            }
            
        except Exception as e:
            activity.logger.warning(f"Could not create structured response: {e}")
            # Fallback to original behavior
            ai_message = result["messages"][-1]
            structured_response = {
                "response": ai_message.content,
                "thinking_steps": [],
                "tool_calls": [],
                "metadata": {
                    "total_thinking_steps": 0,
                    "total_tool_calls": 0,
                    "has_reasoning": False,
                    "has_tool_usage": False
                }
            }
        
        activity.logger.info(f"Extracted structured response with {structured_response['metadata']['total_tool_calls']} tool calls")
        
        return {
            "query": messages,
            "model_used": model_name,
            "thread_id": thread_id,
            "success": True,
            "response": structured_response["response"],
            "thinking_steps": structured_response["thinking_steps"],
            "tool_calls": structured_response["tool_calls"],
            "metadata": structured_response["metadata"]
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in agent activity: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        return {
            "query": messages,
            "model_used": model_name,
            "thread_id": thread_id,
            "success": False,
            "error": str(e),
            "traceback": error_details,
            "response": f"Error: {str(e)}",
            "thinking_steps": [],
            "tool_calls": [],
            "metadata": {
                "total_thinking_steps": 0,
                "total_tool_calls": 0,
                "has_reasoning": False,
                "has_tool_usage": False
            }
        } 