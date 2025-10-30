# Brazilian Soccer Knowledge Graph - Data Model & Schema Design

<!--
CONTEXT: Research deliverable for brazil-bench-hive project
PURPOSE: Complete Neo4j schema design for Brazilian soccer knowledge graph
AGENT: Researcher (swarm-1761784111350-vc2pgfssn)
DATE: 2025-10-30
STATUS: Research Phase Complete
DEPENDENCIES: NEO4J_SETUP.md, brazilian-soccer-mcp-guide.md
-->

## Executive Summary

This document defines the complete data model and Neo4j Cypher schema for the Brazilian Soccer Knowledge Graph. The schema is optimized for complex relationship queries, natural language processing via MCP tools, and efficient retrieval of historical soccer data.

**Key Design Principles:**
- Graph-first approach for relationship traversal
- Optimized for MCP tool queries (25+ question types)
- Supports both historical and current data
- Extensible for future enhancements
- Performance-optimized with constraints and indexes

---

## 1. Core Entity Definitions

### 1.1 Player Node

**Purpose**: Represents individual soccer players (current and historical)

**Label**: `:Player`

**Properties**:
```cypher
{
  player_id: STRING [REQUIRED, UNIQUE]  // Primary identifier (e.g., "P12345")
  name: STRING [REQUIRED]               // Full player name
  birth_date: DATE                      // Birth date (YYYY-MM-DD)
  nationality: STRING [REQUIRED]        // Primary nationality
  position: STRING                      // Playing position (Forward, Midfielder, Defender, Goalkeeper)
  jersey_number: INTEGER                // Current/last jersey number
  height_cm: INTEGER                    // Height in centimeters
  weight_kg: INTEGER                    // Weight in kilograms
  preferred_foot: STRING                // Left, Right, or Both
  current_team_id: STRING               // Reference to current team (nullable)
  market_value_eur: INTEGER             // Market value in euros (if available)
  image_url: STRING                     // Player photo URL
  created_at: DATETIME                  // Record creation timestamp
  updated_at: DATETIME                  // Last update timestamp
}
```

**Business Rules**:
- `player_id` must be globally unique across all players
- `position` should use standardized values: "Forward", "Midfielder", "Defender", "Goalkeeper"
- Historical players may have null `current_team_id`
- `birth_date` enables age-based queries and career timeline analysis

---

### 1.2 Team Node

**Purpose**: Represents soccer clubs/teams in Brazilian leagues

**Label**: `:Team`

**Properties**:
```cypher
{
  team_id: STRING [REQUIRED, UNIQUE]    // Primary identifier (e.g., "T123")
  name: STRING [REQUIRED]               // Official team name
  short_name: STRING                    // Abbreviated name (e.g., "FLA" for Flamengo)
  city: STRING [REQUIRED]               // Home city
  state: STRING                         // Brazilian state code (e.g., "RJ", "SP")
  stadium_id: STRING                    // Reference to home stadium
  founded_year: INTEGER                 // Year established
  colors: LIST<STRING>                  // Team colors (e.g., ["Red", "Black"])
  logo_url: STRING                      // Team logo URL
  official_website: STRING              // Official website URL
  league_tier: INTEGER                  // Current league tier (1=Serie A, 2=Serie B, etc.)
  created_at: DATETIME
  updated_at: DATETIME
}
```

**Business Rules**:
- `team_id` must be unique across all teams
- `stadium_id` references Stadium node for home venue
- `colors` stored as array for flexible querying
- `league_tier` tracks current competitive level

---

### 1.3 Match Node

**Purpose**: Represents individual soccer matches

**Label**: `:Match`

**Properties**:
```cypher
{
  match_id: STRING [REQUIRED, UNIQUE]   // Primary identifier (e.g., "M67890")
  date: DATE [REQUIRED]                 // Match date (YYYY-MM-DD)
  time: TIME                            // Kickoff time
  home_team_id: STRING [REQUIRED]       // Home team reference
  away_team_id: STRING [REQUIRED]       // Away team reference
  home_score: INTEGER                   // Final home team score
  away_score: INTEGER                   // Final away team score
  home_halftime_score: INTEGER          // Halftime home score
  away_halftime_score: INTEGER          // Halftime away score
  competition_id: STRING [REQUIRED]     // Competition reference
  stadium_id: STRING                    // Venue reference
  attendance: INTEGER                   // Number of spectators
  referee: STRING                       // Referee name
  match_status: STRING                  // Scheduled, Live, Completed, Postponed, Cancelled
  weather_condition: STRING             // Weather during match
  created_at: DATETIME
  updated_at: DATETIME
}
```

