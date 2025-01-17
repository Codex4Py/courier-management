from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_shipment/', views.add_shipment, name='add_shipment'),
    path('track_shipment/', views.track_shipment, name='track_shipment'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('couriers/', views.courier_list, name='couriers_list'),
    path('couriers-all/', views.all_courier_list, name='all_couriers_list'),
    path('courier/my_bookings/', views.my_booking, name='my_booking'),


    path('courier/<int:courier_id>/packed/', views.packed_this, name='packed_this'),
    path('courier/<int:courier_id>/sent/', views.sent_this, name='sent_this'),
    path('courier/<int:courier_id>/recieve/', views.recieve_this, name='recieve_this'),


    path('add-customer/', views.add_customer, name='add_customer'),
    path('customer-list/', views.customer_list, name='customer_list'),
    path('add-area/', views.add_area, name='add_area'),
    path('add-branch/', views.add_branch, name='add_branch'),

    path('courier/booking/', views.booking, name='order_booking_main'),
    path('update_order/', views.update_order, name='update_order'),

    path('courier/<int:courier_id>/', views.courier_details, name='courier_details'),
    path('tracking/', views.tracking, name='tracking'),

    # View to show all statuses of a courier
    path('courier/<int:courier_id>/status/', views.courier_status, name='courier_status'),
    path('courier/<int:courier_id>/update-status/', views.update_courier_status, name='update_courier_status'),
    path('courier/<int:courier_id>/create-status/', views.create_courier_status, name='create_courier_status'),
    path('sent_courier/<int:courier_id>/', views.sent_courier, name='sent_courier'),
    path('book-courier/', views.to_sent__courier_list, name='booked_courier_list'),
    path('courier/picked/', views.picked_orders, name='picked_orders'),
    path('courier/dispatched/', views.dispatched_orders, name='dispatched_orders'),
    path('courier/comming/', views.incomming_orders, name='incomming_orders'),
    path('courier/recieved/', views.recieve_orders, name='recieve_orders'),
    path('courier/<int:courier_id>/deliver/', views.deliver_this, name='deliver_this'),
    path('courier/delivered/', views.delivered_orders, name='delivered_orders'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
