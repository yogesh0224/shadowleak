from django.core.management.base import BaseCommand
from experiments.runner import run_experiment


class Command(BaseCommand):
    help = "Run ShadowLeak experiment"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, default="ShadowLeak Experiment")
        parser.add_argument("--model", type=str, default="mock")
        parser.add_argument("--guard", action="store_true", help="Enable GuardShield defense")
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--record-limit", type=int, default=5)
        parser.add_argument("--prompts-per-record", type=int, default=8)

    def handle(self, *args, **options):
        experiment_name = options["name"]
        model_name = options["model"]
        use_guardshield = options["guard"]

        experiment, total = run_experiment(
            experiment_name=experiment_name,
            model_name=model_name,
            use_guardshield=use_guardshield,
            seed=options["seed"],
            record_limit=options["record_limit"],
            prompts_per_record=options["prompts_per_record"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Experiment '{experiment.name}' completed using {model_name} with {total} responses."
            )
        )
