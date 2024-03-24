from django.urls import path
from django.contrib import admin
from knox.views import LogoutView, LogoutAllView
from . import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("register", views.register.as_view(), name="register"),
    path("register/username", views.register_username.as_view(), name="register_username"),
    path("register/email", views.register_email.as_view(), name="register_email"),
    path("login", views.login.as_view(), name="login"),
    path("token_login", views.token_login.as_view(), name="token_login"),
    path('logout', LogoutView.as_view()),
    path('logout-all', LogoutAllView.as_view()),
    path("tracking", views.tracking.as_view(), name="tracking"),
    path("tracking/<int:id>", views.tracking_id.as_view(), name="tracking_id"),
    path("addition", views.addition.as_view(), name="addition"),
    path("exercise", views.exercise.as_view(), name="exercise"),
    path("exercise/<int:id>", views.exercise_id.as_view(), name="exercise_id"),
    path("goal", views.goal.as_view(), name="goal"),
    path("goal/<int:id>", views.goal_id.as_view(), name="goal_id"),
    path("goal-additions/<int:id>", views.goal_additions_id.as_view(), name="goal_additions_id"),
    path("user", views.user.as_view(), name="user"),
    path("movement", views.movement.as_view(), name="movement"),
    path("movement/<int:id>", views.movement_id.as_view(), name="movement_id"),
    path("trainingplan", views.trainingplan.as_view(), name="trainingplan"),
    path("trainingplan/<int:id>", views.trainingplan_id.as_view(), name="trainingplan_id"),
    path("exercisemovementconnection", views.exercisemovementconnection.as_view(), name="exercisemovementconnection"),
    path("exercisemovementconnection/<int:id>", views.exercisemovementconnection_id.as_view(), name="exercisemovementconnection_id"),
    path("feedback", views.feedback.as_view(), name="feedback"),
]