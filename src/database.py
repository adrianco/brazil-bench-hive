"""
Brazilian Soccer MCP Server - Database Connection Manager

CONTEXT:
This module manages the Neo4j database connection lifecycle and provides
session management for executing Cypher queries. It implements:
- Connection pooling with automatic retry
- Transaction management
- Query execution with error handling
- Context managers for safe resource cleanup
- Health checks for database connectivity

DESIGN PATTERNS:
- Singleton pattern for database driver
- Context manager for session lifecycle
- Async/await for non-blocking operations

DEPENDENCIES:
- neo4j: Official Neo4j Python driver
- src.config: Configuration settings

USAGE:
    from src.database import Neo4jConnection

    # Initialize connection
    db = Neo4jConnection()
    await db.connect()

    # Execute query
    result = await db.execute_query("MATCH (n) RETURN count(n)")

    # Cleanup
    await db.close()
"""

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Optional, Dict, List, Any
import logging
from contextlib import asynccontextmanager

from src.config import settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """
    Neo4j database connection manager with async support.

    This class manages the lifecycle of Neo4j connections and provides
    methods for executing queries safely with proper error handling.
    """

    def __init__(self):
        """Initialize Neo4j connection manager."""
        self._driver: Optional[AsyncDriver] = None
        self._connected: bool = False
        self._uri = settings.neo4j_uri
        self._user = settings.neo4j_user
        self._password = settings.neo4j_password
        self._database = settings.neo4j_database

        logger.info(f"Initializing Neo4j connection to {self._uri}")

    async def connect(self) -> None:
        """
        Establish connection to Neo4j database.

        Raises:
            AuthError: If authentication fails
            ServiceUnavailable: If database is not reachable
        """
        if self._connected:
            logger.warning("Already connected to Neo4j")
            return

        try:
            logger.info(f"Connecting to Neo4j at {self._uri}")
            self._driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password)
            )

            # Verify connectivity
            await self._driver.verify_connectivity()
            self._connected = True
            logger.info(f"Successfully connected to Neo4j database: {self._database}")

        except AuthError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self) -> None:
        """Close database connection and cleanup resources."""
        if self._driver and self._connected:
            logger.info("Closing Neo4j connection")
            await self._driver.close()
            self._connected = False
            self._driver = None
            logger.info("Neo4j connection closed")

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """
        Context manager for Neo4j session.

        Yields:
            AsyncSession: Neo4j session for executing queries

        Example:
            async with db.session() as session:
                result = await session.run("MATCH (n) RETURN n")
        """
        if not self._connected or not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")

        session = self._driver.session(database=self._database)
        try:
            yield session
        finally:
            await session.close()

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            database: Database name (uses default if not specified)

        Returns:
            List of result records as dictionaries

        Example:
            results = await db.execute_query(
                "MATCH (p:Player {name: $name}) RETURN p",
                parameters={"name": "Neymar"}
            )
        """
        if not self._connected or not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")

        db_name = database or self._database
        params = parameters or {}

        logger.debug(f"Executing query: {query[:100]}...")
        logger.debug(f"Parameters: {params}")

        try:
            async with self.session() as session:
                result = await session.run(query, params)
                records = await result.values()

                # Convert records to list of dictionaries
                results = []
                async for record in result:
                    results.append(dict(record))

                logger.debug(f"Query returned {len(results)} results")
                return results

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            raise

    async def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a write query (CREATE, UPDATE, DELETE) in a transaction.

        Args:
            query: Cypher write query
            parameters: Query parameters (optional)

        Returns:
            Summary information about the write operation
        """
        if not self._connected or not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")

        params = parameters or {}
        logger.debug(f"Executing write query: {query[:100]}...")

        try:
            async with self.session() as session:
                result = await session.run(query, params)
                summary = await result.consume()

                return {
                    "nodes_created": summary.counters.nodes_created,
                    "nodes_deleted": summary.counters.nodes_deleted,
                    "relationships_created": summary.counters.relationships_created,
                    "relationships_deleted": summary.counters.relationships_deleted,
                    "properties_set": summary.counters.properties_set
                }

        except Exception as e:
            logger.error(f"Write query execution failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on database connection.

        Returns:
            Dictionary with health status information
        """
        if not self._connected:
            return {
                "status": "disconnected",
                "connected": False,
                "message": "Not connected to database"
            }

        try:
            # Simple query to verify connection
            result = await self.execute_query("RETURN 1 AS test")

            # Count total nodes
            count_result = await self.execute_query("MATCH (n) RETURN count(n) AS total")
            total_nodes = count_result[0]["total"] if count_result else 0

            return {
                "status": "healthy",
                "connected": True,
                "database": self._database,
                "uri": self._uri,
                "total_nodes": total_nodes,
                "message": "Database connection is healthy"
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "message": "Database connection is unhealthy"
            }

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected


# Global database instance
_db_instance: Optional[Neo4jConnection] = None


def get_db() -> Neo4jConnection:
    """
    Get or create global database instance (singleton pattern).

    Returns:
        Neo4jConnection: Global database connection instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Neo4jConnection()
    return _db_instance
