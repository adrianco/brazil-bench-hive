# Brazilian Soccer Knowledge Graph - Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Neo4j Setup](#neo4j-setup)
- [MCP Server Configuration](#mcp-server-configuration)
- [Data Import](#data-import)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Development Environment](#development-environment)

---

## Prerequisites

### Required Software

#### 1. Docker & Docker Compose
- **Version**: Docker 20.10+ and Docker Compose 2.0+
- **Installation**:
  - **macOS**: Download [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - **Windows**: Download [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - **Linux**:
    ```bash
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh

    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

#### 2. Python
- **Version**: Python 3.10 or higher
- **Installation**:
  ```bash
  # Check Python version
  python3 --version

  # macOS (using Homebrew)
  brew install python@3.10

  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.10 python3-pip python3-venv

  # Windows
  # Download from https://www.python.org/downloads/
  ```

#### 3. Git
- **Version**: Git 2.30+
- **Installation**:
  ```bash
  # Check Git version
  git --version

  # macOS
  brew install git

  # Ubuntu/Debian
  sudo apt install git

  # Windows
  # Download from https://git-scm.com/download/win
  ```

#### 4. Node.js (for Claude Code CLI)
- **Version**: Node.js 18+
- **Installation**:
  ```bash
  # macOS
  brew install node

  # Ubuntu/Debian
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs

  # Windows
  # Download from https://nodejs.org/
  ```

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/brazil-bench-hive.git
cd brazil-bench-hive
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Expected packages:
# - mcp (Model Context Protocol)
# - neo4j (Neo4j Python Driver)
# - pytest (Testing framework)
# - pytest-bdd (BDD testing)
# - python-dotenv (Environment variables)
```

**Note**: If `requirements.txt` doesn't exist yet, create it with:
```txt
mcp>=0.1.0
neo4j>=5.14.0
pytest>=7.4.0
pytest-bdd>=6.1.0
python-dotenv>=1.0.0
pandas>=2.0.0
```

### Step 4: Install Claude Code CLI

```bash
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

### Step 5: Install Claude Flow

```bash
# Initialize Claude Flow
npx claude-flow@alpha init --force

# Verify installation
npx claude-flow@alpha --version
```

---

## Neo4j Setup

### Option 1: Using Docker Compose (Recommended)

#### Start Neo4j
```bash
# Start Neo4j container
docker-compose -f docker-compose.neo4j.yml up -d

# Wait for Neo4j to start (15-30 seconds)
# Check logs
docker-compose -f docker-compose.neo4j.yml logs -f
```

#### Verify Neo4j is Running
```bash
# Check container status
docker ps | grep neo4j-brazil

# Expected output:
# CONTAINER ID   IMAGE          STATUS          PORTS
# xxxxxxxxxxxx   neo4j:latest   Up 2 minutes    0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
```

#### Access Neo4j Browser
1. Open browser: http://localhost:7474
2. Login credentials:
   - **Username**: `neo4j`
   - **Password**: `password`
   - **Database**: `brazil-kg`

### Option 2: Using Docker Commands

```bash
# Create Neo4j container
docker run -d \
  --name neo4j-brazil \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_dbms_default__database=brazil-kg \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:latest
```

### Neo4j Configuration

#### Connection Details
- **HTTP Interface**: http://localhost:7474
- **Bolt Protocol**: bolt://localhost:7687
- **Username**: `neo4j`
- **Password**: `password`
- **Database**: `brazil-kg`

#### Test Connection
```bash
# Test connection using cypher-shell
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg "MATCH (n) RETURN count(n) AS node_count;"

# Expected output:
# +------------+
# | node_count |
# +------------+
# | 0          |
# +------------+
```

### Create Database Schema

```bash
# Run schema creation script
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg < scripts/create_schema.cypher

# Or manually via Neo4j Browser:
# 1. Open http://localhost:7474
# 2. Copy and paste commands from scripts/create_schema.cypher
# 3. Execute each command
```

**Schema Commands** (scripts/create_schema.cypher):
```cypher
// Create indexes for fast lookups
CREATE INDEX player_name IF NOT EXISTS FOR (p:Player) ON (p.name);
CREATE INDEX player_id IF NOT EXISTS FOR (p:Player) ON (p.player_id);
CREATE INDEX team_name IF NOT EXISTS FOR (t:Team) ON (t.name);
CREATE INDEX team_id IF NOT EXISTS FOR (t:Team) ON (t.team_id);
CREATE INDEX match_date IF NOT EXISTS FOR (m:Match) ON (m.date);
CREATE INDEX match_id IF NOT EXISTS FOR (m:Match) ON (m.match_id);
CREATE INDEX competition_season IF NOT EXISTS FOR (c:Competition) ON (c.season);

// Create constraints
CREATE CONSTRAINT player_unique IF NOT EXISTS FOR (p:Player) REQUIRE p.player_id IS UNIQUE;
CREATE CONSTRAINT team_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.team_id IS UNIQUE;
CREATE CONSTRAINT match_unique IF NOT EXISTS FOR (m:Match) REQUIRE m.match_id IS UNIQUE;
CREATE CONSTRAINT competition_unique IF NOT EXISTS FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE;
```

---

## MCP Server Configuration

### Step 1: Create Environment File

```bash
# Create .env file
cat > .env << EOF
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=brazil-kg

# MCP Server Configuration
MCP_SERVER_NAME=brazilian-soccer-kb
MCP_LOG_LEVEL=INFO

# Data Sources
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key

# Optional: API Keys for data enhancement
API_FOOTBALL_KEY=your_api_key
THESPORTSDB_KEY=123
EOF
```

### Step 2: Configure Claude Code

```bash
# Create .mcp.json configuration
cat > .mcp.json << EOF
{
  "mcpServers": {
    "brazilian-soccer-kb": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "type": "stdio",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "NEO4J_DATABASE": "brazil-kg"
      }
    }
  }
}
EOF
```

### Step 3: Test MCP Server

```bash
# Test MCP server directly
python src/mcp_server.py --test

# Expected output:
# ✓ MCP Server initialized
# ✓ Neo4j connection established
# ✓ Tools registered: 15
# ✓ Ready to accept requests
```

---

## Data Import

### Step 1: Download Data Sources

#### Kaggle Dataset (Recommended)
```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle API
mkdir -p ~/.kaggle
# Place your kaggle.json in ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download Brazilian Football Matches dataset
kaggle datasets download -d cuecacuela/brazilian-football-matches
unzip brazilian-football-matches.zip -d data/raw/
```

#### Manual Download
1. Visit: https://www.kaggle.com/datasets/cuecacuela/brazilian-football-matches
2. Click "Download" (requires Kaggle account)
3. Extract to `data/raw/` directory

### Step 2: Process and Import Data

```bash
# Run data import script
python scripts/import_data.py --source data/raw/ --batch-size 1000

# Expected output:
# Processing teams... ✓ 500 teams imported
# Processing players... ✓ 5,000 players imported
# Processing matches... ✓ 14,406 matches imported
# Processing competitions... ✓ 50 competitions imported
# Creating relationships... ✓ 50,000 relationships created
# Import complete! Total time: 2m 35s
```

### Step 3: Verify Data Import

```bash
# Check data in Neo4j
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg "
MATCH (n)
RETURN labels(n) AS type, count(n) AS count
ORDER BY count DESC;
"

# Expected output:
# +-------------------+-------+
# | type              | count |
# +-------------------+-------+
# | [\"Match\"]        | 14406 |
# | [\"Player\"]       | 5000  |
# | [\"Team\"]         | 500   |
# | [\"Competition\"]  | 50    |
# +-------------------+-------+
```

---

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_mcp_tools.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Run BDD Tests

```bash
# Run BDD (Given-When-Then) tests
pytest tests/features/

# Run specific feature
pytest tests/features/test_player_search.py

# Expected output:
# tests/features/test_player_search.py::test_search_player_by_name PASSED
# tests/features/test_player_search.py::test_search_player_by_team PASSED
# tests/features/test_player_search.py::test_player_not_found PASSED
```

### Test MCP Tools with Claude

```bash
# Start Claude Code CLI
claude --dangerously-skip-permissions

# Test queries in Claude:
# > "Search for players named Neymar"
# > "Show me Flamengo's roster"
# > "What's the head-to-head between Flamengo and Fluminense?"
```

---

## Troubleshooting

### Issue: Neo4j Container Won't Start

**Symptoms**: Container exits immediately or logs show errors

**Solutions**:
```bash
# Check logs
docker logs neo4j-brazil

# Common fixes:
# 1. Port already in use
docker ps -a | grep 7474  # Check if another Neo4j is running
docker stop <container_id>

# 2. Permission issues
docker volume rm neo4j_data neo4j_logs
docker-compose -f docker-compose.neo4j.yml up -d

# 3. Insufficient memory
# Increase Docker memory limit in Docker Desktop settings
# Recommended: 4GB minimum
```

### Issue: Cannot Connect to Neo4j

**Symptoms**: "Connection refused" or "Authentication failed"

**Solutions**:
```bash
# 1. Verify Neo4j is running
docker ps | grep neo4j-brazil

# 2. Test connection
curl http://localhost:7474

# 3. Check credentials
docker exec neo4j-brazil cypher-shell -u neo4j -p password

# 4. Reset password
docker exec neo4j-brazil cypher-shell -u neo4j -p neo4j
# Then run: ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'password';
```

### Issue: Python Import Errors

**Symptoms**: ModuleNotFoundError when running scripts

**Solutions**:
```bash
# 1. Verify virtual environment is activated
which python  # Should show path to venv/bin/python

# 2. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 3. Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: MCP Server Not Found by Claude

**Symptoms**: Claude doesn't see MCP tools

**Solutions**:
```bash
# 1. Verify .mcp.json exists
cat .mcp.json

# 2. Test MCP server manually
python src/mcp_server.py --test

# 3. Check Claude Code configuration
claude mcp list

# 4. Restart Claude Code
# Exit Claude and restart
```

### Issue: Data Import Fails

**Symptoms**: Import script errors or incomplete data

**Solutions**:
```bash
# 1. Check data file format
head -n 5 data/raw/matches.csv

# 2. Clear existing data
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg "MATCH (n) DETACH DELETE n;"

# 3. Run import with debug mode
python scripts/import_data.py --debug --source data/raw/

# 4. Import smaller batch
python scripts/import_data.py --batch-size 100 --limit 1000
```

### Issue: Tests Failing

**Symptoms**: pytest shows failures

**Solutions**:
```bash
# 1. Ensure Neo4j has test data
python scripts/create_test_data.py

# 2. Check environment variables
cat .env

# 3. Run single test with verbose output
pytest tests/test_player_search.py::test_search_by_name -v -s

# 4. Clear pytest cache
pytest --cache-clear
```

---

## Development Environment

### Recommended IDE Setup

#### VS Code
```bash
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension neo4j.cypher
code --install-extension ms-python.vscode-pylance

# Open project
code .
```

#### PyCharm
1. Open PyCharm
2. File → Open → Select brazil-bench-hive directory
3. Configure Python interpreter: Preferences → Project → Python Interpreter → Add → Existing environment → Select `venv/bin/python`

### Environment Variables

Create `.env.development` for development settings:
```bash
# Development settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=brazil-kg
MCP_LOG_LEVEL=DEBUG
ENABLE_QUERY_LOGGING=true
CACHE_ENABLED=false
```

### Debugging

#### Debug MCP Server
```bash
# Run with debug logging
python src/mcp_server.py --log-level DEBUG

# Or use Python debugger
python -m pdb src/mcp_server.py
```

#### Debug Neo4j Queries
```cypher
// In Neo4j Browser, explain query execution plan
EXPLAIN
MATCH (p:Player {name: "Neymar"})-[:PLAYS_FOR]->(t:Team)
RETURN p, t;

// Profile query performance
PROFILE
MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
RETURN t.name, count(p) AS player_count
ORDER BY player_count DESC
LIMIT 10;
```

### Code Quality Tools

```bash
# Install development dependencies
pip install black isort flake8 mypy pylint

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

---

## Next Steps

After completing setup:

1. **Read the Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Explore the API**: [API.md](./API.md)
3. **Try the Demo**: [DEMO.md](./DEMO.md)
4. **Read Project Guide**: [brazilian-soccer-mcp-guide.md](../brazilian-soccer-mcp-guide.md)

---

## Additional Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: `docker logs neo4j-brazil` and MCP server logs
2. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/brazil-bench-hive/issues)
3. **Create a new issue**: Include logs, error messages, and steps to reproduce
4. **Ask in discussions**: [GitHub Discussions](https://github.com/yourusername/brazil-bench-hive/discussions)

---

## Quick Reference

### Common Commands

```bash
# Neo4j
docker-compose -f docker-compose.neo4j.yml up -d     # Start Neo4j
docker-compose -f docker-compose.neo4j.yml down      # Stop Neo4j
docker logs neo4j-brazil -f                          # View logs

# Python
source venv/bin/activate                             # Activate venv
pip install -r requirements.txt                      # Install deps
python src/mcp_server.py                             # Run server

# Testing
pytest                                               # Run all tests
pytest -v                                            # Verbose output
pytest --cov=src                                     # With coverage

# Claude Code
claude                                               # Start Claude
claude mcp list                                      # List MCP servers
```

### Project Structure
```
brazil-bench-hive/
├── src/                    # Source code
│   ├── mcp_server.py       # MCP server main
│   └── tools/              # MCP tool implementations
├── tests/                  # Test files
│   ├── features/           # BDD tests
│   └── test_*.py           # Unit tests
├── data/                   # Data files
│   ├── raw/                # Raw data
│   └── processed/          # Processed data
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── docker-compose.neo4j.yml # Neo4j configuration
```

---

**Setup Complete!** You're now ready to start querying Brazilian soccer data with Claude AI.
