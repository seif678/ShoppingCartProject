from django.urls import path
from . import views

urlpatterns = [
    path('',views.Store,name="Store"),
    path('cart/', views.Cart, name="Cart"),
    path('checkout/', views.Checkout, name="Checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/',views.processOrder,name="process_order"),
    #path('login/',views.login,name="login"),
    #path('register/', views.register,name="register"),
    path ('login/',views.loginPage,name="login"),
    path ('logout/',views.logoutPage,name="logout"),
    path('register/', views.registerPage,name="register"),

]

