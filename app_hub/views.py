from django.shortcuts import render, redirect
from django.contrib import messages
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
            return redirect('home')

    return render(request, 'home.html', {'projects': projects})
