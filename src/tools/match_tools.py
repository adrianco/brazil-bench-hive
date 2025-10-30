"""
Brazilian Soccer MCP Server - Match Tools

CONTEXT:
This module implements MCP tools for match-related queries:
- get_match_details: Get detailed information about a specific match
- search_matches: Search for matches by team, date range, or competition
- get_head_to_head: Compare two teams' historical matchups
- get_match_scorers: List all goal scorers in a match

CYPHER PATTERNS:
- MATCH (m:Match) for match nodes
- MATCH (m)-[:PART_OF]->(c:Competition) for competition context
- MATCH (p:Player)-[:SCORED_IN]->(m) for goal scorers
- MATCH (m)-[:PLAYED_AT]->(s:Stadium) for venue information

DEPENDENCIES:
- src.database: Database connection management
- src.models: Data models for type safety

USAGE:
    from src.tools.match_tools import get_match_details, get_head_to_head

    # Get match details
    match = await get_match_details(match_id="M12345")

    # Get head-to-head stats
    h2h = await get_head_to_head(team1_id="T001", team2_id="T002")
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging
from src.database import get_db

logger = logging.getLogger(__name__)


async def get_match_details(match_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific match.

    Args:
        match_id: Unique match identifier

    Returns:
        Dictionary with:
        - Match basic info (teams, score, date)
        - Goal scorers with timestamps
        - Cards (yellow/red)
        - Stadium information
        - Competition context

    Example:
        >>> match = await get_match_details(match_id="M12345")
    """
    db = get_db()
    logger.info(f"Getting details for match: {match_id}")

    # Main match query with teams, competition, and stadium
    match_query = """
    MATCH (m:Match {match_id: $match_id})
    MATCH (home:Team {team_id: m.home_team_id})
    MATCH (away:Team {team_id: m.away_team_id})
    MATCH (m)-[:PART_OF]->(c:Competition)
    OPTIONAL MATCH (m)-[:PLAYED_AT]->(s:Stadium)
    RETURN m.match_id AS match_id,
           m.date AS date,
           m.home_score AS home_score,
           m.away_score AS away_score,
           m.attendance AS attendance,
           m.referee AS referee,
           home.team_id AS home_team_id,
           home.name AS home_team_name,
           away.team_id AS away_team_id,
           away.name AS away_team_name,
           c.name AS competition_name,
           c.season AS season,
           s.name AS stadium_name,
           s.city AS stadium_city
    """

    # Goal scorers query
    scorers_query = """
    MATCH (p:Player)-[s:SCORED_IN]->(m:Match {match_id: $match_id})
    MATCH (t:Team {team_id: s.team_id})
    RETURN p.name AS player_name,
           p.player_id AS player_id,
           t.name AS team_name,
           s.minute AS minute,
           s.goal_type AS goal_type
    ORDER BY s.minute
    """

    # Cards query
    cards_query = """
    MATCH (p:Player)-[c:RECEIVED_CARD]->(m:Match {match_id: $match_id})
    MATCH (p)-[:PLAYS_FOR]->(t:Team)
    RETURN p.name AS player_name,
           p.player_id AS player_id,
           t.name AS team_name,
           c.card_type AS card_type,
           c.minute AS minute,
           c.reason AS reason
    ORDER BY c.minute
    """

    try:
        params = {"match_id": match_id}

        match_result = await db.execute_query(match_query, params)
        if not match_result:
            logger.warning(f"Match not found: {match_id}")
            return {"error": f"Match {match_id} not found"}

        scorers_result = await db.execute_query(scorers_query, params)
        cards_result = await db.execute_query(cards_query, params)

        match_details = {
            "match": match_result[0],
            "scorers": scorers_result,
            "cards": cards_result,
            "total_goals": len(scorers_result),
            "total_cards": len(cards_result)
        }

        logger.info(f"Retrieved details for match {match_id}: {match_result[0]['home_team_name']} vs {match_result[0]['away_team_name']}")
        return match_details

    except Exception as e:
        logger.error(f"Error getting match details: {e}")
        raise


