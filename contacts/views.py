from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from cars.models import Car

def inquiry(request):
    if request.method == 'POST':
        car_id = request.POST['car_id']
        car_title = request.POST['car_title']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        customer_need = request.POST['customer_need']
        city = request.POST['city']
        state = request.POST['state']
        email = request.POST['email']
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        
        user_id = request.user.id if request.user.is_authenticated else None
        
        if request.user.is_authenticated:
            if Contact.objects.filter(car_id=car_id, user_id=user_id).exists():
                messages.error(request, 'You have already made an inquiry about this car. Please wait for our response.')
                return redirect('cars:car_detail', id=car_id)  # Changed to use namespace and 'id'
        
        contact = Contact(
            car_id=car_id,
            car_title=car_title,
            first_name=first_name,
            last_name=last_name,
            customer_need=customer_need,
            city=city,
            state=state,
            email=email,
            phone=phone,
            message=message,
            user_id=user_id
        )
        contact.save()
        
        # Send email
        try:
            send_mail(
                f'New Inquiry for {car_title}',
                f'You have a new inquiry for {car_title}. Please login to your admin panel for more info.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        messages.success(request, 'Your inquiry has been submitted successfully! We will contact you soon.')
        return redirect('cars:car_detail', id=car_id)  # Changed to use namespace and 'id'
    
    return redirect('home')

@login_required
def dashboard(request):
    user_inquiries = Contact.objects.filter(user_id=request.user.id).order_by('-create_date')
    return render(request, 'accounts/dashboard.html', {'inquiries': user_inquiries})

@login_required
def delete_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Contact, id=inquiry_id, user_id=request.user.id)
    
    if request.method == 'POST':
        inquiry.delete()
        messages.success(request, 'Your inquiry has been deleted successfully.')
        return redirect('contacts:dashboard')
    
    return redirect('contacts:dashboard')

@login_required
def inquiry_detail(request, inquiry_id):
    inquiry = get_object_or_404(Contact, id=inquiry_id, user_id=request.user.id)
    car = get_object_or_404(Car, pk=inquiry.car_id)
    return render(request, 'accounts/inquiry_detail.html', {'inquiry': inquiry, 'car': car})

@login_required
def admin_reply(request, inquiry_id):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('contacts:dashboard')
    
    inquiry = get_object_or_404(Contact, id=inquiry_id)
    
    if request.method == 'POST':
        reply_text = request.POST.get('admin_reply', '').strip()
        if reply_text:
            inquiry.admin_reply = reply_text
            inquiry.is_resolved = True
            inquiry.save()
            
            try:
                send_mail(
                    f'Reply to your inquiry about {inquiry.car_title}',
                    f'Hello {inquiry.first_name},\n\nHere is our response to your inquiry:\n\n{reply_text}\n\nThank you for contacting us!',
                    settings.DEFAULT_FROM_EMAIL,
                    [inquiry.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Error sending email to user: {e}")
            
            messages.success(request, 'Your reply has been submitted successfully!')
        else:
            messages.error(request, 'Reply cannot be empty.')
        
        return redirect('admin:contacts_contact_change', inquiry_id)
    
    return redirect('admin:contacts_contact_change', inquiry_id)