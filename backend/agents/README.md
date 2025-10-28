# NFeCrew - Multi-Agent System for NF-e Processing

## Overview

NFeCrew is a CrewAI-based multi-agent system designed to process electronic invoices (NF-e) and answer user queries through natural language conversations. The system uses three specialized AI agents that work together to provide accurate and helpful responses.

## Architecture

### Agents

1. **Coordinator (Manager Agent)**
   - Role: Analyzes user intent and coordinates other agents
   - Capabilities: Delegation, intent analysis, workflow orchestration
   - Process: Acts as manager in hierarchical process
   - Tools: None (delegates to specialized agents)

2. **SQL Specialist**
   - Role: Generates and executes database queries
   - Capabilities: SQL generation, query optimization, data retrieval
   - Tools:
     - DatabaseQueryTool: Execute SELECT queries via Supabase REST API
     - DatabaseJoinQueryTool: Execute complex queries with JOINs
     - SchemaInfoTool: Get database schema information
     - SchemaSearchTool: Search for relevant tables/columns

3. **Conversation Specialist**
   - Role: Formats responses in natural, friendly language
   - Capabilities: Natural language generation, data formatting, conversational interaction
   - Tools: None (focuses on language and formatting)

### Process Flow

```
User Message
    ↓
Coordinator (analyzes intent)
    ↓
    ├─→ SQL Specialist (if database query needed)
    │       ↓
    │   Execute Query
    │       ↓
    │   Return Results
    │       ↓
    └─→ Conversation Specialist (format response)
            ↓
        Natural Language Response
            ↓
        User
```

### Hierarchical Process

The system uses CrewAI's hierarchical process where:
- The Coordinator acts as the manager
- The Coordinator is NOT in the agents list (only SQL Specialist and Conversation Specialist)
- The Coordinator automatically delegates tasks to appropriate agents
- Agents work independently on their specialized tasks
- Results flow back through the Coordinator to the user

## Configuration

### Agent Configuration (agents.yaml)

Located at `backend/agents/config/agents.yaml`, this file defines:
- Role: What the agent does
- Goal: What the agent aims to achieve
- Backstory: Context and personality for the agent

### Task Configuration (tasks.yaml)

Located at `backend/agents/config/tasks.yaml`, this file defines:
- Description: What the task involves
- Expected Output: What the task should produce
- Agent: Which agent executes the task

Tasks:
1. `analyze_intent`: Determine if query needs database or is conversational
2. `execute_sql_query`: Generate and execute SQL queries
3. `format_response`: Format database results into natural language
4. `direct_conversation`: Handle conversational interactions

## Usage

### Basic Usage

```python
from agents import NFeCrew

# Create crew instance
crew = NFeCrew()

# Process a message
response = crew.process_message(
    message="Quantas notas fiscais foram emitidas hoje?",
    chat_history=[
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Olá! Como posso ajudar?"}
    ],
    session_id="user-123"
)

print(response)
```

### With FastAPI

```python
from fastapi import FastAPI
from agents import create_nfe_crew

app = FastAPI()
crew = create_nfe_crew()

@app.post("/chat")
async def chat(message: str, session_id: str):
    response = crew.process_message(
        message=message,
        session_id=session_id
    )
    return {"response": response}
```

## Features

### 1. Automatic Intent Analysis

The Coordinator automatically determines whether a user message requires:
- **Database Query**: Questions about specific NF-e data (values, dates, companies, products)
- **Conversational Response**: Greetings, explanations, general questions

### 2. Intelligent SQL Generation

The SQL Specialist:
- Understands the database schema
- Generates optimized SELECT queries
- Uses appropriate JOINs for related data
- Applies filters and limits
- Handles errors gracefully

### 3. Natural Language Responses

The Conversation Specialist:
- Formats technical data into accessible language
- Uses proper currency formatting (R$ with thousands separators)
- Maintains professional but friendly tone
- Provides context and explanations
- Offers additional help when appropriate

### 4. Conversation Memory

The system maintains conversation context:
- Stores last N interactions (configurable via `MAX_CHAT_HISTORY`)
- Uses CrewAI's built-in memory system
- Supports semantic search (optional, requires embeddings)
- Enables follow-up questions without repeating context

### 5. Database Integration

Connects to Supabase PostgreSQL via REST API:
- Read-only access (SELECT queries only)
- PostgREST filters (eq, gt, lt, like, etc.)
- Support for complex queries with JOINs
- Automatic error handling and retry logic

## Database Schema

The system works with the following main tables:

- **empresas**: Companies (emitters and recipients)
- **notas_fiscais**: Electronic invoices (NF-e)
- **nf_itens**: Invoice items (products/services)
- **nf_itens_icms/ipi/pis/cofins**: Tax details per item
- **nf_pagamentos**: Payment information
- **nf_transporte**: Transport information

See `backend/database/schema.py` for complete schema documentation.

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Memory
MAX_CHAT_HISTORY=4
ENABLE_SEMANTIC_SEARCH=true
```

## Testing

Run the test suite:

```bash
python backend/agents/test_crew.py
```

Tests verify:
- ✓ Crew initialization
- ✓ Agent creation
- ✓ Task creation
- ✓ Crew configuration
- ✓ Schema summary generation

## Error Handling

The system handles errors at multiple levels:

1. **Tool Level**: Database and schema tools return structured error messages
2. **Agent Level**: Agents handle tool errors and provide fallback responses
3. **Crew Level**: Coordinator manages overall error flow
4. **API Level**: FastAPI exception handlers format errors for clients

## Performance Considerations

- **Query Limits**: All database queries are limited to prevent excessive data retrieval
- **Memory Management**: Conversation history is limited to recent interactions
- **Caching**: Schema information is cached to reduce database calls
- **Async Support**: Compatible with async/await patterns

## Extending the System

### Adding a New Agent

1. Define agent in `agents.yaml`
2. Create agent method with `@agent` decorator
3. Add agent to crew configuration
4. Define tasks for the agent in `tasks.yaml`

### Adding a New Tool

1. Create tool class inheriting from `BaseTool`
2. Define input schema with Pydantic
3. Implement `_run` method
4. Add tool to appropriate agent(s)

### Adding a New Task

1. Define task in `tasks.yaml`
2. Create task method with `@task` decorator
3. Assign task to appropriate agent
4. Update process flow if needed

## Troubleshooting

### Common Issues

1. **"Manager agent should not be included in agents list"**
   - Solution: In hierarchical process, manager is separate from agents list

2. **"CHROMA_OPENAI_API_KEY environment variable is not set"**
   - Solution: Set `ENABLE_SEMANTIC_SEARCH=false` or provide valid OpenAI API key

3. **"Validation error for Settings"**
   - Solution: Ensure all required environment variables are set

4. **Database connection errors**
   - Solution: Verify Supabase URL and service key are correct

## Best Practices

1. **Always provide chat history** for better context understanding
2. **Use session IDs** to maintain separate conversations
3. **Limit query results** to prevent overwhelming responses
4. **Monitor token usage** to control OpenAI API costs
5. **Log all interactions** for debugging and improvement

## License

Part of the Multi-Agent NF-e System project.

## Support

For issues or questions, refer to the main project documentation or create an issue in the project repository.

