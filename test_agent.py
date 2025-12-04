#!/usr/bin/env python3
"""
Test AIOps Agent with Demo Service

This script tests your AIOps Agent against the deployed demo service.
"""

import sys
import os

# Add parent directory to path to import the agent
sys.path.insert(0, os.path.abspath('..'))

from src.agents.ops_commander import OpsCommander
import json


def print_result(result, test_name):
    """Pretty print investigation results"""
    print(f"\n{'='*70}")
    print(f"🔍 {test_name}")
    print('='*70)
    
    if result.get("success"):
        print(f"\n✅ Investigation Successful")
        print(f"\n📊 Results:")
        print(f"   Service: {result.get('service_name')}")
        print(f"   Root Cause: {result.get('root_cause')}")
        print(f"   Confidence: {result.get('confidence', 0):.0%}")
        print(f"   Duration: {result.get('duration_seconds', 0):.2f}s")
        print(f"   Metrics Analyzed: {result.get('metrics_analyzed')}")
        print(f"   Logs Analyzed: {result.get('logs_analyzed')}")
        
        if result.get('time_window'):
            tw = result['time_window']
            print(f"\n⏰ Time Window:")
            print(f"   From: {tw.get('start')}")
            print(f"   To:   {tw.get('end')}")
        
        print(f"\n📝 Full Summary:")
        print("-" * 70)
        print(result.get('summary', 'No summary available'))
        
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"   • {error}")
    else:
        print(f"\n❌ Investigation Failed")
        print(f"   Error: {result.get('error')}")


def main():
    """Run AIOps Agent tests"""
    
    # Get project ID and service name from environment or arguments
    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        project_id = os.popen("gcloud config get-value project").read().strip()
    
    service_name = sys.argv[1] if len(sys.argv) > 1 else "aiops-demo-service"
    
    print("\n" + "="*70)
    print(" " * 20 + "🤖 AIOps Agent - End-to-End Test")
    print("="*70)
    print(f"\nProject ID: {project_id}")
    print(f"Service Name: {service_name}")
    print("\n" + "="*70)
    
    # Initialize AIOps Agent
    print("\n🔧 Initializing AIOps Agent...")
    commander = OpsCommander(project_id=project_id, use_llm=False)
    print("✅ Agent initialized!\n")
    
    # Test Case 1: General health check
    print("\n" + "="*70)
    print("TEST 1: General Health Investigation")
    print("="*70)
    
    result1 = commander.handle_query(
        f"Check the health of {service_name}",
        service_name=service_name
    )
    print_result(result1, "General Health Check")
    
    # Test Case 2: Error investigation
    print("\n" + "="*70)
    print("TEST 2: Error Investigation")
    print("="*70)
    
    result2 = commander.handle_query(
        f"{service_name} is throwing errors",
        service_name=service_name
    )
    print_result(result2, "Error Investigation")
    
    # Test Case 3: Performance issue
    print("\n" + "="*70)
    print("TEST 3: Performance Investigation")
    print("="*70)
    
    result3 = commander.handle_query(
        f"Why is {service_name} so slow?",
        service_name=service_name
    )
    print_result(result3, "Performance Investigation")
    
    # Test Case 4: Crash investigation
    print("\n" + "="*70)
    print("TEST 4: Crash Investigation")
    print("="*70)
    
    result4 = commander.handle_query(
        f"{service_name} keeps crashing!",
        service_name=service_name
    )
    print_result(result4, "Crash Investigation")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    tests = [result1, result2, result3, result4]
    successful = sum(1 for r in tests if r.get('success'))
    
    print(f"\nTests Run: {len(tests)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(tests) - successful}")
    
    # Detailed findings
    print(f"\n🔍 Key Findings:")
    for i, result in enumerate(tests, 1):
        if result.get('success'):
            logs = result.get('logs_analyzed', 0)
            metrics = result.get('metrics_analyzed', 0)
            print(f"  Test {i}: {logs} logs, {metrics} metrics analyzed")
    
    print("\n" + "="*70)
    print("✅ End-to-End Testing Complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
