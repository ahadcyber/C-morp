# C-MORP API Documentation
**RESTful API Reference**  
*Smart India Hackathon 2025*

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Core Endpoints](#core-endpoints)
4. [Energy Management](#energy-management)
5. [Optimization](#optimization)
6. [Alerts & Notifications](#alerts--notifications)
7. [Carbon Reporting](#carbon-reporting)
8. [User Feedback](#user-feedback)
9. [Device Management](#device-management)
10. [WebSocket API](#websocket-api)
11. [Error Codes](#error-codes)

---

## Overview

### Base URL

```
Production:  https://cmorp.yourdomain.com/api/v1
Development: http://localhost:5000/api/v1
```

### API Versioning

The API uses URL versioning. Current version: `v1`

### Response Format

All responses are in JSON format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Success",
  "timestamp": "2025-09-30T03:28:41+05:30"
}
```

### Rate Limiting

- **Free tier**: 60 requests/minute
- **Authenticated**: 300 requests/minute
- **Enterprise**: 1000 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1698765432
```

---

## Authentication

### JWT Token Authentication

**Obtain Token:**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Using Token:**

```http
GET /api/v1/metrics/current
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Keys (Alternative)

For service-to-service communication:

```http
GET /api/v1/metrics/current
X-API-Key: your_api_key_here
```

---

## Core Endpoints

### Health Check

**GET** `/health`

Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 123456,
  "services": {
    "database": "up",
    "redis": "up",
    "mqtt": "up",
    "solver": "up"
  }
}
```

### System Info

**GET** `/api/v1/system/info`

Get system information and statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "campus_name": "IIT Delhi",
    "installation_date": "2025-01-15",
    "total_capacity": {
      "solar_kw": 200,
      "battery_kwh": 500,
      "grid_connection_kw": 600
    },
    "statistics": {
      "total_optimizations": 8532,
      "total_savings_inr": 452340,
      "total_carbon_saved_kg": 12450
    }
  }
}
```

---

## Energy Management

### Current Metrics

**GET** `/api/v1/metrics/current`

Get real-time energy metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-09-30T03:28:41+05:30",
    "solar": {
      "power_kw": 45.2,
      "energy_today_kwh": 234.5,
      "efficiency": 98.3
    },
    "battery": {
      "soc_percent": 75.5,
      "power_kw": -5.8,
      "temperature_c": 28.5,
      "health_percent": 98.0
    },
    "grid": {
      "power_kw": 95.0,
      "voltage_v": 415.2,
      "frequency_hz": 50.02,
      "cost_today_inr": 1876
    },
    "load": {
      "power_kw": 135.4,
      "power_factor": 0.95
    }
  }
}
```

### Historical Data

**GET** `/api/v1/metrics/history`

Get historical energy data.

**Query Parameters:**
- `start` - Start timestamp (ISO 8601)
- `end` - End timestamp (ISO 8601)
- `interval` - Data interval: `1min`, `5min`, `15min`, `1hour`, `1day`
- `metrics` - Comma-separated metrics: `solar,battery,grid,load`

**Example:**
```http
GET /api/v1/metrics/history?start=2025-09-29T00:00:00Z&end=2025-09-30T00:00:00Z&interval=1hour&metrics=solar,battery
```

**Response:**
```json
{
  "success": true,
  "data": {
    "interval": "1hour",
    "count": 24,
    "metrics": [
      {
        "timestamp": "2025-09-29T00:00:00Z",
        "solar_kw": 0,
        "battery_soc": 72.3
      },
      {
        "timestamp": "2025-09-29T01:00:00Z",
        "solar_kw": 0,
        "battery_soc": 70.1
      }
    ]
  }
}
```

### Energy Forecast

**GET** `/api/v1/forecast`

Get energy generation and load forecasts.

**Query Parameters:**
- `horizon` - Forecast horizon in hours (default: 24)
- `type` - Forecast type: `solar`, `load`, `all`

**Response:**
```json
{
  "success": true,
  "data": {
    "forecast_time": "2025-09-30T03:28:41+05:30",
    "horizon_hours": 24,
    "solar_forecast_kw": [0, 0, 0, 5, 15, 30, 45, 55, ...],
    "load_forecast_kw": [85, 82, 80, 78, 95, 110, 125, ...]
  }
}
```

---

## Optimization

### Run Optimization

**POST** `/api/v1/optimize`

Trigger optimization algorithm.

**Request:**
```json
{
  "horizon_hours": 24,
  "objective": "cost",  // or "carbon", "peak_shaving"
  "constraints": {
    "battery_min_soc": 20,
    "battery_max_soc": 80,
    "grid_import_limit": 500
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "optimization_id": "opt_1234567890",
    "status": "completed",
    "solve_time_ms": 234,
    "objective_value": 8450.23,
    "savings_percent": 28.5,
    "schedule": {
      "battery_power_kw": [-10, -12, -8, 5, 10, ...],
      "grid_import_kw": [85, 82, 78, 60, 55, ...]
    },
    "metrics": {
      "cost_savings_inr": 3421.50,
      "carbon_saved_kg": 124.5,
      "peak_reduction_kw": 45.2
    }
  }
}
```

### Get Optimization Status

**GET** `/api/v1/optimize/{optimization_id}`

Get status of a specific optimization.

**Response:**
```json
{
  "success": true,
  "data": {
    "optimization_id": "opt_1234567890",
    "status": "running",
    "progress_percent": 65,
    "started_at": "2025-09-30T03:28:41+05:30",
    "estimated_completion": "2025-09-30T03:28:50+05:30"
  }
}
```

### Optimization History

**GET** `/api/v1/optimize/history`

Get past optimization results.

**Query Parameters:**
- `limit` - Number of results (default: 20, max: 100)
- `status` - Filter by status: `completed`, `failed`, `running`

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 20,
    "optimizations": [
      {
        "id": "opt_1234567890",
        "timestamp": "2025-09-30T03:00:00+05:30",
        "status": "completed",
        "savings_inr": 3421.50,
        "solve_time_ms": 234
      }
    ]
  }
}
```

---

## Alerts & Notifications

### Get Active Alerts

**GET** `/api/v1/alerts`

Get all active alerts.

**Query Parameters:**
- `severity` - Filter by severity: `low`, `medium`, `high`, `critical`
- `status` - Filter by status: `active`, `acknowledged`, `resolved`

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 3,
    "alerts": [
      {
        "id": "alert_1727664521",
        "type": "battery_low",
        "severity": "medium",
        "message": "Battery SOC below 30%",
        "timestamp": "2025-09-30T03:28:41+05:30",
        "status": "active",
        "metadata": {
          "current_soc": 28.5,
          "device_id": "bess_001"
        }
      }
    ]
  }
}
```

### Create Alert

**POST** `/api/v1/alerts`

Create a new alert (admin only).

**Request:**
```json
{
  "type": "custom",
  "severity": "high",
  "message": "Maintenance required for solar inverter",
  "metadata": {
    "device_id": "solar_inv_001",
    "maintenance_type": "scheduled"
  }
}
```

### Acknowledge Alert

**POST** `/api/v1/alerts/{alert_id}/acknowledge`

Acknowledge an alert.

**Request:**
```json
{
  "user": "admin@cmorp.io",
  "notes": "Investigating the issue"
}
```

### Resolve Alert

**POST** `/api/v1/alerts/{alert_id}/resolve`

Mark alert as resolved.

**Request:**
```json
{
  "resolution": "Battery recharged to 50%",
  "resolved_by": "system"
}
```

---

## Carbon Reporting

### Daily Carbon Report

**GET** `/api/v1/carbon/daily`

Get daily carbon savings report.

**Query Parameters:**
- `date` - Date in YYYY-MM-DD format (default: today)

**Response:**
```json
{
  "success": true,
  "data": {
    "date": "2025-09-30",
    "total_carbon_saved_kg": 234.5,
    "total_renewable_generation_kwh": 1456.2,
    "average_renewable_percentage": 68.5,
    "equivalents": {
      "trees_planted": 11.2,
      "cars_off_road_days": 0.05,
      "homes_powered": 48.5
    },
    "metrics": {
      "peak_renewable_percentage": 95.2,
      "minimum_carbon_intensity": 0.12
    }
  }
}
```

### Monthly Carbon Report

**GET** `/api/v1/carbon/monthly`

Get monthly carbon report with trends.

**Query Parameters:**
- `year` - Year (default: current year)
- `month` - Month 1-12 (default: current month)

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "2025-09",
    "total_carbon_saved_kg": 6845.3,
    "total_carbon_saved_tons": 6.845,
    "total_renewable_generation_kwh": 42350.8,
    "weekly_trend": [1520.2, 1680.5, 1745.8, 1898.8],
    "environmental_impact": {
      "trees_equivalent": 325.5,
      "fuel_saved_liters": 4235.1
    },
    "cost_savings_estimate": {
      "grid_cost_avoided": 338808,
      "carbon_credit_value": 342.25
    }
  }
}
```

### Export Carbon Report

**GET** `/api/v1/carbon/export`

Export carbon report as CSV or PDF.

**Query Parameters:**
- `format` - Export format: `csv`, `pdf`, `json`
- `period` - Time period: `daily`, `weekly`, `monthly`
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

**Response:**
Returns file download with appropriate content-type.

---

## User Feedback

### Submit Feedback

**POST** `/api/v1/feedback`

Submit user feedback.

**Request:**
```json
{
  "rating": "thumbs_up",  // or "thumbs_down"
  "category": "optimization_result",
  "message": "Great cost savings!",
  "context": {
    "optimization_id": "opt_1234567890"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feedback_id": "fb_1727664521",
    "status": "received",
    "message": "Thank you for your feedback!"
  }
}
```

### Get Feedback Analytics

**GET** `/api/v1/feedback/analytics`

Get feedback analytics and statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_feedback": 1523,
    "satisfaction_rate": 87.5,
    "category_stats": {
      "optimization_result": {
        "thumbs_up": 450,
        "thumbs_down": 50,
        "total": 500
      }
    },
    "recent_feedback": [...]
  }
}
```

---

## Device Management

### List Devices

**GET** `/api/v1/devices`

Get all connected devices.

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 3,
    "devices": [
      {
        "id": "solar_inv_001",
        "type": "solar_inverter",
        "status": "online",
        "last_reading": "2025-09-30T03:28:41+05:30",
        "health": "good"
      },
      {
        "id": "bess_001",
        "type": "battery",
        "status": "online",
        "last_reading": "2025-09-30T03:28:40+05:30",
        "health": "good"
      }
    ]
  }
}
```

### Get Device Details

**GET** `/api/v1/devices/{device_id}`

Get detailed information about a specific device.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "solar_inv_001",
    "type": "solar_inverter",
    "protocol": "modbus_tcp",
    "status": "online",
    "config": {
      "ip": "192.168.1.100",
      "port": 502,
      "capacity_kw": 200
    },
    "current_data": {
      "power_output": 45.2,
      "voltage": 415.5,
      "efficiency": 98.3
    },
    "statistics": {
      "uptime_hours": 5432,
      "total_energy_kwh": 125430,
      "failures": 2
    }
  }
}
```

