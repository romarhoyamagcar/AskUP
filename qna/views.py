from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Question, Answer, AdminQuestionRecord
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Avg
from datetime import datetime
from users.gamification import GamificationManager
from users.models import Notification

# Home Page – show questions based on user role
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            # Admins see open/assigned questions plus anything directly assigned to them
            questions = Question.objects.filter(
                Q(status__in=['open', 'assigned']) | Q(assigned_admin=request.user)
            ).distinct().order_by('-created_at')
        else:
            # Students see their own questions plus public/open questions to keep the feed active
            questions = Question.objects.filter(
                Q(author=request.user) |
                Q(is_private=False, status='open')
            ).distinct().order_by('-created_at')
    else:
        # Anonymous users see public open questions only
        questions = Question.objects.filter(is_private=False, status='open').order_by('-created_at')[:10]

    context = {
        'questions': questions,
        'total_students': User.objects.filter(is_staff=False).count(),
        'total_admins': User.objects.filter(is_staff=True).count(),
        'total_questions': Question.objects.count(),
        'total_answers': Answer.objects.count(),
    }

    return render(request, 'qna/home.html', context)


def community_stats_api(request):
    data = {
        'total_students': User.objects.filter(is_staff=False).count(),
        'total_admins': User.objects.filter(is_staff=True).count(),
        'total_questions': Question.objects.count(),
        'total_answers': Answer.objects.count(),
        'average_rating': 4.9,
    }
    return JsonResponse({'success': True, 'data': data})

# Question Detail – view answers and add a new one
@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    # Check if user can view this question
    if question.is_private and not (request.user == question.author or request.user == question.assigned_admin or request.user.is_staff):
        messages.error(request, 'You do not have permission to view this question.')
        return redirect('home')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'claim_question' and request.user.is_staff:
            # Admin claims the question
            if not question.assigned_admin:
                question.assigned_admin = request.user
                question.status = 'assigned'
                question.assigned_at = timezone.now()
                question.save()
                
                # Create admin record
                AdminQuestionRecord.objects.create(
                    admin=request.user,
                    question=question,
                    student=question.author
                )
                
                messages.success(request, 'Question assigned to you successfully!')
            else:
                messages.error(request, 'This question is already assigned to another admin.')
        
        elif action == 'answer_question':
            content = request.POST.get("content")
            admin_notes = request.POST.get("admin_notes", "")
            
            if content:
                # Create the answer
                answer = Answer.objects.create(
                    question=question,
                    content=content,
                    author=request.user,
                    is_admin_response=request.user.is_staff
                )
                
                # Get or create user profile
                from users.views import get_or_create_profile
                profile = get_or_create_profile(request.user)
                
                # Award points for providing answer
                gamification_result = GamificationManager.award_points(
                    request.user,
                    'first_answer' if profile.answers_given == 0 else 'answer_given'
                )
                
                # Update user profile
                profile.answers_given += 1
                profile.save()
                
                # Notify question author about new answer
                if question.author != request.user:
                    Notification.objects.create(
                        user=question.author,
                        title='New Answer to Your Question!',
                        message=f'{request.user.first_name or request.user.username} answered your question "{question.title[:50]}..."',
                        notification_type='new_answer',
                        action_url=f'/question/{question.pk}/',
                        icon='fas fa-comment',
                        color='info'
                    )
                
                # Create notifications for achievements
                if gamification_result['new_achievements']:
                    for achievement in gamification_result['new_achievements']:
                        Notification.objects.create(
                            user=request.user,
                            title=f'Achievement Unlocked: {achievement.name}!',
                            message=f'Congratulations! You earned the "{achievement.name}" badge: {achievement.description}',
                            notification_type='achievement_earned',
                            icon=achievement.icon,
                            color='success'
                        )
                
                # Level up notification
                if gamification_result['level_up']:
                    Notification.objects.create(
                        user=request.user,
                        title=f'Level Up! You are now Level {gamification_result["new_level"]}',
                        message=f'Amazing progress! You\'ve reached Level {gamification_result["new_level"]} and earned {gamification_result["points_awarded"]} points!',
                        notification_type='level_up',
                        icon='fas fa-star',
                        color='warning'
                    )
                
                # If admin is answering, update question status and record
                if request.user.is_staff:
                    question.status = 'answered'
                    question.answered_at = timezone.now()
                    question.save()
                    
                    # Update admin record
                    try:
                        admin_record = AdminQuestionRecord.objects.get(admin=request.user, question=question)
                        admin_record.answered_at = timezone.now()
                        admin_record.admin_notes = admin_notes
                        
                        # Calculate response time
                        if admin_record.assigned_at:
                            time_diff = admin_record.answered_at - admin_record.assigned_at
                            admin_record.response_time_hours = time_diff.total_seconds() / 3600
                        
                        admin_record.save()
                    except AdminQuestionRecord.DoesNotExist:
                        # Create record if it doesn't exist (shouldn't happen)
                        AdminQuestionRecord.objects.create(
                            admin=request.user,
                            question=question,
                            student=question.author,
                            answered_at=timezone.now(),
                            admin_notes=admin_notes
                        )
                
                messages.success(request, 'Your answer has been posted!')
                return redirect('question_detail', pk=question.pk)
    
    # Get admin record if exists
    admin_record = None
    if request.user.is_staff:
        try:
            admin_record = AdminQuestionRecord.objects.get(admin=request.user, question=question)
        except AdminQuestionRecord.DoesNotExist:
            pass
    
    context = {
        'question': question,
        'admin_record': admin_record,
        'can_claim': request.user.is_staff and not question.assigned_admin,
        'is_assigned_admin': request.user == question.assigned_admin,
    }
    
    return render(request, 'qna/question_detail.html', context)

