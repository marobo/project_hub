from django.contrib import admin
from .models import Project, Contact, Visitor


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['name', 'email', 'message', 'created_at']


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'page', 'visited_at']
    list_filter = ['visited_at', 'page']
    search_fields = ['ip_address', 'page']
    readonly_fields = ['ip_address', 'page', 'user_agent', 'visited_at']
    date_hierarchy = 'visited_at'
