from opensearchpy import OpenSearch, helpers
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from config import settings
from services.observability import observability_service

class OpenSearchService:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False
        )
        self.items_index = "crisis_items"
        self.claims_index = "crisis_claims"
        self.evidence_index = "crisis_evidence"
        
    async def ensure_indexes(self):
        """Create indexes if they don't exist"""
        # Items index
        if not self.client.indices.exists(index=self.items_index):
            self.client.indices.create(
                index=self.items_index,
                body={
                    "settings": {
                        "number_of_shards": 2,
                        "number_of_replicas": 1,
                        "analysis": {
                            "analyzer": {
                                "crisis_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "stop", "snowball"]
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "source": {"type": "keyword"},
                            "source_id": {"type": "keyword"},
                            "url": {"type": "keyword"},
                            "title": {"type": "text", "analyzer": "crisis_analyzer"},
                            "text": {"type": "text", "analyzer": "crisis_analyzer"},
                            "author": {"type": "text"},
                            "timestamp": {"type": "date"},
                            "language_detected": {"type": "keyword"},
                            "entities": {"type": "nested"},
                            "topics": {"type": "keyword"},
                            "risk_score": {"type": "float"},
                            "ingested_at": {"type": "date"}
                        }
                    }
                }
            )
            observability_service.log_info(f"Created index: {self.items_index}")
        
        # Claims index
        if not self.client.indices.exists(index=self.claims_index):
            self.client.indices.create(
                index=self.claims_index,
                body={
                    "settings": {"number_of_shards": 2, "number_of_replicas": 1},
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "text": {"type": "text", "analyzer": "crisis_analyzer"},
                            "normalized_item_id": {"type": "keyword"},
                            "topic": {"type": "keyword"},
                            "checkworthiness": {"type": "float"},
                            "veracity_likelihood": {"type": "float"},
                            "harm_potential": {"type": "float"},
                            "risk_score": {"type": "float"},
                            "status": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    }
                }
            )
            observability_service.log_info(f"Created index: {self.claims_index}")
    
    async def index_item(self, item: Dict[str, Any]):
        """Index a normalized item"""
        try:
            self.client.index(
                index=self.items_index,
                id=item['id'],
                body=item
            )
            observability_service.log_info(f"Indexed item: {item['id']}")
        except Exception as e:
            observability_service.log_error(f"Failed to index item {item['id']}: {e}")
    
    async def index_claim(self, claim: Dict[str, Any]):
        """Index a claim"""
        try:
            self.client.index(
                index=self.claims_index,
                id=claim['id'],
                body=claim
            )
            observability_service.log_info(f"Indexed claim: {claim['id']}")
        except Exception as e:
            observability_service.log_error(f"Failed to index claim {claim['id']}: {e}")
    
    async def search_items(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """Full-text search for items"""
        body = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "text"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}]
        }
        
        # Add filters
        if filters:
            filter_clauses = []
            if "source" in filters:
                filter_clauses.append({"term": {"source": filters["source"]}})
            if "topics" in filters:
                filter_clauses.append({"terms": {"topics": filters["topics"]}})
            if "min_risk_score" in filters:
                filter_clauses.append({"range": {"risk_score": {"gte": filters["min_risk_score"]}}})
            
            if filter_clauses:
                body["query"]["bool"]["filter"] = filter_clauses
        
        result = self.client.search(index=self.items_index, body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]
    
    async def get_aggregations(self, field: str, size: int = 10) -> Dict[str, int]:
        """Get aggregations for analytics"""
        body = {
            "size": 0,
            "aggs": {
                f"{field}_counts": {
                    "terms": {"field": field, "size": size}
                }
            }
        }
        
        result = self.client.search(index=self.items_index, body=body)
        buckets = result["aggregations"][f"{field}_counts"]["buckets"]
        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}

# Singleton instance
opensearch_service = OpenSearchService()
