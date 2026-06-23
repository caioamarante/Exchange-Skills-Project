from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('support/', views.support_view, name='support'),
    path('like/<int:user_id>/', views.like_user, name='like_user'),
    path('chats/', views.chat_list, name='chats'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
]
