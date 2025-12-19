from django.db import models
from django.utils import timezone


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    page = models.CharField(max_length=500)
    user_agent = models.TextField(blank=True)
    visited_at = models.DateTimeField(default=timezone.now)

    # Biographical/demographic fields
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    # desktop, mobile, or tablet
    device_type = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.ip_address} - {self.page}"


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
