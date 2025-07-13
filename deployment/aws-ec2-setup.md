# AWS EC2 Deployment Guide

## Prerequisites

1. **AWS EC2 Instance** with at least:
   - 1 vCPU, 1GB RAM (t2.micro is sufficient for testing)
   - Ubuntu 20.04 LTS or newer
   - Security group allowing inbound traffic on ports 80 and 443 (and 22 for SSH)

2. **Domain name** pointed to your EC2 instance (required for SSL)

3. **Docker installed** on the EC2 instance

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

# Update email in docker-compose.yml for SSL certificate
sed -i 's/your-email@example.com/your-actual-email@domain.com/g' docker-compose.yml

# For AWS/Production deployment with SSL (Recommended)
make docker-compose-aws

# For local development only
make docker-compose-local
```

### 4. Setup SSL Certificate (Production)
```bash
# Generate SSL certificate (run once after deployment)
make ssl-setup

# Your site will be available at https://your-domain.com
```

### 5. Access the Application
- **Production (with SSL)**: `https://your-domain.com`
- **Local development**: `http://your-ec2-public-ip:8501`
- **HTTP access**: Automatically redirects to HTTPS

## Deployment Options

### Option 1: AWS/Production with SSL (Recommended)
Includes nginx reverse proxy with automatic HTTPS redirect:

```bash
# Deploy with SSL support
make docker-compose-aws

# Setup SSL certificate (run once)
make ssl-setup
```

### Option 2: Local Development
Direct access without SSL for testing:

```bash
# Local development mode
make docker-compose-local
```

## AWS Security Group Configuration

Ensure your EC2 security group has the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP traffic (redirects to HTTPS) |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS traffic (SSL) |
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlit (local dev only) |
| SSH | TCP | 22 | Your IP | SSH access |

## Production Considerations

### 1. SSL Certificate Management
The setup includes automatic SSL certificate generation and renewal:

```bash
# Initial SSL setup (run once)
make ssl-setup

# Renew certificates (set up as cron job)
make ssl-renew
```

**Automatic Renewal**: Add to crontab for automatic certificate renewal:
```bash
# Renew certificates monthly
echo "0 0 1 * * cd /home/ubuntu/dv_website_streamlit_minimal && make ssl-renew" | crontab -
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
# For production deployment with SSL
echo "@reboot cd /home/ubuntu/dv_website_streamlit_minimal && make docker-compose-aws" | crontab -

# For local development
echo "@reboot cd /home/ubuntu/dv_website_streamlit_minimal && make docker-compose-local" | crontab -
```

## Troubleshooting

### Common Issues:

1. **SSL certificate generation fails**
   - Ensure domain points to your server IP
   - Check DNS propagation: `nslookup your-domain.com`
   - Verify port 80 is accessible for Let's Encrypt validation

2. **HTTPS not working**
   - Check nginx container is running: `docker ps`
   - Verify SSL certificates exist: `docker exec nginx ls -la /etc/letsencrypt/live/`
   - Check nginx logs: `docker logs <nginx-container>`

3. **Port 8501 not accessible (local dev)**
   - Check security group settings
   - Verify container is running: `docker ps`

4. **Container fails to start**
   - Check logs: `make docker-logs`
   - Verify Docker daemon is running: `sudo systemctl status docker`

5. **Permission issues**
   - Ensure user is in docker group: `groups $USER`
   - Check file permissions in project directory

### Useful Commands:

```bash
# Check if application is responding (HTTPS)
curl -f https://your-domain.com/_stcore/health

# Check if application is responding (local)
curl -f http://localhost:8501/_stcore/health

# View all containers
docker ps -a

# Check SSL certificate status
docker exec nginx openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# View nginx logs
docker logs <nginx-container-name>

# Remove all containers and start fresh
make docker-clean
make docker-build
make docker-compose-aws
```

## Cost Optimization

- Use **t2.micro** for development/testing (free tier eligible)
- Consider **t3.small** for light production workloads
- Use **Elastic IP** if you need a static IP address
- Set up **CloudWatch monitoring** for resource optimization