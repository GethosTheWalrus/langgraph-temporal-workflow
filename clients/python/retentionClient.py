"""
Test client for Customer Retention Workflow.

This client demonstrates how to trigger the multi-agent customer retention workflow
with a customer complaint scenario.
"""

import asyncio
import os
import sys
import traceback
from dataclasses import asdict

from temporalio.client import Client

# Import the workflow classes and data structures
sys.path.append('../../workers/python')
from workflows.customer_retention_workflow import CustomerRetentionWorkflow, CustomerComplaint


async def main():
    # Connect to Temporal server
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Configuration from environment or defaults
    config = {
        # Database configuration (matches docker-compose.yml)
        "postgres_host": os.getenv("POSTGRES_HOST", "app-postgres"),
        "postgres_port": os.getenv("POSTGRES_PORT", "5432"),
        "postgres_db": os.getenv("POSTGRES_DB", "appdb"),
        "postgres_user": os.getenv("POSTGRES_USER", "appuser"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD", "apppassword"),
        
        # LLM configuration (matches docker-compose.yml)
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        "model_name": os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b"),
        "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.0")),
        
        # Redis configuration (matches docker-compose.yml)
        "redis_url": os.getenv("REDIS_URL", "redis://redis:6379"),
    }
    
    print("Customer Retention Workflow Test Client")
    print("=" * 50)
    
    # Realistic customer complaint scenario based on enhanced schema
    # Using David Jones (Customer ID 5) - gaming customer marked as "at_risk" with support ticket
    complaint = CustomerComplaint(
        customer_id=5,  # david_jones - gaming segment, at_risk status, has open support ticket
        complaint_details="""
        Subject: PC Build Delayed - Missing GPU Component - Tournament Deadline

        I am extremely frustrated and disappointed. My custom PC build order has been 
        delayed for over 3 weeks due to a missing RTX 4090 GPU. This was supposed to 
        be delivered for a major gaming tournament I am participating in next week.
        
        Customer Details:
        - Gaming enthusiast segment
        - Previously at-risk customer status
        - Has open urgent support ticket about this issue
        - Prefers SMS communication
        - Has spent $3,200+ historically
        
        The delay is affecting my professional gaming preparation and I'm considering:
        1. Cancelling this order and going with a competitor
        2. Downgrading to an available GPU to get the system faster
        3. Demanding significant compensation for the delays
        
        I've been patient but this delay is now affecting my competitive gaming 
        schedule and potential prize money. As a loyal AMD customer who specifically 
        chose your custom build service, this experience is damaging my trust.
        
        I need immediate action: either expedite the GPU or provide alternatives.
        If not resolved by end of week, I will cancel and leave negative reviews.
        """,
        order_ids=[5],  # David's order that has the GPU delay issue
        urgency_level="urgent"  # Time-sensitive tournament deadline
    )
    
    print(f"Initiating retention workflow for customer {complaint.customer_id}")
    print(f"Complaint: {complaint.complaint_details[:100]}...")
    print(f"Urgency: {complaint.urgency_level}")
    print()
    
    try:
        # Generate workflow ID
        workflow_id = f"customer-retention-{complaint.customer_id}-{int(asyncio.get_event_loop().time())}"
        
        # Start the customer retention workflow (async start)
        handle = await client.start_workflow(
            CustomerRetentionWorkflow.run,
            complaint,
            **config,
            id=workflow_id,
            task_queue="customer-retention-queue",
        )
        
        print(f"🚀 Started workflow {workflow_id}")
        print("⏳ Running multi-agent analysis... This will take several minutes")
        print()
        
        print("📊 Agents will analyze the case:")
        print("   - Customer Intelligence Agent: Calculating CLV and risk assessment")
        print("   - Operations Investigation Agent: Investigating order delays") 
        print("   - Retention Strategy Agent: Developing retention approach")
        print("   - Business Intelligence Agent: Generating executive insights")
        print("   - Case Analysis Agent: Extracting metrics from findings")
        print("   - Resolution Suggestion Agent: Creating action plan")
        print()
        print("⏸️  WORKFLOW WILL PAUSE for human approval of resolution suggestion")
        print("💡 When the resolution is ready, use the Temporal UI to send approval signal:")
        print("   🌐 Temporal UI: http://localhost:8080")
        print(f"   🔍 Workflow ID: {workflow_id}")
        print("   📡 Signal Name: approve_resolution")
        print("   📝 Signal Payload Examples:")
        print('       {"approve": true, "followUp": ""}')
        print('       {"approve": false, "followUp": "Please provide more details..."}')
        print()
        print("🔄 If declined, the workflow will generate a new resolution based on your feedback")
        print("♾️  No limit on approval attempts - workflow continues until approved")
        print()
        print("⏳ Waiting for workflow completion...")
        
        # Get final result
        result = await handle.result()
        
        print()
        print("✅ Customer Retention Workflow Completed!")
        print("=" * 50)
        print(f"Case ID: {result.case_id}")
        print(f"Customer Retained: {result.customer_retained}")
        print(f"Estimated Value: ${result.total_estimated_value:,.2f}")
        print(f"Completion Time: {result.completion_time_minutes:.1f} minutes")
        print(f"Resolution Approved: {result.resolution_approved}")
        print(f"Resolution Attempts: {result.resolution_attempts}")
        if result.resolution_attempts > 1:
            print(f"📝 Required {result.resolution_attempts} iterations to reach approval")
        print()
        
        print("Agent Execution Status:")
        for agent, success in result.strategy_executed.items():
            status = "✅ Completed" if success else "❌ Failed"
            print(f"  - {agent.replace('_', ' ').title()}: {status}")
        
        print()
        print("Executive Summary:")
        print("-" * 30)
        print(result.executive_summary)
        
        print()
        print("Final Resolution Plan:")
        print("-" * 30)
        print(result.final_resolution[:500] + "..." if len(result.final_resolution) > 500 else result.final_resolution)
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 