#!/usr/bin/env python3

import json
import requests

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test root endpoint"""
    print("🏠 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_register_client():
    """Test client registration"""
    print("👤 Testing client registration...")
    data = {
        "name": "Juan Perez Test",
        "email": "juan.test2@fastapi.com",
        "phone": "+51987654321",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/client/register", json=data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw response: {response.text}")
    print()
    return response

if __name__ == "__main__":
    print("🚀 Testing Collique Delivery FastAPI endpoints...")
    print("=" * 50)

    test_health()
    test_root()
    test_register_client()

    print("✅ Test completed!")