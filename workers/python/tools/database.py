"""
Database tools for LangChain agents.

These tools provide PostgreSQL database interaction capabilities including
schema inspection, relationship analysis, and read-only query execution.
"""

import asyncio
import json
import logging
from typing import List, Optional

import asyncpg
from temporalio import activity
from langchain_core.tools import tool


def create_database_tools(db_config: dict):
    """
    Factory function that creates database tools configured with specific db_config.
    
    Args:
        db_config: Dictionary containing database connection parameters
                  (host, port, database, user, password)
    
    Returns:
        List of configured database tools
    """
    
    @tool
    async def get_batch_table_schemas(table_names: List[str]) -> str:
        """
        Get the schema (column names and data types) for one or more tables.
        Use this to understand table structure before writing queries or analyzing data.
        
        Args:
            table_names: List of table names to inspect (e.g., ["users"], ["users", "orders", "products"])
            
        Examples:
            - get_batch_table_schemas(["users"]) - Gets schema for just the users table
            - get_batch_table_schemas(["users", "orders"]) - Gets schemas for users and orders tables
            - get_batch_table_schemas(["products", "categories", "inventory"]) - Gets schemas for multiple product-related tables
        """
        try:
            try:
                activity.logger.info(f"Getting batch schemas for tables: {', '.join(table_names)}")
                conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
                
                try:
                    all_schemas = {}
                    
                    for table_name in table_names:
                        try:
                            # Get column information for each table
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
                                all_schemas[table_name] = f"Table '{table_name}' not found or has no columns."
                            else:
                                # Format as JSON like the individual schema function
                                schema_info = []
                                for row in rows:
                                    schema_info.append(dict(row))
                                all_schemas[table_name] = schema_info
                                
                        except Exception as table_error:
                            all_schemas[table_name] = f"Error getting schema for table '{table_name}': {str(table_error)}"
                    
                    # Format the complete result
                    result = "Batch table schemas:\n\n"
                    for table_name, schema_data in all_schemas.items():
                        result += f"## Table: {table_name}\n"
                        if isinstance(schema_data, str):
                            # Error message
                            result += f"{schema_data}\n\n"
                        else:
                            # Actual schema data
                            formatted_schema = json.dumps(schema_data, indent=2, default=str)
                            result += f"{formatted_schema}\n\n"
                    
                    return result
                    
                finally:
                    await conn.close()
                    
            except Exception as e:
                return f"Error getting batch table schemas: {str(e)}"
                
        except Exception as e:
            return f"Error preparing batch schema query: {str(e)}"

    @tool
    async def analyze_table_relationships(table_names: Optional[List[str]] = None) -> str:
        """
        Analyze foreign key relationships between tables in the database.
        Use this to understand how tables connect to each other.
        
        Args:
            table_names: Optional list of specific tables to analyze. If not provided, analyzes all tables.
            
        Examples:
            - analyze_table_relationships() - Gets all foreign key relationships in the database
            - analyze_table_relationships(["users", "orders", "order_items"]) - Gets relationships for specific tables
        """
        try:
            try:
                activity.logger.info(f"Analyzing table relationships for: {table_names or 'all tables'}")
                conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
                
                try:
                    # Query to get foreign key relationships
                    fk_query = """
                    SELECT 
                        tc.table_name AS source_table,
                        kcu.column_name AS source_column,
                        ccu.table_name AS target_table,
                        ccu.column_name AS target_column,
                        tc.constraint_name
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema = 'public'
                    """
                    
                    # Add table name filter if specified
                    if table_names:
                        table_names_str = "', '".join(table_names)
                        fk_query += f" AND (tc.table_name IN ('{table_names_str}') OR ccu.table_name IN ('{table_names_str}'))"
                    
                    fk_query += " ORDER BY tc.table_name, kcu.column_name"
                    
                    rows = await conn.fetch(fk_query)
                    
                    if not rows:
                        return "No foreign key relationships found for the specified tables."
                    
                    # Format relationships
                    relationships = []
                    for row in rows:
                        relationships.append(dict(row))
                    
                    # Group by source table for better readability
                    grouped_relationships = {}
                    for rel in relationships:
                        source_table = rel['source_table']
                        if source_table not in grouped_relationships:
                            grouped_relationships[source_table] = []
                        grouped_relationships[source_table].append(rel)
                    
                    # Format the result
                    result = "Table Relationships Analysis:\n\n"
                    
                    for source_table, rels in grouped_relationships.items():
                        result += f"## {source_table}\n"
                        for rel in rels:
                            result += f"- {rel['source_column']} → {rel['target_table']}.{rel['target_column']}\n"
                        result += "\n"
                    
                    # Add JSON format for detailed analysis
                    result += "Detailed relationships (JSON):\n"
                    result += json.dumps(relationships, indent=2, default=str)
                    
                    return result
                    
                finally:
                    await conn.close()
                    
            except Exception as e:
                return f"Error analyzing table relationships: {str(e)}"
                
        except Exception as e:
            return f"Error preparing relationship analysis: {str(e)}"

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
                try:
                    
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
    
    # Return the configured tools
    return [get_batch_table_schemas, analyze_table_relationships, query_database] 