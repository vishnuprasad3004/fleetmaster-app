#!/bin/bash
# FleetMaster PostgreSQL Backup Health Monitoring
# Version: 1.0.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config/backup.conf"

[[ -f "$CONFIG_FILE" ]] && source <(grep -v '^#' "$CONFIG_FILE" | sed 's/\${\([^}]*\):-\([^}]*\)}/\2/g')

BACKUP_DIR="${BACKUP_DIR:-/backups/postgresql}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-fleetmaster_db}"
DB_USER="${DB_USER:-postgres}"

# Check backup freshness
check_backup_freshness() {
    local max_age_hours="${1:-26}"
    local latest_backup
    latest_backup=$(find "${BACKUP_DIR}"/{daily,weekly} -name "*.backup.*" -type f 2>/dev/null | sort -r | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        echo "CRITICAL: No backups found"
        return 2
    fi
    
    local age_seconds=$(( $(date +%s) - $(stat -f%m "$latest_backup" 2>/dev/null || stat -c%Y "$latest_backup") ))
    local age_hours=$(( age_seconds / 3600 ))
    
    if [[ $age_hours -gt $max_age_hours ]]; then
        echo "CRITICAL: Latest backup is ${age_hours}h old (threshold: ${max_age_hours}h)"
        return 2
    fi
    echo "OK: Latest backup is ${age_hours}h old"
    return 0
}

# Check backup size
check_backup_size() {
    local min_size_mb="${1:-10}"
    local latest_backup
    latest_backup=$(find "${BACKUP_DIR}"/{daily,weekly} -name "*.backup.*" -type f 2>/dev/null | sort -r | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        echo "CRITICAL: No backup found"
        return 2
    fi
    
    local size_mb=$(( $(stat -f%z "$latest_backup" 2>/dev/null || stat -c%s "$latest_backup") / 1024 / 1024 ))
    
    if [[ $size_mb -lt $min_size_mb ]]; then
        echo "WARNING: Backup size ${size_mb}MB below minimum ${min_size_mb}MB"
        return 1
    fi
    echo "OK: Backup size is ${size_mb}MB"
    return 0
}

# Check backup integrity
check_backup_integrity() {
    local latest_backup
    latest_backup=$(find "${BACKUP_DIR}"/{daily,weekly} -name "*.backup.*" -type f 2>/dev/null | sort -r | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        echo "CRITICAL: No backup found"
        return 2
    fi
    
    local test_file="$latest_backup"
    [[ "$latest_backup" == *.gz ]] && { test_file=$(mktemp); gunzip -c "$latest_backup" > "$test_file"; }
    
    export PGPASSWORD="${DB_PASSWORD:-}"
    if pg_restore --list "$test_file" > /dev/null 2>&1; then
        [[ "$test_file" != "$latest_backup" ]] && rm -f "$test_file"
        echo "OK: Backup integrity verified"
        return 0
    fi
    [[ "$test_file" != "$latest_backup" ]] && rm -f "$test_file"
    echo "CRITICAL: Backup integrity check failed"
    return 2
}

# Check database connection
check_database_connection() {
    export PGPASSWORD="${DB_PASSWORD:-}"
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
        echo "OK: Database connection successful"
        return 0
    fi
    echo "CRITICAL: Cannot connect to database"
    return 2
}

# Check disk space
check_disk_space() {
    local threshold="${1:-90}"
    local usage
    usage=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $5}' | tr -d '%')
    
    if [[ $usage -gt $threshold ]]; then
        echo "CRITICAL: Disk usage ${usage}% exceeds threshold ${threshold}%"
        return 2
    fi
    echo "OK: Disk usage is ${usage}%"
    return 0
}

# Generate metrics
generate_metrics() {
    local latest_backup
    latest_backup=$(find "${BACKUP_DIR}"/{daily,weekly} -name "*.backup.*" -type f 2>/dev/null | sort -r | head -n1)
    
    local backup_count
    backup_count=$(find "${BACKUP_DIR}"/{daily,weekly,monthly,yearly} -name "*.backup.*" -type f 2>/dev/null | wc -l)
    
    local total_size=0
    [[ -n "$latest_backup" ]] && total_size=$(stat -f%z "$latest_backup" 2>/dev/null || stat -c%s "$latest_backup")
    
    cat <<EOF
# HELP pg_backup_count Total number of backups
# TYPE pg_backup_count gauge
pg_backup_count ${backup_count}

# HELP pg_backup_size_bytes Size of latest backup in bytes
# TYPE pg_backup_size_bytes gauge
pg_backup_size_bytes ${total_size}

# HELP pg_backup_age_hours Age of latest backup in hours
# TYPE pg_backup_age_hours gauge
pg_backup_age_hours $([[ -n "$latest_backup" ]] && echo $(( ($(date +%s) - $(stat -f%m "$latest_backup" 2>/dev/null || stat -c%Y "$latest_backup")) / 3600 )) || echo "0")
EOF
}

# Run all checks
run_all_checks() {
    local overall_status=0
    
    echo "=== FleetMaster PostgreSQL Backup Health Check ==="
    echo "Timestamp: $(date)"
    echo ""
    
    check_database_connection || overall_status=1
    check_backup_freshness || overall_status=1
    check_backup_size || overall_status=1
    check_backup_integrity || overall_status=1
    check_disk_space || overall_status=1
    
    echo ""
    echo "Overall Status: $([[ $overall_status -eq 0 ]] && echo "HEALTHY" || echo "UNHEALTHY")"
    
    return $overall_status
}

# CLI interface
case "${1:-all}" in
    freshness) check_backup_freshness "${2:-26}" ;;
    size) check_backup_size "${2:-10}" ;;
    integrity) check_backup_integrity ;;
    connection) check_database_connection ;;
    disk) check_disk_space "${2:-90}" ;;
    metrics) generate_metrics ;;
    all|"") run_all_checks ;;
    *)
        echo "Usage: $0 [freshness|size|integrity|connection|disk|metrics|all]"
        exit 1
        ;;
esac
