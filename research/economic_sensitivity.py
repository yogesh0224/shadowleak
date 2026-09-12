"""Run economic sensitivity analysis on a ShadowLeak benchmark report."""

import argparse
import json
from pathlib import Path

from research.economics import sensitivity_grid


def _csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--leakage-costs", default="1,2,5,10")
    parser.add_argument("--utility-costs", default="1,2,5")
    parser.add_argument("--latency-costs-per-ms", default="0,0.0001")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    result = sensitivity_grid(
        report,
        leakage_costs=_csv_floats(args.leakage_costs),
        utility_loss_costs=_csv_floats(args.utility_costs),
        latency_costs_per_ms=_csv_floats(args.latency_costs_per_ms),
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote economic sensitivity report to {destination}")


if __name__ == "__main__":
    main()
