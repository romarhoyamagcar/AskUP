"""
Gamification utilities for AskUP
Handles points, achievements, and level progression
"""

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import StudentPoints, Achievement, StudentAchievement, LearningStreak, StudentActivity

class GamificationManager:
    """Manages all gamification features"""
    
    # Point values for different activities
    POINTS = {
        'question_asked': 5,
        'answer_given': 10,
        'answer_accepted': 15,
        'helpful_answer': 20,
        'daily_streak': 5,
        'weekly_streak': 25,
        'monthly_streak': 100,
        'first_question': 10,
        'first_answer': 15,
        'message_sent': 2,
        'question_deleted': -3,  # Negative points for deleting questions
    }
    
    @classmethod
    def get_or_create_points(cls, user):
        """Get or create StudentPoints for user"""
        points, created = StudentPoints.objects.get_or_create(
            student=user,
            defaults={
                'total_points': 0,
                'level': 1,
                'current_streak': 0,
                'longest_streak': 0
            }
        )
        return points
    
    @classmethod
    def award_points(cls, user, activity_type, points_override=None):
        """Award points to user for activity"""
        if not user.is_authenticated:
            return False
        
        # Ensure UserProfile exists
        from .models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
            
        points_obj = cls.get_or_create_points(user)
        points_to_add = points_override or cls.POINTS.get(activity_type, 0)
        
        # Add points to appropriate category
        if activity_type in ['question_asked', 'first_question']:
            points_obj.questions_points = max(0, points_obj.questions_points + points_to_add)
        elif activity_type in ['answer_given', 'answer_accepted', 'helpful_answer', 'first_answer']:
            points_obj.answers_points = max(0, points_obj.answers_points + points_to_add)
        elif 'streak' in activity_type:
            points_obj.consistency_points = max(0, points_obj.consistency_points + points_to_add)
        elif activity_type == 'question_deleted':
            # Handle negative points for deletion
            points_obj.questions_points = max(0, points_obj.questions_points + points_to_add)
        else:
            points_obj.helping_points = max(0, points_obj.helping_points + points_to_add)
        
        # Update total points (allow negative total but ensure categories stay non-negative)
        points_obj.total_points += points_to_add
        # Ensure total points don't go below 0
        points_obj.total_points = max(0, points_obj.total_points)
        
        # Check for level up
        level_up = points_obj.update_level()
        
        # Update streak
        cls.update_streak(user)
        
        points_obj.save()
        
        # Log activity
        StudentActivity.objects.create(
            student=user,
            activity_type=activity_type,
            description=f"Earned {points_to_add} points for {activity_type}"
        )
        
        # Check for new achievements
        new_achievements = cls.check_achievements(user)
        
        return {
            'points_awarded': points_to_add,
            'total_points': points_obj.total_points,
            'level_up': level_up,
            'new_level': points_obj.level if level_up else None,
            'new_achievements': new_achievements
        }
    
    @classmethod
    def update_streak(cls, user):
        """Update user's learning streak"""
        points_obj = cls.get_or_create_points(user)
        today = date.today()
        
        # Get or create today's streak record
        streak, created = LearningStreak.objects.get_or_create(
            student=user,
            date=today,
            defaults={'activities_count': 0, 'points_earned': 0}
        )
        
        streak.activities_count += 1
        streak.save()
        
        # Check if streak continues from yesterday
        yesterday = today - timedelta(days=1)
        
        if points_obj.last_activity_date == yesterday:
            # Streak continues
            points_obj.current_streak += 1 if created else 0
        elif points_obj.last_activity_date != today:
            # New streak or broken streak
            points_obj.current_streak = 1
        
        # Update longest streak
        if points_obj.current_streak > points_obj.longest_streak:
            points_obj.longest_streak = points_obj.current_streak
        
        points_obj.last_activity_date = today
        points_obj.save()
        
        # Award streak bonuses
        if points_obj.current_streak % 7 == 0:  # Weekly streak
            cls.award_points(user, 'weekly_streak')
        elif points_obj.current_streak % 30 == 0:  # Monthly streak
            cls.award_points(user, 'monthly_streak')
        elif created:  # Daily activity
            cls.award_points(user, 'daily_streak')
    
    @classmethod
    def check_achievements(cls, user):
        """Check and award new achievements"""
        points_obj = cls.get_or_create_points(user)
        new_achievements = []
        
        # Get all available achievements
        available_achievements = Achievement.objects.filter(is_active=True)
        
        # Get user's current achievements
        earned_achievement_ids = StudentAchievement.objects.filter(
            student=user
        ).values_list('achievement_id', flat=True)
        
        for achievement in available_achievements:
            if achievement.id in earned_achievement_ids:
                continue  # Already earned
            
            # Check if user qualifies for this achievement
            if cls.qualifies_for_achievement(user, achievement, points_obj):
                # Award achievement
                StudentAchievement.objects.create(
                    student=user,
                    achievement=achievement
                )
                new_achievements.append(achievement)
        
        return new_achievements
    
    @classmethod
    def qualifies_for_achievement(cls, user, achievement, points_obj):
        """Check if user qualifies for specific achievement"""
        
        # Points-based achievements
        if achievement.points_required > 0:
            category_points = {
                'questions': points_obj.questions_points,
                'answers': points_obj.answers_points,
                'helping': points_obj.helping_points,
                'consistency': points_obj.consistency_points,
            }
            
            required_points = achievement.points_required
            if achievement.category in category_points:
                return category_points[achievement.category] >= required_points
            else:
                return points_obj.total_points >= required_points
        
        # Special achievement logic
        achievement_name = achievement.name.lower()
        
        if 'first question' in achievement_name:
            return points_obj.questions_points > 0
        elif 'first answer' in achievement_name:
            return points_obj.answers_points > 0
        elif 'streak' in achievement_name:
            if '7 day' in achievement_name:
                return points_obj.current_streak >= 7
            elif '30 day' in achievement_name:
                return points_obj.current_streak >= 30
        elif 'level' in achievement_name:
            if 'level 5' in achievement_name:
                return points_obj.level >= 5
            elif 'level 10' in achievement_name:
                return points_obj.level >= 10
        
        return False
    
    @classmethod
    def get_leaderboard(cls, limit=10, category='total'):
        """Get leaderboard for points"""
        order_field = {
            'total': '-total_points',
            'questions': '-questions_points',
            'answers': '-answers_points',
            'level': '-level',
            'streak': '-current_streak'
        }.get(category, '-total_points')
        
        return StudentPoints.objects.select_related('student').order_by(order_field)[:limit]
    
    @classmethod
    def get_user_stats(cls, user):
        """Get comprehensive stats for user"""
        points_obj = cls.get_or_create_points(user)
        achievements = StudentAchievement.objects.filter(student=user).select_related('achievement')
        
        return {
            'points': points_obj,
            'achievements': achievements,
            'achievements_count': achievements.count(),
            'rank': cls.get_user_rank(user),
            'progress_to_next_level': cls.get_level_progress(points_obj)
        }
    
    @classmethod
    def get_user_rank(cls, user):
        """Get user's rank based on total points"""
        points_obj = cls.get_or_create_points(user)
        higher_ranked = StudentPoints.objects.filter(
            total_points__gt=points_obj.total_points
        ).count()
        return higher_ranked + 1
    
    @classmethod
    def get_level_progress(cls, points_obj):
        """Get progress towards next level"""
        points_needed = points_obj.points_to_next_level()
        current_level_points = (points_obj.level - 1) ** 2 * 100
        next_level_points = points_obj.level ** 2 * 100
        level_points_range = next_level_points - current_level_points
        
        # Ensure safe calculation with non-negative points
        safe_total_points = max(0, points_obj.total_points)
        progress = max(0, safe_total_points - current_level_points)
        
        return {
            'current_progress': progress,
            'points_needed': points_needed,
            'percentage': min(100, (progress / level_points_range) * 100) if level_points_range > 0 else 100
        }

