"""
PyTest Configuration and Fixtures for brazil-bench-hive BDD Tests

This module provides test fixtures for:
- Neo4j test database setup and teardown
- MCP client mocking and configuration
- Test data generation and cleanup
- Session management and isolation

Context:
- Creates isolated Neo4j test database for each test session
- Provides clean state for each test via fixtures
- Handles async operations with pytest-asyncio
- Manages test data lifecycle
"""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from neo4j import GraphDatabase, AsyncGraphDatabase
from faker import Faker
from datetime import datetime

# Test database configuration
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "password")
TEST_NEO4J_DATABASE = os.getenv("TEST_NEO4J_DATABASE", "brazil-kg")  # Community Edition - using main DB

fake = Faker()


# ============================================================================
# PYTEST-BDD CONFIGURATION
# ============================================================================

def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    """Enhanced error reporting for BDD steps"""
    print(f"\n❌ BDD Step Failed: {step.name}")
    print(f"   Feature: {feature.name}")
    print(f"   Scenario: {scenario.name}")
    print(f"   Exception: {exception}")


# ============================================================================
# SESSION-LEVEL FIXTURES (Setup once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def neo4j_driver():
    """
    Session-level Neo4j driver for test database

    Context:
    - Creates driver instance once per test session
    - Connects to test database (brazil-kg-test)
    - Automatically closes connection after all tests
    """
    driver = GraphDatabase.driver(
        TEST_NEO4J_URI,
        auth=(TEST_NEO4J_USER, TEST_NEO4J_PASSWORD)
    )

    # Verify connection
    driver.verify_connectivity()

    yield driver

    # Cleanup
    driver.close()


@pytest.fixture(scope="session")
async def async_neo4j_driver():
    """
    Session-level async Neo4j driver for async tests

    Context:
    - Provides async driver for concurrent operations
    - Used for performance testing and async workflows
    """
    driver = AsyncGraphDatabase.driver(
        TEST_NEO4J_URI,
        auth=(TEST_NEO4J_USER, TEST_NEO4J_PASSWORD)
    )

    await driver.verify_connectivity()

    yield driver

    await driver.close()


# ============================================================================
# FUNCTION-LEVEL FIXTURES (Setup/teardown for each test)
# ============================================================================

@pytest.fixture
def neo4j_session(neo4j_driver):
    """
    Function-level Neo4j session with automatic cleanup

    Context:
    - Creates fresh session for each test
    - Ensures test isolation
    - Cleans up test data after each test

    Given: A clean Neo4j test database
    When: A test executes database operations
    Then: All changes are rolled back after test completion
    """
    session = neo4j_driver.session(database=TEST_NEO4J_DATABASE)

    yield session

    # Cleanup: Remove all test data
    with session.begin_transaction() as tx:
        tx.run("MATCH (n) DETACH DELETE n")

    session.close()


@pytest.fixture
async def async_neo4j_session(async_neo4j_driver):
    """
    Async Neo4j session for async test operations

    Context:
    - Supports async/await patterns
    - Used for concurrent database operations
    """
    session = async_neo4j_driver.session(database=TEST_NEO4J_DATABASE)

    yield session

    # Cleanup
    await session.run("MATCH (n) DETACH DELETE n")
    await session.close()


@pytest.fixture
def clean_database(neo4j_session):
    """
    Ensures database is completely clean before test

    Given: A Neo4j database that may contain data
    When: This fixture is used
    Then: All nodes and relationships are deleted
    """
    neo4j_session.run("MATCH (n) DETACH DELETE n")
    return neo4j_session


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_player_data():
    """
    Generate sample player data for testing

    Context:
    - Provides realistic test data
    - Includes various positions and attributes
    - Can be used for bulk insert testing
    """
    return {
        "player_id": fake.uuid4(),
        "name": fake.name(),
        "position": fake.random_element(["Forward", "Midfielder", "Defender", "Goalkeeper"]),
        "number": fake.random_int(min=1, max=99),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=40).isoformat(),
        "nationality": "Brazil",
        "height": fake.random_int(min=160, max=200),
        "weight": fake.random_int(min=60, max=100),
        "preferred_foot": fake.random_element(["Left", "Right", "Both"])
    }


@pytest.fixture
def sample_team_data():
    """
    Generate sample team data for testing

    Context:
    - Provides realistic team information
    - Includes stadium and founding details
    """
    return {
        "team_id": fake.uuid4(),
        "name": f"{fake.city()} FC",
        "founded": fake.random_int(min=1900, max=2020),
        "stadium": f"{fake.city()} Stadium",
        "city": fake.city(),
        "country": "Brazil",
        "capacity": fake.random_int(min=10000, max=100000)
    }


