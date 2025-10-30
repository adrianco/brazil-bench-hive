# Brazilian Soccer Knowledge Graph - Demo Script

## Overview

This demo showcases the capabilities of the Brazilian Soccer Knowledge Graph MCP server integrated with Claude AI. Follow this script to demonstrate natural language querying of soccer data through graph traversal and semantic understanding.

## Demo Setup

### Before You Start

1. **Ensure Neo4j is Running**
   ```bash
   docker ps | grep neo4j-brazil
   # Should show: neo4j-brazil ... Up X minutes
   ```

2. **Verify Data is Loaded**
   ```bash
   docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg "MATCH (n) RETURN count(n);"
   # Should show: count(n) > 0
   ```

3. **Start Claude Code**
   ```bash
   claude --dangerously-skip-permissions
   # Wait for Claude to initialize and connect to MCP servers
   ```

4. **Verify MCP Connection**
   ```
   In Claude: "List available MCP tools"
   # Should show: brazilian-soccer-kb tools
   ```

---

## Demo Flow

### Act 1: Introduction - Simple Queries (5 minutes)

**Goal**: Show basic entity lookup and data retrieval

#### Query 1: Player Lookup
```
You: "Tell me about Pelé's career"

Expected Response:
- Player biography
- Career statistics
- Teams played for
- Major achievements

Tools Used: search_player, get_player_career, get_player_stats
```

**What to Highlight**:
- Natural language understanding
- Single entity retrieval
- Data aggregation from multiple sources

#### Query 2: Team Information
```
You: "What is Flamengo's home stadium?"

Expected Response:
- Stadium name: Maracanã
- Capacity: 78,838
- Location: Rio de Janeiro
- Additional stadium facts

Tools Used: search_team, get_team_history
```

**What to Highlight**:
- Quick fact retrieval
- Entity property access
- Contextual information

#### Query 3: Recent Match
```
You: "When was the last match between Palmeiras and São Paulo?"

Expected Response:
- Match date
- Final score
- Competition
- Key events (goals, cards)

Tools Used: search_team (×2), search_matches, get_match_details
```

**What to Highlight**:
- Multi-entity query
- Temporal filtering
- Relationship traversal

---

### Act 2: Relationships - Graph Traversal (8 minutes)

**Goal**: Demonstrate complex relationship queries and graph navigation

#### Query 4: Common Teammates
```
You: "Who were Neymar's teammates at Santos?"

Expected Response:
- List of players who played with Neymar at Santos
- Playing periods
- Positions
- Notable achievements together

Tools Used: search_player, get_player_career, find_common_teammates
```

**What to Highlight**:
- Relationship traversal (PLAYS_FOR)
- Temporal overlap calculation
- Team-based filtering

#### Query 5: Player Career Path
```
You: "What teams did Ronaldo Nazário play for during his career?"

Expected Response:
- Complete career timeline
- All teams (Brazilian and international)
- Goals and statistics per team
- Transfer details

Tools Used: search_player, get_player_career, get_player_transfers
```

**What to Highlight**:
- Multi-hop traversal (Player → Teams → Transfers)
- Career trajectory visualization
- Historical data access

#### Query 6: Cross-Team Players
```
You: "Which players have played for both Corinthians and Palmeiras?"

Expected Response:
- List of players who played for both rival clubs
- Playing periods for each team
- Context about the rivalry
- Notable controversies

Tools Used: search_team (×2), get_team_roster (×2), get_player_career (×N)
```

**What to Highlight**:
- Complex graph intersection
- Rivalry context awareness
- Multiple relationship traversal
- Data synthesis

---

### Act 3: Statistical Analysis - Aggregation (10 minutes)

**Goal**: Show data aggregation, statistics, and analytical capabilities

#### Query 7: Team Performance
```
You: "What's Flamengo's win rate against Internacional in the last 10 years?"

Expected Response:
- Total matches played
- Wins, draws, losses
- Win percentage
- Recent form (last 5 matches)
- Notable matches

Tools Used: search_team (×2), get_head_to_head, search_matches
```

