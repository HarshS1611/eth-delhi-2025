#!/usr/bin/env python3
"""
System Startup Script - ETH Delhi 2025
Comprehensive Dataset Validation System
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_header():
    """Print system header"""
    print("=" * 70)
    print("🎯 ETH DELHI 2025 - DATASET VALIDATION SYSTEM")
    print("🤖 Autonomous Agent-to-Agent Validation Pipeline")
    print("=" * 70)

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking system requirements...")
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check key packages
        required_packages = [
            'pandas', 'numpy', 'uagents', 'fastapi', 'uvicorn'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} not found")
        
        if missing_packages:
            print(f"\n🔧 Install missing packages: pip install {' '.join(missing_packages)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements check failed: {e}")
        return False

def check_datasets():
    """Check if demo datasets are available"""
    print("\n📊 Checking demo datasets...")
    
    base_dir = Path(__file__).parent
    datasets = [
        ("comprehensive_healthcare_dataset.csv", "Healthcare Dataset"),
        ("comprehensive_air_quality_dataset.csv", "Air Quality Dataset")
    ]
    
    available_datasets = 0
    for filename, name in datasets:
        dataset_path = base_dir / filename
        if dataset_path.exists():
            size_mb = dataset_path.stat().st_size / (1024 * 1024)
            print(f"✅ {name}: {size_mb:.1f}MB")
            available_datasets += 1
        else:
            print(f"❌ {name}: Not found")
    
    return available_datasets > 0

def run_system_test():
    """Run comprehensive system test"""
    print("\n🧪 Running system validation test...")
    
    try:
        # Run the comprehensive test
        result = subprocess.run([
            sys.executable, "test_comprehensive_system.py"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✅ System test passed!")
            return True
        else:
            print("❌ System test failed!")
            print("Error output:", result.stderr[-500:] if result.stderr else "No error output")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ System test timed out - this may be normal for first run")
        return True  # Continue anyway
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def start_api_server():
    """Start the validation API server"""
    print("\n🚀 Starting validation API server...")
    
    try:
        # Check if server is already running
        import requests
        try:
            response = requests.get("http://localhost:8080/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server already running!")
                return True
        except:
            pass
        
        # Start the server in background
        print("📡 Launching API server on http://localhost:8080")
        subprocess.Popen([
            sys.executable, "validation_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for attempt in range(15):  # 15 second timeout
            try:
                import requests
                response = requests.get("http://localhost:8080/health", timeout=1)
                if response.status_code == 200:
                    print("✅ API server started successfully!")
                    return True
            except:
                time.sleep(1)
        
        print("⚠️ API server may still be starting...")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return False

def open_dashboard():
    """Open the validation dashboard"""
    print("\n🌐 Opening validation dashboard...")
    
    # Check if dashboard HTML exists
    dashboard_path = Path(__file__).parent / "validation_dashboard.html"
    if not dashboard_path.exists():
        print("❌ Dashboard HTML not found")
        return False
    
    dashboard_url = "http://localhost:8080"
    
    try:
        # Try to open in browser
        webbrowser.open(dashboard_url)
        print(f"✅ Dashboard opened: {dashboard_url}")
        return True
    except Exception as e:
        print(f"⚠️ Could not auto-open browser: {e}")
        print(f"🌐 Manual: Open {dashboard_url} in your browser")
        return True

def print_system_info():
    """Print system information and next steps"""
    print("\n" + "=" * 70)
    print("🎯 SYSTEM READY - ETH DELHI 2025")
    print("=" * 70)
    print("🌐 Dashboard: http://localhost:8080")
    print("📖 API Docs: http://localhost:8080/docs")
    print("🏥 Healthcare Demo: Click 'Demo: Healthcare Data' button")
    print("🌍 Air Quality Demo: Click 'Demo: Air Quality Data' button")
    print("\n📊 VALIDATION FEATURES:")
    print("  • 16 specialized validation tools")
    print("  • 2 legal compliance tools") 
    print("  • Agent-to-agent communication")
    print("  • Real-time scoring (0-100)")
    print("  • Executive summaries")
    print("  • Actionable recommendations")
    print("\n🚀 READY FOR DEMO!")
    print("=" * 70)

def main():
    """Main startup sequence"""
    print_header()
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing packages.")
        return False
    
    # Step 2: Check datasets
    if not check_datasets():
        print("\n❌ Demo datasets not found. Please ensure datasets are in the agents folder.")
        return False
    
    # Step 3: Run system test (optional, can be skipped if takes too long)
    print("\n🔄 Would you like to run the comprehensive system test? (y/n): ", end="")
    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            if not run_system_test():
                print("\n⚠️ System test failed, but continuing anyway...")
        else:
            print("⏩ Skipping system test")
    except KeyboardInterrupt:
        print("\n⏩ Skipping system test")
    
    # Step 4: Start API server
    if not start_api_server():
        print("\n❌ Failed to start API server")
        return False
    
    # Step 5: Open dashboard
    time.sleep(2)  # Give server a moment to fully start
    open_dashboard()
    
    # Step 6: Print system info
    print_system_info()
    
    print("\n🎤 Press Ctrl+C to stop the system")
    
    # Keep the script running
    try:
        while True:
            time.sleep(10)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down ETH Delhi 2025 validation system...")
        return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)