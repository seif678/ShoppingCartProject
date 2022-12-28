from django.shortcuts import render
from Site.models import *
def Store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request,'Site/Store.html', context)
def Cart(request):
    context = {}
    return render(request,'Site/Cart.html', context)
def Checkout(request):
    context = {}
    return render(request, 'Site/Checkout.html', context)
