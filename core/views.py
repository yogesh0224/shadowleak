from django.shortcuts import render
from django.db.models import Count,Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Experiment, ModelResponse, LeakageResult, ExperimentSummary
from .serializers import (
    ExperimentSerializer,
    ModelResponseSerializer,
    LeakageResultSerializer,
    ExperimentSummarySerializer,
)

from core.models import MLPredictionResult

@api_view(["GET"])
def list_experiments(request):
    experiments = Experiment.objects.all().order_by("-created_at")
    serializer = ExperimentSerializer(experiments, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def experiment_summary(request, experiment_id):
    summary = ExperimentSummary.objects.filter(experiment_id=experiment_id).first()
    if not summary:
        return Response({"error": "Summary not found"}, status=404)

    serializer = ExperimentSummarySerializer(summary)
    return Response(serializer.data)


@api_view(["GET"])
def experiment_responses(request, experiment_id):
    responses = (
        ModelResponse.objects
        .filter(experiment_id=experiment_id)
        .order_by("-created_at")
    )
    serializer = ModelResponseSerializer(responses, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def experiment_leaks(request, experiment_id):
    leaks = LeakageResult.objects.filter(response__experiment_id=experiment_id)
    serializer = LeakageResultSerializer(leaks, many=True)
    return Response(serializer.data)


def dashboard(request):
    experiments = Experiment.objects.all().order_by("-created_at")[:10]
    latest_experiment = experiments.first()

    summary = None
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

        field_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("field_name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        type_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("leakage_type")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        category_data = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .values("response__prompt__category")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        top_leaks = (
            LeakageResult.objects
            .filter(response__experiment=latest_experiment)
            .select_related("response", "response__prompt")
            .order_by("-leakage_risk")[:10]
        )

        field_labels = [item["field_name"] for item in field_data]
        field_counts = [item["total"] for item in field_data]

        type_labels = [item["leakage_type"] for item in type_data]
        type_counts = [item["total"] for item in type_data]

        category_labels = [item["response__prompt__category"] for item in category_data]
        category_counts = [item["total"] for item in category_data]

    context = {
        "experiments": experiments,
        "latest_experiment": latest_experiment,
        "summary": summary,
        "field_labels": field_labels,
        "field_counts": field_counts,
        "type_labels": type_labels,
        "type_counts": type_counts,
        "category_labels": category_labels,
        "category_counts": category_counts,
        "top_leaks": top_leaks,
    }

    return render(request, "core/dashboard.html", context)


def comparison_dashboard(request):
    summaries = (
        ExperimentSummary.objects
        .select_related("experiment")
        .order_by("-id")[:10]
    )

    model_names = []
    risk_scores = []

    for s in summaries:
        model_names.append(s.experiment.model_name)
        risk_scores.append(s.overall_risk_score)

    context = {
        "summaries": summaries,
        "model_names": model_names,
        "risk_scores": risk_scores,
    }

    return render(request, "core/comparison.html", context)


def defense_comparison(request):
    summaries = (
        ExperimentSummary.objects
        .select_related("experiment")
        .order_by("-id")[:10]
    )

    labels = []
    risks = []

    for s in summaries:
        shield_label = "Shield" if s.experiment.use_guardshield else "No Shield"
        labels.append(f"{s.experiment.model_name} ({shield_label})")
        risks.append(s.overall_risk_score)

    context = {
        "summaries": summaries,
        "labels": labels,
        "risks": risks,
    }

    return render(request, "core/defense.html", context)

from django.shortcuts import render
from core.models import ModelResponse, LeakageResult, MLPredictionResult,GeneratedPrompt


def ml_comparison(request):
    try:
        responses = ModelResponse.objects.select_related("prompt").all().order_by("-id")[:50]

        data = []

        for r in responses:
            rule_leak = LeakageResult.objects.filter(response=r).exists()

            ml = MLPredictionResult.objects.filter(response=r).first()

            ml_pred = ml.predicted_leak if ml else None
            ml_conf = ml.confidence_score if ml else None

            agreement = None
            if ml_pred is not None:
                agreement = (rule_leak == ml_pred)

            data.append({
                "prompt": r.prompt.final_prompt,
                "output": r.output_text,
                "rule": rule_leak,
                "ml": ml_pred,
                "confidence": ml_conf,
                "agreement": agreement,
            })

        # 🔥 Metrics
        total = len(data)

        rule_positive = sum(1 for d in data if d["rule"])
        ml_positive = sum(1 for d in data if d["ml"])

        agreement_count = sum(1 for d in data if d["agreement"] is True)
        agreement_rate = agreement_count / total if total else 0

        ml_extra = sum(1 for d in data if d["ml"] and not d["rule"])
        rule_extra = sum(1 for d in data if d["rule"] and not d["ml"])

        context = {
            "data": data,
            "total": total,
            "agreement_rate": round(agreement_rate, 3),
            "ml_extra": ml_extra,
            "rule_extra": rule_extra,
            "rule_positive": rule_positive,
            "ml_positive": ml_positive,
        }

        return render(request, "core/ml_comparison.html", context)

    except Exception as e:
        # 🔥 Debug fallback (VERY IMPORTANT)
        return render(request, "core/ml_comparison.html", {
            "data": [],
            "error": str(e)
        })
    
def adversarial_analysis(request):
    data = (
        LeakageResult.objects
        .filter(response__prompt__is_adversarial=True)
        .values("response__prompt__attack_strategy")
        .annotate(
            total_leaks=Count("id"),
            avg_risk=Avg("leakage_risk")
        )
        .order_by("-total_leaks")
    )

    labels = []
    counts = []
    risks = []

    for item in data:
        labels.append(item["response__prompt__attack_strategy"] or "unknown")
        counts.append(item["total_leaks"])
        risks.append(round(item["avg_risk"], 3) if item["avg_risk"] else 0)

    context = {
        "data": data,
        "labels": labels,
        "counts": counts,
        "risks": risks,
    }

    return render(request, "core/adversarial_analysis.html", context)