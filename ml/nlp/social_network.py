import networkx as nx
from typing import List, Dict, Any, Set
from collections import defaultdict
from services.observability import observability_service

class SocialNetworkAnalyzer:
    """Analyze social networks and information spread"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_network(self, interactions: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Build social network from interactions
        
        Args:
            interactions: List of {source, target, type, weight} dicts
            
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        
        for interaction in interactions:
            source = interaction.get('source')
            target = interaction.get('target')
            weight = interaction.get('weight', 1.0)
            interaction_type = interaction.get('type', 'unknown')
            
            if source and target:
                G.add_edge(
                    source,
                    target,
                    weight=weight,
                    type=interaction_type
                )
        
        self.graph = G
        return G
    
    def find_influencers(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Find most influential nodes
        
        Uses PageRank algorithm
        
        Returns:
            List of top influencers with scores
        """
        if len(self.graph) == 0:
            return []
        
        # Calculate PageRank
        pagerank = nx.pagerank(self.graph)
        
        # Sort by score
        sorted_nodes = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        influencers = []
        for node, score in sorted_nodes:
            influencers.append({
                'node': node,
                'pagerank_score': score,
                'in_degree': self.graph.in_degree(node),
                'out_degree': self.graph.out_degree(node)
            })
        
        return influencers
    
    def detect_communities(self) -> List[Set]:
        """
        Detect communities using Louvain algorithm
        
        Returns:
            List of community sets
        """
        if len(self.graph) == 0:
            return []
        
        # Convert to undirected for community detection
        G_undirected = self.graph.to_undirected()
        
        try:
            import community as community_louvain
            
            # Detect communities
            partition = community_louvain.best_partition(G_undirected)
            
            # Group nodes by community
            communities = defaultdict(set)
            for node, comm_id in partition.items():
                communities[comm_id].add(node)
            
            return list(communities.values())
            
        except ImportError:
            observability_service.log_warning("python-louvain not installed, using basic clustering")
            
            # Fallback: connected components
            return list(nx.connected_components(G_undirected))
    
    def find_shortest_path(self, source: str, target: str) -> List[str]:
        """Find shortest path between two nodes"""
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []
    
    def calculate_centrality_measures(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate various centrality measures
        
        Returns:
            Dict of {measure_name: {node: score}}
        """
        if len(self.graph) == 0:
            return {}
        
        measures = {}
        
        # Degree centrality
        measures['degree'] = nx.degree_centrality(self.graph)
        
        # Betweenness centrality (how often node is on shortest paths)
        measures['betweenness'] = nx.betweenness_centrality(self.graph)
        
        # Closeness centrality (average distance to all other nodes)
        if nx.is_strongly_connected(self.graph):
            measures['closeness'] = nx.closeness_centrality(self.graph)
        else:
            measures['closeness'] = {}
        
        # Eigenvector centrality
        try:
            measures['eigenvector'] = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except:
            measures['eigenvector'] = {}
        
        return measures
    
    def analyze_information_spread(
        self,
        source_node: str,
        max_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze how information spreads from a source
        
        Args:
            source_node: Starting node
            max_hops: Maximum propagation distance
            
        Returns:
            Dict with reach analysis
        """
        if source_node not in self.graph:
            return {
'reach': 0,
                'nodes_by_hop': {}
            }
        
        # BFS to find nodes at each hop distance
        nodes_by_hop = defaultdict(set)
        visited = {source_node}
        current_level = {source_node}
        
        for hop in range(max_hops):
            next_level = set()
            for node in current_level:
                for neighbor in self.graph.successors(node):
                    if neighbor not in visited:
                        next_level.add(neighbor)
                        visited.add(neighbor)
                        nodes_by_hop[hop + 1].add(neighbor)
            
            current_level = next_level
            if not current_level:
                break
        
        return {
            'source': source_node,
            'total_reach': len(visited) - 1,  # Exclude source
            'nodes_by_hop': {k: list(v) for k, v in nodes_by_hop.items()},
            'max_hops_reached': max(nodes_by_hop.keys()) if nodes_by_hop else 0
        }
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """
        Export network for visualization
        
        Returns:
            Dict with nodes and edges for vis tools
        """
        nodes = []
        for node in self.graph.nodes():
            nodes.append({
                'id': node,
                'label': str(node),
                'in_degree': self.graph.in_degree(node),
                'out_degree': self.graph.out_degree(node)
            })
        
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                'from': source,
                'to': target,
                'weight': data.get('weight', 1.0),
                'type': data.get('type', 'unknown')
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }

# Singleton
social_network_analyzer = SocialNetworkAnalyzer()
