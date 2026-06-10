#!/usr/bin/env python3
"""
FleetMaster PostgreSQL Backup Service
HTTP API for backup management and monitoring
"""

import os
import json
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
BACKUP_COUNT = Counter('pg_backup_total', 'Total number of backups', ['type', 'status'])
BACKUP_SIZE = Gauge('pg_backup_size_bytes', 'Size of latest backup in bytes')
BACKUP_AGE = Gauge('pg_backup_age_hours', 'Age of latest backup in hours')
BACKUP_DURATION = Histogram('pg_backup_duration_seconds', 'Backup duration in seconds')
BACKUP_ERRORS = Counter('pg_backup_errors_total', 'Total backup errors')
RESTORE_TEST_COUNT = Counter('pg_restore_test_total', 'Total restore tests', ['status'])

# Configuration
BACKUP_DIR = os.getenv('BACKUP_DIR', '/backups/postgresql')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'fleetmaster_db')
HEALTH_PORT = int(os.getenv('HEALTH_PORT', '9090'))

# Background tasks
backup_lock = threading.Lock()
restore_lock = threading.Lock()
last_backup_status = {'status': 'none', 'timestamp': None}

def run_script(script_name):
    """Run a backup script and return the result."""
    try:
        result = subprocess.run(
            [f'/usr/local/bin/{script_name}'],
            capture_output=True,
            text=True,
            timeout=7200
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        BACKUP_ERRORS.inc()
        return {'success': False, 'error': 'Script timed out'}
    except Exception as e:
        BACKUP_ERRORS.inc()
        return {'success': False, 'error': str(e)}

def get_backup_metrics():
    """Get current backup metrics."""
    import glob
    import pathlib
    
    backups = {
        'daily': [],
        'weekly': [],
        'monthly': [],
        'yearly': []
    }
    
    for backup_type in backups.keys():
        pattern = f"{BACKUP_DIR}/{backup_type}/*.backup.*"
        files = glob.glob(pattern)
        for f in files:
            stat = pathlib.Path(f).stat()
            backups[backup_type].append({
                'file': os.path.basename(f),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return backups

def update_prometheus_metrics():
    """Update Prometheus metrics from backup status."""
    import glob
    import pathlib
    
    # Find latest backup
    latest = None
    for backup_type in ['daily', 'weekly', 'monthly', 'yearly']:
        pattern = f"{BACKUP_DIR}/{backup_type}/*.backup.*"
        files = glob.glob(pattern)
        for f in files:
            if latest is None or pathlib.Path(f).stat().st_mtime > pathlib.Path(latest).stat().st_mtime:
                latest = f
    
    if latest:
        stat = pathlib.Path(latest).stat()
        BACKUP_SIZE.set(stat.st_size)
        age_hours = (time.time() - stat.st_mtime) / 3600
        BACKUP_AGE.set(age_hours)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        result = subprocess.run(
            ['psql', '-h', DB_HOST, '-p', DB_PORT, '-U', os.getenv('DB_USER', 'postgres'),
             '-d', DB_NAME, '-c', 'SELECT 1'],
            capture_output=True,
            timeout=10
        )
        db_healthy = result.returncode == 0
    except:
        db_healthy = False
    
    # Check backup freshness
    backups = get_backup_metrics()
    latest_backup = None
    for backup_type in ['daily', 'weekly']:
        if backups[backup_type]:
            latest_backup = backups[backup_type][0]
            break
    
    healthy = db_healthy and latest_backup is not None
    
    return jsonify({
        'status': 'healthy' if healthy else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': 'healthy' if db_healthy else 'unhealthy',
            'backups': 'healthy' if latest_backup else 'unhealthy'
        },
        'latest_backup': latest_backup
    }), 200 if healthy else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint."""
    update_prometheus_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/backups', methods=['GET'])
def list_backups():
    """List all backups."""
    backups = get_backup_metrics()
    return jsonify({
        'status': 'success',
        'data': backups,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/trigger/backup', methods=['POST'])
def trigger_backup():
    """Trigger a manual backup."""
    if backup_lock.locked():
        return jsonify({
            'status': 'error',
            'message': 'Backup already in progress'
        }), 409
    
    def run_backup():
        with backup_lock:
            global last_backup_status
            with BACKUP_DURATION.time():
                result = run_script('backup.sh')
                last_backup_status = {
                    'status': 'success' if result['success'] else 'failed',
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': result
                }
                BACKUP_COUNT.labels(type='manual', status='success' if result['success'] else 'failed').inc()
    
    thread = threading.Thread(target=run_backup)
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Backup started',
        'timestamp': datetime.utcnow().isoformat()
    }), 202

@app.route('/trigger/test', methods=['POST'])
def trigger_restore_test():
    """Trigger a restore test."""
    if restore_lock.locked():
        return jsonify({
            'status': 'error',
            'message': 'Restore test already in progress'
        }), 409
    
    def run_test():
        with restore_lock:
            result = run_script('restore.sh test')
            status = 'success' if result['success'] else 'failed'
            RESTORE_TEST_COUNT.labels(status=status).inc()
    
    thread = threading.Thread(target=run_test)
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Restore test started',
        'timestamp': datetime.utcnow().isoformat()
    }), 202

@app.route('/status', methods=['GET'])
def backup_status():
    """Get last backup status."""
    return jsonify({
        'status': 'success',
        'last_backup': last_backup_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/restore', methods=['POST'])
def restore_backup():
    """Restore from a backup."""
    data = request.get_json()
    backup_file = data.get('backup_file')
    target_db = data.get('target_db', DB_NAME)
    create_db = data.get('create_db', False)
    
    if not backup_file:
        return jsonify({
            'status': 'error',
            'message': 'backup_file is required'
        }), 400
    
    if restore_lock.locked():
        return jsonify({
            'status': 'error',
            'message': 'Restore already in progress'
        }), 409
    
    def run_restore():
        with restore_lock:
            cmd = ['restore.sh', 'restore', backup_file, target_db]
            if create_db:
                cmd.append('--create')
            subprocess.run(cmd)
    
    thread = threading.Thread(target=run_restore)
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Restore started',
        'timestamp': datetime.utcnow().isoformat()
    }), 202

if __name__ == '__main__':
    logger.info(f"Starting FleetMaster Backup Service on port {HEALTH_PORT}")
    app.run(host='0.0.0.0', port=HEALTH_PORT, threaded=True)
