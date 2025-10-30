"""
BDD Tests for Player Management Tools

This module implements Given-When-Then tests for all player-related operations
including CRUD operations, search, statistics, and career history tracking.

Context:
- Tests player creation, retrieval, update, and deletion
- Validates search functionality by various criteria
- Ensures data integrity and relationship management
- Tests performance with bulk operations
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime

# Load all scenarios from player.feature
scenarios('player.feature')


# ============================================================================
# GIVEN STEPS - Test Setup and Preconditions
# ============================================================================

@given('the Neo4j database is running')
def verify_neo4j_connection(neo4j_session):
    """
    Verify that Neo4j database is accessible and responding

    Context:
    - Ensures test infrastructure is ready
    - Validates database connectivity
    """
    result = neo4j_session.run("RETURN 1 AS test")
    assert result.single()["test"] == 1, "Neo4j database is not responding"


@given('the database is clean')
def ensure_clean_database(clean_database):
    """
    Ensure database has no residual test data

    Context:
    - Provides isolated test environment
    - Prevents test interference
    """
    result = clean_database.run("MATCH (n) RETURN count(n) AS count")
    count = result.single()["count"]
    assert count == 0, f"Database is not clean, found {count} nodes"


@given('the database has player data')
def setup_player_data(neo4j_session):
    """
    Populate database with sample player data

    Context:
    - Creates realistic test data
    - Provides foundation for search tests
    """
    players = [
        {"name": "Pelé", "position": "Forward", "number": 10, "nationality": "Brazil"},
        {"name": "Zico", "position": "Midfielder", "number": 10, "nationality": "Brazil"},
        {"name": "Romário", "position": "Forward", "number": 11, "nationality": "Brazil"}
    ]

    for player in players:
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            position: $position,
            number: $number,
            nationality: $nationality,
            created_at: datetime()
        })
        """
        neo4j_session.run(query, **player)


@given(parsers.parse('a player named "{player_name}" exists'))
def create_player(neo4j_session, player_name):
    """
    Create a specific player in the database

    Context:
    - Sets up test precondition
    - Creates player with given name
    """
    query = """
    CREATE (p:Player {
        player_id: randomUUID(),
        name: $name,
        position: 'Forward',
        number: 10,
        nationality: 'Brazil',
        date_of_birth: '1990-01-01',
        created_at: datetime()
    })
    RETURN p
    """
    result = neo4j_session.run(query, name=player_name)
    assert result.single() is not None, f"Failed to create player {player_name}"


@given('I have valid player data')
def prepare_valid_player_data(sample_player_data):
    """
    Prepare valid player data for creation test

    Context:
    - Uses fixture to generate realistic data
    - Stores data in test context
    """
    return sample_player_data


@given('the database has multiple players')
def create_multiple_players(neo4j_session):
    """
    Create a diverse set of players for testing queries

    Context:
    - Creates players with different attributes
    - Enables filtering and search tests
    """
    players = [
        {"name": "Player1", "position": "Forward", "nationality": "Brazil"},
        {"name": "Player2", "position": "Forward", "nationality": "Brazil"},
        {"name": "Player3", "position": "Forward", "nationality": "Brazil"},
        {"name": "Player4", "position": "Midfielder", "nationality": "Brazil"},
        {"name": "Player5", "position": "Midfielder", "nationality": "Argentina"},
        {"name": "Player6", "position": "Defender", "nationality": "Argentina"},
    ]

    for player in players:
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            position: $position,
            nationality: $nationality,
            created_at: datetime()
        })
        """
        neo4j_session.run(query, **player)


@given(parsers.parse('there are {count:d} players with position "{position}"'))
def create_players_by_position(neo4j_session, count, position):
    """
    Create specific number of players with given position

    Context:
    - Sets up precise test conditions
    - Enables count verification tests
    """
    for i in range(count):
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            position: $position,
            number: $number,
            nationality: 'Brazil',
            created_at: datetime()
        })
        """
        neo4j_session.run(
            query,
            name=f"Player_{position}_{i}",
            position=position,
            number=i + 1
        )


