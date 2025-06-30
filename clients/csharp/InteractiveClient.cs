using System.Text.Json;
using Temporalio.Client;

class InteractiveConversationClient
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("🤖 Interactive Conversation Workflow Demo");
        Console.WriteLine("=" + new string('=', 49));
        
        // Create client connected to Temporal server
        var client = await TemporalClient.ConnectAsync(new("temporal:7233")
        {
            Namespace = "default"
        });

        // Configuration - Generate unique IDs for each workflow instance
        var initialQuery = "You are a chatbot that can answer questions and help with tasks.";
        var timestamp = DateTime.UtcNow.ToString("yyyyMMdd-HHmmss");
        var uuid = Guid.NewGuid().ToString("N")[..8]; // First 8 chars of UUID (no hyphens)
        var sessionId = $"{timestamp}-{uuid}"; // Combined timestamp + UUID
        var threadId = $"thread-{sessionId}";  // Unique Redis conversation thread
        var workflowId = $"interactive-conversation-{sessionId}";  // Unique workflow instance
        // Get configuration from environment variables (with defaults)
        var postgresHost = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "app-postgres";
        var postgresPort = Environment.GetEnvironmentVariable("POSTGRES_PORT") ?? "5432";
        var postgresDb = Environment.GetEnvironmentVariable("POSTGRES_DB") ?? "appdb";
        var postgresUser = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "appuser";
        var postgresPassword = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "apppassword";
        var ollamaBaseUrl = Environment.GetEnvironmentVariable("OLLAMA_BASE_URL") ?? "http://172.17.0.1:11434";
        var modelName = Environment.GetEnvironmentVariable("OLLAMA_MODEL_NAME") ?? "qwen3:8b";
        var temperature = float.Parse(Environment.GetEnvironmentVariable("OLLAMA_TEMPERATURE") ?? "0.0");
        var redisUrl = Environment.GetEnvironmentVariable("REDIS_URL") ?? "redis://redis:6379";
        
        Console.WriteLine($"🔄 Starting workflow with query: {initialQuery}");
        Console.WriteLine($"🧠 Thread ID: {threadId}");
        Console.WriteLine($"🗄️ Database: {postgresUser}@{postgresHost}:{postgresPort}/{postgresDb}");
        Console.WriteLine($"🤖 Model: {modelName}");
        Console.WriteLine($"🌐 Ollama URL: {ollamaBaseUrl}");
        Console.WriteLine($"🌡️ Temperature: {temperature}");
        Console.WriteLine();

        // Start the interactive conversation workflow
        // Pass all configuration as parameters for deterministic execution
        var handle = await client.StartWorkflowAsync(
            "InteractiveConversationWorkflow",
            new object[] { initialQuery, threadId, postgresHost, postgresPort, postgresDb, postgresUser, postgresPassword, ollamaBaseUrl, modelName, temperature, redisUrl },
            new WorkflowOptions
            {
                Id = workflowId,
                TaskQueue = "hello-task-queue"
            });

        Console.WriteLine("✅ Workflow started!");
        Console.WriteLine();
        Console.WriteLine("📋 Workflow Details:");
        Console.WriteLine($"   ID: {workflowId}");
        Console.WriteLine($"   Thread ID: {threadId}");
        Console.WriteLine($"   Task Queue: hello-task-queue");
        Console.WriteLine();
        Console.WriteLine("🎯 The workflow is now waiting for signals!");
        Console.WriteLine("   Use the Temporal UI to send 'user_feedback' signals:");
        Console.WriteLine("   Signal name: user_feedback");
        Console.WriteLine("   Signal payload examples:");
        Console.WriteLine("     Continue: [true, \"your follow-up question here\"]");
        Console.WriteLine("     End:      [false]");
        Console.WriteLine();
        Console.WriteLine("🌐 Temporal UI: http://localhost:8080");
        Console.WriteLine($"   Navigate to: Workflows → {workflowId} → Signal");
        Console.WriteLine();
        Console.WriteLine("⏳ Waiting for workflow to complete (will wait indefinitely for signals)...");
        
        // Wait for workflow to complete and get final result
        try
        {
            var result = await handle.GetResultAsync<dynamic>();
            
            Console.WriteLine("🎉 Conversation Complete!");
            Console.WriteLine("=" + new string('=', 49));
            
            var resultJson = JsonSerializer.Serialize(result, new JsonSerializerOptions 
            { 
                WriteIndented = true 
            });
            var resultDoc = JsonDocument.Parse(resultJson);
            var root = resultDoc.RootElement;
            
            Console.WriteLine("📊 Final Summary:");
            if (root.TryGetProperty("total_turns", out JsonElement turnsElement))
            {
                Console.WriteLine($"   Total turns: {turnsElement.GetInt32()}");
            }
            
            if (root.TryGetProperty("thread_id", out JsonElement threadElement))
            {
                Console.WriteLine($"   Thread ID: {threadElement.GetString()}");
            }
            
            if (root.TryGetProperty("model_used", out JsonElement modelElement))
            {
                Console.WriteLine($"   Model used: {modelElement.GetString()}");
            }
            
            if (root.TryGetProperty("conversation_complete", out JsonElement completeElement))
            {
                Console.WriteLine($"   Conversation complete: {completeElement.GetBoolean()}");
            }
            
            Console.WriteLine("\n🔍 Full result:");
            Console.WriteLine(resultJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error getting workflow result: {ex.Message}");
            Console.WriteLine($"   Details: {ex}");
        }
    }
} 