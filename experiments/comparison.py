from experiments.runner import run_experiment


MODELS = ["mock", "hf"]


def run_multi_model_experiment(base_name="Model Comparison"):
    experiments = []

    for model_name in MODELS:
        name = f"{base_name} - {model_name}"
        exp, _ = run_experiment(
            experiment_name=name,
            model_name=model_name
        )
        experiments.append(exp)

    return experiments