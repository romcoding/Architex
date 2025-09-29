# Architex - Solution Architect Support Platform

A comprehensive AI-powered platform designed to support solution architects throughout the entire solution architecture lifecycle, from business problem analysis to implementation guidance.

## 🚀 Vision

Architex transforms how solution architects work by providing an integrated platform that combines intelligent workbench capabilities, knowledge management, AI assistance, and real-time collaboration.

## Architecture Overview

The platform is built as a microservices architecture on Azure with the following components:

```
solution-architect-platform/
├── frontend/                    # React-based Solution Architect Workbench
├── services/
│   ├── api-gateway/            # FastAPI-based API Gateway
│   ├── ai-oracle/              # AI/ML services (NLP, Knowledge Graph, Generative AI)
│   ├── knowledge-hub/          # Neo4j-based knowledge management
│   ├── collaboration-engine/   # Real-time collaboration services
│   └── integration-layer/      # External system integrations
├── infrastructure/             # Azure infrastructure as code
├── shared/                     # Shared libraries and utilities
└── docs/                      # Documentation
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** for component library
- **Monaco Editor** for code/text editing
- **Mermaid** for diagram rendering

### Backend Services
- **Python 3.11** with FastAPI
- **Neo4j** for graph database
- **Redis** for caching and sessions
- **PostgreSQL** for relational data
- **WebSockets** for real-time features

### AI/ML Stack
- **OpenAI API** for generative AI
- **spaCy** for NLP processing
- **scikit-learn** for ML models
- **LangChain** for AI orchestration

### Infrastructure
- **Azure Container Apps** for microservices
- **Azure Cosmos DB** for document storage
- **Azure Service Bus** for messaging
- **Azure Key Vault** for secrets
- **Azure Monitor** for observability

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker
- Azure CLI

### Local Development Setup

1. Clone the repository
2. Set up environment variables
3. Start the development environment:

```bash
# Start all services
docker-compose up -d

# Start frontend development server
cd frontend && npm run dev

# Start individual backend services
cd services/api-gateway && python -m uvicorn main:app --reload
```

## Development Workflow

Each microservice is designed to be independently deployable with its own:
- Dockerfile for containerization
- CI/CD pipeline configuration
- Health checks and monitoring
- API documentation

## Contributing

Please read our [Contributing Guide](docs/CONTRIBUTING.md) for development guidelines and best practices.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
