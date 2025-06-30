# Distributed LangGraph Agent As A Temporal Workflow

This repository demonstrates how to set up a distributed LangGraph ReAct agent utilizing Redis for conversational memory management and Temporal for durable execution of agentic workflows.

## Quick Start

1. Start the platform services
```bash
docker compose --profile temporal up --build -d
```

2. Start the worker(s) - expand for additional workers
```bash
docker compose up --build -d python-worker
```

3. Start the workflow
```bash
docker compose up --build -d csharp-client
```

## Usage

To chat with the agent, send a signal via the Temporal [UI](http://localhost:8080)
```json
[true, "Why should I use Temporal for durable workflow execution?]
```

To complete the workflow
```json
[false]
```

## Diagrams

```mermaid
graph TB
    subgraph "Client Layer"
        CS[C# Interactive Client]
        PY[Python Basic Client]
    end
    
    subgraph "Temporal Server"
        TS[Temporal Server<br/>Orchestration Engine]
        TUI[Temporal UI<br/>Signal Management]
    end
    
    subgraph "Current Agent Workflow"
        direction TB
        ICW[Interactive Conversation Workflow]
        ICW --> |"execute_activity(10min timeout)"| AG1[Agent Activity<br/>LangChain + LangGraph]
        AG1 --> |"uses tools"| TOOLS1[Tool Set 1<br/>• query_database<br/>• get_table_schema<br/>• think_step_by_step<br/>• analyze_text]
    end
    
    subgraph "Potential Future Workflows"
        direction TB
        subgraph "Data Analysis Workflow"
            DAW[Data Analytics Workflow]
            DAW --> AGA[Analysis Agent Activity]
            AGA --> TOOLSA[Analytics Tools<br/>• statistical_analysis<br/>• data_visualization<br/>• trend_detection<br/>• forecasting]
        end
        
        subgraph "Content Generation Workflow"
            CGW[Content Generation Workflow]
            CGW --> AGC[Content Agent Activity]
            AGC --> TOOLSC[Content Tools<br/>• document_generator<br/>• image_analysis<br/>• translation<br/>• summarization]
        end
        
        subgraph "Multi-Agent Workflow"
            MAW[Multi-Agent Workflow]
            MAW --> AG2[Research Agent]
            MAW --> AG3[Analysis Agent]
            MAW --> AG4[Report Agent]
            AG2 --> AG3
            AG3 --> AG4
        end
    end
    
    subgraph "Infrastructure Layer"
        direction LR
        REDIS[(Redis<br/>Conversation State<br/>& Memory)]
        PG[(PostgreSQL<br/>Application Data<br/>E-commerce DB)]
        OLLAMA[Ollama LLM Server<br/>Local AI Models]
    end
    
    subgraph "Python Worker Process"
        PW[Python Temporal Worker<br/>Handles All Activities]
    end
    
    %% Client connections
    CS --> |signals| TS
    PY --> |workflow execution| TS
    TUI --> |manual signals| TS
    
    %% Temporal orchestration
    TS --> |schedules| ICW
    TS --> |schedules| DAW
    TS --> |schedules| CGW
    TS --> |schedules| MAW
    
    %% Worker execution
    TS --> |activity execution| PW
    PW --> |runs| ICW
    PW --> |runs| DAW
    PW --> |runs| CGW
    PW --> |runs| MAW
    
    %% Agent infrastructure
    AG1 --> |state persistence| REDIS
    AG1 --> |data queries| PG
    AG1 --> |LLM inference| OLLAMA
    
    AGA --> |state persistence| REDIS
    AGA --> |data access| PG
    AGA --> |LLM inference| OLLAMA
    
    AGC --> |state persistence| REDIS
    AGC --> |LLM inference| OLLAMA
    
    AG2 --> |shared state| REDIS
    AG3 --> |shared state| REDIS
    AG4 --> |shared state| REDIS
    AG2 --> |LLM inference| OLLAMA
    AG3 --> |LLM inference| OLLAMA
    AG4 --> |LLM inference| OLLAMA
    
    %% Styling
    classDef client fill:#e1f5fe
    classDef temporal fill:#f3e5f5
    classDef agent fill:#e8f5e8
    classDef infra fill:#fff3e0
    classDef workflow fill:#fce4ec
    
    class CS,PY client
    class TS,TUI temporal
    class AG1,AGA,AGC,AG2,AG3,AG4 agent
    class REDIS,PG,OLLAMA infra
    class ICW,DAW,CGW,MAW workflow
```

```mermaid
sequenceDiagram
    participant Client as C# Client
    participant Temporal as Temporal Server
    participant Workflow as Interactive Workflow
    participant Agent as Agent Activity
    participant Redis as Redis State
    participant DB as PostgreSQL
    participant Ollama as Ollama LLM
    
    Note over Client,Ollama: Agent-Powered Temporal Workflow Execution
    
    Client->>Temporal: Start Workflow("revenue report", session_id)
    Temporal->>Workflow: Execute InteractiveConversationWorkflow
    
    loop Conversation Loop
        Workflow->>Agent: execute_activity("revenue report", thread_id)
        Note over Agent: Activity Timeout: 10 minutes
        
        Agent->>Redis: Setup checkpointer & load conversation history
        Agent->>Agent: Create LangGraph agent with 4 tools
        
        Agent->>Ollama: "Generate revenue report for PC shop"
        Ollama->>Agent: "I need to explore the database first"
        
        Agent->>DB: get_table_schema("orders")
        DB->>Agent: JSON schema with columns & types
        
        Agent->>DB: get_table_schema("order_items") 
        DB->>Agent: JSON schema with relationships
        
        Agent->>Ollama: "Now I understand the schema, let me write SQL"
        Ollama->>Agent: Generate SQL query
        
        Agent->>DB: BEGIN TRANSACTION READ ONLY
        Agent->>DB: Execute complex SQL query
        DB->>Agent: JSON results (up to 100 rows)
        Agent->>DB: ROLLBACK (safety)
        
        Agent->>Ollama: "Analyze this data and format report"
        Ollama->>Agent: Formatted revenue analysis
        
        Agent->>Redis: Save conversation state
        Agent->>Workflow: Return analysis result
        
        Workflow->>Client: Response ready, waiting for signal
        
        Client->>Temporal: Send signal([true, "break down by category"])
        Temporal->>Workflow: Deliver user_feedback signal
        
        Workflow->>Agent: execute_activity("break down by category", thread_id)
        Agent->>Redis: Load previous conversation context
        Note over Agent: Agent remembers previous analysis
        
        Agent->>Ollama: "User wants category breakdown of previous data"
        Agent->>DB: Execute category analysis query
        Agent->>Ollama: "Generate category-specific insights"
        Agent->>Workflow: Return detailed breakdown
        
        Workflow->>Client: Category analysis complete
    end
    
    Client->>Temporal: Send signal([false, null])
    Temporal->>Workflow: End conversation signal
    Workflow->>Client: Final conversation summary
```