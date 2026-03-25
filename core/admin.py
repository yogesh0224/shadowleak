from django.contrib import admin
from .models import (
    SensitiveRecord,
    PromptTemplate,
    GeneratedPrompt,
    Experiment,
    ModelResponse,
    LeakageResult,
    ExperimentSummary,
)


@admin.register(SensitiveRecord)
class SensitiveRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "city", "organization", "created_at")
    search_fields = ("name", "email", "city", "organization")
    list_filter = ("city", "organization", "created_at")


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "template_text", "active")
    search_fields = ("template_text",)
    list_filter = ("category", "active")


@admin.register(GeneratedPrompt)
class GeneratedPromptAdmin(admin.ModelAdmin):
    list_display = ("id", "record", "category", "created_at")
    search_fields = ("final_prompt", "record__name", "record__email")
    list_filter = ("category", "created_at")


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "model_name", "scenario_type", "created_at")
    search_fields = ("name", "model_name", "scenario_type")
    list_filter = ("model_name", "scenario_type", "created_at")


@admin.register(ModelResponse)
class ModelResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "experiment", "prompt", "latency", "created_at")
    search_fields = ("output_text",)
    list_filter = ("created_at",)


@admin.register(LeakageResult)
class LeakageResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "response",
        "field_name",
        "leakage_type",
        "similarity_score",
        "confidence_score",
        "severity_weight",
        "leakage_risk",
    )
    search_fields = ("field_name", "matched_text")
    list_filter = ("field_name", "leakage_type")


@admin.register(ExperimentSummary)
class ExperimentSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "experiment",
        "exposure_rate",
        "exact_leak_rate",
        "partial_leak_rate",
        "semantic_leak_rate",
        "overall_risk_score",
        "risk_level",
    )
    list_filter = ("risk_level",)