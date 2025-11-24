#!/usr/bin/env python
"""
Final verification script for Django Admin integration and cleanup
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')

# Configure minimal settings for testing
test_settings = {
    'DEBUG': True,
    'INSTALLED_APPS': [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'accounts',
    ],
    'MIDDLEWARE': [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'SECRET_KEY': 'test-secret-key-for-admin-verification',
    'USE_TZ': True,
}

# Apply test settings
settings.configure(**test_settings)

# Setup Django
django.setup()

def verify_admin_integration():
    """Verify Django admin integration is complete"""
    print("🔍 Verifying Django Admin Integration and Cleanup...")
    
    # 1. Check admin site configuration
    from django.contrib import admin
    print(f"✅ Admin site header: {admin.site.site_header}")
    print(f"✅ Admin site title: {admin.site.site_title}")
    print(f"✅ Admin index title: {admin.site.index_title}")
    
    # 2. Check if all models are registered
    registered_models = admin.site._registry.keys()
    from accounts.models import User, PasswordResetCode, CertificateRequest, IncidentReport, Announcement
    expected_models = [User, PasswordResetCode, CertificateRequest, IncidentReport, Announcement]
    
    print(f"\n📋 Registered models:")
    all_registered = True
    for model in expected_models:
        if model in registered_models:
            print(f"✅ {model.__name__} is registered")
        else:
            print(f"❌ {model.__name__} is NOT registered")
            all_registered = False
    
    # 3. Check admin classes configuration
    print(f"\n🔧 Admin classes configured:")
    admin_classes = {
        User: 'UserAdmin',
        PasswordResetCode: 'PasswordResetCodeAdmin', 
        CertificateRequest: 'CertificateRequestAdmin',
        IncidentReport: 'IncidentReportAdmin',
        Announcement: 'AnnouncementAdmin'
    }
    
    for model, expected_class in admin_classes.items():
        if model in admin.site._registry:
            actual_class = admin.site._registry[model].__class__.__name__
            if actual_class == expected_class:
                print(f"✅ {model.__name__} uses {actual_class}")
            else:
                print(f"⚠️  {model.__name__} uses {actual_class} (expected {expected_class})")
    
    # 4. Check middleware configuration
    print(f"\n🛡️  Middleware configuration:")
    middleware_classes = settings.MIDDLEWARE
    if 'accounts.middleware.AdminAccessMiddleware' in middleware_classes:
        print("✅ AdminAccessMiddleware is configured")
    else:
        print("❌ AdminAccessMiddleware is NOT configured")
        all_registered = False
    
    # 5. Check URL configuration (check if admin URLs are present)
    print(f"\n🔗 URL configuration:")
    try:
        from django.urls import reverse
        admin_url = reverse('admin:index')
        print(f"✅ Admin URL configured: {admin_url}")
    except Exception as e:
        print(f"❌ Admin URL not configured: {e}")
        all_registered = False
    
    # 6. Check that old admin functions are removed
    print(f"\n🧹 Old admin functions cleanup:")
    try:
        from accounts import views
        admin_functions = [
            'admin_dashboard', 'admin_users', 'admin_verify_user', 
            'admin_deactivate_user', 'admin_activate_user', 'admin_certificates',
            'admin_certificate_detail', 'admin_verify_payment', 'admin_reject_payment',
            'admin_update_claim_status', 'admin_reports', 'admin_report_detail',
            'admin_update_report_status', 'admin_delete_report', 'admin_announcements',
            'admin_create_announcement', 'admin_edit_announcement', 
            'admin_delete_announcement', 'admin_toggle_announcement'
        ]
        
        old_functions_found = []
        for func_name in admin_functions:
            if hasattr(views, func_name):
                old_functions_found.append(func_name)
        
        if not old_functions_found:
            print("✅ All old admin functions have been removed")
        else:
            print(f"❌ Found old admin functions: {', '.join(old_functions_found)}")
            all_registered = False
            
    except Exception as e:
        print(f"❌ Error checking views: {e}")
        all_registered = False
    
    # 7. Check that old admin templates are removed
    print(f"\n📁 Old admin templates cleanup:")
    old_admin_templates = [
        'templates/admin/dashboard.html',
        'templates/admin/users.html', 
        'templates/admin/certificates.html',
        'templates/admin/reports.html',
        'templates/admin/announcements.html'
    ]
    
    templates_removed = True
    for template in old_admin_templates:
        full_path = os.path.join(os.path.dirname(__file__), template)
        if os.path.exists(full_path):
            print(f"❌ Template still exists: {template}")
            templates_removed = False
        else:
            print(f"✅ Template removed: {template}")
    
    if templates_removed:
        print("✅ All old admin templates have been removed")
    else:
        all_registered = False
    
    # 8. Check that old admin URLs are removed
    print(f"\n🌐 Old admin URLs cleanup:")
    try:
        from accounts.urls import urlpatterns
        old_admin_url_patterns = [
            'admin/dashboard/', 'admin/users/', 'admin/certificates/', 
            'admin/reports/', 'admin/announcements/'
        ]
        
        urls_found = []
        for pattern in urlpatterns:
            pattern_str = str(pattern.pattern) if hasattr(pattern, 'pattern') else str(pattern)
            for old_pattern in old_admin_url_patterns:
                if old_pattern in pattern_str:
                    urls_found.append(pattern_str)
        
        if not urls_found:
            print("✅ All old admin URLs have been removed")
        else:
            print(f"❌ Found old admin URLs: {', '.join(urls_found)}")
            all_registered = False
            
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")
        all_registered = False
    
    # Final summary
    print(f"\n" + "="*60)
    if all_registered and templates_removed:
        print("🎉 SUCCESS: Django Admin integration and cleanup is COMPLETE!")
        print("\n📊 Summary:")
        print("✅ Django Admin is properly configured with custom branding")
        print("✅ All models are registered in the admin panel")
        print("✅ Admin access middleware is configured for security")
        print("✅ Old admin functions have been removed from views.py")
        print("✅ Old admin templates have been deleted")
        print("✅ Old admin URLs have been removed from urls.py")
        print("\n🚀 The system now uses Django Admin exclusively for administration!")
    else:
        print("⚠️  WARNING: Some issues were found during verification")
        print("Please review the output above and fix any remaining issues.")
    
    return all_registered and templates_removed

if __name__ == "__main__":
    verify_admin_integration()