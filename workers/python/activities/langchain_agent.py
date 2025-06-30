import logging
from typing import Dict, Any, Optional
from temporalio import activity
import redis.asyncio as redis

# LangChain/LangGraph imports
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver


@activity.defn
async def process_with_agent(
    messages: str,  # Can be a single message or conversation
    thread_id: Optional[str] = None,
    ollama_base_url: str = "http://host.docker.internal:11434",
    model_name: str = "llama3.2",
    temperature: float = 0.0,
    redis_url: str = "redis://redis:6379"
) -> Dict[str, Any]:
    """
    Simple Temporal activity that uses LangGraph agent to process messages.
    LangGraph handles all the conversation state, memory, and complexity for us.
    Uses Redis for distributed state persistence across worker instances.
    
    Args:
        messages: The user's message(s) - can be single query or part of conversation
        thread_id: Optional thread ID for conversation memory (LangGraph manages this)
        ollama_base_url: Ollama server URL
        model_name: Ollama model to use
        temperature: Model temperature
        redis_url: Redis connection URL for persistent state storage
        
    Returns:
        Dict with the agent's response and metadata
    """
    
    try:
        activity.logger.info(f"Processing with agent (model: {model_name}, thread: {thread_id})")
        
        # Set up model
        activity.logger.info(f"Creating Ollama model: {model_name} at {ollama_base_url}")
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature
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
        
        activity.logger.info("Creating LangGraph agent...")
        agent = create_react_agent(model, [], checkpointer=memory)  # No tools needed
        activity.logger.info("LangGraph agent created successfully")
        
        # Configure thread for conversation memory
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        activity.logger.info(f"Invoking agent with config: {config}")
        
        # Let LangGraph handle the conversation - it's that simple!
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": messages}]},
            config=config
        )
        activity.logger.info("Agent invocation completed")
        
        # Extract the response (LangGraph gives us a clean format)
        activity.logger.info(f"Result structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        activity.logger.info(f"Extracted response: {response_text[:100]}...")
        
        return {
            "query": messages,
            "response": response_text,
            "model_used": model_name,
            "thread_id": thread_id,
            "success": True
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in agent activity: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        return {
            "query": messages,
            "response": f"Error: {str(e)}",
            "model_used": model_name,
            "thread_id": thread_id,
            "success": False,
            "error": str(e),
            "traceback": error_details
        } 