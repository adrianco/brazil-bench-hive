"""
Brazilian Soccer MCP Server - Tools Package

CONTEXT:
This package contains all MCP tool implementations for querying the Brazilian
Soccer Knowledge Graph. Tools are organized by entity type:

- player_tools: Player search, stats, career, transfers
- team_tools: Team search, roster, stats, history
- match_tools: Match details, search, head-to-head, scorers
- competition_tools: Standings, top scorers, competition matches
- analysis_tools: Advanced analytics and graph traversal queries

Each tool module provides async functions that interact with Neo4j to
retrieve and analyze soccer data.
"""

__all__ = [
    "player_tools",
    "team_tools",
    "match_tools",
    "competition_tools",
    "analysis_tools"
]
