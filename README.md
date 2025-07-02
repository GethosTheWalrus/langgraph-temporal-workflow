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
sequenceDiagram
    participant Client as Retention Client
    participant Temporal as Temporal Server
    participant UI as Temporal UI
    participant Queue as customer-retention-queue
    participant Workflow as Customer Retention Workflow
    participant W1 as Customer Intelligence Worker
    participant W2 as Operations Investigation Worker
    participant W3 as Retention Strategy Worker
    participant W4 as Business Intelligence Worker
    participant W5 as Case Analysis Worker
    participant W6 as Resolution Suggestion Worker
    participant Redis as Redis Case State
    participant DB as PostgreSQL
    participant LLM as Ollama
    
    Client->>Temporal: start_workflow("CustomerRetentionWorkflow", complaint)
    Temporal->>Workflow: execute with customer complaint
    
    Note over Workflow: Stage 1: Generate Case ID
    Workflow->>Workflow: case_id = retention_customerID_timestamp
    
    Note over Workflow: Stage 2: Parallel Intelligence Gathering
    par Customer Intelligence
        Workflow->>Queue: schedule customer_intelligence_agent
        Queue->>W1: poll for task
        W1->>Redis: create_retention_case(case_id)
        W1->>DB: get_customer_profile & calculate_clv
        W1->>LLM: analyze customer value & risk
        W1->>Redis: update_case_state with intelligence
        W1->>Workflow: return customer analysis
    and Operations Investigation  
        Workflow->>Queue: schedule operations_investigation_agent
        Queue->>W2: poll for task
        W2->>DB: investigate orders & root causes
        W2->>LLM: analyze operational issues
        W2->>Redis: update_case_state with investigation
        W2->>Workflow: return investigation results
    end
    
    Note over Workflow: Stage 3: Strategy Development
    Workflow->>Queue: schedule retention_strategy_agent
    Queue->>W3: poll for task
    W3->>Redis: get_case_state (intelligence + investigation)
    W3->>LLM: develop retention strategy
    W3->>Redis: update_case_state with strategy
    W3->>Workflow: return strategy results
    
    Note over Workflow: Stage 4-5: Parallel Analysis & Reporting
    par Business Intelligence
        Workflow->>Queue: schedule business_intelligence_agent
        Queue->>W4: poll for task
        W4->>Redis: get_case_state (all previous data)
        W4->>LLM: generate executive insights
        W4->>Redis: update_case_state with BI report
        W4->>Workflow: return BI results
    and Case Analysis
        Workflow->>Queue: schedule case_analysis_agent
        Queue->>W5: poll for task
        W5->>Redis: get_case_state (all previous data)
        W5->>LLM: extract real metrics & validation
        W5->>Redis: update_case_state with analysis
        W5->>Workflow: return case analysis
    end
    
    Note over Workflow: Stage 6: Resolution & Human Approval Loop
    loop Until Human Approval
        Workflow->>Queue: schedule suggest_resolution
        Queue->>W6: poll for task
        W6->>Redis: get_case_summary (all accumulated data)
        W6->>LLM: synthesize actionable resolution plan
        W6->>Workflow: return resolution suggestion
        
        Workflow->>Workflow: await approve_resolution signal (30min timeout)
        Note over Workflow: Waiting for human approval via Temporal UI
        
        UI->>Temporal: send approve_resolution signal
        Temporal->>Workflow: deliver approval decision
        
        alt Resolution Approved
            Note over Workflow: approve: true - Continue to final stage
        else Resolution Declined  
            Note over Workflow: approve: false + feedback - Generate new resolution
        end
    end
    
    Note over Workflow: Stage 7: Results Compilation
    Workflow->>Redis: extract final metrics from case analysis
    Workflow->>Client: return RetentionResult with outcomes
    
    Client->>Client: display case summary & resolution attempts
```

**Human Approval Signal Examples:**
```json
// Approve resolution
{"approve": true, "followUp": ""}

// Decline with feedback  
{"approve": false, "followUp": "Please provide more specific timeline commitments and escalation procedures."}
```