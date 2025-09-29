"""
Shared data models for the Solution Architect Platform
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class UserRole(str, Enum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    STAKEHOLDER = "stakeholder"
    VIEWER = "viewer"


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


# Base Models
class BaseEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None


# User Models
class User(BaseEntity):
    email: str
    name: str
    role: UserRole
    avatar_url: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole = UserRole.ARCHITECT


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Project Models
class Project(BaseEntity):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    owner_id: UUID
    team_members: List[UUID] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_members: List[UUID] = []
    tags: List[str] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    team_members: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None


# Architecture Decision Record Models
class ADR(BaseEntity):
    project_id: UUID
    title: str
    status: ADRStatus = ADRStatus.PROPOSED
    context: str
    decision: str
    consequences: str
    alternatives: Optional[str] = None
    tags: List[str] = []
    version: int = 1
    superseded_by: Optional[UUID] = None


class ADRCreate(BaseModel):
    project_id: UUID
    title: str
    context: str
    decision: str
    consequences: str
    alternatives: Optional[str] = None
    tags: List[str] = []


class ADRUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ADRStatus] = None
    context: Optional[str] = None
    decision: Optional[str] = None
    consequences: Optional[str] = None
    alternatives: Optional[str] = None
    tags: Optional[List[str]] = None


# Diagram Models
class Diagram(BaseEntity):
    project_id: UUID
    name: str
    type: DiagramType
    content: str  # Mermaid/PlantUML source
    rendered_url: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    version: int = 1


class DiagramCreate(BaseModel):
    project_id: UUID
    name: str
    type: DiagramType
    content: str
    description: Optional[str] = None
    tags: List[str] = []


class DiagramUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


# Knowledge Models
class KnowledgeAsset(BaseEntity):
    title: str
    content: str
    type: str  # pattern, best_practice, guideline, etc.
    category: str
    tags: List[str] = []
    author_id: UUID
    is_public: bool = False
    usage_count: int = 0
    rating: float = 0.0


class KnowledgeAssetCreate(BaseModel):
    title: str
    content: str
    type: str
    category: str
    tags: List[str] = []
    is_public: bool = False


# AI Oracle Models
class AIRequest(BaseModel):
    type: str  # suggestion, generation, analysis
    context: Dict[str, Any]
    user_id: UUID
    project_id: Optional[UUID] = None


class AISuggestion(BaseModel):
    type: str
    title: str
    description: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = {}


class AIResponse(BaseModel):
    request_id: UUID
    suggestions: List[AISuggestion]
    generated_content: Optional[str] = None
    processing_time: float
    model_used: str


# Collaboration Models
class Comment(BaseEntity):
    project_id: UUID
    target_type: str  # adr, diagram, document
    target_id: UUID
    content: str
    author_id: UUID
    parent_id: Optional[UUID] = None  # For threaded comments
    is_resolved: bool = False


class CommentCreate(BaseModel):
    target_type: str
    target_id: UUID
    content: str
    parent_id: Optional[UUID] = None


# Integration Models
class ExternalIntegration(BaseEntity):
    name: str
    type: str  # jira, confluence, github, etc.
    config: Dict[str, Any]
    is_active: bool = True
    project_id: Optional[UUID] = None


class IntegrationCreate(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    project_id: Optional[UUID] = None


# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