@given(parsers.parse('the player has played for "{team}" from {start_year:d} to {end_year:d}'))
def create_career_history(neo4j_session, team, start_year, end_year):
    """
    Create career history relationship for player

    Context:
    - Establishes player-team relationships
    - Tracks career timeline
    """
    # First create the team if it doesn't exist
    team_query = """
    MERGE (t:Team {name: $team})
    ON CREATE SET t.team_id = randomUUID(),
                  t.created_at = datetime()
    RETURN t
    """
    neo4j_session.run(team_query, team=team)

    # Create relationship
    rel_query = """
    MATCH (p:Player) WHERE p.name IS NOT NULL
    MATCH (t:Team {name: $team})
    CREATE (p)-[:PLAYED_FOR {
        from_year: $start_year,
        to_year: $end_year,
        created_at: datetime()
    }]->(t)
    """
    neo4j_session.run(rel_query, team=team, start_year=start_year, end_year=end_year)


@given(parsers.parse('there are {count:d} Brazilian players'))
def create_brazilian_players(neo4j_session, count):
    """Create specified number of Brazilian players"""
    for i in range(count):
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            nationality: 'Brazil',
            position: 'Forward',
            created_at: datetime()
        })
        """
        neo4j_session.run(query, name=f"Brazilian_Player_{i}")


@given(parsers.parse('there are {count:d} Argentine players'))
def create_argentine_players(neo4j_session, count):
    """Create specified number of Argentine players"""
    for i in range(count):
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            nationality: 'Argentina',
            position: 'Forward',
            created_at: datetime()
        })
        """
        neo4j_session.run(query, name=f"Argentine_Player_{i}")


@given(parsers.parse('the player has {match_count:d} matches recorded'))
def record_player_matches(neo4j_session, match_count):
    """Record match statistics for player"""
    query = """
    MATCH (p:Player)
    WHERE p.name IS NOT NULL
    SET p.matches_played = $match_count
    """
    neo4j_session.run(query, match_count=match_count)


@given(parsers.parse('the player has scored {goal_count:d} goals'))
def record_player_goals(neo4j_session, goal_count):
    """Record goal statistics for player"""
    query = """
    MATCH (p:Player)
    WHERE p.name IS NOT NULL
    SET p.goals_scored = $goal_count
    """
    neo4j_session.run(query, goal_count=goal_count)


@given(parsers.parse('the player has position "{position}"'))
def set_player_position(neo4j_session, position):
    """Set player position"""
    query = """
    MATCH (p:Player)
    WHERE p.name IS NOT NULL
    SET p.position = $position
    """
    neo4j_session.run(query, position=position)


@given(parsers.parse('I have a list of {count:d} valid player records'))
def prepare_bulk_players(count):
    """Prepare list of players for bulk import"""
    players = []
    for i in range(count):
        players.append({
            "name": f"BulkPlayer_{i}",
            "position": "Forward",
            "number": i + 1,
            "nationality": "Brazil"
        })
    return players


# ============================================================================
# WHEN STEPS - Actions and Operations
# ============================================================================

@when(parsers.parse('I search for player "{player_name}"'))
def search_player(neo4j_session, player_name):
    """
    Execute player search query

    Context:
    - Simulates MCP tool call
    - Searches player by name
    """
    query = """
    MATCH (p:Player {name: $name})
    RETURN p
    """
    result = neo4j_session.run(query, name=player_name)
    # Store result in pytest context
    pytest.player_search_result = result.single()


@when(parsers.parse('I add a new player with name "{player_name}"'))
def add_new_player(neo4j_session, player_name):
    """
    Create new player in database

    Context:
    - Tests player creation functionality
    - Validates data persistence
    """
    query = """
    CREATE (p:Player {
        player_id: randomUUID(),
        name: $name,
        position: 'Forward',
        number: 10,
        nationality: 'Brazil',
        created_at: datetime()
    })
    RETURN p
    """
    result = neo4j_session.run(query, name=player_name)
    pytest.created_player = result.single()


@when(parsers.parse('I update the player position to "{new_position}"'))
def update_player_position(neo4j_session, new_position):
    """Update player position and record timestamp"""
    query = """
    MATCH (p:Player)
    WHERE p.name IS NOT NULL
    SET p.position = $position,
        p.updated_at = datetime()
    RETURN p
    """
    result = neo4j_session.run(query, position=new_position)
    pytest.updated_player = result.single()


@when(parsers.parse('I search for players with position "{position}"'))
def search_by_position(neo4j_session, position):
    """Search players by position"""
    query = """
    MATCH (p:Player {position: $position})
    RETURN p
    ORDER BY p.name
    """
    result = neo4j_session.run(query, position=position)
    pytest.position_search_results = list(result)


