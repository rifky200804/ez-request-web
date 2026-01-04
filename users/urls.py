from django.urls import path
from users.views import (
    login_view, 
    logout_view, 
    user_list_view, 
    user_create_view, 
    user_update_view, 
    user_delete_view,
    dashboard_view,
    welcome_view
)

app_name = 'users'

urlpatterns = [
    path('', welcome_view, name='welcome'), # Welcome page
    path('dashboard/', dashboard_view, name='dashboard'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('list/', user_list_view, name='list'),
    path('create/', user_create_view, name='create'),
    path('update/<int:pk>/', user_update_view, name='update'),
    path('delete/<int:pk>/', user_delete_view, name='delete'),
]
