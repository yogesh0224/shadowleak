from django.core.management.base import BaseCommand
from core.models import SensitiveRecord
from prompt_engine.generator import generate_prompts_for_record


class Command(BaseCommand):
    help = "Generate prompts for all sensitive records"

    def handle(self, *args, **kwargs):
        records = SensitiveRecord.objects.all()
        total_prompts = 0

        for record in records:
            prompts = generate_prompts_for_record(record)
            total_prompts += len(prompts)

        self.stdout.write(
            self.style.SUCCESS(f"{total_prompts} prompts generated.")
        )