"""
Alert Broker Service - C-MORP
Manages alerts, notifications, and escalation policies
Smart India Hackathon 2025
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import redis
import paho.mqtt.client as mqtt
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts in the system"""
    GRID_OVERLOAD = "grid_overload"
    BATTERY_LOW = "battery_low"
    EQUIPMENT_FAILURE = "equipment_failure"
    OPTIMIZATION_FAILURE = "optimization_failure"
    ANOMALY_DETECTED = "anomaly_detected"
    PEAK_DEMAND_WARNING = "peak_demand_warning"


class AlertBroker:
    """Central alert management and distribution system"""
    
    def __init__(self, redis_url: str, mqtt_broker: str, webhook_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.mqtt_client = mqtt.Client()
        self.mqtt_broker = mqtt_broker
        self.webhook_url = webhook_url
        self.alert_queue = []
        
    async def connect(self):
        """Initialize connections"""
        self.mqtt_client.connect(self.mqtt_broker, 1883, 60)
        self.mqtt_client.loop_start()
        logger.info("Alert Broker connected to MQTT")
        
    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new alert"""
        alert = {
            "id": f"alert_{datetime.now().timestamp()}",
            "type": alert_type.value,
            "severity": severity.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "status": "active",
            "acknowledged": False
        }
        
        # Store in Redis
        self.redis_client.setex(
            f"alert:{alert['id']}",
            3600,  # 1 hour TTL
            json.dumps(alert)
        )
        
        # Publish to MQTT
        self.mqtt_client.publish(
            f"cmorp/alerts/{severity.value}",
            json.dumps(alert)
        )
        
        # Escalate if critical
        if severity == AlertSeverity.CRITICAL:
            self._escalate_alert(alert)
        
        logger.info(f"Alert created: {alert['id']} - {message}")
        return alert
    
    def _escalate_alert(self, alert: Dict):
        """Escalate critical alerts to external systems"""
        try:
            # Send to webhook (Slack, Teams, etc.)
            if self.webhook_url:
                payload = {
                    "text": f"🚨 CRITICAL ALERT: {alert['message']}",
                    "attachments": [{
                        "color": "danger",
                        "fields": [
                            {"title": "Type", "value": alert['type'], "short": True},
                            {"title": "Time", "value": alert['timestamp'], "short": True}
                        ]
                    }]
                }
                requests.post(self.webhook_url, json=payload, timeout=5)
                logger.info(f"Alert escalated via webhook: {alert['id']}")
                
        except Exception as e:
            logger.error(f"Failed to escalate alert: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert"""
        alert_key = f"alert:{alert_id}"
        alert_data = self.redis_client.get(alert_key)
        
        if alert_data:
            alert = json.loads(alert_data)
            alert['acknowledged'] = True
            alert['acknowledged_by'] = user
            alert['acknowledged_at'] = datetime.now().isoformat()
            
            self.redis_client.setex(alert_key, 3600, json.dumps(alert))
            logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict]:
        """Retrieve active alerts, optionally filtered by severity"""
        alerts = []
        for key in self.redis_client.scan_iter("alert:*"):
            alert_data = self.redis_client.get(key)
            if alert_data:
                alert = json.loads(alert_data)
                if not severity or alert['severity'] == severity.value:
                    if alert['status'] == 'active':
                        alerts.append(alert)
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        alert_key = f"alert:{alert_id}"
        alert_data = self.redis_client.get(alert_key)
        
        if alert_data:
            alert = json.loads(alert_data)
            alert['status'] = 'resolved'
            alert['resolved_at'] = datetime.now().isoformat()
            
            self.redis_client.setex(alert_key, 3600, json.dumps(alert))
            logger.info(f"Alert {alert_id} resolved")
            return True
        return False


# Example usage for benchmarking
async def run_alert_benchmark():
    """Benchmark test for alert system"""
    broker = AlertBroker(
        redis_url="redis://:redis_pass@localhost:6379",
        mqtt_broker="localhost",
        webhook_url="https://hooks.slack.com/services/YOUR_WEBHOOK"
    )
    
    await broker.connect()
    
    # Create sample alerts
    alerts = [
        (AlertType.BATTERY_LOW, AlertSeverity.MEDIUM, "Battery SOC below 30%"),
        (AlertType.PEAK_DEMAND_WARNING, AlertSeverity.HIGH, "Peak demand in 15 minutes"),
        (AlertType.GRID_OVERLOAD, AlertSeverity.CRITICAL, "Grid capacity exceeded"),
    ]
    
    for alert_type, severity, message in alerts:
        broker.create_alert(alert_type, severity, message)
        await asyncio.sleep(0.1)
    
    # Get active alerts
    active = broker.get_active_alerts()
    logger.info(f"Active alerts: {len(active)}")
    
    return len(active)


if __name__ == "__main__":
    asyncio.run(run_alert_benchmark())
