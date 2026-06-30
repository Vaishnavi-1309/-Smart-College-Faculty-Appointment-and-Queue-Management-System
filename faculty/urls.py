from django.urls import path
from . import views

urlpatterns = [
    path('update-status/', views.update_status, name='update_status'),
    path('complete/<int:token_id>/', views.complete_token, name='complete_token'),
    path('start-session/', views.start_session, name='start_session'),
     path('qr-code/', views.get_qr_code, name='qr_code'),  
]