**What to Highlight**:
- Statistical aggregation
- Temporal filtering (10 years)
- Percentage calculations
- Trend analysis

#### Query 8: Competition Standings
```
You: "Who are the top 5 goal scorers in Brazilian Serie A history?"

Expected Response:
- Ranked list of top scorers
- Goal counts
- Teams played for
- Active periods
- Notable achievements

Tools Used: get_competition_top_scorers, get_player_stats (×5)
```

**What to Highlight**:
- Cross-competition aggregation
- Historical data access
- Ranking and sorting
- Player comparison

#### Query 9: Championship History
```
You: "Which team has won the most Brasileirão titles?"

Expected Response:
- Team ranking by championship wins
- Years won
- Runner-up positions
- Historical dominance analysis

Tools Used: search_team (×N), get_team_history, get_competition_standings
```

**What to Highlight**:
- Historical aggregation
- Multi-team comparison
- Championship tracking
- Legacy analysis

---

### Act 4: Complex Multi-Hop Queries (12 minutes)

**Goal**: Demonstrate advanced reasoning and complex graph traversal

#### Query 10: Career Trajectory Analysis
```
You: "Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar"

Expected Response:
- Side-by-side career comparison
- Teams played for
- Peak performance periods
- International success
- Similarity analysis
- Career arc patterns

Tools Used: search_player (×3), get_player_career (×3), get_player_stats (×3), get_player_transfers (×3)
```

**What to Highlight**:
- Multi-entity comparison
- Complex data synthesis
- Pattern recognition
- Narrative generation

#### Query 11: Pattern Finding
```
You: "Find players who scored in a Copa do Brasil final and later played in Europe"

Expected Response:
- List of matching players
- Copa do Brasil final details
- European clubs played for
- Career progression
- Success stories

Tools Used: get_competition_matches, get_match_scorers, get_player_career, get_player_transfers
```

**What to Highlight**:
- Multi-condition filtering
- Cross-competition analysis
- Geographic filtering
- Success pattern identification

#### Query 12: Coaching Success
```
You: "Which coaches have managed multiple championship-winning teams?"

Expected Response:
- List of successful coaches
- Teams managed
- Championships won
- Years of success
- Coaching style analysis

Tools Used: search_team (×N), get_team_history, (future: get_coach_history)
```

**What to Highlight**:
- Coach-team relationships
- Achievement tracking
- Multi-team success
- Historical impact

---

### Act 5: Contextual Knowledge - Synthesis (10 minutes)

**Goal**: Show Claude's ability to synthesize data with contextual knowledge

#### Query 13: Derby Explanation
```
You: "Why is Flamengo vs Fluminense called Fla-Flu?"

Expected Response:
- Historical context
- Rivalry origins (1912)
- Cultural significance
- Famous matches
- Statistical head-to-head
- Social impact

Tools Used: search_team (×2), get_head_to_head, get_rivalry_stats + Claude's knowledge
```

**What to Highlight**:
- Data + knowledge synthesis
- Historical context
- Cultural understanding
- Storytelling capability

#### Query 14: Tournament Significance
```
You: "What makes the Paulista championship (Paulistão) significant?"

Expected Response:
- Historical importance
- Team participation (São Paulo state)
- Famous matches
- Cultural relevance
- Comparison to Brasileirão
- Impact on Brazilian soccer

Tools Used: get_competition + Claude's contextual knowledge
```

**What to Highlight**:
- Regional context
- Historical significance
- Cultural awareness
- Comparative analysis

#### Query 15: Iconic Venue
```
You: "Explain the significance of Maracanã stadium in Brazilian football"

Expected Response:
- Stadium history (opened 1950)
- 1950 World Cup Final (Maracanazo)
- Record attendance
- Major events hosted
- Cultural icon status
- Modern renovations

Tools Used: get_team_history (teams using Maracanã) + Claude's knowledge
```