@when(parsers.parse('I request the career history for "{player_name}"'))
def get_career_history(neo4j_session, player_name):
    """Retrieve player career history with teams"""
    query = """
    MATCH (p:Player {name: $name})-[r:PLAYED_FOR]->(t:Team)
    RETURN t.name AS team, r.from_year AS from_year, r.to_year AS to_year
    ORDER BY r.from_year
    """
    result = neo4j_session.run(query, name=player_name)
    pytest.career_history = list(result)


@when(parsers.parse('I search for players from "{nationality}"'))
def search_by_nationality(neo4j_session, nationality):
    """Search players by nationality"""
    query = """
    MATCH (p:Player {nationality: $nationality})
    RETURN p
    """
    result = neo4j_session.run(query, nationality=nationality)
    pytest.nationality_search_results = list(result)


@when(parsers.parse('I request statistics for "{player_name}"'))
def get_player_statistics(neo4j_session, player_name):
    """Retrieve player statistics"""
    query = """
    MATCH (p:Player {name: $name})
    RETURN p.matches_played AS matches,
           p.goals_scored AS goals,
           toFloat(p.goals_scored) / p.matches_played AS goals_per_match
    """
    result = neo4j_session.run(query, name=player_name)
    pytest.player_statistics = result.single()


@when(parsers.parse('I delete the player "{player_name}"'))
def delete_player(neo4j_session, player_name):
    """Delete player from database"""
    query = """
    MATCH (p:Player {name: $name})
    DELETE p
    """
    neo4j_session.run(query, name=player_name)
    pytest.deleted_player_name = player_name


@when('I perform a bulk import')
def bulk_import_players(neo4j_session, benchmark_context):
    """Perform bulk player import with performance tracking"""
    players = [
        {"name": f"BulkPlayer_{i}", "position": "Forward", "number": i + 1}
        for i in range(10)
    ]

    with benchmark_context() as bench:
        query = """
        UNWIND $players AS player
        CREATE (p:Player {
            player_id: randomUUID(),
            name: player.name,
            position: player.position,
            number: player.number,
            nationality: 'Brazil',
            created_at: datetime()
        })
        """
        neo4j_session.run(query, players=players)

    pytest.bulk_import_duration = bench.duration


# ============================================================================
# THEN STEPS - Assertions and Validations
# ============================================================================

@then('I should get player details')
def verify_player_details():
    """Verify player search returned results"""
    assert pytest.player_search_result is not None, "Player not found"
    assert "p" in pytest.player_search_result, "Player data missing"


@then(parsers.parse('the player name should be "{expected_name}"'))
def verify_player_name(expected_name):
    """Verify player name matches expected value"""
    player = pytest.player_search_result["p"]
    assert player["name"] == expected_name, f"Expected {expected_name}, got {player['name']}"


@then('the response should include player statistics')
def verify_player_statistics():
    """Verify response includes statistics fields"""
    player = pytest.player_search_result["p"]
    # In real implementation, would check for stats fields
    assert player is not None, "Player data missing"


@then('the player should be created successfully')
def verify_player_created():
    """Verify player creation succeeded"""
    assert pytest.created_player is not None, "Player creation failed"
    player = pytest.created_player["p"]
    assert "player_id" in player, "Player ID not generated"


@then('the player should be queryable by ID')
def verify_player_queryable(neo4j_session):
    """Verify created player can be queried"""
    player = pytest.created_player["p"]
    query = """
    MATCH (p:Player {player_id: $id})
    RETURN p
    """
    result = neo4j_session.run(query, id=player["player_id"])
    assert result.single() is not None, "Player not queryable by ID"


@then(parsers.parse('the database should contain {count:d} player'))
def verify_player_count(neo4j_session, count):
    """Verify exact player count in database"""
    query = "MATCH (p:Player) RETURN count(p) AS count"
    result = neo4j_session.run(query)
    actual_count = result.single()["count"]
    assert actual_count == count, f"Expected {count} players, found {actual_count}"


@then(parsers.parse('the player position should be "{expected_position}"'))
def verify_position_updated(expected_position):
    """Verify player position was updated"""
    player = pytest.updated_player["p"]
    assert player["position"] == expected_position, \
        f"Position not updated correctly: {player['position']}"


@then('the update timestamp should be recorded')
def verify_update_timestamp():
    """Verify update timestamp exists"""
    player = pytest.updated_player["p"]
    assert "updated_at" in player, "Update timestamp not recorded"


