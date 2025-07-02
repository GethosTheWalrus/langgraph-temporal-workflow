# Distributed LangGraph Agent As A Temporal Workflow

This repository demonstrates how to set up a distributed LangGraph ReAct agent utilizing Redis for conversational memory management and Temporal for durable execution of agentic workflows.

## Demo

[![Watch the Demo](https://img.youtube.com/vi/DDVs6I3xeNo/maxresdefault.jpg)](https://youtu.be/DDVs6I3xeNo)

*Click the image above to watch the demo video*


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
[true, "Why should I use Temporal for durable workflow execution?"]
```

To complete the workflow
```json
[false]
```

## Architecture Diagrams

### 1. Overall System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        BC[Basic Client<br/>C# & Python]
        IC[Interactive Client<br/>C# & Python]  
        RC[Retention Client<br/>C# & Python]
    end
    
    subgraph "Temporal Orchestration Layer"
        TS[Temporal Server<br/>Workflow Orchestration]
        TUI[Temporal UI<br/>Monitoring & Signals]
        subgraph "Task Queues"
            TQ1[hello-task-queue<br/>Basic Workflows]
            TQ2[customer-retention-queue<br/>Retention Workflows]
            TQ3[interactive-conversation-queue<br/>Interactive Workflows]
        end
    end
    
    subgraph "Workflow Layer"
        AW[AgentWorkflow<br/>Basic Q&A]
        ICW[InteractiveConversationWorkflow<br/>Signal-driven Chat]
        CRW[CustomerRetentionWorkflow<br/>Multi-Agent Processing]
    end
    
    subgraph "Worker Layer (5 Replicas)"
        subgraph "Each Replica Runs 3 Concurrent Workers"
            W1[Basic Worker<br/>hello-task-queue]
            W2[Retention Worker<br/>customer-retention-queue]
            W3[Interactive Worker<br/>interactive-conversation-queue]
        end
    end
    
    subgraph "Activity Layer"
        LA[LangChain Agent<br/>General Purpose]
        CIA[Customer Intelligence<br/>Agent Activity]
        OIA[Operations Investigation<br/>Agent Activity]
        RSA[Retention Strategy<br/>Agent Activity]
        BIA[Business Intelligence<br/>Agent Activity]
        CAA[Case Analysis<br/>Agent Activity]
        RES[Resolution Suggestion<br/>Agent Activity]
    end
    
    subgraph "Tool Layer"
        GT[General Tools<br/>• think_step_by_step<br/>• analyze_text]
        DT[Database Tools<br/>• query_database<br/>• get_batch_table_schemas<br/>• analyze_table_relationships]
        CIT[Customer Intelligence Tools<br/>• get_customer_profile<br/>• calculate_clv<br/>• get_risk_score]
        CMT[Case Management Tools<br/>• create_retention_case<br/>• update_case_state<br/>• get_case_summary]
    end
    
    subgraph "Infrastructure Layer"
        REDIS[(Redis<br/>Conversation Memory<br/>& Case State)]
        POSTGRES[(PostgreSQL<br/>E-commerce Database<br/>Enhanced Schema)]
        OLLAMA[Ollama LLM<br/>qwen3:8b Model]
    end
    
    %% Client to Temporal
    BC --> TS
    IC --> TS  
    RC --> TS
    TUI --> TS
    
    %% Temporal to Workflows via Task Queues
    TS --> TQ1
    TS --> TQ2
    TS --> TQ3
    TQ1 --> AW
    TQ2 --> CRW
    TQ3 --> ICW
    
    %% Workers polling from specific queues
    TQ1 --> W1
    TQ2 --> W2
    TQ3 --> W3
    
    %% Workers execute activities
    W1 --> LA
    W2 --> CIA
    W2 --> OIA
    W2 --> RSA
    W2 --> BIA
    W2 --> CAA
    W2 --> RES
    W3 --> LA
    
    %% Activities use tools
    LA --> GT
    LA --> DT
    CIA --> GT
    CIA --> CIT
    CIA --> CMT
    CIA --> DT
    OIA --> GT
    OIA --> DT
    OIA --> CMT
    RSA --> GT
    RSA --> CMT
    BIA --> GT
    BIA --> CMT
    CAA --> GT
    CAA --> CMT
    RES --> GT
    RES --> CMT
    
    %% Infrastructure connections
    LA --> REDIS
    CIA --> REDIS
    OIA --> REDIS
    RSA --> REDIS
    BIA --> REDIS
    CAA --> REDIS
    RES --> REDIS
    
    DT --> POSTGRES
    CIT --> POSTGRES
    
    LA --> OLLAMA
    CIA --> OLLAMA
    OIA --> OLLAMA
    RSA --> OLLAMA
    BIA --> OLLAMA
    CAA --> OLLAMA
    RES --> OLLAMA
    
    %% Styling
    classDef client fill:#e3f2fd
    classDef temporal fill:#f3e5f5  
    classDef workflow fill:#e8f5e8
    classDef worker fill:#fff3e0
    classDef activity fill:#fce4ec
    classDef tool fill:#f1f8e9
    classDef infra fill:#ffebee
    
    class BC,IC,RC client
    class TS,TUI,TQ1,TQ2,TQ3 temporal
    class AW,ICW,CRW workflow
    class W1,W2,W3 worker
    class LA,CIA,OIA,RSA,BIA,CAA,RES activity
    class GT,DT,CIT,CMT tool
    class REDIS,POSTGRES,OLLAMA infra
```

### 2. Basic Workflow Execution

```mermaid
sequenceDiagram
    participant Client as Client<br/>(C# or Python)
    participant Temporal as Temporal Server
    participant Queue as hello-task-queue
    participant Worker as Basic Worker
    participant Agent as LangChain Agent
    participant Tools as Tool Suite
    participant DB as PostgreSQL
    participant LLM as Ollama qwen3:8b
    participant Redis as Redis Memory
    
    Client->>Temporal: execute_workflow("AgentWorkflow", [query, config])
    Temporal->>Queue: schedule activity on hello-task-queue
    Queue->>Worker: poll for tasks
    Worker->>Agent: process_with_agent(query, thread_id, config)
    
    Agent->>Redis: setup checkpointer & load conversation
    Agent->>Tools: initialize tool suite (5 tools)
    Agent->>LLM: send query with available tools
    
    LLM->>Agent: "I need to explore the database"
    Agent->>Tools: get_batch_table_schemas([tables])
    Tools->>DB: fetch multiple schemas efficiently  
    DB->>Tools: return JSON schemas
    Tools->>Agent: structured table information
    
    Agent->>LLM: "Here are the database schemas"
    LLM->>Agent: generate SQL query
    Agent->>Tools: query_database(sql)
    Tools->>DB: execute read-only transaction
    DB->>Tools: return query results (max 100 rows)
    Tools->>Agent: formatted results
    
    Agent->>LLM: "Analyze this data and respond"
    LLM->>Agent: final analysis response
    Agent->>Redis: save conversation state
    Agent->>Worker: return structured response
    Worker->>Queue: activity completed
    Queue->>Temporal: workflow result
    Temporal->>Client: workflow result with analysis
```

### 3. Interactive Conversation Workflow

```mermaid
sequenceDiagram
    participant Client as Interactive Client
    participant Temporal as Temporal Server  
    participant UI as Temporal UI
    participant Queue as interactive-conversation-queue
    participant Workflow as Interactive Workflow
    participant Worker as Interactive Worker
    participant Agent as LangChain Agent
    participant Redis as Redis Memory
    participant LLM as Ollama
    
    Client->>Temporal: start_workflow("InteractiveConversationWorkflow")
    Temporal->>Workflow: execute with initial query
    
    Workflow->>Queue: schedule activity on interactive-conversation-queue
    Queue->>Worker: poll for tasks
    Worker->>Agent: process with conversation context
    Agent->>Redis: load conversation history
    Agent->>LLM: process initial query
    LLM->>Agent: initial response
    Agent->>Redis: save conversation state
    Agent->>Worker: return response
    Worker->>Workflow: activity completed
    
    loop Interactive Conversation
        Workflow->>Workflow: await user_feedback signal
        Note over Workflow: Waiting for user input via signal
        
        UI->>Temporal: send signal([true, "follow-up question"])
        Temporal->>Workflow: deliver user_feedback signal
        
        Workflow->>Queue: schedule follow-up activity
        Queue->>Worker: poll for follow-up task
        Worker->>Agent: continue conversation
        Agent->>Redis: load previous conversation context
        Note over Agent: Agent remembers full conversation
        Agent->>LLM: process follow-up with context
        LLM->>Agent: contextual response
        Agent->>Redis: update conversation state
        Agent->>Worker: return follow-up response
        Worker->>Workflow: follow-up activity completed
        
        Workflow->>Client: signal completion (continue=true)
    end
    
    UI->>Temporal: send signal([false])
    Temporal->>Workflow: deliver end conversation signal
    Workflow->>Client: return final conversation summary
```

### 4. Customer Retention Multi-Agent Workflow

```mermaid
graph TB
    subgraph "Customer Retention Workflow - customer-retention-queue"
        START[Customer Complaint<br/>+ Order IDs + Priority]
        
        STAGE1[Stage 1: Case ID Generation<br/>retention_customerID_timestamp]
        
        subgraph "Stage 2: Parallel Intelligence Gathering"
            direction TB
            CIA[Customer Intelligence Agent<br/>Worker 1<br/>• Customer profile & CLV<br/>• Risk assessment<br/>• Retention priority<br/>• Case initialization]
            OIA[Operations Investigation Agent<br/>Worker 2<br/>• Order investigation<br/>• Root cause analysis<br/>• Systemic issues<br/>• Timeline reconstruction]
        end
        
        STAGE3[Stage 3: Strategy Development<br/>Worker 3<br/>Retention Strategy Agent<br/>• Analyze intelligence data<br/>• Develop retention plan<br/>• Calculate compensation<br/>• ROI justification]
        
        subgraph "Stage 4-5: Parallel Analysis & Reporting"
            direction TB
            BIA[Business Intelligence Agent<br/>Worker 4<br/>• Executive reporting<br/>• Strategic insights<br/>• Policy recommendations<br/>• Process improvements]
            CAA[Case Analysis Agent<br/>Worker 5<br/>• Extract REAL metrics<br/>• CLV validation<br/>• Retention probability<br/>• Success assessment]
        end
        
        subgraph "Stage 6: Resolution & Human Approval"
            RES[Resolution Suggestion Agent<br/>Worker 6<br/>• Synthesize all case data<br/>• Create actionable resolution<br/>• Human-in-the-loop approval]
            APPROVAL{Human Approval<br/>via Temporal Signal<br/>approve_resolution}
            RETRY[Generate New Resolution<br/>Based on Feedback]
        end
        
        FINAL[Stage 7: Results Compilation<br/>• Customer Retained: True/False<br/>• Actual CLV: $X,XXX<br/>• ROI Analysis: X.XX<br/>• Executive Summary<br/>• Resolution Attempts: N]
    end
    
    subgraph "Distributed State Management"
        REDIS[Redis Shared State<br/>• Case metadata & context<br/>• Cross-agent coordination<br/>• Real-time progress tracking]
        POSTGRES[Enhanced PostgreSQL Schema<br/>• Customer intelligence data<br/>• Support tickets & preferences<br/>• Financial & delivery tracking]
    end
    
    subgraph "Specialized Tool Distribution"
        CITOOLS[Customer Intelligence Tools<br/>• get_customer_profile<br/>• calculate_clv<br/>• get_risk_score]
        DBTOOLS[Database Investigation Tools<br/>• query_database<br/>• get_batch_schemas<br/>• analyze_relationships]
        CMTOOLS[Case Management Tools<br/>• create_retention_case<br/>• update_case_state<br/>• get_case_summary]
    end
    
    subgraph "Human Interaction"
        UI[Temporal UI<br/>Manual Signal Sending]
        SIGNALS[Signal Examples:<br/>{"approve": true, "followUp": ""}<br/>{"approve": false, "followUp": "..."}]
    end
    
    %% Flow connections
    START --> STAGE1
    STAGE1 --> CIA
    STAGE1 --> OIA
    CIA --> STAGE3
    OIA --> STAGE3
    STAGE3 --> BIA
    STAGE3 --> CAA
    BIA --> RES
    CAA --> RES
    RES --> APPROVAL
    APPROVAL -->|Approved| FINAL
    APPROVAL -->|Declined| RETRY
    RETRY --> RES
    
    %% Human interaction
    UI --> APPROVAL
    SIGNALS --> UI
    
    %% State management
    CIA -.-> REDIS
    OIA -.-> REDIS
    STAGE3 -.-> REDIS
    BIA -.-> REDIS
    CAA -.-> REDIS
    RES -.-> REDIS
    
    %% Data access
    CIA --> POSTGRES
    OIA --> POSTGRES
    CIA --> CITOOLS
    OIA --> DBTOOLS
    STAGE3 --> CMTOOLS
    BIA --> CMTOOLS
    CAA --> CMTOOLS
    RES --> CMTOOLS
    
    %% Parallel execution indicators
    CIA -.->|"asyncio.gather()"| OIA
    BIA -.->|"asyncio.gather()"| CAA
    
    %% Styling
    classDef parallel fill:#e8f5e8,stroke:#4caf50,stroke-width:3px
    classDef sequential fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef human fill:#fff3e0,stroke:#ff9800,stroke-width:3px
    classDef state fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef tools fill:#f1f8e9,stroke:#8bc34a,stroke-width:2px
    
    class CIA,OIA,BIA,CAA parallel
    class START,STAGE1,STAGE3,RES,FINAL sequential
    class APPROVAL,RETRY,UI,SIGNALS human
    class REDIS,POSTGRES state
    class CITOOLS,DBTOOLS,CMTOOLS tools
```