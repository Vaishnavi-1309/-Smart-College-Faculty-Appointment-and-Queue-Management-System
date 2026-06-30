from django.urls import path
from . import views

urlpatterns = [
    path('join/', views.join_queue, name='join_queue'),
    path('track/<int:token_id>/', views.track_queue, name='track_queue'),
    path('api/status/<int:token_id>/', views.queue_status_api, name='queue_status_api'), 
]