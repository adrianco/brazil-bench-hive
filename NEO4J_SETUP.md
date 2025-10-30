# Neo4j Setup for brazil-bench-hive

This document describes the Neo4j database setup for the brazil-bench-hive project.

## Overview

Neo4j is running in a Docker container with the following configuration:
- **Database Name**: `brazil-kg` (Knowledge Graph)
- **Version**: Neo4j 2025.09.0
- **Container Name**: `neo4j-brazil`

## Connection Details

- **HTTP Interface**: http://localhost:7474
- **Bolt Protocol**: bolt://localhost:7687
- **Username**: `neo4j`
- **Password**: `password`

## Quick Start

### Using Docker Compose (Recommended)

The easiest way to manage Neo4j is using Docker Compose:

```bash
# Start Neo4j
docker-compose -f docker-compose.neo4j.yml up -d

# Stop Neo4j
docker-compose -f docker-compose.neo4j.yml down

# View logs
docker-compose -f docker-compose.neo4j.yml logs -f
```

### Using Docker Commands

The Neo4j container should already be running. To check its status:

```bash
docker ps | grep neo4j-brazil
```

If the container is not running, start it with:

```bash
docker start neo4j-brazil
```

### Accessing Neo4j

#### Via Browser
Open your web browser and navigate to:
```
http://localhost:7474
```

Login with:
- Username: `neo4j`
- Password: `password`

#### Via Command Line (cypher-shell)

Execute Cypher queries from the command line:

```bash
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg
```

Example query:
```bash
docker exec neo4j-brazil cypher-shell -u neo4j -p password -d brazil-kg "MATCH (n) RETURN count(n);"
```

## Container Management

### View Logs
```bash
docker logs neo4j-brazil
```

### Stop Container
```bash
docker stop neo4j-brazil
```

### Start Container
```bash
docker start neo4j-brazil
```

### Restart Container
```bash
docker restart neo4j-brazil
```

### Remove Container (WARNING: This will delete all data)
```bash
docker stop neo4j-brazil
docker rm neo4j-brazil
docker volume rm neo4j_data neo4j_logs
```

## Recreating the Container

If you need to recreate the container from scratch:

```bash
docker run -d \
  --name neo4j-brazil \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_dbms_default__database=brazil-kg \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:latest
```

## Data Persistence

Data is persisted in Docker volumes:
- `neo4j_data`: Database files and configuration
- `neo4j_logs`: Log files

These volumes persist even when the container is stopped or removed (unless explicitly deleted).

## Features

- **APOC Plugin**: The APOC (Awesome Procedures on Cypher) library is installed and available for use.

## Database Schema

The `brazil-kg` database is currently empty and ready for your knowledge graph data.

### Example: Creating Nodes and Relationships

```cypher
// Create a player node
CREATE (p:Player {name: "Pelé", position: "Forward", number: 10})

// Create a team node
CREATE (t:Team {name: "Santos FC", founded: 1912})

// Create a relationship
MATCH (p:Player {name: "Pelé"}), (t:Team {name: "Santos FC"})
CREATE (p)-[:PLAYED_FOR {from: 1956, to: 1974}]->(t)
```

## Troubleshooting

### Container won't start
Check the logs for errors:
```bash
docker logs neo4j-brazil
```

### Can't connect to Neo4j
1. Ensure the container is running: `docker ps | grep neo4j-brazil`
2. Check that ports 7474 and 7687 are not in use by other applications
3. Verify the password is correct: `password`

### Need to reset the database
To start with a fresh database:
```bash
docker stop neo4j-brazil
docker rm neo4j-brazil
docker volume rm neo4j_data neo4j_logs
# Then recreate using the command in "Recreating the Container" section
```

## Integration with Development

### Python
```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

with driver.session(database="brazil-kg") as session:
    result = session.run("MATCH (n) RETURN count(n) AS count")
    print(result.single()["count"])

driver.close()
```

### JavaScript/Node.js
```javascript
const neo4j = require('neo4j-driver');

const driver = neo4j.driver(
  'bolt://localhost:7687',
  neo4j.auth.basic('neo4j', 'password')
);

const session = driver.session({ database: 'brazil-kg' });

session.run('MATCH (n) RETURN count(n) AS count')
  .then(result => {
    console.log(result.records[0].get('count'));
    session.close();
    driver.close();
  });
```

## Additional Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [APOC Documentation](https://neo4j.com/labs/apoc/)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/current/)

## Notes

- The default password is intentionally simple (`password`) for development purposes. In production, use a strong password.
- The Neo4j browser interface at http://localhost:7474 provides an interactive way to explore and query the database.
- The `brazil-kg` database is configured as the default database and will be used automatically when connecting.
