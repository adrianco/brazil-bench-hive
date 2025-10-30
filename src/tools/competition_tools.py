"""
Brazilian Soccer MCP Server - Competition Tools

CONTEXT:
This module implements MCP tools for competition-related queries:
- get_competition_standings: Get league table/standings
- get_competition_top_scorers: List top goal scorers in a competition
- get_competition_matches: Get all matches in a competition

CYPHER PATTERNS:
- MATCH (c:Competition) for competition nodes
- MATCH (m:Match)-[:PART_OF]->(c) for competition matches
- MATCH (p:Player)-[:SCORED_IN]->(m)-[:PART_OF]->(c) for scorers
- Aggregation for standings calculation

DEPENDENCIES:
- src.database: Database connection management
- src.models: Data models for type safety

USAGE:
    from src.tools.competition_tools import get_competition_standings

    # Get standings
    standings = await get_competition_standings(
        competition_id="C001",
        season="2023"
    )
"""

from typing import List, Optional, Dict, Any
import logging
from src.database import get_db

logger = logging.getLogger(__name__)


async def get_competition_standings(
    competition_id: str,
    season: str
) -> Dict[str, Any]:
    """
    Get league standings/table for a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")

    Returns:
        Dictionary with:
        - Competition information
        - Standings table with points, wins, draws, losses
        - Goal statistics for each team

    Example:
        >>> standings = await get_competition_standings(
        ...     competition_id="C001",
        ...     season="2023"
        ... )
    """
    db = get_db()
    logger.info(f"Getting standings for competition: {competition_id}, season: {season}")

    # Competition info
    comp_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    RETURN c.competition_id AS competition_id,
           c.name AS name,
           c.season AS season,
           c.type AS type
    """

    # Calculate standings
    standings_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    MATCH (m:Match)-[:PART_OF]->(c)
    MATCH (t:Team)
    WHERE t.team_id = m.home_team_id OR t.team_id = m.away_team_id
    WITH t, m,
         CASE WHEN m.home_team_id = t.team_id THEN m.home_score ELSE m.away_score END AS goals_for,
         CASE WHEN m.home_team_id = t.team_id THEN m.away_score ELSE m.home_score END AS goals_against,
         CASE
           WHEN m.home_team_id = t.team_id AND m.home_score > m.away_score THEN 3
           WHEN m.away_team_id = t.team_id AND m.away_score > m.home_score THEN 3
           WHEN m.home_score = m.away_score THEN 1
           ELSE 0
         END AS points,
         CASE
           WHEN m.home_team_id = t.team_id AND m.home_score > m.away_score THEN 1
           WHEN m.away_team_id = t.team_id AND m.away_score > m.home_score THEN 1
           ELSE 0
         END AS wins,
         CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END AS draws,
         CASE
           WHEN m.home_team_id = t.team_id AND m.home_score < m.away_score THEN 1
           WHEN m.away_team_id = t.team_id AND m.away_score < m.home_score THEN 1
           ELSE 0
         END AS losses
    WITH t.team_id AS team_id,
         t.name AS team_name,
         count(m) AS played,
         sum(wins) AS wins,
         sum(draws) AS draws,
         sum(losses) AS losses,
         sum(goals_for) AS goals_for,
         sum(goals_against) AS goals_against,
         sum(points) AS points
    RETURN team_id,
           team_name,
           played,
           wins,
           draws,
           losses,
           goals_for,
           goals_against,
           goals_for - goals_against AS goal_difference,
           points
    ORDER BY points DESC, goal_difference DESC, goals_for DESC
    """

    try:
        params = {"competition_id": competition_id, "season": season}

        comp_result = await db.execute_query(comp_query, params)
        if not comp_result:
            logger.warning(f"Competition not found: {competition_id} season {season}")
            return {"error": f"Competition {competition_id} season {season} not found"}

        standings_result = await db.execute_query(standings_query, params)

        # Add position numbers
        for idx, team in enumerate(standings_result, start=1):
            team["position"] = idx

        standings = {
            "competition": comp_result[0],
            "standings": standings_result,
            "total_teams": len(standings_result)
        }

        logger.info(f"Retrieved standings for {competition_id} {season}: {len(standings_result)} teams")
        return standings

    except Exception as e:
        logger.error(f"Error getting competition standings: {e}")
        raise


