import time

from core.models import (
    Experiment,
    ModelResponse,
    LeakageResult,
    ExperimentSummary,
    SensitiveRecord,
    GeneratedPrompt,
)

from prompt_engine.generator import generate_prompts_for_record
from experiments.context_builder import build_context_from_record
from model_interface.mock_model import MockModelInterface
from model_interface.hf_model import HuggingFaceModelInterface

from leakage_detector.orchestrator import analyze_output
from scoring.engine import calculate_leakage_risk, get_risk_band

from guardshield.prompt_filter import is_prompt_risky, sanitize_prompt
from guardshield.output_sanitizer import sanitize_output

# 🔥 ADD THIS (ML)
from ml_detector.predict import LeakMLPredictor
from core.models import MLPredictionResult

from adversarial_engine.generator import generate_adversarial_prompts_for_record

FIELD_WEIGHTS = {
    "name": 0.30,
    "email": 0.90,
    "phone": 0.95,
    "city": 0.40,
    "organization": 0.50,
    "dob": 0.85,
}


def get_model(model_name: str):
    if model_name == "hf":
        return HuggingFaceModelInterface()
    return MockModelInterface()


def run_experiment(
    experiment_name="ShadowLeak Test",
    model_name="mock",
    use_guardshield=False,
):
    experiment = Experiment.objects.create(
        name=experiment_name,
        model_name=model_name,
        scenario_type="context_exposure",
        use_guardshield=use_guardshield,
    )

    model = get_model(model_name)

    # 🔥 INIT ML MODEL (SAFE)
    try:
        ml_predictor = LeakMLPredictor()
        print("ML model loaded successfully")
    except Exception as e:
        print("ML model NOT loaded:", e)
        ml_predictor = None

    records = SensitiveRecord.objects.all()[:5]

    total_prompts = 0
    leaking_prompts = 0
    total_risk_score = 0.0

    for record in records:
        prompts = GeneratedPrompt.objects.filter(record=record)

        if not prompts.exists():
            generate_prompts_for_record(record)
            generate_adversarial_prompts_for_record(record, per_strategy=1)
            prompts = GeneratedPrompt.objects.filter(record=record)

        prompts = prompts.order_by("-id")[:8]

        context = build_context_from_record(record)

        for prompt in prompts:
            total_prompts += 1
            print(f"\nRunning prompt: {prompt.final_prompt[:60]}")

            original_prompt = prompt.final_prompt

            # 🛡️ GuardShield (input)
            if use_guardshield and is_prompt_risky(original_prompt):
                safe_prompt = sanitize_prompt(original_prompt)
            else:
                safe_prompt = original_prompt

            start_time = time.time()
            raw_output = model.generate(safe_prompt, context=context)
            latency = time.time() - start_time

            # 🛡️ GuardShield (output)
            if use_guardshield:
                output = sanitize_output(raw_output)
            else:
                output = raw_output

            print("Model Output:", output[:100])

            response = ModelResponse.objects.create(
                experiment=experiment,
                prompt=prompt,
                output_text=output,
                latency=latency,
            )

            # 🔍 RULE-BASED DETECTION
            analysis_results = analyze_output(record, output)

            if analysis_results:
                leaking_prompts += 1

            for result in analysis_results:
                risk = calculate_leakage_risk(
                    field_name=result["field_name"],
                    leakage_type=result["leakage_type"],
                    confidence_score=result["confidence_score"],
                )

                LeakageResult.objects.create(
                    response=response,
                    field_name=result["field_name"],
                    leakage_type=result["leakage_type"],
                    matched_text=result["matched_text"],
                    similarity_score=result["similarity_score"],
                    confidence_score=result["confidence_score"],
                    severity_weight=FIELD_WEIGHTS.get(result["field_name"], 0.5),
                    leakage_risk=risk,
                )

                total_risk_score += risk

            # 🤖 ML DETECTION (NEW)
            if ml_predictor:
                try:
                    ml_result = ml_predictor.predict(
                        prompt_text=prompt.final_prompt,
                        prompt_category=prompt.category,
                        output_text=output,
                        record=record,
                    )

                    print("ML Prediction:", ml_result)

                    MLPredictionResult.objects.create(
                        response=response,
                        predicted_leak=bool(ml_result["prediction"]),
                        confidence_score=ml_result["confidence"],
                    )

                except Exception as e:
                    print("ML prediction failed:", e)

    # 📊 Summary
    exposure_rate = leaking_prompts / total_prompts if total_prompts else 0.0
    overall_risk_score = total_risk_score / total_prompts if total_prompts else 0.0
    risk_level = get_risk_band(overall_risk_score)

    ExperimentSummary.objects.create(
        experiment=experiment,
        exposure_rate=round(exposure_rate, 4),
        exact_leak_rate=0,
        partial_leak_rate=0,
        semantic_leak_rate=0,
        overall_risk_score=round(overall_risk_score, 4),
        risk_level=risk_level,
    )

    return experiment, total_prompts