"""
Brazilian Soccer MCP Server - Team Tools

CONTEXT:
This module implements MCP tools for team-related queries:
- search_team: Find teams by name or city
- get_team_roster: Get current or historical roster
- get_team_stats: Retrieve team statistics for a season
- get_team_history: Get complete team history including championships

CYPHER PATTERNS:
- MATCH (t:Team) for team nodes
- MATCH (p:Player)-[:PLAYS_FOR]->(t) for roster
- MATCH (t)-[:COMPETED_IN]->(m:Match) for matches
- MATCH (m)-[:PART_OF]->(c:Competition) for competitions

DEPENDENCIES:
- src.database: Database connection management
- src.models: Data models for type safety

USAGE:
    from src.tools.team_tools import search_team, get_team_roster

    # Search for teams
    teams = await search_team(name="Flamengo")

    # Get team roster
    roster = await get_team_roster(team_id="T001", season="2023")
"""

from typing import List, Optional, Dict, Any
import logging
from src.database import get_db
from src.config import settings

logger = logging.getLogger(__name__)


async def search_team(
    name: str,
    city: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for teams by name, optionally filtering by city.

    Args:
        name: Team name (partial match supported)
        city: City to filter by (optional)
        limit: Maximum number of results (default: 10)

    Returns:
        List of team dictionaries with basic information

    Example:
        >>> teams = await search_team(name="Flamengo")
        >>> teams = await search_team(name="FC", city="São Paulo")
    """
    db = get_db()
    logger.info(f"Searching for team: name={name}, city={city}")

    query = """
    MATCH (t:Team)
    WHERE t.name CONTAINS $name
    """

    params = {"name": name, "limit": limit}

    if city:
        query += " AND t.city CONTAINS $city"
        params["city"] = city

    query += """
    RETURN t.team_id AS team_id,
           t.name AS name,
           t.city AS city,
           t.stadium AS stadium,
           t.founded_year AS founded_year,
           t.colors AS colors,
           t.nickname AS nickname
    LIMIT $limit
    """

    try:
        results = await db.execute_query(query, params)
        logger.info(f"Found {len(results)} teams matching search criteria")
        return results
    except Exception as e:
        logger.error(f"Error searching for teams: {e}")
        raise


async def get_team_roster(
    team_id: str,
    season: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get team roster (list of players).

    Args:
        team_id: Unique team identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Dictionary with team info and list of players

    Example:
        >>> roster = await get_team_roster(team_id="T001")
        >>> roster = await get_team_roster(team_id="T001", season="2023")
    """
    db = get_db()
    logger.info(f"Getting roster for team: {team_id}, season: {season}")

    # Get team info
    team_query = """
    MATCH (t:Team {team_id: $team_id})
    RETURN t.team_id AS team_id,
           t.name AS name,
           t.city AS city,
           t.stadium AS stadium
    """

    # Get players
    players_query = """
    MATCH (p:Player)-[pf:PLAYS_FOR]->(t:Team {team_id: $team_id})
    """

    params = {"team_id": team_id}

    if season:
        # Filter by season dates
        players_query += """
        WHERE (pf.from_date IS NULL OR date(pf.from_date).year <= $year)
          AND (pf.to_date IS NULL OR date(pf.to_date).year >= $year)
        """
        params["year"] = int(season)

    players_query += """
    RETURN p.player_id AS player_id,
           p.name AS name,
           p.position AS position,
           pf.jersey_number AS jersey_number,
           pf.from_date AS from_date,
           pf.to_date AS to_date
    ORDER BY p.position, pf.jersey_number
    """

    try:
        team_result = await db.execute_query(team_query, params)
        if not team_result:
            logger.warning(f"Team not found: {team_id}")
            return {"error": f"Team {team_id} not found"}

        players_result = await db.execute_query(players_query, params)

        roster = {
            "team": team_result[0],
            "season": season,
            "players": players_result,
            "total_players": len(players_result)
        }

        logger.info(f"Retrieved roster for team {team_id}: {len(players_result)} players")
        return roster

    except Exception as e:
        logger.error(f"Error getting team roster: {e}")
        raise


async def get_team_stats(
    team_id: str,
    season: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a team.

    Args:
        team_id: Unique team identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Dictionary with team statistics including:
        - Wins, draws, losses
        - Goals scored and conceded
        - Home and away performance

    Example:
        >>> stats = await get_team_stats(team_id="T001")
        >>> stats = await get_team_stats(team_id="T001", season="2023")
    """
    db = get_db()
    logger.info(f"Getting stats for team: {team_id}, season: {season}")

    # Team info
    team_query = """
    MATCH (t:Team {team_id: $team_id})
    RETURN t.team_id AS team_id, t.name AS name
    """

    # Matches statistics query
    stats_query = """
    MATCH (t:Team {team_id: $team_id})
    MATCH (m:Match)
    WHERE m.home_team_id = $team_id OR m.away_team_id = $team_id
    """

    params = {"team_id": team_id}

    if season:
        stats_query += """
        MATCH (m)-[:PART_OF]->(c:Competition {season: $season})
        """
        params["season"] = season

    stats_query += """
    WITH t, m,
         CASE WHEN m.home_team_id = $team_id THEN m.home_score ELSE m.away_score END AS goals_for,
         CASE WHEN m.home_team_id = $team_id THEN m.away_score ELSE m.home_score END AS goals_against,
         CASE WHEN m.home_team_id = $team_id THEN 'home' ELSE 'away' END AS venue,
         CASE
           WHEN m.home_team_id = $team_id AND m.home_score > m.away_score THEN 'win'
           WHEN m.away_team_id = $team_id AND m.away_score > m.home_score THEN 'win'
           WHEN m.home_score = m.away_score THEN 'draw'
           ELSE 'loss'
         END AS result
    RETURN
         count(m) AS total_matches,
         sum(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS wins,
         sum(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws,
         sum(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
         sum(goals_for) AS goals_scored,
         sum(goals_against) AS goals_conceded,
         sum(CASE WHEN venue = 'home' THEN 1 ELSE 0 END) AS home_matches,
         sum(CASE WHEN venue = 'home' AND result = 'win' THEN 1 ELSE 0 END) AS home_wins,
         sum(CASE WHEN venue = 'away' THEN 1 ELSE 0 END) AS away_matches,
         sum(CASE WHEN venue = 'away' AND result = 'win' THEN 1 ELSE 0 END) AS away_wins
    """

    try:
        team_result = await db.execute_query(team_query, params)
        if not team_result:
            logger.warning(f"Team not found: {team_id}")
            return {"error": f"Team {team_id} not found"}

        stats_result = await db.execute_query(stats_query, params)

        if not stats_result or stats_result[0]["total_matches"] == 0:
            stats_data = {
                "total_matches": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_scored": 0,
                "goals_conceded": 0,
                "home_matches": 0,
                "home_wins": 0,
                "away_matches": 0,
                "away_wins": 0
            }
        else:
            stats_data = stats_result[0]

        # Calculate additional metrics
        total_matches = stats_data["total_matches"]
        wins = stats_data["wins"]
        draws = stats_data["draws"]
        goals_scored = stats_data["goals_scored"]
        goals_conceded = stats_data["goals_conceded"]

        stats = {
            "team_id": team_result[0]["team_id"],
            "team_name": team_result[0]["name"],
            "season": season,
            "total_matches": total_matches,
            "wins": wins,
            "draws": draws,
            "losses": stats_data["losses"],
            "goals_scored": goals_scored,
            "goals_conceded": goals_conceded,
            "goal_difference": goals_scored - goals_conceded,
            "win_rate": round((wins / total_matches * 100), 2) if total_matches > 0 else 0,
            "points": wins * 3 + draws,  # Standard 3 points for win, 1 for draw
            "home_record": {
                "matches": stats_data["home_matches"],
                "wins": stats_data["home_wins"]
            },
            "away_record": {
                "matches": stats_data["away_matches"],
                "wins": stats_data["away_wins"]
            }
        }

        logger.info(f"Retrieved stats for team {team_id}: {wins}W {draws}D {stats_data['losses']}L")
        return stats

    except Exception as e:
        logger.error(f"Error getting team stats: {e}")
        raise


async def get_team_history(
    team_id: str,
    include_championships: bool = True
) -> Dict[str, Any]:
    """
    Get complete team history.

    Args:
        team_id: Unique team identifier
        include_championships: Include championship wins (default: True)

    Returns:
        Dictionary with:
        - Team basic information
        - All competitions participated in
        - Championship titles (if requested)
        - Historical statistics

    Example:
        >>> history = await get_team_history(team_id="T001")
    """
    db = get_db()
    logger.info(f"Getting history for team: {team_id}")

    # Team info with stadium
    team_query = """
    MATCH (t:Team {team_id: $team_id})
    OPTIONAL MATCH (t)-[:PLAYS_AT]->(s:Stadium)
    RETURN t.team_id AS team_id,
           t.name AS name,
           t.city AS city,
           t.founded_year AS founded_year,
           t.colors AS colors,
           t.nickname AS nickname,
           s.name AS stadium_name,
           s.capacity AS stadium_capacity
    """

    # Competitions participated
    competitions_query = """
    MATCH (t:Team {team_id: $team_id})-[:COMPETED_IN]->(m:Match)-[:PART_OF]->(c:Competition)
    RETURN DISTINCT c.name AS competition_name,
                    c.season AS season,
                    c.type AS type
    ORDER BY c.season DESC
    """

    # Championships won (if team won the competition)
    championships_query = """
    MATCH (t:Team {team_id: $team_id})-[:WON]->(c:Competition)
    RETURN c.name AS competition_name,
           c.season AS season,
           c.type AS type
    ORDER BY c.season DESC
    """

    try:
        params = {"team_id": team_id}

        team_result = await db.execute_query(team_query, params)
        if not team_result:
            logger.warning(f"Team not found: {team_id}")
            return {"error": f"Team {team_id} not found"}

        competitions_result = await db.execute_query(competitions_query, params)

        history = {
            "team": team_result[0],
            "competitions_participated": competitions_result,
            "total_competitions": len(competitions_result)
        }

        if include_championships:
            championships_result = await db.execute_query(championships_query, params)
            history["championships"] = championships_result
            history["total_championships"] = len(championships_result)

        # Get all-time stats
        all_time_stats = await get_team_stats(team_id)
        history["all_time_stats"] = all_time_stats

        logger.info(f"Retrieved history for team {team_id}: {len(competitions_result)} competitions")
        return history

    except Exception as e:
        logger.error(f"Error getting team history: {e}")
        raise
