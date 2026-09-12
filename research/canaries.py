"""Deterministic synthetic records for privacy-leakage experiments."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class CanaryRecord:
    name: str
    email: str
    phone: str
    city: str
    organization: str
    dob: date


def generate_canaries(count: int = 20, seed: int = 42) -> list[CanaryRecord]:
    """Return visibly synthetic, reproducible identities.

    ``example.invalid`` is reserved for documentation/testing. Values are
    generated locally and are not intended to resemble real people.
    """
    if count < 1:
        raise ValueError("count must be positive")
    rng = random.Random(seed)
    base_date = date(1980, 1, 1)
    records = []
    for index in range(1, count + 1):
        token = f"{seed:04d}-{index:04d}"
        records.append(
            CanaryRecord(
                name=f"Canary Subject {token}",
                email=f"canary-{token}@example.invalid",
                phone=f"555{index:07d}",
                city=f"Synthetic City {1 + (index - 1) % 8}",
                organization=f"Canary Research Unit {1 + (index - 1) % 6}",
                dob=base_date + timedelta(days=rng.randrange(365 * 25)),
            )
        )
    return records
