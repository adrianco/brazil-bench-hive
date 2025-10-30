"""
Brazilian Soccer MCP Server - Configuration Management

CONTEXT:
This module manages all configuration settings for the MCP server, including:
- Neo4j database connection parameters
- Environment variable loading
- Server configuration settings
- Logging configuration

The configuration is loaded from environment variables with sensible defaults
for development. Production deployments should override via .env file.

DEPENDENCIES:
- pydantic: Type-safe configuration with validation
- pydantic-settings: Environment variable loading
- python-dotenv: .env file support

USAGE:
    from src.config import settings

    # Access configuration
    print(settings.neo4j_uri)
    print(settings.neo4j_database)
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import logging


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables with NEO4J_ prefix.
    Example: NEO4J_URI=bolt://localhost:7687
    """

    # Neo4j Database Configuration
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j database connection URI"
    )
    neo4j_user: str = Field(
        default="neo4j",
        description="Neo4j database username"
    )
    neo4j_password: str = Field(
        default="password",
        description="Neo4j database password"
    )
    neo4j_database: str = Field(
        default="brazil-kg",
        description="Neo4j database name (knowledge graph)"
    )

    # Server Configuration
    server_name: str = Field(
        default="brazilian-soccer-mcp",
        description="MCP server name identifier"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # Query Configuration
    max_results: int = Field(
        default=100,
        description="Maximum number of results to return from queries"
    )
    query_timeout: int = Field(
        default=30,
        description="Query timeout in seconds"
    )

    # Cache Configuration (for future enhancement)
    enable_cache: bool = Field(
        default=False,
        description="Enable result caching"
    )
    cache_ttl: int = Field(
        default=300,
        description="Cache time-to-live in seconds"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="NEO4J_",
        case_sensitive=False
    )

    def configure_logging(self) -> None:
        """Configure application logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Global settings instance
settings = Settings()

# Configure logging on module import
settings.configure_logging()

# Create logger for this module
logger = logging.getLogger(__name__)
logger.info(f"Configuration loaded: {settings.server_name}")
logger.debug(f"Neo4j URI: {settings.neo4j_uri}")
logger.debug(f"Neo4j Database: {settings.neo4j_database}")
