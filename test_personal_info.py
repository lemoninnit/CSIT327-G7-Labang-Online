#!/usr/bin/env python
"""
Test script to verify the personal_info page loads without errors
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

def test_personal_info_page():
    """Test that the personal_info page loads without the admin_dashboard error"""
    print("🧪 Testing Personal Info Page...")
    
    client = Client()
    User = get_user_model()
    
    # Test 1: Check if the URL can be reversed without errors
    try:
        url = reverse('accounts:personal_info')
        print(f"✅ Personal info URL accessible: {url}")
    except Exception as e:
        print(f"❌ URL reversal error: {e}")
        return False
    
    # Test 2: Test page access without login (should redirect)
    try:
        response = client.get(url)
        if response.status_code == 302:  # Should redirect to login
            print("✅ Page properly redirects to login when not authenticated")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Page access error: {e}")
        return False
    
    # Test 3: Create a test user and test authenticated access
    try:
        # Create test user
        from datetime import date
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            resident_confirmation=True,
            date_of_birth=date(1990, 1, 1),
            contact_number='09123456789',
            address_line='Test Address'
        )
        
        # Login and access page
        client.login(username='testuser', password='testpass123')
        response = client.get(url)
        
        if response.status_code == 200:
            print("✅ Personal info page loads successfully for authenticated user")
            
            # Check that the page doesn't contain broken admin_dashboard links
            content = response.content.decode('utf-8')
            if 'admin_dashboard' in content:
                print("❌ Page still contains admin_dashboard references")
                return False
            else:
                print("✅ No broken admin_dashboard references found in page")
        else:
            print(f"❌ Page load failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated page access error: {e}")
        return False
    
    print("\n🎉 Personal info page test passed!")
    return True

if __name__ == '__main__':
    success = test_personal_info_page()
    sys.exit(0 if success else 1)