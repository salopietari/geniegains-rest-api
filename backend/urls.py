from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("register", views.register, name="register"),
    path("register/username", views.register_username, name="register_username"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("token_login", views.token_login, name="token_login"),
    path("tracking", views.tracking, name="tracking"),
    path("tracking/<int:id>", views.tracking_id, name="tracking_id"),
    path("addition", views.addition, name="addition"),
    path("exercise", views.exercise, name="exercise"),
    path("exercise/<int:id>", views.exercise_id, name="exercise_id"),
    path("goal", views.goal, name="goal"),
    path("goal/<int:id>", views.goal_id, name="goal_id"),
    path("user", views.user, name="user"),
    path("movement", views.movement, name="movement"),
    path("trainingplan", views.trainingplan, name="trainingplan"),
    path("trainingplan/<int:id>", views.trainingplan_id, name="trainingplan_id"),
    path("exercisemovementconnection", views.exercisemovementconnection, name="exercisemovementconnection"),
    path("exercisemovementconnection/<int:id>", views.exercisemovementconnection_id, name="exercisemovementconnection_id"),
    path("feedback", views.feedback, name="feedback"),
]