import os
from django.contrib import admin
from .models import Project, Contact, Visitor


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'created_at']
    search_fields = ['title', 'description']

    def save_model(self, request, obj, form, change):
        if change and 'image-clear' in request.POST:
            # Get the old image before saving
            try:
                old_obj = Project.objects.get(pk=obj.pk)
                if old_obj.image:
                    # Delete the old image file from filesystem
                    if os.path.isfile(old_obj.image.path):
                        os.remove(old_obj.image.path)
            except Project.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # Delete the image file when project is deleted
        if obj.image:
            if os.path.isfile(obj.image.path):
                os.remove(obj.image.path)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Handle bulk deletion from admin
        for obj in queryset:
            if obj.image:
                if os.path.isfile(obj.image.path):
                    os.remove(obj.image.path)
        super().delete_queryset(request, queryset)


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
