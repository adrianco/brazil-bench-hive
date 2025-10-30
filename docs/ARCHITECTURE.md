# Brazilian Soccer Knowledge Graph - System Architecture

## Overview

This project implements a Model Context Protocol (MCP) server that provides natural language access to Brazilian soccer data through a Neo4j knowledge graph. The system allows Claude AI to answer complex questions about Brazilian soccer players, teams, matches, and competitions using graph traversal and semantic queries.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude AI                             │
│              (Natural Language Interface)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol
                     │ (Tool Invocation)
┌────────────────────▼────────────────────────────────────────┐
│                   MCP Server                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Tool Registry                            │  │
│  │  • search_player      • get_player_stats              │  │
│  │  • search_team        • get_team_roster               │  │
│  │  • get_match_details  • search_matches                │  │
│  │  • get_competition    • get_head_to_head              │  │
│  │  • find_teammates     • analyze_rivalry               │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │            Business Logic Layer                       │  │
│  │  • Query Builder    • Result Formatter                │  │
│  │  • Data Aggregator  • Validation                      │  │
│  └───────────────────┬──────────────────────────────────┘  │
└────────────────────┬─┴────────────────────────────────────┘
                     │ Neo4j Bolt Protocol
                     │ (Cypher Queries)
┌────────────────────▼────────────────────────────────────────┐
│                    Neo4j Database                            │
│                 (Knowledge Graph Storage)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Nodes:                                                │  │
│  │  • Player      • Team       • Match                   │  │
│  │  • Competition • Stadium    • Coach                   │  │
│  │                                                        │  │
│  │ Relationships:                                        │  │
│  │  • PLAYS_FOR    • SCORED_IN    • ASSISTED_IN         │  │
│  │  • COMPETED_IN  • MANAGED_BY   • TRANSFERRED_TO      │  │
│  │  • PLAYED_AT    • YELLOW_CARD  • RED_CARD            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ Data Import
┌────────────────────▼────────────────────────────────────────┐
│                  Data Sources                                │
│  • Kaggle Datasets (Brazilian Football Matches)             │
│  • API-Football (Current Season Data)                       │
│  • TheSportsDB (Media & Metadata)                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Claude AI Interface
- **Purpose**: Natural language query interface for users
- **Communication**: MCP protocol for tool discovery and invocation
- **Capabilities**:
  - Understands complex multi-hop queries
  - Combines multiple tool calls
  - Synthesizes data into natural responses

### 2. MCP Server
- **Framework**: Python MCP Server SDK
- **Port**: Configurable (stdio mode for Claude integration)
- **Features**:
  - Tool registration and discovery
  - Parameter validation
  - Error handling and logging
  - Response formatting

### 3. Neo4j Knowledge Graph
- **Version**: Neo4j 2025.09.0
- **Database**: `brazil-kg`
- **Connection**:
  - HTTP: `http://localhost:7474`
  - Bolt: `bolt://localhost:7687`
- **Credentials**:
  - Username: `neo4j`
  - Password: `password` (development)
- **Plugins**: APOC (Awesome Procedures on Cypher)

## Data Model

### Core Entities (Nodes)

#### Player
```cypher
(:Player {
  player_id: String,      // Unique identifier
  name: String,           // Full name
  birth_date: Date,       // Date of birth
  nationality: String,    // Country
  position: String,       // Forward, Midfielder, etc.
  jersey_number: Integer, // Shirt number
  current_team_id: String // Reference to current team
})
```

#### Team
```cypher
(:Team {
  team_id: String,       // Unique identifier
  name: String,          // Team name
  city: String,          // Home city
  stadium: String,       // Stadium name
  founded_year: Integer, // Year founded
  colors: String         // Team colors
})
```

#### Match
```cypher
(:Match {
  match_id: String,       // Unique identifier
  date: Date,             // Match date
  home_team_id: String,   // Home team
  away_team_id: String,   // Away team
  home_score: Integer,    // Home team score
  away_score: Integer,    // Away team score
  competition_id: String, // Competition reference
  stadium_id: String,     // Stadium reference
  attendance: Integer     // Attendance count
})
```

#### Competition
```cypher
(:Competition {
  competition_id: String, // Unique identifier
  name: String,           // Competition name
  season: String,         // Season (e.g., "2023")
  type: String,           // "league" or "cup"
  tier: Integer           // Competition tier (1, 2, etc.)
})
```

#### Stadium
```cypher
(:Stadium {
  stadium_id: String,    // Unique identifier
  name: String,          // Stadium name
  city: String,          // Location
  capacity: Integer,     // Seating capacity
  opened_year: Integer   // Year opened
})
```

#### Coach
```cypher
(:Coach {
  coach_id: String,      // Unique identifier
  name: String,          // Full name
  nationality: String,   // Country
  birth_date: Date       // Date of birth
})
```

### Relationships (Edges)

#### PLAYS_FOR
```cypher
(player:Player)-[:PLAYS_FOR {
  from_date: Date,       // Start date
  to_date: Date,         // End date (null if current)
  jersey_number: Integer // Number worn
}]->(team:Team)
```

