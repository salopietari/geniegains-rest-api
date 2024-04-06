from django.contrib import admin
from .models import Movement, TrainingPlan

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ['name', 'experience_level']
    search_fields = ['name']
    list_filter = ['experience_level']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('user', None)
        return form

@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].required = False
        return form
