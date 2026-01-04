from django.urls import path
from service_requests.views import request_list_view, request_create_view, request_delete_view, approval_list_view, request_approve_view

app_name = 'service_requests'

urlpatterns = [
    path('list/', request_list_view, name='list'),
    path('create/', request_create_view, name='create'),
    path('delete/<int:pk>/', request_delete_view, name='delete'),
    path('approvals/', approval_list_view, name='approvals'),
    path('approve/<int:pk>/', request_approve_view, name='approve'),
]
