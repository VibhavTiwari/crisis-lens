import clickhouse_connect
from typing import List, Dict, Any
from datetime import datetime, timedelta
from config import settings
from services.observability import observability_service

class ClickHouseService:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD
        )
        
    async def ensure_tables(self):
        """Create tables if they don't exist"""
        # Events table
        self.client.command("""
        CREATE TABLE IF NOT EXISTS crisis_events (
            event_id String,
            event_type String,
            item_id String,
            claim_id Nullable(String),
            source String,
            risk_score Float32,
            timestamp DateTime,
            metadata String
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, event_type, source)
        PARTITION BY toYYYYMM(timestamp)
        """)
        
        # Metrics table
        self.client.command("""
        CREATE TABLE IF NOT EXISTS crisis_metrics (
            metric_name String,
            metric_value Float64,
            tags String,
            timestamp DateTime
        ) ENGINE = MergeTree()
        ORDER BY (metric_name, timestamp)
        PARTITION BY toYYYYMM(timestamp)
        """)
        
        # Materialized view for hourly aggregations
        self.client.command("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_event_counts
        ENGINE = SummingMergeTree()
        ORDER BY (event_date, event_hour, event_type, source)
        AS SELECT
            toDate(timestamp) as event_date,
            toHour(timestamp) as event_hour,
            event_type,
            source,
            count() as event_count
        FROM crisis_events
        GROUP BY event_date, event_hour, event_type, source
        """)
        
        observability_service.log_info("ClickHouse tables ensured")
    
    async def record_event(
        self,
        event_type: str,
        item_id: str,
        source: str,
        risk_score: float = 0.0,
        claim_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Record an event"""
        import json
        import uuid
        
        self.client.insert(
            'crisis_events',
            [[
                str(uuid.uuid4()),
                event_type,
                item_id,
                claim_id,
                source,
                risk_score,
                datetime.utcnow(),
                json.dumps(metadata or {})
            ]]
        )
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a metric"""
        import json
        
        self.client.insert(
            'crisis_metrics',
            [[
                metric_name,
                value,
                json.dumps(tags or {}),
                datetime.utcnow()
            ]]
        )
    
    async def get_event_timeline(
        self,
        start_time: datetime,
        end_time: datetime,
        event_type: str = None
    ) -> List[Dict[str, Any]]:
        """Get event timeline"""
        where_clause = "timestamp BETWEEN %(start)s AND %(end)s"
        params = {'start': start_time, 'end': end_time}
        
        if event_type:
            where_clause += " AND event_type = %(event_type)s"
            params['event_type'] = event_type
        
        query = f"""
        SELECT
            toStartOfHour(timestamp) as hour,
            event_type,
            source,
            count() as count,
            avg(risk_score) as avg_risk
        FROM crisis_events
        WHERE {where_clause}
        GROUP BY hour, event_type, source
        ORDER BY hour DESC
        """
        
        result = self.client.query(query, parameters=params)
        return [
            {
                "hour": row[0],
                "event_type": row[1],
                "source": row[2],
                "count": row[3],
                "avg_risk": row[4]
            }
            for row in result.result_rows
        ]
    
    async def get_top_sources(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top sources by volume"""
        query = """
        SELECT
            source,
            count() as total_events,
            avg(risk_score) as avg_risk,
            max(risk_score) as max_risk
        FROM crisis_events
        WHERE timestamp >= now() - INTERVAL %(days)s DAY
        GROUP BY source
        ORDER BY total_events DESC
        LIMIT %(limit)s
        """
        
        result = self.client.query(query, parameters={'days': days, 'limit': limit})
        return [
            {
                "source": row[0],
                "total_events": row[1],
                "avg_risk": row[2],
                "max_risk": row[3]
            }
            for row in result.result_rows
        ]

# Singleton instance
clickhouse_service = ClickHouseService()
