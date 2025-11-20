"""
Management command to create missing UserProfiles for existing users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from users.gamification import GamificationManager


class Command(BaseCommand):
    help = 'Create missing UserProfiles for existing users and initialize gamification'

    def handle(self, *args, **options):
        self.stdout.write('Fixing missing UserProfiles...')
        
        created_count = 0
        fixed_count = 0
        
        for user in User.objects.all():
            try:
                # Try to access the profile
                profile = user.userprofile
                # If we get here, profile exists, just ensure gamification is initialized
                GamificationManager.get_or_create_points(user)
                fixed_count += 1
            except UserProfile.DoesNotExist:
                # Create the missing profile
                UserProfile.objects.create(user=user)
                GamificationManager.get_or_create_points(user)
                created_count += 1
                self.stdout.write(f'Created UserProfile for: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created {created_count} new UserProfiles\n'
                f'✓ Fixed {fixed_count} existing users\n'
                f'✓ Total users processed: {created_count + fixed_count}'
            )
        )
