"""
Management command to initialize gamification system
Run this after migrations to set up default achievements and user points
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.gamification import GamificationManager, create_default_achievements
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Initialize gamification system with default achievements and user points'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all gamification data (WARNING: This will delete all points and achievements)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing AskUP Gamification System...')
        
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all gamification data...'))
            # Reset logic here if needed
            
        # Create default achievements
        self.stdout.write('Creating default achievements...')
        create_default_achievements()
        self.stdout.write(self.style.SUCCESS('✓ Default achievements created'))
        
        # Initialize points for all existing users
        self.stdout.write('Initializing user points...')
        users_count = 0
        for user in User.objects.all():
            if not user.is_superuser:  # Skip superusers
                # Create UserProfile if it doesn't exist
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Initialize gamification
                GamificationManager.get_or_create_points(user)
                users_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Initialized points for {users_count} users'))
        
        # Display summary
        from users.models import Achievement, StudentPoints
        achievements_count = Achievement.objects.count()
        points_count = StudentPoints.objects.count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Gamification System Initialized Successfully!'))
        self.stdout.write('='*50)
        self.stdout.write(f'📊 Achievements created: {achievements_count}')
        self.stdout.write(f'👥 Users with points: {points_count}')
        self.stdout.write('='*50)
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Run migrations if you haven\'t: python manage.py migrate')
        self.stdout.write('2. Access gamification at: /progress/')
        self.stdout.write('3. View leaderboard at: /leaderboard/')
        self.stdout.write('4. Users will earn points automatically when they:')
        self.stdout.write('   - Ask questions (5 points)')
        self.stdout.write('   - Provide answers (10 points)')
        self.stdout.write('   - Maintain learning streaks (5+ points)')
        self.stdout.write('   - Earn achievements (varies)')
