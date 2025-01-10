from django.urls import path
from Store import urls  
from . import views

urlpatterns = [
    path('shop/',views.Store, name='store'),
    path('product/<int:product_id>/',views.viewProduct, name='product')
]