**What to Highlight**:
- Cultural synthesis
- Historical events
- Emotional context
- Storytelling ability

---

### Act 6: Trend Analysis - Insights (8 minutes)

**Goal**: Demonstrate analytical insights and trend identification

#### Query 16: Transfer Trends
```
You: "What trends do you see in Brazilian players moving to Europe over the past decade?"

Expected Response:
- Transfer volume trends
- Most popular leagues
- Average age of transfers
- Position distribution
- Fee trends
- Success rate analysis

Tools Used: get_player_transfers (×N), get_player_career (×N) + analysis
```

**What to Highlight**:
- Trend identification
- Statistical analysis
- Pattern recognition
- Predictive insights

#### Query 17: Goal-Scoring Evolution
```
You: "How has the average number of goals per match changed in Serie A over the years?"

Expected Response:
- Historical goal average trends
- Year-by-year comparison
- Factors affecting changes
- Comparison to international leagues
- Modern vs historic play styles

Tools Used: get_competition_matches, search_matches + aggregation
```

**What to Highlight**:
- Longitudinal analysis
- Statistical trends
- Comparative insights
- Game evolution understanding

---

## Demo Tips

### Presentation Guidelines

1. **Start Simple**: Begin with basic queries to build audience confidence
2. **Show Progress**: Gradually increase complexity to demonstrate capability
3. **Highlight Intelligence**: Point out when Claude combines multiple tools
4. **Emphasize Natural Language**: Show you're using plain language, not code
5. **Showcase Errors Gracefully**: If a query fails, show how to rephrase

### What to Emphasize

- **Natural Language**: No special syntax or commands required
- **Graph Relationships**: Show how connections reveal insights
- **Multi-Tool Orchestration**: Claude chains multiple tools automatically
- **Contextual Understanding**: Claude adds knowledge beyond just data
- **Complex Reasoning**: Handles multi-hop queries seamlessly

### Common Audience Questions

**Q: "Can it handle ambiguous queries?"**
```
Demo: "Show me matches between São Paulo and Corinthians"
(Note: São Paulo is both a team and a city - Claude resolves correctly)
```

**Q: "What if data is missing?"**
```
Demo: "Tell me about player X who doesn't exist"
Show graceful error handling and suggestions
```

**Q: "Can it combine multiple conditions?"**
```
Demo: "Find forwards who played for Flamengo and scored 20+ goals in a season"
Show complex filtering
```

**Q: "How fast is it?"**
```
Time a complex query (should be < 3 seconds)
Show query optimization
```

---

## Sample Demo Questions by Category

### Category 1: Simple Lookups (3-5 seconds each)
1. "Who scored the most goals for Flamengo in 2023?"
2. "What teams has Neymar played for in his career?"
3. "When was the last match between Palmeiras and São Paulo?"
4. "Tell me about Pelé's career statistics"
5. "What is Corinthians' home stadium?"

### Category 2: Relationship Queries (5-10 seconds each)
6. "Which players have played for both Corinthians and Palmeiras?"
7. "Show me all Brazilian players who moved to European clubs in 2024"
8. "What teams did Ronaldo Nazário play for during his career?"
9. "Who were Neymar's teammates at Santos?"
10. "Find all players who scored in a Flamengo vs Fluminense match"

### Category 3: Statistical Analysis (10-15 seconds each)
11. "Which team has won the most Brasileirão titles?"
12. "Who are the top 5 goal scorers in Brazilian Serie A history?"
13. "What's Flamengo's win rate against Internacional in the last 10 years?"
14. "Which stadium has hosted the most championship finals?"
15. "What's the average number of goals per match in Serie A 2023?"

### Category 4: Complex Multi-Hop (15-25 seconds each)
16. "Find players who scored in a Copa do Brasil final and later played in Europe"
17. "Which coaches have managed multiple championship-winning teams?"
18. "Show me teammates of Neymar at Santos who also made it to European leagues"
19. "Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar"
20. "Which players have won championships with three different Brazilian teams?"

