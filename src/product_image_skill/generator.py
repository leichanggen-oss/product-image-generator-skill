from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import resolve_reference
from .models import GeneratorConfig, SceneConfig
from .prompts import build_scene_prompt
from .provider import OpenAIImageProvider
from .render import render_detail_card, render_dimensions


@dataclass
class ManifestItem:
    id: str
    filename: str
    kind: str
    status: str
    prompt: str | None = None
    references: list[str] | None = None
    error: str | None = None
    duration_seconds: float | None = None


def _references_for_scene(config: GeneratorConfig, scene: SceneConfig, base_dir: Path) -> list[Path]:
    values = scene.references or config.default_references
    return [resolve_reference(base_dir, value) for value in values]


def generate_all(
    config: GeneratorConfig,
    base_dir: Path,
    dry_run: bool = False,
    only: set[str] | None = None,
) -> Path:
    output_dir = Path(config.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    provider: OpenAIImageProvider | None = None
    manifest: list[ManifestItem] = []

    for scene in config.scenes:
        if only and scene.id not in only:
            continue

        started = time.perf_counter()
        item = ManifestItem(id=scene.id, filename=scene.filename, kind=scene.kind, status="pending")
        target = output_dir / scene.filename

        try:
            if scene.kind == "ai":
                prompt = build_scene_prompt(config, scene)
                references = _references_for_scene(config, scene, base_dir)
                item.prompt = prompt
                item.references = [str(path) for path in references]
                if dry_run:
                    item.status = "dry-run"
                else:
                    if provider is None:
                        provider = OpenAIImageProvider(config.api)
                    target.write_bytes(provider.edit(references, prompt))
                    item.status = "generated"

            elif scene.kind == "detail_card":
                source = resolve_reference(base_dir, scene.source or "")
                item.references = [str(source)]
                if dry_run:
                    item.status = "dry-run"
                else:
                    render_detail_card(scene, source, target, config.api.size)
                    item.status = "rendered"

            elif scene.kind == "dimensions":
                source = resolve_reference(base_dir, scene.source or "")
                item.references = [str(source)]
                if dry_run:
                    item.status = "dry-run"
                else:
                    render_dimensions(scene, source, target, config.api.size)
                    item.status = "rendered"

            else:
                raise ValueError(f"Unsupported scene kind: {scene.kind}")

        except Exception as exc:  # keep the batch running and record failures
            item.status = "failed"
            item.error = f"{type(exc).__name__}: {exc}"
        finally:
            item.duration_seconds = round(time.perf_counter() - started, 3)
            manifest.append(item)
            print(f"[{item.status:9}] {scene.id} -> {target}")

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps([asdict(item) for item in manifest], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest_path
