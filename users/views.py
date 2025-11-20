from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Message, MessageThread, UserProfile, StudentActivity, Notification, StudentPoints, Achievement
from qna.models import Question, Answer
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.timesince import timesince
from django.core.paginator import Paginator
from django.conf import settings
from .forms import (
    SignUpForm, AdminSignUpForm, ProfileUpdateForm, SecuritySettingsForm,
    CustomPasswordChangeForm, ThemePreferenceForm, NotificationSettingsForm,
    MessageForm, MessageReplyForm
)
from .gamification import GamificationManager

# Import enhanced messaging views
from .messaging_views import (
    messenger_home, conversation_detail, start_conversation, 
    start_question_conversation, get_conversation_messages, search_users
)


# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Helper function to get or create user profile
def get_or_create_profile(user):
    """Safely get or create UserProfile for user"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        # Initialize gamification for new profile
        GamificationManager.get_or_create_points(user)
    return profile

# Authentication Views
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Create onboarding notifications for newcomers
            notifications_payload = [
                {
                    'title': 'Welcome to AskUP! 🎉',
                    'message': 'Explore your personalized dashboard to track streaks, badges, and activity.',
                    'notification_type': 'system_update',
                    'icon': 'fas fa-handshake',
                    'color': 'success',
                    'action_url': reverse('student_dashboard') if user.is_authenticated else reverse('login')
                },
                {
                    'title': 'Ask your first question',
                    'message': 'Head over to the Ask Question page to get help from students and admins.',
                    'notification_type': 'new_answer',
                    'icon': 'fas fa-question-circle',
                    'color': 'primary',
                    'action_url': reverse('ask_question')
                },
                {
                    'title': 'Chat with the community',
                    'message': 'Use Messenger to start conversations with peers or admins for quick support.',
                    'notification_type': 'message_received',
                    'icon': 'fas fa-comments',
                    'color': 'info',
                    'action_url': reverse('messenger_home')
                },
                {
                    'title': 'Track your progress',
                    'message': 'Visit the Gamification hub to view achievements, levels, and leaderboards.',
                    'notification_type': 'achievement_earned',
                    'icon': 'fas fa-trophy',
                    'color': 'warning',
                    'action_url': reverse('gamification_dashboard')
                }
            ]

            for payload in notifications_payload:
                Notification.objects.create(user=user, **payload)

            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

# Admin Authentication Views
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome to Admin Panel, {user.first_name or user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient privileges.')
    
    return render(request, 'users/admin_login.html')

def admin_signup(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Admin account created for {username}! You can now log in to the admin panel.')
            return redirect('admin_login')
    else:
        form = AdminSignUpForm()
    
    return render(request, 'users/admin_signup.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    from qna.models import Question, Answer
    
    # Get statistics
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    total_admins = User.objects.filter(is_staff=True).count()
    
    # Get recent questions with prefetch to avoid slicing issues
    recent_questions = Question.objects.select_related('author').prefetch_related('answers').order_by('-created_at')[:10]
    
    # Get recent users
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    
    # Get messaging statistics (handle potential missing Message model)
    try:
        total_messages = Message.objects.count()
        pending_messages = Message.objects.filter(status='pending').count()
        recent_messages = Message.objects.select_related('sender').order_by('-created_at')[:5]
    except:
        total_messages = 0
        pending_messages = 0
        recent_messages = []
    
    # Get student activities (handle potential missing StudentActivity model)
    try:
        recent_activities = StudentActivity.objects.select_related('user').order_by('-timestamp')[:10]
    except:
        recent_activities = []
    
    context = {
        'total_questions': total_questions,
        'total_answers': total_answers,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_messages': total_messages,
        'pending_messages': pending_messages,
        'recent_questions': recent_questions,
        'recent_users': recent_users,
        'recent_messages': recent_messages,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'users/admin_dashboard.html', context)


# Messaging Views
@login_required
def send_message(request):
    """Students send messages to admins"""
    if request.user.is_staff:
        messages.error(request, 'Admins cannot send messages through this form.')
        return redirect('admin_dashboard')
    
    # Check if user has messaging privileges
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.can_message_admins:
        messages.error(request, 'You do not have permission to send messages to admins.')
        return redirect('home')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Update user profile
            profile.messages_sent += 1
            profile.last_active = timezone.now()
            profile.save()
            
            # Log activity (handle potential missing StudentActivity model)
            try:
                StudentActivity.objects.create(
                    student=request.user,
                    activity_type='message_sent',
                    description=f'Sent message: {message.subject}',
                    related_message_id=message.id
                )
            except:
                pass  # StudentActivity model might not exist
            
            messages.success(request, 'Your message has been sent to the administrators.')
            return redirect('view_messages')  # Redirect after successful submission
    else:
        form = MessageForm()
    
    return render(request, 'users/send_message.html', {'form': form})

@login_required
def view_messages(request):
    """View user's messages"""
    if request.user.is_staff:
        # Admin view: all messages with statistics
        user_messages = Message.objects.all().order_by('-created_at')
        
        # Statistics for admin view
        stats = {
            'total': Message.objects.count(),
            'pending': Message.objects.filter(status='pending').count(),
            'in_progress': Message.objects.filter(status='in_progress').count(),
            'resolved': Message.objects.filter(status='resolved').count(),
            'high_priority': Message.objects.filter(priority='high').count(),
        }
        
        context = {
            'messages': user_messages,
            'stats': stats,
            'total_messages': stats['total'],
            'pending_messages': stats['pending'],
            'in_progress_messages': stats['in_progress'],
            'resolved_messages': stats['resolved'],
            'status_filter': 'all',
            'priority_filter': 'all',
        }
        template = 'users/admin_messages.html'
    else:
        # Student view: only their messages
        user_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
        context = {'messages': user_messages}
        template = 'users/student_messages.html'
    
    return render(request, template, context)


