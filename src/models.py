"""
Brazilian Soccer MCP Server - Data Models

CONTEXT:
This module defines all Pydantic models for the Brazilian Soccer Knowledge Graph.
These models provide type safety, validation, and serialization for:
- Players (personal info, career stats)
- Teams (club information)
- Matches (game results, events)
- Competitions (leagues, tournaments)
- Stadiums (venue information)
- Coaches (manager information)
- Relationships (transfers, goals, cards)

SCHEMA DESIGN:
Based on Neo4j graph database with nodes and relationships:
- Nodes: Player, Team, Match, Competition, Stadium, Coach
- Relationships: PLAYS_FOR, SCORED_IN, ASSISTED_IN, COMPETED_IN, etc.

DEPENDENCIES:
- pydantic: Data validation and serialization
- datetime: Date/time handling
- typing: Type hints

USAGE:
    from src.models import Player, Team, Match

    player = Player(
        player_id="P12345",
        name="Neymar da Silva Santos Júnior",
        birth_date="1992-02-05",
        position="Forward"
    )
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class Position(str, Enum):
    """Player positions in Brazilian soccer."""
    GOALKEEPER = "Goalkeeper"
    DEFENDER = "Defender"
    MIDFIELDER = "Midfielder"
    FORWARD = "Forward"


class CompetitionType(str, Enum):
    """Types of soccer competitions."""
    LEAGUE = "League"
    CUP = "Cup"
    TOURNAMENT = "Tournament"


class CardType(str, Enum):
    """Types of cards in matches."""
    YELLOW = "Yellow"
    RED = "Red"


class GoalType(str, Enum):
    """Types of goals scored."""
    OPEN_PLAY = "Open Play"
    PENALTY = "Penalty"
    FREE_KICK = "Free Kick"
    HEADER = "Header"
    OWN_GOAL = "Own Goal"


# ============================================================================
# CORE ENTITY MODELS
# ============================================================================

class Player(BaseModel):
    """
    Player entity model representing a soccer player.

    Attributes:
        player_id: Unique identifier for the player
        name: Full name of the player
        birth_date: Date of birth
        nationality: Player's nationality
        position: Primary playing position
        jersey_number: Current jersey number (optional)
        height: Height in cm (optional)
        weight: Weight in kg (optional)
        current_team_id: ID of current team (optional)
    """
    player_id: str = Field(..., description="Unique player identifier")
    name: str = Field(..., description="Full player name")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    nationality: str = Field(default="Brazilian", description="Player nationality")
    position: Optional[Position] = Field(None, description="Primary position")
    jersey_number: Optional[int] = Field(None, ge=1, le=99, description="Jersey number")
    height: Optional[int] = Field(None, description="Height in centimeters")
    weight: Optional[int] = Field(None, description="Weight in kilograms")
    current_team_id: Optional[str] = Field(None, description="Current team ID")


class Team(BaseModel):
    """
    Team entity model representing a soccer club.

    Attributes:
        team_id: Unique identifier for the team
        name: Official team name
        city: City where team is based
        stadium: Home stadium name
        founded_year: Year the club was founded
        colors: Team colors (comma-separated)
        nickname: Team nickname (optional)
    """
    team_id: str = Field(..., description="Unique team identifier")
    name: str = Field(..., description="Official team name")
    city: str = Field(..., description="City location")
    stadium: Optional[str] = Field(None, description="Home stadium name")
    founded_year: Optional[int] = Field(None, description="Year founded")
    colors: Optional[str] = Field(None, description="Team colors")
    nickname: Optional[str] = Field(None, description="Team nickname")


class Match(BaseModel):
    """
    Match entity model representing a soccer game.

    Attributes:
        match_id: Unique identifier for the match
        date: Date when match was played
        home_team_id: ID of home team
        away_team_id: ID of away team
        home_score: Goals scored by home team
        away_score: Goals scored by away team
        competition_id: ID of competition
        stadium_id: ID of stadium (optional)
        attendance: Number of spectators (optional)
        referee: Name of referee (optional)
    """
    match_id: str = Field(..., description="Unique match identifier")
    date: date = Field(..., description="Match date")
    home_team_id: str = Field(..., description="Home team ID")
    away_team_id: str = Field(..., description="Away team ID")
    home_score: int = Field(..., ge=0, description="Home team score")
    away_score: int = Field(..., ge=0, description="Away team score")
    competition_id: str = Field(..., description="Competition ID")
    stadium_id: Optional[str] = Field(None, description="Stadium ID")
    attendance: Optional[int] = Field(None, ge=0, description="Attendance")
    referee: Optional[str] = Field(None, description="Referee name")


class Competition(BaseModel):
    """
    Competition entity model representing a tournament or league.

    Attributes:
        competition_id: Unique identifier for the competition
        name: Official competition name
        season: Season year or year range
        type: Type of competition (league/cup)
        tier: Competition tier/division
        country: Country where competition is held
    """
    competition_id: str = Field(..., description="Unique competition identifier")
    name: str = Field(..., description="Competition name")
    season: str = Field(..., description="Season identifier")
    type: CompetitionType = Field(..., description="Competition type")
    tier: Optional[int] = Field(None, description="Competition tier")
    country: str = Field(default="Brazil", description="Country")


class Stadium(BaseModel):
    """
    Stadium entity model representing a soccer venue.

    Attributes:
        stadium_id: Unique identifier for the stadium
        name: Official stadium name
        city: City where stadium is located
        capacity: Maximum seating capacity
        opened_year: Year stadium opened
        surface: Field surface type (optional)
    """
    stadium_id: str = Field(..., description="Unique stadium identifier")
    name: str = Field(..., description="Stadium name")
    city: str = Field(..., description="City location")
    capacity: Optional[int] = Field(None, ge=0, description="Seating capacity")
    opened_year: Optional[int] = Field(None, description="Year opened")
    surface: Optional[str] = Field(None, description="Field surface type")


class Coach(BaseModel):
    """
    Coach entity model representing a team manager.

    Attributes:
        coach_id: Unique identifier for the coach
        name: Full name of the coach
        nationality: Coach's nationality
        birth_date: Date of birth (optional)
        current_team_id: ID of current team (optional)
    """
    coach_id: str = Field(..., description="Unique coach identifier")
    name: str = Field(..., description="Full coach name")
    nationality: str = Field(default="Brazilian", description="Coach nationality")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    current_team_id: Optional[str] = Field(None, description="Current team ID")


# ============================================================================
# RELATIONSHIP MODELS
# ============================================================================

class PlaysFor(BaseModel):
    """Relationship: Player plays for Team."""
    player_id: str
    team_id: str
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    jersey_number: Optional[int] = None


class ScoredIn(BaseModel):
    """Relationship: Player scored in Match."""
    player_id: str
    match_id: str
    minute: int = Field(..., ge=0, le=120)
    goal_type: Optional[GoalType] = None
    team_id: str


class AssistedIn(BaseModel):
    """Relationship: Player assisted in Match."""
    player_id: str
    match_id: str
    minute: int = Field(..., ge=0, le=120)
    team_id: str


class Transfer(BaseModel):
    """Relationship: Player transferred between teams."""
    player_id: str
    from_team_id: str
    to_team_id: str
    transfer_date: date
    fee: Optional[float] = Field(None, description="Transfer fee in currency")
    loan: bool = Field(default=False, description="Is this a loan transfer")


class CardReceived(BaseModel):
    """Relationship: Player received card in Match."""
    player_id: str
    match_id: str
    card_type: CardType
    minute: int = Field(..., ge=0, le=120)
    reason: Optional[str] = None


class Manages(BaseModel):
    """Relationship: Coach manages Team."""
    coach_id: str
    team_id: str
    from_date: date
    to_date: Optional[date] = None


# ============================================================================
# RESPONSE MODELS (for API results)
# ============================================================================

class PlayerStats(BaseModel):
    """Aggregated statistics for a player."""
    player_id: str
    player_name: str
    total_goals: int = 0
    total_assists: int = 0
    total_matches: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    teams_played_for: List[str] = []


class TeamStats(BaseModel):
    """Aggregated statistics for a team."""
    team_id: str
    team_name: str
    total_wins: int = 0
    total_draws: int = 0
    total_losses: int = 0
    goals_scored: int = 0
    goals_conceded: int = 0
    total_matches: int = 0


class MatchDetails(BaseModel):
    """Detailed information about a match."""
    match: Match
    home_team: Team
    away_team: Team
    scorers: List[ScoredIn] = []
    cards: List[CardReceived] = []
    stadium: Optional[Stadium] = None


class PlayerCareer(BaseModel):
    """Complete career information for a player."""
    player: Player
    teams: List[PlaysFor] = []
    transfers: List[Transfer] = []
    stats: PlayerStats


class SearchResult(BaseModel):
    """Generic search result wrapper."""
    total_results: int
    results: List[dict]
    query: str
