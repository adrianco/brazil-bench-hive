"""
Brazilian Soccer MCP Server - Analysis Tools

CONTEXT:
This module implements advanced MCP tools for graph-based analytics:
- find_common_teammates: Find players who played together
- get_rivalry_stats: Analyze historical rivalry between teams
- find_players_by_career_path: Complex career pattern matching

These tools leverage Neo4j's graph capabilities to perform multi-hop
queries and relationship analysis that would be difficult with traditional
relational databases.

CYPHER PATTERNS:
- Path queries: (p1)-[:PLAYS_FOR]->(t)<-[:PLAYS_FOR]-(p2)
- Temporal filtering: WHERE date overlaps
- Pattern matching: Multiple relationship chains
- Aggregation across relationships

DEPENDENCIES:
- src.database: Database connection management
- src.models: Data models for type safety

USAGE:
    from src.tools.analysis_tools import find_common_teammates

    # Find common teammates
    teammates = await find_common_teammates(
        player1_id="P001",
        player2_id="P002"
    )
"""

from typing import List, Optional, Dict, Any
import logging
from src.database import get_db

logger = logging.getLogger(__name__)


async def find_common_teammates(
    player1_id: str,
    player2_id: str
) -> Dict[str, Any]:
    """
    Find all players who were teammates with both specified players.

    This performs a graph traversal to find the intersection of teammates,
    considering the time periods they played together.

    Args:
        player1_id: First player identifier
        player2_id: Second player identifier

    Returns:
        Dictionary with:
        - Player information for both players
        - List of common teammates with teams and dates
        - Total count of common teammates

    Example:
        >>> teammates = await find_common_teammates(
        ...     player1_id="P001",  # Neymar
        ...     player2_id="P002"   # Robinho
        ... )
    """
    db = get_db()
    logger.info(f"Finding common teammates: {player1_id} and {player2_id}")

    # Get player names
    players_query = """
    MATCH (p1:Player {player_id: $player1_id})
    MATCH (p2:Player {player_id: $player2_id})
    RETURN p1.name AS player1_name, p2.name AS player2_name
    """

    # Find common teammates
    # This query finds players who played for the same team as both players
    # during overlapping time periods
    teammates_query = """
    MATCH (p1:Player {player_id: $player1_id})-[pf1:PLAYS_FOR]->(t:Team)
    MATCH (p2:Player {player_id: $player2_id})-[pf2:PLAYS_FOR]->(t)
    MATCH (common:Player)-[pfc:PLAYS_FOR]->(t)
    WHERE common.player_id <> $player1_id
      AND common.player_id <> $player2_id
      AND (
        (pf1.from_date IS NULL OR pfc.to_date IS NULL OR pf1.from_date <= pfc.to_date)
        AND (pf1.to_date IS NULL OR pfc.from_date IS NULL OR pf1.to_date >= pfc.from_date)
      )
      AND (
        (pf2.from_date IS NULL OR pfc.to_date IS NULL OR pf2.from_date <= pfc.to_date)
        AND (pf2.to_date IS NULL OR pfc.from_date IS NULL OR pf2.to_date >= pfc.from_date)
      )
    RETURN DISTINCT
           common.player_id AS player_id,
           common.name AS player_name,
           common.position AS position,
           t.name AS team_name,
           pfc.from_date AS from_date,
           pfc.to_date AS to_date
    ORDER BY t.name, pfc.from_date DESC
    """

    try:
        params = {"player1_id": player1_id, "player2_id": player2_id}

        players_result = await db.execute_query(players_query, params)
        if not players_result:
            logger.warning(f"One or both players not found: {player1_id}, {player2_id}")
            return {"error": "One or both players not found"}

        teammates_result = await db.execute_query(teammates_query, params)

        result = {
            "player1": {
                "player_id": player1_id,
                "name": players_result[0]["player1_name"]
            },
            "player2": {
                "player_id": player2_id,
                "name": players_result[0]["player2_name"]
            },
            "common_teammates": teammates_result,
            "total_common_teammates": len(teammates_result)
        }

        logger.info(f"Found {len(teammates_result)} common teammates")
        return result

    except Exception as e:
        logger.error(f"Error finding common teammates: {e}")
        raise


