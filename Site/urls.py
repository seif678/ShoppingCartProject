from django.urls import path
from . import views

urlpatterns = [
    path('',views.Store,name="Store"),
    path('cart/', views.Cart, name="Cart"),
    path('checkout/', views.Checkout, name="Checkout")

]

