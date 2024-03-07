from django.contrib import admin
from .models import Movement, TrainingPlan

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_experience']
    search_fields = ['name']
    
    def user_experience(self, obj):
        return obj.user.experience

    user_experience.short_description = 'User Experience Level'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__experience=self.user_experience)