**Business Rules**:
- `match_id` must be unique across all matches
- `match_status` enables filtering by completion state
- Scores are nullable until match completion
- `home_team_id` and `away_team_id` must reference valid Team nodes

---

### 1.4 Competition Node

**Purpose**: Represents tournaments and league seasons

**Label**: `:Competition`

**Properties**:
```cypher
{
  competition_id: STRING [REQUIRED, UNIQUE]  // Primary identifier (e.g., "C001")
  name: STRING [REQUIRED]                    // Competition name
  short_name: STRING                         // Abbreviation (e.g., "Brasileirão")
  season: STRING [REQUIRED]                  // Season year (e.g., "2023", "2023/24")
  type: STRING [REQUIRED]                    // League, Cup, Playoff
  tier: INTEGER                              // Competition tier (1=top tier)
  country: STRING                            // Country code (BR)
  start_date: DATE                           // Season start date
  end_date: DATE                             // Season end date
  total_rounds: INTEGER                      // Number of rounds/matchdays
  logo_url: STRING                           // Competition logo URL
  created_at: DATETIME
  updated_at: DATETIME
}
```

**Business Rules**:
- `competition_id` unique per competition-season combination
- `type` values: "League", "Cup", "Playoff", "Supercup"
- `season` format: single year for calendar year, "YYYY/YY" for split seasons

---

### 1.5 Stadium Node

**Purpose**: Represents soccer stadiums/venues

**Label**: `:Stadium`

**Properties**:
```cypher
{
  stadium_id: STRING [REQUIRED, UNIQUE]  // Primary identifier (e.g., "S555")
  name: STRING [REQUIRED]                // Official stadium name
  city: STRING [REQUIRED]                // City location
  state: STRING                          // State code
  capacity: INTEGER                      // Maximum capacity
  opened_year: INTEGER                   // Year opened/inaugurated
  surface_type: STRING                   // Grass, Artificial, Hybrid
  latitude: FLOAT                        // Geographic latitude
  longitude: FLOAT                       // Geographic longitude
  image_url: STRING                      // Stadium photo URL
  created_at: DATETIME
  updated_at: DATETIME
}
```

**Business Rules**:
- `stadium_id` must be unique
- `capacity` represents maximum seating/standing capacity
- Geographic coordinates enable location-based queries

---

### 1.6 Coach Node

**Purpose**: Represents team coaches/managers

**Label**: `:Coach`

**Properties**:
```cypher
{
  coach_id: STRING [REQUIRED, UNIQUE]   // Primary identifier (e.g., "C789")
  name: STRING [REQUIRED]               // Full name
  birth_date: DATE                      // Birth date
  nationality: STRING                   // Nationality
  coaching_license: STRING              // Coaching qualification level
  image_url: STRING                     // Coach photo URL
  created_at: DATETIME
  updated_at: DATETIME
}
```

**Business Rules**:
- `coach_id` must be unique
- Supports historical and current coaches

---

## 2. Relationship Definitions

### 2.1 Player-Team Relationships

#### PLAYS_FOR
**Purpose**: Current or historical team membership

```cypher
(:Player)-[r:PLAYS_FOR]->(:Team)

Properties:
{
  start_date: DATE [REQUIRED]           // Contract/membership start
  end_date: DATE                        // Contract end (null if current)
  jersey_number: INTEGER                // Jersey number during this period
  is_current: BOOLEAN                   // Active membership flag
  is_on_loan: BOOLEAN                   // Loan status
  loan_from_team_id: STRING             // If on loan, source team
}
```

**Query Examples**:
- Current roster: `MATCH (p:Player)-[r:PLAYS_FOR {is_current: true}]->(t:Team)`
- Player career: `MATCH (p:Player)-[r:PLAYS_FOR]->(t:Team) RETURN t, r ORDER BY r.start_date`

---

#### TRANSFERRED_TO
**Purpose**: Transfer events between teams

