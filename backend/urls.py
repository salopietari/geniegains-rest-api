from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
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
    path("exercisemovementconnection", views.exercisemovementconnection, name="exercisemovementconnection")
]