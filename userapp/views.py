from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .models import CourierUser
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from courierapp.models import Branch, Courier, CourierStatus, CourierPOD



# Create your views here.
def dashboard_2(request):
    all_courier = Courier.get_all_couriers()
    done_courier = Courier.get_delivered_couriers()
    pending_courier = Courier.get_pending_couriers()

    all_couriers = all_courier.count()
    done_couriers = done_courier.count()
    pending_couriers = pending_courier.count()

    shipment_status = None
    courier = None
    statuses = []
    pods = []  # Initialize pods variable
    tracking_number = request.GET.get('tracking_number')

    if tracking_number:
        try:
            courier = Courier.objects.get(tracking_id=tracking_number)
            statuses = CourierStatus.objects.filter(courier=courier).order_by('timestamp')

            # Get the latest shipment status
            shipment_status = statuses.last().status if statuses.exists() else 'No status updates available.'

            # Fetch the related PODs
            pods = CourierPOD.objects.filter(courier=courier)

        except Courier.DoesNotExist:
            courier = None
            messages.error(request, 'Invalid tracking number. Please check the details.')

    context =  {
        'courier': courier,
        'pods': pods,
        'shipment_status': shipment_status,
        'statuses': statuses,
        
        'all_couriers': all_couriers,
        'done_couriers': done_couriers,
        'pending_couriers': pending_couriers
    }
    return render(request, 'users/dashboard.html', context)



from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import CourierUser, Branch

def signup(request):
    branchs = Branch.objects.all()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        working_area = request.POST.get('working_area')
        branch_name_id = request.POST.get('branch_name')  # We get the ID here, not the name
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validate that the fields are not empty
        if not all([email, username, full_name, phone_number, working_area, branch_name_id, password, password2]):
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        # Check if email or username already exists
        if CourierUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('signup')

        if CourierUser.objects.filter(username=username).exists():
            messages.error(request, 'Username is already in use.')
            return redirect('signup')

        # Check if passwords match
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        # Get the branch object based on the selected branch ID
        try:
            branch = Branch.objects.get(id=branch_name_id)
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid branch selected.')
            return redirect('signup')

        # Create the new user
        user = CourierUser.objects.create_user(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            working_area=working_area,
            branch_name=branch  # Now using the Branch object
        )

        # Log the user in after successful registration
        auth_login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('dashboard')  # Redirect to the dashboard or wherever you want

    return render(request, 'users/signup.html', {'branchs': branchs})







def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Log the user in
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to home or dashboard
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login')  # Redirect back to login page if invalid credentials

    return render(request, 'users/login.html')


@login_required(login_url='login') 
def logout_view(request):
    auth_logout(request)  # Log the user out
    messages.success(request, "You have successfully logged out.")
    return redirect('login')  # Redirect to login page after logout


class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        # Get the current user
        user = request.user
        branches = Branch.objects.all()
        return render(request, 'users/update_user.html', {'user': user, 'branches': branches})

    def post(self, request):
        user = request.user
        
        # Get the updated values from the form
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        working_area = request.POST.get('working_area')
        branch_name = request.POST.get('branch_name')

        # Update the user object
        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone_number = phone_number
        if working_area:
            user.working_area = working_area
        if branch_name:
            user.branch_name_id = branch_name  # Assuming branch_name is a ForeignKey to Branch

        # Save the updated user information
        user.save()

        # Show a success message and redirect to profile page
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('view_profile')