#### SCORED_IN
```cypher
(player:Player)-[:SCORED_IN {
  minute: Integer,       // Goal minute
  goal_type: String,     // "penalty", "open_play", etc.
  assist_by: String      // Player ID of assist provider
}]->(match:Match)
```

#### ASSISTED_IN
```cypher
(player:Player)-[:ASSISTED_IN {
  minute: Integer,       // Assist minute
  goal_scorer: String    // Player ID who scored
}]->(match:Match)
```

#### COMPETED_IN
```cypher
(team:Team)-[:COMPETED_IN {
  home_away: String,     // "home" or "away"
  result: String         // "win", "loss", "draw"
}]->(match:Match)
```

#### PART_OF
```cypher
(match:Match)-[:PART_OF]->(competition:Competition)
```

#### PLAYED_AT
```cypher
(match:Match)-[:PLAYED_AT]->(stadium:Stadium)
```

#### MANAGES
```cypher
(coach:Coach)-[:MANAGES {
  from_date: Date,       // Start date
  to_date: Date          // End date (null if current)
}]->(team:Team)
```

#### TRANSFERRED_TO
```cypher
(player:Player)-[:TRANSFERRED_TO {
  transfer_date: Date,   // Transfer date
  fee: Float,            // Transfer fee
  from_team_id: String   // Previous team
}]->(team:Team)
```

#### YELLOW_CARD_IN / RED_CARD_IN
```cypher
(player:Player)-[:YELLOW_CARD_IN {
  minute: Integer,       // Card minute
  reason: String         // Reason if available
}]->(match:Match)
```

## MCP Tools

### Player Tools

#### `search_player`
**Description**: Search for players by name, team, or position
**Parameters**:
- `name` (required): Player name (partial match supported)
- `team` (optional): Filter by current team
- `position` (optional): Filter by position

**Returns**: List of matching players with basic information

#### `get_player_stats`
**Description**: Get detailed statistics for a player
**Parameters**:
- `player_id` (required): Unique player identifier
- `season` (optional): Filter by specific season

**Returns**: Goals, assists, matches played, cards received

#### `get_player_career`
**Description**: Get complete career history for a player
**Parameters**:
- `player_id` (required): Unique player identifier

**Returns**: All teams played for, transfers, major achievements

#### `get_player_transfers`
**Description**: Get transfer history for a player
**Parameters**:
- `player_id` (required): Unique player identifier

**Returns**: List of transfers with dates, teams, and fees

### Team Tools

#### `search_team`
**Description**: Search for teams by name
**Parameters**:
- `name` (required): Team name (partial match supported)

**Returns**: List of matching teams with basic information

#### `get_team_roster`
**Description**: Get current or historical roster for a team
**Parameters**:
- `team_id` (required): Unique team identifier
- `season` (optional): Filter by specific season

**Returns**: List of players with positions and jersey numbers

#### `get_team_stats`
**Description**: Get statistics for a team
**Parameters**:
- `team_id` (required): Unique team identifier
- `season` (optional): Filter by specific season

**Returns**: Wins, losses, draws, goals for/against, points

#### `get_team_history`
**Description**: Get historical information about a team
**Parameters**:
- `team_id` (required): Unique team identifier

**Returns**: Championships won, notable players, historical facts

### Match Tools

#### `get_match_details`
**Description**: Get detailed information about a specific match
**Parameters**:
- `match_id` (required): Unique match identifier

**Returns**: Teams, score, goals, cards, attendance, stadium

#### `search_matches`
**Description**: Search for matches by team and date range
**Parameters**:
- `team` (optional): Filter by team name
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `competition` (optional): Filter by competition

**Returns**: List of matches matching criteria

#### `get_head_to_head`
**Description**: Get head-to-head statistics between two teams
**Parameters**:
- `team1_id` (required): First team identifier
- `team2_id` (required): Second team identifier

**Returns**: Historical results, aggregate statistics

#### `get_match_scorers`
**Description**: Get all goal scorers in a specific match
**Parameters**:
- `match_id` (required): Unique match identifier

**Returns**: List of scorers with times and goal types

### Competition Tools

#### `get_competition_standings`
**Description**: Get current standings for a competition
**Parameters**:
- `competition_id` (required): Competition identifier
- `season` (required): Season year

**Returns**: Team rankings with points, wins, losses, draws

#### `get_competition_top_scorers`
**Description**: Get top scorers for a competition
**Parameters**:
- `competition_id` (required): Competition identifier
- `season` (required): Season year

**Returns**: List of top scorers with goal counts

#### `get_competition_matches`
**Description**: Get all matches in a competition
**Parameters**:
- `competition_id` (required): Competition identifier
- `season` (required): Season year

**Returns**: List of matches in chronological order

### Analysis Tools

#### `find_common_teammates`
**Description**: Find players who were teammates of two given players
**Parameters**:
- `player1_id` (required): First player identifier
- `player2_id` (required): Second player identifier

**Returns**: List of common teammates with teams and dates

