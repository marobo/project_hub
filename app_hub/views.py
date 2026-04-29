from django.contrib import messages
from django.shortcuts import redirect, render
from django_visitor_stats.views import track_visitor

from .utils.email import send_contact_email
from .models import Contact, Project


def home(request):
    track_visitor(request)
    projects = Project.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_message = request.POST.get('message')

        if name and email and user_message:
            Contact.objects.create(name=name, email=email, message=user_message)
            try:
                send_contact_email(name, email, user_message)
                messages.success(request, 'Thank you! Your message has been sent.')
                return redirect('home')
            except Exception:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
                return redirect('home')

    return render(request, 'home.html', {'projects': projects})
