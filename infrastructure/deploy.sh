#!/bin/bash

# Solution Architect Platform - Azure Deployment Script

set -e

# Configuration
RESOURCE_GROUP_NAME="rg-sa-platform"
LOCATION="eastus"
ENVIRONMENT="dev"
PLATFORM_NAME="sa-platform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo_warn "You are not logged in to Azure. Please log in first."
    az login
fi

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo_info "Using subscription: $SUBSCRIPTION_ID"

# Create resource group if it doesn't exist
echo_info "Creating resource group: $RESOURCE_GROUP_NAME"
az group create \
    --name $RESOURCE_GROUP_NAME \
    --location $LOCATION \
    --output table

# Deploy the infrastructure
echo_info "Deploying infrastructure..."
DEPLOYMENT_NAME="sa-platform-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file main.bicep \
    --parameters \
        platformName=$PLATFORM_NAME \
        environment=$ENVIRONMENT \
        location=$LOCATION \
    --name $DEPLOYMENT_NAME \
    --output table

# Get deployment outputs
echo_info "Getting deployment outputs..."
CONTAINER_REGISTRY=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs.containerRegistryLoginServer.value \
    -o tsv)

FRONTEND_URL=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs.frontendUrl.value \
    -o tsv)

API_GATEWAY_URL=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs.apiGatewayUrl.value \
    -o tsv)

KEY_VAULT_NAME=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs.keyVaultName.value \
    -o tsv)

# Display results
echo_info "Deployment completed successfully!"
echo ""
echo "=== Deployment Information ==="
echo "Resource Group: $RESOURCE_GROUP_NAME"
echo "Container Registry: $CONTAINER_REGISTRY"
echo "Frontend URL: $FRONTEND_URL"
echo "API Gateway URL: $API_GATEWAY_URL"
echo "Key Vault: $KEY_VAULT_NAME"
echo ""

# Create .env file for local development
echo_info "Creating .env file for local development..."
cat > ../.env << EOF
# Azure Configuration
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP_NAME
AZURE_CONTAINER_REGISTRY=$CONTAINER_REGISTRY
AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME

# Application URLs
FRONTEND_URL=$FRONTEND_URL
API_GATEWAY_URL=$API_GATEWAY_URL

# Environment
ENVIRONMENT=$ENVIRONMENT
EOF

echo_info ".env file created successfully!"

# Instructions for next steps
echo ""
echo "=== Next Steps ==="
echo "1. Build and push container images:"
echo "   cd .. && ./scripts/build-and-push.sh"
echo ""
echo "2. Configure secrets in Key Vault:"
echo "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name openai-api-key --value 'your-openai-key'"
echo ""
echo "3. Update container apps with new images:"
echo "   ./scripts/update-apps.sh"
echo ""
echo "4. Access your application:"
echo "   Frontend: $FRONTEND_URL"
echo "   API: $API_GATEWAY_URL"
