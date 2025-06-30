import logging
import asyncio
from typing import Dict, Any, Optional
from temporalio import activity
import redis.asyncio as redis

# LangChain/LangGraph imports
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langchain_core.tools import tool


@tool
def think_step_by_step(problem: str) -> str:
    """
    Break down complex problems into smaller steps for better reasoning.
    Use this when you need to think through a complex problem methodically.
    
    Args:
        problem: The problem or question to break down
    """
    return f"Breaking down the problem: '{problem}'\n\nThis tool helps structure thinking into logical steps. The LLM will continue reasoning based on this breakdown."


@tool
def analyze_text(text: str, analysis_type: str = "summary") -> str:
    """
    Analyze text for various properties like length, complexity, etc.
    
    Args:
        text: Text to analyze
        analysis_type: Type of analysis ("summary", "length", "complexity")
    """
    if analysis_type == "length":
        return f"Text analysis: {len(text)} characters, {len(text.split())} words, {len(text.split('.'))} sentences"
    elif analysis_type == "complexity":
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        return f"Text complexity: Average word length: {avg_word_length:.1f} characters"
    else:  # summary
        return f"Text summary: This text contains {len(text.split())} words discussing various topics."


@tool
async def get_table_schema(table_name: str) -> str:
    """
    Get the schema (column names and data types) for a specific table.
    Use this before writing complex queries to understand the table structure.
    
    Args:
        table_name: Name of the table to inspect (e.g., "users", "orders")
        
    Examples:
        - get_table_schema("orders") - Shows columns in the orders table
        - get_table_schema("users") - Shows columns in the users table
    """
    try:
        import os
        import json
        
        # Database connection parameters
        db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        }
        
        try:
            import asyncpg
            
            activity.logger.info(f"Getting schema for table: {table_name}")
            conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
            
            try:
                # Get column information for the table
                schema_query = """
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = $1 AND table_schema = 'public'
                ORDER BY ordinal_position
                """
                
                rows = await conn.fetch(schema_query, table_name)
                
                if not rows:
                    return f"Table '{table_name}' not found or has no columns."
                
                # Format as JSON like the MCP server
                schema_info = []
                for row in rows:
                    schema_info.append(dict(row))
                
                formatted_schema = json.dumps(schema_info, indent=2, default=str)
                return f"Schema for table '{table_name}':\n\n{formatted_schema}"
                
            finally:
                await conn.close()
                
        except Exception as e:
            return f"Error getting table schema: {str(e)}"
            
    except Exception as e:
        return f"Error preparing schema query: {str(e)}"


