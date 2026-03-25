from faker import Faker
from core.models import SensitiveRecord
import random

fake = Faker()

CITIES = [
    "Kathmandu",
    "Pokhara",
    "Lalitpur",
    "Biratnagar",
    "Butwal",
    "Bhaktapur",
]

ORGANIZATIONS = [
    "Himalayan Tech",
    "Everest Data Lab",
    "Nepal Secure Systems",
    "AI Valley",
    "PrivacyWorks",
    "Kathmandu Digital Group",
]


def generate_sensitive_records(count=20):
    records = []

    for _ in range(count):
        record = SensitiveRecord.objects.create(
            name=fake.name(),
            email=fake.email(),
            phone=fake.msisdn()[:10],
            city=random.choice(CITIES),
            organization=random.choice(ORGANIZATIONS),
            dob=fake.date_of_birth(minimum_age=20, maximum_age=45),
        )
        records.append(record)

    return records