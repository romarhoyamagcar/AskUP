from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # Admin URLs
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/signup/', views.admin_signup, name='admin_signup'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Messaging URLs
    path('send-message/', views.send_message, name='send_message'),
    path('messages/', views.view_messages, name='view_messages'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/reply/', views.reply_message, name='reply_message'),
    path('messages/json/', views.get_messages_json, name='get_messages_json'),
    path('messages/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
    
    # Admin Message Management
    path('admin/messages/', views.admin_message_management, name='admin_message_management'),
    path('admin/messages/<int:message_id>/', views.admin_message_detail, name='admin_message_detail'),
    path('admin/messages/<int:message_id>/update/', views.update_message_status, name='update_message_status'),
    
    # Student Dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Settings URLs
    path('settings/', views.user_settings, name='user_settings'),
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    path('settings/security/', views.security_settings, name='security_settings'),
    path('settings/password/', views.password_change_view, name='password_change'),
    path('settings/theme/', views.theme_settings, name='theme_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/toggle-password/', views.toggle_password_visibility, name='toggle_password_visibility'),
    path('settings/export-data/', views.export_data, name='export_data'),
    
    # Gamification URLs
    path('progress/', views.gamification_dashboard, name='gamification_dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/json/', views.get_notifications_json, name='get_notifications_json'),
    path('notifications/mark-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    
    # Enhanced Messaging URLs
    path('messenger/', views.messenger_home, name='messenger_home'),
    path('messenger/conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('messenger/start/', views.start_conversation, name='start_conversation'),
    path('messenger/question/<int:question_id>/', views.start_question_conversation, name='start_question_conversation'),
    path('messenger/api/messages/<int:conversation_id>/', views.get_conversation_messages, name='get_conversation_messages'),
    path('messenger/api/search-users/', views.search_users, name='search_users'),
    
    # Additional Admin URLs
    path('admin/my-records/', views.admin_my_records, name='admin_my_records'),
]
