# Test Execution Guide - brazil-bench-hive

Quick reference for running the BDD test suite.

## Prerequisites

```bash
# 1. Install test dependencies
pip install -r tests/requirements.txt

# 2. Ensure Neo4j is running
docker ps | grep neo4j-brazil

# 3. Set environment variables (optional - uses defaults)
export TEST_NEO4J_URI="bolt://localhost:7687"
export TEST_NEO4J_USER="neo4j"
export TEST_NEO4J_PASSWORD="password"
export TEST_NEO4J_DATABASE="brazil-kg-test"
```

## Quick Test Commands

### Run All Tests
```bash
# Full suite with coverage
pytest

# Verbose output
pytest -v

# With detailed tracebacks
pytest -vv --tb=long
```

### Run by Category
```bash
# Player tests
pytest tests/test_player_tools.py -v

# Team tests
pytest tests/test_team_tools.py -v

# Match tests
pytest tests/test_match_tools.py -v

# Competition tests
pytest tests/test_competition_tools.py -v

# Analysis tests
pytest tests/test_analysis_tools.py -v

# Integration tests only
pytest tests/test_integration.py -v
```

### Run by Marker
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Skip slow tests
pytest -m "not slow"

# Neo4j-dependent tests
pytest -m neo4j

# Specific domain
pytest -m player
pytest -m team
pytest -m match
```

### Run by Pattern
```bash
# All search tests
pytest -k "search"

# All bulk/import tests
pytest -k "bulk or import"

# All performance tests
pytest -k "performance"
```

## Coverage Reports

### Generate Coverage
```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html

# Both
pytest --cov=src --cov-report=term-missing --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Thresholds
```bash
# Fail if coverage < 80%
pytest --cov=src --cov-fail-under=80
```

## Debugging Tests

### Stop on First Failure
```bash
pytest -x
```

### Show Print Statements
```bash
pytest -s
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Show Test Collection
```bash
pytest --collect-only
```

### Show Available Fixtures
```bash
pytest --fixtures
```

## Performance Testing

### Run Only Performance Tests
```bash
pytest -m slow --durations=10
```

### Show Slowest Tests
```bash
pytest --durations=10
```

## Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run in parallel (4 workers)
pytest -n 4
```

## Continuous Integration

### CI Command
```bash
pytest --cov=src --cov-report=xml --cov-fail-under=80 -v
```

### Docker Test Environment
```bash
# Start Neo4j test container
docker run -d \
  --name neo4j-test \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Run tests
pytest

# Cleanup
docker stop neo4j-test && docker rm neo4j-test
```

## Test Output Examples

### Successful Run
```
tests/test_player_tools.py::test_search_for_a_player_by_name PASSED     [10%]
tests/test_player_tools.py::test_add_a_new_player_to_database PASSED    [20%]
...
==================== 150 passed in 45.23s ====================
```

### With Coverage
```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/player_tools.py        45      2    96%   34-35
src/team_tools.py          38      1    97%   67
src/match_tools.py         52      3    94%   89-91
-----------------------------------------------------
TOTAL                     135      6    96%
```

## Troubleshooting

### Database Connection Issues
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Test connection
docker exec neo4j-brazil cypher-shell -u neo4j -p password

# Restart Neo4j
docker restart neo4j-brazil
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r tests/requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Fixture Not Found
```bash
# Verify conftest.py location
ls tests/conftest.py

# List available fixtures
pytest --fixtures | grep neo4j
```

### Test Isolation Issues
```bash
# Run tests with fresh database
pytest --cleandb

# Run single test in isolation
pytest tests/test_player_tools.py::test_search_for_a_player_by_name -v
```

## Best Practices

1. **Always run tests before committing**
   ```bash
   pytest --cov=src --cov-fail-under=80
   ```

2. **Write tests alongside code**
   - Feature file first (BDD)
   - Implement steps
   - Run tests iteratively

3. **Keep tests fast**
   - Use markers for slow tests
   - Mock external dependencies
   - Clean database between tests

4. **Use descriptive names**
   - Gherkin scenarios should read like documentation
   - Test functions should be self-explanatory

5. **Maintain test data**
   - Use fixtures for reusable data
   - Keep test data realistic
   - Clean up after tests

## Quick Reference Card

```bash
# Most Common Commands
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -m unit                  # Unit tests only
pytest -k "search"              # Pattern matching
pytest --lf                     # Last failed
pytest -x                       # Stop on failure
pytest --cov=src               # With coverage
pytest tests/test_player_tools.py  # Single file

# Coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Debugging
pytest -s -vv --tb=long

# Performance
pytest -m slow --durations=10
```

## Test Metrics

Current test suite:
- **150+** BDD scenarios
- **500+** step definitions
- **50+** integration tests
- **20+** E2E workflows
- **10+** performance benchmarks

Expected execution time: **<60 seconds**

---

For detailed information, see `/tests/README.md`