# Initialize default achievements
def create_default_achievements():
    """Create default achievements for the platform"""
    default_achievements = [
        {
            'name': 'First Question',
            'description': 'Asked your first question',
            'icon': 'fas fa-question-circle',
            'points_required': 0,
            'category': 'questions',
            'color': 'bronze'
        },
        {
            'name': 'First Answer',
            'description': 'Provided your first answer',
            'icon': 'fas fa-comment',
            'points_required': 0,
            'category': 'answers',
            'color': 'bronze'
        },
        {
            'name': 'Curious Mind',
            'description': 'Asked 10 questions',
            'icon': 'fas fa-brain',
            'points_required': 50,
            'category': 'questions',
            'color': 'silver'
        },
        {
            'name': 'Helper',
            'description': 'Provided 10 helpful answers',
            'icon': 'fas fa-hands-helping',
            'points_required': 100,
            'category': 'answers',
            'color': 'silver'
        },
        {
            'name': 'Consistent Learner',
            'description': 'Maintained a 7-day learning streak',
            'icon': 'fas fa-fire',
            'points_required': 35,
            'category': 'consistency',
            'color': 'gold'
        },
        {
            'name': 'Expert',
            'description': 'Reached Level 5',
            'icon': 'fas fa-star',
            'points_required': 2500,
            'category': 'expertise',
            'color': 'gold'
        },
        {
            'name': 'Master',
            'description': 'Reached Level 10',
            'icon': 'fas fa-crown',
            'points_required': 10000,
            'category': 'expertise',
            'color': 'platinum'
        },
        {
            'name': 'Community Builder',
            'description': 'Helped 50 students with answers',
            'icon': 'fas fa-users',
            'points_required': 500,
            'category': 'community',
            'color': 'gold'
        }
    ]
    
    for achievement_data in default_achievements:
        Achievement.objects.get_or_create(
            name=achievement_data['name'],
            defaults=achievement_data
        )
