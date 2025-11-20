from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/community-stats/', views.community_stats_api, name='community_stats_api'),
    path('about/', views.about, name='about'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('ask/', views.ask_question, name='ask_question'),
    
    # Student Question Management
    path('my-questions/', views.student_my_questions, name='student_my_questions'),
    
    # Admin Question Management
    path('admin/questions/', views.admin_question_queue, name='admin_question_queue'),
    path('admin/my-records/', views.admin_my_records, name='admin_my_records'),
]
