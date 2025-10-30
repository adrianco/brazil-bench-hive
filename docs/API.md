# Brazilian Soccer Knowledge Graph - MCP Tools API Reference

## Overview

This document provides comprehensive documentation for all MCP (Model Context Protocol) tools exposed by the Brazilian Soccer Knowledge Graph server. Each tool can be invoked by Claude AI to query and analyze Brazilian soccer data.

## Table of Contents

- [Player Tools](#player-tools)
- [Team Tools](#team-tools)
- [Match Tools](#match-tools)
- [Competition Tools](#competition-tools)
- [Analysis Tools](#analysis-tools)
- [Common Response Formats](#common-response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Player Tools

### search_player

Search for players by name, team, or position.

**Parameters:**
```json
{
  "name": "string (required)",
  "team": "string (optional)",
  "position": "string (optional)"
}
```

**Example Request:**
```json
{
  "name": "Neymar",
  "team": "Santos"
}
```

**Example Response:**
```json
{
  "results": [
    {
      "player_id": "P12345",
      "name": "Neymar da Silva Santos Júnior",
      "birth_date": "1992-02-05",
      "nationality": "Brazilian",
      "position": "Forward",
      "current_team": "Santos FC",
      "current_team_id": "T789"
    }
  ],
  "count": 1
}
```

**Use Cases:**
- "Find all forwards named Silva"
- "Who plays for Flamengo?"
- "Search for midfielders in Palmeiras"

---

### get_player_stats

Get detailed statistics for a specific player.

**Parameters:**
```json
{
  "player_id": "string (required)",
  "season": "string (optional, format: YYYY)"
}
```

**Example Request:**
```json
{
  "player_id": "P12345",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "player_id": "P12345",
  "name": "Neymar da Silva Santos Júnior",
  "season": "2023",
  "statistics": {
    "matches_played": 38,
    "goals": 21,
    "assists": 14,
    "minutes_played": 3240,
    "yellow_cards": 5,
    "red_cards": 0,
    "goals_per_match": 0.55,
    "assists_per_match": 0.37
  },
  "team": {
    "team_id": "T789",
    "name": "Santos FC"
  }
}
```

**Use Cases:**
- "How many goals did Neymar score in 2023?"
- "Show me player X's statistics"
- "What were Pelé's career stats?"

---

### get_player_career

Get complete career history for a player.

**Parameters:**
```json
{
  "player_id": "string (required)"
}
```

**Example Request:**
```json
{
  "player_id": "P12345"
}
```

**Example Response:**
```json
{
  "player_id": "P12345",
  "name": "Neymar da Silva Santos Júnior",
  "career": [
    {
      "team_id": "T789",
      "team_name": "Santos FC",
      "from_date": "2009-03-07",
      "to_date": "2013-06-03",
      "matches": 225,
      "goals": 136,
      "assists": 64,
      "jersey_number": 11
    },
    {
      "team_id": "T456",
      "team_name": "FC Barcelona",
      "from_date": "2013-06-03",
      "to_date": "2017-08-03",
      "matches": 186,
      "goals": 105,
      "assists": 76,
      "jersey_number": 11
    }
  ],
  "total_stats": {
    "teams_played_for": 4,
    "total_matches": 500,
    "total_goals": 350,
    "total_assists": 180
  }
}
```

**Use Cases:**
- "What teams has Ronaldo played for?"
- "Show me Neymar's complete career"
- "Where did Pelé play during his career?"

---

### get_player_transfers

Get transfer history for a player.

**Parameters:**
```json
{
  "player_id": "string (required)"
}
```

**Example Request:**
```json
{
  "player_id": "P12345"
}
```

**Example Response:**
```json
{
  "player_id": "P12345",
  "name": "Neymar da Silva Santos Júnior",
  "transfers": [
    {
      "transfer_date": "2013-06-03",
      "from_team": "Santos FC",
      "from_team_id": "T789",
      "to_team": "FC Barcelona",
      "to_team_id": "T456",
      "fee": 57000000,
      "currency": "EUR",
      "transfer_type": "permanent"
    },
    {
      "transfer_date": "2017-08-03",
      "from_team": "FC Barcelona",
      "from_team_id": "T456",
      "to_team": "Paris Saint-Germain",
      "to_team_id": "T123",
      "fee": 222000000,
      "currency": "EUR",
      "transfer_type": "permanent"
    }
  ],
  "total_transfer_value": 279000000
}
```

**Use Cases:**
- "When did Neymar transfer to Barcelona?"
- "Show me all of player X's transfers"
- "Which Brazilian players moved to Europe in 2023?"

---

## Team Tools

### search_team

Search for teams by name.

**Parameters:**
```json
{
  "name": "string (required)"
}
```

**Example Request:**
```json
{
  "name": "Flamengo"
}
```

**Example Response:**
```json
{
  "results": [
    {
      "team_id": "T001",
      "name": "Clube de Regatas do Flamengo",
      "common_name": "Flamengo",
      "city": "Rio de Janeiro",
      "stadium": "Maracanã",
      "founded_year": 1895,
      "colors": "Red and Black"
    }
  ],
  "count": 1
}
```

**Use Cases:**
- "Find Flamengo"
- "Search for teams in São Paulo"
- "Which teams play in Rio?"

---

### get_team_roster

Get current or historical roster for a team.

**Parameters:**
```json
{
  "team_id": "string (required)",
  "season": "string (optional, format: YYYY)"
}
```

**Example Request:**
```json
{
  "team_id": "T001",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "team_id": "T001",
  "team_name": "Flamengo",
  "season": "2023",
  "roster": [
    {
      "player_id": "P101",
      "name": "Gabriel Barbosa",
      "position": "Forward",
      "jersey_number": 9,
      "joined_date": "2019-01-15"
    },
    {
      "player_id": "P102",
      "name": "Éverton Ribeiro",
      "position": "Midfielder",
      "jersey_number": 7,
      "joined_date": "2017-07-01"
    }
  ],
  "roster_size": 28,
  "coaches": [
    {
      "coach_id": "C001",
      "name": "Jorge Jesus",
      "role": "Head Coach"
    }
  ]
}
```

**Use Cases:**
- "Who plays for Flamengo?"
- "Show me Palmeiras' 2023 roster"
- "List all players on team X"

---

### get_team_stats

Get statistics for a team in a specific season.

**Parameters:**
```json
{
  "team_id": "string (required)",
  "season": "string (optional, format: YYYY)"
}
```

**Example Request:**
```json
{
  "team_id": "T001",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "team_id": "T001",
  "team_name": "Flamengo",
  "season": "2023",
  "statistics": {
    "matches_played": 60,
    "wins": 38,
    "draws": 12,
    "losses": 10,
    "goals_for": 95,
    "goals_against": 45,
    "goal_difference": 50,
    "points": 126,
    "win_percentage": 63.3,
    "clean_sheets": 22,
    "biggest_win": "6-0 vs Corinthians",
    "biggest_loss": "0-3 vs Palmeiras"
  },
  "home_record": {
    "wins": 22,
    "draws": 5,
    "losses": 3
  },
  "away_record": {
    "wins": 16,
    "draws": 7,
    "losses": 7
  }
}
```

**Use Cases:**
- "How did Flamengo perform in 2023?"
- "Show me team statistics"
- "What's Palmeiras' win rate?"

---

### get_team_history

Get historical information about a team.

**Parameters:**
```json
{
  "team_id": "string (required)"
}
```

**Example Request:**
```json
{
  "team_id": "T001"
}
```

**Example Response:**
```json
{
  "team_id": "T001",
  "team_name": "Flamengo",
  "founded_year": 1895,
  "stadium": {
    "name": "Maracanã",
    "capacity": 78838,
    "opened_year": 1950
  },
  "championships": {
    "brasileirao": [1980, 1982, 1983, 1987, 1992, 2009, 2019, 2020],
    "copa_do_brasil": [1990, 2006, 2013, 2022],
    "copa_libertadores": [1981, 2019, 2022],
    "total_titles": 38
  },
  "notable_players": [
    {
      "player_id": "P999",
      "name": "Zico",
      "period": "1971-1989",
      "legacy": "Club legend, 508 goals"
    }
  ],
  "rivalries": [
    {
      "team": "Fluminense",
      "derby_name": "Fla-Flu",
      "first_match": "1912-07-07"
    }
  ]
}
```

**Use Cases:**
- "Tell me about Flamengo's history"
- "How many championships has Palmeiras won?"
- "Who are Corinthians' rivals?"

---

## Match Tools

### get_match_details

Get detailed information about a specific match.

**Parameters:**
```json
{
  "match_id": "string (required)"
}
```

**Example Request:**
```json
{
  "match_id": "M67890"
}
```

**Example Response:**
```json
{
  "match_id": "M67890",
  "date": "2023-11-15",
  "competition": {
    "competition_id": "C001",
    "name": "Campeonato Brasileiro Série A",
    "season": "2023"
  },
  "home_team": {
    "team_id": "T001",
    "name": "Flamengo",
    "score": 2
  },
  "away_team": {
    "team_id": "T002",
    "name": "Palmeiras",
    "score": 1
  },
  "stadium": {
    "stadium_id": "S001",
    "name": "Maracanã",
    "attendance": 65000
  },
  "goals": [
    {
      "minute": 23,
      "player_id": "P101",
      "player_name": "Gabriel Barbosa",
      "team": "Flamengo",
      "type": "open_play",
      "assisted_by": "P102"
    },
    {
      "minute": 67,
      "player_id": "P201",
      "player_name": "Rony",
      "team": "Palmeiras",
      "type": "penalty"
    },
    {
      "minute": 89,
      "player_id": "P103",
      "player_name": "Pedro",
      "team": "Flamengo",
      "type": "header"
    }
  ],
  "cards": {
    "yellow": [
      {"minute": 45, "player": "P104", "team": "Flamengo"},
      {"minute": 78, "player": "P202", "team": "Palmeiras"}
    ],
    "red": []
  }
}
```

**Use Cases:**
- "Show me details of match M67890"
- "What happened in the last Fla-Flu?"
- "Who scored in the Brasileirão final?"

---

### search_matches

Search for matches by team and date range.

**Parameters:**
```json
{
  "team": "string (optional)",
  "date_from": "string (optional, format: YYYY-MM-DD)",
  "date_to": "string (optional, format: YYYY-MM-DD)",
  "competition": "string (optional)"
}
```

**Example Request:**
```json
{
  "team": "Flamengo",
  "date_from": "2023-01-01",
  "date_to": "2023-12-31",
  "competition": "Brasileirão"
}
```

**Example Response:**
```json
{
  "matches": [
    {
      "match_id": "M001",
      "date": "2023-04-16",
      "home_team": "Flamengo",
      "away_team": "Botafogo",
      "score": "2-1",
      "competition": "Brasileirão"
    },
    {
      "match_id": "M002",
      "date": "2023-04-23",
      "home_team": "Vasco",
      "away_team": "Flamengo",
      "score": "0-3",
      "competition": "Brasileirão"
    }
  ],
  "count": 38,
  "showing": 2
}
```

**Use Cases:**
- "Find all Flamengo matches in 2023"
- "Show me matches between two dates"
- "List Copa do Brasil matches"

---

### get_head_to_head

Get head-to-head statistics between two teams.

**Parameters:**
```json
{
  "team1_id": "string (required)",
  "team2_id": "string (required)"
}
```

**Example Request:**
```json
{
  "team1_id": "T001",
  "team2_id": "T002"
}
```

**Example Response:**
```json
{
  "team1": {
    "team_id": "T001",
    "name": "Flamengo"
  },
  "team2": {
    "team_id": "T002",
    "name": "Fluminense"
  },
  "rivalry_name": "Fla-Flu",
  "first_meeting": "1912-07-07",
  "total_matches": 432,
  "statistics": {
    "team1_wins": 158,
    "team2_wins": 141,
    "draws": 133,
    "team1_goals": 612,
    "team2_goals": 558
  },
  "recent_form": [
    {"date": "2023-11-05", "result": "2-1", "winner": "Flamengo"},
    {"date": "2023-07-16", "result": "1-1", "winner": "draw"},
    {"date": "2023-03-12", "result": "0-2", "winner": "Fluminense"}
  ],
  "biggest_wins": [
    {"date": "1995-06-04", "score": "6-0", "winner": "Flamengo"},
    {"date": "1930-10-05", "score": "0-5", "winner": "Fluminense"}
  ]
}
```

**Use Cases:**
- "Flamengo vs Fluminense history"
- "Head to head between team X and team Y"
- "Show me the Fla-Flu rivalry stats"

---

### get_match_scorers

Get all goal scorers in a specific match.

**Parameters:**
```json
{
  "match_id": "string (required)"
}
```

**Example Request:**
```json
{
  "match_id": "M67890"
}
```

**Example Response:**
```json
{
  "match_id": "M67890",
  "match_info": {
    "date": "2023-11-15",
    "home_team": "Flamengo",
    "away_team": "Palmeiras",
    "final_score": "2-1"
  },
  "scorers": [
    {
      "player_id": "P101",
      "name": "Gabriel Barbosa",
      "team": "Flamengo",
      "minute": 23,
      "goal_type": "open_play",
      "assisted_by": {
        "player_id": "P102",
        "name": "Éverton Ribeiro"
      }
    },
    {
      "player_id": "P201",
      "name": "Rony",
      "team": "Palmeiras",
      "minute": 67,
      "goal_type": "penalty"
    },
    {
      "player_id": "P103",
      "name": "Pedro",
      "team": "Flamengo",
      "minute": 89,
      "goal_type": "header"
    }
  ],
  "total_goals": 3
}
```

**Use Cases:**
- "Who scored in match M67890?"
- "Show me the scorers from the last derby"
- "List all goals in the championship final"

---

## Competition Tools

### get_competition_standings

Get current standings for a competition.

**Parameters:**
```json
{
  "competition_id": "string (required)",
  "season": "string (required, format: YYYY)"
}
```

**Example Request:**
```json
{
  "competition_id": "C001",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "competition_id": "C001",
  "competition_name": "Campeonato Brasileiro Série A",
  "season": "2023",
  "standings": [
    {
      "position": 1,
      "team_id": "T001",
      "team_name": "Flamengo",
      "matches_played": 38,
      "wins": 24,
      "draws": 8,
      "losses": 6,
      "goals_for": 72,
      "goals_against": 35,
      "goal_difference": 37,
      "points": 80,
      "form": ["W", "W", "D", "W", "L"]
    },
    {
      "position": 2,
      "team_id": "T002",
      "team_name": "Palmeiras",
      "matches_played": 38,
      "wins": 22,
      "draws": 10,
      "losses": 6,
      "goals_for": 65,
      "goals_against": 30,
      "goal_difference": 35,
      "points": 76,
      "form": ["W", "D", "W", "W", "W"]
    }
  ],
  "total_teams": 20,
  "updated": "2023-12-06"
}
```

**Use Cases:**
- "Show me the Brasileirão standings"
- "What's the current league table?"
- "Who's leading the championship?"

---

### get_competition_top_scorers

Get top scorers for a competition.

**Parameters:**
```json
{
  "competition_id": "string (required)",
  "season": "string (required, format: YYYY)"
}
```

**Example Request:**
```json
{
  "competition_id": "C001",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "competition_id": "C001",
  "competition_name": "Campeonato Brasileiro Série A",
  "season": "2023",
  "top_scorers": [
    {
      "position": 1,
      "player_id": "P101",
      "name": "Gabriel Barbosa",
      "team": "Flamengo",
      "goals": 28,
      "penalties": 5,
      "matches_played": 36
    },
    {
      "position": 2,
      "player_id": "P201",
      "name": "Pedro",
      "team": "Flamengo",
      "goals": 24,
      "penalties": 3,
      "matches_played": 35
    },
    {
      "position": 3,
      "player_id": "P301",
      "name": "Dudu",
      "team": "Palmeiras",
      "goals": 21,
      "penalties": 2,
      "matches_played": 38
    }
  ],
  "total_scorers": 150
}
```

**Use Cases:**
- "Who's the top scorer in Brasileirão 2023?"
- "Show me the golden boot race"
- "List top 10 scorers"

---

### get_competition_matches

Get all matches in a competition for a season.

**Parameters:**
```json
{
  "competition_id": "string (required)",
  "season": "string (required, format: YYYY)"
}
```

**Example Request:**
```json
{
  "competition_id": "C001",
  "season": "2023"
}
```

**Example Response:**
```json
{
  "competition_id": "C001",
  "competition_name": "Campeonato Brasileiro Série A",
  "season": "2023",
  "matches": [
    {
      "match_id": "M001",
      "round": 1,
      "date": "2023-04-16",
      "home_team": "Flamengo",
      "away_team": "Botafogo",
      "score": "2-1",
      "status": "completed"
    },
    {
      "match_id": "M002",
      "round": 1,
      "date": "2023-04-16",
      "home_team": "Palmeiras",
      "away_team": "Corinthians",
      "score": "3-0",
      "status": "completed"
    }
  ],
  "total_matches": 380,
  "completed": 380,
  "scheduled": 0
}
```

**Use Cases:**
- "Show me all Brasileirão 2023 matches"
- "List matches from round 10"
- "When does Flamengo play next?"

---

## Analysis Tools

### find_common_teammates

Find players who were teammates of two given players.

**Parameters:**
```json
{
  "player1_id": "string (required)",
  "player2_id": "string (required)"
}
```

**Example Request:**
```json
{
  "player1_id": "P101",
  "player2_id": "P102"
}
```

**Example Response:**
```json
{
  "player1": {
    "player_id": "P101",
    "name": "Gabriel Barbosa"
  },
  "player2": {
    "player_id": "P102",
    "name": "Pedro"
  },
  "common_teammates": [
    {
      "player_id": "P103",
      "name": "Éverton Ribeiro",
      "team": "Flamengo",
      "period": "2019-2023",
      "overlap_with_both": "2019-2023"
    },
    {
      "player_id": "P104",
      "name": "Filipe Luís",
      "team": "Flamengo",
      "period": "2019-2021",
      "overlap_with_both": "2019-2021"
    }
  ],
  "total_common_teammates": 15
}
```

**Use Cases:**
- "Who played with both Neymar and Pelé?"
- "Find common teammates of player X and player Y"
- "Which players were teammates with both?"

---

### get_rivalry_stats

Analyze rivalry statistics between two teams.

**Parameters:**
```json
{
  "team1_id": "string (required)",
  "team2_id": "string (required)"
}
```

**Example Request:**
```json
{
  "team1_id": "T001",
  "team2_id": "T002"
}
```

**Example Response:**
```json
{
  "rivalry": {
    "team1": "Flamengo",
    "team2": "Fluminense",
    "name": "Fla-Flu",
    "intensity_score": 9.5
  },
  "all_time_stats": {
    "total_matches": 432,
    "team1_wins": 158,
    "team2_wins": 141,
    "draws": 133,
    "team1_goals": 612,
    "team2_goals": 558
  },
  "recent_trends": {
    "last_10_matches": {
      "team1_wins": 6,
      "team2_wins": 2,
      "draws": 2
    },
    "momentum": "Flamengo"
  },
  "notable_matches": [
    {
      "date": "2022-11-13",
      "competition": "Copa do Brasil Final",
      "score": "2-0",
      "winner": "Flamengo",
      "significance": "Championship deciding match"
    }
  ],
  "top_scorers_in_rivalry": [
    {"player": "Zico", "team": "Flamengo", "goals": 45},
    {"player": "Fred", "team": "Fluminense", "goals": 38}
  ]
}
```

**Use Cases:**
- "Analyze the Fla-Flu rivalry"
- "Show me derby statistics"
- "Compare Flamengo vs Palmeiras historically"

---

### find_players_by_career_path

Find players matching specific career criteria.

**Parameters:**
```json
{
  "criteria": {
    "teams": ["string"],
    "min_goals": "number (optional)",
    "positions": ["string (optional)"],
    "championships": ["string (optional)"],
    "international": "boolean (optional)"
  }
}
```

**Example Request:**
```json
{
  "criteria": {
    "teams": ["Santos", "Barcelona"],
    "min_goals": 100,
    "international": true
  }
}
```

**Example Response:**
```json
{
  "matching_players": [
    {
      "player_id": "P12345",
      "name": "Neymar da Silva Santos Júnior",
      "career_summary": {
        "teams_played": ["Santos", "Barcelona", "PSG"],
        "total_goals": 350,
        "championships": 15,
        "international_caps": 120
      },
      "matching_criteria": {
        "played_for_santos": true,
        "played_for_barcelona": true,
        "goals_above_threshold": true,
        "international_player": true
      }
    }
  ],
  "total_matches": 1
}
```

**Use Cases:**
- "Find players who played for both Santos and Barcelona"
- "Which players scored 100+ goals and played in Europe?"
- "Show me championship-winning strikers"

---

## Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { /* tool-specific data */ },
  "metadata": {
    "query_time_ms": 45,
    "result_count": 10,
    "timestamp": "2023-12-06T10:30:00Z"
  }
}
```

### Paginated Response
```json
{
  "status": "success",
  "data": [ /* results */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "total_results": 95,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## Error Handling

### Error Response Format
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "parameter_name",
      "reason": "Specific reason for error"
    },
    "timestamp": "2023-12-06T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_PARAMETER` | Invalid or missing parameter | 400 |
| `PLAYER_NOT_FOUND` | Player ID doesn't exist | 404 |
| `TEAM_NOT_FOUND` | Team ID doesn't exist | 404 |
| `MATCH_NOT_FOUND` | Match ID doesn't exist | 404 |
| `COMPETITION_NOT_FOUND` | Competition ID doesn't exist | 404 |
| `DATABASE_ERROR` | Neo4j connection or query error | 500 |
| `TIMEOUT` | Query exceeded time limit | 504 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |

### Example Error Response
```json
{
  "status": "error",
  "error": {
    "code": "PLAYER_NOT_FOUND",
    "message": "No player found with ID: P99999",
    "details": {
      "searched_id": "P99999",
      "suggestions": [
        "P12345 - Neymar",
        "P12346 - Gabriel Barbosa"
      ]
    },
    "timestamp": "2023-12-06T10:30:00Z"
  }
}
```

---

## Rate Limiting

### Default Limits
- **Per Tool**: 100 requests per minute
- **Per Session**: 1000 requests per hour
- **Burst**: Up to 20 requests in 10 seconds

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1701860400
```

### Rate Limit Exceeded Response
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    }
  }
}
```

---

## Best Practices

### Query Optimization
1. **Use specific parameters**: More specific queries return faster
2. **Limit result sets**: Use pagination for large datasets
3. **Cache frequent queries**: Store commonly accessed data locally
4. **Batch related queries**: Minimize round trips

### Error Handling
1. **Always check status**: Verify `status` field before processing data
2. **Handle suggestions**: Use error suggestions for recovery
3. **Implement retry logic**: With exponential backoff for transient errors
4. **Log errors**: Track errors for debugging

### Security
1. **Validate inputs**: Never trust user input
2. **Use parameterized queries**: Prevent injection attacks
3. **Rate limit**: Respect rate limits to avoid blocking
4. **Sanitize outputs**: Clean data before display

---

## Examples by Use Case

### Simple Lookup
```
User: "Who is Neymar?"
Tools: search_player(name="Neymar") → get_player_stats(player_id)
```

### Complex Query
```
User: "Which players played for both Corinthians and Palmeiras?"
Tools:
  1. search_team("Corinthians") → team_id_1
  2. search_team("Palmeiras") → team_id_2
  3. get_team_roster(team_id_1) → players_1
  4. get_team_roster(team_id_2) → players_2
  5. Find intersection and get_player_career for each
```

### Statistical Analysis
```
User: "Compare Flamengo vs Fluminense over the last 10 years"
Tools:
  1. search_team("Flamengo") → team_id_1
  2. search_team("Fluminense") → team_id_2
  3. get_head_to_head(team_id_1, team_id_2)
  4. get_rivalry_stats(team_id_1, team_id_2)
```

---

## Changelog

### Version 1.0.0 (2025-10-30)
- Initial API documentation
- 15 core tools implemented
- Player, Team, Match, Competition, and Analysis tools
- Comprehensive error handling
- Rate limiting support

---

## Support

For API support and questions:
- GitHub Issues: [brazil-bench-hive/issues](https://github.com/yourusername/brazil-bench-hive/issues)
- Documentation: [README.md](../README.md)
- Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