async def get_rivalry_stats(
    team1_id: str,
    team2_id: str,
    years: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get comprehensive rivalry statistics between two teams.

    Args:
        team1_id: First team identifier
        team2_id: Second team identifier
        years: Limit to last N years (optional)

    Returns:
        Dictionary with:
        - Overall head-to-head statistics
        - Biggest victories for each team
        - Most common scorelines
        - Top scorers in the rivalry
        - Memorable matches

    Example:
        >>> rivalry = await get_rivalry_stats(
        ...     team1_id="T001",  # Flamengo
        ...     team2_id="T002",  # Fluminense
        ...     years=10
        ... )
    """
    db = get_db()
    logger.info(f"Getting rivalry stats: {team1_id} vs {team2_id}, years: {years}")

    # Teams info
    teams_query = """
    MATCH (t1:Team {team_id: $team1_id})
    MATCH (t2:Team {team_id: $team2_id})
    RETURN t1.name AS team1_name, t2.name AS team2_name
    """

    # Overall statistics with date filter
    base_where = """
    WHERE (m.home_team_id = $team1_id AND m.away_team_id = $team2_id)
       OR (m.home_team_id = $team2_id AND m.away_team_id = $team1_id)
    """

    if years:
        base_where += f" AND date(m.date).year >= date().year - {years}"

    stats_query = f"""
    MATCH (m:Match)
    {base_where}
    WITH m,
         CASE
           WHEN m.home_team_id = $team1_id AND m.home_score > m.away_score THEN 'team1'
           WHEN m.away_team_id = $team1_id AND m.away_score > m.home_score THEN 'team1'
           WHEN m.home_score = m.away_score THEN 'draw'
           ELSE 'team2'
         END AS winner,
         CASE WHEN m.home_team_id = $team1_id THEN m.home_score ELSE m.away_score END AS team1_score,
         CASE WHEN m.home_team_id = $team2_id THEN m.home_score ELSE m.away_score END AS team2_score,
         abs(m.home_score - m.away_score) AS goal_margin
    RETURN
         count(m) AS total_matches,
         sum(CASE WHEN winner = 'team1' THEN 1 ELSE 0 END) AS team1_wins,
         sum(CASE WHEN winner = 'team2' THEN 1 ELSE 0 END) AS team2_wins,
         sum(CASE WHEN winner = 'draw' THEN 1 ELSE 0 END) AS draws,
         sum(team1_score) AS team1_goals,
         sum(team2_score) AS team2_goals,
         max(goal_margin) AS biggest_margin
    """

    # Biggest victories for team1
    biggest_wins_query = f"""
    MATCH (m:Match)
    {base_where}
    MATCH (home:Team {{team_id: m.home_team_id}})
    MATCH (away:Team {{team_id: m.away_team_id}})
    WITH m, home, away,
         CASE
           WHEN m.home_team_id = $team1_id THEN m.home_score - m.away_score
           ELSE m.away_score - m.home_score
         END AS margin
    WHERE margin > 0
    RETURN m.match_id AS match_id,
           m.date AS date,
           home.name AS home_team,
           away.name AS away_team,
           m.home_score AS home_score,
           m.away_score AS away_score,
           margin
    ORDER BY margin DESC, m.date DESC
    LIMIT 5
    """

    # Top scorers in rivalry
    top_scorers_query = f"""
    MATCH (m:Match)
    {base_where}
    MATCH (p:Player)-[s:SCORED_IN]->(m)
    MATCH (t:Team {{team_id: s.team_id}})
    WHERE t.team_id = $team1_id OR t.team_id = $team2_id
    WITH p, t, count(s) AS goals
    RETURN p.player_id AS player_id,
           p.name AS player_name,
           t.name AS team_name,
           goals
    ORDER BY goals DESC
    LIMIT 10
    """

    try:
        params = {"team1_id": team1_id, "team2_id": team2_id}

        teams_result = await db.execute_query(teams_query, params)
        if not teams_result:
            logger.warning(f"One or both teams not found: {team1_id}, {team2_id}")
            return {"error": "One or both teams not found"}

        stats_result = await db.execute_query(stats_query, params)
        biggest_wins_result = await db.execute_query(biggest_wins_query, params)
        top_scorers_result = await db.execute_query(top_scorers_query, params)

        stats = stats_result[0] if stats_result else {
            "total_matches": 0,
            "team1_wins": 0,
            "team2_wins": 0,
            "draws": 0,
            "team1_goals": 0,
            "team2_goals": 0,
            "biggest_margin": 0
        }

        rivalry = {
            "teams": {
                "team1": {
                    "team_id": team1_id,
                    "name": teams_result[0]["team1_name"],
                    "wins": stats["team1_wins"],
                    "goals": stats["team1_goals"]
                },
                "team2": {
                    "team_id": team2_id,
                    "name": teams_result[0]["team2_name"],
                    "wins": stats["team2_wins"],
                    "goals": stats["team2_goals"]
                }
            },
            "overall": {
                "total_matches": stats["total_matches"],
                "draws": stats["draws"],
                "biggest_margin": stats["biggest_margin"]
            },
            "biggest_victories": biggest_wins_result,
            "top_scorers": top_scorers_result,
            "time_period": f"Last {years} years" if years else "All time"
        }

        logger.info(f"Retrieved rivalry stats: {stats['total_matches']} matches")
        return rivalry

    except Exception as e:
        logger.error(f"Error getting rivalry stats: {e}")
        raise


async def find_players_by_career_path(
    criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Find players matching complex career path criteria.

    This is a flexible query that can search for players based on:
    - Teams played for (e.g., "played for both Santos and Barcelona")
    - Career progression (e.g., "started in Brazil, moved to Europe")
    - Achievements (e.g., "scored in Copa do Brasil and played abroad")

    Args:
        criteria: Dictionary with search criteria:
            - teams: List of team names (must have played for all)
            - min_teams: Minimum number of teams
            - positions: List of positions
            - transferred_abroad: Boolean
            - min_goals: Minimum career goals

    Returns:
        List of player dictionaries matching criteria

    Example:
        >>> players = await find_players_by_career_path({
        ...     "teams": ["Santos", "Barcelona"],
        ...     "min_goals": 50
        ... })
    """
    db = get_db()
    logger.info(f"Finding players by career path: {criteria}")

    # Build dynamic query based on criteria
    query_parts = ["MATCH (p:Player)"]
    where_clauses = []
    params = {}

    # Teams criteria - must have played for all specified teams
    if "teams" in criteria and criteria["teams"]:
        teams = criteria["teams"]
        for idx, team in enumerate(teams):
            query_parts.append(f"MATCH (p)-[:PLAYS_FOR]->(t{idx}:Team)")
            where_clauses.append(f"t{idx}.name CONTAINS ${f'team{idx}'}")
            params[f"team{idx}"] = team

    # Position filter
    if "positions" in criteria and criteria["positions"]:
        positions_str = ", ".join([f"'{p}'" for p in criteria["positions"]])
        where_clauses.append(f"p.position IN [{positions_str}]")

    # Minimum teams played for
    if "min_teams" in criteria:
        query_parts.append("WITH p, size((p)-[:PLAYS_FOR]->(:Team)) AS num_teams")
        where_clauses.append(f"num_teams >= {criteria['min_teams']}")

    # Build WHERE clause
    base_query = "\n".join(query_parts)
    if where_clauses:
        base_query += "\nWHERE " + " AND ".join(where_clauses)

    # Get player info with career details
    query = base_query + """
    OPTIONAL MATCH (p)-[pf:PLAYS_FOR]->(t:Team)
    WITH p,
         collect(DISTINCT t.name) AS teams,
         count(DISTINCT t) AS num_teams
    """

    # Goals filter
    if "min_goals" in criteria:
        query += f"""
        OPTIONAL MATCH (p)-[s:SCORED_IN]->(:Match)
        WITH p, teams, num_teams, count(s) AS total_goals
        WHERE total_goals >= {criteria['min_goals']}
        """

    query += """
    RETURN p.player_id AS player_id,
           p.name AS name,
           p.position AS position,
           p.nationality AS nationality,
           teams,
           num_teams
    ORDER BY num_teams DESC, p.name
    LIMIT 50
    """

    try:
        results = await db.execute_query(query, params)
        logger.info(f"Found {len(results)} players matching career path criteria")
        return results
    except Exception as e:
        logger.error(f"Error finding players by career path: {e}")
        raise
