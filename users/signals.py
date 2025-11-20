"""
Django signals for automatic UserProfile creation and gamification initialization
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from .gamification import GamificationManager


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure UserProfile exists and initialize gamification
    """
    # Create UserProfile if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=instance)
    
    # Initialize gamification for new users
    if created or not hasattr(instance, 'points'):
        GamificationManager.get_or_create_points(instance)


@receiver(post_save, sender=UserProfile)
def initialize_gamification(sender, instance, created, **kwargs):
    """
    Initialize gamification when UserProfile is created
    """
    if created:
        # Create default achievements if they don't exist
        from .gamification import create_default_achievements
        create_default_achievements()
        
        # Initialize points for this user
        GamificationManager.get_or_create_points(instance.user)
