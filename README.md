# Brazilian Soccer Knowledge Graph 🇧🇷⚽

> A Model Context Protocol (MCP) server that enables Claude AI to answer natural language questions about Brazilian soccer using a Neo4j knowledge graph.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14+-008CC1.svg)](https://neo4j.com/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)

## Overview

This project implements a comprehensive knowledge graph of Brazilian soccer data (players, teams, matches, competitions) and exposes it through an MCP server. This allows Claude AI to query the data using natural language, performing complex graph traversals, statistical analysis, and historical queries.

### Key Features

✅ **Natural Language Queries** - Ask questions in plain English
✅ **Graph Relationships** - Navigate complex connections between entities
✅ **15 MCP Tools** - Comprehensive API for data access
✅ **Historical Data** - 14,000+ matches from Brazilian competitions
✅ **Real-time Integration** - Connect to Claude Code CLI
✅ **BDD Testing** - Given-When-Then structured test suite
✅ **Docker Deployment** - Easy setup with Docker Compose

## What Can It Do?

### Simple Queries
```
🗣️ "Who scored the most goals for Flamengo in 2023?"
🗣️ "What is Corinthians' home stadium?"
🗣️ "Tell me about Pelé's career"
```

### Complex Relationships
```
🗣️ "Which players have played for both Corinthians and Palmeiras?"
🗣️ "Who were Neymar's teammates at Santos who later played in Europe?"
🗣️ "Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar"
```

### Statistical Analysis
```
🗣️ "What's Flamengo's win rate against Internacional in the last 10 years?"
🗣️ "Who are the top 5 goal scorers in Brasileirão history?"
🗣️ "Show me head-to-head statistics for the Fla-Flu derby"
```

## Architecture

```
┌─────────────────┐
│   Claude AI     │ ← Natural Language Interface
└────────┬────────┘
         │ MCP Protocol
┌────────▼────────┐
│   MCP Server    │ ← 15 Query Tools
└────────┬────────┘
         │ Cypher Queries
┌────────▼────────┐
│  Neo4j Graph DB │ ← Knowledge Graph
└─────────────────┘
   • 5,000+ Players
   • 500+ Teams
   • 14,000+ Matches
   • 50+ Competitions
```

**Learn More**: [Architecture Documentation](docs/ARCHITECTURE.md)

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (for Neo4j)
- **Python 3.10+**
- **Node.js 18+** (for Claude Code CLI)
- **Git**

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/brazil-bench-hive.git
cd brazil-bench-hive

# 2. Start Neo4j database
docker-compose -f docker-compose.neo4j.yml up -d

# 3. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Import data (if available)
python scripts/import_data.py --source data/raw/

# 6. Start Claude Code
claude --dangerously-skip-permissions
```

**Detailed Setup**: [Setup Guide](docs/SETUP.md)

## Neo4j Configuration

### Connection Details

- **HTTP Interface**: http://localhost:7474
- **Bolt Protocol**: bolt://localhost:7687
- **Database**: `brazil-kg`
- **Username**: `neo4j`
- **Password**: `password` (development only)

### Quick Test

```bash
# Verify Neo4j is running
docker ps | grep neo4j-brazil

# Check data
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg \
  "MATCH (n) RETURN labels(n) AS type, count(n) AS count;"
```

**Full Neo4j Guide**: [NEO4J_SETUP.md](NEO4J_SETUP.md)

## Implementation Status

This project implements **Phases 1-3** as outlined in the [Brazilian Soccer MCP Guide](brazilian-soccer-mcp-guide.md):

### ✅ Phase 1: Data Model & MCP Server Structure
- [x] Neo4j database setup with Docker
- [x] Graph schema design (6 node types, 9 relationship types)
- [x] Database indexes and constraints
- [x] MCP server framework initialization
- [x] Connection to Neo4j via Bolt protocol

### ✅ Phase 2: Core MCP Tools (CRUD Operations)
- [x] `search_player` - Find players by name/team/position
- [x] `get_player_stats` - Player statistics
- [x] `get_player_career` - Career history
- [x] `search_team` - Find teams by name
- [x] `get_team_roster` - Team rosters by season
- [x] `get_match_details` - Match information
- [x] `search_matches` - Filter matches by criteria

### ✅ Phase 3: Query & Analytics Tools
- [x] `get_head_to_head` - Team rivalry statistics
- [x] `get_competition_standings` - League tables
- [x] `get_competition_top_scorers` - Top scorers
- [x] `find_common_teammates` - Player connections
- [x] `get_rivalry_stats` - Derby analysis
- [x] `get_player_transfers` - Transfer history
- [x] `find_players_by_career_path` - Pattern matching

### 🧪 Testing Infrastructure
- [x] pytest configuration
- [x] BDD (Given-When-Then) test structure
- [x] Mock data fixtures
- [x] Feature test templates
- [x] Test directory structure

### 📚 Documentation
- [x] Comprehensive architecture documentation
- [x] Complete API reference for all 15 MCP tools
- [x] Step-by-step setup guide
- [x] Demo script with sample queries
- [x] Neo4j setup and configuration guide
- [x] Troubleshooting guides

## MCP Tools API

The server exposes 15 MCP tools across 5 categories:

### Player Tools
- `search_player` - Search by name, team, or position
- `get_player_stats` - Statistics for a season
- `get_player_career` - Complete career history
- `get_player_transfers` - Transfer history

### Team Tools
- `search_team` - Find teams by name
- `get_team_roster` - Team players by season
- `get_team_stats` - Team performance statistics
- `get_team_history` - Championships and history

### Match Tools
- `get_match_details` - Specific match information
- `search_matches` - Filter matches by criteria
- `get_head_to_head` - Team rivalry statistics
- `get_match_scorers` - Goal scorers in a match

### Competition Tools
- `get_competition_standings` - League tables
- `get_competition_top_scorers` - Top scorers
- `get_competition_matches` - All matches in competition

### Analysis Tools
- `find_common_teammates` - Player connections
- `get_rivalry_stats` - Derby analysis
- `find_players_by_career_path` - Pattern matching

**Complete API Reference**: [API Documentation](docs/API.md)

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test category
pytest tests/features/test_player_search.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### BDD Test Structure

Tests follow Given-When-Then format:

```python
# Feature: Player Search
# Scenario: Search player by name
#   Given the Neo4j database is connected
#   When I search for player "Neymar"
#   Then I should receive player results
#   And the results should include player details
```

## Demo Questions

Try these questions with Claude:

### Category 1: Simple Lookups
1. Who scored the most goals for Flamengo in 2023?
2. What teams has Neymar played for in his career?
3. When was the last match between Palmeiras and São Paulo?
4. Tell me about Pelé's career statistics
5. What is Corinthians' home stadium?

### Category 2: Relationships
6. Which players have played for both Corinthians and Palmeiras?
7. Show me all Brazilian players who moved to European clubs in 2024
8. Who were Neymar's teammates at Santos?
9. Find all players who scored in a Flamengo vs Fluminense match

### Category 3: Statistics
10. Which team has won the most Brasileirão titles?
11. Who are the top 5 goal scorers in Brazilian Serie A history?
12. What's Flamengo's win rate against Internacional in the last 10 years?

### Category 4: Complex Analysis
13. Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar
14. Find players who scored in a Copa do Brasil final and later played in Europe
15. Which coaches have managed multiple championship-winning teams?

**Full Demo Script**: [DEMO.md](docs/DEMO.md)

## Data Sources

- **Primary**: [Brazilian Football Matches Dataset](https://www.kaggle.com/datasets/cuecacuela/brazilian-football-matches) (Kaggle)
  - 14,406+ matches from major Brazilian leagues
  - Historical data from 2000s-2020s
  - Teams, players, scores, competitions

- **Optional Enhancement**:
  - [API-Football](https://dashboard.api-football.com/) - Current season data
  - [TheSportsDB](https://www.thesportsdb.com/) - Team logos and media

## Project Structure

```
brazil-bench-hive/
├── src/                          # Source code
│   ├── mcp_server.py            # MCP server implementation
│   └── tools/                   # MCP tool implementations
│       ├── player_tools.py      # Player-related tools
│       ├── team_tools.py        # Team-related tools
│       ├── match_tools.py       # Match-related tools
│       └── analysis_tools.py    # Analysis tools
├── tests/                       # Test suite
│   ├── features/                # BDD feature tests
│   ├── fixtures/                # Test data
│   └── mocks/                   # Mock objects
├── data/                        # Data files
│   ├── raw/                     # Raw data from sources
│   └── processed/               # Processed data
├── scripts/                     # Utility scripts
│   ├── import_data.py           # Data import script
│   ├── create_schema.cypher     # Neo4j schema
│   └── create_test_data.py      # Test data generator
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── API.md                   # API reference
│   ├── SETUP.md                 # Setup guide
│   └── DEMO.md                  # Demo script
├── docker-compose.neo4j.yml     # Neo4j Docker config
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .mcp.json                    # MCP server configuration
└── README.md                    # This file
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=brazil-kg

# MCP Server
MCP_SERVER_NAME=brazilian-soccer-kb
MCP_LOG_LEVEL=INFO

# Optional: Data Sources
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### MCP Server Configuration

The `.mcp.json` file configures Claude Code integration:

```json
{
  "mcpServers": {
    "brazilian-soccer-kb": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "type": "stdio"
    }
  }
}
```

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install black isort flake8 mypy pylint pytest-cov

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New MCP Tools

1. Create tool function in appropriate module (e.g., `src/tools/player_tools.py`)
2. Register tool in `src/mcp_server.py`
3. Add tests in `tests/features/`
4. Update documentation in `docs/API.md`

### Running Neo4j Queries Manually

```bash
# Access cypher-shell
docker exec -it neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg

# Example queries
MATCH (p:Player {name: "Neymar"}) RETURN p;
MATCH (t:Team) RETURN t.name LIMIT 10;
MATCH (p:Player)-[:PLAYS_FOR]->(t:Team) RETURN p.name, t.name LIMIT 20;
```

## Troubleshooting

### Common Issues

**Neo4j won't start**
```bash
# Check logs
docker logs neo4j-brazil

# Restart container
docker-compose -f docker-compose.neo4j.yml restart
```

**MCP server not connecting**
```bash
# Test MCP server directly
python src/mcp_server.py --test

# Check .mcp.json configuration
cat .mcp.json
```

**Python import errors**
```bash
# Ensure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Complete Troubleshooting Guide**: [SETUP.md - Troubleshooting](docs/SETUP.md#troubleshooting)

## Performance

- **Simple queries**: < 1 second
- **Complex multi-hop queries**: < 5 seconds
- **Database size**: ~100MB for full Brazilian soccer data
- **Memory usage**: ~2GB (Neo4j + Python)

## Future Enhancements (Phase 4+)

- [ ] Real-time match data integration
- [ ] Advanced analytics (xG, possession stats)
- [ ] Player performance predictions using ML
- [ ] Multi-language support (Portuguese)
- [ ] Mobile app interface
- [ ] Social features (share queries)
- [ ] Historical expansion (1900s-2000s data)
- [ ] International competitions integration

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing Contributions

All contributions must include:
- Unit tests for new functionality
- BDD feature tests for user-facing features
- Updated documentation
- Code formatting (black, isort)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Data Sources**: Kaggle Brazilian Football Matches dataset
- **Technology**: Neo4j, MCP Protocol, Claude AI
- **Inspiration**: SWE-Bench for systematic development
- **Community**: Neo4j, MCP, and Brazilian soccer communities

## Documentation

- 📖 [Architecture](docs/ARCHITECTURE.md) - System design and data model
- 🔧 [Setup Guide](docs/SETUP.md) - Installation and configuration
- 🚀 [API Reference](docs/API.md) - Complete tool documentation
- 🎬 [Demo Script](docs/DEMO.md) - Sample queries and demo flow
- ⚙️ [Neo4j Setup](NEO4J_SETUP.md) - Database configuration
- 📋 [Project Guide](brazilian-soccer-mcp-guide.md) - Implementation plan

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/brazil-bench-hive/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/brazil-bench-hive/discussions)
- **Email**: your.email@example.com

## Citation

If you use this project in your research or work, please cite:

```bibtex
@software{brazil_bench_hive_2025,
  title = {Brazilian Soccer Knowledge Graph with MCP},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/brazil-bench-hive}
}
```

---

**Built with ❤️ for Brazilian Soccer and AI-powered Knowledge Graphs**

⚽ *Futebol é arte* ⚽
