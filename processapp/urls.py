from django.urls import path
from . import views

urlpatterns = [
    path("pickup_orders/", views.pickupOrders, name="pickup_orders"),
    path('sent_orders/', views.sentOrders, name='sent_orders'),
    path('received_orders/', views.receivedOrders, name='received_orders'),
    path("delivered_orders/", views.deliveredOrders, name="delivered"),
    path("cancel_orders/", views.cancelOrders, name="cancel_orders"),
]
