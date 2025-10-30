Feature: Football Data Analysis
  As a football data analyst
  I want to perform advanced analytics on the knowledge graph
  So that I can derive insights and identify patterns

  Background:
    Given the Neo4j database is running
    And the database is populated with sample data

  Scenario: Calculate player performance metrics
    Given a player "Neymar" exists
    And the player has played 20 matches
    And the player has scored 15 goals
    And the player has 10 assists
    When I analyze player performance
    Then the goals per match should be 0.75
    And the assists per match should be 0.5
    And the goal contribution should be 25 events

  Scenario: Identify top scorers
    Given there are 10 players in the database
    And players have different goal counts
    When I request top 5 scorers
    Then I should get 5 players
    And players should be ordered by goals descending
    And the top player should have the most goals

  Scenario: Analyze team form
    Given a team "Palmeiras" exists
    And the team's last 5 matches are "W,W,D,W,L"
    When I analyze recent form
    Then the form score should be 10 points
    And the win percentage should be 60%

  Scenario: Predict match outcome
    Given team "Flamengo" has win rate 70%
    And team "Vasco" has win rate 30%
    And teams have played each other 10 times
    When I generate match prediction
    Then "Flamengo" should be favored
    And prediction confidence should be provided

  Scenario: Find player transfer patterns
    Given player "Ronaldinho" exists
    And the player has played for 5 different teams
    When I analyze transfer patterns
    Then I should see transfer timeline
    And average tenure should be calculated
    And career progression should be mapped

  Scenario: Identify team rivalry
    Given team "Flamengo" and "Fluminense" exist
    And they have played 50 matches historically
    And matches have high attendance
    When I calculate rivalry score
    Then the rivalry should be classified as "intense"
    And historical statistics should be provided

  Scenario: Analyze competition competitiveness
    Given a competition "Série A" exists
    And the competition has 20 teams
    And point differences are small
    When I calculate competition balance
    Then the competitiveness score should be high
    And parity index should be calculated

  Scenario: Find player similar to another
    Given player "Pelé" exists with specific attributes
    When I search for similar players
    Then I should get players with similar positions
    And playing styles should be comparable
    And statistical profiles should match

  Scenario: Calculate team chemistry
    Given a team "São Paulo" exists
    And the team has 11 starting players
    And players have played together for 2 seasons
    When I analyze team chemistry
    Then the chemistry score should be calculated
    And player partnerships should be identified

  Scenario: Identify breakthrough players
    Given there are young players in database
    And players have increasing performance metrics
    When I search for breakthrough talents
    Then I should get players under 23
    And players should show performance growth
    And potential should be estimated

  Scenario: Analyze home vs away performance
    Given a team "Corinthians" exists
    And the team has played 10 home matches
    And the team has played 10 away matches
    When I compare home and away performance
    Then home win rate should be calculated
    And away win rate should be calculated
    And home advantage should be quantified

  Scenario: Find optimal team formation
    Given a team "Internacional" exists
    And the team has players in various positions
    When I analyze formation effectiveness
    Then the best formation should be identified
    And player positions should be optimized

  Scenario: Calculate goal scoring patterns
    Given a team "Grêmio" exists
    And the team has scored goals at various minutes
    When I analyze scoring patterns
    Then peak scoring times should be identified
    And scoring distribution should be shown

  Scenario: Identify underperforming players
    Given a team "Atlético-MG" exists
    And players have expected vs actual statistics
    When I analyze performance gaps
    Then underperforming players should be listed
    And performance delta should be calculated

  Scenario: Generate season summary
    Given a competition "Série A 2024" exists
    And the season is completed
    When I generate season analytics
    Then I should get comprehensive statistics
    And top performers should be highlighted
    And key moments should be identified
    And records should be documented