@login_required
def get_messages_json(request):
    """Return latest messages and unread count for realtime UI updates"""
    if request.user.is_staff:
        queryset = Message.objects.all()
    else:
        queryset = Message.objects.filter(sender=request.user)

    total_count = queryset.count()
    unread_count = queryset.filter(is_read=False).count()

    limit = int(request.GET.get('limit', 5))
    messages_qs = queryset.select_related('sender', 'recipient').order_by('-created_at')[:limit]

    messages_data = []
    for message in messages_qs:
        sender_initial = (message.sender.first_name[:1] if message.sender.first_name else message.sender.username[:1]).upper()
        messages_data.append({
            'id': message.id,
            'subject': message.subject,
            'preview': Truncator(message.content).chars(140),
            'sender_name': message.sender.get_full_name() or message.sender.username,
             'sender_initial': sender_initial,
            'sender_is_staff': message.sender.is_staff,
            'is_read': message.is_read,
            'message_type': message.message_type,
            'status': message.status,
            'priority': message.priority,
            'created_display': f"{timesince(message.created_at)} ago",
            'detail_url': reverse('message_detail', args=[message.id]),
            'reply_url': reverse('reply_message', args=[message.id]),
            'mark_read_url': reverse('mark_message_read', args=[message.id]),
            'detail_url': reverse('message_detail', args=[message.id])
        })

    return JsonResponse({
        'messages': messages_data,
        'unread_count': unread_count,
        'total_count': total_count
    })


@login_required
@require_POST
def mark_message_read(request, message_id):
    """Mark a message as read (students or admins)"""
    message = get_object_or_404(Message, id=message_id)

    if not request.user.is_staff and message.sender != request.user:
        return JsonResponse({'success': False, 'error': 'Not allowed'}, status=403)

    if not message.is_read:
        message.is_read = True
        message.save(update_fields=['is_read'])

    return JsonResponse({'success': True})