```cypher
(:Player)-[r:TRANSFERRED_TO]->(:Team)

Properties:
{
  transfer_date: DATE [REQUIRED]        // Transfer completion date
  from_team_id: STRING                  // Previous team reference
  transfer_fee_eur: INTEGER             // Transfer fee in euros
  transfer_type: STRING                 // Permanent, Loan, Free, End-of-loan
  contract_duration_years: INTEGER      // Contract length
}
```

**Business Rules**:
- `from_team_id` references the previous team
- `transfer_type` values: "Permanent", "Loan", "Free", "End-of-loan"
- Enables tracking of player movement patterns

---

### 2.2 Player-Match Relationships

#### SCORED_IN
**Purpose**: Goal-scoring events

```cypher
(:Player)-[r:SCORED_IN]->(:Match)

Properties:
{
  minute: INTEGER [REQUIRED]            // Goal minute
  goal_type: STRING                     // Open-play, Penalty, Free-kick, Header, Own-goal
  assisted_by_player_id: STRING         // Assisting player reference
  team_id: STRING [REQUIRED]            // Team player scored for
  video_url: STRING                     // Goal highlight URL
}
```

**Query Examples**:
- Top scorers: `MATCH (p:Player)-[r:SCORED_IN]->(m:Match) RETURN p.name, count(r) ORDER BY count(r) DESC`
- Goals in specific competition: Filter by match competition_id

---

#### ASSISTED_IN
**Purpose**: Assist/goal creation events

```cypher
(:Player)-[r:ASSISTED_IN]->(:Match)

Properties:
{
  minute: INTEGER [REQUIRED]            // Assist minute
  scorer_player_id: STRING [REQUIRED]   // Player who scored
  assist_type: STRING                   // Pass, Cross, Through-ball, Set-piece
  team_id: STRING [REQUIRED]            // Team player assisted for
}
```

---

#### YELLOW_CARD_IN
**Purpose**: Yellow card disciplinary events

```cypher
(:Player)-[r:YELLOW_CARD_IN]->(:Match)

Properties:
{
  minute: INTEGER [REQUIRED]            // Card minute
  reason: STRING                        // Foul, Dissent, Unsporting, Delaying
  team_id: STRING [REQUIRED]            // Team player represented
}
```

---

#### RED_CARD_IN
**Purpose**: Red card/ejection events

```cypher
(:Player)-[r:RED_CARD_IN]->(:Match)

Properties:
{
  minute: INTEGER [REQUIRED]            // Card minute
  reason: STRING                        // Violent-conduct, Denial, Second-yellow, Abusive
  team_id: STRING [REQUIRED]            // Team player represented
}
```

---

#### PLAYED_IN
**Purpose**: General match participation

```cypher
(:Player)-[r:PLAYED_IN]->(:Match)

Properties:
{
  team_id: STRING [REQUIRED]            // Team played for
  minutes_played: INTEGER               // Minutes on field
  starting_lineup: BOOLEAN              // Started match or substitute
  position: STRING                      // Position played
  substituted_in_minute: INTEGER        // When substituted (if applicable)
  substituted_out_minute: INTEGER       // When substituted off
}
```

---

### 2.3 Team-Match Relationships

#### COMPETED_IN (Home)
**Purpose**: Home team participation

```cypher
(:Team)-[r:COMPETED_IN {home_away: "HOME"}]->(:Match)

Properties:
{
  home_away: STRING [REQUIRED]          // "HOME"
  final_score: INTEGER                  // Team's final score
  result: STRING                        // Win, Draw, Loss
}
```

---

#### COMPETED_IN (Away)
**Purpose**: Away team participation

```cypher
(:Team)-[r:COMPETED_IN {home_away: "AWAY"}]->(:Match)

Properties:
{
  home_away: STRING [REQUIRED]          // "AWAY"
  final_score: INTEGER                  // Team's final score
  result: STRING                        // Win, Draw, Loss
}
```

**Query Examples**:
- Team record: `MATCH (t:Team)-[r:COMPETED_IN]->(m:Match) RETURN r.result, count(*)`
- Head-to-head: Match both teams in same match with home_away filter

---

### 2.4 Match-Competition Relationships

#### PART_OF
**Purpose**: Match belongs to competition/season

