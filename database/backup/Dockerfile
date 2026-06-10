# FleetMaster PostgreSQL Backup Service
# Production-ready backup container

FROM postgres:15-alpine

LABEL maintainer="FleetMaster <dev@fleetmaster.com>"
LABEL version="1.0.0"
LABEL description="Automated PostgreSQL backup system"

# Install required packages
RUN apk add --no-cache \
    bash \
    curl \
    jq \
    gzip \
    lz4 \
    zstd \
    python3 \
    py3-pip \
    aws-cli \
    && rm -rf /var/cache/apk/*

# Create directories
RUN mkdir -p /backups/postgresql/{daily,weekly,monthly,yearly,metadata} \
    /var/log/postgresql-backup \
    /etc/fleetmaster

# Copy scripts
COPY scripts/ /usr/local/bin/
COPY config/ /etc/fleetmaster/backup/

# Make scripts executable
RUN chmod +x /usr/local/bin/*.sh

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m \
    CMD /usr/local/bin/health_check.sh all || exit 1

# Default environment
ENV BACKUP_DIR=/backups/postgresql \
    LOG_DIR=/var/log/postgresql-backup \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_NAME=fleetmaster_db \
    DB_USER=postgres \
    COMPRESSION=gzip \
    RETENTION_DAILY=7 \
    RETENTION_WEEKLY=30 \
    RETENTION_MONTHLY=90

# Run backup service
CMD ["/usr/local/bin/backup.sh"]
