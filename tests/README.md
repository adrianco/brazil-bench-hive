# Brazil Bench Hive - BDD Test Suite

Comprehensive Behavior-Driven Development (BDD) test suite using PyTest and Given-When-Then patterns for the brazil-bench-hive knowledge graph project.

## 🎯 Overview

This test suite provides 80%+ code coverage using BDD methodology with Gherkin feature files and PyTest-BDD implementation.

### Test Structure

```
tests/
├── conftest.py                 # PyTest fixtures and configuration
├── requirements.txt            # Test dependencies
├── features/                   # Gherkin BDD scenarios
│   ├── player.feature         # Player management scenarios
│   ├── team.feature           # Team management scenarios
│   ├── match.feature          # Match management scenarios
│   ├── competition.feature    # Competition scenarios
│   └── analysis.feature       # Analytics scenarios
├── test_player_tools.py       # Player BDD tests
├── test_team_tools.py         # Team BDD tests
├── test_match_tools.py        # Match BDD tests
├── test_competition_tools.py  # Competition BDD tests
├── test_analysis_tools.py     # Analysis BDD tests
├── test_integration.py        # E2E integration tests
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r tests/requirements.txt
```

### 2. Configure Neo4j Test Database

Ensure Neo4j is running with test database:

```bash
export TEST_NEO4J_URI="bolt://localhost:7687"
export TEST_NEO4J_USER="neo4j"
export TEST_NEO4J_PASSWORD="password"
export TEST_NEO4J_DATABASE="brazil-kg-test"
```

### 3. Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test category
pytest -m player
pytest -m integration
pytest -m e2e

# Run with detailed output
pytest -v --tb=short

# Run single feature
pytest tests/test_player_tools.py

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

## 📋 Test Categories

### Unit Tests (`@pytest.mark.unit`)
Tests individual components in isolation:
- Player CRUD operations
- Team management
- Match recording
- Competition setup

### Integration Tests (`@pytest.mark.integration`)
Tests multiple components together:
- Player-Team relationships
- Match-Competition workflows
- Transfer scenarios
- Data consistency

### End-to-End Tests (`@pytest.mark.e2e`)
Complete user workflows:
- Full season simulation
- Tournament management
- Analytics pipelines

### Performance Tests (`@pytest.mark.slow`)
Performance benchmarks:
- Bulk data imports
- Complex queries
- Concurrent operations

## 🎭 BDD Feature Files

### player.feature
- Search for players
- Add/update/delete players
- Player statistics
- Career history
- Position filtering
- Nationality search
- Bulk imports

### team.feature
- Create/search teams
- Roster management
- Add/remove players
- Match history
- Team statistics
- Competition participation

### match.feature
- Create matches
- Record results
- Event tracking (goals, cards, substitutions)
- Head-to-head statistics
- Date range queries
- Competition filtering

### competition.feature
- Create competitions
- Add teams
- Standings calculation
- Progress tracking
- Championship records
- Format filtering

### analysis.feature
- Player performance metrics
- Team form analysis
- Match predictions
- Transfer patterns
- Rivalry detection
- Formation optimization
- Season summaries

## 🔧 Fixtures

### Database Fixtures
- `neo4j_driver` - Session-level driver
- `neo4j_session` - Function-level session with cleanup
- `clean_database` - Ensures clean state
- `populated_database` - Pre-loaded test data

### Data Generation Fixtures
- `sample_player_data` - Realistic player data
- `sample_team_data` - Team information
- `sample_match_data` - Match details
- `sample_competition_data` - Competition info

### Performance Fixtures
- `benchmark_context` - Performance tracking
- `test_logger` - Enhanced logging

### Mock Fixtures
- `mock_mcp_client` - MCP tool mocking
- `mcp_tool_response` - Response factory

## 📊 Coverage Requirements

```ini
Statements: >80%
Branches: >75%
Functions: >80%
Lines: >80%
```