@login_required
def message_detail(request, message_id):
    """View message details and thread"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check permissions
    if not request.user.is_staff and message.sender != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('message_list')
    
    # Mark as read
    if not message.is_read:
        message.is_read = True
        message.save()
    
    # Get thread
    thread = MessageThread.objects.filter(original_message=message)
    
    # Handle reply
    if request.method == 'POST':
        reply_form = MessageReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.original_message = message
            reply.sender = request.user
            reply.save()
            
            # Update message status if admin replies
            if request.user.is_staff and message.status == 'pending':
                message.status = 'in_progress'
                message.save()
            
            messages.success(request, 'Reply sent successfully.')
            return redirect('message_detail', message_id=message.id)
    else:
        reply_form = MessageReplyForm()
    
    context = {
        'message': message,
        'thread': thread,
        'reply_form': reply_form,
    }
    
    return render(request, 'users/message_detail.html', context)

@login_required
def reply_message(request, message_id):
    """Reply to a specific message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check permissions
    if not request.user.is_staff and message.sender != request.user:
        messages.error(request, 'You do not have permission to reply to this message.')
        return redirect('view_messages')
    
    if request.method == 'POST':
        reply_form = MessageReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.original_message = message
            reply.sender = request.user
            reply.save()
            
            # Update message status if admin replies
            if request.user.is_staff and message.status == 'pending':
                message.status = 'in_progress'
                message.save()
            
            messages.success(request, 'Reply sent successfully.')
            return redirect('message_detail', message_id=message.id)
    
    return redirect('message_detail', message_id=message.id)

@login_required
@user_passes_test(is_admin)
def admin_message_detail(request, message_id):
    """Admin detailed view of a message"""
    message = get_object_or_404(Message, id=message_id)
    thread = MessageThread.objects.filter(original_message=message)
    
    # Mark as read
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {
        'message': message,
        'thread': thread,
        'can_update_status': True,
    }
    
    return render(request, 'users/admin_message_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_message_management(request):
    """Admin view for managing all messages"""
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    
    messages_queryset = Message.objects.all()
    
    if status_filter != 'all':
        messages_queryset = messages_queryset.filter(status=status_filter)
    
    if priority_filter != 'all':
        messages_queryset = messages_queryset.filter(priority=priority_filter)
    
    messages_list = messages_queryset.order_by('-created_at')
    
    # Statistics
    stats = {
        'total': Message.objects.count(),
        'pending': Message.objects.filter(status='pending').count(),
        'in_progress': Message.objects.filter(status='in_progress').count(),
        'resolved': Message.objects.filter(status='resolved').count(),
        'high_priority': Message.objects.filter(priority='high').count(),
    }
    
    context = {
        'messages': messages_list,
        'stats': stats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'users/admin_message_management.html', context)

@login_required
@user_passes_test(is_admin)
def update_message_status(request, message_id):
    """Admin updates message status"""
    if request.method == 'POST':
        message = get_object_or_404(Message, id=message_id)
        new_status = request.POST.get('status')
        admin_response = request.POST.get('admin_response', '')
        admin_notes = request.POST.get('admin_notes', '')
        
        message.status = new_status
        if admin_response:
            message.admin_response = admin_response
        if admin_notes:
            message.admin_notes = admin_notes
        
        if new_status == 'resolved':
            message.resolved_by = request.user
            message.resolved_at = timezone.now()
        
        message.save()
        
        messages.success(request, 'Message status updated successfully.')
        return redirect('admin_message_management')
    
    return redirect('admin_message_management')

@login_required
def student_dashboard(request):
    """Enhanced student dashboard with messaging and activity"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's messages (handle potential missing Message model)
    try:
        all_user_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
        user_messages = all_user_messages[:5]
        unread_messages_count = all_user_messages.filter(is_read=False).count()
    except:
        user_messages = []
        unread_messages_count = 0
    
    # Get user's questions and answers
    from qna.models import Question, Answer
    user_questions = Question.objects.filter(author=request.user).select_related('author').prefetch_related('answers').order_by('-created_at')[:5]
    user_answers = Answer.objects.filter(author=request.user).select_related('author', 'question').order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'user_messages': user_messages,
        'user_questions': user_questions,
        'user_answers': user_answers,
        'unread_messages': unread_messages_count,
    }
    
    return render(request, 'users/student_dashboard.html', context)

# Initialize gamification system for new users
def initialize_user_gamification(user):
    """Initialize gamification data for new user"""
    # Create StudentPoints if it doesn't exist
    GamificationManager.get_or_create_points(user)
    
    # Create default achievements if they don't exist
    from .gamification import create_default_achievements
    create_default_achievements()

# Settings Views
@login_required
def user_settings(request):
    """Main settings page with tabs for different settings categories"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
        'active_tab': request.GET.get('tab', 'profile')
    }
    
    return render(request, 'users/settings.html', context)

