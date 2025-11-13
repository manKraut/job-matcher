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