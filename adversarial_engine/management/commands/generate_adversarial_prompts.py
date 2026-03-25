from django.core.management.base import BaseCommand
from core.models import SensitiveRecord
from adversarial_engine.generator import generate_adversarial_prompts_for_record


class Command(BaseCommand):
    help = "Generate smarter adversarial prompts for all records"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5)
        parser.add_argument("--per_strategy", type=int, default=2)

    def handle(self, *args, **options):
        limit = options["limit"]
        per_strategy = options["per_strategy"]

        records = SensitiveRecord.objects.all()[:limit]
        total = 0

        for record in records:
            prompts = generate_adversarial_prompts_for_record(
                record,
                per_strategy=per_strategy,
            )
            total += len(prompts)

        self.stdout.write(
            self.style.SUCCESS(f"Generated {total} adversarial prompts.")
        )