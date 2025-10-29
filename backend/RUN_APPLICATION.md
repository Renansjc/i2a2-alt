# Running the Multi-Agent NF-e System

This guide explains how to run the FastAPI application with CrewAI multi-agent system.

## Prerequisites

1. **Python 3.12** installed
2. **Environment variables** configured in `.env` file
3. **Dependencies** installed: `pip install -r requirements.txt`

## Environment Variables

The application requires the following environment variables (see `.env.example`):

### Required Variables

```bash
# OpenAI Configuration (Required for CrewAI)
OPENAI_API_KEY=sk-...                    # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini                 # Model to use (default: gpt-4o-mini)

# Supabase Configuration (Required for database)
SUPABASE_URL=https://xxx.supabase.co     # Your Supabase project URL
SUPABASE_SERVICE_KEY=eyJ...              # Your Supabase service key
```

### Optional Variables

```bash
# Application Configuration
APP_ENV=development                       # Environment: development, production
LOG_LEVEL=INFO                           # Logging level: DEBUG, INFO, WARNING, ERROR

# Chat Memory Configuration
MAX_CHAT_HISTORY=4                       # Number of messages to keep (2 interactions)
ENABLE_SEMANTIC_SEARCH=true              # Enable RAG-based semantic search

# Batch Processing Configuration
XML_FOLDER=xml_nf                        # Default folder for XML files
MAX_CONCURRENT_UPLOADS=5                 # Max concurrent file processing

# API Configuration
API_HOST=0.0.0.0                         # API host
API_PORT=8000                            # API port
API_RELOAD=true                          # Auto-reload on code changes
CORS_ORIGINS=["*"]                       # CORS allowed origins
```

## Running the Application

### Method 1: Using Python directly

```bash
cd backend
python main.py
```

This will start the server on `http://localhost:8000` with auto-reload enabled.

### Method 2: Using Uvicorn

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Production mode

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verifying the Application

### 1. Check Health Status

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Check Detailed Health

```bash
curl http://localhost:8000/health/detailed
```

This will show:
- CrewAI agent status
- Memory system statistics
- Batch processor status
- Configuration details

### 3. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Application Startup Process

When the application starts, it:

1. **Validates Environment Variables**
   - Checks for required: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
   - Exits with error if any are missing

2. **Initializes CrewAI System**
   - Creates NFeCrew with 3 agents:
     - coordenador (manager)
     - SQL Specialist
     - Conversation Specialist
   - Configures hierarchical process
   - Enables memory system

3. **Initializes Chat Memory**
   - Sets up RAG-based memory with ChromaDB
   - Configures short-term, long-term, and entity memory
   - Creates storage directory

4. **Initializes Batch Processor**
   - Sets up XML import processor
   - Configures concurrency control
   - Initializes job manager

5. **Registers API Routes**
   - Chat endpoints: `/api/chat`
   - Batch endpoints: `/api/batch`
   - Health checks: `/health`, `/health/detailed`

## Testing the Application

### Run Startup Tests

```bash
cd backend
python test_main_startup.py
```

This tests:
- Import functionality
- App creation
- Environment validation

### Run Integration Tests

```bash
cd backend
python test_main_integration.py
```

This tests:
- Full application startup
- Health endpoints
- Service initialization

## API Endpoints

### Chat Endpoints

- `POST /api/chat` - Process chat message
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/history/{session_id}` - Clear chat history
- `GET /api/chat/stats` - Get memory statistics

### Batch Endpoints

- `POST /api/batch/upload` - Start batch XML processing
- `GET /api/batch/status/{job_id}` - Get batch job status
- `GET /api/batch/jobs` - List all batch jobs
- `DELETE /api/batch/jobs/{job_id}` - Delete a batch job
- `POST /api/batch/cleanup` - Cleanup old jobs

### Health Endpoints

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with service info
- `GET /` - API root with information

## Example Usage

### Send a Chat Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "Quantas notas fiscais foram emitidas hoje?"
  }'
```

### Start Batch Processing

```bash
curl -X POST http://localhost:8000/api/batch/upload \
  -H "Content-Type: application/json" \
  -d '{
    "xml_folder": "xml_nf"
  }'
```

### Check Batch Status

```bash
curl http://localhost:8000/api/batch/status/{job_id}
```

## Troubleshooting

### Error: Missing environment variables

```
❌ ERROR: Missing required environment variables: OPENAI_API_KEY
```

**Solution**: Create a `.env` file with all required variables. See `.env.example`.

### Error: Port already in use

```
ERROR: [Errno 48] Address already in use
```

**Solution**: Either stop the other process or use a different port:
```bash
uvicorn main:app --port 8001
```

### Error: CrewAI initialization failed

Check that:
1. `OPENAI_API_KEY` is valid
2. Internet connection is available
3. OpenAI API is accessible

### Error: Database connection failed

Check that:
1. `SUPABASE_URL` is correct
2. `SUPABASE_SERVICE_KEY` is valid
3. Supabase project is active

## Logs

The application uses structured JSON logging. All events are logged with:
- Timestamp
- Logger name
- Event type
- Environment
- Context data

Example log entry:
```json
{
  "timestamp": "2025-10-27T22:04:19.379917",
  "logger": "main",
  "event": "application_startup_complete",
  "environment": "development",
  "context": {
    "message": "All services initialized successfully"
  }
}
```

## Development Mode

In development mode (`APP_ENV=development`):
- Auto-reload is enabled
- Detailed error messages are shown
- Debug logging is available

## Production Mode

For production deployment:

1. Set `APP_ENV=production`
2. Set `API_RELOAD=false`
3. Use multiple workers: `--workers 4`
4. Set appropriate `LOG_LEVEL=WARNING`
5. Configure specific `CORS_ORIGINS`
6. Use a reverse proxy (nginx, traefik)

Example production command:
```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-access-log \
  --log-level warning
```

## Next Steps

1. Configure your `.env` file
2. Run the application: `python main.py`
3. Test the endpoints using the Swagger UI at `/docs`
4. Integrate with the frontend application
5. Monitor logs for any issues

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check the health endpoints for service status
