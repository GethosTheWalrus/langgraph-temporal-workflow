import logging
from typing import Dict, Any, Optional
from temporalio import activity

# LangChain/LangGraph imports
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


@activity.defn
async def process_with_agent(
    messages: str,  # Can be a single message or conversation
    thread_id: Optional[str] = None,
    ollama_base_url: str = "http://host.docker.internal:11434",
    model_name: str = "llama3.2",
    temperature: float = 0.0
) -> Dict[str, Any]:
    """
    Simple Temporal activity that uses LangGraph agent to process messages.
    LangGraph handles all the conversation state, memory, and complexity for us.
    
    Args:
        messages: The user's message(s) - can be single query or part of conversation
        thread_id: Optional thread ID for conversation memory (LangGraph manages this)
        ollama_base_url: Ollama server URL
        model_name: Ollama model to use
        temperature: Model temperature
        
    Returns:
        Dict with the agent's response and metadata
    """
    
    try:
        activity.logger.info(f"Processing with agent (model: {model_name}, thread: {thread_id})")
        
        # Set up model
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature
        )
        
        # Create agent with memory (LangGraph handles everything)
        memory = MemorySaver()
        agent = create_react_agent(model, [], checkpointer=memory)  # No tools needed
        
        # Configure thread for conversation memory
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        
        # Let LangGraph handle the conversation - it's that simple!
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": messages}]},
            config=config
        )
        
        # Extract the response (LangGraph gives us a clean format)
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        
        return {
            "query": messages,
            "response": response_text,
            "model_used": model_name,
            "thread_id": thread_id,
            "success": True
        }
        
    except Exception as e:
        activity.logger.error(f"Error in agent activity: {str(e)}")
        return {
            "query": messages,
            "response": f"Error: {str(e)}",
            "model_used": model_name,
            "thread_id": thread_id,
            "success": False,
            "error": str(e)
        } 