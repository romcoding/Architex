"""
Solution Architect Platform - Knowledge Hub
Neo4j-based Knowledge Management Service
"""
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import redis
import logging
from pydantic import BaseModel
from enum import Enum

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledge-hub")

# Configuration
class Config:
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

config = Config()

# Pydantic Models
class KnowledgeAssetType(str, Enum):
    PATTERN = "pattern"
    BEST_PRACTICE = "best_practice"
    GUIDELINE = "guideline"
    TEMPLATE = "template"
    CASE_STUDY = "case_study"

class KnowledgeAsset(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    type: KnowledgeAssetType
    category: str
    tags: List[str] = []
    author_id: str
    is_public: bool = False
    usage_count: int = 0
    rating: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class KnowledgeAssetCreate(BaseModel):
    title: str
    content: str
    type: KnowledgeAssetType
    category: str
    tags: List[str] = []
    is_public: bool = False

class KnowledgeAssetUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class SearchQuery(BaseModel):
    query: str
    type: Optional[KnowledgeAssetType] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20

class RelationshipType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    IMPLEMENTS = "IMPLEMENTS"
    EXTENDS = "EXTENDS"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    COMPLEMENTS = "COMPLEMENTS"

class KnowledgeRelationship(BaseModel):
    from_asset_id: str
    to_asset_id: str
    type: RelationshipType
    description: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Hub Service",
    description="Neo4j-based Knowledge Management for Solution Architects",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connections
neo4j_driver = None
redis_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections"""
    global neo4j_driver, redis_client
    
    try:
        # Initialize Neo4j connection
        neo4j_driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password)
        )
        
        # Test Neo4j connection and create constraints
        with neo4j_driver.session() as session:
            # Test connection
            session.run("RETURN 1")
            
            # Create constraints and indexes
            session.run("""
                CREATE CONSTRAINT knowledge_asset_id IF NOT EXISTS
                FOR (ka:KnowledgeAsset) REQUIRE ka.id IS UNIQUE
            """)
            
            session.run("""
                CREATE INDEX knowledge_asset_title IF NOT EXISTS
                FOR (ka:KnowledgeAsset) ON (ka.title)
            """)
            
            session.run("""
                CREATE INDEX knowledge_asset_category IF NOT EXISTS
                FOR (ka:KnowledgeAsset) ON (ka.category)
            """)
            
        logger.info("Connected to Neo4j and created constraints")
        
        # Initialize Redis connection
        if config.redis_url:
            redis_client = redis.from_url(config.redis_url)
            redis_client.ping()
            logger.info("Connected to Redis")
            
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections"""
    global neo4j_driver, redis_client
    
    if neo4j_driver:
        neo4j_driver.close()
    if redis_client:
        redis_client.close()

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "knowledge-hub"
    }