```cypher
(:Match)-[r:PART_OF]->(:Competition)

Properties:
{
  round: INTEGER                        // Matchday/round number
  phase: STRING                         // Group-stage, Quarter-final, Final, etc.
  is_knockout: BOOLEAN                  // Knockout phase flag
}
```

---

### 2.5 Match-Stadium Relationships

#### PLAYED_AT
**Purpose**: Match venue

```cypher
(:Match)-[r:PLAYED_AT]->(:Stadium)

Properties:
{
  attendance: INTEGER                   // Actual attendance
  capacity_percentage: FLOAT            // Attendance as % of capacity
}
```

---

### 2.6 Coach-Team Relationships

#### MANAGES
**Purpose**: Coaching appointments

```cypher
(:Coach)-[r:MANAGES]->(:Team)

Properties:
{
  start_date: DATE [REQUIRED]           // Appointment start
  end_date: DATE                        // Appointment end (null if current)
  is_current: BOOLEAN                   // Active appointment
  matches_managed: INTEGER              // Total matches
  wins: INTEGER                         // Matches won
  draws: INTEGER                        // Matches drawn
  losses: INTEGER                       // Matches lost
}
```

---

## 3. Neo4j Schema Implementation

### 3.1 Constraints (Uniqueness & Data Integrity)

```cypher
// Player constraints
CREATE CONSTRAINT player_id_unique IF NOT EXISTS
FOR (p:Player) REQUIRE p.player_id IS UNIQUE;

CREATE CONSTRAINT player_name_required IF NOT EXISTS
FOR (p:Player) REQUIRE p.name IS NOT NULL;

// Team constraints
CREATE CONSTRAINT team_id_unique IF NOT EXISTS
FOR (t:Team) REQUIRE t.team_id IS UNIQUE;

CREATE CONSTRAINT team_name_required IF NOT EXISTS
FOR (t:Team) REQUIRE t.name IS NOT NULL;

// Match constraints
CREATE CONSTRAINT match_id_unique IF NOT EXISTS
FOR (m:Match) REQUIRE m.match_id IS UNIQUE;

CREATE CONSTRAINT match_date_required IF NOT EXISTS
FOR (m:Match) REQUIRE m.date IS NOT NULL;

// Competition constraints
CREATE CONSTRAINT competition_id_unique IF NOT EXISTS
FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE;

CREATE CONSTRAINT competition_name_season_unique IF NOT EXISTS
FOR (c:Competition) REQUIRE (c.name, c.season) IS UNIQUE;

// Stadium constraints
CREATE CONSTRAINT stadium_id_unique IF NOT EXISTS
FOR (s:Stadium) REQUIRE s.stadium_id IS UNIQUE;

// Coach constraints
CREATE CONSTRAINT coach_id_unique IF NOT EXISTS
FOR (co:Coach) REQUIRE co.coach_id IS UNIQUE;
```

---

### 3.2 Indexes (Query Performance Optimization)

```cypher
// Player indexes
CREATE INDEX player_name_index IF NOT EXISTS
FOR (p:Player) ON (p.name);

CREATE INDEX player_position_index IF NOT EXISTS
FOR (p:Player) ON (p.position);

CREATE INDEX player_nationality_index IF NOT EXISTS
FOR (p:Player) ON (p.nationality);

// Team indexes
CREATE INDEX team_name_index IF NOT EXISTS
FOR (t:Team) ON (t.name);

CREATE INDEX team_city_index IF NOT EXISTS
FOR (t:Team) ON (t.city);

// Match indexes
CREATE INDEX match_date_index IF NOT EXISTS
FOR (m:Match) ON (m.date);

CREATE INDEX match_status_index IF NOT EXISTS
FOR (m:Match) ON (m.match_status);

CREATE INDEX match_competition_index IF NOT EXISTS
FOR (m:Match) ON (m.competition_id);

// Competition indexes
CREATE INDEX competition_season_index IF NOT EXISTS
FOR (c:Competition) ON (c.season);

CREATE INDEX competition_type_index IF NOT EXISTS
FOR (c:Competition) ON (c.type);

// Stadium indexes
CREATE INDEX stadium_name_index IF NOT EXISTS
FOR (s:Stadium) ON (s.name);

CREATE INDEX stadium_city_index IF NOT EXISTS
FOR (s:Stadium) ON (s.city);

// Coach indexes
CREATE INDEX coach_name_index IF NOT EXISTS
FOR (co:Coach) ON (co.name);
```

