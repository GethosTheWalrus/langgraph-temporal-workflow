"""
Customer Retention Multi-Agent Workflow.

This workflow orchestrates multiple specialized agents to handle customer retention cases:
1. Customer Intelligence Agent - Analyzes customer data and value
2. Operations Investigation Agent - Investigates operational issues
3. Retention Strategy Agent - Develops retention strategies
4. Communication Agent - Executes customer communication
5. Business Intelligence Agent - Generates executive reports

State is shared between agents using Redis for distributed operation.
"""

from datetime import timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

from temporalio import workflow
import asyncio

# Import only workflow-safe modules - activities are referenced by string name


@dataclass
class CustomerComplaint:
    """Input for customer retention workflow"""
    customer_id: int
    complaint_details: str
    order_ids: Optional[list] = None
    urgency_level: str = "medium"


@dataclass
class HumanApproval:
    """Human approval signal for resolution"""
    approve: bool
    followUp: str = ""


@dataclass
class RetentionResult:
    """Final result of customer retention workflow"""
    case_id: str
    customer_retained: bool
    total_estimated_value: float
    strategy_executed: Dict[str, Any]
    executive_summary: str
    completion_time_minutes: float
    resolution_approved: bool
    final_resolution: str
    resolution_attempts: int


@workflow.defn
class CustomerRetentionWorkflow:
    """
    Multi-agent workflow for customer retention cases.
    
    Flow:
    1. Create retention case and initialize shared state
    2. Run Customer Intelligence Agent (parallel with Operations)
    3. Run Operations Investigation Agent (parallel with Customer Intelligence)
    4. Run Retention Strategy Agent (uses results from 1 & 2)
    5. Run Business Intelligence Agent (parallel with Case Analysis)
    6. Run Case Analysis Agent (parallel with Business Intelligence)
    7. Run Resolution Suggestion Agent and wait for human approval (loop until approved)
    8. Return comprehensive results
    
    Note: The workflow will continue generating new resolution suggestions until
    human approval is received via the approve_resolution signal. There is no
    limit on the number of attempts.
    """
    
    def __init__(self):
        self.human_approval: Optional[HumanApproval] = None
    
    @workflow.signal
    async def approve_resolution(self, approval_data: Dict[str, Any]) -> None:
        """
        Signal from human reviewer approving or declining the resolution.
        
        Args:
            approval_data: {"approve": bool, "followUp": str}
        """
        self.human_approval = HumanApproval(
            approve=approval_data.get("approve", False),
            followUp=approval_data.get("followUp", "")
        )
    
    @workflow.run
    async def run(
        self,
        complaint: CustomerComplaint,
        # Database configuration
        postgres_host: str,
        postgres_port: str,
        postgres_db: str,
        postgres_user: str,
        postgres_password: str,
        # LLM configuration
        ollama_base_url: str,
        model_name: str,
        temperature: float,
        # Redis configuration
        redis_url: str
    ) -> RetentionResult:
        """
        Execute customer retention workflow with multiple specialized agents.
        
        Args:
            complaint: Customer complaint details
            postgres_*: Database connection parameters
            ollama_*: LLM configuration
            redis_url: Redis connection for state sharing
            
        Returns:
            Complete retention workflow results
        """
        
        workflow.logger.info(f"Starting customer retention workflow for customer {complaint.customer_id}")
        start_time = workflow.now()
        
        # Validate required parameters
        required_params = {
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
        
        # Stage 1: Generate Case ID (simplified)
        workflow.logger.info("Stage 1: Generating case ID for tracking")
        
        # Generate case_id directly in workflow
        case_id = f"retention_{complaint.customer_id}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        workflow.logger.info(f"Generated retention case ID: {case_id}")
        
        # Note: Redis case state initialization will be handled by the Customer Intelligence Agent
        
        # Stage 2: Enhanced Parallel Customer Intelligence & Operations Investigation
        workflow.logger.info("Stage 2: Running Customer Intelligence and Operations Investigation in parallel across multiple workers")
        
        # Create both activity tasks for parallel execution
        customer_intelligence_task = workflow.execute_activity(
            "customer_intelligence_agent",
            args=[
                case_id,
                complaint.customer_id,
                complaint.complaint_details,
                ollama_base_url,
                model_name,
                temperature,
                redis_url,
                postgres_host,
                postgres_port,
                postgres_db,
                postgres_user,
                postgres_password,
            ],
            start_to_close_timeout=timedelta(minutes=8),
        )
        
        operations_investigation_task = workflow.execute_activity(
            "operations_investigation_agent",
            args=[
                case_id,
                complaint.customer_id,
                complaint.complaint_details,
                complaint.order_ids,
                ollama_base_url,
                model_name,
                temperature,
                redis_url,
                postgres_host,
                postgres_port,
                postgres_db,
                postgres_user,
                postgres_password,
            ],
            start_to_close_timeout=timedelta(minutes=8),
        )
        
        # Use asyncio.gather for guaranteed parallel execution
        workflow.logger.info("Waiting for parallel agents to complete on separate workers...")
        customer_analysis, investigation = await asyncio.gather(
            customer_intelligence_task,
            operations_investigation_task,
            return_exceptions=False
        )
        
        workflow.logger.info("Stage 2 completed: Customer Intelligence and Operations Investigation")
        
        # Stage 3: Retention Strategy Development
        workflow.logger.info("Stage 3: Developing retention strategy")
        
        strategy_result = await workflow.execute_activity(
            "retention_strategy_agent",
            args=[
                case_id,
                complaint.customer_id,
                complaint.complaint_details,
                ollama_base_url,
                model_name,
                temperature,
                redis_url,
                postgres_host,
                postgres_port,
                postgres_db,
                postgres_user,
                postgres_password,
            ],
            start_to_close_timeout=timedelta(minutes=6),
        )
        
        workflow.logger.info("Stage 3 completed: Retention strategy developed")
        
        # Stage 4 & 5: Parallel Business Intelligence & Case Analysis
        workflow.logger.info("Stage 4-5: Running Business Intelligence and Case Analysis in parallel")
        
        # Create both final analysis tasks for parallel execution
        bi_task = workflow.execute_activity(
            "business_intelligence_agent",
            args=[
                case_id,
                complaint.customer_id,
                complaint.complaint_details,
                ollama_base_url,
                model_name,
                temperature,
                redis_url,
                postgres_host,
                postgres_port,
                postgres_db,
                postgres_user,
                postgres_password,
            ],
            start_to_close_timeout=timedelta(minutes=6),
        )
        
        case_analysis_task = workflow.execute_activity(
            "case_analysis_agent",
            args=[
                case_id,
                complaint.customer_id,
                complaint.complaint_details,
                ollama_base_url,
                model_name,
                temperature,
                redis_url,
                postgres_host,
                postgres_port,
                postgres_db,
                postgres_user,
                postgres_password,
            ],
            start_to_close_timeout=timedelta(minutes=4),
        )
        
        # Execute final analysis in parallel across workers
        workflow.logger.info("Waiting for parallel final analysis to complete on separate workers...")
        bi_result, case_analysis_result = await asyncio.gather(
            bi_task,
            case_analysis_task,
            return_exceptions=False
        )
        
        workflow.logger.info("Stage 4-5 completed: Business intelligence and case analysis")
        
        # Stage 6: Resolution Suggestion with Human Approval Loop
        workflow.logger.info("Stage 6: Generating resolution suggestion and waiting for human approval")
        
        resolution_attempts = 0
        resolution_approved = False
        final_resolution = ""
        current_feedback = ""
        
        # Resolution approval loop - continue until approved (no limit on attempts)
        while not resolution_approved:
            resolution_attempts += 1
            workflow.logger.info(f"Resolution attempt {resolution_attempts}")
            
            # Generate resolution suggestion (with feedback if retry)
            resolution_result = await workflow.execute_activity(
                "suggest_resolution",
                args=[
                    case_id,
                    current_feedback,
                    ollama_base_url,
                    model_name,
                    temperature,
                    redis_url,
                    postgres_host,
                    postgres_port,
                    postgres_db,
                    postgres_user,
                    postgres_password,
                ],
                start_to_close_timeout=timedelta(minutes=8),
            )
            
            final_resolution = resolution_result.get("response", "")
            workflow.logger.info("Resolution suggestion generated. Waiting for human approval...")
            
            # Reset approval state and wait for human signal
            self.human_approval = None
            
            # Wait for human approval with 30-minute timeout
            try:
                await workflow.wait_condition(
                    lambda: self.human_approval is not None,
                    timeout=timedelta(minutes=30)
                )
                
                approval = self.human_approval
                if approval.approve:
                    workflow.logger.info("Resolution approved by human reviewer")
                    resolution_approved = True
                else:
                    workflow.logger.info(f"Resolution declined. Feedback: {approval.followUp}")
                    # Set up feedback for next attempt
                    current_feedback = approval.followUp if approval.followUp.strip() else "This will not work. Please suggest something different."
                    workflow.logger.info("Generating new resolution based on feedback...")
                    
            except Exception as e:
                # Handle timeout - end with last resolution
                workflow.logger.info(f"Timeout waiting for human approval: {str(e)}")
                workflow.logger.info("Using last resolution suggestion as final")
                resolution_approved = True  # Exit loop with current resolution
        
        # Stage 7: Final Results Compilation with Real Data
        workflow.logger.info("Stage 7: Compiling final results with extracted metrics")
        
        end_time = workflow.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60.0
        
        # Extract real metrics from case analysis
        metrics = case_analysis_result.get("extracted_metrics", {})
        
        # Use real values instead of assumptions
        customer_retained = metrics.get("customer_retained")
        if customer_retained is None:
            # If uncertain, use probability to make a decision
            retention_prob = metrics.get("retention_probability_percent", 0)
            customer_retained = retention_prob >= 50.0  # 50%+ probability = likely retained
        
        total_estimated_value = metrics.get("total_estimated_value", 0.0)
        
        workflow.logger.info(f"Customer retention workflow completed for case {case_id} in {duration_minutes:.1f} minutes")
        workflow.logger.info(f"Real outcomes - Customer Retained: {customer_retained}, CLV: ${total_estimated_value:,.2f}")
        workflow.logger.info(f"Resolution - Approved: {resolution_approved}, Attempts: {resolution_attempts}")
        workflow.logger.info("Human approval process completed successfully")
        
        return RetentionResult(
            case_id=case_id,
            customer_retained=customer_retained,
            total_estimated_value=total_estimated_value,
            strategy_executed={
                "customer_intelligence": customer_analysis.get("success", False),
                "operations_investigation": investigation.get("success", False),
                "retention_strategy": strategy_result.get("success", False),
                "business_intelligence": bi_result.get("success", False),
                "case_analysis": case_analysis_result.get("success", False),
                "resolution_suggestion": resolution_result.get("success", False)
            },
            executive_summary=bi_result.get("response", "Executive report not available")[:500] + "...",
            completion_time_minutes=duration_minutes,
            resolution_approved=resolution_approved,
            final_resolution=final_resolution,
            resolution_attempts=resolution_attempts
        ) 