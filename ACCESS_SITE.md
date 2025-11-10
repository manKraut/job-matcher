# How to Access Your Site in Minikube

## Option 1: Using Port Forward (Easiest for Testing)

Forward the frontend service to your local machine:

```bash
# Forward frontend (runs in background)
kubectl port-forward service/frontend-service 8080:80

# In another terminal, forward backend
kubectl port-forward service/backend-service 8000:8000
```

Then access:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000

**Note**: You'll need to update the frontend code to use `http://localhost:8000` instead of `http://localhost:8000/api/agents/...` OR keep the backend port-forward and update frontend API calls.

## Option 2: Using Minikube Tunnel (Recommended)

This exposes services as if they were LoadBalancer type:

```bash
# Start tunnel (runs in background)
minikube tunnel

# In another terminal, check the external IP
kubectl get services
```

Then access via the external IP shown.

## Option 3: Using Ingress (Production-like)

Your ingress is configured for `jobmatcher.local`:

1. **Get the minikube IP:**
   ```bash
   minikube ip
   ```

2. **Add to /etc/hosts:**
   ```bash
   sudo nano /etc/hosts
   # Add this line (replace IP with your minikube IP):
   192.168.49.2 jobmatcher.local
   ```

3. **Access the site:**
   - Frontend: http://jobmatcher.local
   - Backend API: http://jobmatcher.local/api

## Option 4: Quick Test with Port Forward (All-in-one)

```bash
# Terminal 1: Frontend
kubectl port-forward service/frontend-service 8080:80

# Terminal 2: Backend  
kubectl port-forward service/backend-service 8000:8000
```

Then open http://localhost:8080 in your browser.

## Check Pod Status

```bash
# Check all pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress
```

## Troubleshooting

If frontend can't reach backend:

1. **Check if pods are running:**
   ```bash
   kubectl get pods
   ```

2. **Check service endpoints:**
   ```bash
   kubectl get endpoints
   ```

3. **Test backend directly:**
   ```bash
   kubectl port-forward service/backend-service 8000:8000
   curl http://localhost:8000/
   ```

4. **Check frontend logs:**
   ```bash
   kubectl logs -l app=frontend
   ```

5. **Check backend logs:**
   ```bash
   kubectl logs -l app=backend
   ```

