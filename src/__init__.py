"""
Brazilian Soccer MCP Server

A Model Context Protocol (MCP) server providing access to a Brazilian Soccer
Knowledge Graph stored in Neo4j. Enables natural language queries about players,
teams, matches, competitions, and historical soccer data.

Features:
- Player search and statistics
- Team information and roster
- Match details and results
- Competition standings and top scorers
- Advanced graph analytics (common teammates, rivalries, career paths)

Usage:
    # Run the MCP server
    python -m src.server

    # Or via MCP CLI
    mcp run src/server.py
"""

__version__ = "1.0.0"
__author__ = "Brazilian Soccer MCP Team"
__license__ = "MIT"

from src.config import settings
from src.database import get_db, Neo4jConnection
from src import models

__all__ = [
    "settings",
    "get_db",
    "Neo4jConnection",
    "models",
]