---

### 3.3 Full-Text Search Indexes

```cypher
// Enable fuzzy name searches for players
CREATE FULLTEXT INDEX player_name_fulltext IF NOT EXISTS
FOR (p:Player) ON EACH [p.name];

// Enable fuzzy name searches for teams
CREATE FULLTEXT INDEX team_name_fulltext IF NOT EXISTS
FOR (t:Team) ON EACH [t.name, t.short_name];

// Enable stadium search
CREATE FULLTEXT INDEX stadium_name_fulltext IF NOT EXISTS
FOR (s:Stadium) ON EACH [s.name];
```

**Usage Example**:
```cypher
CALL db.index.fulltext.queryNodes("player_name_fulltext", "Neymar~")
YIELD node, score
RETURN node.name, score
ORDER BY score DESC LIMIT 5;
```

---

## 4. Query Patterns for MCP Tools

### 4.1 Player Queries

#### Search Player by Name
```cypher
// Exact match
MATCH (p:Player {name: $playerName})
RETURN p;

// Fuzzy match
CALL db.index.fulltext.queryNodes("player_name_fulltext", $searchTerm)
YIELD node AS p, score
RETURN p, score
ORDER BY score DESC LIMIT 10;
```

#### Get Player Career History
```cypher
MATCH (p:Player {player_id: $playerId})-[r:PLAYS_FOR]->(t:Team)
RETURN t.name, r.start_date, r.end_date, r.jersey_number
ORDER BY r.start_date DESC;
```

#### Get Player Statistics for Season
```cypher
MATCH (p:Player {player_id: $playerId})-[scored:SCORED_IN]->(m:Match)-[:PART_OF]->(c:Competition {season: $season})
WITH p, count(scored) AS goals
MATCH (p)-[assisted:ASSISTED_IN]->(m2:Match)-[:PART_OF]->(c2:Competition {season: $season})
WITH p, goals, count(assisted) AS assists
MATCH (p)-[played:PLAYED_IN]->(m3:Match)-[:PART_OF]->(c3:Competition {season: $season})
RETURN p.name, goals, assists, count(played) AS matches_played, sum(played.minutes_played) AS total_minutes;
```

---

### 4.2 Team Queries

#### Get Team Roster for Season
```cypher
MATCH (p:Player)-[r:PLAYS_FOR {is_current: true}]->(t:Team {team_id: $teamId})
OPTIONAL MATCH (p)-[scored:SCORED_IN]->(m:Match)-[:PART_OF]->(c:Competition {season: $season})
WHERE m.home_team_id = $teamId OR m.away_team_id = $teamId
RETURN p.name, p.position, r.jersey_number, count(scored) AS goals
ORDER BY p.position, p.name;
```

#### Get Team Match Results
```cypher
MATCH (t:Team {team_id: $teamId})-[r:COMPETED_IN]->(m:Match)-[:PART_OF]->(c:Competition {season: $season})
WHERE m.match_status = 'Completed'
RETURN m.date,
       CASE WHEN m.home_team_id = $teamId THEN m.away_team_id ELSE m.home_team_id END AS opponent_id,
       r.final_score AS team_score,
       CASE WHEN m.home_team_id = $teamId THEN m.away_score ELSE m.home_score END AS opponent_score,
       r.result
ORDER BY m.date DESC;
```

---

### 4.3 Match Queries

#### Get Match Details with Scorers
```cypher
MATCH (m:Match {match_id: $matchId})
MATCH (m)-[:PLAYED_AT]->(s:Stadium)
MATCH (m)-[:PART_OF]->(c:Competition)
OPTIONAL MATCH (p:Player)-[scored:SCORED_IN]->(m)
RETURN m, s, c, collect({player: p.name, minute: scored.minute, type: scored.goal_type}) AS goals;
```

#### Head-to-Head Record
```cypher
MATCH (t1:Team {team_id: $team1Id})-[r1:COMPETED_IN]->(m:Match)<-[r2:COMPETED_IN]-(t2:Team {team_id: $team2Id})
WHERE m.match_status = 'Completed'
RETURN m.date, r1.final_score AS team1_score, r2.final_score AS team2_score, r1.result AS team1_result
ORDER BY m.date DESC;
```

