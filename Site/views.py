from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.db.models.signals import post_save
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import CustomerUserCreationForm
import json
import datetime
from .models import *

def create_profile(sender, instance, created, *args, **kwargs):
    # ignore if this is an existing User
    if not created:
        return

    try:
        Customer.objects.get(user=instance)
    except Customer.DoesNotExist:
        Customer.objects.create(user=instance)
def Store(request):
    if request.user.is_authenticated:
        create_profile(sender=User, instance=request.user, created=True)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cartItems = []
    categories = Product.objects.values('brand').distinct()
    minMaxPrice = Product.objects.aggregate(Min('price'), Max('price'))
    minPrice = minMaxPrice['price__min']
    maxPrice = minMaxPrice['price__max']
    if 'q' in request.GET:
        q = request.GET['q']
        products = Product.objects.filter(name__icontains=q) | Product.objects.filter(brand__icontains=q)
        context = {'products': products, 'cartItems': cartItems, 'minMaxPrice': minMaxPrice}
        return render(request, 'Site/Store.html', context)
    if 'k' in request.GET:
        k = request.GET['k']
    else:
        k = maxPrice
    if 'h' in request.GET:
        h = request.GET['h']
    else:
        h = minPrice

    if 'b' in request.GET and request.GET['b'] != 'Choose...':
        b = request.GET['b']
        products = Product.objects.filter(brand__icontains=b) & Product.objects.filter(price__range=(h, k))
    else:
        products = Product.objects.filter(price__range=(h, k))

    context = {'products': products, 'cartItems': cartItems, 'minMaxPrice': minMaxPrice, 'categories': categories}
    return render(request, 'Site/Store.html',context)





def Cart(request):
    if request.user.is_authenticated:
        create_profile(sender=User, instance=request.user, created=True)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'Site/Cart.html', context)

@login_required(login_url='login')
def Checkout(request):
    if request.user.is_authenticated:
        create_profile(sender=User, instance=request.user, created=True)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        newtotal = order.get_cart_total*0.9
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
        newtotal = order.get_cart_total*0.9
    promocodes = ["PromoCode","promo","promocode"]
    str=''
    if 'n' in request.GET:
        n = request.GET['n']
        if n in promocodes:
            str = "After Discount: ${}".format(newtotal)

    context = {'items': items, 'order': order, 'cartItems': cartItems,'newtotal':newtotal,'str':str}
    return render(request, 'Site/Checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shippingaddress_set:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)


def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Store')

    return render(request, 'Site/login_register.html',{'page': page})

def logoutPage(request):
    logout(request)
    return redirect('login')

def registerPage(request):
    page = 'register'
    form = CustomerUserCreationForm()
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user = authenticate(request, username=user.username, password=request.POST['password1'])
            if user is not None:
                login(request, user)
                return redirect('Store')
    context = {'form': form, 'page': page}
    return render(request,'Site/login_register.html',context)