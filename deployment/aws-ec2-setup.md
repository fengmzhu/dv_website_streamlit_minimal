# AWS EC2 Deployment Guide

## Prerequisites

1. **AWS EC2 Instance** with at least:
   - 1 vCPU, 1GB RAM (t2.micro is sufficient for testing)
   - Ubuntu 20.04 LTS or newer
   - Security group allowing inbound traffic on port 8501

2. **Docker installed** on the EC2 instance

## Quick Deployment Steps

### 1. Connect to EC2 Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 2. Install Docker (if not already installed)
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker ubuntu

# Restart session or run:
newgrp docker
```

### 3. Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/fengmzhu/dv_website_streamlit_minimal.git
cd dv_website_streamlit_minimal

# Build and run with Docker
make docker-build
make docker-run
```

### 4. Access the Application
- Open browser and navigate to: `http://your-ec2-public-ip:8501`
- The application should be running and accessible

## Alternative: Docker Compose (Recommended)

For production deployments, use Docker Compose:

```bash
# Start with Docker Compose
make docker-compose-up

# Stop the application
make docker-compose-down
```

## AWS Security Group Configuration

Ensure your EC2 security group has the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlit application |
| SSH | TCP | 22 | Your IP | SSH access |

## Production Considerations

### 1. SSL/HTTPS Setup
Consider using a reverse proxy (nginx) with SSL:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Data Persistence
The Docker setup includes volume mounts for:
- Database files: `./database:/app/database`
- Exports: `./exports:/app/exports`
- Imports: `./imports:/app/imports`

### 3. Monitoring and Logs
```bash
# View application logs
make docker-logs

# Monitor container health
docker ps

# Check resource usage
docker stats
```

### 4. Automatic Startup
To start the application automatically on EC2 reboot:

```bash
# Add to crontab
echo "@reboot cd /home/ubuntu/dv_website_streamlit_minimal && make docker-compose-up" | crontab -
```

## Troubleshooting

### Common Issues:

1. **Port 8501 not accessible**
   - Check security group settings
   - Verify container is running: `docker ps`

2. **Container fails to start**
   - Check logs: `make docker-logs`
   - Verify Docker daemon is running: `sudo systemctl status docker`

3. **Permission issues**
   - Ensure user is in docker group: `groups $USER`
   - Check file permissions in project directory

### Useful Commands:

```bash
# Check if application is responding
curl -f http://localhost:8501/_stcore/health

# View all containers
docker ps -a

# Remove all containers and start fresh
make docker-clean
make docker-build
make docker-compose-up
```

## Cost Optimization

- Use **t2.micro** for development/testing (free tier eligible)
- Consider **t3.small** for light production workloads
- Use **Elastic IP** if you need a static IP address
- Set up **CloudWatch monitoring** for resource optimization