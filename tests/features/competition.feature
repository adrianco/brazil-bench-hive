Feature: Competition Management
  As a football data analyst
  I want to manage competition and tournament data
  So that I can organize matches and track championships

  Background:
    Given the Neo4j database is running
    And the database is clean

  Scenario: Create a new competition
    Given I have valid competition data
    When I create a competition named "Campeonato Brasileiro Série A"
    Then the competition should be created successfully
    And the competition should have a unique ID
    And the competition should have a season year

  Scenario: Get competition details
    Given a competition "Copa do Brasil 2024" exists
    When I request competition details
    Then I should get competition information
    And the response should include the name
    And the response should include the format
    And the response should include participating teams

  Scenario: Add teams to competition
    Given a competition "Libertadores 2024" exists
    And teams "Flamengo", "Palmeiras", "Atlético-MG" exist
    When I add these teams to the competition
    Then the competition should have 3 teams
    And all teams should be linked to the competition

  Scenario: Get competition standings
    Given a competition "Série A 2024" exists
    And the competition has 4 teams
    And teams have played matches with results
    When I request the standings
    Then teams should be ordered by points
    And each team should show wins, draws, losses
    And the points should be calculated correctly

  Scenario: Search competitions by season
    Given there are 5 competitions in 2024
    And there are 3 competitions in 2023
    When I search for competitions in 2024
    Then I should get 5 competitions
    And all competitions should be in 2024

  Scenario: Get competition matches
    Given a competition "Copa do Brasil" exists
    And the competition has 10 matches scheduled
    When I request competition matches
    Then I should get 10 matches
    And all matches should belong to the competition
    And matches should include teams and dates

  Scenario: Update competition information
    Given a competition "Libertadores" exists
    And the competition has 8 teams
    When I update the number of teams to 16
    Then the competition should have 16 team slots
    And the update should be persisted

  Scenario: Track competition progress
    Given a competition "Série A" exists
    And there are 20 total rounds
    And 15 rounds are completed
    When I check competition progress
    Then the completion percentage should be 75%
    And 5 rounds should remain

  Scenario: Get competition champions
    Given a competition "Série A 2023" exists
    And the competition is completed
    And "Palmeiras" won the competition
    When I request the champion
    Then the champion should be "Palmeiras"
    And the championship date should be recorded

  Scenario: Calculate competition statistics
    Given a competition "Copa do Brasil" exists
    And the competition has 50 matches played
    And there were 125 total goals
    When I calculate competition statistics
    Then the average goals per match should be 2.5
    And the total matches should be 50

  Scenario: Search competitions by type
    Given there are 3 "League" competitions
    And there are 2 "Cup" competitions
    When I search for "Cup" competitions
    Then I should get 2 competitions
    And all should have format "Cup"

  Scenario: Get team competition history
    Given team "Flamengo" exists
    And "Flamengo" competed in "Série A 2023"
    And "Flamengo" competed in "Copa do Brasil 2023"
    And "Flamengo" competed in "Libertadores 2023"
    When I request competition history for "Flamengo"
    Then I should see 3 competitions
    And all competitions should link to "Flamengo"

  Scenario: Handle competition not found
    When I search for competition "NonExistent Cup"
    Then I should get an empty result
    And no error should occur

  Scenario: Delete a competition
    Given a competition "Test Tournament" exists
    When I delete the competition
    Then the competition should not be found
    And related matches should be unlinked
