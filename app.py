"""
Demo Service for AIOps Agent Testing

This service intentionally has various issues to test the agent:
- Memory leaks
- Slow endpoints
- Random errors
- Database connection issues
"""

from flask import Flask, jsonify, request
import logging
import time
import random
import os
from datetime import datetime

app = Flask(__name__)

# Configure logging to Cloud Logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simulate memory leak
memory_leak = []

# Track request count
request_count = 0


@app.route('/')
def home():
    """Healthy endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "demo-service",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route('/api/process')
def process():
    """
    Endpoint with random errors (30% failure rate)
    Tests error detection and log analysis
    """
    global request_count
    request_count += 1
    
    logger.info(f"Processing request #{request_count}")
    
    # 30% chance of error
    if random.random() < 0.3:
        error_type = random.choice([
            "ValueError",
            "ConnectionError", 
            "TimeoutError",
            "PermissionError"
        ])
        
        logger.error(f"Request failed with {error_type}: Unable to process request")
        
        if error_type == "ValueError":
            logger.error("ValueError: Invalid input data received")
            return jsonify({"error": "Invalid data"}), 400
        elif error_type == "ConnectionError":
            logger.error("ConnectionError: Database connection refused")
            return jsonify({"error": "Database unavailable"}), 503
        elif error_type == "TimeoutError":
            logger.error("TimeoutError: Request timed out after 30s")
            return jsonify({"error": "Request timeout"}), 504
        else:
            logger.error("PermissionError: Access denied to resource")
            return jsonify({"error": "Permission denied"}), 403
    
    logger.info(f"Request #{request_count} completed successfully")
    return jsonify({
        "status": "success",
        "request_id": request_count,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/slow')
def slow_endpoint():
    """
    Intentionally slow endpoint (2-5 seconds)
    Tests performance issue detection
    """
    delay = random.uniform(2, 5)
    logger.warning(f"Slow endpoint called, sleeping for {delay:.2f}s")
    
    time.sleep(delay)
    
    logger.info("Slow endpoint completed")
    return jsonify({
        "status": "completed",
        "delay": delay,
        "message": "This endpoint is intentionally slow"
    })


@app.route('/api/memory-leak')
def memory_leak_endpoint():
    """
    Causes memory leak
    Tests resource exhaustion detection
    """
    global memory_leak
    
    # Add 1MB of data to memory
    memory_leak.append('x' * 1024 * 1024)
    
    logger.warning(f"Memory leak: {len(memory_leak)}MB allocated")
    
    if len(memory_leak) > 10:
        logger.error("Memory leak critical: Over 10MB leaked!")
    
    return jsonify({
        "status": "ok",
        "leaked_mb": len(memory_leak)
    })


@app.route('/api/crash')
def crash():
    """
    Intentionally crashes
    Tests crash detection
    """
    logger.error("CRITICAL: Application crash triggered!")
    logger.error("NullPointerException: Attempted to access null object")
    
    # Simulate crash
    raise Exception("Simulated application crash!")


@app.route('/api/cpu-spike')
def cpu_spike():
    """
    Causes CPU spike
    Tests CPU anomaly detection
    """
    logger.warning("CPU spike endpoint called")
    
    # Do intensive computation for 3 seconds
    start = time.time()
    result = 0
    while time.time() - start < 3:
        result += sum(range(10000))
    
    logger.info("CPU spike completed")
    return jsonify({
        "status": "completed",
        "computation_result": result
    })


@app.route('/api/database')
def database():
    """
    Simulates database connection issues
    Tests infrastructure issue detection
    """
    # 50% chance of connection failure
    if random.random() < 0.5:
        logger.error("Database connection failed: Connection refused on port 5432")
        logger.error("PostgreSQL connection pool exhausted")
        return jsonify({"error": "Database unavailable"}), 503
    
    logger.info("Database query successful")
    return jsonify({"status": "ok", "data": []})


@app.route('/api/permission')
def permission():
    """
    Simulates permission errors
    Tests permission issue detection
    """
    logger.error("Permission denied: Insufficient privileges to access resource")
    logger.error("IAM check failed for service account")
    return jsonify({"error": "Access denied"}), 403


@app.route('/api/network')
def network():
    """
    Simulates network issues
    Tests network issue detection
    """
    logger.error("Network error: Connection to external service timed out")
    logger.error("DNS resolution failed for api.external-service.com")
    return jsonify({"error": "Network unreachable"}), 503


@app.route('/api/stress')
def stress():
    """
    Stress test - generates lots of traffic
    """
    logger.info("Stress test started")
    
    # Generate multiple log entries
    for i in range(10):
        if random.random() < 0.3:
            logger.error(f"Stress test error #{i}: Random failure")
        else:
            logger.info(f"Stress test log #{i}")
    
    return jsonify({"status": "completed", "logs_generated": 10})


@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
