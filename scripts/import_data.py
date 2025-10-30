#!/usr/bin/env python3
"""
Brazilian Soccer Knowledge Graph - Data Import Script

This script initializes the Neo4j database with:
1. Schema constraints and indexes
2. Sample data from docs/sample-data.json

Context:
- Connects to Neo4j at bolt://localhost:7687
- Database: brazil-kg
- Credentials: neo4j/password
- Creates complete graph structure for testing

Author: Hive Mind Collective Intelligence System
"""

import json
import sys
from pathlib import Path
from neo4j import GraphDatabase
from datetime import datetime

# Neo4j connection configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "brazil-kg"

class DataImporter:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.stats = {
            "constraints": 0,
            "indexes": 0,
            "nodes": 0,
            "relationships": 0,
            "errors": []
        }

    def close(self):
        self.driver.close()

    def execute_query(self, query, params=None):
        """Execute a single query"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            try:
                result = session.run(query, params or {})
                return result
            except Exception as e:
                error_msg = f"Query failed: {str(e)[:100]}"
                self.stats["errors"].append(error_msg)
                print(f"  ⚠️  {error_msg}")
                return None

    def initialize_schema(self):
        """Create constraints and indexes"""
        print("\n📐 Initializing Schema...")
        print("=" * 60)

        # Constraints
        constraints = [
            "CREATE CONSTRAINT player_id_unique IF NOT EXISTS FOR (p:Player) REQUIRE p.player_id IS UNIQUE",
            "CREATE CONSTRAINT player_name_required IF NOT EXISTS FOR (p:Player) REQUIRE p.name IS NOT NULL",
            "CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.team_id IS UNIQUE",
            "CREATE CONSTRAINT team_name_required IF NOT EXISTS FOR (t:Team) REQUIRE t.name IS NOT NULL",
            "CREATE CONSTRAINT match_id_unique IF NOT EXISTS FOR (m:Match) REQUIRE m.match_id IS UNIQUE",
            "CREATE CONSTRAINT match_date_required IF NOT EXISTS FOR (m:Match) REQUIRE m.date IS NOT NULL",
            "CREATE CONSTRAINT competition_id_unique IF NOT EXISTS FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE",
            "CREATE CONSTRAINT stadium_id_unique IF NOT EXISTS FOR (s:Stadium) REQUIRE s.stadium_id IS UNIQUE",
            "CREATE CONSTRAINT coach_id_unique IF NOT EXISTS FOR (co:Coach) REQUIRE co.coach_id IS UNIQUE",
        ]

        print(f"\nCreating {len(constraints)} constraints...")
        for constraint in constraints:
            result = self.execute_query(constraint)
            if result is not None:
                self.stats["constraints"] += 1
                print("  ✓ Constraint created")

        # Indexes
        indexes = [
            "CREATE INDEX player_name_index IF NOT EXISTS FOR (p:Player) ON (p.name)",
            "CREATE INDEX player_position_index IF NOT EXISTS FOR (p:Player) ON (p.position)",
            "CREATE INDEX team_name_index IF NOT EXISTS FOR (t:Team) ON (t.name)",
            "CREATE INDEX team_city_index IF NOT EXISTS FOR (t:Team) ON (t.city)",
            "CREATE INDEX match_date_index IF NOT EXISTS FOR (m:Match) ON (m.date)",
            "CREATE INDEX competition_season_index IF NOT EXISTS FOR (c:Competition) ON (c.season)",
            "CREATE INDEX stadium_name_index IF NOT EXISTS FOR (s:Stadium) ON (s.name)",
            "CREATE INDEX coach_name_index IF NOT EXISTS FOR (co:Coach) ON (co.name)",
        ]

        print(f"\nCreating {len(indexes)} indexes...")
        for index in indexes:
            result = self.execute_query(index)
            if result is not None:
                self.stats["indexes"] += 1
                print("  ✓ Index created")

        print(f"\n✅ Schema initialized: {self.stats['constraints']} constraints, {self.stats['indexes']} indexes")

    def import_sample_data(self):
        """Import sample data from JSON file"""
        print("\n📦 Importing Sample Data...")
        print("=" * 60)

        data_file = Path("/workspaces/brazil-bench-hive/docs/sample-data.json")
        if not data_file.exists():
            print("❌ Sample data file not found!")
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Import stadiums
        print(f"\nImporting {len(data.get('stadiums', []))} stadiums...")
        for stadium in data.get('stadiums', []):
            query = """
            CREATE (s:Stadium {
                stadium_id: $stadium_id,
                name: $name,
                city: $city,
                state: $state,
                capacity: $capacity,
                opened_year: $opened_year
            })
            """
            self.execute_query(query, stadium)
            self.stats["nodes"] += 1
            print(f"  ✓ {stadium['name']}")

        # Import teams
        print(f"\nImporting {len(data.get('teams', []))} teams...")
        for team in data.get('teams', []):
            query = """
            CREATE (t:Team {
                team_id: $team_id,
                name: $name,
                short_name: $short_name,
                city: $city,
                state: $state,
                founded_year: $founded_year,
                stadium_name: $stadium_name,
                colors: $colors
            })
            """
            self.execute_query(query, team)
            self.stats["nodes"] += 1
            print(f"  ✓ {team['name']}")

        # Import competitions
        print(f"\nImporting {len(data.get('competitions', []))} competitions...")
        for comp in data.get('competitions', []):
            query = """
            CREATE (c:Competition {
                competition_id: $competition_id,
                name: $name,
                season: $season,
                type: $type,
                tier: $tier
            })
            """
            self.execute_query(query, comp)
            self.stats["nodes"] += 1
            print(f"  ✓ {comp['name']} {comp['season']}")

        # Import players
        print(f"\nImporting {len(data.get('players', []))} players...")
        for player in data.get('players', []):
            query = """
            CREATE (p:Player {
                player_id: $player_id,
                name: $name,
                birth_date: $birth_date,
                nationality: $nationality,
                position: $position,
                jersey_number: $jersey_number
            })
            """
            self.execute_query(query, player)
            self.stats["nodes"] += 1
            print(f"  ✓ {player['name']}")

        # Import matches
        print(f"\nImporting {len(data.get('matches', []))} matches...")
        for match in data.get('matches', []):
            query = """
            CREATE (m:Match {
                match_id: $match_id,
                date: $date,
                home_score: $home_score,
                away_score: $away_score,
                attendance: $attendance,
                match_status: $match_status
            })
            """
            self.execute_query(query, match)
            self.stats["nodes"] += 1
            print(f"  ✓ Match {match['match_id']}")

        print(f"\n✅ Imported {self.stats['nodes']} nodes")

    def create_relationships(self):
        """Create relationships between entities"""
        print("\n🔗 Creating Relationships...")
        print("=" * 60)

        data_file = Path("/workspaces/brazil-bench-hive/docs/sample-data.json")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # PLAYS_FOR relationships
        print("\nCreating PLAYS_FOR relationships...")
        for rel in data.get('relationships', {}).get('plays_for', []):
            query = """
            MATCH (p:Player {player_id: $player_id})
            MATCH (t:Team {team_id: $team_id})
            CREATE (p)-[:PLAYS_FOR {
                from_date: $from_date,
                to_date: $to_date,
                jersey_number: $jersey_number
            }]->(t)
            """
            self.execute_query(query, rel)
            self.stats["relationships"] += 1
            print(f"  ✓ Player → Team")

        # COMPETED_IN relationships for matches
        print("\nCreating COMPETED_IN relationships...")
        for rel in data.get('relationships', {}).get('match_teams', []):
            query = """
            MATCH (t:Team {team_id: $team_id})
            MATCH (m:Match {match_id: $match_id})
            CREATE (t)-[:COMPETED_IN {
                side: $side
            }]->(m)
            """
            self.execute_query(query, rel)
            self.stats["relationships"] += 1
            print(f"  ✓ Team → Match ({rel['side']})")

        # PART_OF relationships (match → competition)
        print("\nCreating PART_OF relationships...")
        for rel in data.get('relationships', {}).get('match_competitions', []):
            query = """
            MATCH (m:Match {match_id: $match_id})
            MATCH (c:Competition {competition_id: $competition_id})
            CREATE (m)-[:PART_OF]->(c)
            """
            self.execute_query(query, rel)
            self.stats["relationships"] += 1
            print(f"  ✓ Match → Competition")

        # PLAYED_AT relationships
        print("\nCreating PLAYED_AT relationships...")
        for rel in data.get('relationships', {}).get('match_stadiums', []):
            query = """
            MATCH (m:Match {match_id: $match_id})
            MATCH (s:Stadium {stadium_id: $stadium_id})
            CREATE (m)-[:PLAYED_AT]->(s)
            """
            self.execute_query(query, rel)
            self.stats["relationships"] += 1
            print(f"  ✓ Match → Stadium")

        # SCORED_IN relationships
        print("\nCreating SCORED_IN relationships...")
        for rel in data.get('relationships', {}).get('goals', []):
            query = """
            MATCH (p:Player {player_id: $player_id})
            MATCH (m:Match {match_id: $match_id})
            CREATE (p)-[:SCORED_IN {
                minute: $minute,
                goal_type: $goal_type
            }]->(m)
            """
            self.execute_query(query, rel)
            self.stats["relationships"] += 1
            print(f"  ✓ Player → Match (goal)")

        print(f"\n✅ Created {self.stats['relationships']} relationships")

    def verify_import(self):
        """Verify the import was successful"""
        print("\n🔍 Verifying Import...")
        print("=" * 60)

        queries = {
            "Players": "MATCH (p:Player) RETURN count(p) as count",
            "Teams": "MATCH (t:Team) RETURN count(t) as count",
            "Matches": "MATCH (m:Match) RETURN count(m) as count",
            "Competitions": "MATCH (c:Competition) RETURN count(c) as count",
            "Stadiums": "MATCH (s:Stadium) RETURN count(s) as count",
            "Relationships": "MATCH ()-[r]->() RETURN count(r) as count",
        }

        for label, query in queries.items():
            result = self.execute_query(query)
            if result:
                count = result.single()["count"]
                print(f"  ✓ {label}: {count}")

    def run(self):
        """Execute full import process"""
        print("\n" + "=" * 60)
        print("🇧🇷 Brazilian Soccer Knowledge Graph - Data Import")
        print("=" * 60)

        try:
            self.initialize_schema()
            self.import_sample_data()
            self.create_relationships()
            self.verify_import()

            print("\n" + "=" * 60)
            print("✅ IMPORT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\n📊 Summary:")
            print(f"  • Constraints: {self.stats['constraints']}")
            print(f"  • Indexes: {self.stats['indexes']}")
            print(f"  • Nodes: {self.stats['nodes']}")
            print(f"  • Relationships: {self.stats['relationships']}")
            if self.stats['errors']:
                print(f"  • Errors: {len(self.stats['errors'])}")
            print()

            return 0

        except Exception as e:
            print(f"\n❌ Import failed: {e}")
            return 1
        finally:
            self.close()

if __name__ == "__main__":
    importer = DataImporter()
    sys.exit(importer.run())
