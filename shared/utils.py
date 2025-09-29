"""
Shared utilities for the Solution Architect Platform
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


# JWT Token handling
def create_access_token(
    data: Dict[str, Any], 
    secret_key: str, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


# Content hashing for change detection
def generate_content_hash(content: str) -> str:
    """Generate a hash for content to detect changes"""
    return hashlib.sha256(content.encode()).hexdigest()


# Slug generation
def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from text"""
    import re
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:max_length].strip('-')


# Validation utilities
def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_html(content: str) -> str:
    """Basic HTML sanitization"""
    import html
    return html.escape(content)


# File utilities
def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def is_allowed_file_type(filename: str, allowed_types: list) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in allowed_types


# Date utilities
def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string"""
    return datetime.strptime(dt_str, format_str)


# Configuration utilities
class Config:
    """Configuration management"""
    
    def __init__(self):
        import os
        self.database_url = os.getenv("DATABASE_URL")
        self.redis_url = os.getenv("REDIS_URL")
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USER")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "default-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"


# Logging utilities
def setup_logging(service_name: str, log_level: str = "INFO"):
    """Setup logging configuration"""
    import logging
    import sys
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=f'%(asctime)s - {service_name} - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(service_name)


# Error handling
class PlatformException(Exception):
    """Base exception for platform errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(PlatformException):
    """Validation error"""
    pass


class AuthenticationError(PlatformException):
    """Authentication error"""
    pass


class AuthorizationError(PlatformException):
    """Authorization error"""
    pass


class NotFoundError(PlatformException):
    """Resource not found error"""
    pass