async def search_matches(
    team: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    competition: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for matches with various filters.

    Args:
        team: Team name (home or away)
        date_from: Start date (format: "YYYY-MM-DD")
        date_to: End date (format: "YYYY-MM-DD")
        competition: Competition name
        limit: Maximum number of results (default: 20)

    Returns:
        List of match dictionaries

    Example:
        >>> matches = await search_matches(team="Flamengo", date_from="2023-01-01")
        >>> matches = await search_matches(competition="Brasileirão", date_from="2023-01-01", date_to="2023-12-31")
    """
    db = get_db()
    logger.info(f"Searching matches: team={team}, date_from={date_from}, date_to={date_to}, competition={competition}")

    query_parts = ["MATCH (m:Match)"]
    where_clauses = []
    params = {"limit": limit}

    if team:
        query_parts.append("MATCH (home:Team {team_id: m.home_team_id})")
        query_parts.append("MATCH (away:Team {team_id: m.away_team_id})")
        where_clauses.append("(home.name CONTAINS $team OR away.name CONTAINS $team)")
        params["team"] = team
    else:
        query_parts.append("MATCH (home:Team {team_id: m.home_team_id})")
        query_parts.append("MATCH (away:Team {team_id: m.away_team_id})")

    if competition:
        query_parts.append("MATCH (m)-[:PART_OF]->(c:Competition)")
        where_clauses.append("c.name CONTAINS $competition")
        params["competition"] = competition
    else:
        query_parts.append("OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)")

    if date_from:
        where_clauses.append("date(m.date) >= date($date_from)")
        params["date_from"] = date_from

    if date_to:
        where_clauses.append("date(m.date) <= date($date_to)")
        params["date_to"] = date_to

    query = "\n".join(query_parts)
    if where_clauses:
        query += "\nWHERE " + " AND ".join(where_clauses)

    query += """
    RETURN m.match_id AS match_id,
           m.date AS date,
           home.name AS home_team,
           away.name AS away_team,
           m.home_score AS home_score,
           m.away_score AS away_score,
           c.name AS competition_name,
           c.season AS season
    ORDER BY m.date DESC
    LIMIT $limit
    """

    try:
        results = await db.execute_query(query, params)
        logger.info(f"Found {len(results)} matches matching search criteria")
        return results
    except Exception as e:
        logger.error(f"Error searching matches: {e}")
        raise


async def get_head_to_head(
    team1_id: str,
    team2_id: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get head-to-head statistics between two teams.

    Args:
        team1_id: First team identifier
        team2_id: Second team identifier
        limit: Limit number of recent matches (optional)

    Returns:
        Dictionary with:
        - Overall statistics (wins, draws, losses for each team)
        - Goal statistics
        - Recent matches
        - Largest victories

    Example:
        >>> h2h = await get_head_to_head(team1_id="T001", team2_id="T002")
        >>> h2h = await get_head_to_head(team1_id="T001", team2_id="T002", limit=10)
    """
    db = get_db()
    logger.info(f"Getting head-to-head: {team1_id} vs {team2_id}")

    # Teams info
    teams_query = """
    MATCH (t1:Team {team_id: $team1_id})
    MATCH (t2:Team {team_id: $team2_id})
    RETURN t1.name AS team1_name, t2.name AS team2_name
    """

    # Overall statistics
    stats_query = """
    MATCH (m:Match)
    WHERE (m.home_team_id = $team1_id AND m.away_team_id = $team2_id)
       OR (m.home_team_id = $team2_id AND m.away_team_id = $team1_id)
    WITH m,
         CASE
           WHEN m.home_team_id = $team1_id AND m.home_score > m.away_score THEN 'team1_win'
           WHEN m.away_team_id = $team1_id AND m.away_score > m.home_score THEN 'team1_win'
           WHEN m.home_score = m.away_score THEN 'draw'
           ELSE 'team2_win'
         END AS result,
         CASE WHEN m.home_team_id = $team1_id THEN m.home_score ELSE m.away_score END AS team1_goals,
         CASE WHEN m.home_team_id = $team2_id THEN m.home_score ELSE m.away_score END AS team2_goals
    RETURN
         count(m) AS total_matches,
         sum(CASE WHEN result = 'team1_win' THEN 1 ELSE 0 END) AS team1_wins,
         sum(CASE WHEN result = 'team2_win' THEN 1 ELSE 0 END) AS team2_wins,
         sum(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws,
         sum(team1_goals) AS team1_total_goals,
         sum(team2_goals) AS team2_total_goals
    """

    # Recent matches
    recent_query = """
    MATCH (m:Match)
    WHERE (m.home_team_id = $team1_id AND m.away_team_id = $team2_id)
       OR (m.home_team_id = $team2_id AND m.away_team_id = $team1_id)
    MATCH (home:Team {team_id: m.home_team_id})
    MATCH (away:Team {team_id: m.away_team_id})
    OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)
    RETURN m.match_id AS match_id,
           m.date AS date,
           home.name AS home_team,
           away.name AS away_team,
           m.home_score AS home_score,
           m.away_score AS away_score,
           c.name AS competition
    ORDER BY m.date DESC
    """

    if limit:
        recent_query += f" LIMIT {limit}"

    try:
        params = {"team1_id": team1_id, "team2_id": team2_id}

        teams_result = await db.execute_query(teams_query, params)
        if not teams_result:
            logger.warning(f"One or both teams not found: {team1_id}, {team2_id}")
            return {"error": "One or both teams not found"}

        stats_result = await db.execute_query(stats_query, params)
        recent_result = await db.execute_query(recent_query, params)

        stats = stats_result[0] if stats_result else {
            "total_matches": 0,
            "team1_wins": 0,
            "team2_wins": 0,
            "draws": 0,
            "team1_total_goals": 0,
            "team2_total_goals": 0
        }

        h2h = {
            "team1": {
                "team_id": team1_id,
                "name": teams_result[0]["team1_name"],
                "wins": stats["team1_wins"],
                "goals": stats["team1_total_goals"]
            },
            "team2": {
                "team_id": team2_id,
                "name": teams_result[0]["team2_name"],
                "wins": stats["team2_wins"],
                "goals": stats["team2_total_goals"]
            },
            "total_matches": stats["total_matches"],
            "draws": stats["draws"],
            "recent_matches": recent_result
        }

        logger.info(f"Retrieved head-to-head: {stats['total_matches']} matches between teams")
        return h2h

    except Exception as e:
        logger.error(f"Error getting head-to-head: {e}")
        raise


async def get_match_scorers(match_id: str) -> List[Dict[str, Any]]:
    """
    Get all goal scorers in a specific match.

    Args:
        match_id: Unique match identifier

    Returns:
        List of scorer dictionaries with:
        - Player name and ID
        - Team name
        - Minute scored
        - Goal type

    Example:
        >>> scorers = await get_match_scorers(match_id="M12345")
    """
    db = get_db()
    logger.info(f"Getting scorers for match: {match_id}")

    query = """
    MATCH (p:Player)-[s:SCORED_IN]->(m:Match {match_id: $match_id})
    MATCH (t:Team {team_id: s.team_id})
    RETURN p.player_id AS player_id,
           p.name AS player_name,
           p.position AS position,
           t.team_id AS team_id,
           t.name AS team_name,
           s.minute AS minute,
           s.goal_type AS goal_type
    ORDER BY s.minute
    """

    try:
        results = await db.execute_query(query, {"match_id": match_id})
        logger.info(f"Found {len(results)} goal scorers in match {match_id}")
        return results
    except Exception as e:
        logger.error(f"Error getting match scorers: {e}")
        raise
