from django.shortcuts import render

def Store(request):
    context = {}
    return render(request,'Site/Store.html', context)
def Cart(request):
    context = {}
    return render(request,'Site/Cart.html', context)
def Checkout(request):
    context = {}
    return render(request, 'Site/Checkout.html', context)
