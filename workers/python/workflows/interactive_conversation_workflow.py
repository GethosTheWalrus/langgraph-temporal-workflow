from typing import List, Dict, Any, Optional
from temporalio import workflow
from dataclasses import dataclass
import asyncio
from datetime import timedelta


@dataclass
class ConversationTurn:
    """Represents one turn in a conversation"""
    query: str
    response: str
    model_used: str
    success: bool
    timestamp: str


@dataclass 
class UserFeedback:
    """User feedback signal containing continuation decision and optional follow-up"""
    continue_conversation: bool
    follow_up_query: Optional[str] = None


@workflow.defn
class InteractiveConversationWorkflow:
    """
    An interactive conversation workflow that runs indefinitely until the user is satisfied.
    
    Flow:
    1. Process initial query with LangGraph agent
    2. Wait for user signal with feedback
    3. If user wants to continue, process follow-up query
    4. Repeat until user indicates they're satisfied
    """
    
    def __init__(self):
        self.continue_conversation = True
        self.latest_user_feedback: Optional[UserFeedback] = None
        self.conversation_history: List[ConversationTurn] = []
    
    @workflow.run
    async def run(
        self, 
        initial_query: str, 
        thread_id: str, 
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
        Start an interactive conversation that continues until user satisfaction.
        
        All configuration parameters are required and must be provided by the client.
        
        Args:
            initial_query: The first question to ask the agent
            thread_id: Thread ID for conversation memory persistence  
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
            Final conversation summary
        """
        
        # Validate all required parameters are provided
        required_params = {
            'initial_query': initial_query,
            'thread_id': thread_id,
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
        
        current_query = initial_query
        
        workflow.logger.info(f"Starting interactive conversation with query: {initial_query}")
        workflow.logger.info(f"Using model: {model_name} at {ollama_base_url}")
        workflow.logger.info(f"Database: {postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}")
        
        # Main conversation loop - continues until user indicates they're done
        while self.continue_conversation:
            workflow.logger.info(f"Processing query: {current_query}")
            
            # Execute the LangGraph agent activity
            result = await workflow.execute_activity(
                "process_with_agent",
                args=[current_query, thread_id, ollama_base_url, model_name, temperature, redis_url, postgres_host, postgres_port, postgres_db, postgres_user, postgres_password],
                start_to_close_timeout=timedelta(minutes=10),  # Allow time for complex reasoning and database queries
            )
            
            # Store this conversation turn
            turn = ConversationTurn(
                query=current_query,
                response=result.get("response", ""),
                model_used=result.get("model_used", model_name),
                success=result.get("success", False),
                timestamp=workflow.now().isoformat()
            )
            self.conversation_history.append(turn)
            
            workflow.logger.info(f"Agent responded. Waiting for user feedback...")
            
            # Wait for user feedback signal (continue or finish) - waits indefinitely
            await workflow.wait_condition(
                lambda: self.latest_user_feedback is not None,
                timeout=timedelta(minutes=30)
            )
            
            # Process user feedback
            feedback = self.latest_user_feedback
            self.latest_user_feedback = None  # Reset for next iteration
            
            if feedback is None:
                workflow.logger.info("No feedback received. Ending conversation.")
                self.continue_conversation = False
                break
                
            workflow.logger.info(f"Processing feedback: continue={feedback.continue_conversation}, query='{feedback.follow_up_query}'")
            
            if not feedback.continue_conversation:
                workflow.logger.info("User indicated they're satisfied. Ending conversation.")
                self.continue_conversation = False
            elif feedback.follow_up_query and feedback.follow_up_query.strip():
                workflow.logger.info(f"User provided follow-up: {feedback.follow_up_query}")
                current_query = feedback.follow_up_query
            else:
                # Default to "explain further" if user wants to continue but provided no specific question
                default_query = "Can you explain that further or provide more details?"
                workflow.logger.info(f"User wants to continue but provided no specific follow-up. Using default: '{default_query}'")
                current_query = default_query
        
        # Return final conversation summary
        return {
            "conversation_complete": True,
            "total_turns": len(self.conversation_history),
            "thread_id": thread_id,
            "model_used": model_name,
            "final_response": self.conversation_history[-1].response if self.conversation_history else "",
            "conversation_history": [
                {
                    "query": turn.query,
                    "response": turn.response,
                    "success": turn.success,
                    "timestamp": turn.timestamp
                }
                for turn in self.conversation_history
            ]
        }
    
    @workflow.signal
    async def user_feedback(self, signal_data) -> None:
        """
        Signal from user indicating whether to continue the conversation.
        
        Args:
            signal_data: Can be either:
                - [bool, str] array: [continue_conversation, follow_up_query]
                - [bool] array: [continue_conversation] (to end conversation)
                - bool: continue_conversation (legacy support)
        """
        workflow.logger.info(f"Received user feedback raw: {signal_data}")
        
        # Parse signal data based on format
        if isinstance(signal_data, list):
            # Array format: [continue, question] or [continue]
            continue_conversation = signal_data[0] if len(signal_data) > 0 else False
            follow_up_query = signal_data[1] if len(signal_data) > 1 else None
        else:
            # Legacy single parameter format
            continue_conversation = signal_data
            follow_up_query = None
            
        workflow.logger.info(f"Parsed feedback: continue={continue_conversation}, follow_up='{follow_up_query}'")
        
        self.latest_user_feedback = UserFeedback(
            continue_conversation=continue_conversation,
            follow_up_query=follow_up_query
        )
    
    @workflow.query
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history"""
        return [
            {
                "query": turn.query,
                "response": turn.response,
                "model_used": turn.model_used,
                "success": turn.success,
                "timestamp": turn.timestamp
            }
            for turn in self.conversation_history
        ]
    
    @workflow.query
    def get_latest_response(self) -> Optional[Dict[str, Any]]:
        """Get the most recent agent response"""
        if self.conversation_history:
            latest = self.conversation_history[-1]
            return {
                "query": latest.query,
                "response": latest.response,
                "model_used": latest.model_used,
                "success": latest.success,
                "timestamp": latest.timestamp
            }
        return None
    
    @workflow.query
    def is_waiting_for_feedback(self) -> bool:
        """Check if workflow is currently waiting for user feedback"""
        return self.continue_conversation and self.latest_user_feedback is None 