@tool
async def query_database(sql: str) -> str:
    """
    Execute a read-only SQL query against the PostgreSQL database.
    Use this to retrieve data, analyze database contents, or answer questions that require database information.
    
    IMPORTANT: Only SELECT queries are allowed. No INSERT, UPDATE, DELETE, DROP, etc.
    For complex analysis, break it down into simpler queries first to understand the data structure.
    
    Args:
        sql: SQL SELECT query to execute (e.g., "SELECT * FROM users LIMIT 10")
        
    Examples:
        - "SELECT COUNT(*) FROM orders WHERE status = 'completed'"  
        - "SELECT name, email FROM users ORDER BY created_at DESC LIMIT 5"
        - "SELECT AVG(price) FROM products WHERE category = 'electronics'"
        - "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        
    For complex reports, start simple:
        1. First explore table structure: "SELECT * FROM orders LIMIT 5"
        2. Check date ranges: "SELECT MIN(created_at), MAX(created_at) FROM orders"
        3. Then build complex queries step by step
    """
    try:
        # Validate that it's a safe query
        sql_upper = sql.strip().upper()
        
        # Allow SELECT and basic introspection queries
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            return "Error: Only SELECT and WITH (CTE) queries are allowed for security reasons."
        
        # Check for dangerous keywords that could modify data
        # Only block keywords that are clearly dangerous for data modification
        dangerous_keywords = ['DROP ', 'DELETE ', 'UPDATE ', 'INSERT ', 'ALTER ', 'CREATE ', 'TRUNCATE ', 'GRANT ', 'REVOKE ']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"Error: Query contains forbidden keyword '{keyword.strip()}'. Only read-only operations are allowed."
        
        try:
            # Try to use asyncpg for database connection
            import os
            
            # Database connection parameters (you'll need to configure these)
            db_config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': os.getenv('POSTGRES_PORT', '5432'),
                'database': os.getenv('POSTGRES_DB', 'postgres'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'password')
            }
            
            try:
                import asyncpg
                
                activity.logger.info(f"Attempting to connect to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
                # Create connection with timeout
                conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
                activity.logger.info("Database connection established successfully")
                
                try:
                    # Start a read-only transaction for extra safety
                    activity.logger.info("Starting read-only transaction")
                    await conn.execute("BEGIN TRANSACTION READ ONLY")
                    
                    try:
                        # Log the query being executed
                        activity.logger.info(f"Executing SQL query: {sql}")
                        # Execute the query with timeout to prevent hanging
                        rows = await asyncio.wait_for(conn.fetch(sql), timeout=30.0)
                        activity.logger.info(f"Query completed successfully, returned {len(rows) if rows else 0} rows")
                        
                        if not rows:
                            return "Query executed successfully. No rows returned."
                        
                        # Convert rows to JSON-serializable format like the MCP server
                        json_rows = []
                        for row in rows[:100]:  # Limit to 100 rows for readability
                            json_rows.append(dict(row))
                        
                        # Format as JSON for better readability and parsing
                        import json
                        formatted_result = json.dumps(json_rows, indent=2, default=str)
                        
                        result_summary = f"Query executed successfully ({len(rows)} rows returned"
                        if len(rows) > 100:
                            result_summary += f", showing first 100"
                        
                        return f"{result_summary}:\n\n{formatted_result}"
                        
                    finally:
                        # Always rollback the read-only transaction
                        try:
                            await conn.execute("ROLLBACK")
                            activity.logger.info("Transaction rolled back successfully")
                        except Exception as rollback_error:
                            activity.logger.warning(f"Could not roll back transaction: {rollback_error}")
                
                finally:
                    await conn.close()
                    
            except ImportError:
                return "Error: asyncpg library not installed. Please install with: pip install asyncpg"
            except asyncio.TimeoutError as timeout_error:
                return f"Database operation timed out: {str(timeout_error)}\n\nThe query may be too complex or the database may be slow to respond."
            except Exception as db_error:
                return f"Database connection error: {str(db_error)}\n\nPlease ensure PostgreSQL is running and connection parameters are correct."
            
        except Exception as e:
            return f"Error executing database query: {str(e)}"
            
    except Exception as e:
        return f"Error preparing database query: {str(e)}"


@activity.defn
async def process_with_agent(
    messages: str,  # Can be a single message or conversation
    thread_id: Optional[str] = None,
    ollama_base_url: str = "http://host.docker.internal:11434",
    model_name: str = "llama3.2",
    temperature: float = 0.0,
    redis_url: str = "redis://redis:6379"
) -> Dict[str, Any]:
    """
    Simple Temporal activity that uses LangGraph agent to process messages.
    LangGraph handles all the conversation state, memory, and complexity for us.
    Uses Redis for distributed state persistence across worker instances.
    
    Args:
        messages: The user's message(s) - can be single query or part of conversation
        thread_id: Optional thread ID for conversation memory (LangGraph manages this)
        ollama_base_url: Ollama server URL
        model_name: Ollama model to use
        temperature: Model temperature
        redis_url: Redis connection URL for persistent state storage
        
    Returns:
        Dict with the agent's response and metadata
    """
    
    try:
        activity.logger.info(f"Processing with agent (model: {model_name}, thread: {thread_id})")
        
        # Set up model with timeout handling
        activity.logger.info(f"Creating Ollama model: {model_name} at {ollama_base_url}")
        model = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature,
            timeout=180,  # 3 minute timeout for individual model calls
            request_timeout=180  # 3 minute request timeout
        )
        activity.logger.info("Ollama model created successfully")
        
        # Create agent with Redis-based persistent memory for distributed systems
        activity.logger.info(f"Connecting to Redis at {redis_url}")
        
        # Create Redis client and AsyncRedisSaver
        redis_client = redis.from_url(redis_url)
        memory = AsyncRedisSaver(redis_client=redis_client)
        activity.logger.info("Setting up Redis checkpointer...")
        await memory.asetup()  # Initialize Redis indices for checkpointing (async)
        activity.logger.info("Redis checkpointer setup complete")
        
        activity.logger.info("Creating LangGraph agent with reasoning tools...")
        # Provide tools for multi-step reasoning and problem solving
        tools = [think_step_by_step, analyze_text, get_table_schema, query_database]
        agent = create_react_agent(model, tools, checkpointer=memory)
        activity.logger.info(f"LangGraph agent created successfully with {len(tools)} reasoning tools")
        
        # Configure thread for conversation memory with iteration limit
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        config["recursion_limit"] = 10  # Limit reasoning loops to prevent infinite cycles
        activity.logger.info(f"Invoking agent with config: {config} (max 10 iterations)")
        
        # Let LangGraph handle the conversation - it's that simple!
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": messages}]},
            config=config
        )
        activity.logger.info("Agent invocation completed")
        
        # Extract the response (LangGraph gives us a clean format)
        activity.logger.info(f"Result structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        activity.logger.info(f"Extracted response: {response_text[:100]}...")
        
        return {
            "query": messages,
            "response": response_text,
            "model_used": model_name,
            "thread_id": thread_id,
            "success": True
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        activity.logger.error(f"Error in agent activity: {str(e)}")
        activity.logger.error(f"Full traceback: {error_details}")
        return {
            "query": messages,
            "response": f"Error: {str(e)}",
            "model_used": model_name,
            "thread_id": thread_id,
            "success": False,
            "error": str(e),
            "traceback": error_details
        } 