#### `get_rivalry_stats`
**Description**: Analyze rivalry statistics between two teams
**Parameters**:
- `team1_id` (required): First team identifier
- `team2_id` (required): Second team identifier

**Returns**: Historical results, trends, notable matches

#### `find_players_by_career_path`
**Description**: Find players matching specific career criteria
**Parameters**:
- `criteria` (required): Object with filters (teams, achievements, etc.)

**Returns**: List of players matching criteria

## Data Flow

### Query Processing Flow

1. **User Input**: Natural language question to Claude
   ```
   "Which players have played for both Corinthians and Palmeiras?"
   ```

2. **Tool Selection**: Claude determines relevant MCP tools
   ```
   1. search_team("Corinthians") → team_id_1
   2. search_team("Palmeiras") → team_id_2
   3. get_team_roster(team_id_1) → players_1
   4. get_team_roster(team_id_2) → players_2
   5. Find intersection of players
   ```

3. **Query Execution**: MCP server translates to Cypher
   ```cypher
   MATCH (p:Player)-[:PLAYS_FOR]->(t1:Team {name: "Corinthians"})
   MATCH (p)-[:PLAYS_FOR]->(t2:Team {name: "Palmeiras"})
   RETURN DISTINCT p.name, p.player_id
   ```

4. **Result Processing**: Format and return data
   ```json
   {
     "players": [
       {"name": "Player X", "player_id": "P123"},
       {"name": "Player Y", "player_id": "P456"}
     ]
   }
   ```

5. **Response Synthesis**: Claude creates natural language response
   ```
   "I found 3 players who played for both Corinthians and Palmeiras..."
   ```

## Performance Optimization

### Indexing Strategy
```cypher
// Create indexes for fast lookups
CREATE INDEX player_name FOR (p:Player) ON (p.name);
CREATE INDEX team_name FOR (t:Team) ON (t.name);
CREATE INDEX match_date FOR (m:Match) ON (m.date);
CREATE INDEX competition_season FOR (c:Competition) ON (c.season);
```

### Caching
- Frequently accessed queries cached in-memory
- Pre-computed aggregations for common statistics
- Cache invalidation on data updates

### Query Optimization
- Limit result sets to reasonable sizes (default: 100)
- Use pagination for large result sets
- Optimize relationship traversal depth
- Use APOC procedures for complex operations

## Security Considerations

### Access Control
- Read-only access for MCP tools
- No direct database modification through MCP
- Input validation and sanitization
- Parameterized queries to prevent injection

### Data Privacy
- No personally identifiable information (PII)
- Public data sources only
- Age-appropriate content filtering

## Scalability

### Current Capacity
- ~50,000 players
- ~500 teams
- ~100,000 matches
- Sub-second query response times

### Future Expansion
- Add more competitions and seasons
- Include international matches
- Add player statistics and performance metrics
- Support real-time updates

## Technology Stack

- **Language**: Python 3.10+
- **MCP Framework**: `mcp` Python package
- **Graph Database**: Neo4j 2025.09.0
- **Database Driver**: `neo4j` Python driver
- **Testing**: pytest with BDD (Given-When-Then)
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git & GitHub

## Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────────────┐
│  Developer Machine                          │
│  ┌───────────────────────────────────────┐ │
│  │  Claude Code / CLI                    │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │  MCP Server (Python Process)          │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │  Neo4j (Docker Container)             │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Production (Future)
- Scalable Neo4j cluster
- Load-balanced MCP servers
- API gateway for rate limiting
- Monitoring and logging infrastructure

## Error Handling

### Error Types
1. **Not Found**: Entity doesn't exist
2. **Invalid Parameters**: Malformed input
3. **Query Timeout**: Complex query exceeded time limit
4. **Database Connection**: Neo4j unavailable
5. **Data Inconsistency**: Graph integrity issues

### Error Responses
```json
{
  "error": {
    "code": "PLAYER_NOT_FOUND",
    "message": "No player found with ID: P12345",
    "details": {
      "searched_id": "P12345",
      "suggestions": ["Did you mean P12346?"]
    }
  }
}
```

## Monitoring and Logging

### Metrics Tracked
- Query response times
- Tool invocation counts
- Error rates
- Cache hit rates
- Database connection health

### Logging Levels
- **DEBUG**: Detailed query execution
- **INFO**: Tool invocations and results
- **WARN**: Slow queries, cache misses
- **ERROR**: Query failures, connection issues

## Future Enhancements

### Phase 4 (Planned)
1. **Real-time Data**: Integrate live match data APIs
2. **Advanced Analytics**: ML-based insights and predictions
3. **Media Integration**: Images, videos, match highlights
4. **Multi-language**: Support for Portuguese queries
5. **Mobile App**: Native mobile application
6. **Social Features**: Share queries and results
7. **Historical Expansion**: Add data from earlier decades
8. **Performance Metrics**: Advanced player performance analytics

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Brazilian Soccer Guide](../brazilian-soccer-mcp-guide.md)
- [Neo4j Setup](../NEO4J_SETUP.md)
