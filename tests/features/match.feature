Feature: Match Management
  As a football data analyst
  I want to record and analyze match data
  So that I can track game results and performance metrics

  Background:
    Given the Neo4j database is running
    And the database is clean

  Scenario: Create a new match
    Given team "Flamengo" exists
    And team "Vasco" exists
    And I have valid match data
    When I create a match between "Flamengo" and "Vasco"
    Then the match should be created successfully
    And the match should link both teams
    And the match should have a date

  Scenario: Record match result
    Given a match exists between "Palmeiras" and "Santos"
    When I record the result as 3-1
    Then the home score should be 3
    And the away score should be 1
    And the match status should be "completed"

  Scenario: Get match details
    Given a completed match exists
    And the match ID is known
    When I request match details
    Then I should get complete match information
    And the response should include both teams
    And the response should include the score
    And the response should include the date

  Scenario: Search matches by team
    Given team "Corinthians" exists
    And "Corinthians" has played 5 home matches
    And "Corinthians" has played 5 away matches
    When I search for matches involving "Corinthians"
    Then I should get 10 matches
    And "Corinthians" should appear in all matches

  Scenario: Search matches by date range
    Given there are matches in January 2024
    And there are matches in February 2024
    And there are matches in March 2024
    When I search for matches between "2024-02-01" and "2024-02-29"
    Then I should only get February matches
    And all matches should be within the date range

  Scenario: Record match events
    Given a match exists between "São Paulo" and "Internacional"
    When I record a goal by "São Paulo" at minute 23
    And I record a yellow card at minute 45
    And I record a substitution at minute 67
    Then the match should have 3 events
    And events should be in chronological order

  Scenario: Get head-to-head statistics
    Given "Fluminense" has played "Botafogo" 10 times
    And "Fluminense" won 4 matches
    And "Botafogo" won 3 matches
    And 3 matches were draws
    When I request head-to-head statistics
    Then "Fluminense" wins should be 4
    And "Botafogo" wins should be 3
    And draws should be 3

  Scenario: Search matches by competition
    Given there are 10 "Série A" matches
    And there are 5 "Copa do Brasil" matches
    When I search for "Série A" matches
    Then I should get 10 matches
    And all matches should be in "Série A"

  Scenario: Get match attendance statistics
    Given a match exists with 45000 attendance
    And the stadium capacity is 50000
    When I calculate attendance percentage
    Then the attendance rate should be 90%

  Scenario: Update match information
    Given a match exists with status "scheduled"
    When I update the match status to "completed"
    And I update the attendance to 30000
    Then the status should be "completed"
    And the attendance should be 30000

  Scenario: Delete a match
    Given a match exists between teams
    When I delete the match
    Then the match should not be found
    And the teams should remain in database

  Scenario: Handle invalid match data
    Given team "TeamA" exists
    When I try to create a match with invalid date
    Then the creation should fail
    And an appropriate error message should be returned

  Scenario: Bulk import matches
    Given I have a list of 20 valid match records
    And all referenced teams exist
    When I perform a bulk match import
    Then all 20 matches should be created
    And each match should link to correct teams
    And the import should complete in under 10 seconds
