from rest_framework import serializers
from .models import (
    Experiment,
    ExperimentSummary,
    ModelResponse,
    LeakageResult,
)


class LeakageResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakageResult
        fields = "__all__"


class ModelResponseSerializer(serializers.ModelSerializer):
    leakage_results = serializers.SerializerMethodField()

    class Meta:
        model = ModelResponse
        fields = "__all__"

    def get_leakage_results(self, obj):
        results = LeakageResult.objects.filter(response=obj)
        return LeakageResultSerializer(results, many=True).data


class ExperimentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentSummary
        fields = "__all__"


class ExperimentSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Experiment
        fields = "__all__"

    def get_summary(self, obj):
        summary = ExperimentSummary.objects.filter(experiment=obj).first()
        if summary:
            return ExperimentSummarySerializer(summary).data
        return None