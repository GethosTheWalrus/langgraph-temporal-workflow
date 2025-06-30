import asyncio
import os

from temporalio.client import Client


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("temporal:7233")

    # Define query and conversation parameters
    query = "Explain what Temporal workflows are and why they're useful"
    thread_id = "python-client-session-1"  # For conversation memory
    
    # Get configuration from environment variables (with defaults)
    postgres_host = os.getenv("POSTGRES_HOST", "app-postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.getenv("POSTGRES_DB", "appdb")
    postgres_user = os.getenv("POSTGRES_USER", "appuser")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "apppassword")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://172.17.0.1:11434")
    model_name = os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b")
    temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

    print(f"🤖 Asking Agent: {query}")
    print(f"🧠 Thread ID: {thread_id}")
    print(f"🗄️ Database: {postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}")
    print(f"🤖 Model: {model_name}")
    print(f"🌐 Ollama URL: {ollama_base_url}")
    print(f"🌡️ Temperature: {temperature}")
    print("🔄 Processing...\n")

    # Execute the Python AgentWorkflow
    # Pass all configuration as parameters for deterministic execution
    result = await client.execute_workflow(
        "AgentWorkflow",
        query, thread_id, postgres_host, postgres_port, postgres_db, postgres_user, postgres_password, ollama_base_url, model_name, temperature, redis_url,
        id="agent-workflow-python",
        task_queue="hello-task-queue"
    )

    print("✅ Agent Response:")
    print("─────────────────────")
    print(f"💬 Response: {result.get('response', 'No response')}")
    print(f"🔧 Model: {result.get('model_used', 'Unknown')}")
    print(f"✅ Success: {result.get('success', False)}")
    print(f"\n🔍 Full Response: {result}")

    # Demo: Send a follow-up message using the same thread_id
    print("\n" + "=" * 50)
    follow_up_query = "Can you give me a practical example of when to use workflows?"
    print(f"🤖 Follow-up: {follow_up_query}")
    print("🔄 Processing...\n")

    follow_up_result = await client.execute_workflow(
        "AgentWorkflow",
        follow_up_query, thread_id, postgres_host, postgres_port, postgres_db, postgres_user, postgres_password, ollama_base_url, model_name, temperature, redis_url,
        id="agent-workflow-followup-python",
        task_queue="hello-task-queue"
    )

    print("✅ Follow-up Response:")
    print("──────────────────────")
    print(f"💬 Response: {follow_up_result.get('response', 'No response')}")


if __name__ == "__main__":
    asyncio.run(main())