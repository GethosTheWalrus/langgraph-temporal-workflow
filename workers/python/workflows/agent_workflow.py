from datetime import timedelta
from typing import Dict, Any, Optional
from temporalio import workflow


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(
        self, 
        query: str, 
        thread_id: Optional[str],
        postgres_host: str,
        postgres_port: str,
        postgres_db: str,
        postgres_user: str,
        postgres_password: str,
        ollama_base_url: str,
        model_name: str,
        temperature: float,
        redis_url: str
    ) -> Dict[str, Any]:
        """
        Simple workflow that processes a query using the LangChain agent.
        
        All configuration parameters are required and must be provided by the client.
        
        Args:
            query: The user's query to process
            thread_id: Optional thread ID for conversation memory
            postgres_host: PostgreSQL host (required)
            postgres_port: PostgreSQL port (required)
            postgres_db: PostgreSQL database name (required)
            postgres_user: PostgreSQL username (required)
            postgres_password: PostgreSQL password (required)
            ollama_base_url: Ollama server URL (required)
            model_name: Ollama model to use (required)
            temperature: Model temperature (required)
            redis_url: Redis connection URL (required)
            
        Returns:
            Dict containing the agent's response and metadata
        """
        
        # Validate all required parameters are provided
        required_params = {
            'query': query,
            'postgres_host': postgres_host,
            'postgres_port': postgres_port,
            'postgres_db': postgres_db,
            'postgres_user': postgres_user,
            'postgres_password': postgres_password,
            'ollama_base_url': ollama_base_url,
            'model_name': model_name,
            'redis_url': redis_url
        }
        
        missing_params = [name for name, value in required_params.items() if not value]
        if missing_params:
            raise ValueError(f"Missing required workflow parameters: {', '.join(missing_params)}")
        
        if temperature is None:
            raise ValueError("Missing required workflow parameter: temperature")
        
        return await workflow.execute_activity(
            "process_with_agent",
            args=[query, thread_id, ollama_base_url, model_name, temperature, redis_url, postgres_host, postgres_port, postgres_db, postgres_user, postgres_password],
            start_to_close_timeout=timedelta(minutes=2)
        )


 