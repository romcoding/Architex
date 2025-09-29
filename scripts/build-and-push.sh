#!/bin/bash

# Solution Architect Platform - Build and Push Script

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
SERVICES=("frontend" "api-gateway" "ai-oracle" "knowledge-hub" "collaboration-engine" "integration-layer")
VERSION=${1:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    echo_error "You are not logged in to Azure. Please log in first."
    exit 1
fi

# Get container registry from environment or Azure
if [ -z "$AZURE_CONTAINER_REGISTRY" ]; then
    echo_error "AZURE_CONTAINER_REGISTRY not set in environment"
    exit 1
fi

REGISTRY_NAME=$(echo $AZURE_CONTAINER_REGISTRY | cut -d'.' -f1)

echo_info "Building and pushing images to: $AZURE_CONTAINER_REGISTRY"
echo_info "Version: $VERSION"

# Login to Azure Container Registry
echo_step "Logging in to Azure Container Registry..."
az acr login --name $REGISTRY_NAME

# Build and push each service
for SERVICE in "${SERVICES[@]}"; do
    echo_step "Building $SERVICE..."
    
    if [ "$SERVICE" = "frontend" ]; then
        DOCKERFILE_PATH="frontend/Dockerfile"
        BUILD_CONTEXT="frontend"
    else
        DOCKERFILE_PATH="services/$SERVICE/Dockerfile"
        BUILD_CONTEXT="services/$SERVICE"
    fi
    
    # Check if Dockerfile exists
    if [ ! -f "$DOCKERFILE_PATH" ]; then
        echo_warn "Dockerfile not found for $SERVICE at $DOCKERFILE_PATH, skipping..."
        continue
    fi
    
    IMAGE_NAME="$AZURE_CONTAINER_REGISTRY/$SERVICE:$VERSION"
    
    echo_info "Building image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH $BUILD_CONTEXT
    
    echo_info "Pushing image: $IMAGE_NAME"
    docker push $IMAGE_NAME
    
    echo_info "✅ Successfully built and pushed $SERVICE"
done

echo_info "🎉 All images built and pushed successfully!"

# Display next steps
echo ""
echo "=== Next Steps ==="
echo "1. Update container apps with new images:"
echo "   ./scripts/update-apps.sh $VERSION"
echo ""
echo "2. Check deployment status:"
echo "   az containerapp list --resource-group $AZURE_RESOURCE_GROUP --output table"
echo ""
echo "3. View logs:"
echo "   az containerapp logs show --name sa-platform-api-gateway --resource-group $AZURE_RESOURCE_GROUP"
