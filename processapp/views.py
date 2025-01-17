from django.shortcuts import render

# View for booked orders
def pickupOrders(request):
    # Fetch your data or logic here
    return render(request, 'pickup_orders.html')

# View for sent orders
def sentOrders(request):
    # Fetch your data or logic here
    return render(request, 'sent_orders.html')

# View for received orders
def receivedOrders(request):
    # Fetch your data or logic here
    return render(request, 'received_orders.html')

# View for delivered orders
def deliveredOrders(request):
    # Fetch your data or logic here
    return render(request, 'delivered_orders.html')

# View for canceled orders
def cancelOrders(request):
    # Fetch your data or logic here
    return render(request, 'cancel_orders.html')
