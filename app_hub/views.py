from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Project, Contact


def home(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            Contact.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Thank you! Your message has been sent.')

            # new message successfully sent, send a notification to the admin
            current_url = request.META['HTTP_REFERER']
            subject = "New Message from {}".format(name)
            message = (
                f"{name} has reached out to you via the contact form "
                f"at this website:\n{current_url}\n\n"
                f"Message:\n{message}\n\n"
                f"Email: {email}\n\nThanks!"
            )
            send_mail(
                subject, message, email,
                [settings.ADMIN_EMAIL], fail_silently=False
            )
            return redirect('home')

    return render(request, 'home.html', {'projects': projects})
