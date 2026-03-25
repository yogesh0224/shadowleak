from django.core.management.base import BaseCommand
from ml_detector.train import train_binary_classifier


class Command(BaseCommand):
    help = "Train ML leakage detection model"

    def handle(self, *args, **options):
        train_binary_classifier()
        self.stdout.write(self.style.SUCCESS("Leakage classifier trained successfully."))