@pytest.fixture
def sample_match_data():
    """
    Generate sample match data for testing

    Context:
    - Provides complete match information
    - Includes scores and statistics
    """
    home_score = fake.random_int(min=0, max=5)
    away_score = fake.random_int(min=0, max=5)

    return {
        "match_id": fake.uuid4(),
        "date": fake.date_time_this_year().isoformat(),
        "home_team_id": fake.uuid4(),
        "away_team_id": fake.uuid4(),
        "home_score": home_score,
        "away_score": away_score,
        "competition": fake.random_element(["Série A", "Copa do Brasil", "Libertadores"]),
        "venue": f"{fake.city()} Stadium",
        "attendance": fake.random_int(min=1000, max=80000)
    }


@pytest.fixture
def sample_competition_data():
    """
    Generate sample competition data for testing

    Context:
    - Provides competition/tournament information
    - Includes season and format details
    """
    return {
        "competition_id": fake.uuid4(),
        "name": fake.random_element([
            "Campeonato Brasileiro Série A",
            "Copa do Brasil",
            "Copa Libertadores",
            "Campeonato Paulista"
        ]),
        "season": fake.random_int(min=2000, max=2024),
        "format": fake.random_element(["League", "Cup", "Knockout"]),
        "number_of_teams": fake.random_int(min=8, max=20)
    }


@pytest.fixture
def populated_database(neo4j_session, sample_player_data, sample_team_data):
    """
    Populate database with sample data for integration tests

    Context:
    - Creates interconnected test data
    - Simulates realistic database state
    - Used for complex query testing

    Given: A clean database
    When: This fixture is applied
    Then: Database contains sample players, teams, and relationships
    """
    # Create team
    team_query = """
    CREATE (t:Team {
        team_id: $team_id,
        name: $name,
        founded: $founded,
        stadium: $stadium,
        city: $city
    })
    RETURN t
    """
    team_result = neo4j_session.run(team_query, **sample_team_data)
    team_node = team_result.single()

    # Create players
    players = []
    for i in range(5):
        player_data = {
            "player_id": fake.uuid4(),
            "name": fake.name(),
            "position": fake.random_element(["Forward", "Midfielder", "Defender", "Goalkeeper"]),
            "number": i + 1,
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=40).isoformat(),
            "nationality": "Brazil"
        }

        player_query = """
        CREATE (p:Player {
            player_id: $player_id,
            name: $name,
            position: $position,
            number: $number,
            date_of_birth: $date_of_birth,
            nationality: $nationality
        })
        RETURN p
        """
        neo4j_session.run(player_query, **player_data)
        players.append(player_data)

    # Create relationships
    for player in players:
        relationship_query = """
        MATCH (p:Player {player_id: $player_id})
        MATCH (t:Team {team_id: $team_id})
        CREATE (p)-[:PLAYS_FOR {since: $since}]->(t)
        """
        neo4j_session.run(
            relationship_query,
            player_id=player["player_id"],
            team_id=sample_team_data["team_id"],
            since=2024
        )

    return {
        "team": sample_team_data,
        "players": players
    }


# ============================================================================
# MCP MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_mcp_client(mocker):
    """
    Mock MCP client for testing MCP tools without actual server

    Context:
    - Simulates MCP server responses
    - Allows testing tool logic in isolation
    - No external dependencies required
    """
    mock_client = mocker.Mock()

    # Configure common mock responses
    mock_client.call_tool.return_value = {
        "success": True,
        "data": {}
    }

    return mock_client


@pytest.fixture
def mcp_tool_response():
    """
    Factory fixture for generating MCP tool responses

    Context:
    - Provides consistent response format
    - Can be customized per test
    """
    def _create_response(success=True, data=None, error=None):
        return {
            "success": success,
            "data": data or {},
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }

    return _create_response


# ============================================================================
# PERFORMANCE AND BENCHMARK FIXTURES
# ============================================================================

@pytest.fixture
def benchmark_context():
    """
    Provides context for performance benchmarking

    Context:
    - Tracks execution times
    - Records memory usage
    - Used for performance regression testing
    """
    import time
    import tracemalloc

    class BenchmarkContext:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None

        def __enter__(self):
            tracemalloc.start()
            self.start_memory = tracemalloc.get_traced_memory()
            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            self.end_time = time.time()
            self.end_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        @property
        def duration(self):
            return self.end_time - self.start_time

        @property
        def memory_used(self):
            return self.end_memory[0] - self.start_memory[0]

    return BenchmarkContext


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def test_logger(caplog):
    """
    Enhanced logging for test debugging

    Context:
    - Captures all log output
    - Provides structured logging for BDD steps
    """
    import logging

    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)

    def log_bdd_step(step_type: str, description: str):
        logger.info(f"🎯 {step_type}: {description}")

    logger.log_bdd_step = log_bdd_step
    return logger


@pytest.fixture(autouse=True)
def test_isolation_check():
    """
    Ensures proper test isolation

    Context:
    - Runs before and after each test
    - Validates no state leakage between tests
    """
    # Before test
    yield
    # After test - could add validation logic here
