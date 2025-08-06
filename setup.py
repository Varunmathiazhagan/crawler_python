#!/usr/bin/env python3
"""
Setup script to install dependencies for the SQL injection testing environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing dependencies...")
    
    # Check if requirements.txt exists
    if os.path.exists('requirements.txt'):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Scanner dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install scanner dependencies")
            return False
    else:
        print("⚠️  requirements.txt not found, installing basic packages...")
        basic_packages = [
            'requests', 'beautifulsoup4', 'fake-useragent', 'tqdm', 
            'colorama', 'reportlab', 'pypandoc', 'lxml'
        ]
        for package in basic_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
    
    # Install Flask for the vulnerable app
    if os.path.exists('app_requirements.txt'):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'app_requirements.txt'])
            print("✅ Web app dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install web app dependencies")
            return False
    else:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask==2.3.3'])
            print("✅ Flask installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Flask")
            return False
    
    return True

def main():
    print("🔧 SQL Injection Testing Environment Setup")
    print("=" * 45)
    
    if install_requirements():
        print("\n✅ Setup completed successfully!")
        print("\n📖 Usage:")
        print("1. Run 'python test_scanner.py' to test automatically")
        print("2. Or manually:")
        print("   - Start app: python vulnerable_app.py")
        print("   - Run scanner: python sql.py -u http://localhost:5000")
        print("\n⚠️  Remember: Only use the vulnerable app in isolated environments!")
    else:
        print("\n❌ Setup failed. Please check error messages above.")

if __name__ == "__main__":
    main()