@login_required
def profile_settings(request):
    """Profile information settings"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Update profile fields
            profile.bio = form.cleaned_data.get('bio', '')
            profile.phone = form.cleaned_data.get('phone', '')
            profile.location = form.cleaned_data.get('location', '')
            profile.website = form.cleaned_data.get('website', '')
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user, initial={
            'bio': profile.bio,
            'phone': profile.phone,
            'location': profile.location,
            'website': profile.website,
        })
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'users/profile_settings.html', context)

@login_required
def security_settings(request):
    """Security and privacy settings"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = SecuritySettingsForm(request.POST)
        if form.is_valid():
            profile.show_email_publicly = form.cleaned_data['show_email_publicly']
            profile.show_real_name = form.cleaned_data['show_real_name']
            profile.allow_messages = form.cleaned_data['allow_messages']
            profile.email_notifications = form.cleaned_data['email_notifications']
            profile.save()
            
            messages.success(request, 'Security settings updated successfully!')
            return redirect('security_settings')
    else:
        form = SecuritySettingsForm(initial={
            'show_email_publicly': profile.show_email_publicly,
            'show_real_name': profile.show_real_name,
            'allow_messages': profile.allow_messages,
            'email_notifications': profile.email_notifications,
        })
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'users/security_settings.html', context)

@login_required
def password_change_view(request):
    """Password change with enhanced security"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('password_change_view')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/password_change.html', context)

@login_required
def theme_settings(request):
    """Theme and appearance settings"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ThemePreferenceForm(request.POST)
        if form.is_valid():
            profile.theme_preference = form.cleaned_data['theme']
            profile.compact_mode = form.cleaned_data['compact_mode']
            profile.animations_enabled = form.cleaned_data['animations']
            profile.save()
            
            # Set theme in session for immediate effect
            request.session['theme'] = profile.theme_preference
            request.session['compact_mode'] = profile.compact_mode
            request.session['animations'] = profile.animations_enabled
            
            messages.success(request, 'Theme settings updated successfully!')
            return redirect('theme_settings')
    else:
        form = ThemePreferenceForm(initial={
            'theme': profile.theme_preference,
            'compact_mode': profile.compact_mode,
            'animations': profile.animations_enabled,
        })
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'users/theme_settings.html', context)

@login_required
def notification_settings(request):
    """Notification preferences"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST)
        if form.is_valid():
            profile.email_new_answer = form.cleaned_data['email_new_answer']
            profile.email_new_message = form.cleaned_data['email_new_message']
            profile.email_weekly_digest = form.cleaned_data['email_weekly_digest']
            profile.browser_notifications = form.cleaned_data['browser_notifications']
            profile.save()
            
            messages.success(request, 'Notification settings updated successfully!')
            return redirect('notification_settings')
    else:
        form = NotificationSettingsForm(initial={
            'email_new_answer': profile.email_new_answer,
            'email_new_message': profile.email_new_message,
            'email_weekly_digest': profile.email_weekly_digest,
            'browser_notifications': profile.browser_notifications,
        })
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'users/notification_settings.html', context)

@login_required
@require_POST
def toggle_password_visibility(request):
    """AJAX endpoint to toggle password visibility"""
    show_password = request.POST.get('show_password') == 'true'
    
    # Store preference in session
    request.session['show_password_fields'] = show_password
    
    return JsonResponse({
        'success': True,
        'show_password': show_password
    })

@login_required
def export_data(request):
    """Export user data for GDPR compliance"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Collect user data
    user_data = {
        'personal_info': {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined.isoformat(),
        },
        'profile': {
            'bio': profile.bio,
            'location': profile.location,
            'phone': profile.phone,
            'website': profile.website,
        },
        'settings': {
            'theme_preference': profile.theme_preference,
            'email_notifications': profile.email_notifications,
            'show_email_publicly': profile.show_email_publicly,
        },
        'activity': {
            'questions_asked': profile.questions_asked,
            'answers_given': profile.answers_given,
            'messages_sent': profile.messages_sent,
        }
    }
    
    return JsonResponse(user_data)

