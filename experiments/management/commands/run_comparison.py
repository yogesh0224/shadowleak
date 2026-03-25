from django.core.management.base import BaseCommand
from experiments.comparison import run_multi_model_experiment


class Command(BaseCommand):
    help = "Run multi-model comparison experiment"

    def handle(self, *args, **kwargs):
        experiments = run_multi_model_experiment()

        self.stdout.write(
            self.style.SUCCESS(f"{len(experiments)} experiments completed.")
        )