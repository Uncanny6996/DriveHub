from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from cars.models import Reservation
from contacts.models import Contact

# ✅ DASHBOARD VIEW
@login_required
def dashboard(request):
    user_reservations = Reservation.objects.filter(user=request.user)
    user_inquiries = Contact.objects.filter(user_id=request.user.id)
    return render(request, 'accounts/dashboard.html', {
        'reservations': user_reservations,
        'inquiries': user_inquiries
    })


# ✅ LOGIN VIEW
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


# ✅ REGISTER VIEW
def register(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    username=username,
                    password=password
                )
                user.save()
                auth.login(request, user)
                messages.success(request, 'You are now logged in.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    return render(request, 'accounts/register.html')


# ✅ LOGOUT VIEW
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
    return redirect('home')
