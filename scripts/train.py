#!/usr/bin/env python3
"""Training script entry point."""

import argparse
import sys
from pathlib import Path

# Add src to path to allow imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from diabetes_triage.training.train import main


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Train the diabetes triage model."
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to the training configuration YAML file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(config_path=args.config)
