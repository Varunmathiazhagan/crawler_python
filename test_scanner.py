#!/usr/bin/env python3
"""
Test script to run the SQL injection scanner against the vulnerable web application
"""

import subprocess
import time
import sys
import os
import requests
from threading import Thread

def start_vulnerable_app():
    """Start the vulnerable web application in background"""
    try:
        # Start the Flask app
        process = subprocess.Popen([
            sys.executable, 'vulnerable_app.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Wait for the app to start
        print("🚀 Starting vulnerable web application...")
        time.sleep(3)
        
        # Test if app is running
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("✅ Vulnerable app is running at http://localhost:5000")
                return process
            else:
                print("❌ App started but not responding correctly")
                return None
        except requests.exceptions.RequestException:
            print("❌ App failed to start or is not accessible")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start vulnerable app: {e}")
        return None

def run_sql_scanner():
    """Run the SQL injection scanner against the vulnerable app"""
    try:
        print("\n🔍 Running SQL injection scanner...")
        print("=" * 50)
        
        # Run the scanner
        result = subprocess.run([
            sys.executable, 'sql.py', 
            '-u', 'http://localhost:5000',
            '-d', '2',
            '-w', '5',
            '-f', 'all'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print("Scanner Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Scanner Errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run scanner: {e}")
        return False

def main():
    print("🧪 SQL Injection Scanner Test Suite")
    print("=" * 40)
    
    # Check if required files exist
    if not os.path.exists('sql.py'):
        print("❌ sql.py not found! Make sure you're in the correct directory.")
        return
        
    if not os.path.exists('vulnerable_app.py'):
        print("❌ vulnerable_app.py not found! Make sure you're in the correct directory.")
        return
    
    # Start the vulnerable application
    app_process = start_vulnerable_app()
    
    if not app_process:
        print("❌ Cannot start vulnerable application. Exiting.")
        return
    
    try:
        # Wait a bit more to ensure app is fully ready
        time.sleep(2)
        
        # Run the scanner
        scanner_success = run_sql_scanner()
        
        if scanner_success:
            print("\n✅ Scanner completed successfully!")
            print("📊 Check the generated reports: report.html, report.pdf, report.docx")
        else:
            print("\n❌ Scanner encountered errors")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        
    finally:
        # Clean up - terminate the app
        print("\n🛑 Stopping vulnerable application...")
        app_process.terminate()
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill()
        print("✅ Cleanup completed")

if __name__ == "__main__":
    main()
