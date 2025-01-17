from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Customer, Courier, Branch, Area, CourierStatus
from userapp.models import CourierUser
from django.http import Http404
from courierapp.models import Branch, CourierPOD
from datetime import datetime


@login_required(login_url='login') 
def customer_list(request):
    try:
        search_query = request.GET.get('search_query', '').strip()

        # Check if the search query is numeric, and handle accordingly
        if search_query.isdigit():
            # If it's numeric, you may want to search by ID, otherwise, continue as string-based search
            customers = Customer.objects.filter(id=search_query)
        else:
            # Perform a string-based search
            customers = Customer.objects.filter(vendor_name__icontains=search_query)

        return render(request, 'couriers/customer_list.html', {'customers': customers, 'search_query': search_query})

    except Exception as e:
        return render(request, 'couriers/customer_list.html', {
            'error_message': f'An error occurred: {str(e)}',
            'search_query': search_query
        })

@login_required(login_url='login') 
def courier_list(request):
    search_name = request.GET.get('name', '')
    search_id = request.GET.get('id', '')
    couriers = Courier.objects.all()
    couriers = couriers.order_by('-order_date')

    if search_name:
        couriers = couriers.filter(customer_name__icontains=search_name)
    if search_id:
        couriers = couriers.filter(tracking_id__icontains=search_id)
    return render(request, 'couriers/courier_list.html', {'couriers': couriers})





