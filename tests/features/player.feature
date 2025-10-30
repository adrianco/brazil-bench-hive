Feature: Player Management
  As a football data analyst
  I want to manage player information in the knowledge graph
  So that I can track player statistics and career history

  Background:
    Given the Neo4j database is running
    And the database is clean

  Scenario: Search for a player by name
    Given the database has player data
    And a player named "Pelé" exists
    When I search for player "Pelé"
    Then I should get player details
    And the player name should be "Pelé"
    And the response should include player statistics

  Scenario: Add a new player to the database
    Given I have valid player data
    When I add a new player with name "Neymar Jr"
    Then the player should be created successfully
    And the player should be queryable by ID
    And the database should contain 1 player

  Scenario: Update player information
    Given a player named "Ronaldo" exists
    And the player has position "Forward"
    When I update the player position to "Striker"
    Then the player position should be "Striker"
    And the update timestamp should be recorded

  Scenario: Search for players by position
    Given the database has multiple players
    And there are 3 players with position "Forward"
    And there are 2 players with position "Midfielder"
    When I search for players with position "Forward"
    Then I should get 3 players in the results
    And all players should have position "Forward"

  Scenario: Get player career history
    Given a player named "Ronaldinho" exists
    And the player has played for "Grêmio" from 1998 to 2001
    And the player has played for "Barcelona" from 2003 to 2008
    When I request the career history for "Ronaldinho"
    Then I should see 2 teams in the career history
    And the teams should be in chronological order

  Scenario: Find players by nationality
    Given the database has multiple players
    And there are 5 Brazilian players
    And there are 2 Argentine players
    When I search for players from "Brazil"
    Then I should get 5 players in the results
    And all players should have nationality "Brazil"

  Scenario: Get player statistics
    Given a player named "Romário" exists
    And the player has 10 matches recorded
    And the player has scored 15 goals
    When I request statistics for "Romário"
    Then the statistics should show 10 matches
    And the statistics should show 15 goals
    And the goals per match ratio should be 1.5

  Scenario: Delete a player from database
    Given a player named "TestPlayer" exists
    When I delete the player "TestPlayer"
    Then the player should not be found in database
    And the deletion should be confirmed

  Scenario: Handle invalid player search
    Given the database has player data
    When I search for player "NonExistentPlayer"
    Then I should get an empty result
    And no error should occur

  Scenario: Bulk import players
    Given I have a list of 10 valid player records
    When I perform a bulk import
    Then all 10 players should be created
    And the import should complete in under 5 seconds
    And each player should have a unique ID
