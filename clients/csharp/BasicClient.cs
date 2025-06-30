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
        var modelName = "llama3.2";

        Console.WriteLine($"🤖 Asking Agent: {query}");
        Console.WriteLine($"🧠 Thread ID: {threadId}");
        Console.WriteLine($"🔄 Processing...\n");

        // Execute the Python AgentWorkflow using the workflow name as a string
        var result = await client.ExecuteWorkflowAsync<dynamic>(
            "AgentWorkflow",                               // LangChain agent workflow
            new object[] { query, threadId, modelName },   // query, thread_id, model_name
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
            new object[] { followUpQuery, threadId, modelName },  // Same thread_id for memory!
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