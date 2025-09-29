"""
Solution Architect Platform - API Gateway
FastAPI-based API Gateway for the Solution Architect Support Platform
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
from neo4j import GraphDatabase
import logging

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import shared models and utilities
shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'shared')
sys.path.insert(0, shared_path)

try:
    from models import *
    from utils import Config, setup_logging, verify_token, PlatformException
except ImportError:
    # Fallback for development - create minimal implementations
    from pydantic import BaseModel
    from enum import Enum
    import logging
    
    class UserRole(str, Enum):
        ADMIN = "admin"
        ARCHITECT = "architect"
        STAKEHOLDER = "stakeholder"
        VIEWER = "viewer"
    
    class User(BaseModel):
        id: str
        email: str
        name: str
        role: UserRole
    
    class Config:
        def __init__(self):
            self.redis_url = os.getenv("REDIS_URL")
            self.neo4j_uri = os.getenv("NEO4J_URI")
            self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "default-secret-key")
    
    def setup_logging(service_name: str):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(service_name)
    
    def verify_token(token: str, secret: str):
        # Mock verification for development
        return {"sub": "user-123"}
    
    class PlatformException(Exception):
        def __init__(self, message: str, error_code: str = None):
            self.message = message
            self.error_code = error_code
    
    # Additional model classes for development
    class ProjectStatus(str, Enum):
        DRAFT = "draft"
        ACTIVE = "active"
        REVIEW = "review"
        COMPLETED = "completed"
        ARCHIVED = "archived"
    
    class ADRStatus(str, Enum):
        PROPOSED = "proposed"
        ACCEPTED = "accepted"
        DEPRECATED = "deprecated"
        SUPERSEDED = "superseded"
    
    class DiagramType(str, Enum):
        SYSTEM_CONTEXT = "system_context"
        CONTAINER = "container"
        COMPONENT = "component"
        DEPLOYMENT = "deployment"
        SEQUENCE = "sequence"
        FLOWCHART = "flowchart"
    
    class Project(BaseModel):
        id: str
        name: str
        description: Optional[str] = None
        status: ProjectStatus = ProjectStatus.DRAFT
        owner_id: str
        team_members: List[str] = []
        tags: List[str] = []
    
    class ProjectCreate(BaseModel):
        name: str
        description: Optional[str] = None
        team_members: List[str] = []
        tags: List[str] = []
    
    class ADR(BaseModel):
        id: str
        project_id: str
        title: str
        status: ADRStatus = ADRStatus.PROPOSED
        context: str
        decision: str
        consequences: str
        alternatives: Optional[str] = None
        tags: List[str] = []
        created_by: Optional[str] = None
    
    class ADRCreate(BaseModel):
        title: str
        context: str
        decision: str
        consequences: str
        alternatives: Optional[str] = None
        tags: List[str] = []
    
    class Diagram(BaseModel):
        id: str
        project_id: str
        name: str
        type: DiagramType
        content: str
        tags: List[str] = []
    
    class AIRequest(BaseModel):
        type: str
        context: dict
        user_id: str
        project_id: Optional[str] = None
    
    class AISuggestion(BaseModel):
        type: str
        title: str
        description: str
        confidence: float
        reasoning: str
    
    class AIResponse(BaseModel):
        request_id: str
        suggestions: List[AISuggestion]
        processing_time: float
        model_used: str

# Initialize configuration and logging
config = Config()
logger = setup_logging("api-gateway")

# Initialize FastAPI app
app = FastAPI(
    title="Solution Architect Platform API",
    description="API Gateway for the Solution Architect Support Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database connections
redis_client = None
neo4j_driver = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    global redis_client, neo4j_driver
    
    try:
        # Initialize Redis connection
        if config.redis_url:
            redis_client = redis.from_url(config.redis_url)
            redis_client.ping()
            logger.info("Connected to Redis")
        
        # Initialize Neo4j connection
        if config.neo4j_uri:
            neo4j_driver = GraphDatabase.driver(
                config.neo4j_uri,
                auth=(config.neo4j_user, config.neo4j_password)
            )
            # Test connection
            with neo4j_driver.session() as session:
                session.run("RETURN 1")
            logger.info("Connected to Neo4j")
            
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    global redis_client, neo4j_driver
    
    if redis_client:
        redis_client.close()
    if neo4j_driver:
        neo4j_driver.close()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Verify JWT token and return current user"""
    try:
        token = credentials.credentials
        payload = verify_token(token, config.jwt_secret_key)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # TODO: Fetch user from database
        # For now, return a mock user
        return User(
            id=user_id,
            email="john.doe@example.com",
            name="John Doe",
            role=UserRole.ARCHITECT
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Solution Architect Platform API Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Projects endpoints
@app.get("/api/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    """Get all projects for the current user"""
    # Mock data for now
    projects = [
        Project(
            id="550e8400-e29b-41d4-a716-446655440001",
            name="E-commerce Platform",
            description="Scalable e-commerce platform with microservices architecture",
            status=ProjectStatus.ACTIVE,
            owner_id=current_user.id,
            team_members=[current_user.id],
            tags=["microservices", "e-commerce", "kubernetes"]
        ),
        Project(
            id="550e8400-e29b-41d4-a716-446655440002",
            name="Data Analytics Pipeline",
            description="Real-time data processing and analytics platform",
            status=ProjectStatus.DRAFT,
            owner_id=current_user.id,
            team_members=[current_user.id],
            tags=["data", "analytics", "streaming"]
        ),
        Project(
            id="550e8400-e29b-41d4-a716-446655440003",
            name="Mobile Banking App",
            description="Secure mobile banking application with biometric authentication",
            status=ProjectStatus.REVIEW,
            owner_id=current_user.id,
            team_members=[current_user.id],
            tags=["mobile", "banking", "security"]
        )
    ]
    return projects

@app.post("/api/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        team_members=project_data.team_members or [current_user.id],
        tags=project_data.tags
    )
    
    # TODO: Save to database
    logger.info(f"Created project: {project.name} by user: {current_user.email}")
    return project

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific project"""
    # TODO: Fetch from database and check permissions
    if project_id == "550e8400-e29b-41d4-a716-446655440001":
        return Project(
            id=project_id,
            name="E-commerce Platform",
            description="Scalable e-commerce platform with microservices architecture",
            status=ProjectStatus.ACTIVE,
            owner_id=current_user.id,
            team_members=[current_user.id],
            tags=["microservices", "e-commerce", "kubernetes"]
        )
    
    raise HTTPException(status_code=404, detail="Project not found")

# ADRs endpoints
@app.get("/api/projects/{project_id}/adrs", response_model=List[ADR])
async def get_project_adrs(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all ADRs for a project"""
    # Mock data
    adrs = [
        ADR(
            id="adr-001",
            project_id=project_id,
            title="Adopt Microservices Architecture",
            status=ADRStatus.ACCEPTED,
            context="Current monolithic architecture cannot scale to meet growing user base",
            decision="We will adopt a microservices architecture using containerized services",
            consequences="Better scalability but increased operational complexity",
            tags=["architecture", "microservices"]
        ),
        ADR(
            id="adr-002",
            project_id=project_id,
            title="Use Kubernetes for Container Orchestration",
            status=ADRStatus.PROPOSED,
            context="Need container orchestration platform for microservices",
            decision="Use Kubernetes for container orchestration and management",
            consequences="Powerful orchestration but steep learning curve",
            tags=["kubernetes", "containers"]
        )
    ]
    return adrs

@app.post("/api/projects/{project_id}/adrs", response_model=ADR)
async def create_adr(
    project_id: str,
    adr_data: ADRCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new ADR"""
    adr = ADR(
        project_id=project_id,
        title=adr_data.title,
        context=adr_data.context,
        decision=adr_data.decision,
        consequences=adr_data.consequences,
        alternatives=adr_data.alternatives,
        tags=adr_data.tags,
        created_by=current_user.id
    )
    
    # TODO: Save to database
    logger.info(f"Created ADR: {adr.title} for project: {project_id}")
    return adr

# Diagrams endpoints
@app.get("/api/projects/{project_id}/diagrams", response_model=List[Diagram])
async def get_project_diagrams(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all diagrams for a project"""
    # Mock data
    diagrams = [
        Diagram(
            id="diagram-001",
            project_id=project_id,
            name="System Architecture",
            type=DiagramType.SYSTEM_CONTEXT,
            content="""graph TB
    A[Load Balancer] --> B[API Gateway]
    B --> C[User Service]
    B --> D[Product Service]
    B --> E[Order Service]""",
            tags=["architecture", "overview"]
        )
    ]
    return diagrams

# AI Oracle endpoints
@app.post("/api/ai/suggestions")
async def get_ai_suggestions(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions based on context"""
    # Mock AI response
    suggestions = [
        AISuggestion(
            type="pattern",
            title="Consider API Gateway Pattern",
            description="For microservices architecture, an API Gateway provides centralized routing",
            confidence=0.92,
            reasoning="Based on your microservices architecture requirements"
        ),
        AISuggestion(
            type="security",
            title="Implement Circuit Breaker",
            description="Add circuit breaker pattern to prevent cascade failures",
            confidence=0.87,
            reasoning="Common pattern for resilient microservices"
        )
    ]
    
    response = AIResponse(
        request_id=request.user_id,  # Using user_id as request_id for now
        suggestions=suggestions,
        processing_time=0.5,
        model_used="gpt-4"
    )
    
    return response

# Error handlers
@app.exception_handler(PlatformException)
async def platform_exception_handler(request, exc: PlatformException):
    return JSONResponse(
        status_code=400,
        content={"message": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