---

### 4.4 Competition Queries

#### Competition Standings (Calculated)
```cypher
MATCH (t:Team)-[r:COMPETED_IN]->(m:Match)-[:PART_OF]->(c:Competition {competition_id: $competitionId, season: $season})
WHERE m.match_status = 'Completed'
WITH t,
     sum(CASE WHEN r.result = 'Win' THEN 3 WHEN r.result = 'Draw' THEN 1 ELSE 0 END) AS points,
     sum(CASE WHEN r.result = 'Win' THEN 1 ELSE 0 END) AS wins,
     sum(CASE WHEN r.result = 'Draw' THEN 1 ELSE 0 END) AS draws,
     sum(CASE WHEN r.result = 'Loss' THEN 1 ELSE 0 END) AS losses,
     sum(r.final_score) AS goals_for,
     sum(CASE WHEN r.home_away = 'HOME' THEN m.away_score ELSE m.home_score END) AS goals_against
RETURN t.name, points, wins, draws, losses, goals_for, goals_against, (goals_for - goals_against) AS goal_difference
ORDER BY points DESC, goal_difference DESC, goals_for DESC;
```

#### Top Scorers in Competition
```cypher
MATCH (p:Player)-[scored:SCORED_IN]->(m:Match)-[:PART_OF]->(c:Competition {competition_id: $competitionId, season: $season})
WHERE scored.goal_type <> 'Own-goal'
RETURN p.name, p.player_id, count(scored) AS goals
ORDER BY goals DESC LIMIT 10;
```

---

### 4.5 Complex Analysis Queries

#### Players Who Played for Multiple Rival Teams
```cypher
MATCH (p:Player)-[r1:PLAYS_FOR]->(t1:Team {team_id: $team1Id})
MATCH (p)-[r2:PLAYS_FOR]->(t2:Team {team_id: $team2Id})
WHERE r1.start_date < r2.start_date OR r2.start_date < r1.start_date
RETURN p.name,
       t1.name AS first_team, r1.start_date AS first_start, r1.end_date AS first_end,
       t2.name AS second_team, r2.start_date AS second_start, r2.end_date AS second_end
ORDER BY r1.start_date;
```

#### Find Common Teammates
```cypher
MATCH (p1:Player {player_id: $player1Id})-[r1:PLAYS_FOR]->(t:Team)<-[r2:PLAYS_FOR]-(p2:Player {player_id: $player2Id})
WHERE r1.start_date <= r2.end_date AND r2.start_date <= r1.end_date
RETURN t.name AS team, r1.start_date AS player1_start, r1.end_date AS player1_end,
       r2.start_date AS player2_start, r2.end_date AS player2_end;
```

---

## 5. Data Quality & Validation Rules

### 5.1 Referential Integrity

