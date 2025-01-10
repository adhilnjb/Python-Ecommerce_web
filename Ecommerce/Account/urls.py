from django.urls import path,include
from . import views

urlpatterns=[

path('login/',views.login, name='login'),
path('register/', views.Registration, name= 'register'),
path('otp/',views.otp, name='otp'),
]