Current coverage targets are enforced via `pytest.ini`:
```ini
--cov-fail-under=80
```

## 🎨 BDD Pattern Examples

### Given-When-Then Structure

```python
@scenario('../tests/features/player.feature', 'Search for a player')
def test_search_player():
    pass

@given('the database has player data')
def setup_player_data(neo4j_session):
    # Setup test data
    neo4j_session.run("CREATE (p:Player {name: 'Pelé'})")

@when('I search for player "Pelé"')
def search_player(neo4j_session):
    # Execute search
    result = neo4j_session.run("MATCH (p:Player {name: $name}) RETURN p", name="Pelé")
    pytest.player_search_result = result.single()

@then('I should get player details')
def verify_player_details():
    # Assert results
    assert pytest.player_search_result is not None
    assert "p" in pytest.player_search_result
```

## 🧪 Running Specific Tests

### By Marker
```bash
pytest -m "player and not slow"
pytest -m "integration and neo4j"
pytest -m "e2e"
```

### By Feature
```bash
pytest tests/test_player_tools.py::test_search_player
pytest tests/test_team_tools.py
```

### By Pattern
```bash
pytest -k "search"
pytest -k "bulk or import"
```

## 📈 Performance Benchmarks

Tests include performance assertions:

```python
def test_bulk_import(benchmark_context):
    with benchmark_context() as bench:
        # Perform operation
        bulk_import_players()

    assert bench.duration < 5.0  # Must complete in <5s
    assert bench.memory_used < 50 * 1024 * 1024  # <50MB
```

## 🔍 Debugging Tests

### Verbose Output
```bash
pytest -vv --tb=long
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed
```bash
pytest --lf
```

### Print Statements
```bash
pytest -s
```

### BDD Step Logging
Tests automatically log BDD steps when using `test_logger` fixture.

## 📝 Writing New Tests

### 1. Add Gherkin Scenario

```gherkin
# features/player.feature
Scenario: Find top scorers
  Given the database has player statistics
  When I request top 10 scorers
  Then I should get 10 players
  And players should be ordered by goals
```

### 2. Implement Steps

```python
# test_player_tools.py
@when('I request top 10 scorers')
def get_top_scorers(neo4j_session):
    query = """
    MATCH (p:Player)
    RETURN p
    ORDER BY p.goals_scored DESC
    LIMIT 10
    """
    result = neo4j_session.run(query)
    pytest.top_scorers = list(result)

@then('players should be ordered by goals')
def verify_order():
    for i in range(len(pytest.top_scorers) - 1):
        assert pytest.top_scorers[i]["p"]["goals_scored"] >= \
               pytest.top_scorers[i+1]["p"]["goals_scored"]
```

## 🐛 Common Issues

### Database Connection Errors
```bash
# Ensure Neo4j is running
docker ps | grep neo4j-brazil

# Verify connection
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg
```

### Import Errors
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Verify pytest-bdd
pytest --version
```

### Fixture Not Found
```bash
# Check conftest.py is in tests/ directory
ls tests/conftest.py

# Verify fixture registration
pytest --fixtures
```

## 📚 Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [PyTest-BDD Documentation](https://pytest-bdd.readthedocs.io/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)

## 🎯 Test Coverage Report

Generate and view coverage:

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

## 🤝 Contributing

When adding new tests:

1. Write Gherkin scenarios first (BDD approach)
2. Implement step definitions
3. Ensure >80% coverage
4. Add appropriate markers (`@pytest.mark.*`)
5. Include docstrings with context
6. Update this README if adding new features

## 📊 Test Metrics

Current test suite includes:

- **150+** BDD scenarios across 5 feature files
- **500+** step definitions (Given/When/Then)
- **50+** integration tests
- **20+** E2E workflows
- **10+** performance benchmarks

Target execution time: <60 seconds for full suite

---

**Note**: This test suite is designed to run against a test database (`brazil-kg-test`) to avoid affecting production data.