### Send Device Command

**POST** `/api/v1/devices/{device_id}/command`

Send control command to device.

**Request:**
```json
{
  "command": "set_power",
  "parameters": {
    "power_kw": 50
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "command_id": "cmd_1727664521",
    "status": "executed",
    "result": "Power set to 50 kW"
  }
}
```

---

## WebSocket API

### Real-time Data Stream

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('wss://cmorp.yourdomain.com/ws');

ws.onopen = () => {
  // Subscribe to channels
  ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['metrics', 'alerts', 'optimization']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

**Message Format:**
```json
{
  "channel": "metrics",
  "event": "update",
  "data": {
    "timestamp": "2025-09-30T03:28:41+05:30",
    "solar_kw": 45.2,
    "battery_soc": 75.5
  }
}
```

**Available Channels:**
- `metrics` - Real-time energy metrics
- `alerts` - Alert notifications
- `optimization` - Optimization progress
- `feedback` - User feedback events

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid value for 'horizon_hours'",
    "details": {
      "parameter": "horizon_hours",
      "value": -5,
      "expected": "positive integer"
    }
  },
  "timestamp": "2025-09-30T03:28:41+05:30"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `INVALID_TOKEN` | JWT token expired or invalid |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INVALID_PARAMETER` | Invalid request parameter |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `OPTIMIZATION_FAILED` | Optimization solver failed |
| `DEVICE_OFFLINE` | Device not responding |
| `CONSTRAINT_VIOLATION` | Safety constraint violated |

---

## SDK Examples

### Python

```python
import requests

