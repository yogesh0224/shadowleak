from django.core.management.base import BaseCommand
from core.models import PromptTemplate
from prompt_engine.templates_seed import TEMPLATES


class Command(BaseCommand):
    help = "Seed prompt templates"

    def handle(self, *args, **kwargs):
        created = 0

        for category, text in TEMPLATES:
            obj, is_created = PromptTemplate.objects.get_or_create(
                category=category,
                template_text=text,
                defaults={"active": True},
            )
            if is_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created} prompt templates added.")
        )