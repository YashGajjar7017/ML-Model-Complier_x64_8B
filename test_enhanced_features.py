#!/usr/bin/env python3
"""
Test script for the enhanced CodeForge AI with multiple models and data management
"""

import requests
import json
import time

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_code_generation():
    """Test code generation with different models"""
    test_cases = [
        {
            "problem_description": "Generate a fibonacci sequence",
            "language": "python",
            "model_type": "pattern_based"
        },
        {
            "problem_description": "Generate a fibonacci sequence",
            "language": "python",
            "model_type": "template_based"
        },
        {
            "problem_description": "Generate a fibonacci sequence",
            "language": "python",
            "model_type": "optimization_focused"
        },
        {
            "problem_description": "Generate a fibonacci sequence",
            "language": "python",
            "model_type": "readability_focused"
        },
        {
            "problem_description": "Generate a fibonacci sequence",
            "language": "python",
            "model_type": "performance_focused"
        }
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['model_type']} ---")
        try:
            response = requests.post('http://localhost:5000/generate', json=test_case)
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Model: {test_case['model_type']}")
                print(f"Confidence: {data.get('confidence', 'N/A')}")
                print(f"Code length: {len(data.get('code', ''))}")
                print("Code preview:")
                print(data.get('code', '')[:200] + "..." if len(data.get('code', '')) > 200 else data.get('code', ''))
            else:
                print(f"Failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error: {e}")

def test_data_management():
    """Test data management endpoints"""
    print("\n--- Testing Data Management ---")

    # Test statistics
    try:
        response = requests.get('http://localhost:5000/data/statistics')
        if response.status_code == 200:
            print("Data statistics retrieved successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Statistics failed: {response.status_code}")
    except Exception as e:
        print(f"Statistics error: {e}")

    # Test similar problems
    try:
        similar_request = {
            "problem_description": "sort an array",
            "limit": 3
        }
        response = requests.post('http://localhost:5000/data/similar', json=similar_request)
        if response.status_code == 200:
            print("Similar problems found successfully")
            data = response.json()
            print(f"Found {data.get('count', 0)} similar problems")
        else:
            print(f"Similar problems failed: {response.status_code}")
    except Exception as e:
        print(f"Similar problems error: {e}")

    # Test recommendations
    try:
        rec_request = {
            "language": "python",
            "problem_type": "sequence_generation"
        }
        response = requests.post('http://localhost:5000/data/recommendations', json=rec_request)
        if response.status_code == 200:
            print("Recommendations retrieved successfully")
            data = response.json()
            print(f"Found {data.get('count', 0)} recommendations")
        else:
            print(f"Recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"Recommendations error: {e}")

if __name__ == "__main__":
    print("Testing CodeForge AI Enhanced Features")
    print("=" * 50)

    # Wait a moment for server to start
    time.sleep(2)

    if test_health():
        test_code_generation()
        test_data_management()
    else:
        print("Server not running, cannot test functionality")