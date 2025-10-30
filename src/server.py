"""
Brazilian Soccer MCP Server - Main Server Implementation

CONTEXT:
This is the main MCP server implementation using FastMCP framework.
It exposes all Brazilian Soccer Knowledge Graph tools as MCP endpoints
that can be queried by Claude and other AI assistants.

The server provides:
- Player queries (search, stats, career, transfers)
- Team queries (search, roster, stats, history)
- Match queries (details, search, head-to-head, scorers)
- Competition queries (standings, top scorers, matches)
- Analysis queries (common teammates, rivalry stats, career paths)

ARCHITECTURE:
- FastMCP server framework for MCP protocol implementation
- Async/await pattern for non-blocking operations
- Neo4j database backend for graph queries
- Structured error handling and logging

DEPENDENCIES:
- mcp: MCP protocol implementation
- fastmcp: FastMCP server framework
- src.tools.*: All tool implementations
- src.database: Database connection management
- src.config: Configuration settings

USAGE:
    # Run server
    python -m src.server

    # Or via MCP
    mcp run src/server.py
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

# FastMCP imports
from mcp.server import Server
from mcp.types import Tool, TextContent

# Database and config
from src.database import get_db, Neo4jConnection
from src.config import settings

# Tool imports
from src.tools import player_tools, team_tools, match_tools, competition_tools, analysis_tools

logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server(settings.server_name)

# Global database connection
db: Optional[Neo4jConnection] = None


# ============================================================================
# LIFECYCLE HOOKS
# ============================================================================

@server.call_tool()
async def startup():
    """Initialize database connection on server startup."""
    global db
    logger.info("Starting Brazilian Soccer MCP Server...")

    try:
        db = get_db()
        await db.connect()
        logger.info("Database connection established")

        # Perform health check
        health = await db.health_check()
        logger.info(f"Database health: {health['status']}")
        logger.info(f"Total nodes in database: {health.get('total_nodes', 0)}")

    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def shutdown():
    """Cleanup database connection on server shutdown."""
    global db
    logger.info("Shutting down Brazilian Soccer MCP Server...")

    if db:
        await db.close()
        logger.info("Database connection closed")


# ============================================================================
# PLAYER TOOLS
# ============================================================================

@server.call_tool()
async def search_player(
    name: str,
    team: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = 10
) -> List[TextContent]:
    """
    Search for players by name, optionally filtering by team and position.

    Args:
        name: Player name (partial match supported)
        team: Team name to filter by (optional)
        position: Position to filter by (optional)
        limit: Maximum number of results (default: 10)

    Returns:
        List of players matching search criteria
    """
    try:
        results = await player_tools.search_player(name, team, position, limit)

        if not results:
            return [TextContent(
                type="text",
                text=f"No players found matching: {name}"
            )]

        # Format results
        response = f"Found {len(results)} player(s):\n\n"
        for player in results:
            response += f"• {player['name']} ({player.get('position', 'N/A')})\n"
            response += f"  ID: {player['player_id']}\n"
            if player.get('nationality'):
                response += f"  Nationality: {player['nationality']}\n"
            if player.get('jersey_number'):
                response += f"  Number: {player['jersey_number']}\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in search_player: {e}")
        return [TextContent(type="text", text=f"Error searching for players: {str(e)}")]


@server.call_tool()
async def get_player_stats(
    player_id: str,
    season: Optional[str] = None
) -> List[TextContent]:
    """
    Get comprehensive statistics for a player.

    Args:
        player_id: Unique player identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Player statistics including goals, assists, matches, and cards
    """
    try:
        stats = await player_tools.get_player_stats(player_id, season)

        if "error" in stats:
            return [TextContent(type="text", text=stats["error"])]

        # Format statistics
        season_text = f" ({stats['season']})" if stats.get('season') else " (All-Time)"
        response = f"Statistics for {stats['player_name']}{season_text}:\n\n"
        response += f"⚽ Goals: {stats['total_goals']}\n"
        response += f"🎯 Assists: {stats['total_assists']}\n"
        response += f"🏟️  Matches: {stats['total_matches']}\n"
        response += f"🟨 Yellow Cards: {stats['yellow_cards']}\n"
        response += f"🟥 Red Cards: {stats['red_cards']}\n"

        if stats.get('teams'):
            response += f"\nTeams: {', '.join(stats['teams'])}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_player_stats: {e}")
        return [TextContent(type="text", text=f"Error getting player stats: {str(e)}")]


@server.call_tool()
async def get_player_career(player_id: str) -> List[TextContent]:
    """
    Get complete career history for a player.

    Args:
        player_id: Unique player identifier

    Returns:
        Complete career information including teams, transfers, and statistics
    """
    try:
        career = await player_tools.get_player_career(player_id)

        if "error" in career:
            return [TextContent(type="text", text=career["error"])]

        # Format career information
        player = career["player"]
        response = f"Career of {player.get('name', 'Unknown')}:\n\n"

        # Teams
        if career["teams"]:
            response += "Teams:\n"
            for team in career["teams"]:
                response += f"• {team['team_name']}"
                if team.get('from_date') or team.get('to_date'):
                    dates = f" ({team.get('from_date', '?')} - {team.get('to_date', 'Present')})"
                    response += dates
                if team.get('jersey_number'):
                    response += f" #{team['jersey_number']}"
                response += "\n"
            response += "\n"

        # Transfers
        if career["transfers"]:
            response += f"Transfers ({len(career['transfers'])}):\n"
            for transfer in career["transfers"][:5]:  # Show first 5
                response += f"• {transfer['from_team']} → {transfer['to_team']} ({transfer['transfer_date']})\n"
            response += "\n"

        # Career stats
        if career.get("career_stats"):
            stats = career["career_stats"]
            response += "Career Statistics:\n"
            response += f"⚽ Goals: {stats.get('total_goals', 0)}\n"
            response += f"🎯 Assists: {stats.get('total_assists', 0)}\n"
            response += f"🏟️  Matches: {stats.get('total_matches', 0)}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_player_career: {e}")
        return [TextContent(type="text", text=f"Error getting player career: {str(e)}")]


@server.call_tool()
async def get_player_transfers(
    player_id: str,
    year: Optional[int] = None
) -> List[TextContent]:
    """
    Get all transfers for a player.

    Args:
        player_id: Unique player identifier
        year: Filter by specific year (optional)

    Returns:
        List of transfers with dates, fees, and teams
    """
    try:
        transfers = await player_tools.get_player_transfers(player_id, year)

        if not transfers:
            year_text = f" in {year}" if year else ""
            return [TextContent(type="text", text=f"No transfers found{year_text}")]

        # Format transfers
        year_text = f" in {year}" if year else ""
        response = f"Transfers{year_text}:\n\n"

        for transfer in transfers:
            response += f"• {transfer['from_team']} → {transfer['to_team']}\n"
            response += f"  Date: {transfer['transfer_date']}\n"
            if transfer.get('fee'):
                response += f"  Fee: {transfer['fee']}\n"
            if transfer.get('loan'):
                response += f"  Type: Loan\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_player_transfers: {e}")
        return [TextContent(type="text", text=f"Error getting player transfers: {str(e)}")]


# ============================================================================
# TEAM TOOLS
# ============================================================================

@server.call_tool()
async def search_team(
    name: str,
    city: Optional[str] = None,
    limit: int = 10
) -> List[TextContent]:
    """
    Search for teams by name, optionally filtering by city.

    Args:
        name: Team name (partial match supported)
        city: City to filter by (optional)
        limit: Maximum number of results (default: 10)

    Returns:
        List of teams matching search criteria
    """
    try:
        results = await team_tools.search_team(name, city, limit)

        if not results:
            return [TextContent(type="text", text=f"No teams found matching: {name}")]

        # Format results
        response = f"Found {len(results)} team(s):\n\n"
        for team in results:
            response += f"• {team['name']}\n"
            response += f"  ID: {team['team_id']}\n"
            if team.get('city'):
                response += f"  City: {team['city']}\n"
            if team.get('stadium'):
                response += f"  Stadium: {team['stadium']}\n"
            if team.get('founded_year'):
                response += f"  Founded: {team['founded_year']}\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in search_team: {e}")
        return [TextContent(type="text", text=f"Error searching for teams: {str(e)}")]


@server.call_tool()
async def get_team_roster(
    team_id: str,
    season: Optional[str] = None
) -> List[TextContent]:
    """
    Get team roster (list of players).

    Args:
        team_id: Unique team identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Team roster with player details
    """
    try:
        roster = await team_tools.get_team_roster(team_id, season)

        if "error" in roster:
            return [TextContent(type="text", text=roster["error"])]

        # Format roster
        team_name = roster["team"]["name"]
        season_text = f" ({roster['season']})" if roster.get('season') else ""
        response = f"{team_name} Roster{season_text}:\n\n"
        response += f"Total Players: {roster['total_players']}\n\n"

        # Group by position
        positions = {}
        for player in roster["players"]:
            pos = player.get('position', 'Unknown')
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(player)

        for position, players in sorted(positions.items()):
            response += f"{position}:\n"
            for player in players:
                response += f"  • #{player.get('jersey_number', '?')} {player['name']}\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_team_roster: {e}")
        return [TextContent(type="text", text=f"Error getting team roster: {str(e)}")]


@server.call_tool()
async def get_team_stats(
    team_id: str,
    season: Optional[str] = None
) -> List[TextContent]:
    """
    Get comprehensive statistics for a team.

    Args:
        team_id: Unique team identifier
        season: Specific season to filter (optional, format: "2023")

    Returns:
        Team statistics including wins, draws, losses, and goals
    """
    try:
        stats = await team_tools.get_team_stats(team_id, season)

        if "error" in stats:
            return [TextContent(type="text", text=stats["error"])]

        # Format statistics
        season_text = f" ({stats['season']})" if stats.get('season') else " (All-Time)"
        response = f"Statistics for {stats['team_name']}{season_text}:\n\n"
        response += f"Matches: {stats['total_matches']}\n"
        response += f"Record: {stats['wins']}W - {stats['draws']}D - {stats['losses']}L\n"
        response += f"Win Rate: {stats['win_rate']}%\n"
        response += f"Points: {stats['points']}\n\n"
        response += f"Goals Scored: {stats['goals_scored']}\n"
        response += f"Goals Conceded: {stats['goals_conceded']}\n"
        response += f"Goal Difference: {stats['goal_difference']:+d}\n\n"
        response += f"Home Record: {stats['home_record']['wins']}W / {stats['home_record']['matches']}M\n"
        response += f"Away Record: {stats['away_record']['wins']}W / {stats['away_record']['matches']}M\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_team_stats: {e}")
        return [TextContent(type="text", text=f"Error getting team stats: {str(e)}")]


@server.call_tool()
async def get_team_history(
    team_id: str,
    include_championships: bool = True
) -> List[TextContent]:
    """
    Get complete team history.

    Args:
        team_id: Unique team identifier
        include_championships: Include championship wins (default: True)

    Returns:
        Complete team history including competitions and achievements
    """
    try:
        history = await team_tools.get_team_history(team_id, include_championships)

        if "error" in history:
            return [TextContent(type="text", text=history["error"])]

        # Format history
        team = history["team"]
        response = f"History of {team['name']}:\n\n"

        if team.get('founded_year'):
            response += f"Founded: {team['founded_year']}\n"
        if team.get('city'):
            response += f"City: {team['city']}\n"
        if team.get('stadium_name'):
            response += f"Stadium: {team['stadium_name']}"
            if team.get('stadium_capacity'):
                response += f" (Capacity: {team['stadium_capacity']:,})"
            response += "\n"
        response += "\n"

        # Championships
        if include_championships and history.get("championships"):
            response += f"Championships ({history['total_championships']}):\n"
            for champ in history["championships"][:10]:  # Show first 10
                response += f"• {champ['competition_name']} {champ['season']}\n"
            response += "\n"

        # Competitions participated
        response += f"Competitions Participated ({history['total_competitions']} total):\n"
        recent_comps = list({c['competition_name']: c for c in history['competitions_participated']}.values())[:5]
        for comp in recent_comps:
            response += f"• {comp['competition_name']}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_team_history: {e}")
        return [TextContent(type="text", text=f"Error getting team history: {str(e)}")]


# ============================================================================
# MATCH TOOLS
# ============================================================================

@server.call_tool()
async def get_match_details(match_id: str) -> List[TextContent]:
    """
    Get detailed information about a specific match.

    Args:
        match_id: Unique match identifier

    Returns:
        Detailed match information including scorers and cards
    """
    try:
        details = await match_tools.get_match_details(match_id)

        if "error" in details:
            return [TextContent(type="text", text=details["error"])]

        # Format match details
        match = details["match"]
        response = f"{match['home_team_name']} {match['home_score']} - {match['away_score']} {match['away_team_name']}\n"
        response += f"Date: {match['date']}\n"
        response += f"Competition: {match['competition_name']} ({match['season']})\n"
        if match.get('stadium_name'):
            response += f"Stadium: {match['stadium_name']}, {match.get('stadium_city', '')}\n"
        if match.get('attendance'):
            response += f"Attendance: {match['attendance']:,}\n"
        response += "\n"

        # Scorers
        if details["scorers"]:
            response += "Goal Scorers:\n"
            for scorer in details["scorers"]:
                response += f"• {scorer['minute']}' {scorer['player_name']} ({scorer['team_name']})\n"
            response += "\n"

        # Cards
        if details["cards"]:
            response += "Cards:\n"
            for card in details["cards"]:
                card_emoji = "🟨" if card['card_type'] == 'Yellow' else "🟥"
                response += f"• {card_emoji} {card['minute']}' {card['player_name']} ({card['team_name']})\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_match_details: {e}")
        return [TextContent(type="text", text=f"Error getting match details: {str(e)}")]


@server.call_tool()
async def search_matches(
    team: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    competition: Optional[str] = None,
    limit: int = 20
) -> List[TextContent]:
    """
    Search for matches with various filters.

    Args:
        team: Team name (home or away)
        date_from: Start date (format: "YYYY-MM-DD")
        date_to: End date (format: "YYYY-MM-DD")
        competition: Competition name
        limit: Maximum number of results (default: 20)

    Returns:
        List of matches matching search criteria
    """
    try:
        results = await match_tools.search_matches(team, date_from, date_to, competition, limit)

        if not results:
            return [TextContent(type="text", text="No matches found matching criteria")]

        # Format results
        response = f"Found {len(results)} match(es):\n\n"
        for match in results:
            response += f"{match['date']}: {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}\n"
            if match.get('competition_name'):
                response += f"  Competition: {match['competition_name']}\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in search_matches: {e}")
        return [TextContent(type="text", text=f"Error searching matches: {str(e)}")]


@server.call_tool()
async def get_head_to_head(
    team1_id: str,
    team2_id: str,
    limit: Optional[int] = None
) -> List[TextContent]:
    """
    Get head-to-head statistics between two teams.

    Args:
        team1_id: First team identifier
        team2_id: Second team identifier
        limit: Limit number of recent matches (optional)

    Returns:
        Head-to-head statistics and recent matches
    """
    try:
        h2h = await match_tools.get_head_to_head(team1_id, team2_id, limit)

        if "error" in h2h:
            return [TextContent(type="text", text=h2h["error"])]

        # Format head-to-head
        response = f"Head-to-Head: {h2h['team1']['name']} vs {h2h['team2']['name']}\n\n"
        response += f"Total Matches: {h2h['total_matches']}\n"
        response += f"{h2h['team1']['name']} Wins: {h2h['team1']['wins']}\n"
        response += f"{h2h['team2']['name']} Wins: {h2h['team2']['wins']}\n"
        response += f"Draws: {h2h['draws']}\n"
        response += f"Goals: {h2h['team1']['goals']} - {h2h['team2']['goals']}\n\n"

        # Recent matches
        if h2h["recent_matches"]:
            response += "Recent Matches:\n"
            for match in h2h["recent_matches"][:5]:
                response += f"• {match['date']}: {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_head_to_head: {e}")
        return [TextContent(type="text", text=f"Error getting head-to-head: {str(e)}")]


@server.call_tool()
async def get_match_scorers(match_id: str) -> List[TextContent]:
    """
    Get all goal scorers in a specific match.

    Args:
        match_id: Unique match identifier

    Returns:
        List of goal scorers with details
    """
    try:
        scorers = await match_tools.get_match_scorers(match_id)

        if not scorers:
            return [TextContent(type="text", text="No goals scored in this match")]

        # Format scorers
        response = f"Goal Scorers ({len(scorers)} goals):\n\n"
        for scorer in scorers:
            response += f"• {scorer['minute']}' {scorer['player_name']} ({scorer['team_name']})\n"
            if scorer.get('goal_type'):
                response += f"  Type: {scorer['goal_type']}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_match_scorers: {e}")
        return [TextContent(type="text", text=f"Error getting match scorers: {str(e)}")]


# ============================================================================
# COMPETITION TOOLS
# ============================================================================

@server.call_tool()
async def get_competition_standings(
    competition_id: str,
    season: str
) -> List[TextContent]:
    """
    Get league standings/table for a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")

    Returns:
        Competition standings with points and statistics
    """
    try:
        standings = await competition_tools.get_competition_standings(competition_id, season)

        if "error" in standings:
            return [TextContent(type="text", text=standings["error"])]

        # Format standings
        comp = standings["competition"]
        response = f"{comp['name']} {comp['season']} - Standings\n\n"
        response += f"{'Pos':<4} {'Team':<25} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts':<4}\n"
        response += "-" * 80 + "\n"

        for team in standings["standings"]:
            response += f"{team['position']:<4} "
            response += f"{team['team_name'][:24]:<25} "
            response += f"{team['played']:<4} "
            response += f"{team['wins']:<4} "
            response += f"{team['draws']:<4} "
            response += f"{team['losses']:<4} "
            response += f"{team['goals_for']:<4} "
            response += f"{team['goals_against']:<4} "
            response += f"{team['goal_difference']:>4} "
            response += f"{team['points']:<4}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_competition_standings: {e}")
        return [TextContent(type="text", text=f"Error getting standings: {str(e)}")]


@server.call_tool()
async def get_competition_top_scorers(
    competition_id: str,
    season: str,
    limit: int = 20
) -> List[TextContent]:
    """
    Get top goal scorers in a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")
        limit: Maximum number of scorers to return (default: 20)

    Returns:
        List of top scorers with goal counts
    """
    try:
        top_scorers = await competition_tools.get_competition_top_scorers(competition_id, season, limit)

        if "error" in top_scorers:
            return [TextContent(type="text", text=top_scorers["error"])]

        # Format top scorers
        comp = top_scorers["competition"]
        response = f"{comp['name']} {comp['season']} - Top Scorers\n\n"

        for scorer in top_scorers["top_scorers"]:
            response += f"{scorer['rank']}. {scorer['player_name']} ({scorer['team_name']}) - {scorer['goals']} goals\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_competition_top_scorers: {e}")
        return [TextContent(type="text", text=f"Error getting top scorers: {str(e)}")]


@server.call_tool()
async def get_competition_matches(
    competition_id: str,
    season: str,
    team: Optional[str] = None,
    round: Optional[int] = None
) -> List[TextContent]:
    """
    Get all matches in a competition.

    Args:
        competition_id: Unique competition identifier
        season: Season year (format: "2023")
        team: Filter by specific team (optional)
        round: Filter by specific round/matchday (optional)

    Returns:
        List of matches in the competition
    """
    try:
        matches = await competition_tools.get_competition_matches(competition_id, season, team, round)

        if "error" in matches:
            return [TextContent(type="text", text=matches["error"])]

        # Format matches
        comp = matches["competition"]
        response = f"{comp['name']} {comp['season']} - Matches ({matches['total_matches']} total)\n\n"

        for match in matches["matches"][:20]:  # Show first 20
            response += f"{match['date']}: {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}\n"

        if matches['total_matches'] > 20:
            response += f"\n... and {matches['total_matches'] - 20} more matches"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_competition_matches: {e}")
        return [TextContent(type="text", text=f"Error getting competition matches: {str(e)}")]


# ============================================================================
# ANALYSIS TOOLS
# ============================================================================

@server.call_tool()
async def find_common_teammates(
    player1_id: str,
    player2_id: str
) -> List[TextContent]:
    """
    Find all players who were teammates with both specified players.

    Args:
        player1_id: First player identifier
        player2_id: Second player identifier

    Returns:
        List of common teammates
    """
    try:
        result = await analysis_tools.find_common_teammates(player1_id, player2_id)

        if "error" in result:
            return [TextContent(type="text", text=result["error"])]

        # Format results
        response = f"Common teammates of {result['player1']['name']} and {result['player2']['name']}:\n\n"
        response += f"Found {result['total_common_teammates']} common teammate(s)\n\n"

        # Group by team
        teams = {}
        for teammate in result["common_teammates"]:
            team = teammate["team_name"]
            if team not in teams:
                teams[team] = []
            teams[team].append(teammate)

        for team, teammates in teams.items():
            response += f"{team}:\n"
            for teammate in teammates:
                response += f"  • {teammate['player_name']} ({teammate.get('position', 'N/A')})\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in find_common_teammates: {e}")
        return [TextContent(type="text", text=f"Error finding common teammates: {str(e)}")]


@server.call_tool()
async def get_rivalry_stats(
    team1_id: str,
    team2_id: str,
    years: Optional[int] = None
) -> List[TextContent]:
    """
    Get comprehensive rivalry statistics between two teams.

    Args:
        team1_id: First team identifier
        team2_id: Second team identifier
        years: Limit to last N years (optional)

    Returns:
        Comprehensive rivalry statistics
    """
    try:
        rivalry = await analysis_tools.get_rivalry_stats(team1_id, team2_id, years)

        if "error" in rivalry:
            return [TextContent(type="text", text=rivalry["error"])]

        # Format rivalry stats
        team1 = rivalry["teams"]["team1"]
        team2 = rivalry["teams"]["team2"]
        overall = rivalry["overall"]

        response = f"Rivalry: {team1['name']} vs {team2['name']}\n"
        response += f"Time Period: {rivalry['time_period']}\n\n"

        response += f"Overall Record:\n"
        response += f"Total Matches: {overall['total_matches']}\n"
        response += f"{team1['name']} Wins: {team1['wins']}\n"
        response += f"{team2['name']} Wins: {team2['wins']}\n"
        response += f"Draws: {overall['draws']}\n"
        response += f"Goals: {team1['goals']} - {team2['goals']}\n"
        response += f"Biggest Margin: {overall['biggest_margin']} goals\n\n"

        # Biggest victories
        if rivalry["biggest_victories"]:
            response += "Biggest Victories:\n"
            for match in rivalry["biggest_victories"][:3]:
                response += f"• {match['date']}: {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}\n"
            response += "\n"

        # Top scorers
        if rivalry["top_scorers"]:
            response += "Top Scorers in Rivalry:\n"
            for scorer in rivalry["top_scorers"][:5]:
                response += f"• {scorer['player_name']} ({scorer['team_name']}) - {scorer['goals']} goals\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in get_rivalry_stats: {e}")
        return [TextContent(type="text", text=f"Error getting rivalry stats: {str(e)}")]


@server.call_tool()
async def find_players_by_career_path(criteria: Dict[str, Any]) -> List[TextContent]:
    """
    Find players matching complex career path criteria.

    Args:
        criteria: Dictionary with search criteria (teams, min_teams, positions, min_goals, etc.)

    Returns:
        List of players matching the career path criteria
    """
    try:
        results = await analysis_tools.find_players_by_career_path(criteria)

        if not results:
            return [TextContent(type="text", text="No players found matching criteria")]

        # Format results
        response = f"Found {len(results)} player(s) matching career criteria:\n\n"

        for player in results:
            response += f"• {player['name']} ({player.get('position', 'N/A')})\n"
            response += f"  Teams ({player['num_teams']}): {', '.join(player['teams'][:5])}\n"
            if len(player['teams']) > 5:
                response += f"  ... and {len(player['teams']) - 5} more\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        logger.error(f"Error in find_players_by_career_path: {e}")
        return [TextContent(type="text", text=f"Error finding players: {str(e)}")]


# ============================================================================
# SERVER MAIN
# ============================================================================

async def main():
    """Main entry point for the MCP server."""
    try:
        await startup()

        # Run the server
        async with server:
            await server.run()

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
