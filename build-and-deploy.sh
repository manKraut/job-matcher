#!/bin/bash

# Script to build and deploy to minikube
set -e

echo "🔧 Setting up minikube docker environment..."
eval $(minikube docker-env)

echo "🏗️  Building backend image..."
cd backend
docker build -t job-matcher-backend:latest .
cd ..

echo "🏗️  Building frontend image..."
cd frontend
docker build -t job-matcher-frontend:latest .
cd ..

echo "✅ Images built successfully!"
echo ""
echo "📦 Deploying to minikube..."

# Create secret if it doesn't exist (optional - edit with your actual key)
if ! kubectl get secret openai-secret &>/dev/null; then
  echo "⚠️  OpenAI secret not found. Creating placeholder secret..."
  echo "   Edit k8s/openai-secret.yaml with your actual API key, then run:"
  echo "   kubectl apply -f k8s/openai-secret.yaml"
  echo ""
  kubectl create secret generic openai-secret \
    --from-literal=api-key='placeholder-key' \
    --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
fi

kubectl apply -f k8s/

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To check status:"
echo "  kubectl get pods"
echo "  kubectl get services"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/backend-deployment"
echo "  kubectl logs -f deployment/frontend-deployment"

