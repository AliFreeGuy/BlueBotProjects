from django.urls import path
from core import views



app_name = 'core'

urlpatterns = [

    path('setting/' , views.SettingsAPIView.as_view() , name = 'setting' ),
    path('create-payment/', views.PaymentCreateView.as_view(), name='create-payment'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify-payment'),
    path('user/' , views.UserAPIView.as_view() , name='update-user')



]