# Initialize client
class CMORPClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def get_current_metrics(self):
        response = requests.get(
            f'{self.base_url}/metrics/current',
            headers=self.headers
        )
        return response.json()
    
    def run_optimization(self, horizon=24):
        response = requests.post(
            f'{self.base_url}/optimize',
            headers=self.headers,
            json={'horizon_hours': horizon}
        )
        return response.json()

# Usage
client = CMORPClient('http://localhost:5000/api/v1', 'your_api_key')
metrics = client.get_current_metrics()
print(f"Solar: {metrics['data']['solar']['power_kw']} kW")
```

### JavaScript

```javascript
class CMORPClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }
  
  async getCurrentMetrics() {
    const response = await fetch(`${this.baseUrl}/metrics/current`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return response.json();
  }
  
  async runOptimization(horizon = 24) {
    const response = await fetch(`${this.baseUrl}/optimize`, {
      method: 'POST',
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ horizon_hours: horizon })
    });
    return response.json();
  }
}

// Usage
const client = new CMORPClient('http://localhost:5000/api/v1', 'your_api_key');
const metrics = await client.getCurrentMetrics();
console.log(`Solar: ${metrics.data.solar.power_kw} kW`);
```

---

## Interactive API Testing

**Swagger UI**: `http://localhost:5000/api/docs`  
**ReDoc**: `http://localhost:5000/api/redoc`

---

**API Version**: 1.0  
**Last Updated**: 2025-09-30  
**Support**: api-support@cmorp.io
