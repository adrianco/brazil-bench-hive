"""
Brazilian Soccer MCP Server - Player Tools

CONTEXT:
This module implements MCP tools for player-related queries:
- search_player: Find players by name, team, or position
- get_player_stats: Retrieve player statistics for a season
- get_player_career: Get complete career history
- get_player_transfers: List all transfers for a player

CYPHER PATTERNS:
- MATCH (p:Player) for player nodes
- MATCH (p)-[:PLAYS_FOR]->(t:Team) for team relationships
- MATCH (p)-[:SCORED_IN]->(m:Match) for goals
- MATCH (p)-[:TRANSFERRED_FROM|TRANSFERRED_TO] for transfers

DEPENDENCIES:
- src.database: Database connection management
- src.models: Data models for type safety
- src.config: Configuration settings

USAGE:
    from src.tools.player_tools import search_player, get_player_stats

    # Search for players
    players = await search_player(name="Neymar")

    # Get player statistics
    stats = await get_player_stats(player_id="P12345", season="2023")
"""

from typing import List, Optional, Dict, Any
import logging
from src.database import get_db
from src.models import Player, PlayerStats, PlayerCareer, PlaysFor, Transfer
from src.config import settings

logger = logging.getLogger(__name__)


async def search_player(
    name: str,
    team: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for players by name, optionally filtering by team and position.

    Args:
        name: Player name (partial match supported)
        team: Team name to filter by (optional)
        position: Position to filter by (optional)
        limit: Maximum number of results (default: 10)

    Returns:
        List of player dictionaries with basic information

    Example:
        >>> players = await search_player(name="Neymar")
        >>> players = await search_player(name="Silva", team="Flamengo")
    """
    db = get_db()
    logger.info(f"Searching for player: name={name}, team={team}, position={position}")

    # Build dynamic query based on filters
    query_parts = ["MATCH (p:Player)"]
    where_clauses = ["p.name CONTAINS $name"]
    params = {"name": name, "limit": limit}

    if team:
        query_parts.append("MATCH (p)-[:PLAYS_FOR]->(t:Team)")
        where_clauses.append("t.name CONTAINS $team")
        params["team"] = team

    if position:
        where_clauses.append("p.position = $position")
        params["position"] = position

    query = "\n".join(query_parts)
    if where_clauses:
        query += "\nWHERE " + " AND ".join(where_clauses)

    query += """
    RETURN p.player_id AS player_id,
           p.name AS name,
           p.birth_date AS birth_date,
           p.nationality AS nationality,
           p.position AS position,
           p.jersey_number AS jersey_number
    LIMIT $limit
    """

    try:
        results = await db.execute_query(query, params)
        logger.info(f"Found {len(results)} players matching search criteria")
        return results
    except Exception as e:
        logger.error(f"Error searching for players: {e}")
        raise


async def get_player_stats(
    player_id: str,
    season: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a player.

    Args:
        player_id: Unique player identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Dictionary with player statistics including:
        - Total goals, assists, matches
        - Yellow and red cards
        - Teams played for

    Example:
        >>> stats = await get_player_stats(player_id="P12345")
        >>> stats = await get_player_stats(player_id="P12345", season="2023")
    """
    db = get_db()
    logger.info(f"Getting stats for player: {player_id}, season: {season}")

    # Base player info query
    player_query = """
    MATCH (p:Player {player_id: $player_id})
    RETURN p.player_id AS player_id,
           p.name AS name,
           p.position AS position
    """

    # Goals query
    goals_query = """
    MATCH (p:Player {player_id: $player_id})-[s:SCORED_IN]->(m:Match)
    """
    if season:
        goals_query += """-[:PART_OF]->(c:Competition {season: $season})"""
    goals_query += """
    RETURN count(s) AS total_goals
    """

    # Assists query
    assists_query = """
    MATCH (p:Player {player_id: $player_id})-[a:ASSISTED_IN]->(m:Match)
    """
    if season:
        assists_query += """-[:PART_OF]->(c:Competition {season: $season})"""
    assists_query += """
    RETURN count(a) AS total_assists
    """

    # Matches played query
    matches_query = """
    MATCH (p:Player {player_id: $player_id})-[:PLAYED_IN]->(m:Match)
    """
    if season:
        matches_query += """-[:PART_OF]->(c:Competition {season: $season})"""
    matches_query += """
    RETURN count(DISTINCT m) AS total_matches
    """

    # Cards query
    cards_query = """
    MATCH (p:Player {player_id: $player_id})-[c:RECEIVED_CARD]->(m:Match)
    """
    if season:
        cards_query += """-[:PART_OF]->(comp:Competition {season: $season})"""
    cards_query += """
    RETURN c.card_type AS card_type, count(c) AS count
    """

    # Teams query
    teams_query = """
    MATCH (p:Player {player_id: $player_id})-[pf:PLAYS_FOR]->(t:Team)
    RETURN t.name AS team_name,
           pf.from_date AS from_date,
           pf.to_date AS to_date
    ORDER BY pf.from_date DESC
    """

    try:
        params = {"player_id": player_id}
        if season:
            params["season"] = season

        # Execute all queries
        player_result = await db.execute_query(player_query, params)
        if not player_result:
            logger.warning(f"Player not found: {player_id}")
            return {"error": f"Player {player_id} not found"}

        goals_result = await db.execute_query(goals_query, params)
        assists_result = await db.execute_query(assists_query, params)
        matches_result = await db.execute_query(matches_query, params)
        cards_result = await db.execute_query(cards_query, params)
        teams_result = await db.execute_query(teams_query, params)

        # Process cards
        yellow_cards = 0
        red_cards = 0
        for card in cards_result:
            if card.get("card_type") == "Yellow":
                yellow_cards = card.get("count", 0)
            elif card.get("card_type") == "Red":
                red_cards = card.get("count", 0)

        # Build stats response
        stats = {
            "player_id": player_result[0]["player_id"],
            "player_name": player_result[0]["name"],
            "position": player_result[0].get("position"),
            "season": season,
            "total_goals": goals_result[0].get("total_goals", 0) if goals_result else 0,
            "total_assists": assists_result[0].get("total_assists", 0) if assists_result else 0,
            "total_matches": matches_result[0].get("total_matches", 0) if matches_result else 0,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "teams": [t["team_name"] for t in teams_result]
        }

        logger.info(f"Retrieved stats for player {player_id}: {stats['total_goals']} goals, {stats['total_matches']} matches")
        return stats

    except Exception as e:
        logger.error(f"Error getting player stats: {e}")
        raise


async def get_player_career(player_id: str) -> Dict[str, Any]:
    """
    Get complete career history for a player.

    Args:
        player_id: Unique player identifier

    Returns:
        Dictionary with:
        - Player basic information
        - All teams played for (with dates)
        - All transfers (with fees and dates)
        - Career statistics

    Example:
        >>> career = await get_player_career(player_id="P12345")
    """
    db = get_db()
    logger.info(f"Getting career history for player: {player_id}")

    # Get player info with teams
    query = """
    MATCH (p:Player {player_id: $player_id})
    OPTIONAL MATCH (p)-[pf:PLAYS_FOR]->(t:Team)
    OPTIONAL MATCH (p)-[tf:TRANSFERRED_FROM]->(from_team:Team)
    OPTIONAL MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
    WHERE tf.transfer_date = tt.transfer_date
    RETURN p,
           collect(DISTINCT {
               team_id: t.team_id,
               team_name: t.name,
               from_date: pf.from_date,
               to_date: pf.to_date,
               jersey_number: pf.jersey_number
           }) AS teams,
           collect(DISTINCT {
               from_team: from_team.name,
               to_team: to_team.name,
               transfer_date: tf.transfer_date,
               fee: tf.fee,
               loan: tf.loan
           }) AS transfers
    """

    try:
        result = await db.execute_query(query, {"player_id": player_id})

        if not result:
            logger.warning(f"Player not found: {player_id}")
            return {"error": f"Player {player_id} not found"}

        player_data = result[0]

        # Get career stats (all-time)
        stats = await get_player_stats(player_id)

        career = {
            "player": player_data["p"],
            "teams": [t for t in player_data["teams"] if t.get("team_name")],
            "transfers": [t for t in player_data["transfers"] if t.get("from_team")],
            "career_stats": stats
        }

        logger.info(f"Retrieved career for player {player_id}: {len(career['teams'])} teams")
        return career

    except Exception as e:
        logger.error(f"Error getting player career: {e}")
        raise


async def get_player_transfers(
    player_id: str,
    year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all transfers for a player.

    Args:
        player_id: Unique player identifier
        year: Filter by specific year (optional)

    Returns:
        List of transfer dictionaries with:
        - from_team, to_team
        - transfer_date, fee, loan status

    Example:
        >>> transfers = await get_player_transfers(player_id="P12345")
        >>> transfers = await get_player_transfers(player_id="P12345", year=2023)
    """
    db = get_db()
    logger.info(f"Getting transfers for player: {player_id}, year: {year}")

    query = """
    MATCH (p:Player {player_id: $player_id})-[tf:TRANSFERRED_FROM]->(from_team:Team)
    MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
    WHERE tf.transfer_date = tt.transfer_date
    """

    params = {"player_id": player_id}
    if year:
        query += " AND date(tf.transfer_date).year = $year"
        params["year"] = year

    query += """
    RETURN from_team.name AS from_team,
           to_team.name AS to_team,
           tf.transfer_date AS transfer_date,
           tf.fee AS fee,
           tf.loan AS loan
    ORDER BY tf.transfer_date DESC
    """

    try:
        results = await db.execute_query(query, params)
        logger.info(f"Found {len(results)} transfers for player {player_id}")
        return results
    except Exception as e:
        logger.error(f"Error getting player transfers: {e}")
        raise
