using System.Text.Json;
using System.Text.Json.Serialization;
using Temporalio.Client;

// Data classes matching Python workflow structures
public record CustomerComplaint
{
    [JsonPropertyName("customer_id")]
    public int CustomerId { get; init; }
    
    [JsonPropertyName("complaint_details")]
    public string ComplaintDetails { get; init; } = string.Empty;
    
    [JsonPropertyName("order_ids")]
    public List<int>? OrderIds { get; init; }
    
    [JsonPropertyName("urgency_level")]
    public string UrgencyLevel { get; init; } = "medium";
}

public record RetentionResult
{
    [JsonPropertyName("case_id")]
    public string CaseId { get; init; } = string.Empty;
    
    [JsonPropertyName("customer_retained")]
    public bool CustomerRetained { get; init; }
    
    [JsonPropertyName("total_estimated_value")]
    public decimal TotalEstimatedValue { get; init; }
    
    [JsonPropertyName("strategy_executed")]
    public Dictionary<string, object> StrategyExecuted { get; init; } = new();
    
    [JsonPropertyName("executive_summary")]
    public string ExecutiveSummary { get; init; } = string.Empty;
    
    [JsonPropertyName("completion_time_minutes")]
    public double CompletionTimeMinutes { get; init; }
    
    [JsonPropertyName("resolution_approved")]
    public bool ResolutionApproved { get; init; }
    
    [JsonPropertyName("final_resolution")]
    public string FinalResolution { get; init; } = string.Empty;
    
    [JsonPropertyName("resolution_attempts")]
    public int ResolutionAttempts { get; init; }
}

