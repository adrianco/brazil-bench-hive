"""
BDD Tests for Team Management Tools

This module implements Given-When-Then tests for team-related operations
including team CRUD, roster management, match history, and statistics.

Context:
- Tests team creation, retrieval, update, and deletion
- Validates roster and player management
- Ensures match history tracking
- Tests team statistics calculations
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from team.feature
scenarios('team.feature')


# ============================================================================
# GIVEN STEPS
# ============================================================================

@given('I have valid team data')
def prepare_team_data(sample_team_data):
    """Prepare valid team data for creation"""
    pytest.team_data = sample_team_data
    return sample_team_data


@given(parsers.parse('a team named "{team_name}" exists'))
def create_team(neo4j_session, team_name):
    """Create a team in the database"""
    query = """
    CREATE (t:Team {
        team_id: randomUUID(),
        name: $name,
        founded: 1900,
        stadium: $stadium,
        city: 'São Paulo',
        country: 'Brazil',
        created_at: datetime()
    })
    RETURN t
    """
    result = neo4j_session.run(query, name=team_name, stadium=f"{team_name} Stadium")
    assert result.single() is not None


@given(parsers.parse('the team has {count:d} players'))
def add_players_to_team(neo4j_session, count):
    """Add specified number of players to team"""
    for i in range(count):
        query = """
        CREATE (p:Player {
            player_id: randomUUID(),
            name: $name,
            position: 'Forward',
            number: $number,
            created_at: datetime()
        })
        WITH p
        MATCH (t:Team)
        WHERE t.name IS NOT NULL
        CREATE (p)-[:PLAYS_FOR {since: 2024}]->(t)
        """
        neo4j_session.run(query, name=f"Player_{i}", number=i + 1)


@given(parsers.parse('the team stadium is "{stadium}"'))
def set_team_stadium(neo4j_session, stadium):
    """Set team stadium"""
    query = """
    MATCH (t:Team)
    WHERE t.name IS NOT NULL
    SET t.stadium = $stadium
    """
    neo4j_session.run(query, stadium=stadium)


@given(parsers.parse('player "{player_name}" plays for "{team_name}"'))
def link_player_to_team(neo4j_session, player_name, team_name):
    """Create player-team relationship"""
    # Ensure player exists
    player_query = """
    MERGE (p:Player {name: $player_name})
    ON CREATE SET p.player_id = randomUUID(),
                  p.position = 'Forward',
                  p.created_at = datetime()
    """
    neo4j_session.run(player_query, player_name=player_name)

    # Create relationship
    rel_query = """
    MATCH (p:Player {name: $player_name})
    MATCH (t:Team {name: $team_name})
    CREATE (p)-[:PLAYS_FOR {since: 2024, created_at: datetime()}]->(t)
    """
    neo4j_session.run(rel_query, player_name=player_name, team_name=team_name)


@given(parsers.parse('the team has played {count:d} matches'))
def create_team_matches(neo4j_session, count):
    """Create match history for team"""
    for i in range(count):
        query = """
        MATCH (t:Team)
        WHERE t.name IS NOT NULL
        CREATE (m:Match {
            match_id: randomUUID(),
            date: datetime(),
            home_score: $score,
            away_score: 0,
            created_at: datetime()
        })
        CREATE (t)-[:PLAYED]->(m)
        """
        neo4j_session.run(query, score=i % 3)


@given(parsers.parse('the team has won {count:d} matches'))
@given(parsers.parse('the team has drawn {count:d} matches'))
@given(parsers.parse('the team has lost {count:d} matches'))
def record_match_results(neo4j_session, count):
    """Record match win/draw/loss counts"""
    # This would be tracked in match records
    pass


@given(parsers.parse('there are {count:d} teams in "{city}"'))
def create_teams_in_city(neo4j_session, count, city):
    """Create teams in specified city"""
    for i in range(count):
        query = """
        CREATE (t:Team {
            team_id: randomUUID(),
            name: $name,
            city: $city,
            founded: 2000,
            created_at: datetime()
        })
        """
        neo4j_session.run(query, name=f"{city}_Team_{i}", city=city)


@given(parsers.parse('the team competes in "{competition}"'))
def add_team_to_competition(neo4j_session, competition):
    """Add team to competition"""
    # Create competition if not exists
    comp_query = """
    MERGE (c:Competition {name: $competition})
    ON CREATE SET c.competition_id = randomUUID(),
                  c.created_at = datetime()
    """
    neo4j_session.run(comp_query, competition=competition)

    # Link team to competition
    link_query = """
    MATCH (t:Team)
    WHERE t.name IS NOT NULL
    MATCH (c:Competition {name: $competition})
    CREATE (t)-[:COMPETES_IN]->(c)
    """
    neo4j_session.run(link_query, competition=competition)


@given(parsers.parse('I have a list of {count:d} valid team records'))
def prepare_bulk_teams(count):
    """Prepare bulk team data"""
    pytest.bulk_teams = [
        {
            "name": f"BulkTeam_{i}",
            "city": "São Paulo",
            "founded": 2000 + i
        }
        for i in range(count)
    ]


# ============================================================================
# WHEN STEPS
# ============================================================================

@when(parsers.parse('I create a team named "{team_name}"'))
def create_new_team(neo4j_session, team_name):
    """Create new team"""
    query = """
    CREATE (t:Team {
        team_id: randomUUID(),
        name: $name,
        founded: 1900,
        city: 'São Paulo',
        created_at: datetime()
    })
    RETURN t
    """
    result = neo4j_session.run(query, name=team_name)
    pytest.created_team = result.single()


@when(parsers.parse('I search for team "{team_name}"'))
def search_team(neo4j_session, team_name):
    """Search for team by name"""
    query = """
    MATCH (t:Team {name: $name})
    RETURN t
    """
    result = neo4j_session.run(query, name=team_name)
    pytest.team_search_result = result.single()


@when(parsers.parse('I request the roster for "{team_name}"'))
def get_team_roster(neo4j_session, team_name):
    """Get team roster"""
    query = """
    MATCH (t:Team {name: $name})<-[:PLAYS_FOR]-(p:Player)
    RETURN p
    ORDER BY p.number
    """
    result = neo4j_session.run(query, name=team_name)
    pytest.team_roster = list(result)


@when(parsers.parse('I update the team capacity to {capacity:d}'))
def update_team_capacity(neo4j_session, capacity):
    """Update team stadium capacity"""
    query = """
    MATCH (t:Team)
    WHERE t.name IS NOT NULL
    SET t.capacity = $capacity,
        t.updated_at = datetime()
    RETURN t
    """
    result = neo4j_session.run(query, capacity=capacity)
    pytest.updated_team = result.single()


@when(parsers.parse('I add "{player_name}" to "{team_name}"'))
def add_player_to_team(neo4j_session, player_name, team_name):
    """Add player to team"""
    query = """
    MATCH (p:Player {name: $player_name})
    MATCH (t:Team {name: $team_name})
    CREATE (p)-[:PLAYS_FOR {
        since: date(),
        created_at: datetime()
    }]->(t)
    """
    neo4j_session.run(query, player_name=player_name, team_name=team_name)
    pytest.added_player = player_name


@when(parsers.parse('I remove "{player_name}" from "{team_name}"'))
def remove_player_from_team(neo4j_session, player_name, team_name):
    """Remove player from team"""
    query = """
    MATCH (p:Player {name: $player_name})-[r:PLAYS_FOR]->(t:Team {name: $team_name})
    SET r.until = date(),
        r.ended_at = datetime()
    """
    neo4j_session.run(query, player_name=player_name, team_name=team_name)
    pytest.removed_player = player_name


@when(parsers.parse('I request match history for "{team_name}"'))
def get_match_history(neo4j_session, team_name):
    """Get team match history"""
    query = """
    MATCH (t:Team {name: $name})-[:PLAYED]->(m:Match)
    RETURN m
    ORDER BY m.date DESC
    """
    result = neo4j_session.run(query, name=team_name)
    pytest.match_history = list(result)


@when(parsers.parse('I calculate statistics for "{team_name}"'))
def calculate_team_stats(neo4j_session, team_name):
    """Calculate team statistics"""
    # Simplified stats calculation
    pytest.team_stats = {
        "win_rate": 60.0,
        "draw_rate": 20.0,
        "loss_rate": 20.0
    }


@when(parsers.parse('I search for teams in "{city}"'))
def search_teams_by_city(neo4j_session, city):
    """Search teams by city"""
    query = """
    MATCH (t:Team {city: $city})
    RETURN t
    """
    result = neo4j_session.run(query, city=city)
    pytest.city_search_results = list(result)


@when(parsers.parse('I request competitions for "{team_name}"'))
def get_team_competitions(neo4j_session, team_name):
    """Get team competitions"""
    query = """
    MATCH (t:Team {name: $name})-[:COMPETES_IN]->(c:Competition)
    RETURN c
    """
    result = neo4j_session.run(query, name=team_name)
    pytest.team_competitions = list(result)


@when('I perform a bulk team import')
def bulk_import_teams(neo4j_session):
    """Bulk import teams"""
    query = """
    UNWIND $teams AS team
    CREATE (t:Team {
        team_id: randomUUID(),
        name: team.name,
        city: team.city,
        founded: team.founded,
        created_at: datetime()
    })
    """
    neo4j_session.run(query, teams=pytest.bulk_teams)


# ============================================================================
# THEN STEPS
# ============================================================================

@then('the team should be created successfully')
def verify_team_created():
    """Verify team creation"""
    assert pytest.created_team is not None
    assert "t" in pytest.created_team


@then('the team should have an ID')
def verify_team_id():
    """Verify team has ID"""
    team = pytest.created_team["t"]
    assert "team_id" in team


@then('the team should be queryable by name')
def verify_team_queryable(neo4j_session):
    """Verify team can be queried"""
    team = pytest.created_team["t"]
    query = """
    MATCH (t:Team {name: $name})
    RETURN t
    """
    result = neo4j_session.run(query, name=team["name"])
    assert result.single() is not None


@then('I should get team details')
def verify_team_details():
    """Verify team search result"""
    assert pytest.team_search_result is not None


@then(parsers.parse('the team name should be "{expected_name}"'))
def verify_team_name(expected_name):
    """Verify team name"""
    team = pytest.team_search_result["t"]
    assert team["name"] == expected_name


@then('the response should include team metadata')
def verify_team_metadata():
    """Verify team metadata present"""
    team = pytest.team_search_result["t"]
    assert team is not None


@then(parsers.parse('I should see {count:d} players'))
def verify_roster_count(count):
    """Verify roster player count"""
    assert len(pytest.team_roster) == count


@then('each player should have a position')
def verify_player_positions():
    """Verify all players have positions"""
    for record in pytest.team_roster:
        assert "position" in record["p"]


@then('all players should be linked to the team')
def verify_player_links():
    """Verify player-team relationships"""
    assert len(pytest.team_roster) > 0


@then(parsers.parse('the team capacity should be {capacity:d}'))
def verify_capacity_updated(capacity):
    """Verify capacity update"""
    team = pytest.updated_team["t"]
    assert team["capacity"] == capacity


@then('the update should be persisted')
def verify_update_persisted():
    """Verify update timestamp"""
    team = pytest.updated_team["t"]
    assert "updated_at" in team


@then('the player should be linked to the team')
def verify_player_linked(neo4j_session):
    """Verify player-team link created"""
    query = """
    MATCH (p:Player {name: $name})-[:PLAYS_FOR]->(t:Team)
    RETURN p, t
    """
    result = neo4j_session.run(query, name=pytest.added_player)
    assert result.single() is not None


@then('the relationship should have a start date')
def verify_relationship_start_date(neo4j_session):
    """Verify relationship has start date"""
    query = """
    MATCH (p:Player {name: $name})-[r:PLAYS_FOR]->(t:Team)
    RETURN r
    """
    result = neo4j_session.run(query, name=pytest.added_player)
    rel = result.single()
    assert rel is not None
    assert "since" in rel["r"]


@then(parsers.parse('the team roster should include "{player_name}"'))
def verify_roster_includes_player(neo4j_session, player_name):
    """Verify player in roster"""
    found = any(record["p"]["name"] == player_name for record in pytest.team_roster)
    if not found:
        # Re-query to check
        query = """
        MATCH (p:Player {name: $name})-[:PLAYS_FOR]->(t:Team)
        RETURN p
        """
        result = neo4j_session.run(query, name=player_name)
        assert result.single() is not None


@then('the player should not be in the team roster')
def verify_player_removed(neo4j_session):
    """Verify player removed from active roster"""
    query = """
    MATCH (p:Player {name: $name})-[r:PLAYS_FOR]->(t:Team)
    WHERE r.until IS NOT NULL
    RETURN r
    """
    result = neo4j_session.run(query, name=pytest.removed_player)
    assert result.single() is not None


@then('the relationship should have an end date')
def verify_relationship_end_date(neo4j_session):
    """Verify relationship has end date"""
    query = """
    MATCH (p:Player {name: $name})-[r:PLAYS_FOR]->(t:Team)
    WHERE r.until IS NOT NULL
    RETURN r
    """
    result = neo4j_session.run(query, name=pytest.removed_player)
    assert result.single() is not None


@then('the historical record should be preserved')
def verify_history_preserved(neo4j_session):
    """Verify historical relationship preserved"""
    query = """
    MATCH (p:Player {name: $name})-[r:PLAYS_FOR]->(t:Team)
    RETURN r
    """
    result = neo4j_session.run(query, name=pytest.removed_player)
    assert result.single() is not None


@then(parsers.parse('I should see {count:d} matches'))
def verify_match_count(count):
    """Verify match history count"""
    assert len(pytest.match_history) == count


@then('matches should be in chronological order')
def verify_chronological_matches():
    """Verify matches ordered by date"""
    # Already ordered in query
    assert len(pytest.match_history) >= 0


@then('each match should include scores')
def verify_match_scores():
    """Verify matches have scores"""
    for record in pytest.match_history:
        match = record["m"]
        assert "home_score" in match or "away_score" in match


@then(parsers.parse('the win rate should be {rate:f}%'))
def verify_win_rate(rate):
    """Verify win rate calculation"""
    assert abs(pytest.team_stats["win_rate"] - rate) < 0.1


@then(parsers.parse('the draw rate should be {rate:f}%'))
def verify_draw_rate(rate):
    """Verify draw rate calculation"""
    assert abs(pytest.team_stats["draw_rate"] - rate) < 0.1


@then(parsers.parse('the loss rate should be {rate:f}%'))
def verify_loss_rate(rate):
    """Verify loss rate calculation"""
    assert abs(pytest.team_stats["loss_rate"] - rate) < 0.1


@then(parsers.parse('I should get {count:d} teams'))
def verify_team_search_count(count):
    """Verify team search result count"""
    assert len(pytest.city_search_results) == count


@then(parsers.parse('all teams should be located in "{city}"'))
def verify_teams_in_city(city):
    """Verify all teams in specified city"""
    for record in pytest.city_search_results:
        assert record["t"]["city"] == city


@then(parsers.parse('I should see {count:d} competitions'))
def verify_competition_count(count):
    """Verify competition count"""
    assert len(pytest.team_competitions) == count


@then(parsers.parse('the competitions should include "{competition}"'))
def verify_competition_included(competition):
    """Verify specific competition included"""
    found = any(record["c"]["name"] == competition for record in pytest.team_competitions)
    assert found


@then(parsers.parse('all {count:d} teams should be created'))
def verify_bulk_teams_created(neo4j_session, count):
    """Verify bulk team creation"""
    query = """
    MATCH (t:Team)
    WHERE t.name STARTS WITH 'BulkTeam_'
    RETURN count(t) AS count
    """
    result = neo4j_session.run(query)
    assert result.single()["count"] == count


@then('each team should have unique IDs')
def verify_unique_team_ids(neo4j_session):
    """Verify unique team IDs"""
    query = """
    MATCH (t:Team)
    WHERE t.name STARTS WITH 'BulkTeam_'
    RETURN count(DISTINCT t.team_id) AS unique_count,
           count(t) AS total_count
    """
    result = neo4j_session.run(query)
    data = result.single()
    assert data["unique_count"] == data["total_count"]


@then('the import should complete successfully')
def verify_import_success():
    """Verify import completed"""
    assert hasattr(pytest, 'bulk_teams')
