import os
from django.contrib import admin
from .models import Project, Contact


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
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


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['name', 'email', 'message', 'created_at']
