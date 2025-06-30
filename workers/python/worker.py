# @@@SNIPSTART python-project-template-run-worker
import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello, process_with_agent
from workflows import SayHello, AgentWorkflow, InteractiveConversationWorkflow


async def main():
    client = await Client.connect("temporal:7233", namespace="default")
    # Run the worker
    worker = Worker(
        client, 
        task_queue="hello-task-queue", 
        workflows=[SayHello, AgentWorkflow, InteractiveConversationWorkflow], 
        activities=[say_hello, process_with_agent]
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())