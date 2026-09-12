from django.core.management.base import BaseCommand
from ml_detector.train import train_binary_classifier


class Command(BaseCommand):
    help = "Train the ML detector from independently annotated gold labels"

    def add_arguments(self, parser):
        parser.add_argument("--gold-labels", required=True)
        parser.add_argument("--report", default="reports/grouped_cv_metrics.json")
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        report = train_binary_classifier(
            gold_labels_path=options["gold_labels"],
            report_path=options["report"],
            seed=options["seed"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Leakage classifier trained with grouped validation: "
                f"F1={report['metrics']['f1']:.3f}"
            )
        )
