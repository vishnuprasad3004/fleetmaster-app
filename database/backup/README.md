# FleetMaster PostgreSQL Backup System

Production-ready automated backup system for PostgreSQL with Docker support.

## Features

- **Automated Daily Backups**: Scheduled backups with configurable timing
- **Multi-tier Retention**: Daily, weekly, monthly, and yearly backup retention
- **Automatic Restore Testing**: Weekly automated restore tests to verify backup integrity
- **Health Monitoring**: Built-in health checks and Prometheus metrics
- **Docker Compatible**: Fully containerized with Docker Compose support
- **Remote Storage**: S3/GCS sync for off-site backup storage
- **Notifications**: Slack/Email alerts for backup status
- **Compression**: Support for gzip, lz4, and zstd compression

## Quick Start

### Using Docker Compose

```bash
# Start the backup system
docker-compose up -d

# Check logs
docker-compose logs -f backup

# Manual backup trigger
curl -X POST http://localhost:9090/trigger/backup

# List backups
curl http://localhost:9090/backups
```

### Manual Installation

```bash
# Install scripts
cd database/backup
chmod +x scripts/*.sh

# Run backup
./scripts/backup.sh

# List backups
./scripts/restore.sh list

# Restore from backup
./scripts/restore.sh restore /backups/daily/fleetmaster_20240115_020000.backup.gz

# Health check
./scripts/health_check.sh all
```

## Configuration

Environment variables (see `config/backup.conf`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `postgres` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `fleetmaster_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `BACKUP_DIR` | Local backup directory | `/backups/postgresql` |
| `COMPRESSION` | Compression type (gzip/lz4/zstd) | `gzip` |
| `RETENTION_DAILY` | Daily backup retention (days) | `7` |
| `RETENTION_WEEKLY` | Weekly backup retention (days) | `30` |
| `RETENTION_MONTHLY` | Monthly backup retention (days) | `90` |
| `REMOTE_BACKUP_ENABLED` | Enable S3/GCS sync | `false` |
| `S3_BUCKET` | S3 bucket name | `fleetmaster-backups` |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check status |
| `/metrics` | GET | Prometheus metrics |
| `/backups` | GET | List all backups |
| `/trigger/backup` | POST | Trigger manual backup |
| `/trigger/test` | POST | Trigger restore test |
| `/status` | GET | Last backup status |
| `/restore` | POST | Restore from backup |

## Retention Policy

Backups are organized into four tiers:

1. **Daily**: Kept for 7 days (default)
2. **Weekly**: Sunday backups kept for 30 days
3. **Monthly**: 1st of month backups kept for 90 days
4. **Yearly**: January 1st backups kept for 365 days

## Monitoring

### Prometheus Metrics

```bash
# Get metrics
curl http://localhost:9090/metrics
```

Available metrics:
- `pg_backup_total`: Total backup count
- `pg_backup_size_bytes`: Latest backup size
- `pg_backup_age_hours`: Latest backup age
- `pg_backup_duration_seconds`: Backup duration
- `pg_backup_errors_total`: Backup error count

### Grafana Dashboard

Access Grafana at `http://localhost:3000` (default: admin/admin)

### Health Checks

```bash
# All checks
./scripts/health_check.sh all

# Individual checks
./scripts/health_check.sh freshness  # Backup age
./scripts/health_check.sh size       # Backup size
./scripts/health_check.sh integrity  # Backup validation
./scripts/health_check.sh connection # Database connection
./scripts/health_check.sh disk       # Disk space
```

## Restore Operations

### List Available Backups

```bash
./scripts/restore.sh list
```

### Restore from Backup

```bash
# Restore to same database (WARNING: overwrites existing data)
./scripts/restore.sh restore /backups/daily/fleetmaster_20240115.backup.gz

# Restore to new database
./scripts/restore.sh restore /backups/daily/fleetmaster_20240115.backup.gz mydb_restore --create
```

### Automated Restore Testing

```bash
# Run restore test
./scripts/restore.sh test
```

## Production Deployment

### Requirements

- PostgreSQL 10+
- Docker & Docker Compose (for containerized deployment)
- S3/GCS bucket (optional, for remote storage)
- Slack webhook (optional, for notifications)

### Recommended Setup

```bash
# 1. Create .env file
cat > .env <<EOF
DB_PASSWORD=your-secure-password
BACKUP_TIME=02:00
REMOTE_BACKUP_ENABLED=true
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
NOTIFICATION_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/your-webhook
EOF

# 2. Start services
docker-compose up -d

# 3. Verify backup system
curl http://localhost:9090/health
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## Security

- Encrypted backups (AES-256) - enable with `ENCRYPTION_ENABLED=true`
- Secure credential handling via environment variables
- IAM roles for S3 access (recommended)
- Network isolation via Docker networks

## Troubleshooting

### Backup Fails

```bash
# Check logs
tail -f /var/log/postgresql-backup/backup_*.log

# Verify database connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Check disk space
df -h /backups/postgresql
```

### Restore Fails

```bash
# Validate backup file
./scripts/restore.sh verify /path/to/backup

# Check backup integrity
pg_restore --list backup_file
```

### Performance Issues

- Increase `PARALLEL_JOBS` for faster backups
- Use `lz4` compression for faster backup/restore
- Consider point-in-time recovery for large databases

## License

MIT License - FleetMaster Team
