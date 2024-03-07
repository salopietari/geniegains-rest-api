from django.contrib import admin
from .models import *

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ['name', 'experience_level']
    search_fields = ['name']
    list_filter = ['experience_level']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('user', None)  # Remove the 'user' field from the form
        return form

@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "experience_level":
            user_experience = request.user.experience
            # Depending on your model structure, you may need to adjust this
            kwargs["queryset"] = TrainingPlan.objects.filter(user__experience=user_experience)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
