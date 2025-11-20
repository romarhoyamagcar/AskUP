"""
Context processors to add user data to all templates
"""

from .gamification import GamificationManager
from .models import StudentPoints, Notification, UserProfile, Message


def user_status_data(request):
    """
    Add user status and gamification data to template context
    """
    if not request.user.is_authenticated:
        return {}
    
    try:
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get gamification data
        points_obj = GamificationManager.get_or_create_points(request.user)
        
        # Get user stats
        user_stats = GamificationManager.get_user_stats(request.user)
        
        # Get unread notifications count
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        # Get recent notifications (last 3)
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:3]
        
        if request.user.is_staff:
            unread_messages_count = Message.objects.filter(is_read=False).count()
        else:
            unread_messages_count = Message.objects.filter(sender=request.user, is_read=False).count()

        return {
            'user_profile': profile,
            'user_points': points_obj,
            'user_level': points_obj.level,
            'user_total_points': points_obj.total_points,
            'user_rank': user_stats.get('rank', 0),
            'user_achievements_count': user_stats.get('achievements_count', 0),
            'user_current_streak': points_obj.current_streak,
            'unread_notifications_count': unread_notifications,
            'recent_notifications': recent_notifications,
            'unread_messages_count': unread_messages_count,
            'show_onboarding': profile.show_onboarding,
            'level_progress': user_stats.get('progress_to_next_level', {
                'percentage': 0,
                'points_needed': 0
            })
        }
    except Exception as e:
        # Return empty dict if there's any error
        return {
            'user_profile': None,
            'user_points': None,
            'user_level': 1,
            'user_total_points': 0,
            'user_rank': 0,
            'user_achievements_count': 0,
            'user_current_streak': 0,
            'unread_notifications_count': 0,
            'recent_notifications': [],
            'unread_messages_count': 0,
            'show_onboarding': False,
            'level_progress': {'percentage': 0, 'points_needed': 0}
        }
