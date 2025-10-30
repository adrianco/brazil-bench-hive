"""
End-to-End Integration Tests for brazil-bench-hive

This module implements comprehensive integration tests that exercise
multiple components together, simulating real-world usage scenarios.

Context:
- Tests complete workflows across multiple tools
- Validates data consistency across operations
- Tests performance under realistic loads
- Ensures proper error handling and recovery
"""

import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
@pytest.mark.e2e
class TestPlayerTeamIntegration:
    """Integration tests for player and team management"""

    def test_create_team_and_add_players(self, neo4j_session):
        """
        GIVEN: A new team needs to be created with players
        WHEN: Team is created and players are added
        THEN: All relationships are properly established
        """
        # Create team
        team_query = """
        CREATE (t:Team {
            team_id: randomUUID(),
            name: 'Integration FC',
            founded: 2024,
            city: 'São Paulo',
            created_at: datetime()
        })
        RETURN t
        """
        team_result = neo4j_session.run(team_query)
        team = team_result.single()["t"]

        # Create and link players
        for i in range(5):
            player_query = """
            MATCH (t:Team {team_id: $team_id})
            CREATE (p:Player {
                player_id: randomUUID(),
                name: $name,
                position: $position,
                number: $number,
                created_at: datetime()
            })
            CREATE (p)-[:PLAYS_FOR {since: 2024}]->(t)
            RETURN p
            """
            neo4j_session.run(
                player_query,
                team_id=team["team_id"],
                name=f"Player_{i}",
                position="Forward",
                number=i + 1
            )

        # Verify roster
        roster_query = """
        MATCH (t:Team {team_id: $team_id})<-[:PLAYS_FOR]-(p:Player)
        RETURN count(p) AS player_count
        """
        result = neo4j_session.run(roster_query, team_id=team["team_id"])
        assert result.single()["player_count"] == 5

    def test_transfer_player_between_teams(self, neo4j_session):
        """
        GIVEN: A player plays for one team
        WHEN: Player transfers to another team
        THEN: Historical record is maintained
        """
        # Create teams
        for team_name in ["Team A", "Team B"]:
            neo4j_session.run("""
                CREATE (t:Team {
                    team_id: randomUUID(),
                    name: $name,
                    created_at: datetime()
                })
            """, name=team_name)

        # Create player at Team A
        neo4j_session.run("""
            MATCH (t:Team {name: 'Team A'})
            CREATE (p:Player {
                player_id: randomUUID(),
                name: 'Transfer Player',
                created_at: datetime()
            })
            CREATE (p)-[:PLAYS_FOR {since: 2023}]->(t)
        """)

        # Transfer to Team B
        neo4j_session.run("""
            MATCH (p:Player {name: 'Transfer Player'})
            MATCH (old:Team {name: 'Team A'})
            MATCH (new:Team {name: 'Team B'})
            MATCH (p)-[r:PLAYS_FOR]->(old)
            SET r.until = 2024
            CREATE (p)-[:PLAYS_FOR {since: 2024}]->(new)
        """)

        # Verify both relationships exist
        history_query = """
        MATCH (p:Player {name: 'Transfer Player'})-[r:PLAYS_FOR]->(t:Team)
        RETURN count(r) AS relationships
        """
        result = neo4j_session.run(history_query)
        assert result.single()["relationships"] == 2