# Ask Question View
@login_required
def ask_question(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        category = request.POST.get('category')
        
        if title and details and category:
            question = Question.objects.create(
                title=title,
                details=details,
                category=category,
                author=request.user
            )
            
            # Get or create user profile
            from users.views import get_or_create_profile
            profile = get_or_create_profile(request.user)
            
            # Award points for asking question
            gamification_result = GamificationManager.award_points(
                request.user, 
                'first_question' if profile.questions_asked == 0 else 'question_asked'
            )
            
            # Update user profile
            profile.questions_asked += 1
            profile.save()
            
            # Create notifications for achievements
            if gamification_result['new_achievements']:
                for achievement in gamification_result['new_achievements']:
                    Notification.objects.create(
                        user=request.user,
                        title=f'Achievement Unlocked: {achievement.name}!',
                        message=f'Congratulations! You earned the "{achievement.name}" badge: {achievement.description}',
                        notification_type='achievement_earned',
                        icon=achievement.icon,
                        color='success'
                    )
            
            # Level up notification
            if gamification_result['level_up']:
                Notification.objects.create(
                    user=request.user,
                    title=f'Level Up! You are now Level {gamification_result["new_level"]}',
                    message=f'Amazing progress! You\'ve reached Level {gamification_result["new_level"]} and earned {gamification_result["points_awarded"]} points!',
                    notification_type='level_up',
                    icon='fas fa-star',
                    color='warning'
                )
            
            success_msg = f'Your question has been posted! You earned {gamification_result["points_awarded"]} points.'
            if gamification_result['level_up']:
                success_msg += f' Level up! You are now Level {gamification_result["new_level"]}!'
            
            messages.success(request, success_msg)
            return redirect('home')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Pass categories to template
    categories = Question.CATEGORY_CHOICES
    return render(request, 'qna/ask_question.html', {'categories': categories})

@login_required
def delete_question(request, pk):
    """Delete a question (only by author or admin)"""
    question = get_object_or_404(Question, pk=pk)
    
    # Check permissions - only author or admin can delete
    if request.user != question.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this question.')
        return redirect('question_detail', pk=pk)
    
    if request.method == 'POST':
        question_title = question.title
        question.delete()
        
        # Award negative points for deleting (to prevent abuse)
        if request.user == question.author:
            from users.views import get_or_create_profile
            profile = get_or_create_profile(request.user)
            if profile.questions_asked > 0:
                profile.questions_asked -= 1
                profile.save()
            
            # Deduct points (but don't let total points go below 0)
            points_obj = GamificationManager.get_or_create_points(request.user)
            if points_obj.total_points >= 3:  # Only deduct if user has enough points
                GamificationManager.award_points(request.user, 'question_deleted', -3)
            else:
                # If user has less than 3 points, just set to 0
                points_obj.total_points = 0
                points_obj.questions_points = max(0, points_obj.questions_points - 3)
                points_obj.save()
        
        messages.success(request, f'Question "{question_title}" has been deleted.')
        return redirect('home')
    
    context = {
        'question': question,
        'can_delete': True
    }
    
    return render(request, 'qna/delete_question.html', context)

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff

# Admin Question Management
@login_required
@user_passes_test(is_admin)
def admin_question_queue(request):
    """Admin view for managing question queue"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'open')
    category_filter = request.GET.get('category', 'all')
    
    # Base queryset
    questions = Question.objects.all()
    
    # Apply filters
    if status_filter != 'all':
        questions = questions.filter(status=status_filter)
    
    if category_filter != 'all':
        questions = questions.filter(category=category_filter)
    
    # Order by priority and creation date
    questions = questions.order_by('-priority', '-created_at')
    
    # Get admin's assigned questions
    my_questions = Question.objects.filter(assigned_admin=request.user).order_by('-assigned_at')
    
    # Statistics
    stats = {
        'total_open': Question.objects.filter(status='open').count(),
        'my_assigned': Question.objects.filter(assigned_admin=request.user).count(),
        'my_answered': AdminQuestionRecord.objects.filter(admin=request.user, answered_at__isnull=False).count(),
        'pending_response': Question.objects.filter(assigned_admin=request.user, status='assigned').count(),
    }
    
    context = {
        'questions': questions,
        'my_questions': my_questions,
        'stats': stats,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': Question.CATEGORY_CHOICES,
    }
    
    return render(request, 'qna/admin_question_queue.html', context)

@login_required
@user_passes_test(is_admin)
def admin_my_records(request):
    """Admin's personal question handling records"""
    records = AdminQuestionRecord.objects.filter(admin=request.user).order_by('-assigned_at')
    
    # Calculate statistics
    total_handled = records.count()
    answered_count = records.filter(answered_at__isnull=False).count()
    avg_response_time = records.filter(response_time_hours__isnull=False).aggregate(
        avg_time=Avg('response_time_hours')
    )['avg_time'] or 0
    
    # Student satisfaction average
    satisfaction_avg = records.filter(student_satisfaction__isnull=False).aggregate(
        avg_rating=Avg('student_satisfaction')
    )['avg_rating'] or 0
    
    stats = {
        'total_handled': total_handled,
        'answered_count': answered_count,
        'pending_count': total_handled - answered_count,
        'avg_response_time': round(avg_response_time, 1),
        'satisfaction_avg': round(satisfaction_avg, 1),
    }
    
    context = {
        'records': records,
        'stats': stats,
    }
    
    return render(request, 'qna/admin_my_records.html', context)

@login_required
def student_my_questions(request):
    """Student's personal question dashboard"""
    if request.user.is_staff:
        return redirect('admin_question_queue')
    
    questions = Question.objects.filter(author=request.user).order_by('-created_at')
    
    # Statistics
    stats = {
        'total_questions': questions.count(),
        'open_questions': questions.filter(status='open').count(),
        'assigned_questions': questions.filter(status='assigned').count(),
        'answered_questions': questions.filter(status='answered').count(),
    }
    
    context = {
        'questions': questions,
        'stats': stats,
    }
    
    return render(request, 'qna/student_my_questions.html', context)

def about(request):
    """About page view"""
    return render(request, 'about.html')
