from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Project, Contact


def home(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_message = request.POST.get('message')

        if name and email and user_message:
            Contact.objects.create(name=name, email=email, message=user_message)
            messages.success(request, 'Thank you! Your message has been sent.')

            # Send notification email to admin
            subject = f"New Message from {name}"
            body = (
                f"{name} ({email}) sent you a message:\n\n"
                f"{user_message}"
            )
            try:
                mail = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[settings.ADMIN_EMAIL],
                    reply_to=[email],  # Reply goes to the user
                )
                mail.send(fail_silently=False)
            except Exception:
                pass  # Message saved to DB, email failed silently

            return redirect('home')

    return render(request, 'home.html', {'projects': projects})
