# Job Matcher

## About

Job Matcher is an AI-powered career discovery platform that helps job seekers find relevant opportunities through intelligent matching and personalized analysis. The application uses OpenAI's GPT-4 to understand your job preferences in natural language and provides tailored recommendations.

### How It Works

1. **Describe Your Ideal Job**: Simply describe what you're looking for in plain English (e.g., "remote frontend developer job in Europe with flexible hours").

2. **AI Extracts Preferences**: The application uses GPT-4 to intelligently parse your input and extract structured preferences including:
   - Relevant keywords and skills
   - Preferred location(s)
   - Remote work preference

3. **Job Search**: Based on your extracted preferences, the system searches for matching job opportunities.

4. **Personalized Analysis**: Get AI-generated insights explaining why each job match is relevant to your preferences, helping you make informed decisions about which opportunities to pursue.

### What to Expect

- **Natural Language Input**: No need to fill out complex forms—just describe what you want in your own words
- **Intelligent Matching**: AI-powered preference extraction ensures accurate understanding of your requirements
- **Actionable Insights**: Receive personalized explanations of why jobs match your criteria
- **Streamlined Experience**: Clean, modern interface that guides you through the job discovery process

You will be required to add your own API key to test this

---

# RAG (Retrieval-Augmented Generation) System

## Overview

Job Matcher uses a RAG system powered by ChromaDB to provide evidence-backed decision making for AI agents. The system stores API documentation in a vector database, allowing agents to retrieve relevant information when making decisions about API calls.

## How RAG Works in This Project

1. **API Documentation Storage**: Rise Jobs API documentation is stored in ChromaDB as vector embeddings
2. **Agent Integration**: When agents (preference extraction, match advisor) need to make decisions, they query the RAG system
3. **Evidence-Backed Decisions**: Agents retrieve relevant API documentation and use it to:
   - Extract preferences in formats that align with API requirements
   - Understand valid location formats (city names, country names, "Remote")
   - Make informed decisions based on actual API capabilities

## Initializing the RAG Database

Before using the application, you need to populate the ChromaDB database with API documentation:

```bash
cd backend
python scripts/init_rag_db.py
```

This script will:
- Initialize the ChromaDB database
- Generate embeddings for all API documentation chunks
- Store them in `./chroma_db/` directory

**Note**: You need to have `OPEN_API_KEY` environment variable set, as embeddings are generated using OpenAI's API.

### Reinitializing the Database

If you update the API documentation, you can reset and repopulate:

```bash
python scripts/init_rag_db.py
# When prompted, answer "yes" to reset the database
```

## Technical Details

- **Vector Database**: ChromaDB (persistent, local storage)
- **Embedding Model**: OpenAI `text-embedding-3-small`
- **Documentation Location**: `backend/app/services/api_documentation.py`
- **Database Location**: `backend/chroma_db/` (excluded from git)

## RAG Integration Points

1. **Preference Agent** (`backend/app/agents/preference_agent.py`):
   - Retrieves API documentation about location filtering and parameters
   - Uses docs to extract preferences in API-compatible formats

2. **Match Advisor Agent** (`backend/app/agents/match_advisor_agent.py`):
   - Retrieves documentation about response structure and data transformation
   - Uses docs to provide context-aware advice about job results

## Troubleshooting RAG

If RAG is not working:

1. **Check if database is initialized**:
   ```bash
   ls backend/chroma_db/
   ```
   If empty, run the initialization script.

2. **Check environment variable**:
   ```bash
   echo $OPEN_API_KEY
   ```
   Must be set for embeddings to work.

3. **Check logs**: The system gracefully falls back if RAG is unavailable, but check backend logs for errors.

---

# Kubernetes Deployment for local Dev

## Setup Secrets

Before deploying, create the OpenAI API key secret (use the provided template (openai-secret_template.yaml) to create your onwn):

```bash
# Option 1: Create secret from file
kubectl create secret generic openai-secret \
  --from-literal=api-key='your-actual-api-key-here'

# Option 2: Apply the secret file (edit it first with your key)
kubectl apply -f k8s/openai-secret.yaml
```

## Deploy

1. Build and deploy:
   ```bash
   ./build-and-deploy.sh
   ```

2. Or manually:
   ```bash
   # Set minikube docker env
   eval $(minikube docker-env)
   
   # Build images
   cd backend && docker build -t job-matcher-backend:latest . && cd ..
   cd frontend && docker build -t job-matcher-frontend:latest . && cd ..
   
   # Create secret (if not already created)
   kubectl create secret generic openai-secret --from-literal=api-key='your-key'
   
   # Deploy
   kubectl apply -f k8s/
   ```

## Troubleshooting

### Backend CrashLoopBackOff

1. Check logs:
   ```bash
   kubectl logs -l app=backend
   ```

2. Common issues:
   - Missing `openai` package → Rebuild image after updating requirements.txt
   - Missing API key → Create the secret
   - Import errors → Check all dependencies in requirements.txt
   - Missing `chromadb` package → Rebuild image after updating requirements.txt
   - RAG database not initialized → Run `python scripts/init_rag_db.py` in the backend container

3. Rebuild and redeploy:
   ```bash
   eval $(minikube docker-env)
   cd backend && docker build -t job-matcher-backend:latest . && cd ..
   kubectl rollout restart deployment/backend-deployment
   ```

### Check Pod Status

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

## Important Notes

- Always run `eval $(minikube docker-env)` before building images
- The `imagePullPolicy: Never` is crucial for local development
- Frontend uses nginx on port 80, not 5173 (which is only for dev server)