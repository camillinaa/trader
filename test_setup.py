#!/usr/bin/env python3
"""
Test script to verify all components of the macro tracker
Run this after setting up your .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("MACRO TRACKER - COMPONENT TEST")
print("=" * 60)
print()

# Test 1: Environment Variables
print("1. Testing Environment Variables...")
required_vars = ['FRED_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY', 'NTFY_TOPIC']
missing_vars = []

for var in required_vars:
    value = os.getenv(var)
    if value and value != f'your_{var.lower()}_here':
        print(f"   ✓ {var}: Set")
    else:
        print(f"   ✗ {var}: Missing or not configured")
        missing_vars.append(var)

import os
print("SUPABASE_URL:", repr(os.getenv('SUPABASE_URL')))
print("SUPABASE_KEY starts with:", os.getenv('SUPABASE_KEY')[:20] if os.getenv('SUPABASE_KEY') else "MISSING")

if missing_vars:
    print(f"\n   ⚠️  Please set these variables in your .env file: {', '.join(missing_vars)}")
    print("   Copy .env.example to .env and fill in your credentials")
    exit(1)

print()

# Test 2: FRED API
print("2. Testing FRED API Connection...")
try:
    from data_fetcher import MacroDataFetcher
    fetcher = MacroDataFetcher()
    
    # Try fetching GDP data
    gdp = fetcher.fetch_gdp_growth()
    if gdp:
        print(f"   ✓ GDP Growth: {gdp:.2f}%")
    else:
        print("   ✗ Failed to fetch GDP data")
    
    # Try fetching inflation
    inflation = fetcher.fetch_inflation_yoy()
    if inflation:
        print(f"   ✓ Inflation: {inflation:.2f}%")
    else:
        print("   ✗ Failed to fetch inflation data")
    
    # Try fetching real rate
    real_rate = fetcher.fetch_real_treasury_rate()
    if real_rate:
        print(f"   ✓ Real Rate: {real_rate:.2f}%")
    else:
        print("   ✗ Failed to fetch real rate data")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Test 3: Supabase Connection
print("3. Testing Supabase Connection...")
try:
    from database import Database
    db = Database()
    
    if db.supabase:
        print("   ✓ Connected to Supabase")
        
        # Try to fetch latest data
        latest = db.get_latest_data()
        if latest:
            print(f"   ✓ Database has {len(latest)} records")
        else:
            print("   ℹ️  Database is empty (this is normal for first run)")
    else:
        print("   ✗ Failed to connect to Supabase")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Test 4: Notifications
print("4. Testing ntfy.sh Notifications...")
try:
    from notifier import Notifier
    notifier = Notifier()
    
    print(f"   Topic: {notifier.ntfy_topic}")
    print(f"   Subscribe URL: https://ntfy.sh/{notifier.ntfy_topic}")
    
    response = input("\n   Send test notification? (y/n): ")
    if response.lower() == 'y':
        if notifier.test_notification():
            print("   ✓ Notification sent! Check your phone.")
        else:
            print("   ✗ Failed to send notification")
            
except Exception as e:
    print(f"   ✗ Error: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. If all tests passed, run: python app.py")
print("2. Open http://localhost:8000 in your browser")
print("3. Subscribe to ntfy topic on your phone:")
print(f"   https://ntfy.sh/{os.getenv('NTFY_TOPIC', 'your-topic')}")
print()
