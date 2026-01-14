from django.urls import path
from users.views import (
    login_view, 
    logout_view, 
    user_list_view, 
    user_create_view, 
    user_update_view, 
    user_delete_view,
    dashboard_view,
    welcome_view,
    about_view,
    contact_view,
    gallery_view,
    team_view,
    check_request_view
)

app_name = 'users'

urlpatterns = [
    path('', welcome_view, name='welcome'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('gallery/', gallery_view, name='gallery'),
    path('team/', team_view, name='team'),
    path('check-request/', check_request_view, name='check_request'),
    path('dashboard/', dashboard_view, name='dashboard'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('list/', user_list_view, name='list'),
    path('create/', user_create_view, name='create'),
    path('update/<int:pk>/', user_update_view, name='update'),
    path('delete/<int:pk>/', user_delete_view, name='delete'),
]
