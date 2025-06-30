from datetime import timedelta
from typing import Dict, Any, Optional
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import process_with_agent


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(
        self, 
        query: str, 
        thread_id: Optional[str] = None,
        model_name: str = "llama3.2"
    ) -> Dict[str, Any]:
        """
        Simple workflow that processes a query using the LangChain agent.
        
        Args:
            query: The user's query to process
            thread_id: Optional thread ID for conversation memory
            model_name: Ollama model to use (default: llama3.2)
            
        Returns:
            Dict containing the agent's response and metadata
        """
        
        return await workflow.execute_activity(
            process_with_agent,
            args=[query, thread_id, "http://host.docker.internal:11434", model_name, 0.0, "redis://redis:6379"],
            start_to_close_timeout=timedelta(minutes=2)
        )


 