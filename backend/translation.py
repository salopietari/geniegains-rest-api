from django.conf import settings
from django.db import models
from modeltranslation.translator import TranslationOptions, register
from .models import Movement, Conversation, QA

@register(Movement)
class MovementTranslationOptions(TranslationOptions):
    fields = ('name', 'category')

class MovementTranslation(models.Model):
    movement = models.ForeignKey(Movement, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=[
        ('triceps', 'Triceps'),
        ('biceps', 'Biceps'),
        ('shoulders', 'Shoulders'),
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('legs', 'Legs'),
        ('core', 'Core'),
        ('other', 'Other')
    ], default="other")

@register(Conversation)
class ConversationTranslationOptions(TranslationOptions):
    fields = ('title',)

class ConversationTranslation(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=100)

@register(QA)
class QATranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

class QATranslation(models.Model):
    qa = models.ForeignKey(QA, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    question = models.TextField(max_length=100)
    answer = models.TextField(max_length=1000)