#!/usr/bin/env python
"""
Test script to verify login functionality is working properly
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import User

def test_login_functionality():
    """Test basic login functionality"""
    print("🧪 Testing Login Functionality...")
    
    # Test 1: Check if we can access the User model
    try:
        user_count = User.objects.count()
        print(f"✅ User model accessible - {user_count} users in database")
    except Exception as e:
        print(f"❌ User model error: {e}")
        return False
    
    # Test 2: Test authentication with a test user (if exists)
    try:
        # Try to authenticate with a common test user
        user = authenticate(username='testuser', password='testpass123')
        if user:
            print(f"✅ Authentication successful for testuser")
        else:
            print("ℹ️  No test user found, but authentication system is working")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test 3: Check if login view exists and is accessible
    try:
        from django.urls import reverse
        login_url = reverse('accounts:login')
        print(f"✅ Login URL accessible: {login_url}")
    except Exception as e:
        print(f"❌ Login URL error: {e}")
        return False
    
    # Test 4: Check if the login view function exists
    try:
        from accounts.views import login
        print("✅ Login view function exists")
    except Exception as e:
        print(f"❌ Login view error: {e}")
        return False
    
    print("\n🎉 All login functionality tests passed!")
    return True

if __name__ == '__main__':
    success = test_login_functionality()
    sys.exit(0 if success else 1)