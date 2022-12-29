from django.shortcuts import render
from .models import *

def Store(request):
	products = Product.objects.all()
	context = {'products':products}
	return render(request, 'Site/Store.html', context)

def Cart(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}

	context = {'items':items, 'order':order}
	return render(request, 'Site/Cart.html', context)

def Checkout(request):
	context = {}
	return render(request, 'Site/checkout.html', context)