@login_required(login_url='login')
def all_courier_list(request):
    search_name = request.GET.get('name', '')
    search_id = request.GET.get('id', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    # Query all couriers
    couriers = Courier.objects.all()

    # Filter by name if provided
    if search_name:
        couriers = couriers.filter(customer_name__icontains=search_name)

    # Filter by tracking ID if provided
    if search_id:
        couriers = couriers.filter(tracking_id__icontains=search_id)

    # Filter by date range if provided
    if from_date:
        couriers = couriers.filter(order_date__gte=datetime.strptime(from_date, '%Y-%m-%d'))

    if to_date:
        couriers = couriers.filter(order_date__lte=datetime.strptime(to_date, '%Y-%m-%d'))

    # Order by the latest date
    couriers = couriers.order_by('-order_date')

    return render(request, 'couriers/couriers.html', {'couriers': couriers})





@login_required(login_url='login') 
def my_booking(request):
    search_name = request.GET.get('name', '')
    search_id = request.GET.get('id', '')
    couriers = Courier.objects.all()
    
    if search_name:
        couriers = couriers.filter(customer_name__icontains=search_name)
        
        if search_id:
            couriers = couriers.filter(tracking_id__icontains=search_id)
            
    couriers = couriers.order_by('-order_date')

    
    return render(request, 'couriers/my_booking.html', {'couriers': couriers})



@login_required(login_url='login') 
def dashboard(request):
    search_query = request.GET.get('search_query', '')
    if search_query:
        couriers = Courier.objects.filter(Q(id__exact=search_query))
    else:
        couriers = Courier.objects.all()
    
    couriers = couriers.order_by('-order_date')

    # Render the dashboard view
    all_courier = Courier.get_all_couriers()
    done_courier = Courier.get_delivered_couriers()
    pending_courier = Courier.get_pending_couriers()

    all_couriers = all_courier.count()
    done_couriers = done_courier.count()
    pending_couriers = pending_courier.count()
    

    context =  {
        'all_couriers': all_couriers,
        'done_couriers': done_couriers,
        'pending_couriers': pending_couriers,
        'couriers': couriers,
        'search_query': search_query,
    }
    return render(request, 'couriers/dashboard.html', context)






# Add Shipment View
@login_required(login_url='login') 
def add_shipment(request):
    if request.method == 'POST':
        pass
    return render(request, 'couriers/add_shipment.html')


# Track Shipment View
@login_required(login_url='login') 
def track_shipment(request):
    shipment_status = None
    if request.method == 'GET' and 'tracking_number' in request.GET:
        # Logic to get shipment status using the tracking number
        shipment_status = "Delivered"
    return render(request, 'couriers/track_shipment.html', {'shipment_status': shipment_status})


# View Profile View
@login_required(login_url='login') 
def view_profile(request):
    return render(request, 'couriers/profile.html')


# Add Customer View
@login_required(login_url='login') 
def add_customer(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_address = request.POST.get('customer_address')
        customer_alt_phone = request.POST.get('customer_alt_phone')

        # Save customer data to database
        Customer.objects.create(
            vendor_name=customer_name,
            vendor_phone=customer_phone,
            vendor_address=customer_address,
            vendor_alt_phone=customer_alt_phone,
            created_by=request.user  # Assuming the user is logged in and a CourierUser
        )
        messages.success(request, 'Customer Created successfully!')
        return redirect('customer_list')

    return render(request, 'couriers/add_customer.html')


@login_required(login_url='login') 
def booking(request, courier_id=None):
    senders = Customer.objects.all()
    branches = Branch.objects.all()

    if courier_id:
        # If there's a courier_id, attempt to fetch the existing courier for updating
        try:
            courier_data = Courier.objects.get(id=courier_id)
        except Courier.DoesNotExist:
            messages.error(request, 'Courier not found. Please check the details.')
            return redirect('dashboard')
    else:
        # If no courier_id, create a new courier
        courier_data = Courier()

    if request.method == 'POST':
        try:
            # Retrieve the customer based on the vendor_name and phone number
            customer_id = request.POST.get('vender_name')  # Get the ID of the selected vendor
            customer = Customer.objects.get(id=customer_id)

            # Update or create a Courier object
            courier_data.destination = Branch.objects.get(id=request.POST.get('destination'))  # Get the Branch by ID
            courier_data.order_type = request.POST.get('order_type')
            courier_data.delivery_type = request.POST.get('delivery_type')
            courier_data.package_name = request.POST.get('package_name')
            courier_data.weight = request.POST.get('order_weight')
            courier_data.total_amount = request.POST.get('total_amount')
            courier_data.reference = request.POST.get('reference')
            courier_data.instruction = request.POST.get('instruction')
            courier_data.vendor_name = customer  # Assuming `vendor_name` links to the Customer
            courier_data.customer_name = request.POST.get('customer_name')
            courier_data.customer_address = request.POST.get('customer_address')
            courier_data.customer_phone = request.POST.get('customer_phone')
            courier_data.customer_alt_phone = request.POST.get('customer_alt_phone')
            courier_data.cod_amount = request.POST.get('cod_amount')
            courier_data.created_by = request.user  # Assume the user is logged in

            # Save the updated or newly created Courier object
            courier_data.save()

            messages.success(request, 'Order successfully booked!' if not courier_id else 'Order successfully updated!')
            return redirect('my_booking')

        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found. Please check the details.')
            return render(request, 'couriers/order_booking.html', {'senders': senders, 'branches': branches, 'courier_data': courier_data})
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid destination branch. Please check the details.')
            return render(request, 'couriers/order_booking.html', {'senders': senders, 'branches': branches, 'courier_data': courier_data})

    # Render the form for GET request with the existing courier data (if updating)
    return render(request, 'couriers/order_booking.html', {'senders': senders, 'branches': branches, 'courier_data': courier_data})


@login_required(login_url='login') 
def update_order(request):
    courier_id = request.GET.get('courier_id')
    
    if courier_id:
        try:
            courier_data = Courier.objects.get(id=courier_id)
        except Courier.DoesNotExist:
            messages.error(request, 'Courier not found. Please check the details.')
            return redirect('dashboard')
    else:
        courier_data = Courier()  # If no courier_id, create a new one (though this case shouldn't be reached during an update)

    senders = Customer.objects.all()
    branches = Branch.objects.all()

    if request.method == 'POST':
        try:
            customer_id = request.POST.get('vender_name')
            customer = Customer.objects.get(id=customer_id)

            courier_data.destination = Branch.objects.get(id=request.POST.get('destination'))
            courier_data.order_type = request.POST.get('order_type')
            courier_data.delivery_type = request.POST.get('delivery_type')
            courier_data.package_name = request.POST.get('package_name')
            courier_data.weight = request.POST.get('order_weight')
            courier_data.total_amount = request.POST.get('total_amount')
            courier_data.reference = request.POST.get('reference')
            courier_data.instruction = request.POST.get('instruction')
            courier_data.vendor_name = customer
            courier_data.customer_name = request.POST.get('customer_name')
            courier_data.customer_address = request.POST.get('customer_address')
            courier_data.customer_phone = request.POST.get('customer_phone')
            courier_data.customer_alt_phone = request.POST.get('customer_alt_phone')
            courier_data.cod_amount = request.POST.get('cod_amount')
            courier_data.created_by = request.user

            courier_data.save()

            messages.success(request, 'Order successfully updated!')
            return redirect('dashboard')
        
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found. Please check the details.')
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid destination branch. Please check the details.')

    return render(request, 'couriers/edit_booking.html', {
        'senders': senders,
        'branches': branches,
        'courier_data': courier_data
    })



# Add Area View
@login_required(login_url='login') 
def add_branch(request):
    if request.method == 'POST':
        branch_name = request.POST.get('branch_name')
        Branch.objects.create(name=branch_name)
        return redirect('add_branch')
    
    branches = Branch.objects.all()
    return render(request, 'couriers/add_branch.html', {'branches': branches})




# Add Area View
@login_required(login_url='login') 
def add_area(request):
    if request.method == 'POST':
        area_name = request.POST.get('area_name')
        branch = Branch.objects.get(id=request.POST.get('branch'))
        
        Area.objects.create(name=area_name, branch=branch)
        return redirect('add_area')
    
    branches = Branch.objects.all()
    return render(request, 'couriers/add_area.html', {'branches': branches})





# Courier Status List View
@login_required(login_url='login') 
def courier_status(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)
    statuses = CourierStatus.objects.filter(courier=courier).order_by('timestamp')
    
    context = {'courier': courier, 'statuses': statuses}
    return render(request, 'couriers/courier_status_list.html', context)



def tracking(request):
    shipment_status = None
    courier = None
    statuses = []
    tracking_number = request.GET.get('tracking_number')

    if tracking_number:
        try:
            courier = Courier.objects.get(tracking_id=tracking_number)
            statuses = CourierStatus.objects.filter(courier=courier).order_by('timestamp')
            shipment_status = statuses.last().status if statuses.exists() else 'No status updates available.'
        except Courier.DoesNotExist:
            courier = None
            messages.error(request, 'Invalid tracking number. Please check the details.')

    return render(request, 'couriers/tracking.html', {
        'courier': courier,
        'shipment_status': shipment_status,
        'statuses': statuses
    })







# Update Courier Status View
@login_required(login_url='login') 
def update_courier_status(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        additional_info = request.POST.get('additional_info', '')
        location_branch = get_object_or_404(Branch, id=request.POST.get('location_branch'))
        
        if not status or not location_branch:
            messages.error(request, "Please select both status and branch location.")
            return redirect('update_courier_status', courier_id=courier_id)
        
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            additional_info=additional_info,
            timestamp=timezone.now()
        )
        
        messages.success(request, f"Status updated for Courier {courier.tracking_id}")
        return redirect('courier_status_list', courier_id=courier_id)

    branches = Branch.objects.all()
    context = {
        'courier': courier,
        'branches': branches,
        'status_choices': CourierStatus.STATUS_CHOICES,
    }
    return render(request, 'couriers/update_courier_status.html', context)


@login_required(login_url='login') 
def packed_this(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        additional_info = request.POST.get('additional_info', '')
        location_branch = get_object_or_404(Branch, id=request.POST.get('location_branch'))
        
        if not status or not location_branch:
            messages.error(request, "Please select both status and branch location.")
            return redirect('couriers_list')
        
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            additional_info=additional_info,
            timestamp=timezone.now()
        )
        messages.success(request, f"Packed this courier - {courier.tracking_id}")
    return redirect('couriers_list')

@login_required(login_url='login') 
def sent_this(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        additional_info = request.POST.get('additional_info', '')
        location_branch_id = request.POST.get('location_branch')
        location_branch = get_object_or_404(Branch, id=location_branch_id)
        
        if not status or not location_branch:
            messages.error(request, "Please select both status and branch location.")
            return redirect('picked_orders')
        
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            additional_info=additional_info,
            timestamp=timezone.now()
        )
        messages.success(request, f"Sent The courier - {courier.tracking_id}")
    return redirect('picked_orders')


@login_required(login_url='login') 
def recieve_this(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        additional_info = request.POST.get('additional_info', '')
        location_branch_id = request.POST.get('location_branch')
        location_branch = get_object_or_404(Branch, id=location_branch_id)
        
        if not status or not location_branch:
            messages.error(request, "Please select both status and branch location.")
            return redirect('incomming_orders')
        
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            additional_info=additional_info,
            timestamp=timezone.now()
        )
        messages.success(request, f"Recieve courier - {courier.tracking_id}")
    return redirect('incomming_orders')





@login_required(login_url='login') 
def deliver_this(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        additional_info = request.POST.get('additional_info', '')
        location_branch_id = request.POST.get('location_branch')
        podImage = request.FILES.get('PODimage')  # Correctly accessing the uploaded image file
        location_branch = get_object_or_404(Branch, id=location_branch_id)

        # Validation to check that status and location branch are provided
        if not status or not location_branch:
            messages.error(request, "Please select both status and branch location.")
            return redirect('recieve_orders')

        # Create a new CourierStatus object
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            additional_info=additional_info,
            timestamp=timezone.now()
        )

        # Save the uploaded image (POD image) to CourierPOD model
        if podImage:  # Ensure the image is not empty or None
            podData = CourierPOD(courier=courier, updated_by=request.user, pod_image=podImage)
            podData.save()
        else:
            # If no image is uploaded, you might want to handle this case
            messages.warning(request, "No POD image uploaded.")

        # Success message to notify the user
        messages.success(request, f"Delivered courier - {courier.tracking_id}")

    return redirect('recieve_orders')








# Create Courier Status View
@login_required(login_url='login') 
def create_courier_status(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        location_branch = get_object_or_404(Branch, id=request.POST.get('location_branch'))
        
        if not status or not location_branch:
            messages.error(request, "Both status and location branch must be selected.")
            return redirect('create_courier_status', courier_id=courier_id)

        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status=status,
            timestamp=timezone.now()
        )

        messages.success(request, f"New status created for Courier {courier.tracking_id}")
        return redirect('courier_status', courier_id=courier_id)

    branches = Branch.objects.all()
    context = {
        'courier': courier,
        'branches': branches,
        'status_choices': CourierStatus.STATUS_CHOICES,
    }
    return render(request, 'couriers/create_courier_status.html', context)


@login_required(login_url='login') 
def to_sent__courier_list(request):
    # Get the selected branch and status from the GET request, or use defaults
    selected_branch = request.GET.get('location_branch', None)
    selected_status = request.GET.get('status', None)

    # Fetch all branches
    branches = Branch.objects.all()

    # Start with all couriers and apply the filters
    couriers = Courier.objects.all()

    # Apply status filter if selected
    if selected_status:
        couriers = couriers.filter(statuses__status=selected_status)

    # Apply branch filter if selected
    if selected_branch:
        couriers = couriers.filter(branch__id=selected_branch)

    couriers = couriers.distinct()

    return render(request, 'couriers/to_sent__courier_list.html', {
        'couriers': couriers,
        'branches': branches,
        'selected_status': selected_status
    })



@login_required(login_url='login') 
def picked_orders(request):
    # Fetch all couriers with the latest status being 'Packed for'
    branches = Branch.objects.all()
    couriers = Courier.objects.filter(
        statuses__status='Packed for'
    ).distinct()
    couriers = couriers.order_by('-order_date')


    return render(request, 'couriers/picked_orders.html', {'couriers': couriers, 'branches': branches})



@login_required(login_url='login') 
def dispatched_orders(request):
    # Fetch all couriers with the latest status being 'Dispatched'
    branches = Branch.objects.all()
    couriers = Courier.objects.filter(
        statuses__status='Sent to'
        ).distinct()
    couriers = couriers.order_by('-order_date')
    return render(request, 'couriers/dispatched_couriers.html', {'couriers': couriers, 'branches': branches})



@login_required(login_url='login') 
def incomming_orders(request):
    # Fetch all couriers with the latest status being 'Incomming'
    branches = Branch.objects.all()
    couriers = Courier.objects.filter(
        statuses__status='Sent to'
        ).distinct()
    couriers = couriers.order_by('-order_date')
    return render(request, 'couriers/incomming_orders.html', {'couriers': couriers, 'branches': branches})




@login_required(login_url='login') 
def recieve_orders(request):
    couriers = Courier.objects.filter(
        statuses__status='Received by'
        ).distinct()
    branches = Branch.objects.all()
    couriers = couriers.order_by('-order_date')

    return render(request, 'couriers/recieve_orders.html', {'couriers': couriers, 'branches': branches})





@login_required(login_url='login') 
def delivered_orders(request):
    # Get all branches and couriers with the latest status 'Delivered'
    branches = Branch.objects.all()
    couriers = Courier.objects.filter(
        statuses__status='Delivered'
    ).distinct()
    couriers = couriers.order_by('-order_date')
    
    # Get all PODs related to couriers that are delivered
    pods = CourierPOD.objects.filter(courier__in=couriers)
    
    # Render the page with couriers, pods, and branches
    return render(request, 'couriers/delivered_orders.html', {'couriers': couriers, 'pods': pods, 'branches': branches})





@login_required(login_url='login')
def sent_courier(request, courier_id):
    courier = get_object_or_404(Courier, id=courier_id)

    if request.method == 'POST':
        # Capture the location branch from the form
        location_branch_id = request.POST.get('location_branch')

        if not location_branch_id:
            messages.error(request, "Location branch must be selected.")
            return redirect('sent_courier', courier_id=courier_id)

        # Get the location branch
        location_branch = get_object_or_404(Branch, id=location_branch_id)

        # Create Courier Status
        CourierStatus.objects.create(
            courier=courier,
            updated_by=request.user,
            location_branch=location_branch,
            status='Sent to',  # Status is fixed as "Sent to"
            timestamp=timezone.now()
        )

        # Add a success message and redirect back to the sent courier page
        messages.success(request, f"Courier {courier.tracking_id} sent to {location_branch.name}.")
        return redirect('sent_courier', courier_id=courier_id)

    # Fetch branches for the form dropdown
    branches = Branch.objects.all()
    couriers = couriers.order_by('-order_date')

    # Render the form
    context = {
        'courier': courier,
        'branches': branches,
    }
    return render(request, 'couriers/sent_courier.html', context)



# Courier Details View
@login_required(login_url='login') 
def courier_details(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)  # Get the courier object
        sender_data = courier.vendor_name  # No need to query Customer again
    except Courier.DoesNotExist:
        raise Http404("Courier not found")
    
    context = {
        'courier': courier,
        'sender_data': sender_data,
    }
    
    # Pass both courier and customer data to the template
    return render(request, 'couriers/courier_details.html', context)
