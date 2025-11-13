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