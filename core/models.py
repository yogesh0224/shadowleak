from django.db import models


class SensitiveRecord(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class PromptTemplate(models.Model):
    CATEGORY_CHOICES = [
        ("direct", "Direct"),
        ("indirect", "Indirect"),
        ("roleplay", "Roleplay"),
        ("obfuscated", "Obfuscated"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    template_text = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category}: {self.template_text[:50]}"


class GeneratedPrompt(models.Model):
    record = models.ForeignKey(SensitiveRecord, on_delete=models.CASCADE)
    template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE,null=True, blank=True)
    final_prompt = models.TextField()
    category = models.CharField(max_length=50)
    is_adversarial = models.BooleanField(default=False)
    attack_strategy = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.final_prompt[:80]


class Experiment(models.Model):
    name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100)
    scenario_type = models.CharField(max_length=100, default="context_exposure")
    use_guardshield = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ModelResponse(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    prompt = models.ForeignKey(GeneratedPrompt, on_delete=models.CASCADE)
    output_text = models.TextField()
    latency = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response #{self.id} for prompt {self.prompt_id}"


class LeakageResult(models.Model):
    LEAKAGE_TYPES = [
        ("exact", "Exact"),
        ("partial", "Partial"),
        ("semantic", "Semantic"),
        ("none", "None"),
    ]

    response = models.ForeignKey(ModelResponse, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    leakage_type = models.CharField(max_length=20, choices=LEAKAGE_TYPES)
    matched_text = models.TextField(blank=True, null=True)
    similarity_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    severity_weight = models.FloatField(default=0.0)
    leakage_risk = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.field_name} - {self.leakage_type}"


class ExperimentSummary(models.Model):
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE)
    exposure_rate = models.FloatField(default=0.0)
    exact_leak_rate = models.FloatField(default=0.0)
    partial_leak_rate = models.FloatField(default=0.0)
    semantic_leak_rate = models.FloatField(default=0.0)
    overall_risk_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=50, default="Low")

    def __str__(self):
        return f"Summary for {self.experiment.name}"

class MLPredictionResult(models.Model):
    response = models.OneToOneField('ModelResponse', on_delete=models.CASCADE)

    predicted_leak = models.BooleanField()
    confidence_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ML Prediction for Response {self.response.id}"