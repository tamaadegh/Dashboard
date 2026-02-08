#!/usr/bin/env python
"""
API Endpoint Test Script
Tests all mobile app endpoints to ensure they're working correctly
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Currency": "GHS"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_endpoint(name: str, url: str, expected_keys: list = None) -> bool:
    """Test a single endpoint"""
    try:
        print_info(f"Testing {name}...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for expected keys
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data and key not in str(data)]
                if missing_keys:
                    print_warning(f"  Missing keys: {missing_keys}")
            
            # Print summary
            if isinstance(data, dict):
                if 'count' in data:
                    print_success(f"{name}: {data['count']} items found")
                elif 'status' in data:
                    print_success(f"{name}: Status = {data['status']}")
                else:
                    print_success(f"{name}: Response OK")
            elif isinstance(data, list):
                print_success(f"{name}: {len(data)} items found")
            else:
                print_success(f"{name}: Response OK")
            
            return True
        else:
            print_error(f"{name}: HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"{name}: Connection refused - Is the server running?")
        return False
    except requests.exceptions.Timeout:
        print_error(f"{name}: Request timeout")
        return False
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False

def test_product_detail(slug: str = None) -> bool:
    """Test product detail endpoint with a real slug"""
    try:
        # First get a product slug from the list
        if not slug:
            response = requests.get(
                f"{BASE_URL}/product/storefront/api/products/",
                headers=HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    slug = data['results'][0]['slug']
                else:
                    print_warning("No products found to test detail endpoint")
                    return False
        
        # Test the detail endpoint
        url = f"{BASE_URL}/product/storefront/api/products/{slug}/"
        return test_endpoint(f"Product Detail ({slug})", url, ['id', 'slug', 'texts'])
        
    except Exception as e:
        print_error(f"Product Detail: {str(e)}")
        return False

def main():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("  Tamaade API Endpoint Test Suite")
    print("="*60 + "\n")
    
    results = {}
    
    # Test 1: Health Check
    print("\n📊 Testing Health & Monitoring")
    print("-" * 40)
    results['health'] = test_endpoint(
        "Health Check",
        f"{BASE_URL}/health/",
        ['status', 'version']
    )
    
    # Test 2: Products
    print("\n📦 Testing Products API")
    print("-" * 40)
    results['products_list'] = test_endpoint(
        "Products List",
        f"{BASE_URL}/product/storefront/api/products/",
        ['count', 'results']
    )
    
    results['products_detail'] = test_product_detail()
    
    # Test 3: Categories
    print("\n📂 Testing Categories API")
    print("-" * 40)
    results['categories'] = test_endpoint(
        "Categories (Recursive)",
        f"{BASE_URL}/product/storefront/api/recursive-categories/",
        ['id', 'name']
    )
    
    # Test 4: Collections
    print("\n🏷️  Testing Collections API")
    print("-" * 40)
    results['collections'] = test_endpoint(
        "Collections",
        f"{BASE_URL}/product/storefront/api/collections/",
        ['id', 'name']
    )
    
    # Test 5: Search & Filtering
    print("\n🔍 Testing Search & Filtering")
    print("-" * 40)
    results['search'] = test_endpoint(
        "Product Search",
        f"{BASE_URL}/product/storefront/api/products/?search=bed",
        ['count', 'results']
    )
    
    results['filter_category'] = test_endpoint(
        "Filter by Category",
        f"{BASE_URL}/product/storefront/api/products/?category=1",
        ['count', 'results']
    )
    
    # Test 6: Pagination
    print("\n📄 Testing Pagination")
    print("-" * 40)
    results['pagination'] = test_endpoint(
        "Pagination (limit=5)",
        f"{BASE_URL}/product/storefront/api/products/?limit=5&offset=0",
        ['count', 'results']
    )
    
    # Test 7: Currency
    print("\n💱 Testing Multi-Currency")
    print("-" * 40)
    usd_headers = HEADERS.copy()
    usd_headers['Currency'] = 'USD'
    try:
        response = requests.get(
            f"{BASE_URL}/product/storefront/api/products/?limit=1",
            headers=usd_headers,
            timeout=10
        )
        if response.status_code == 200:
            print_success("Currency Header (USD): Response OK")
            results['currency'] = True
        else:
            print_error(f"Currency Header: HTTP {response.status_code}")
            results['currency'] = False
    except Exception as e:
        print_error(f"Currency Header: {str(e)}")
        results['currency'] = False
    
    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.END} - {test_name}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print_success("\n🎉 All tests passed! API is ready for mobile app integration.")
    else:
        print_error(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    print("\n")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
