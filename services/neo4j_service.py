from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from config import settings
from services.observability import observability_service

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
    def close(self):
        self.driver.close()
    
    async def create_entity(self, entity_type: str, properties: Dict[str, Any]):
        """Create an entity node"""
        with self.driver.session() as session:
            query = f"""
            MERGE (e:{entity_type} {{name: $name}})
            SET e += $properties
            RETURN e
            """
            session.run(query, name=properties['name'], properties=properties)
            observability_service.log_info(f"Created {entity_type} entity: {properties['name']}")
    
    async def create_relationship(
        self,
        from_entity: Dict[str, str],
        to_entity: Dict[str, str],
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Create a relationship between entities"""
        with self.driver.session() as session:
            query = """
            MATCH (a {name: $from_name})
            MATCH (b {name: $to_name})
            MERGE (a)-[r:%s]->(b)
            SET r += $properties
            RETURN r
            """ % relationship_type
            
            session.run(
                query,
                from_name=from_entity['name'],
                to_name=to_entity['name'],
                properties=properties or {}
            )
    
    async def find_connected_entities(
        self,
        entity_name: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """Find all entities connected to a given entity"""
        with self.driver.session() as session:
            query = """
            MATCH path = (start {name: $name})-[*1..%d]-(connected)
            RETURN DISTINCT connected.name as name, labels(connected) as types
            LIMIT 100
            """ % max_depth
            
            result = session.run(query, name=entity_name)
            return [{"name": record["name"], "types": record["types"]} for record in result]
    
    async def find_influence_path(
        self,
        source: str,
        target: str,
        max_hops: int = 5
    ) -> Optional[List[str]]:
        """Find shortest path between two entities"""
        with self.driver.session() as session:
            query = """
            MATCH path = shortestPath(
                (source {name: $source})-[*..%d]-(target {name: $target})
            )
            RETURN [node in nodes(path) | node.name] as path
            """ % max_hops
            
            result = session.run(query, source=source, target=target)
            record = result.single()
            return record["path"] if record else None
    
    async def get_entity_degree(self, entity_name: str) -> int:
        """Get the degree (number of connections) of an entity"""
        with self.driver.session() as session:
            query = """
            MATCH (e {name: $name})--(connected)
            RETURN count(DISTINCT connected) as degree
            """
            result = session.run(query, name=entity_name)
            record = result.single()
            return record["degree"] if record else 0
    
    async def detect_communities(self, algorithm: str = "louvain") -> List[List[str]]:
        """Detect communities using graph algorithms"""
        with self.driver.session() as session:
            # Simplified - in production, use Neo4j Graph Data Science library
            query = """
            CALL gds.louvain.stream('crisis-graph')
            YIELD nodeId, communityId
            RETURN communityId, collect(gds.util.asNode(nodeId).name) as members
            ORDER BY size(members) DESC
            LIMIT 20
            """
            try:
                result = session.run(query)
                return [record["members"] for record in result]
            except Exception as e:
                observability_service.log_warning(f"Community detection failed: {e}")
                return []

# Singleton instance
neo4j_service = Neo4jService()
