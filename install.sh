#!/bin/bash
# C-MORP Installer - No IT Expertise Required
# Smart India Hackathon 2025 - Campus Microgrid Optimization Platform

set -e

echo "======================================"
echo "C-MORP Installation Wizard"
echo "Campus Microgrid Optimization Platform"
echo "======================================"
echo ""

# Color codes for better UX
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Please run with sudo: sudo bash install.sh${NC}"
    exit 1
fi

echo -e "${BLUE}[1/6] Checking system requirements...${NC}"
# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo -e "${GREEN}✓ Docker found${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}✓ Docker Compose found${NC}"
fi

echo -e "${BLUE}[2/6] Installing Python dependencies...${NC}"
if ! command -v python3 &> /dev/null; then
    apt-get update
    apt-get install -y python3 python3-pip
fi
pip3 install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo -e "${BLUE}[3/6] Setting up environment...${NC}"
# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << EOF
# C-MORP Configuration
POSTGRES_USER=cmorp_user
POSTGRES_PASSWORD=secure_password_$(openssl rand -hex 8)
POSTGRES_DB=microgrid_db
REDIS_PASSWORD=$(openssl rand -hex 16)
GRAFANA_ADMIN_PASSWORD=admin123
MQTT_BROKER=mosquitto
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WEBHOOK
WHATSAPP_API_KEY=your_whatsapp_business_api_key
EOF
    echo -e "${GREEN}✓ Environment file created${NC}"
else
    echo -e "${GREEN}✓ Environment file exists${NC}"
fi

echo -e "${BLUE}[4/6] Building Docker containers...${NC}"
cd docker
docker-compose -f compose.yml up -d --build
cd ..
echo -e "${GREEN}✓ Containers started${NC}"

echo -e "${BLUE}[5/6] Initializing database...${NC}"
sleep 5  # Wait for database to be ready
python3 src/init_db.py
echo -e "${GREEN}✓ Database initialized${NC}"

echo -e "${BLUE}[6/6] Running health checks...${NC}"
python3 tests/health_check.py
echo -e "${GREEN}✓ All systems operational${NC}"

echo ""
echo -e "${GREEN}======================================"
echo "✓ Installation Complete!"
echo "======================================${NC}"
echo ""
echo "Access the platform at: http://localhost:8080"
echo "Grafana Dashboard: http://localhost:3000 (admin/admin123)"
echo ""
echo "To run benchmarks: bash reproduce.sh"
echo ""