**Enforced via Application Logic** (Neo4j doesn't enforce foreign key constraints):

1. **Player.current_team_id** must reference existing Team.team_id
2. **Team.stadium_id** must reference existing Stadium.stadium_id
3. **Match.home_team_id** and **Match.away_team_id** must reference existing Team.team_id
4. **Match.competition_id** must reference existing Competition.competition_id
5. **SCORED_IN.assisted_by_player_id** must reference existing Player.player_id

### 5.2 Business Logic Validation

```cypher
// Validate no player has overlapping active contracts
MATCH (p:Player)-[r1:PLAYS_FOR]->(t1:Team)
MATCH (p)-[r2:PLAYS_FOR]->(t2:Team)
WHERE r1 <> r2
  AND r1.is_current = true
  AND r2.is_current = true
  AND NOT r1.is_on_loan
  AND NOT r2.is_on_loan
RETURN p.name, t1.name, t2.name;
// Should return empty result

// Validate match scores match relationship goals
MATCH (m:Match {match_id: $matchId})
MATCH (p:Player)-[scored:SCORED_IN {team_id: m.home_team_id}]->(m)
WITH m, count(scored) AS home_goals_from_relationships
WHERE m.home_score <> home_goals_from_relationships
RETURN m.match_id, m.home_score AS recorded_score, home_goals_from_relationships AS calculated_goals;
```

---

## 6. Performance Optimization Guidelines

### 6.1 Query Optimization Best Practices

1. **Use indexes**: Always filter on indexed properties
2. **Limit result sets**: Use `LIMIT` clause for large datasets
3. **Avoid Cartesian products**: Use `OPTIONAL MATCH` carefully
4. **Profile queries**: Use `EXPLAIN` and `PROFILE` to analyze execution plans

Example:
```cypher
PROFILE
MATCH (p:Player {name: "Pelé"})-[r:SCORED_IN]->(m:Match)
RETURN count(r);
```

### 6.2 Pre-computed Aggregations

For frequently accessed statistics, consider materialized views or cached properties:

```cypher
// Add career statistics to Player nodes (run periodically)
MATCH (p:Player)-[scored:SCORED_IN]->(m:Match)
WITH p, count(scored) AS total_goals
SET p.career_goals = total_goals;

// Then query becomes:
MATCH (p:Player) WHERE p.career_goals > 100
RETURN p.name, p.career_goals ORDER BY p.career_goals DESC;
```

---

## 7. Migration & Data Loading Strategy

### 7.1 Initial Load Order

1. **Reference Data First**: Stadium, Competition
2. **Core Entities**: Team, Coach, Player
3. **Relationships**: MANAGES, PLAYS_FOR
4. **Transactional Data**: Match
5. **Event Data**: COMPETED_IN, SCORED_IN, ASSISTED_IN, PLAYED_IN

### 7.2 Bulk Load Template (CSV)

```cypher
// Load Players
LOAD CSV WITH HEADERS FROM 'file:///players.csv' AS row
CREATE (p:Player {
  player_id: row.player_id,
  name: row.name,
  birth_date: date(row.birth_date),
  nationality: row.nationality,
  position: row.position,
  created_at: datetime()
});

// Load PLAYS_FOR relationships
LOAD CSV WITH HEADERS FROM 'file:///player_teams.csv' AS row
MATCH (p:Player {player_id: row.player_id})
MATCH (t:Team {team_id: row.team_id})
CREATE (p)-[r:PLAYS_FOR {
  start_date: date(row.start_date),
  end_date: CASE row.end_date WHEN '' THEN null ELSE date(row.end_date) END,
  is_current: row.is_current = 'true',
  jersey_number: toInteger(row.jersey_number)
}]->(t);
```

---

## 8. Extension Points

### 8.1 Future Entity Types

- **Referee**: Track referee assignments and performance
- **Transfer**: Separate node for transfer events with detailed attributes
- **Injury**: Track player injuries and recovery
- **Award**: Individual and team awards/honors

### 8.2 Future Relationships

- **RIVALS_WITH**: Define rivalry relationships between teams
- **MENTORED_BY**: Player mentorship relationships
- **TRAINED_AT**: Youth academy relationships
- **SPONSORED_BY**: Commercial sponsorships

---

## 9. Appendix: Complete Schema Initialization Script

```cypher
// ============================================================
// BRAZILIAN SOCCER KNOWLEDGE GRAPH - SCHEMA INITIALIZATION
// ============================================================
// Run this script to create the complete schema with constraints and indexes
// Execute in Neo4j Browser or via cypher-shell

// ------------------------------------------------------------
// 1. CREATE CONSTRAINTS
// ------------------------------------------------------------

// Player constraints
CREATE CONSTRAINT player_id_unique IF NOT EXISTS
FOR (p:Player) REQUIRE p.player_id IS UNIQUE;

CREATE CONSTRAINT player_name_required IF NOT EXISTS
FOR (p:Player) REQUIRE p.name IS NOT NULL;

// Team constraints
CREATE CONSTRAINT team_id_unique IF NOT EXISTS
FOR (t:Team) REQUIRE t.team_id IS UNIQUE;

CREATE CONSTRAINT team_name_required IF NOT EXISTS
FOR (t:Team) REQUIRE t.name IS NOT NULL;

// Match constraints
CREATE CONSTRAINT match_id_unique IF NOT EXISTS
FOR (m:Match) REQUIRE m.match_id IS UNIQUE;

CREATE CONSTRAINT match_date_required IF NOT EXISTS
FOR (m:Match) REQUIRE m.date IS NOT NULL;

// Competition constraints
CREATE CONSTRAINT competition_id_unique IF NOT EXISTS
FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE;

CREATE CONSTRAINT competition_name_season_unique IF NOT EXISTS
FOR (c:Competition) REQUIRE (c.name, c.season) IS UNIQUE;

// Stadium constraints
CREATE CONSTRAINT stadium_id_unique IF NOT EXISTS
FOR (s:Stadium) REQUIRE s.stadium_id IS UNIQUE;

// Coach constraints
CREATE CONSTRAINT coach_id_unique IF NOT EXISTS
FOR (co:Coach) REQUIRE co.coach_id IS UNIQUE;

// ------------------------------------------------------------
// 2. CREATE INDEXES
// ------------------------------------------------------------

// Player indexes
CREATE INDEX player_name_index IF NOT EXISTS
FOR (p:Player) ON (p.name);

CREATE INDEX player_position_index IF NOT EXISTS
FOR (p:Player) ON (p.position);

CREATE INDEX player_nationality_index IF NOT EXISTS
FOR (p:Player) ON (p.nationality);

// Team indexes
CREATE INDEX team_name_index IF NOT EXISTS
FOR (t:Team) ON (t.name);

CREATE INDEX team_city_index IF NOT EXISTS
FOR (t:Team) ON (t.city);

// Match indexes
CREATE INDEX match_date_index IF NOT EXISTS
FOR (m:Match) ON (m.date);

CREATE INDEX match_status_index IF NOT EXISTS
FOR (m:Match) ON (m.match_status);

CREATE INDEX match_competition_index IF NOT EXISTS
FOR (m:Match) ON (m.competition_id);

// Competition indexes
CREATE INDEX competition_season_index IF NOT EXISTS
FOR (c:Competition) ON (c.season);

CREATE INDEX competition_type_index IF NOT EXISTS
FOR (c:Competition) ON (c.type);

// Stadium indexes
CREATE INDEX stadium_name_index IF NOT EXISTS
FOR (s:Stadium) ON (s.name);

CREATE INDEX stadium_city_index IF NOT EXISTS
FOR (s:Stadium) ON (s.city);

// Coach indexes
CREATE INDEX coach_name_index IF NOT EXISTS
FOR (co:Coach) ON (co.name);

// ------------------------------------------------------------
// 3. CREATE FULL-TEXT SEARCH INDEXES
// ------------------------------------------------------------

CREATE FULLTEXT INDEX player_name_fulltext IF NOT EXISTS
FOR (p:Player) ON EACH [p.name];

CREATE FULLTEXT INDEX team_name_fulltext IF NOT EXISTS
FOR (t:Team) ON EACH [t.name, t.short_name];

CREATE FULLTEXT INDEX stadium_name_fulltext IF NOT EXISTS
FOR (s:Stadium) ON EACH [s.name];

// ------------------------------------------------------------
// SCHEMA INITIALIZATION COMPLETE
// ------------------------------------------------------------
// To verify schema:
// CALL db.schema.visualization();
// CALL db.constraints();
// CALL db.indexes();
```

---

## 10. Summary & Recommendations

### Key Strengths of This Design

1. **Graph-Optimized**: Leverages Neo4j's strength in relationship traversal
2. **MCP-Ready**: Schema aligns with planned MCP tool requirements
3. **Performance-First**: Comprehensive indexing strategy
4. **Extensible**: Clear extension points for future features
5. **Query-Friendly**: Optimized for the 25+ demo questions

### Implementation Priority

**Phase 1 (MVP)**:
- Player, Team, Match, Competition nodes
- PLAYS_FOR, SCORED_IN, COMPETED_IN, PART_OF relationships
- Core constraints and indexes

**Phase 2 (Enhanced)**:
- Stadium, Coach nodes
- PLAYED_AT, MANAGES relationships
- Full-text search indexes

**Phase 3 (Advanced)**:
- ASSISTED_IN, YELLOW_CARD_IN, RED_CARD_IN relationships
- Pre-computed aggregations
- Query optimization

### Next Steps for Implementation Team

1. Review schema with stakeholders
2. Validate against Kaggle dataset structure
3. Create data transformation pipeline
4. Implement schema in Neo4j `brazil-kg` database
5. Load sample data for testing
6. Build MCP tools on top of schema

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Maintained By**: Researcher Agent (Hive Mind swarm-1761784111350-vc2pgfssn)
**Status**: ✅ Research Phase Complete
