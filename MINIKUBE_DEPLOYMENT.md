# Minikube Deployment Guide

## Fixed Issues

1. **Added `imagePullPolicy: Never`** - This tells Kubernetes to use local images instead of trying to pull from a registry
2. **Fixed frontend port** - Changed from 5173 to 80 (nginx serves on port 80)
3. **Added `:latest` tag** - Explicitly tags images for consistency

## Quick Deploy

Use the provided script:
```bash
./build-and-deploy.sh
```

## Manual Steps

If you prefer to do it manually:

1. **Set minikube docker environment:**
   ```bash
   eval $(minikube docker-env)
   ```

2. **Build backend image:**
   ```bash
   cd backend
   docker build -t job-matcher-backend:latest .
   cd ..
   ```

3. **Build frontend image:**
   ```bash
   cd frontend
   docker build -t job-matcher-frontend:latest .
   cd ..
   ```

4. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f k8s/
   ```

## Verify Deployment

Check pod status:
```bash
kubectl get pods
```

Check services:
```bash
kubectl get services
```

View logs:
```bash
kubectl logs -f deployment/backend-deployment
kubectl logs -f deployment/frontend-deployment
```

## Troubleshooting

If you still get `ErrImagePull`:

1. **Verify images exist in minikube:**
   ```bash
   eval $(minikube docker-env)
   docker images | grep job-matcher
   ```

2. **Delete and recreate deployments:**
   ```bash
   kubectl delete -f k8s/
   kubectl apply -f k8s/
   ```

3. **Check pod events:**
   ```bash
   kubectl describe pod <pod-name>
   ```

4. **Make sure minikube is running:**
   ```bash
   minikube status
   ```

## Important Notes

- Always run `eval $(minikube docker-env)` before building images
- The `imagePullPolicy: Never` is crucial for local development
- Frontend uses nginx on port 80, not 5173 (which is only for dev server)

