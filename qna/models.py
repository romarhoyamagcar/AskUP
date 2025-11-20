from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned to Admin'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        # Academic Subjects
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('economics', 'Economics'),
        ('psychology', 'Psychology'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('arts', 'Arts & Literature'),
        ('philosophy', 'Philosophy'),
        ('social_studies', 'Social Studies'),
        
        # Programming & Computer Science
        ('computer_science', 'Computer Science'),
        ('python', 'Python Programming'),
        ('javascript', 'JavaScript'),
        ('java', 'Java Programming'),
        ('cpp', 'C/C++ Programming'),
        ('csharp', 'C# Programming'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('data_science', 'Data Science'),
        ('machine_learning', 'Machine Learning'),
        ('artificial_intelligence', 'Artificial Intelligence'),
        ('database', 'Database & SQL'),
        ('algorithms', 'Algorithms & Data Structures'),
        ('software_engineering', 'Software Engineering'),
        ('cybersecurity', 'Cybersecurity'),
        ('networking', 'Computer Networking'),
        ('operating_systems', 'Operating Systems'),
        ('game_development', 'Game Development'),
        ('frontend', 'Frontend Development'),
        ('backend', 'Backend Development'),
        ('devops', 'DevOps & Cloud'),
        
        # General
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    details = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_questions')
    assigned_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_questions', limit_choices_to={'is_staff': True})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_private = models.BooleanField(default=False)  # Private questions only visible to author and assigned admin
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def get_admin_name(self):
        """Get the name of the assigned admin"""
        if self.assigned_admin:
            return f"{self.assigned_admin.first_name} {self.assigned_admin.last_name}".strip() or self.assigned_admin.username
        return "Unassigned"

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin_response = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer by {self.author}"

class AdminQuestionRecord(models.Model):
    """Track questions handled by each admin"""
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handled_questions', limit_choices_to={'is_staff': True})
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='admin_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_interactions')
    assigned_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    response_time_hours = models.FloatField(null=True, blank=True)  # Time taken to respond
    admin_notes = models.TextField(blank=True)  # Private admin notes
    student_satisfaction = models.IntegerField(null=True, blank=True, choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    
    class Meta:
        unique_together = ['admin', 'question']  # One admin per question
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.admin.username} handling {self.question.title[:50]}"