### Category 5: Contextual & Historical (5-10 seconds + explanation)
21. "Why is Flamengo vs Fluminense called Fla-Flu?"
22. "What makes the Paulista championship (Paulistão) significant?"
23. "Explain the significance of Maracanã stadium in Brazilian football"
24. "Who are considered the greatest Brazilian strikers of all time?"
25. "What was special about Brazil's 1970 World Cup team?"

---

## Backup Scenarios

If live demo fails, have these ready:

### Pre-Recorded Video
- 5-minute highlight reel
- Shows key capabilities
- Narrated explanations

### Screenshots
- Sample queries and responses
- Architecture diagrams
- Performance metrics

### Fallback Queries
Simple guaranteed-to-work queries:
1. "Search for players named Silva"
2. "Show me Flamengo"
3. "List competitions"

---

## Post-Demo Q&A

### Expected Questions

**Q: "How does it handle real-time data?"**
A: Currently historical data; future versions will support live updates via API integrations.

**Q: "Can it work with other sports?"**
A: Yes! The MCP framework and graph model are sport-agnostic. Just change the data model.

**Q: "What's the query latency?"**
A: Simple queries: < 1s, Complex multi-hop: < 5s, depending on data size.

**Q: "Can users add custom data?"**
A: Yes, through data import scripts or manual Cypher queries.

**Q: "Is it production-ready?"**
A: This is a demo/prototype. Production requires:
- Scalable Neo4j cluster
- Rate limiting
- Authentication
- Monitoring
- Error recovery

---

## Success Metrics

Track these during demo:

- ✅ All queries return correct results
- ✅ No timeout errors (< 5s per query)
- ✅ Natural language understood correctly
- ✅ Audience engagement (questions, reactions)
- ✅ "Aha moments" when complex queries work
- ✅ Clear value proposition demonstrated

---

## Follow-Up Materials

After demo, provide:

1. **GitHub Repository**: Link to full code
2. **Setup Guide**: [SETUP.md](./SETUP.md)
3. **Architecture Document**: [ARCHITECTURE.md](./ARCHITECTURE.md)
4. **API Reference**: [API.md](./API.md)
5. **Sample Queries**: This document
6. **Contact Information**: For questions and collaboration

---

## Demo Checklist

### Pre-Demo (15 minutes before)
- [ ] Neo4j running and accessible
- [ ] Data loaded and verified
- [ ] Claude Code CLI started
- [ ] MCP server connected
- [ ] Test 2-3 sample queries
- [ ] Browser tabs ready (Neo4j Browser, GitHub)
- [ ] Backup materials accessible

### During Demo
- [ ] Start with simple queries
- [ ] Gradually increase complexity
- [ ] Point out tool chaining
- [ ] Highlight natural language
- [ ] Show error handling
- [ ] Encourage audience questions

### Post-Demo
- [ ] Share repository link
- [ ] Distribute setup guide
- [ ] Answer questions
- [ ] Collect feedback
- [ ] Follow up with interested parties

---

## Troubleshooting During Demo

### If Query Fails
1. Stay calm
2. Rephrase the query
3. Show debugging process
4. Use backup query
5. Explain what went wrong

### If MCP Disconnects
1. Check Neo4j is running
2. Restart MCP server
3. Use pre-recorded demo as backup

### If Neo4j Slow
1. Reduce query complexity
2. Use simpler examples
3. Show architecture slide while waiting

---

## Demo Duration Guide

- **Quick Demo**: 15 minutes (Acts 1-2)
- **Standard Demo**: 30 minutes (Acts 1-4)
- **Full Demo**: 45-60 minutes (All acts + Q&A)

---

**Ready to Demo!** Follow this script to showcase the power of Knowledge Graphs + MCP + Claude AI.
