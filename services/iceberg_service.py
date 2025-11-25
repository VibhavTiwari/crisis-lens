from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, TimestampType, DoubleType, ListType, MapType
from pyiceberg.table import Table
from typing import Dict, Any, List
from datetime import datetime
from services.observability import observability_service

class IcebergService:
    def __init__(self):
        # Configure Iceberg catalog (using REST catalog for simplicity)
        # In production, use AWS Glue, Hive Metastore, or Nessie
        self.catalog = load_catalog(
            "rest",
            **{
                "uri": "http://localhost:8181",
                "warehouse": "s3://crisis-lens-warehouse/"
            }
        )
        self.namespace = "crisis_lens"
        
    async def ensure_tables(self):
        """Create Iceberg tables if they don't exist"""
        # Ensure namespace exists
        if self.namespace not in self.catalog.list_namespaces():
            self.catalog.create_namespace(self.namespace)
        
        # Raw items table
        raw_items_schema = Schema(
            NestedField(1, "id", StringType(), required=True),
            NestedField(2, "source", StringType(), required=True),
            NestedField(3, "source_id", StringType(), required=True),
            NestedField(4, "url", StringType(), required=True),
            NestedField(5, "title", StringType(), required=False),
            NestedField(6, "text", StringType(), required=False),
            NestedField(7, "author", StringType(), required=False),
            NestedField(8, "timestamp", TimestampType(), required=True),
            NestedField(9, "language_hint", StringType(), required=False),
            NestedField(10, "raw_data", MapType(11, StringType(), 12, StringType()), required=False),
            NestedField(13, "ingested_at", TimestampType(), required=True)
        )
        
        # Normalized items table
        normalized_items_schema = Schema(
            NestedField(1, "id", StringType(), required=True),
            NestedField(2, "source", StringType(), required=True),
            NestedField(3, "url", StringType(), required=True),
            NestedField(4, "title", StringType(), required=False),
            NestedField(5, "text", StringType(), required=False),
            NestedField(6, "timestamp", TimestampType(), required=True),
            NestedField(7, "language_detected", StringType(), required=False),
            NestedField(8, "topics", ListType(9, StringType()), required=False),
            NestedField(10, "risk_score", DoubleType(), required=False),
            NestedField(11, "ingested_at", TimestampType(), required=True)
        )
        
        # Claims table
        claims_schema = Schema(
            NestedField(1, "id", StringType(), required=True),
            NestedField(2, "text", StringType(), required=True),
            NestedField(3, "normalized_item_id", StringType(), required=True),
            NestedField(4, "checkworthiness", DoubleType(), required=False),
            NestedField(5, "veracity_likelihood", DoubleType(), required=False),
            NestedField(6, "harm_potential", DoubleType(), required=False),
            NestedField(7, "risk_score", DoubleType(), required=False),
            NestedField(8, "status", StringType(), required=True),
            NestedField(9, "created_at", TimestampType(), required=True)
        )
        
        # Create tables with partitioning
        for table_name, schema in [
            ("raw_items", raw_items_schema),
            ("normalized_items", normalized_items_schema),
            ("claims", claims_schema)
        ]:
            full_name = f"{self.namespace}.{table_name}"
            if full_name not in self.catalog.list_tables(self.namespace):
                self.catalog.create_table(
                    identifier=full_name,
                    schema=schema,
                    partition_spec={"day": "day(timestamp)"}  # Partition by day
                )
                observability_service.log_info(f"Created Iceberg table: {full_name}")
    
    async def write_raw_items(self, items: List[Dict[str, Any]]):
        """Write raw items to Iceberg"""
        try:
            table = self.catalog.load_table(f"{self.namespace}.raw_items")
            # Convert dictionaries to PyArrow records
            # In production, use proper PyArrow conversion
            observability_service.log_info(f"Writing {len(items)} raw items to Iceberg")
            # table.append(...) would go here with PyArrow records
        except Exception as e:
            observability_service.log_error(f"Failed to write to Iceberg: {e}")
    
    async def write_normalized_items(self, items: List[Dict[str, Any]]):
        """Write normalized items to Iceberg"""
        try:
            table = self.catalog.load_table(f"{self.namespace}.normalized_items")
            observability_service.log_info(f"Writing {len(items)} normalized items to Iceberg")
            # table.append(...) would go here
        except Exception as e:
            observability_service.log_error(f"Failed to write normalized items: {e}")
    
    async def write_claims(self, claims: List[Dict[str, Any]]):
        """Write claims to Iceberg"""
        try:
            table = self.catalog.load_table(f"{self.namespace}.claims")
            observability_service.log_info(f"Writing {len(claims)} claims to Iceberg")
            # table.append(...) would go here
        except Exception as e:
            observability_service.log_error(f"Failed to write claims: {e}")
    
    async def query_items_by_date(
        self,
        start_date: datetime,
        end_date: datetime,
        table_name: str = "normalized_items"
    ) -> List[Dict[str, Any]]:
        """Query items by date range"""
        try:
            table = self.catalog.load_table(f"{self.namespace}.{table_name}")
            # In production, use DuckDB or Spark to query Iceberg
            # scan = table.scan(
            #     row_filter=f"timestamp >= {start_date} AND timestamp < {end_date}"
            # )
            observability_service.log_info(f"Querying {table_name} from {start_date} to {end_date}")
            return []  # Placeholder
        except Exception as e:
            observability_service.log_error(f"Failed to query Iceberg: {e}")
            return []

# Singleton instance (note: Iceberg is optional, can fail gracefully)
try:
    iceberg_service = IcebergService()
except Exception as e:
    observability_service.log_warning(f"Iceberg not available: {e}")
    iceberg_service = None
