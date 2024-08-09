from django.urls import path
from core import views



app_name = 'core'

urlpatterns = [
    
    path('create-payment/', views.PaymentCreateView.as_view(), name='create-payment'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify-payment'),
]