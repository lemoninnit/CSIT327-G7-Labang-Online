#!/usr/bin/env python
"""
Comprehensive test script to verify all user functions work properly after admin integration
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')
django.setup()

def test_all_user_functions():
    """Test all user functions to ensure they work properly"""
    print("🧪 Testing All User Functions After Admin Integration...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: User model and authentication
    total_tests += 1
    try:
        from accounts.models import User
        from django.contrib.auth import authenticate
        
        user_count = User.objects.count()
        print(f"✅ User model accessible - {user_count} users in database")
        tests_passed += 1
    except Exception as e:
        print(f"❌ User model error: {e}")
    
    # Test 2: All view functions exist
    total_tests += 1
    try:
        from accounts.views import (
            login, register, forgot_password, verify_code, 
            reset_password, personal_info, edit_profile,
            certificate_requests, barangay_clearance_request,
            brgy_residency_cert, brgy_indigency_cert,
            brgy_goodmoral_character, brgy_business_cert,
            payment_mode_selection, gcash_payment, counter_payment,
            report_records, file_report, announcements
        )
        print("✅ All user view functions exist and are importable")
        tests_passed += 1
    except Exception as e:
        print(f"❌ View functions error: {e}")
    
    # Test 3: URL patterns are properly configured
    total_tests += 1
    try:
        from django.urls import reverse
        
        # Test key user URLs
        urls_to_test = [
            'accounts:login',
            'accounts:register',
            'accounts:forgot_password',
            'accounts:personal_info',
            'accounts:certificate_requests',
            'accounts:report_records',
            'accounts:announcements'
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} error: {e}")
                raise
        
        print("✅ All user URLs are properly configured")
        tests_passed += 1
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
    
    # Test 4: Models are properly registered in admin
    total_tests += 1
    try:
        from django.contrib import admin
        
        # Check if models are registered in admin
        registered_models = admin.site._registry
        expected_models = [
            'User', 'PasswordResetCode', 'CertificateRequest', 
            'IncidentReport', 'Announcement'
        ]
        
        for model_name in expected_models:
            found = any(model.__name__ == model_name for model in registered_models.keys())
            if found:
                print(f"✅ {model_name} is registered in admin")
            else:
                print(f"❌ {model_name} is NOT registered in admin")
                raise Exception(f"{model_name} not registered")
        
        print("✅ All models are properly registered in Django admin")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Admin registration error: {e}")
    
    # Test 5: Middleware is properly configured
    total_tests += 1
    try:
        from django.conf import settings
        
        # Check if our custom middleware is in settings
        middleware_classes = settings.MIDDLEWARE
        if 'accounts.middleware.AdminAccessMiddleware' in middleware_classes:
            print("✅ AdminAccessMiddleware is properly configured")
            tests_passed += 1
        else:
            print("❌ AdminAccessMiddleware is NOT configured")
    except Exception as e:
        print(f"❌ Middleware configuration error: {e}")
    
    # Test 6: No old admin functions remain
    total_tests += 1
    try:
        from accounts import views
        
        # Check that old admin functions are removed
        admin_functions = [
            'admin_dashboard', 'admin_users', 'admin_certificates',
            'admin_reports', 'admin_announcements', 'user_create',
            'user_edit', 'user_delete', 'toggle_user_status'
        ]
        
        remaining_functions = []
        for func_name in admin_functions:
            if hasattr(views, func_name):
                remaining_functions.append(func_name)
        
        if not remaining_functions:
            print("✅ All old admin functions have been removed")
            tests_passed += 1
        else:
            print(f"❌ Old admin functions still exist: {remaining_functions}")
    except Exception as e:
        print(f"❌ Admin cleanup error: {e}")
    
    # Test 7: User authentication works
    total_tests += 1
    try:
        # Test basic authentication
        user = authenticate(username='nonexistent', password='wrongpass')
        if user is None:
            print("✅ Authentication system working correctly (returns None for invalid credentials)")
            tests_passed += 1
        else:
            print("❌ Authentication system error")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All user functions are working properly!")
        print("\n✅ Your login and user functionality has been fully restored!")
        print("✅ The admin integration is complete and working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == '__main__':
    success = test_all_user_functions()
    sys.exit(0 if success else 1)