from django.contrib import admin
from django.urls import path, include
from core.views import dashboard
from core.views import comparison_dashboard, defense_comparison
from core.views import ml_comparison, adversarial_analysis

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("api/", include("core.urls")),
    path("comparison/", comparison_dashboard),
    path("defense/", defense_comparison),
    path("ml-comparison/", ml_comparison),
    path("adversarial-analysis/", adversarial_analysis),
]