from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)  # For students
    department = models.CharField(max_length=100, blank=True)
    year_level = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Privacy Settings
    show_email_publicly = models.BooleanField(default=False)
    show_real_name = models.BooleanField(default=True)
    allow_messages = models.BooleanField(default=True)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    email_new_answer = models.BooleanField(default=True)
    email_new_message = models.BooleanField(default=True)
    email_weekly_digest = models.BooleanField(default=False)
    browser_notifications = models.BooleanField(default=True)
    
    # Theme Settings
    theme_preference = models.CharField(
        max_length=10, 
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')], 
        default='light'
    )
    compact_mode = models.BooleanField(default=False)
    animations_enabled = models.BooleanField(default=True)

    # Student privileges
    can_message_admins = models.BooleanField(default=True)
    can_post_questions = models.BooleanField(default=True)
    can_answer_questions = models.BooleanField(default=True)

    # Onboarding status
    show_onboarding = models.BooleanField(default=True)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Activity tracking
    questions_asked = models.IntegerField(default=0)
    answers_given = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('question_inquiry', 'Question Inquiry'),
        ('general_help', 'General Help'),
        ('technical_support', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('complaint', 'Complaint'),
        ('peer_chat', 'Peer Chat'),
        ('study_group', 'Study Group'),
        ('announcement', 'Announcement'),
        ('question_answer', 'Question Answer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general_help')
    content = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    
    # Admin feedback fields
    admin_response = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_messages')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username}: {self.subject[:50]}"

class MessageThread(models.Model):
    """For conversation threads between students and admins"""
    original_message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='thread')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply from {self.sender.username} at {self.created_at}"

class StudentActivity(models.Model):
    """Track student activities for admin insights"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)  # 'question_asked', 'answer_given', 'message_sent', etc.
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    related_question_id = models.IntegerField(null=True, blank=True)
    related_message_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.student.username} - {self.activity_type} at {self.timestamp}"

# Gamification Models
class Achievement(models.Model):
    """Achievement badges that students can earn"""
    CATEGORY_CHOICES = [
        ('questions', 'Question Asking'),
        ('answers', 'Answer Providing'),
        ('helping', 'Helping Others'),
        ('consistency', 'Regular Participation'),
        ('expertise', 'Subject Expertise'),
        ('community', 'Community Building')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')  # Font Awesome icon class
    points_required = models.IntegerField(default=0)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=20, default='gold')  # Badge color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class StudentPoints(models.Model):
    """Point system for gamification"""
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    questions_points = models.IntegerField(default=0)
    answers_points = models.IntegerField(default=0)
    helping_points = models.IntegerField(default=0)
    consistency_points = models.IntegerField(default=0)
    
    # Level system
    level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)
    
    # Streak tracking
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.total_points} points (Level {self.level})"
    
    def calculate_level(self):
        """Calculate level based on total points"""
        # Level formula: Level = sqrt(max(0, total_points) / 100) + 1
        # Ensure points are not negative to avoid math domain error
        import math
        safe_points = max(0, self.total_points)
        return int(math.sqrt(safe_points / 100)) + 1
    
    def points_to_next_level(self):
        """Calculate points needed for next level"""
        next_level = self.level + 1
        points_needed = (next_level - 1) ** 2 * 100
        current_points = max(0, self.total_points)  # Ensure non-negative
        return max(0, points_needed - current_points)
    
    def update_level(self):
        """Update level based on current points"""
        new_level = self.calculate_level()
        if new_level > self.level:
            self.level = new_level
            self.save()
            return True  # Level up occurred
        return False

class StudentAchievement(models.Model):
    """Track achievements earned by students"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.FloatField(default=100.0)  # For partial achievements
    
    class Meta:
        unique_together = ['student', 'achievement']
    
    def __str__(self):
        return f"{self.student.username} - {self.achievement.name}"

class LearningStreak(models.Model):
    """Track daily learning streaks"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks')
    date = models.DateField()
    activities_count = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} ({self.activities_count} activities)"

# Notification System
class Notification(models.Model):
    """Real-time notifications for users"""
    NOTIFICATION_TYPES = [
        ('new_answer', 'New Answer'),
        ('question_assigned', 'Question Assigned'),
        ('achievement_earned', 'Achievement Earned'),
        ('level_up', 'Level Up'),
        ('message_received', 'Message Received'),
        ('streak_milestone', 'Streak Milestone'),
        ('challenge_available', 'Challenge Available'),
        ('system_update', 'System Update')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=20, default='primary')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_new_answer = models.BooleanField(default=True)
    email_achievement = models.BooleanField(default=True)
    email_level_up = models.BooleanField(default=True)
    email_weekly_digest = models.BooleanField(default=False)
    
    # Browser notifications
    browser_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    
    # Frequency settings
    digest_frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ], default='immediate')
    
    def __str__(self):
        return f"{self.user.username}'s notification preferences"

# Enhanced Messaging System for Peer-to-Peer Communication
class Conversation(models.Model):
    """Conversation between users (students and/or admins)"""
    CONVERSATION_TYPES = [
        ('direct_message', 'Direct Message'),
        ('study_group', 'Study Group'),
        ('question_help', 'Question Help'),
        ('announcement', 'Announcement'),
    ]
    
    participants = models.ManyToManyField(User, related_name='conversations')
    title = models.CharField(max_length=200)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES, default='direct_message')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # For question-related conversations
    related_question = models.ForeignKey('qna.Question', on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_conversation_type_display()}"
    
    def get_last_message(self):
        return self.messages.last()
    
    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class ConversationMessage(models.Model):
    """Individual messages within a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # File attachments (optional)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

class MessageReadStatus(models.Model):
    """Track read status for each user in conversation"""
    message = models.ForeignKey(ConversationMessage, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} read message at {self.read_at}"
