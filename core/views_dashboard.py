from django.shortcuts import render
from django.db.models import Count
from .models import Experiment, ExperimentSummary, LeakageResult


def dashboard(request):
    experiments = Experiment.objects.all().order_by("-created_at")[:10]
    latest_experiment = experiments.first()

    summary = None

    # Charts data
    field_labels = []
    field_counts = []

    type_labels = []
    type_counts = []

    category_labels = []
    category_counts = []

    top_leaks = []

    if latest_experiment:
        summary = ExperimentSummary.objects.filter(
            experiment=latest_experiment
        ).first()

        # 🔹 Leakage by FIELD
        field_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("field_name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        field_labels = [item["field_name"] for item in field_data]
        field_counts = [item["total"] for item in field_data]

        # 🔹 Leakage by TYPE
        type_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("leakage_type")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        type_labels = [item["leakage_type"] for item in type_data]
        type_counts = [item["total"] for item in type_data]

        # 🔥 NEW — Leakage by PROMPT CATEGORY
        category_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("response__prompt__category")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        category_labels = [
            item["response__prompt__category"] for item in category_data
        ]
        category_counts = [item["total"] for item in category_data]

        # 🔹 Top risky leaks
        top_leaks = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .select_related("response", "response__prompt")
            .order_by("-leakage_risk")[:10]
        )

    context = {
        "experiments": experiments,
        "latest_experiment": latest_experiment,
        "summary": summary,

        "field_labels": field_labels,
        "field_counts": field_counts,

        "type_labels": type_labels,
        "type_counts": type_counts,

        # NEW
        "category_labels": category_labels,
        "category_counts": category_counts,

        "top_leaks": top_leaks,
    }

    return render(request, "core/dashboard.html", context)