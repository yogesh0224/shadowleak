from core.models import SensitiveRecord
from research.canaries import generate_canaries


def generate_sensitive_records(count=20, seed=42):
    """Persist deterministic synthetic canaries, never Faker identities."""
    records = []
    for canary in generate_canaries(count=count, seed=seed):
        record, _ = SensitiveRecord.objects.get_or_create(
            email=canary.email,
            defaults={
                "name": canary.name,
                "phone": canary.phone,
                "city": canary.city,
                "organization": canary.organization,
                "dob": canary.dob,
            },
        )
        records.append(record)
    return records
