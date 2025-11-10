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

