from django.urls import path
from .views import (
    list_experiments,
    experiment_summary,
    experiment_responses,
    experiment_leaks,
)

urlpatterns = [
    path("experiments/", list_experiments),
    path("experiments/<int:experiment_id>/summary/", experiment_summary),
    path("experiments/<int:experiment_id>/responses/", experiment_responses),
    path("experiments/<int:experiment_id>/leaks/", experiment_leaks),
]