# Local Development Guide

## Can You Run This Locally?

**Yes!** The project is designed for local development with AWS deployment as the target.

---

## What Runs Locally

### ✅ Backend (100% Local)
- FastAPI server on `localhost:8000`
- All Python agents (Research, Compliance, Execution)
- DynamoDB with LocalStack or DynamoDB Local
- All middleware and routers

### ✅ Frontend (100% Local)
- React app on `localhost:3000`
- Vite dev server with HMR
- API proxy to backend

### ⚠️ Agentic AI (Partial)
- **Research Agent**: ✅ Works (uses yfinance)
- **Compliance Agent**: ✅ Works (pure Python)
- **Execution Agent**: ✅ Works (pure Python)
- **Memory Agent**: ⚠️ Needs mock/placeholder
- **Supervisor Agent**: ⚠️ Needs Bedrock mock

---

## Quick Start - Local Development

### 1. Backend Setup

```bash
# Navigate to project
cd AssetManagement

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn boto3 pydantic yfinance python-dateutil

# Start backend
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend
cd AssetManagement/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 3. DynamoDB (Optional - for persistence)

**Option A: DynamoDB Local (Recommended for local dev)**

```bash
# Download DynamoDB Local
curl https://dynamodb-local.s3.amazonaws.com/dynamodb_local_latest.tar.gz -o dynamodb_local.tar.gz
tar -xzf dynamodb_local.tar.gz

# Start DynamoDB Local
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
```

**Option B: LocalStack (Full AWS compatibility)**

```bash
# Install LocalStack
pip install localstack

# Start LocalStack
localstack start
```

---

## Agentic AI - Local Development

### Current State

The agentic AI code is **designed for AWS Bedrock** but has **fallback implementations**:

### Research Agent ✅
```python
# Uses yfinance for market data
# Works 100% locally
# No AWS dependencies
```

### Compliance Agent ✅
```python
# Pure Python logic
# No AWS dependencies
# Works 100% locally
```

### Execution Agent ✅
```python
# Pure Python logic
# No AWS dependencies
# Works 100% locally
```

### Memory Agent ⚠️
```python
# Needs AgentCore Memory client
# Has placeholder implementation
# For local dev, use mock client
```

### Supervisor Agent ⚠️
```python
# Invokes Bedrock agents
# Has mock responses for local dev
# For full local dev, mock Bedrock client
```

### Mocking for Local Development

Create a `mock_bedrock_client.py`:

```python
class MockBedrockAgentClient:
    async def invoke_agent(self, agent_id, agent_alias, input_text):
        # Return mock response
        return {
            'body': {'output': 'mock response'},
            'agent_version': '1.0.0'
        }
```

---

## Testing Locally

### Backend Tests

```bash
cd AssetManagement
pytest tests/ -v
```

### Frontend Tests (when added)

```bash
cd AssetManagement/frontend
npm test
```

---

## Development Workflow

### 1. Start Backend

```bash
cd AssetManagement/backend
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend

```bash
cd AssetManagement/frontend
npm run dev
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Root endpoint
curl http://localhost:8000/
```

### 4. Access Frontend

Open browser to `http://localhost:3000`

---

## Limitations

### What Doesn't Work Locally (Without AWS)

1. **Real Bedrock Agent Invocation** - Uses AWS Bedrock API
2. **AgentCore Memory** - Requires AWS AgentCore service
3. **AgentCore Observability** - Requires AWS AgentCore service
4. **Real DynamoDB** - Use DynamoDB Local or LocalStack instead
5. **CloudWatch Metrics** - Use local metrics or mock

### What Works Locally

1. **All Python Logic** - Agents, validation, business logic
2. **API Endpoints** - All routes work
3. **Schema Validation** - Pydantic models
4. **Middleware** - CORS, error handling, validation
5. **Frontend UI** - Complete React app

---

## Recommended Local Setup

### For Full Local Development

1. **DynamoDB Local** - For database persistence
2. **LocalStack** - For AWS service mocking
3. **Mock Clients** - For Bedrock, Memory, Observability

### For Basic Development

1. **FastAPI Backend** - Core API
2. **React Frontend** - UI
3. **Mock Responses** - For agentic AI

---

## Summary

| Component | Local Status | Notes |
|-----------|-------------|-------|
| Backend API | ✅ Yes | FastAPI on localhost:8000 |
| Frontend UI | ✅ Yes | React on localhost:3000 |
| Research Agent | ✅ Yes | Uses yfinance |
| Compliance Agent | ✅ Yes | Pure Python |
| Execution Agent | ✅ Yes | Pure Python |
| Memory Agent | ⚠️ Mock | Needs mock client |
| Supervisor Agent | ⚠️ Mock | Needs mock Bedrock |
| DynamoDB | ⚠️ Local | Use DynamoDB Local |
| Bedrock Agents | ❌ No | Requires AWS |

**Bottom Line**: You can develop and test the **majority** of the application locally. The agentic AI code has fallback implementations, and you can mock the AWS services for local development.
