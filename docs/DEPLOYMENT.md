# FleetMaster Deployment Guide

## Prerequisites

- Docker and Docker Compose
- PostgreSQL database
- AWS Account (for S3 bucket)
- Google Maps API key
- SSL certificates (for production)

## Local Development

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/vishnuprasad3004/fleetmaster-app.git
cd fleetmaster-app

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration

# Start services
docker-compose up -d

# Initialize database
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Backend: http://localhost:8000
# Web: http://localhost:5000
```

## Production Deployment

### AWS Deployment

#### 1. Prepare EC2 Instance

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/vishnuprasad3004/fleetmaster-app.git
cd fleetmaster-app
```

#### 3. Configure Production Environment

```bash
sudo cp .env.example .env.production
sudo nano .env.production

# Set production values:
# - DATABASE_URL with RDS endpoint
# - AWS credentials for S3
# - Google Maps API key
# - JWT_SECRET_KEY (generate strong key)
```

#### 4. Build and Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose ps
```

### Database Setup

#### AWS RDS PostgreSQL

1. Create RDS instance
2. Configure security group
3. Note endpoint and credentials
4. Update DATABASE_URL in .env

```bash
# Run migrations
docker-compose exec backend python manage.py migrate
```

### SSL Configuration

#### Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d fleetmaster.com

# Update Nginx configuration with SSL
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend
docker-compose logs -f web
```

### Backup Strategy

```bash
# Backup database
PGDUMP_ARGS="-h $DB_HOST -U $DB_USER -d $DB_NAME"
dump=$(pg_dump $PGDUMP_ARGS | gzip)
aws s3 cp - s3://backup-bucket/fleetmaster-$(date +%Y%m%d).sql.gz
```

### Performance Optimization

1. Enable Redis caching
2. Configure CDN for static files
3. Optimize database queries
4. Use connection pooling
5. Enable gzip compression

## Scaling

### Horizontal Scaling

```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Use load balancer (AWS ELB or Nginx)
```

### Database Scaling

- Use read replicas for read-heavy operations
- Implement sharding for large datasets
- Archive old tracking data

## Troubleshooting

### Common Issues

#### Containers won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database connection errors
```bash
# Verify connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

#### API rate limiting
- Implement throttling
- Use Redis for rate limiting
- Configure nginx `limit_req`

## Support

For deployment issues, contact support@fleetmaster.app or open a GitHub issue.