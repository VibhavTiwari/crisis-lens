import logging
import sys
from typing import Dict, Any

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class ObservabilityService:
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(service_name)
        self.metrics: Dict[str, Any] = {}

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def increment_counter(self, metric_name: str, value: int = 1):
        """
        Stub for metric increment (e.g., Prometheus/StatsD).
        """
        current = self.metrics.get(metric_name, 0)
        self.metrics[metric_name] = current + value
        # In a real app, this would send to a metrics backend

    def record_gauge(self, metric_name: str, value: float):
        """
        Stub for recording a gauge value.
        """
        self.metrics[metric_name] = value

observability_service = ObservabilityService("CrisisLens")
