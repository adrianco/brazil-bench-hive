# Brazilian Soccer MCP Server - Documentation

## Overview

This MCP server provides access to a comprehensive Brazilian Soccer Knowledge Graph, enabling natural language queries about players, teams, matches, and competitions.

## Architecture

```
src/
├── server.py              # Main MCP server implementation
├── config.py              # Configuration management
├── database.py            # Neo4j connection manager
├── models.py              # Pydantic data models
└── tools/                 # MCP tool implementations
    ├── player_tools.py    # Player queries
    ├── team_tools.py      # Team queries
    ├── match_tools.py     # Match queries
    ├── competition_tools.py  # Competition queries
    └── analysis_tools.py  # Advanced analytics
```

## Installation

### Prerequisites

- Python 3.9+
- Neo4j database (running in Docker or locally)
- pip or poetry for dependency management

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd brazil-bench-hive
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

4. **Start Neo4j database**
   ```bash
   docker-compose -f docker-compose.neo4j.yml up -d
   ```

5. **Verify Neo4j connection**
   ```bash
   # Access Neo4j browser at http://localhost:7474
   # Login with credentials from .env file
   ```

## Usage

### Running the Server

```bash
# Run directly
python -m src.server

# Or via MCP CLI
mcp run src/server.py
```

### Configuration

All configuration is managed via environment variables. See `.env.example` for available options.

Key settings:
- `NEO4J_URI`: Database connection URI
- `NEO4J_USER`: Database username
- `NEO4J_PASSWORD`: Database password
- `NEO4J_DATABASE`: Database name (default: brazil-kg)
- `NEO4J_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Available Tools

### Player Tools

1. **search_player**
   - Find players by name, team, or position
   - Parameters: `name`, `team` (optional), `position` (optional), `limit` (default: 10)

2. **get_player_stats**
   - Get comprehensive player statistics
   - Parameters: `player_id`, `season` (optional)

3. **get_player_career**
   - Get complete career history
   - Parameters: `player_id`

4. **get_player_transfers**
   - List all player transfers
   - Parameters: `player_id`, `year` (optional)

### Team Tools

1. **search_team**
   - Find teams by name or city
   - Parameters: `name`, `city` (optional), `limit` (default: 10)

2. **get_team_roster**
   - Get team roster for a season
   - Parameters: `team_id`, `season` (optional)

3. **get_team_stats**
   - Get team statistics
   - Parameters: `team_id`, `season` (optional)

4. **get_team_history**
   - Get complete team history
   - Parameters: `team_id`, `include_championships` (default: True)

### Match Tools

1. **get_match_details**
   - Get detailed match information
   - Parameters: `match_id`

2. **search_matches**
   - Search for matches
   - Parameters: `team` (optional), `date_from` (optional), `date_to` (optional), `competition` (optional), `limit` (default: 20)

3. **get_head_to_head**
   - Compare two teams' historical matchups
   - Parameters: `team1_id`, `team2_id`, `limit` (optional)

4. **get_match_scorers**
   - List goal scorers in a match
   - Parameters: `match_id`

### Competition Tools

1. **get_competition_standings**
   - Get league standings/table
   - Parameters: `competition_id`, `season`

2. **get_competition_top_scorers**
   - List top goal scorers
   - Parameters: `competition_id`, `season`, `limit` (default: 20)

3. **get_competition_matches**
   - Get all matches in a competition
   - Parameters: `competition_id`, `season`, `team` (optional), `round` (optional)

### Analysis Tools

1. **find_common_teammates**
   - Find players who were teammates with both specified players
   - Parameters: `player1_id`, `player2_id`

2. **get_rivalry_stats**
   - Get comprehensive rivalry statistics
   - Parameters: `team1_id`, `team2_id`, `years` (optional)

3. **find_players_by_career_path**
   - Find players matching complex career criteria
   - Parameters: `criteria` (dict with keys: teams, min_teams, positions, min_goals, etc.)

## Example Queries

### Simple Lookups
```
"Find player named Neymar"
→ Uses search_player tool

"Get statistics for player P12345"
→ Uses get_player_stats tool

"Show me Flamengo's roster"
→ Uses search_team then get_team_roster
```

### Relationship Queries
```
"Which players have played for both Corinthians and Palmeiras?"
→ Uses find_players_by_career_path tool

"Who were Neymar's teammates at Santos?"
→ Uses get_player_career then find_common_teammates
```

### Statistical Analysis
```
"What's Flamengo's win rate against Internacional?"
→ Uses search_team then get_head_to_head

"Show me the Brasileirão 2023 standings"
→ Uses get_competition_standings
```

## Database Schema

### Node Types
- **Player**: Soccer players with personal information
- **Team**: Soccer clubs and their details
- **Match**: Individual soccer matches
- **Competition**: Leagues and tournaments
- **Stadium**: Soccer venues
- **Coach**: Team managers

### Relationships
- `PLAYS_FOR`: Player → Team (with dates)
- `SCORED_IN`: Player → Match (with minute, goal type)
- `ASSISTED_IN`: Player → Match
- `COMPETED_IN`: Team → Match (home/away)
- `PART_OF`: Match → Competition
- `PLAYED_AT`: Match → Stadium
- `TRANSFERRED_FROM/TO`: Player → Team
- `MANAGES`: Coach → Team

## Development

### Project Structure

```
brazil-bench-hive/
├── src/                   # Source code
│   ├── server.py          # Main MCP server
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection
│   ├── models.py          # Data models
│   └── tools/             # MCP tools
├── docs/                  # Documentation
├── tests/                 # Unit tests (future)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── docker-compose.neo4j.yml  # Neo4j setup
```

### Adding New Tools

1. Create tool function in appropriate `tools/*.py` file
2. Add `@server.call_tool()` decorator in `server.py`
3. Implement Cypher queries for data retrieval
4. Add proper error handling and logging
5. Document the tool in this README

### Testing

```bash
# Run tests (when available)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Code formatting
black src/
ruff check src/
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Neo4j
**Solution**:
- Verify Neo4j container is running: `docker ps | grep neo4j`
- Check connection details in `.env` file
- Ensure ports 7474 and 7687 are not blocked

### Query Performance

**Problem**: Slow query responses
**Solution**:
- Check database indexes are created
- Limit result sets with `limit` parameter
- Consider adding caching (future enhancement)

### Data Issues

**Problem**: Incomplete or missing data
**Solution**:
- Verify data import was successful
- Check Neo4j browser for data: http://localhost:7474
- Run database health check (built into server startup)

## Contributing

1. Follow Python coding standards (PEP 8)
2. Add docstrings to all functions
3. Include context blocks in file headers
4. Test thoroughly before committing
5. Update documentation with new features

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Review the implementation guide: `brazilian-soccer-mcp-guide.md`
- Check Neo4j setup: `NEO4J_SETUP.md`
