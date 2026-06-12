#!/bin/bash
exec > >(tee /var/log/user-data.log) 2>&1

echo "Starting bootstrap..."

apt update -y


# Install Docker AND Docker Compose Plugin
apt install -y docker.io docker-compose-v2

# Install Git
apt install -y git

# Start and enable Docker
systemctl enable docker
systemctl start docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Clone application
cd /home/ubuntu

if [ ! -d "scalable-exam-result-platform" ]; then
git clone https://github.com/Reddysekhar8333/scalable-exam-result-platform.git
fi

cd scalable-exam-result-platform

# Create production environment file
cat > backend/.env << EOF
ENVIRONMENT=production
REDIS_HOST=redis
REDIS_PORT=6379
EOF

# Build and start containers
docker compose up -d --build

echo "Bootstrap completed successfully"