# Gamification Views
@login_required
def gamification_dashboard(request):
    """Student gamification dashboard"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Get user stats
    user_stats = GamificationManager.get_user_stats(request.user)
    
    # Get leaderboard preview (top 5)
    leaderboard = GamificationManager.get_leaderboard(limit=5)
    
    context = {
        'user_stats': user_stats,
        'leaderboard': leaderboard
    }
    
    return render(request, 'users/gamification_dashboard.html', context)

@login_required
def leaderboard(request):
    """Full leaderboard view"""
    category = request.GET.get('category', 'total')
    
    # Get leaderboard
    leaders = GamificationManager.get_leaderboard(limit=50, category=category)
    
    # Get user's rank
    user_rank = GamificationManager.get_user_rank(request.user)
    
    context = {
        'leaders': leaders,
        'user_rank': user_rank,
        'current_category': category,
        'categories': [
            ('total', 'Total Points'),
            ('questions', 'Questions Asked'),
            ('answers', 'Answers Given'),
            ('level', 'Highest Level'),
            ('streak', 'Current Streak')
        ]
    }
    
    return render(request, 'users/leaderboard.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    (Notification.objects
        .filter(user=request.user, is_read=False)
        .update(is_read=True, read_at=timezone.now()))
    return JsonResponse({'success': True})


@login_required
@require_POST
def complete_onboarding(request):
    profile = get_or_create_profile(request.user)
    if profile.show_onboarding:
        profile.show_onboarding = False
        profile.onboarding_completed_at = timezone.now()
        profile.save(update_fields=['show_onboarding', 'onboarding_completed_at'])
    return JsonResponse({'success': True})

@login_required
def notifications_list(request):
    """List all notifications for user"""
    # Get all notifications for user (without slicing first)
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all unread notifications as read when viewing (bulk update for efficiency)
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    # Now get the limited set for display
    notifications = all_notifications[:20]
    
    context = {
        'notifications': notifications
    }
    
    return render(request, 'users/notifications.html', context)

@login_required
@user_passes_test(is_admin)
def admin_my_records(request):
    """Admin records and activity tracking"""
    # Get admin statistics
    messages_handled = Message.objects.filter(resolved_by=request.user).count()
    questions_answered = Answer.objects.filter(author=request.user).count() if 'qna' in settings.INSTALLED_APPS else 0
    conversations_started = request.user.created_conversations.count() if hasattr(request.user, 'created_conversations') else 0
    
    # Calculate students helped (unique users from resolved messages)
    students_helped = Message.objects.filter(resolved_by=request.user).values('sender').distinct().count()
    
    # Recent activities (placeholder - would need proper activity tracking)
    recent_activities = []
    
    # Performance metrics (placeholder)
    response_rate = 85
    avg_response_time = "2.5 hours"
    satisfaction_rate = 92
    total_score = messages_handled * 10 + questions_answered * 5
    
    context = {
        'messages_handled': messages_handled,
        'questions_answered': questions_answered,
        'conversations_started': conversations_started,
        'students_helped': students_helped,
        'recent_activities': recent_activities,
        'response_rate': response_rate,
        'avg_response_time': avg_response_time,
        'satisfaction_rate': satisfaction_rate,
        'total_score': total_score,
    }
    
    return render(request, 'qna/admin_my_records.html', context)

@login_required
def get_notifications_json(request):
    """Get notifications as JSON for AJAX requests"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    unread_total = Notification.objects.filter(user=request.user, is_read=False).count()
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'icon': notification.icon,
            'color': notification.color,
            'action_url': notification.action_url,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_total
    })
