"""
Enhanced messaging views for peer-to-peer communication
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Conversation, ConversationMessage, MessageReadStatus, Notification
from .forms import MessageForm
from qna.models import Question


@login_required
def messenger_home(request):
    """Main messenger interface showing all conversations"""
    # Get user's conversations
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_active=True
    ).annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-last_message_time')
    
    # Get other students for starting new conversations
    other_students = User.objects.filter(
        is_active=True
    ).exclude(id=request.user.id).order_by('first_name', 'username')
    
    context = {
        'conversations': conversations,
        'other_students': other_students,
        'active_conversation': None
    }
    
    return render(request, 'users/messenger/home.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """View and send messages in a specific conversation"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Mark messages as read
    unread_messages = conversation.messages.filter(
        is_read=False
    ).exclude(sender=request.user)
    
    for message in unread_messages:
        message.is_read = True
        message.save()
        # Create read status
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
    
    # Get messages with pagination
    messages_list = conversation.messages.all().select_related('sender')
    paginator = Paginator(messages_list, 50)
    page_number = request.GET.get('page', paginator.num_pages)  # Start from last page
    page_messages = paginator.get_page(page_number)
    
    # Handle new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            new_message = ConversationMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            
            # Create notifications for other participants
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    title=f"New message from {request.user.first_name or request.user.username}",
                    message=content[:100] + "..." if len(content) > 100 else content,
                    notification_type='message_received',
                    action_url=f'/messenger/conversation/{conversation.id}/',
                    icon='fas fa-comment',
                    color='primary'
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': new_message.id,
                        'content': new_message.content,
                        'sender': new_message.sender.first_name or new_message.sender.username,
                        'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    # Get all conversations for sidebar
    all_conversations = Conversation.objects.filter(
        participants=request.user,
        is_active=True
    ).annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-last_message_time')
    
    context = {
        'conversation': conversation,
        'messages': page_messages,
        'conversations': all_conversations,
        'active_conversation': conversation
    }
    
    return render(request, 'users/messenger/conversation.html', context)


@login_required
def start_conversation(request):
    """Start a new conversation with another user"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        message_content = request.POST.get('content', '').strip()
        conversation_type = request.POST.get('conversation_type', 'direct_message')
        
        if not recipient_id or not message_content:
            messages.error(request, 'Please select a recipient and enter a message.')
            return redirect('messenger_home')
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            messages.error(request, 'Selected user not found.')
            return redirect('messenger_home')
        
        # Check if conversation already exists between these users
        existing_conversation = Conversation.objects.filter(
            participants=request.user,
            conversation_type='direct_message'
        ).filter(participants=recipient).first()
        
        if existing_conversation:
            # Add message to existing conversation
            ConversationMessage.objects.create(
                conversation=existing_conversation,
                sender=request.user,
                content=message_content
            )
            existing_conversation.updated_at = timezone.now()
            existing_conversation.save()
            
            return redirect('conversation_detail', conversation_id=existing_conversation.id)
        else:
            # Create new conversation
            title = f"Chat between {request.user.first_name or request.user.username} and {recipient.first_name or recipient.username}"
            
            conversation = Conversation.objects.create(
                title=title,
                conversation_type=conversation_type,
                created_by=request.user
            )
            
            # Add participants
            conversation.participants.add(request.user, recipient)
            
            # Create first message
            ConversationMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_content
            )
            
            # Create notification for recipient
            Notification.objects.create(
                user=recipient,
                title=f"New message from {request.user.first_name or request.user.username}",
                message=message_content[:100] + "..." if len(message_content) > 100 else message_content,
                notification_type='message_received',
                action_url=f'/messenger/conversation/{conversation.id}/',
                icon='fas fa-comment',
                color='primary'
            )
            
            messages.success(request, f'Conversation started with {recipient.first_name or recipient.username}!')
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    return redirect('messenger_home')


@login_required
def start_question_conversation(request, question_id):
    """Start a conversation related to a specific question"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('content', '').strip()
        
        if not message_content:
            messages.error(request, 'Please enter a message.')
            return redirect('question_detail', pk=question_id)
        
        # Create conversation for this question
        title = f"Help with: {question.title[:50]}..."
        
        conversation = Conversation.objects.create(
            title=title,
            conversation_type='question_help',
            created_by=request.user,
            related_question=question
        )
        
        # Add question author and current user as participants
        conversation.participants.add(request.user)
        if question.author != request.user:
            conversation.participants.add(question.author)
        
        # If user is admin, add them; if student, add available admins
        if request.user.is_staff:
            # Admin is helping
            pass
        else:
            # Student needs help, add admins
            admins = User.objects.filter(is_staff=True, is_active=True)
            for admin in admins:
                conversation.participants.add(admin)
        
        # Create first message
        ConversationMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            content=message_content
        )
        
        # Create notifications for participants
        for participant in conversation.participants.exclude(id=request.user.id):
            Notification.objects.create(
                user=participant,
                title=f"Question help request: {question.title[:30]}...",
                message=message_content[:100] + "..." if len(message_content) > 100 else message_content,
                notification_type='message_received',
                action_url=f'/messenger/conversation/{conversation.id}/',
                icon='fas fa-question-circle',
                color='success'
            )
        
        messages.success(request, 'Help conversation started! Check your messages.')
        return redirect('conversation_detail', conversation_id=conversation.id)
    
    return redirect('question_detail', pk=question_id)


@login_required
@require_POST
def get_conversation_messages(request, conversation_id):
    """AJAX endpoint to get latest messages"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    last_message_id = request.POST.get('last_message_id', 0)
    
    new_messages = conversation.messages.filter(
        id__gt=last_message_id
    ).select_related('sender')
    
    messages_data = []
    for message in new_messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender': message.sender.first_name or message.sender.username,
            'sender_id': message.sender.id,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_own': message.sender == request.user
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })


@login_required
def search_users(request):
    """Search for users to start conversations with"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(username__icontains=query),
        is_active=True
    ).exclude(id=request.user.id)[:10]
    
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'username': user.username,
            'is_staff': user.is_staff
        })
    
    return JsonResponse({'users': users_data})
