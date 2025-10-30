Feature: Team Management
  As a football data analyst
  I want to manage team information in the knowledge graph
  So that I can analyze team performance and roster changes

  Background:
    Given the Neo4j database is running
    And the database is clean

  Scenario: Create a new team
    Given I have valid team data
    When I create a team named "Santos FC"
    Then the team should be created successfully
    And the team should have an ID
    And the team should be queryable by name

  Scenario: Search for a team by name
    Given a team named "Flamengo" exists
    When I search for team "Flamengo"
    Then I should get team details
    And the team name should be "Flamengo"
    And the response should include team metadata

  Scenario: Get team roster
    Given a team named "São Paulo FC" exists
    And the team has 5 players
    When I request the roster for "São Paulo FC"
    Then I should see 5 players
    And each player should have a position
    And all players should be linked to the team

  Scenario: Update team information
    Given a team named "Corinthians" exists
    And the team stadium is "Arena Corinthians"
    When I update the team capacity to 49205
    Then the team capacity should be 49205
    And the update should be persisted

  Scenario: Add player to team
    Given a team named "Palmeiras" exists
    And a player named "Gabriel Jesus" exists
    When I add "Gabriel Jesus" to "Palmeiras"
    Then the player should be linked to the team
    And the relationship should have a start date
    And the team roster should include "Gabriel Jesus"

  Scenario: Remove player from team
    Given a team named "Grêmio" exists
    And player "Douglas Costa" plays for "Grêmio"
    When I remove "Douglas Costa" from "Grêmio"
    Then the player should not be in the team roster
    And the relationship should have an end date
    And the historical record should be preserved

  Scenario: Get team match history
    Given a team named "Internacional" exists
    And the team has played 5 matches
    When I request match history for "Internacional"
    Then I should see 5 matches
    And matches should be in chronological order
    And each match should include scores

  Scenario: Calculate team statistics
    Given a team named "Atlético Mineiro" exists
    And the team has played 10 matches
    And the team has won 6 matches
    And the team has drawn 2 matches
    And the team has lost 2 matches
    When I calculate statistics for "Atlético Mineiro"
    Then the win rate should be 60%
    And the draw rate should be 20%
    And the loss rate should be 20%

  Scenario: Find teams by city
    Given there are 3 teams in "São Paulo"
    And there are 2 teams in "Rio de Janeiro"
    When I search for teams in "São Paulo"
    Then I should get 3 teams
    And all teams should be located in "São Paulo"

  Scenario: Get team competitions
    Given a team named "Botafogo" exists
    And the team competes in "Série A"
    And the team competes in "Copa do Brasil"
    When I request competitions for "Botafogo"
    Then I should see 2 competitions
    And the competitions should include "Série A"
    And the competitions should include "Copa do Brasil"

  Scenario: Handle team not found
    When I search for team "NonExistentTeam"
    Then I should get an empty result
    And no error should occur

  Scenario: Bulk create teams
    Given I have a list of 5 valid team records
    When I perform a bulk team import
    Then all 5 teams should be created
    And each team should have unique IDs
    And the import should complete successfully