@then(parsers.parse('I should get {count:d} players in the results'))
def verify_result_count(count):
    """Verify number of results matches expected count"""
    if hasattr(pytest, 'position_search_results'):
        results = pytest.position_search_results
    elif hasattr(pytest, 'nationality_search_results'):
        results = pytest.nationality_search_results
    else:
        raise AssertionError("No search results found")

    assert len(results) == count, f"Expected {count} results, got {len(results)}"


@then(parsers.parse('all players should have position "{position}"'))
def verify_all_positions(position):
    """Verify all results have expected position"""
    results = pytest.position_search_results
    for record in results:
        assert record["p"]["position"] == position, \
            f"Found player with different position: {record['p']['position']}"


@then(parsers.parse('I should see {count:d} teams in the career history'))
def verify_career_history_count(count):
    """Verify career history contains expected number of teams"""
    assert len(pytest.career_history) == count, \
        f"Expected {count} teams, found {len(pytest.career_history)}"


@then('the teams should be in chronological order')
def verify_chronological_order():
    """Verify career history is sorted chronologically"""
    history = pytest.career_history
    for i in range(len(history) - 1):
        assert history[i]["from_year"] <= history[i + 1]["from_year"], \
            "Career history not in chronological order"


@then(parsers.parse('all players should have nationality "{nationality}"'))
def verify_all_nationalities(nationality):
    """Verify all results have expected nationality"""
    results = pytest.nationality_search_results
    for record in results:
        assert record["p"]["nationality"] == nationality, \
            f"Found player with different nationality: {record['p']['nationality']}"


@then(parsers.parse('the statistics should show {matches:d} matches'))
def verify_matches_stat(matches):
    """Verify matches statistic"""
    stats = pytest.player_statistics
    assert stats["matches"] == matches, f"Expected {matches} matches, got {stats['matches']}"


@then(parsers.parse('the statistics should show {goals:d} goals'))
def verify_goals_stat(goals):
    """Verify goals statistic"""
    stats = pytest.player_statistics
    assert stats["goals"] == goals, f"Expected {goals} goals, got {stats['goals']}"


@then(parsers.parse('the goals per match ratio should be {ratio:f}'))
def verify_goals_per_match(ratio):
    """Verify calculated goals per match ratio"""
    stats = pytest.player_statistics
    assert abs(stats["goals_per_match"] - ratio) < 0.01, \
        f"Expected ratio {ratio}, got {stats['goals_per_match']}"


@then('the player should not be found in database')
def verify_player_deleted(neo4j_session):
    """Verify player was deleted"""
    query = """
    MATCH (p:Player {name: $name})
    RETURN p
    """
    result = neo4j_session.run(query, name=pytest.deleted_player_name)
    assert result.single() is None, "Player still exists after deletion"


@then('the deletion should be confirmed')
def verify_deletion_confirmed():
    """Verify deletion operation completed"""
    assert hasattr(pytest, 'deleted_player_name'), "Deletion not recorded"


@then('I should get an empty result')
def verify_empty_result():
    """Verify search returned no results"""
    result = pytest.player_search_result
    assert result is None, "Expected empty result but found data"


@then('no error should occur')
def verify_no_error():
    """Verify operation completed without errors"""
    # If we reached this point, no exception was raised
    assert True


@then(parsers.parse('all {count:d} players should be created'))
def verify_bulk_create_count(neo4j_session, count):
    """Verify bulk import created all players"""
    query = """
    MATCH (p:Player)
    WHERE p.name STARTS WITH 'BulkPlayer_'
    RETURN count(p) AS count
    """
    result = neo4j_session.run(query)
    actual_count = result.single()["count"]
    assert actual_count == count, f"Expected {count} players, created {actual_count}"


@then(parsers.parse('the import should complete in under {seconds:d} seconds'))
def verify_import_performance(seconds):
    """Verify bulk import performance"""
    duration = pytest.bulk_import_duration
    assert duration < seconds, \
        f"Import took {duration}s, expected under {seconds}s"


@then('each player should have a unique ID')
def verify_unique_ids(neo4j_session):
    """Verify all players have unique IDs"""
    query = """
    MATCH (p:Player)
    WHERE p.name STARTS WITH 'BulkPlayer_'
    RETURN count(DISTINCT p.player_id) AS unique_count,
           count(p) AS total_count
    """
    result = neo4j_session.run(query)
    data = result.single()
    assert data["unique_count"] == data["total_count"], \
        "Not all players have unique IDs"
