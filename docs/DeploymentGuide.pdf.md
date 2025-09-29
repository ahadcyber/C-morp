# C-MORP Deployment Guide
**Production Deployment & Operations Manual**  
*Smart India Hackathon 2025*

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-deployment Checklist](#pre-deployment-checklist)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Security Hardening](#security-hardening)
6. [High Availability Setup](#high-availability-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## System Requirements

### Minimum Production Requirements

**Hardware:**
- CPU: 4 cores (8 recommended)
- RAM: 8GB (16GB recommended)
- Storage: 100GB SSD (500GB recommended)
- Network: 100 Mbps (1 Gbps recommended)

**Operating System:**
- Ubuntu 20.04 LTS or 22.04 LTS
- Debian 11 or later
- RHEL 8+ / CentOS 8+ (with adjustments)

**Software Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.9+
- PostgreSQL 15+ (containerized or external)

### Recommended Production Setup

```
┌─────────────────────────────────────────┐
│  Load Balancer (Nginx/HAProxy)         │
│  SSL Termination                        │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────┐         ┌────▼────┐
│ App     │         │ App     │
│ Server  │         │ Server  │
│ Node 1  │         │ Node 2  │
└────┬────┘         └────┬────┘
     │                   │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │  Database Cluster │
     │  PostgreSQL HA    │
     └───────────────────┘
```

---

## Pre-deployment Checklist

### Planning Phase

- [ ] Campus load profile analysis completed
- [ ] Renewable energy capacity documented
- [ ] Battery storage specifications confirmed
- [ ] Network topology mapped
- [ ] Security requirements defined
- [ ] Backup strategy planned
- [ ] Disaster recovery plan created

### Infrastructure Phase

- [ ] Server hardware provisioned
- [ ] Network connectivity verified
- [ ] Firewall rules configured
- [ ] SSL certificates obtained
- [ ] DNS records configured
- [ ] Monitoring tools selected
- [ ] Backup storage allocated

### Software Phase

- [ ] Docker installed and tested
- [ ] Database server ready
- [ ] Redis cache configured
- [ ] MQTT broker set up
- [ ] Time synchronization (NTP) configured
- [ ] Log aggregation configured

---

## Installation Methods

### Method 1: Automated Installation (Recommended)

**For new deployments:**

```bash
# 1. Clone repository
git clone https://github.com/your-org/c-morp.git
cd c-morp

# 2. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 3. Run installer
sudo bash install.sh --production

# 4. Verify installation
curl http://localhost:8080/health
```

**Installation flags:**
- `--production` - Enables production optimizations
- `--ssl` - Configures SSL certificates
- `--external-db` - Uses external PostgreSQL
- `--ha` - High availability mode

### Method 2: Manual Installation

**Step-by-step manual deployment:**

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Create application user
sudo useradd -r -s /bin/false cmorp
sudo mkdir -p /opt/cmorp
sudo chown cmorp:cmorp /opt/cmorp

# 4. Clone and configure
cd /opt/cmorp
git clone https://github.com/your-org/c-morp.git .
cp .env.example .env

# 5. Generate secrets
openssl rand -hex 32 > /opt/cmorp/.secrets/db_password
openssl rand -hex 32 > /opt/cmorp/.secrets/redis_password
openssl rand -hex 32 > /opt/cmorp/.secrets/jwt_secret

# 6. Build and start services
docker-compose -f docker/compose.yml build
docker-compose -f docker/compose.yml up -d

# 7. Initialize database
docker exec cmorp_postgres psql -U cmorp_user -d microgrid_db -f /opt/cmorp/sql/init.sql

# 8. Run health checks
docker-compose ps
curl http://localhost:8080/health
```

### Method 3: Kubernetes Deployment

```bash
# 1. Create namespace
kubectl create namespace cmorp-prod

# 2. Create secrets
kubectl create secret generic cmorp-secrets \
  --from-literal=db-password=$(openssl rand -hex 32) \
  --from-literal=redis-password=$(openssl rand -hex 32) \
  -n cmorp-prod

# 3. Deploy using Helm
helm install cmorp ./helm/cmorp \
  --namespace cmorp-prod \
  --values values-production.yaml

# 4. Verify deployment
kubectl get pods -n cmorp-prod
kubectl get svc -n cmorp-prod
```

---

## Configuration

### Environment Variables

**Critical Configuration (.env):**

```bash
# ======================================
# PRODUCTION CONFIGURATION
# ======================================

# Application
APP_ENV=production
APP_DEBUG=false
APP_LOG_LEVEL=info
APP_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Database
DATABASE_URL=postgresql://cmorp_user:${DB_PASSWORD}@postgres:5432/microgrid_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_SSL_MODE=require

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_MAX_CONNECTIONS=50

# MQTT Broker
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=cmorp_mqtt
MQTT_PASSWORD=${MQTT_PASSWORD}
MQTT_TLS=true

# Security
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
CORS_ORIGINS=https://yourdomain.com
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=60

# Grid Configuration
GRID_CARBON_INTENSITY=0.71  # kg CO2/kWh for India
PEAK_TARIFF=10.50          # ₹/kWh
OFF_PEAK_TARIFF=6.00       # ₹/kWh
SHOULDER_TARIFF=8.00       # ₹/kWh

# Battery Configuration
BATTERY_CAPACITY=500       # kWh
BATTERY_MAX_POWER=100      # kW
BATTERY_MIN_SOC=20         # %
BATTERY_MAX_SOC=80         # %
BATTERY_EFFICIENCY=0.95

# Solar Configuration
SOLAR_CAPACITY=200         # kWp
SOLAR_EFFICIENCY=0.98

# Optimization
SOLVER_TIMEOUT=300         # seconds
OPTIMIZATION_HORIZON=24    # hours
SOLVER_THREADS=4

# Alerts
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WEBHOOK
WHATSAPP_API_KEY=${WHATSAPP_KEY}
WHATSAPP_PHONE_ID=${WHATSAPP_PHONE_ID}
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=alerts@cmorp.io

# Monitoring
GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
ENABLE_METRICS=true
METRICS_PORT=9090

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 2 AM daily
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=cmorp-backups
```

### Device Configuration

**plugins/devices.json:**

```json
{
  "devices": [
    {
      "id": "solar_inv_001",
      "type": "solar_inverter",
      "protocol": "modbus_tcp",
      "config": {
        "ip": "192.168.1.100",
        "port": 502,
        "unit_id": 1,
        "capacity_kw": 200,
        "poll_interval": 5
      }
    },
    {
      "id": "bess_001",
      "type": "battery",
      "protocol": "modbus_tcp",
      "config": {
        "ip": "192.168.1.101",
        "port": 502,
        "unit_id": 2,
        "capacity_kwh": 500,
        "max_power_kw": 100,
        "poll_interval": 2
      }
    },
    {
      "id": "meter_main",
      "type": "smart_meter",
      "protocol": "mqtt",
      "config": {
        "topic": "cmorp/meters/main",
        "qos": 1
      }
    }
  ]
}
```

---

## Security Hardening

### SSL/TLS Configuration

**1. Obtain SSL Certificate:**

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d cmorp.yourdomain.com
```

**2. Configure Nginx for SSL:**

```nginx
server {
    listen 443 ssl http2;
    server_name cmorp.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/cmorp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cmorp.yourdomain.com/privkey.pem;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Additional security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Rules

```bash
# UFW Configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Rate limiting for SSH
sudo ufw limit 22/tcp
```

### Database Security

```sql
-- Create read-only user for reporting
CREATE USER cmorp_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE microgrid_db TO cmorp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cmorp_readonly;

-- Revoke unnecessary privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE microgrid_db FROM PUBLIC;

-- Enable SSL connections
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server-cert.pem';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server-key.pem';
```

---

## High Availability Setup

### Database Replication

**Primary Server:**
```bash
# Configure PostgreSQL primary
sudo -u postgres psql
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET wal_keep_size = '1GB';
```

**Replica Server:**
```bash
# Set up streaming replication
pg_basebackup -h primary_server -D /var/lib/postgresql/15/main -U replication -P -v -R
```

### Load Balancing

**HAProxy Configuration:**
```
frontend cmorp_frontend
    bind *:443 ssl crt /etc/ssl/cmorp.pem
    default_backend cmorp_backend

backend cmorp_backend
    balance roundrobin
    option httpchk GET /health
    server app1 10.0.1.10:8080 check
    server app2 10.0.1.11:8080 check backup
```

---

## Monitoring & Logging

### Prometheus Metrics

**prometheus.yml:**
```yaml
scrape_configs:
  - job_name: 'cmorp'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

### Log Aggregation

**Using ELK Stack:**
```bash
# Install Filebeat
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.0.0-amd64.deb
sudo dpkg -i filebeat-8.0.0-amd64.deb

# Configure Filebeat
sudo nano /etc/filebeat/filebeat.yml
sudo systemctl enable filebeat
sudo systemctl start filebeat
```

### Grafana Dashboards

Access: `https://cmorp.yourdomain.com:3000`

**Key Dashboards:**
1. System Overview
2. Energy Flow Monitor
3. Optimization Performance
4. Alert History
5. Carbon Savings

---

## Backup & Recovery

### Automated Backup Script

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/cmorp"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec cmorp_postgres pg_dump -U cmorp_user microgrid_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Configuration backup
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /opt/cmorp/.env /opt/cmorp/plugins/

# Upload to S3
aws s3 cp "$BACKUP_DIR/" s3://cmorp-backups/ --recursive

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
```

### Recovery Procedure

```bash
# 1. Stop services
docker-compose down

# 2. Restore database
gunzip < backup_db.sql.gz | docker exec -i cmorp_postgres psql -U cmorp_user -d microgrid_db

# 3. Restore configuration
tar -xzf config_backup.tar.gz -C /opt/cmorp/

# 4. Restart services
docker-compose up -d

# 5. Verify
curl http://localhost:8080/health
```

---

## Troubleshooting

### Common Issues

**Issue: Containers won't start**
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

**Issue: Database connection refused**
```bash
# Check PostgreSQL status
docker exec cmorp_postgres pg_isready

# Check network
docker network inspect cmorp_network

# Verify credentials
docker exec cmorp_postgres psql -U cmorp_user -d microgrid_db -c "SELECT 1"
```

**Issue: Optimization fails**
```bash
# Check solver logs
docker logs cmorp_solver

# Verify constraints
python3 src/guard_rail.py --validate

# Test solver manually
docker exec cmorp_solver python3 -c "import pulp; print(pulp.PULP_CBC_CMD().available())"
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- [ ] Review system logs
- [ ] Check alert history
- [ ] Verify backup completion
- [ ] Monitor disk usage

**Weekly:**
- [ ] Review optimization performance
- [ ] Analyze user feedback
- [ ] Check for security updates
- [ ] Test failover procedures

**Monthly:**
- [ ] Update dependencies
- [ ] Review and tune configurations
- [ ] Audit access logs
- [ ] Performance optimization
- [ ] Disaster recovery drill

### Update Procedure

```bash
# 1. Backup current version
bash backup.sh

# 2. Pull latest code
git pull origin main

# 3. Review changelog
cat CHANGELOG.md

# 4. Update containers
docker-compose pull
docker-compose up -d

# 5. Run migrations
docker exec cmorp_api python3 manage.py migrate

# 6. Verify
curl http://localhost:8080/health
bash reproduce.sh
```

---

## Support & Escalation

### Support Levels

**Level 1**: Basic troubleshooting (see this guide)  
**Level 2**: Configuration issues (contact: support@cmorp.io)  
**Level 3**: Critical system failures (emergency: +91-XXXX-XXXXX)

### Performance Targets (SLA)

- System Availability: 99.5%
- Optimization Response Time: <5s
- Alert Delivery Time: <30s
- API Response Time: <100ms

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-30  
**Maintained by**: C-MORP Development Team
