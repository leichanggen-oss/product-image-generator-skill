from __future__ import annotations

import base64
from contextlib import ExitStack
from pathlib import Path

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import APIConfig


class OpenAIImageProvider:
    def __init__(self, api: APIConfig) -> None:
        self.api = api
        self.client = OpenAI()

    @retry(wait=wait_exponential(multiplier=2, min=2, max=20), stop=stop_after_attempt(3), reraise=True)
    def edit(self, references: list[Path], prompt: str) -> bytes:
        if not references:
            raise ValueError("At least one image reference is required for an AI scene")
        missing = [str(path) for path in references if not path.is_file()]
        if missing:
            raise FileNotFoundError("Missing reference images: " + ", ".join(missing))

        with ExitStack() as stack:
            images = [stack.enter_context(path.open("rb")) for path in references]
            response = self.client.images.edit(
                model=self.api.model,
                image=images,
                prompt=prompt,
                size=self.api.size,
                quality=self.api.quality,
                output_format=self.api.output_format,
                output_compression=self.api.output_compression,
            )

        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("Image API returned no base64 image data")
        return base64.b64decode(response.data[0].b64_json)
