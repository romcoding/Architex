@description('The name of the solution architect platform deployment')
param platformName string = 'sa-platform'

@description('The Azure region for deployment')
param location string = resourceGroup().location

@description('The environment (dev, staging, prod)')
param environment string = 'dev'

@description('The container registry name')
param containerRegistryName string = '${platformName}${environment}acr'

@description('The Log Analytics workspace name')
param logAnalyticsWorkspaceName string = '${platformName}-${environment}-logs'

@description('The Application Insights name')
param applicationInsightsName string = '${platformName}-${environment}-ai'

@description('The Container Apps Environment name')
param containerAppsEnvironmentName string = '${platformName}-${environment}-env'

@description('The Key Vault name')
param keyVaultName string = '${platformName}-${environment}-kv'

@description('The Cosmos DB account name')
param cosmosDbAccountName string = '${platformName}-${environment}-cosmos'

@description('The Service Bus namespace name')
param serviceBusNamespaceName string = '${platformName}-${environment}-sb'

@description('The Redis cache name')
param redisCacheName string = '${platformName}-${environment}-redis'

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
}

// Cosmos DB Account
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosDbAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
  }
}

// Cosmos DB Database
resource cosmosDbDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDbAccount
  name: 'saplatform'
  properties: {
    resource: {
      id: 'saplatform'
    }
  }
}

// Service Bus Namespace
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusNamespaceName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}

// Redis Cache
resource redisCache 'Microsoft.Cache/redis@2023-04-01' = {
  name: redisCacheName
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

// API Gateway Container App
resource apiGatewayApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${platformName}-api-gateway'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
      }
      secrets: [
        {
          name: 'container-registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'container-registry-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api-gateway'
          image: '${containerRegistry.properties.loginServer}/api-gateway:latest'
          env: [
            {
              name: 'DATABASE_URL'
              value: 'cosmosdb://${cosmosDbAccount.properties.documentEndpoint}'
            }
            {
              name: 'REDIS_URL'
              value: 'redis://${redisCache.properties.hostName}:6380'
            }
            {
              name: 'APPLICATION_INSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
}

// AI Oracle Container App
resource aiOracleApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${platformName}-ai-oracle'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
      }
      secrets: [
        {
          name: 'container-registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'container-registry-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'ai-oracle'
          image: '${containerRegistry.properties.loginServer}/ai-oracle:latest'
          env: [
            {
              name: 'REDIS_URL'
              value: 'redis://${redisCache.properties.hostName}:6380'
            }
            {
              name: 'APPLICATION_INSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
          ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

// Frontend Container App
resource frontendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${platformName}-frontend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        allowInsecure: false
      }
      secrets: [
        {
          name: 'container-registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'container-registry-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: '${containerRegistry.properties.loginServer}/frontend:latest'
          env: [
            {
              name: 'REACT_APP_API_URL'
              value: 'https://${apiGatewayApp.properties.configuration.ingress.fqdn}'
            }
          ]
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
}

// Outputs
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output apiGatewayUrl string = 'https://${apiGatewayApp.properties.configuration.ingress.fqdn}'
output keyVaultName string = keyVault.name
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint
output redisCacheHostName string = redisCache.properties.hostName