async def get_competition_top_scorers(
    competition_id: str,
    season: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get top goal scorers in a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")
        limit: Maximum number of scorers to return (default: 20)

    Returns:
        Dictionary with:
        - Competition information
        - List of top scorers with goal counts

    Example:
        >>> top_scorers = await get_competition_top_scorers(
        ...     competition_id="C001",
        ...     season="2023",
        ...     limit=10
        ... )
    """
    db = get_db()
    logger.info(f"Getting top scorers for competition: {competition_id}, season: {season}")

    # Competition info
    comp_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    RETURN c.competition_id AS competition_id,
           c.name AS name,
           c.season AS season
    """

    # Top scorers query
    scorers_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    MATCH (m:Match)-[:PART_OF]->(c)
    MATCH (p:Player)-[s:SCORED_IN]->(m)
    MATCH (t:Team {team_id: s.team_id})
    WITH p, t, count(s) AS goals
    RETURN p.player_id AS player_id,
           p.name AS player_name,
           p.position AS position,
           t.name AS team_name,
           goals
    ORDER BY goals DESC, p.name
    LIMIT $limit
    """

    try:
        params = {"competition_id": competition_id, "season": season, "limit": limit}

        comp_result = await db.execute_query(comp_query, params)
        if not comp_result:
            logger.warning(f"Competition not found: {competition_id} season {season}")
            return {"error": f"Competition {competition_id} season {season} not found"}

        scorers_result = await db.execute_query(scorers_query, params)

        # Add rank numbers
        for idx, scorer in enumerate(scorers_result, start=1):
            scorer["rank"] = idx

        top_scorers = {
            "competition": comp_result[0],
            "top_scorers": scorers_result,
            "total_scorers": len(scorers_result)
        }

        logger.info(f"Retrieved top scorers for {competition_id} {season}: {len(scorers_result)} players")
        return top_scorers

    except Exception as e:
        logger.error(f"Error getting competition top scorers: {e}")
        raise


async def get_competition_matches(
    competition_id: str,
    season: str,
    team: Optional[str] = None,
    round: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get all matches in a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")
        team: Filter by specific team (optional)
        round: Filter by specific round/matchday (optional)

    Returns:
        Dictionary with:
        - Competition information
        - List of matches with results

    Example:
        >>> matches = await get_competition_matches(
        ...     competition_id="C001",
        ...     season="2023"
        ... )
        >>> matches = await get_competition_matches(
        ...     competition_id="C001",
        ...     season="2023",
        ...     team="Flamengo"
        ... )
    """
    db = get_db()
    logger.info(f"Getting matches for competition: {competition_id}, season: {season}, team: {team}")

    # Competition info
    comp_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    RETURN c.competition_id AS competition_id,
           c.name AS name,
           c.season AS season,
           c.type AS type
    """

    # Matches query
    matches_query = """
    MATCH (c:Competition {competition_id: $competition_id, season: $season})
    MATCH (m:Match)-[:PART_OF]->(c)
    MATCH (home:Team {team_id: m.home_team_id})
    MATCH (away:Team {team_id: m.away_team_id})
    """

    params = {"competition_id": competition_id, "season": season}
    where_clauses = []

    if team:
        where_clauses.append("(home.name CONTAINS $team OR away.name CONTAINS $team)")
        params["team"] = team

    if round is not None:
        where_clauses.append("m.round = $round")
        params["round"] = round

    if where_clauses:
        matches_query += "\nWHERE " + " AND ".join(where_clauses)

    matches_query += """
    RETURN m.match_id AS match_id,
           m.date AS date,
           home.name AS home_team,
           away.name AS away_team,
           m.home_score AS home_score,
           m.away_score AS away_score,
           m.round AS round,
           m.attendance AS attendance
    ORDER BY m.date DESC, m.round
    """

    try:
        comp_result = await db.execute_query(comp_query, params)
        if not comp_result:
            logger.warning(f"Competition not found: {competition_id} season {season}")
            return {"error": f"Competition {competition_id} season {season} not found"}

        matches_result = await db.execute_query(matches_query, params)

        competition_matches = {
            "competition": comp_result[0],
            "matches": matches_result,
            "total_matches": len(matches_result)
        }

        logger.info(f"Retrieved matches for {competition_id} {season}: {len(matches_result)} matches")
        return competition_matches

    except Exception as e:
        logger.error(f"Error getting competition matches: {e}")
        raise
