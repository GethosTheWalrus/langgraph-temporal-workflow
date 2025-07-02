# @@@SNIPSTART python-project-template-run-worker
import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import (
    say_hello, 
    process_with_agent, 
    process_with_retention_agent,
    customer_intelligence_agent,
    operations_investigation_agent,
    retention_strategy_agent,
    business_intelligence_agent,
    case_analysis_agent
)
from activities.resolution_suggestion_agent import suggest_resolution
from workflows import SayHello, AgentWorkflow, InteractiveConversationWorkflow, CustomerRetentionWorkflow


async def main():
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Basic Workflows Worker - handles simple agent workflows and say_hello
    basic_worker = Worker(
        client, 
        task_queue="hello-task-queue", 
        workflows=[SayHello, AgentWorkflow], 
        activities=[say_hello, process_with_agent]
    )
    
    # Customer Retention Worker - handles multi-agent retention workflows
    retention_worker = Worker(
        client, 
        task_queue="customer-retention-queue", 
        workflows=[CustomerRetentionWorkflow], 
        activities=[
            process_with_retention_agent,
            customer_intelligence_agent,
            operations_investigation_agent,
            retention_strategy_agent,
            business_intelligence_agent,
            case_analysis_agent,
            suggest_resolution
        ]
    )
    
    # Interactive Conversation Worker - handles conversational workflows
    interactive_worker = Worker(
        client, 
        task_queue="interactive-conversation-queue", 
        workflows=[InteractiveConversationWorkflow], 
        activities=[process_with_agent]  # Interactive conversations use the main agent
    )
    
    # Run all workers concurrently
    await asyncio.gather(
        basic_worker.run(),
        retention_worker.run(),
        interactive_worker.run()
    )


if __name__ == "__main__":
    asyncio.run(main())