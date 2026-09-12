from django.core.management.base import BaseCommand, CommandError

from data_generator.generator import generate_sensitive_records


class Command(BaseCommand):
    help = "Create deterministic synthetic canary records for experiments"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        if options["count"] < 1:
            raise CommandError("--count must be positive")
        records = generate_sensitive_records(
            count=options["count"], seed=options["seed"]
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Ensured {len(records)} deterministic synthetic canary records exist."
            )
        )
