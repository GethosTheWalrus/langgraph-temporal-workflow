"""
Case management tools for multi-agent workflows.

These tools provide Redis-based state sharing between agents in distributed systems,
allowing different agents to communicate and share context throughout a workflow.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

import asyncpg
import redis.asyncio as redis
from temporalio import activity
from langchain_core.tools import tool


@dataclass
class RetentionCaseState:
    """Shared state for customer retention workflow"""
    case_id: str
    customer_id: int
    created_at: str
    
    # Agent Results
    customer_profile: Optional[Dict[str, Any]] = None
    investigation: Optional[Dict[str, Any]] = None
    strategy: Optional[Dict[str, Any]] = None
    communication_result: Optional[Dict[str, Any]] = None
    
    # Shared Context
    urgency_level: str = "medium"
    estimated_value: float = 0.0
    priority_escalated: bool = False
    decision_points: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.decision_points is None:
            self.decision_points = []


def create_case_management_tools(redis_url: str):
    """
    Factory function that creates case management tools configured with Redis connection.
    
    Args:
        redis_url: Redis connection URL
    
    Returns:
        List of configured case management tools
    """
    
    @tool
    async def create_retention_case(customer_id: int, complaint_details: str, case_id: Optional[str] = None) -> str:
        """
        Create a new customer retention case and initialize shared state.
        
        Args:
            customer_id: ID of the customer requiring retention
            complaint_details: Description of the customer complaint/issue
            case_id: Optional predefined case ID (if not provided, generates one)
            
        Returns:
            case_id: Unique identifier for this retention case
        """
        try:
            # Use provided case_id or generate unique one
            if not case_id:
                case_id = f"retention_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize case state
            case_state = RetentionCaseState(
                case_id=case_id,
                customer_id=customer_id,
                created_at=datetime.now().isoformat()
            )
            
            # Store in Redis with 24-hour TTL
            redis_client = redis.from_url(redis_url)
            case_key = f"retention_case:{case_id}"
            
            await redis_client.hset(case_key, mapping={
                "state": json.dumps(asdict(case_state), default=str),
                "complaint_details": complaint_details,
                "created_at": case_state.created_at
            })
            await redis_client.expire(case_key, 86400)  # 24 hours
            
            # Log case creation
            activity.logger.info(f"Created retention case {case_id} for customer {customer_id}")
            
            await redis_client.close()
            return case_id
            
        except Exception as e:
            activity.logger.error(f"Error creating retention case: {str(e)}")
            return f"Error creating case: {str(e)}"

    @tool
    async def get_case_state(case_id: str) -> Dict[str, Any]:
        """
        Retrieve current state of a retention case.
        
        Args:
            case_id: ID of the retention case
            
        Returns:
            Current case state as dictionary
        """
        try:
            redis_client = redis.from_url(redis_url)
            case_key = f"retention_case:{case_id}"
            
            case_data = await redis_client.hgetall(case_key)
            if not case_data:
                return {"error": f"Case {case_id} not found. Make sure the Customer Intelligence Agent created the case first using create_retention_case."}
            
            # Parse the state
            state_data = json.loads(case_data.get(b"state", b"{}").decode())
            state_data["complaint_details"] = case_data.get(b"complaint_details", b"").decode()
            
            await redis_client.close()
            return state_data
            
        except Exception as e:
            activity.logger.error(f"Error retrieving case state: {str(e)}")
            return {"error": f"Error retrieving case state: {str(e)}"}

    @tool
    async def update_case_state(case_id: str, agent_name: str, agent_results: Dict[str, Any]) -> str:
        """
        Update case state with results from an agent.
        
        Args:
            case_id: ID of the retention case
            agent_name: Name of the agent providing results ("customer_intelligence", "operations", "strategy", "communication")
            agent_results: Results data from the agent
            
        Returns:
            Success message or error
        """
        try:
            redis_client = redis.from_url(redis_url)
            case_key = f"retention_case:{case_id}"
            
            # Get current state
            case_data = await redis_client.hgetall(case_key)
            if not case_data:
                await redis_client.close()
                return f"Error: Case {case_id} not found"
            
            # Parse current state
            current_state = json.loads(case_data.get(b"state", b"{}").decode())
            
            # Update with agent results
            if agent_name == "customer_intelligence":
                current_state["customer_profile"] = agent_results
            elif agent_name == "operations":
                current_state["investigation"] = agent_results
            elif agent_name == "strategy":
                current_state["strategy"] = agent_results
            elif agent_name == "communication":
                current_state["communication_result"] = agent_results
            else:
                await redis_client.close()
                return f"Error: Unknown agent name '{agent_name}'"
            
            # Store updated state
            await redis_client.hset(case_key, "state", json.dumps(current_state, default=str))
            
            # Log the update
            activity.logger.info(f"Updated case {case_id} with {agent_name} results")
            
            await redis_client.close()
            return f"Successfully updated case {case_id} with {agent_name} results"
            
        except Exception as e:
            activity.logger.error(f"Error updating case state: {str(e)}")
            return f"Error updating case state: {str(e)}"

    @tool
    async def update_case_context(case_id: str, urgency_level: Optional[str] = None, estimated_value: Optional[float] = None, escalated: Optional[bool] = None, decision_point: Optional[str] = None) -> str:
        """
        Update shared context for a retention case.
        
        Args:
            case_id: ID of the retention case
            urgency_level: New urgency level ("low", "medium", "high", "critical")
            estimated_value: Updated customer lifetime value estimate
            escalated: Whether the case has been escalated
            decision_point: Log a decision point or milestone
            
        Returns:
            Success message or error
        """
        try:
            redis_client = redis.from_url(redis_url)
            case_key = f"retention_case:{case_id}"
            
            # Get current state
            case_data = await redis_client.hgetall(case_key)
            if not case_data:
                await redis_client.close()
                return f"Error: Case {case_id} not found"
            
            # Parse current state
            current_state = json.loads(case_data.get(b"state", b"{}").decode())
            
            # Update context fields
            if urgency_level:
                current_state["urgency_level"] = urgency_level
            if estimated_value is not None:
                current_state["estimated_value"] = estimated_value
            if escalated is not None:
                current_state["priority_escalated"] = escalated
            if decision_point:
                if "decision_points" not in current_state:
                    current_state["decision_points"] = []
                current_state["decision_points"].append({
                    "timestamp": datetime.now().isoformat(),
                    "decision": decision_point
                })
            
            # Store updated state
            await redis_client.hset(case_key, "state", json.dumps(current_state, default=str))
            
            activity.logger.info(f"Updated context for case {case_id}")
            
            await redis_client.close()
            return f"Successfully updated context for case {case_id}"
            
        except Exception as e:
            activity.logger.error(f"Error updating case context: {str(e)}")
            return f"Error updating case context: {str(e)}"

    @tool
    async def get_case_summary(case_id: str) -> str:
        """
        Get a comprehensive summary of a retention case for reporting.
        
        Args:
            case_id: ID of the retention case
            
        Returns:
            Formatted case summary
        """
        try:
            # Direct Redis access instead of calling tool function
            redis_client = redis.from_url(redis_url)
            case_key = f"retention_case:{case_id}"
            
            case_data = await redis_client.hgetall(case_key)
            if not case_data:
                await redis_client.close()
                return f"Error: Case {case_id} not found. Make sure the Customer Intelligence Agent created the case first using create_retention_case."
            
            # Parse the state
            try:
                case_state = json.loads(case_data.get(b"state", b"{}").decode())
                case_state["complaint_details"] = case_data.get(b"complaint_details", b"").decode()
            except json.JSONDecodeError as e:
                await redis_client.close()
                return f"Error: Case {case_id} has corrupted data. JSON decode error: {str(e)}"
            
            await redis_client.close()
            
            if not case_state:
                return f"Error: Case {case_id} has empty state data"
            
            # Build summary
            summary = f"Retention Case Summary: {case_id}\n\n"
            summary += f"Customer ID: {case_state.get('customer_id', 'Unknown')}\n"
            summary += f"Created: {case_state.get('created_at', 'Unknown')}\n"
            summary += f"Urgency: {case_state.get('urgency_level', 'medium')}\n"
            summary += f"Estimated Value: ${case_state.get('estimated_value', 0):,.2f}\n"
            summary += f"Escalated: {case_state.get('priority_escalated', False)}\n\n"
            
            # Agent completion status
            summary += "Agent Completion Status:\n"
            summary += f"- Customer Intelligence: {'✓' if case_state.get('customer_profile') else '✗'}\n"
            summary += f"- Operations Investigation: {'✓' if case_state.get('investigation') else '✗'}\n"
            summary += f"- Retention Strategy: {'✓' if case_state.get('strategy') else '✗'}\n"
            summary += f"- Communication: {'✓' if case_state.get('communication_result') else '✗'}\n\n"
            
            # Decision points
            decision_points = case_state.get('decision_points', [])
            if decision_points:
                summary += "Key Decision Points:\n"
                for point in decision_points:
                    summary += f"- {point.get('timestamp', 'Unknown')}: {point.get('decision', 'No details')}\n"
            
            return summary
            
        except Exception as e:
            activity.logger.error(f"Error generating case summary: {str(e)}")
            return f"Error generating summary: {str(e)}"

    @tool
    async def save_retention_case_to_db(
        case_id: str,
        user_id: int,
        support_ticket_id: Optional[int] = None,
        case_status: str = "resolved",
        urgency_level: str = "medium",
        estimated_value: float = 0.0,
        actual_retention_cost: float = 0.0,
        customer_retained: Optional[bool] = None,
        retention_strategy_used: str = "",
        case_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Save the completed retention case to the database for tracking and analytics.
        
        Args:
            case_id: Unique case identifier
            user_id: Customer ID
            support_ticket_id: Related support ticket if any
            case_status: Final case status
            urgency_level: Case urgency level
            estimated_value: Customer lifetime value
            actual_retention_cost: Cost invested in retention
            customer_retained: Whether customer was successfully retained
            retention_strategy_used: Summary of strategy used
            case_notes: Additional case notes
            
        Returns:
            Success/failure status of database save
        """
        try:
            from datetime import datetime
            
            # Extract database connection info from Redis URL pattern
            # This is a simplified approach - in production you'd want proper config
            db_config = {
                'host': 'postgres',  # Docker service name
                'port': 5432,
                'database': 'ecommerce',
                'user': 'user',
                'password': 'password'
            }
            
            conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
            
            try:
                # Insert or update retention case
                query = """
                    INSERT INTO retention_cases (
                        id, user_id, support_ticket_id, case_status, urgency_level,
                        estimated_value, actual_retention_cost, customer_retained,
                        retention_strategy_used, case_notes, resolved_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        case_status = EXCLUDED.case_status,
                        urgency_level = EXCLUDED.urgency_level,
                        estimated_value = EXCLUDED.estimated_value,
                        actual_retention_cost = EXCLUDED.actual_retention_cost,
                        customer_retained = EXCLUDED.customer_retained,
                        retention_strategy_used = EXCLUDED.retention_strategy_used,
                        case_notes = EXCLUDED.case_notes,
                        resolved_at = EXCLUDED.resolved_at,
                        updated_at = EXCLUDED.updated_at
                """
                
                now = datetime.now()
                
                await conn.execute(
                    query,
                    case_id, user_id, support_ticket_id, case_status, urgency_level,
                    estimated_value, actual_retention_cost, customer_retained,
                    retention_strategy_used, case_notes, now, now
                )
                
                activity.logger.info(f"Retention case {case_id} saved to database successfully")
                
                return {
                    "success": True,
                    "case_id": case_id,
                    "message": "Retention case saved to database",
                    "database_updated": True
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            activity.logger.error(f"Error saving retention case to database: {str(e)}")
            return {
                "success": False,
                "case_id": case_id,
                "error": str(e),
                "message": "Failed to save retention case to database"
            }

    return [create_retention_case, get_case_state, update_case_state, update_case_context, get_case_summary, save_retention_case_to_db] 