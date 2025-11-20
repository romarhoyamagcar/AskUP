from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys

class Command(BaseCommand):
    help = 'Fix database issues by applying migrations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database fix...'))
        
        try:
            # Check if tables exist
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
            if 'users_conversation' not in tables:
                self.stdout.write(self.style.WARNING('users_conversation table missing. Applying migrations...'))
                
                # Apply migrations
                call_command('migrate', verbosity=1, interactive=False)
                
                self.stdout.write(self.style.SUCCESS('✅ Database migrations applied successfully!'))
                self.stdout.write(self.style.SUCCESS('✅ users_conversation table created'))
                self.stdout.write(self.style.SUCCESS('✅ Messenger functionality should now work'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Database tables already exist'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error fixing database: {str(e)}'))
            sys.exit(1)
