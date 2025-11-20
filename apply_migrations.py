#!/usr/bin/env python
"""
Quick script to apply database migrations
Run this with: python apply_migrations.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askup.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("=" * 60)
    print("Applying Database Migrations...")
    print("=" * 60)
    
    try:
        # Apply all migrations
        call_command('migrate', verbosity=2, interactive=False)
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Database migrations applied successfully!")
        print("=" * 60)
        print("\nThe following tables have been created:")
        print("  ✓ users_conversation")
        print("  ✓ users_conversationmessage")
        print("  ✓ users_messagereadstatus")
        print("\n✅ The /messenger/ page should now work!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 60)
        sys.exit(1)
