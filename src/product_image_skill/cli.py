from __future__ import annotations

import argparse
import sys

from .config import load_config
from .generator import generate_all


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="product-image-generator",
        description="Generate a set of separate ecommerce product images from verified references.",
    )
    parser.add_argument("config", help="Path to the product YAML configuration")
    parser.add_argument("--dry-run", action="store_true", help="Validate and build prompts without API calls")
    parser.add_argument(
        "--only",
        help="Comma-separated scene ids to run, for example 01_hero,12_dimensions",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config, base_dir = load_config(args.config)
        only = {value.strip() for value in args.only.split(",")} if args.only else None
        manifest = generate_all(config, base_dir, dry_run=args.dry_run, only=only)
        print(f"Manifest: {manifest}")
        return 0
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
