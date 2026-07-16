from django.urls import path
from . import views

urlpatterns = [
    # Landing Page
    path('', views.index, name='index'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/editors/', views.manage_editors, name='manage_editors'),
    path('admin-dashboard/editors/add/', views.add_editor, name='add_editor'),
    path('admin-dashboard/editors/edit/<int:pk>/', views.edit_editor, name='edit_editor'),
    path('admin-dashboard/editors/delete/<int:pk>/', views.delete_editor, name='delete_editor'),
    path('admin-dashboard/monitor/', views.monitor_articles, name='monitor_articles'),
    path('admin-dashboard/reports/', views.view_reports, name='view_reports'),
    path('admin-dashboard/feedback/', views.view_feedback, name='view_feedback'),
    
    # Editor
    path('editor-dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('editor-dashboard/articles/add/', views.add_article, name='add_article'),
    path('editor-dashboard/articles/edit/<int:pk>/', views.edit_article, name='edit_article'),
    path('editor-dashboard/articles/delete/<int:pk>/', views.delete_article, name='delete_article'),
    path('editor-dashboard/articles/submit/<int:pk>/', views.submit_article, name='submit_article'),
    
    # User
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user-dashboard/articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('user-dashboard/feedback/add/', views.add_feedback, name='add_feedback'),
]
