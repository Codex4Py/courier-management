from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from courierapp.models import Courier, CourierStatus, CourierPOD, Branch
from userapp.models import CourierUser




def home(request):
    all_couriers = Courier.get_all_couriers()
    done_couriers = Courier.get_delivered_couriers()
    pending_couriers = Courier.get_pending_couriers()
    shipment_status = None
    courier = None
    statuses = []
    pods = []  # Initialize pods variable
    tracking_number = request.GET.get('tracking_number')

    if tracking_number:
        try:
            courier = Courier.objects.get(tracking_id=tracking_number)
            statuses = CourierStatus.objects.filter(courier=courier).order_by('timestamp')

            # Get the latest shipment status (or default to 'No status updates available.')
            shipment_status = statuses.last().status if statuses.exists() else 'No status updates available.'

            # Fetch the related PODs
            pods = CourierPOD.objects.filter(courier=courier)

        except Courier.DoesNotExist:
            courier = None
            messages.error(request, 'Invalid tracking number. Please check the details.')

    # Define the flow steps directly from the model's STATUS_CHOICES
    flow_steps = dict(CourierStatus.STATUS_CHOICES)

    # Pass the flow_steps and other data to the template
    return render(request, 'couriers/home.html', {
        'courier': courier,
        'pods': pods,
        'shipment_status': shipment_status,
        'statuses': statuses,
        'flow_steps': flow_steps,  # Passing flow_steps to template
        'all_couriers': all_couriers,
        'done_couriers': done_couriers,
        'pending_couriers': pending_couriers
    })


def branch_list(request):
    branches = Branch.objects.all()
    userss = CourierUser.objects.all()
    branches_numbers = branches.count()
    context = {
        'branches': branches,
        'branches_numbers': branches_numbers,
        'userss': userss,
    }
    return render(request, 'branches.html', context)



def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
