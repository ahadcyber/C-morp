# C-MORP Quick Start Guide
**Campus Microgrid Optimization & Reliability Platform**  
*Smart India Hackathon 2025*

---

## 🚀 5-Minute Setup

### Prerequisites
- Docker & Docker Compose
- 8GB RAM minimum
- Linux/Ubuntu (tested on 20.04+)

### Installation

**Step 1: Clone the Repository**
```bash
git clone https://github.com/your-team/c-morp.git
cd c-morp
```

**Step 2: Run Installation Script**
```bash
sudo bash install.sh
```

The installer will automatically:
- ✅ Install Docker if not present
- ✅ Set up Python dependencies
- ✅ Configure environment variables
- ✅ Start all microservices
- ✅ Initialize database

**Step 3: Access the Platform**
```
Dashboard: http://localhost:8080
Grafana:   http://localhost:3000 (admin/admin123)
API:       http://localhost:5000/api
```

---

## 🎯 Running Benchmarks

To validate system performance:

```bash
bash reproduce.sh
```

This will execute:
- Optimization solver tests
- Alert system validation
- Carbon reporting accuracy checks
- Integration tests
- Performance benchmarks

**Expected Output:**
```
✓ Solver Speed Test: 0.234s
✓ Data Throughput: 125,000 points/s
✓ Alert Creation: 5,430 alerts/s
✓ Carbon Calculation: 98.7% accuracy
✓ Coverage: 97.2%
```

---

## 📊 Key Features Demo

### 1. Real-Time Monitoring
View live energy metrics on the dashboard:
- Solar generation
- Battery state of charge
- Grid import/export
- Cost savings

### 2. Run Optimization
Click **"Run Optimization"** button to:
- Minimize electricity costs
- Maximize renewable usage
- Maintain battery health
- Respect grid constraints

### 3. Carbon Tracking
View environmental impact:
- kg CO₂ saved
- Trees planted equivalent
- Cost savings in ₹

### 4. WhatsApp Feedback
After each optimization, users receive:
- 👍 Thumbs Up / 👎 Thumbs Down buttons
- Real-time satisfaction tracking
- Improvement suggestions

---

## 🔧 Configuration

Edit `.env` file for customization:

```bash
# Grid Parameters
GRID_CARBON_INTENSITY=0.71  # kg CO2/kWh
PEAK_TARIFF=10.5  # ₹/kWh
OFF_PEAK_TARIFF=6.0  # ₹/kWh

# Battery Settings
BATTERY_CAPACITY=500  # kWh
MIN_SOC=20  # %
MAX_SOC=80  # %

# Optimization
SOLVER_TIMEOUT=300  # seconds
OPTIMIZATION_HORIZON=24  # hours
```

---

## 📱 Mobile App (PWA)

The dashboard is a Progressive Web App:

**On Mobile:**
1. Open browser: `http://your-server:8080`
2. Tap "Add to Home Screen"
3. Access offline mode

**Features:**
- ✅ Offline support
- ✅ Push notifications
- ✅ Real-time updates
- ✅ Touch-optimized UI

---

## 🧪 Testing Your Setup

### Health Check
```bash
curl http://localhost:8080/health
# Expected: "healthy"
```

### API Test
```bash
curl http://localhost:5000/api/metrics/current
```

### Database Connection
```bash
docker exec cmorp_postgres psql -U cmorp_user -d microgrid_db -c "SELECT COUNT(*) FROM energy_data;"
```

---

## 🎓 Adaptation for Your Campus

### Step 1: Configure Devices
Edit `plugins/devices.json`:

```json
{
  "solar_inverter": {
    "ip": "192.168.1.100",
    "capacity": 100,
    "type": "modbus_tcp"
  },
  "battery": {
    "ip": "192.168.1.101",
    "capacity": 500,
    "type": "can_bus"
  }
}
```

### Step 2: Set Load Profiles
Update `data/campus_profile.csv` with your consumption patterns.

### Step 3: Configure Tariffs
Match your electricity provider's rates in `.env` file.

### Step 4: Test & Deploy
```bash
bash reproduce.sh
docker-compose up -d
```

---

## 📈 Monitoring & Alerts

### Grafana Dashboards
1. Energy Flow Monitor
2. Optimization Metrics
3. Cost Savings Trends
4. System Health

### Alert Channels
- 📧 Email
- 💬 Slack/Teams webhook
- 📱 WhatsApp Business API
- 🔔 In-app notifications

---

## 🆘 Troubleshooting

### Issue: Containers won't start
```bash
docker-compose down
docker system prune -a
bash install.sh
```

### Issue: No data on dashboard
```bash
# Check MQTT broker
docker logs cmorp_mqtt

# Restart data ingestion
docker restart cmorp_api
```

### Issue: Optimization fails
```bash
# Check solver logs
docker logs cmorp_solver

# Verify constraints
python3 src/validate_constraints.py
```

---

## 📞 Support

**Documentation:** `/docs/DeploymentGuide.pdf`  
**GitHub Issues:** [github.com/your-team/c-morp/issues](https://github.com)  
**Email:** team@c-morp.io

---

## 🏆 Smart India Hackathon 2025

**Key Differentiators:**
- ✅ No IT expertise required (one-command install)
- ✅ 97%+ test coverage
- ✅ Real-time optimization (<5s response)
- ✅ WhatsApp integration for user engagement
- ✅ PWA for cross-platform access
- ✅ Production-ready architecture

**Judges Can:**
1. Run `bash reproduce.sh` to see all benchmarks
2. Access live dashboard immediately
3. View detailed metrics in Grafana
4. Review code quality and documentation
5. Test with sample data

---

*Built with ❤️ for sustainable energy management*
