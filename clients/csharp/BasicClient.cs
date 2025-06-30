using System.Text.Json;
using Temporalio.Client;

class Program
{
    static async Task Main(string[] args)
    {
        // Create client connected to server at the given address
        var client = await TemporalClient.ConnectAsync(new("temporal:7233")
        {
            Namespace = "default"
        });

        // Define query and conversation parameters
        var query = "Explain what Temporal workflows are and why they're useful";
        var threadId = "csharp-client-session-1";  // For conversation memory
        
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

        Console.WriteLine($"🤖 Asking Agent: {query}");
        Console.WriteLine($"🧠 Thread ID: {threadId}");
        Console.WriteLine($"🗄️ Database: {postgresUser}@{postgresHost}:{postgresPort}/{postgresDb}");
        Console.WriteLine($"🤖 Model: {modelName}");
        Console.WriteLine($"🌐 Ollama URL: {ollamaBaseUrl}");
        Console.WriteLine($"🌡️ Temperature: {temperature}");
        Console.WriteLine($"🔄 Processing...\n");

        // Execute the Python AgentWorkflow using the workflow name as a string
        // Pass all configuration as parameters for deterministic execution
        var result = await client.ExecuteWorkflowAsync<dynamic>(
            "AgentWorkflow",                               // LangChain agent workflow
            new object[] { query, threadId, postgresHost, postgresPort, postgresDb, postgresUser, postgresPassword, ollamaBaseUrl, modelName, temperature, redisUrl },   // All config parameters
            new WorkflowOptions
            {
                Id = "agent-workflow-csharp",
                TaskQueue = "hello-task-queue"
            });

        // Parse and display the response
        Console.WriteLine("✅ Agent Response:");
        Console.WriteLine("─────────────────────");
        
        // Convert dynamic result to JSON for easier reading
        var jsonResult = JsonSerializer.Serialize(result, new JsonSerializerOptions 
        { 
            WriteIndented = true 
        });
        
        // Parse the JSON to extract specific fields
        var resultDoc = JsonDocument.Parse(jsonResult);
        var root = resultDoc.RootElement;
        
        if (root.TryGetProperty("response", out JsonElement responseElement))
        {
            Console.WriteLine($"💬 Response: {responseElement.GetString()}");
        }
        
        if (root.TryGetProperty("model_used", out JsonElement modelElement))
        {
            Console.WriteLine($"🔧 Model: {modelElement.GetString()}");
        }
        
        if (root.TryGetProperty("success", out JsonElement successElement))
        {
            Console.WriteLine($"✅ Success: {successElement.GetBoolean()}");
        }

        Console.WriteLine("\n🔍 Full Response JSON:");
        Console.WriteLine(jsonResult);

        // Demo: Send a follow-up message using the same thread_id
        Console.WriteLine("\n" + new string('=', 50));
        var followUpQuery = "Can you give me a practical example of when to use workflows?";
        Console.WriteLine($"🤖 Follow-up: {followUpQuery}");
        Console.WriteLine("🔄 Processing...\n");

        var followUpResult = await client.ExecuteWorkflowAsync<dynamic>(
            "AgentWorkflow",
            new object[] { followUpQuery, threadId, postgresHost, postgresPort, postgresDb, postgresUser, postgresPassword, ollamaBaseUrl, modelName, temperature, redisUrl },  // Same config for memory!
            new WorkflowOptions
            {
                Id = "agent-workflow-followup-csharp",
                TaskQueue = "hello-task-queue"
            });

        var followUpJson = JsonSerializer.Serialize(followUpResult, new JsonSerializerOptions 
        { 
            WriteIndented = true 
        });
        
        var followUpDoc = JsonDocument.Parse(followUpJson);
        var followUpRoot = followUpDoc.RootElement;
        
        Console.WriteLine("✅ Follow-up Response:");
        Console.WriteLine("──────────────────────");
        if (followUpRoot.TryGetProperty("response", out JsonElement followUpResponseElement))
        {
            Console.WriteLine($"💬 Response: {followUpResponseElement.GetString()}");
        }
    }
} 