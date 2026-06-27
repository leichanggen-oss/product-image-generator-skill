from __future__ import annotations

from pathlib import Path

import yaml

from .models import GeneratorConfig


def load_config(path: str | Path) -> tuple[GeneratorConfig, Path]:
    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a YAML mapping")

    return GeneratorConfig.model_validate(raw), config_path.parent


def resolve_reference(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()
