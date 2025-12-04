#!/usr/bin/env python3
"""
Authenticated Traffic Generator for Demo Service

Uses your gcloud credentials to make authenticated requests.
"""

import subprocess
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
import sys
import json


def get_id_token(service_url):
    """Get ID token for authentication"""
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'print-identity-token'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to get auth token: {e}")
        print("\nMake sure you're authenticated:")
        print("  gcloud auth login")
        sys.exit(1)


def generate_traffic(service_url, duration_minutes=5):
    """
    Generate authenticated traffic to the demo service

    Args:
        service_url: URL of the deployed service
        duration_minutes: How long to generate traffic
    """
    print(f"\n🚀 Starting authenticated traffic generation for {duration_minutes} minutes...")
    print(f"Target: {service_url}")
    print("-" * 60)

    # Get auth token
    print("🔐 Getting authentication token...")
    id_token = get_id_token(service_url)
    headers = {
        'Authorization': f'Bearer {id_token}'
    }

    endpoints = [
        ("/api/process", "Normal requests with 30% errors"),
        ("/api/slow", "Slow endpoint (2-5s)"),
        ("/api/database", "Database errors (50% fail)"),
        ("/api/permission", "Permission errors"),
        ("/api/network", "Network errors"),
        ("/api/memory-leak", "Memory leak"),
    ]

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    request_count = 0
    error_count = 0

    def make_request(endpoint):
        """Make a single authenticated request"""
        nonlocal request_count, error_count
        try:
            response = requests.get(
                f"{service_url}{endpoint}",
                headers=headers,
                timeout=10
            )
            request_count += 1

            if response.status_code >= 400:
                error_count += 1
                print(f"❌ {endpoint} -> {response.status_code}")
            else:
                print(f"✅ {endpoint} -> {response.status_code}")

            return response.status_code
        except Exception as e:
            error_count += 1
            print(f"❌ {endpoint} -> Error: {e}")
            return None

    print("\n📊 Traffic Pattern:")
    for endpoint, description in endpoints:
        print(f"  • {endpoint}: {description}")
    print("\n" + "-" * 60 + "\n")

    # Test first request
    print("🧪 Testing connectivity...")
    test_response = requests.get(f"{service_url}/health", headers=headers, timeout=5)
    if test_response.status_code == 200:
        print("✅ Service is reachable with authentication\n")
    else:
        print(f"⚠️  Service returned status {test_response.status_code}\n")

    # Generate traffic
    print("🔄 Generating traffic...\n")
    with ThreadPoolExecutor(max_workers=3) as executor:
        while time.time() < end_time:
            # Random endpoint selection (weighted towards errors)
            endpoint = random.choice([
                "/api/process",
                "/api/process",
                "/api/process",  # More normal traffic
                "/api/slow",
                "/api/database",
                "/api/permission",
                "/api/network",
            ])

            executor.submit(make_request, endpoint)

            # Random delay between requests (0.5-2 seconds)
            time.sleep(random.uniform(0.5, 2))

    # Summary
    print("\n" + "=" * 60)
    print("📈 Traffic Generation Complete!")
    print("=" * 60)
    print(f"Total Requests: {request_count}")
    print(f"Errors: {error_count}")
    print(f"Error Rate: {(error_count / request_count * 100) if request_count > 0 else 0:.1f}%")
    print(f"Duration: {(time.time() - start_time) / 60:.1f} minutes")
    print("\n⏳ Wait 2-3 minutes for logs to be available in Cloud Logging")
    print("Then run your AIOps Agent test")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_traffic_auth.py <SERVICE_URL> [duration_minutes]")
        print("\nExample:")
        print("  python generate_traffic_auth.py https://aiops-demo-service-xxx.run.app 5")
        sys.exit(1)

    service_url = sys.argv[1].rstrip('/')
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"\n{'=' * 60}")
    print("🎯 AIOps Demo Service - Authenticated Traffic Generator")
    print(f"{'=' * 60}")

    generate_traffic(service_url, duration)