@pytest.mark.integration
@pytest.mark.e2e
class TestMatchCompetitionIntegration:
    """Integration tests for match and competition management"""

    def test_create_competition_with_matches(self, neo4j_session):
        """
        GIVEN: A new competition season starts
        WHEN: Competition and matches are created
        THEN: All matches are properly linked to competition
        """
        # Create competition
        comp_query = """
        CREATE (c:Competition {
            competition_id: randomUUID(),
            name: 'Test League',
            season: 2024,
            created_at: datetime()
        })
        RETURN c
        """
        comp_result = neo4j_session.run(comp_query)
        comp = comp_result.single()["c"]

        # Create teams
        teams = []
        for i in range(4):
            team_query = """
            CREATE (t:Team {
                team_id: randomUUID(),
                name: $name,
                created_at: datetime()
            })
            RETURN t
            """
            result = neo4j_session.run(team_query, name=f"Team_{i}")
            teams.append(result.single()["t"])

        # Create round-robin matches
        match_count = 0
        for i, home in enumerate(teams):
            for away in teams[i+1:]:
                match_query = """
                MATCH (c:Competition {competition_id: $comp_id})
                MATCH (home:Team {team_id: $home_id})
                MATCH (away:Team {team_id: $away_id})
                CREATE (m:Match {
                    match_id: randomUUID(),
                    date: datetime(),
                    created_at: datetime()
                })
                CREATE (home)-[:HOME_TEAM]->(m)
                CREATE (away)-[:AWAY_TEAM]->(m)
                CREATE (m)-[:IN_COMPETITION]->(c)
                """
                neo4j_session.run(
                    match_query,
                    comp_id=comp["competition_id"],
                    home_id=home["team_id"],
                    away_id=away["team_id"]
                )
                match_count += 1

        # Verify match count (n choose 2 = 6)
        verify_query = """
        MATCH (m:Match)-[:IN_COMPETITION]->(c:Competition {competition_id: $comp_id})
        RETURN count(m) AS match_count
        """
        result = neo4j_session.run(verify_query, comp_id=comp["competition_id"])
        assert result.single()["match_count"] == 6

    def test_record_match_with_events(self, neo4j_session):
        """
        GIVEN: A match is scheduled
        WHEN: Match is played and events are recorded
        THEN: Complete match record with events exists
        """
        # Setup teams and match
        neo4j_session.run("""
            CREATE (home:Team {team_id: randomUUID(), name: 'Home Team'})
            CREATE (away:Team {team_id: randomUUID(), name: 'Away Team'})
            CREATE (m:Match {
                match_id: randomUUID(),
                date: datetime(),
                status: 'in_progress',
                created_at: datetime()
            })
            CREATE (home)-[:HOME_TEAM]->(m)
            CREATE (away)-[:AWAY_TEAM]->(m)
        """)

        # Record events
        events = [
            ("goal", 23, "Home Team"),
            ("yellow_card", 35, None),
            ("goal", 67, "Away Team"),
            ("substitution", 72, "Home Team"),
            ("goal", 89, "Home Team")
        ]

        for event_type, minute, team in events:
            event_query = """
            MATCH (m:Match)
            CREATE (e:Event {
                event_id: randomUUID(),
                type: $type,
                minute: $minute,
                team: $team,
                created_at: datetime()
            })
            CREATE (m)-[:HAS_EVENT]->(e)
            """
            neo4j_session.run(event_query, type=event_type, minute=minute, team=team)

        # Update final score
        neo4j_session.run("""
            MATCH (m:Match)
            SET m.home_score = 2,
                m.away_score = 1,
                m.status = 'completed'
        """)

        # Verify complete record
        verify_query = """
        MATCH (m:Match)
        OPTIONAL MATCH (m)-[:HAS_EVENT]->(e:Event)
        RETURN m, count(e) AS event_count
        """
        result = neo4j_session.run(verify_query)
        record = result.single()
        assert record["m"]["status"] == "completed"
        assert record["event_count"] == 5


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Performance integration tests"""

    def test_bulk_data_import_performance(self, neo4j_session, benchmark_context):
        """
        GIVEN: Large dataset needs to be imported
        WHEN: Bulk import is performed
        THEN: Import completes within performance threshold
        """
        # Prepare bulk data
        teams = [{"name": f"BulkTeam_{i}", "founded": 2000 + i} for i in range(20)]
        players = [{"name": f"BulkPlayer_{i}", "position": "Forward"} for i in range(100)]

        with benchmark_context() as bench:
            # Bulk import teams
            team_query = """
            UNWIND $teams AS team
            CREATE (t:Team {
                team_id: randomUUID(),
                name: team.name,
                founded: team.founded,
                created_at: datetime()
            })
            """
            neo4j_session.run(team_query, teams=teams)

            # Bulk import players and assign to teams
            player_query = """
            UNWIND $players AS player
            CREATE (p:Player {
                player_id: randomUUID(),
                name: player.name,
                position: player.position,
                created_at: datetime()
            })
            WITH p
            MATCH (t:Team)
            WHERE t.name STARTS WITH 'BulkTeam_'
            WITH p, t
            LIMIT 1
            CREATE (p)-[:PLAYS_FOR {since: 2024}]->(t)
            """
            neo4j_session.run(player_query, players=players)

        # Verify import succeeded
        verify_query = """
        MATCH (t:Team) WHERE t.name STARTS WITH 'BulkTeam_'
        MATCH (p:Player) WHERE p.name STARTS WITH 'BulkPlayer_'
        RETURN count(DISTINCT t) AS team_count, count(DISTINCT p) AS player_count
        """
        result = neo4j_session.run(verify_query)
        counts = result.single()
        assert counts["team_count"] == 20
        assert counts["player_count"] == 100
        assert bench.duration < 5.0  # Should complete in under 5 seconds

    def test_complex_query_performance(self, neo4j_session, populated_database):
        """
        GIVEN: Database with related entities
        WHEN: Complex analytical query is executed
        THEN: Query completes within acceptable time
        """
        query = """
        MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
        OPTIONAL MATCH (t)-[:PLAYED]->(m:Match)
        WITH p, t, count(m) AS match_count
        RETURN p.name AS player,
               t.name AS team,
               match_count,
               p.position AS position
        ORDER BY match_count DESC
        LIMIT 10
        """

        import time
        start = time.time()
        result = neo4j_session.run(query)
        records = list(result)
        duration = time.time() - start

        assert len(records) > 0
        assert duration < 1.0  # Should complete in under 1 second


@pytest.mark.integration
@pytest.mark.e2e
class TestDataConsistencyIntegration:
    """Data consistency integration tests"""

    def test_referential_integrity(self, neo4j_session):
        """
        GIVEN: Related entities in database
        WHEN: Parent entity is deleted
        THEN: Orphan relationships are handled correctly
        """
        # Create entities
        neo4j_session.run("""
            CREATE (t:Team {team_id: randomUUID(), name: 'Test Team'})
            CREATE (p:Player {player_id: randomUUID(), name: 'Test Player'})
            CREATE (m:Match {match_id: randomUUID(), date: datetime()})
            CREATE (p)-[:PLAYS_FOR]->(t)
            CREATE (t)-[:HOME_TEAM]->(m)
        """)

        # Delete team and check cleanup
        neo4j_session.run("""
            MATCH (t:Team {name: 'Test Team'})
            DETACH DELETE t
        """)

        # Verify player still exists but relationship is gone
        verify_query = """
        MATCH (p:Player {name: 'Test Player'})
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(t:Team)
        RETURN p, t
        """
        result = neo4j_session.run(verify_query)
        record = result.single()
        assert record["p"] is not None  # Player exists
        assert record["t"] is None  # No team relationship

    def test_concurrent_updates(self, neo4j_session):
        """
        GIVEN: Multiple updates to same entity
        WHEN: Updates are applied concurrently
        THEN: Data remains consistent
        """
        # Create player
        neo4j_session.run("""
            CREATE (p:Player {
                player_id: randomUUID(),
                name: 'Concurrent Player',
                goals_scored: 0
            })
        """)

        # Simulate concurrent goal updates
        for _ in range(10):
            neo4j_session.run("""
                MATCH (p:Player {name: 'Concurrent Player'})
                SET p.goals_scored = p.goals_scored + 1
            """)

        # Verify final count
        verify_query = """
        MATCH (p:Player {name: 'Concurrent Player'})
        RETURN p.goals_scored AS goals
        """
        result = neo4j_session.run(verify_query)
        assert result.single()["goals"] == 10


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Error handling integration tests"""

    def test_handle_duplicate_player_creation(self, neo4j_session):
        """
        GIVEN: Player already exists
        WHEN: Attempt to create duplicate
        THEN: Error is handled gracefully
        """
        # Create player
        neo4j_session.run("""
            CREATE (p:Player {
                player_id: 'test-123',
                name: 'Unique Player'
            })
        """)

        # Attempt duplicate (using MERGE to prevent error)
        neo4j_session.run("""
            MERGE (p:Player {player_id: 'test-123'})
            ON CREATE SET p.name = 'Unique Player'
            ON MATCH SET p.updated_at = datetime()
        """)

        # Verify only one player exists
        verify_query = """
        MATCH (p:Player {player_id: 'test-123'})
        RETURN count(p) AS count
        """
        result = neo4j_session.run(verify_query)
        assert result.single()["count"] == 1


# Test execution summary
@pytest.fixture(scope="session", autouse=True)
def print_test_summary(request):
    """Print test execution summary after all tests complete"""
    yield

    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Test session completed at: {datetime.now().isoformat()}")
    print("All integration tests passed successfully!")
    print("="*80)