class Program
{
    static async Task Main(string[] args)
    {
        // Create client connected to server at the given address
        var client = await TemporalClient.ConnectAsync(new("temporal:7233")
        {
            Namespace = "default"
        });

        // Configuration from environment variables (matches docker-compose.yml)
        var postgresHost = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "app-postgres";
        var postgresPort = Environment.GetEnvironmentVariable("POSTGRES_PORT") ?? "5432";
        var postgresDb = Environment.GetEnvironmentVariable("POSTGRES_DB") ?? "appdb";
        var postgresUser = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "appuser";
        var postgresPassword = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "apppassword";
        var ollamaBaseUrl = Environment.GetEnvironmentVariable("OLLAMA_BASE_URL") ?? "http://host.docker.internal:11434";
        var modelName = Environment.GetEnvironmentVariable("OLLAMA_MODEL_NAME") ?? "qwen3:8b";
        var temperature = float.Parse(Environment.GetEnvironmentVariable("OLLAMA_TEMPERATURE") ?? "0.0");
        var redisUrl = Environment.GetEnvironmentVariable("REDIS_URL") ?? "redis://redis:6379";

        Console.WriteLine("Customer Retention Workflow Test Client (C#)");
        Console.WriteLine("=".PadRight(60, '='));
        Console.WriteLine($"🗄️ Database: {postgresUser}@{postgresHost}:{postgresPort}/{postgresDb}");
        Console.WriteLine($"🤖 Model: {modelName}");
        Console.WriteLine($"🌐 Ollama URL: {ollamaBaseUrl}");
        Console.WriteLine($"🌡️ Temperature: {temperature}");
        Console.WriteLine($"🔗 Redis: {redisUrl}");
        Console.WriteLine();

        // Realistic customer complaint scenario based on enhanced schema
        // Using David Jones (Customer ID 5) - gaming customer marked as "at_risk" with support ticket
        var complaint = new CustomerComplaint
        {
            CustomerId = 5,  // david_jones - gaming segment, at_risk status, has open support ticket
            ComplaintDetails = """
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
            OrderIds = new List<int> { 5 },  // David's order that has the GPU delay issue
            UrgencyLevel = "urgent"  // Time-sensitive tournament deadline
        };

        Console.WriteLine($"🚨 Initiating retention workflow for customer {complaint.CustomerId}");
        Console.WriteLine($"📋 Complaint: {complaint.ComplaintDetails[..100]}...");
        Console.WriteLine($"⚡ Urgency: {complaint.UrgencyLevel}");
        Console.WriteLine($"📦 Order IDs: [{string.Join(", ", complaint.OrderIds ?? new List<int>())}]");
        Console.WriteLine();
        Console.WriteLine("🔄 Processing multi-agent retention workflow...");
        Console.WriteLine();

        try
        {
            // Start the CustomerRetentionWorkflow (async)
            var workflowId = $"customer-retention-{complaint.CustomerId}-{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";
            
            var handle = await client.StartWorkflowAsync(
                "CustomerRetentionWorkflow",  // Python workflow name
                new object[] { 
                    complaint,           // CustomerComplaint object
                    postgresHost,        // Database configuration
                    postgresPort,
                    postgresDb,
                    postgresUser,
                    postgresPassword,
                    ollamaBaseUrl,       // LLM configuration
                    modelName,
                    temperature,
                    redisUrl            // Redis configuration
                },
                new WorkflowOptions
                {
                    Id = workflowId,
                    TaskQueue = "customer-retention-queue"
                });
            
            Console.WriteLine($"🚀 Started workflow {workflowId}");
            Console.WriteLine("⏳ Running multi-agent analysis... This will take several minutes");
            Console.WriteLine();
            Console.WriteLine("📊 Agents will analyze the case:");
            Console.WriteLine("   - Customer Intelligence Agent: Calculating CLV and risk assessment");
            Console.WriteLine("   - Operations Investigation Agent: Investigating order delays");
            Console.WriteLine("   - Retention Strategy Agent: Developing retention approach");
            Console.WriteLine("   - Business Intelligence Agent: Generating executive insights");
            Console.WriteLine("   - Case Analysis Agent: Extracting metrics from findings");
            Console.WriteLine("   - Resolution Suggestion Agent: Creating action plan");
            Console.WriteLine();
            Console.WriteLine("⏸️  WORKFLOW WILL PAUSE for human approval of resolution suggestion");
            Console.WriteLine("💡 When the resolution is ready, use the Temporal UI to send approval signal:");
            Console.WriteLine("   🌐 Temporal UI: http://localhost:8080");
            Console.WriteLine($"   🔍 Workflow ID: {workflowId}");
            Console.WriteLine("   📡 Signal Name: approve_resolution");
            Console.WriteLine("   📝 Signal Payload Example:");
            Console.WriteLine("       {\"approve\": true, \"followUp\": \"\"}");
            Console.WriteLine("       {\"approve\": false, \"followUp\": \"Please provide more details...\"}");
            Console.WriteLine();
            Console.WriteLine("🔄 If declined, the workflow will generate a new resolution based on your feedback");
            Console.WriteLine("♾️  No limit on approval attempts - workflow continues until approved");
            Console.WriteLine();
            Console.WriteLine("⏳ Waiting for workflow completion...");
            
            // Get final result
            var result = await handle.GetResultAsync<dynamic>();

            // Parse and display the response
            var jsonResult = JsonSerializer.Serialize(result, new JsonSerializerOptions 
            { 
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
            });
            
            Console.WriteLine("✅ Customer Retention Workflow Completed!");
            Console.WriteLine("=".PadRight(60, '='));
            
            // Parse the JSON to extract specific fields
            var resultDoc = JsonDocument.Parse(jsonResult);
            var root = resultDoc.RootElement;
            
            // Display key results
            if (root.TryGetProperty("case_id", out JsonElement caseIdElement))
            {
                Console.WriteLine($"📂 Case ID: {caseIdElement.GetString()}");
            }
            
            if (root.TryGetProperty("customer_retained", out JsonElement retainedElement))
            {
                var isRetained = retainedElement.GetBoolean();
                var retainedIcon = isRetained ? "✅" : "❌";
                Console.WriteLine($"{retainedIcon} Customer Retained: {isRetained}");
            }
            
            if (root.TryGetProperty("total_estimated_value", out JsonElement valueElement))
            {
                var value = valueElement.GetDecimal();
                Console.WriteLine($"💰 Estimated Value: ${value:N2}");
            }
            
            if (root.TryGetProperty("completion_time_minutes", out JsonElement timeElement))
            {
                var minutes = timeElement.GetDouble();
                Console.WriteLine($"⏱️ Completion Time: {minutes:F1} minutes");
            }
            
            if (root.TryGetProperty("resolution_approved", out JsonElement approvedElement))
            {
                var isApproved = approvedElement.GetBoolean();
                var approvedIcon = isApproved ? "✅" : "❌";
                Console.WriteLine($"{approvedIcon} Resolution Approved: {isApproved}");
            }
            
            if (root.TryGetProperty("resolution_attempts", out JsonElement attemptsElement))
            {
                var attempts = attemptsElement.GetInt32();
                Console.WriteLine($"🔄 Resolution Attempts: {attempts}");
                if (attempts > 1)
                {
                    Console.WriteLine($"📝 Required {attempts} iterations to reach approval");
                }
            }
            
            Console.WriteLine();
            Console.WriteLine("🤖 Agent Execution Status:");
            if (root.TryGetProperty("strategy_executed", out JsonElement strategyElement))
            {
                foreach (var prop in strategyElement.EnumerateObject())
                {
                    var agentName = prop.Name.Replace("_", " ");
                    var success = prop.Value.GetBoolean();
                    var statusIcon = success ? "✅" : "❌";
                    var statusText = success ? "Completed" : "Failed";
                    Console.WriteLine($"  - {char.ToUpper(agentName[0])}{agentName[1..]}: {statusIcon} {statusText}");
                }
            }
            
            Console.WriteLine();
            Console.WriteLine("📊 Executive Summary:");
            Console.WriteLine("-".PadRight(40, '-'));
            if (root.TryGetProperty("executive_summary", out JsonElement summaryElement))
            {
                var summary = summaryElement.GetString() ?? "Executive report not available";
                // Wrap text at reasonable length
                var words = summary.Split(' ');
                var line = string.Empty;
                foreach (var word in words)
                {
                    if (line.Length + word.Length + 1 > 80)
                    {
                        Console.WriteLine(line.Trim());
                        line = word + " ";
                    }
                    else
                    {
                        line += word + " ";
                    }
                }
                if (!string.IsNullOrEmpty(line.Trim()))
                {
                    Console.WriteLine(line.Trim());
                }
            }
            
            Console.WriteLine();
            Console.WriteLine("📋 Final Resolution Plan:");
            Console.WriteLine("-".PadRight(40, '-'));
            if (root.TryGetProperty("final_resolution", out JsonElement resolutionElement))
            {
                var resolution = resolutionElement.GetString() ?? "Resolution not available";
                // Wrap text at reasonable length and display first 1000 characters
                var displayResolution = resolution.Length > 1000 ? resolution[..1000] + "..." : resolution;
                var words = displayResolution.Split(' ');
                var line = string.Empty;
                foreach (var word in words)
                {
                    if (line.Length + word.Length + 1 > 80)
                    {
                        Console.WriteLine(line.Trim());
                        line = word + " ";
                    }
                    else
                    {
                        line += word + " ";
                    }
                }
                if (!string.IsNullOrEmpty(line.Trim()))
                {
                    Console.WriteLine(line.Trim());
                }
            }
            
            Console.WriteLine();
            Console.WriteLine("🔍 Full Workflow Response (JSON):");
            Console.WriteLine("-".PadRight(40, '-'));
            Console.WriteLine(jsonResult);

        }
        catch (Exception e)
        {
            Console.WriteLine($"❌ Workflow failed: {e.Message}");
            Console.WriteLine($"🔍 Stack trace: {e.StackTrace}");
            
            if (e.InnerException != null)
            {
                Console.WriteLine($"🔗 Inner exception: {e.InnerException.Message}");
            }
        }
        
        Console.WriteLine();
        Console.WriteLine("🏁 Customer Retention Test Completed");
    }
} 