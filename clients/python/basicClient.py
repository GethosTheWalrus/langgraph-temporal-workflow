import asyncio

from temporalio.client import Client


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("temporal:7233")

    # Execute a workflow using the workflow name as a string
    result = await client.execute_workflow(
        "SayHello", "Python", id="hello-workflow", task_queue="hello-task-queue"
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())