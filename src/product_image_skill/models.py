from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class APIConfig(BaseModel):
    model: str = "gpt-image-2"
    quality: Literal["low", "medium", "high", "auto"] = "medium"
    size: str = "1536x1024"
    output_format: Literal["png", "jpeg", "webp"] = "webp"
    output_compression: int = Field(default=85, ge=0, le=100)

    @field_validator("size")
    @classmethod
    def validate_size(cls, value: str) -> str:
        try:
            width, height = (int(part) for part in value.lower().split("x", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("size must use WIDTHxHEIGHT, for example 1536x1024") from exc
        if width <= 0 or height <= 0:
            raise ValueError("size dimensions must be positive")
        return f"{width}x{height}"


class ProductFacts(BaseModel):
    product_name: str
    sku: str
    variant: str
    market: str = "United States"
    language: str = "English"
    description: str
    preserve: list[str]
    forbid: list[str]
    verified_features: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)


class DimensionSpec(BaseModel):
    width_mm: int = Field(gt=0)
    depth_mm: int = Field(gt=0)
    height_mm: int = Field(gt=0)


class SceneConfig(BaseModel):
    id: str
    kind: Literal["ai", "detail_card", "dimensions"]
    filename: str
    title: str | None = None
    body: str | None = None
    prompt: str | None = None
    references: list[str] = Field(default_factory=list)
    source: str | None = None
    crop: tuple[int, int, int, int] | None = None
    dimensions: DimensionSpec | None = None

    @model_validator(mode="after")
    def validate_kind_fields(self) -> "SceneConfig":
        if self.kind == "ai" and not self.prompt:
            raise ValueError(f"AI scene {self.id!r} requires prompt")
        if self.kind == "detail_card":
            if not self.source or not self.crop:
                raise ValueError(f"detail_card scene {self.id!r} requires source and crop")
        if self.kind == "dimensions":
            if not self.source or not self.dimensions:
                raise ValueError(f"dimensions scene {self.id!r} requires source and dimensions")
        return self


class GeneratorConfig(BaseModel):
    output_dir: str
    api: APIConfig = Field(default_factory=APIConfig)
    product: ProductFacts
    default_references: list[str]
    visual_direction: list[str] = Field(default_factory=list)
    scenes: list[SceneConfig]

    @model_validator(mode="after")
    def unique_scene_ids_and_filenames(self) -> "GeneratorConfig":
        ids = [scene.id for scene in self.scenes]
        filenames = [scene.filename for scene in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("scene ids must be unique")
        if len(filenames) != len(set(filenames)):
            raise ValueError("scene filenames must be unique")
        return self