# Knowledge Assets CRUD
@app.post("/api/knowledge/assets", response_model=KnowledgeAsset)
async def create_knowledge_asset(asset_data: KnowledgeAssetCreate, author_id: str = "user-123"):
    """Create a new knowledge asset"""
    
    asset_id = f"ka_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Mock implementation for development (when Neo4j is not available)
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                CREATE (ka:KnowledgeAsset {
                    id: $id,
                    title: $title,
                    content: $content,
                    type: $type,
                    category: $category,
                    tags: $tags,
                    author_id: $author_id,
                    is_public: $is_public,
                    usage_count: 0,
                    rating: 0.0,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                RETURN ka
            """, {
                "id": asset_id,
                "title": asset_data.title,
                "content": asset_data.content,
                "type": asset_data.type.value,
                "category": asset_data.category,
                "tags": asset_data.tags,
                "author_id": author_id,
                "is_public": asset_data.is_public
            })
            
            record = result.single()
            if record:
                node = record["ka"]
                return KnowledgeAsset(
                    id=node["id"],
                    title=node["title"],
                    content=node["content"],
                    type=node["type"],
                    category=node["category"],
                    tags=node["tags"],
                    author_id=node["author_id"],
                    is_public=node["is_public"],
                    usage_count=node["usage_count"],
                    rating=node["rating"],
                    created_at=node["created_at"],
                    updated_at=node["updated_at"]
                )
    except Exception as e:
        logger.warning(f"Neo4j not available, using mock data: {e}")
        # Return mock data for development
        return KnowledgeAsset(
            id=asset_id,
            title=asset_data.title,
            content=asset_data.content,
            type=asset_data.type,
            category=asset_data.category,
            tags=asset_data.tags,
            author_id=author_id,
            is_public=asset_data.is_public,
            usage_count=0,
            rating=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    raise HTTPException(status_code=500, detail="Failed to create knowledge asset")

@app.get("/api/knowledge/assets", response_model=List[KnowledgeAsset])
async def get_knowledge_assets(
    type: Optional[KnowledgeAssetType] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    limit: int = Query(20, le=100)
):
    """Get knowledge assets with optional filtering"""
    
    # Mock data for development
    mock_assets = [
        KnowledgeAsset(
            id="ka_001",
            title="Microservices Architecture Pattern",
            content="A comprehensive guide to implementing microservices architecture...",
            type=KnowledgeAssetType.PATTERN,
            category="Architecture",
            tags=["microservices", "architecture", "scalability"],
            author_id="user-123",
            is_public=True,
            usage_count=45,
            rating=4.8,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        KnowledgeAsset(
            id="ka_002",
            title="API Gateway Best Practices",
            content="Essential best practices for implementing API gateways...",
            type=KnowledgeAssetType.BEST_PRACTICE,
            category="API Design",
            tags=["api", "gateway", "security"],
            author_id="user-123",
            is_public=True,
            usage_count=32,
            rating=4.6,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        KnowledgeAsset(
            id="ka_003",
            title="Database Sharding Strategy",
            content="Guidelines for implementing database sharding for scalability...",
            type=KnowledgeAssetType.GUIDELINE,
            category="Database",
            tags=["database", "sharding", "performance"],
            author_id="user-123",
            is_public=True,
            usage_count=28,
            rating=4.4,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    # Apply filters
    filtered_assets = mock_assets
    
    if type:
        filtered_assets = [a for a in filtered_assets if a.type == type]
    
    if category:
        filtered_assets = [a for a in filtered_assets if a.category == category]
    
    if is_public is not None:
        filtered_assets = [a for a in filtered_assets if a.is_public == is_public]
    
    return filtered_assets[:limit]

@app.get("/api/knowledge/assets/{asset_id}", response_model=KnowledgeAsset)
async def get_knowledge_asset(asset_id: str):
    """Get a specific knowledge asset"""
    
    # Mock data for development
    if asset_id == "ka_001":
        return KnowledgeAsset(
            id="ka_001",
            title="Microservices Architecture Pattern",
            content="A comprehensive guide to implementing microservices architecture...",
            type=KnowledgeAssetType.PATTERN,
            category="Architecture",
            tags=["microservices", "architecture", "scalability"],
            author_id="user-123",
            is_public=True,
            usage_count=46,  # Incremented
            rating=4.8,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    raise HTTPException(status_code=404, detail="Knowledge asset not found")

@app.post("/api/knowledge/search")
async def search_knowledge_assets(search_query: SearchQuery):
    """Search knowledge assets using full-text search and filters"""
    
    # Mock search results
    mock_results = [
        {
            "asset": KnowledgeAsset(
                id="ka_001",
                title="Microservices Architecture Pattern",
                content="A comprehensive guide to implementing microservices architecture...",
                type=KnowledgeAssetType.PATTERN,
                category="Architecture",
                tags=["microservices", "architecture", "scalability"],
                author_id="user-123",
                is_public=True,
                usage_count=45,
                rating=4.8,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            "relevance_score": 2
        }
    ]
    
    # Filter based on query
    query_lower = search_query.query.lower()
    filtered_results = []
    
    for result in mock_results:
        asset = result["asset"]
        if (query_lower in asset.title.lower() or 
            query_lower in asset.content.lower() or
            any(query_lower in tag.lower() for tag in asset.tags)):
            filtered_results.append(result)
    
    return {
        "query": search_query.query,
        "total_results": len(filtered_results),
        "results": filtered_results
    }

@app.get("/api/knowledge/analytics")
async def get_knowledge_analytics():
    """Get knowledge base analytics"""
    
    # Mock analytics data
    return {
        "total_assets": 156,
        "public_assets": 89,
        "private_assets": 67,
        "average_rating": 4.3,
        "total_usage": 2847,
        "category_distribution": [
            {"category": "Architecture", "count": 45},
            {"category": "API Design", "count": 32},
            {"category": "Database", "count": 28},
            {"category": "Security", "count": 25},
            {"category": "Performance", "count": 26}
        ],
        "type_distribution": [
            {"type": "pattern", "count": 62},
            {"type": "best_practice", "count": 48},
            {"type": "guideline", "count": 31},
            {"type": "template", "count": 15}
        ],
        "most_popular_assets": [
            {"id": "ka_001", "title": "Microservices Architecture Pattern", "usage_count": 45},
            {"id": "ka_002", "title": "API Gateway Best Practices", "usage_count": 32},
            {"id": "ka_003", "title": "Database Sharding Strategy", "usage_count": 28}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
