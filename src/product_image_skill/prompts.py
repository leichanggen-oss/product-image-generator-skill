from __future__ import annotations

from .models import GeneratorConfig, SceneConfig


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def build_scene_prompt(config: GeneratorConfig, scene: SceneConfig) -> str:
    product = config.product
    visual_direction = _bullets(config.visual_direction)

    return f"""
Create exactly ONE standalone ecommerce product image. Do not create a collage, grid,
carousel screenshot, split panel, long detail page, contact sheet, or before/after layout.

PRODUCT IDENTITY
- Product: {product.product_name}
- SKU: {product.sku}
- Selected variant: {product.variant}
- Product description: {product.description}

STRICT PRODUCT LOCK — preserve every visible real-world detail from the reference images:
{_bullets(product.preserve)}

FORBIDDEN CHANGES:
{_bullets(product.forbid)}

VERIFIED FEATURES THAT MAY BE SHOWN:
{_bullets(product.verified_features)}

DO NOT CLAIM OR VISUALIZE:
{_bullets(product.prohibited_claims)}

SCENE BRIEF
{scene.prompt}

VISUAL DIRECTION
{visual_direction}

EXECUTION RULES
- Use the supplied images as high-fidelity product references, not loose inspiration.
- Keep the exact housing, proportions, fan grille, controls, filter, ports, fasteners,
  wheels, handles, colors, materials, labels, and accessory relationships visible in the references.
- Keep the selected SKU isolated; do not substitute or mix another shape, size, or variant.
- The product must sit naturally on the floor with physically credible contact shadows,
  reflections, perspective, scale, cable routing, and hose connections.
- Do not add invented accessories, screens, phones, apps, Wi-Fi symbols, certifications,
  water effects, logos, labels, dimensions, or marketing copy.
- Do not redesign or beautify the machinery. Improve only the environment, composition,
  lighting, styling, and photographic finish.
- Avoid AI-generated text. Leave clean negative space where copy could later be overlaid.
- Photorealistic premium commercial product photography suitable for an independent-store product gallery.
- Target market: {product.market}. Language context: {product.language}.
""".strip()
