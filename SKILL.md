---
name: product-image-generator
summary: 一键批量生成独立站产品图，默认输出多张单独图片，并锁定产品结构、SKU、品牌和参数。
description: Use this skill when the user wants ecommerce product images, independent-store product gallery assets, AI product photography, lifestyle scenes, product detail cards, dimension graphics, or a one-click batch image set. It preserves the real product and outputs separate files by default. Do not use it for collages or long detail-page composites unless the user explicitly asks for them.
version: 1.0.0
---

# Product Image Generator

## Objective

Turn one or more real product reference images plus verified product facts into a consistent set of independent ecommerce images.

Default behavior:

- Generate separate image files, never a collage.
- Preserve the exact product geometry, control panels, ports, fan structure, fasteners, filters, wheels, labels, colors, and brand marks.
- Keep each SKU isolated. Never mix round and oval tubs, color variants, sizes, or accessory bundles.
- Use AI for environments, lighting, people, and styling; use real references and programmatic composition for dimensions, labels, and technical claims.
- Do not invent app control, Wi-Fi, UV, filtration, temperature range, certifications, dimensions, or performance claims.

## Required inputs

Read these from the user's files or ask only for facts that are missing and materially affect correctness:

1. Product reference images: front, 3/4 angle, rear/side when available, detail images.
2. Product name and SKU/variant.
3. Verified dimensions and features.
4. Target market and language.
5. Output aspect ratio and number of images, if the user has a preference.

If the user does not specify a set, use the default 12-image set below.

## Default 12-image set

1. `01_hero` — premium hero image with the complete product system.
2. `02_studio_front` — clean studio front view.
3. `03_studio_angle` — clean 3/4 view.
4. `04_complete_system` — product plus required accessories and connections.
5. `05_bathroom` — premium bathroom/shower-room scene.
6. `06_home_gym` — recovery scene in a home gym.
7. `07_outdoor` — patio, poolside, or lake-house setting.
8. `08_wellness` — hotel, spa, or wellness-club scene.
9. `09_filter_detail` — real or cropped filter detail.
10. `10_cooling_detail` — real or cropped cooling/fan detail.
11. `11_control_panel` — real or cropped control-panel detail.
12. `12_dimensions` — programmatically drawn dimension graphic using verified numbers.

## Workflow

### 1. Inspect and classify inputs

Classify every image as one of:

- product front
- product angle
- product detail
- dimension/spec reference
- style reference
- scene reference

Do not treat a supplier composite as a clean product reference when a clean white-background image is available.

### 2. Create a product lock

Before generation, write a concise lock block containing:

- exact product identity
- selected SKU/variant
- fixed geometry and visible components
- verified facts
- forbidden changes

Example:

```yaml
product_lock:
  sku: cold-plunge-oval-1hp
  preserve:
    - black powder-coated rectangular chiller housing
    - large circular front cooling fan with crossed support bars
    - top control panel and two recessed handles
    - side transparent filter canister
    - green water-in and red water-out ports
    - caster wheels and visible fasteners
  forbid:
    - changing fan count or grille
    - moving the control panel
    - removing the filter
    - changing the tub from oval to round
    - adding app or Wi-Fi features
```

### 3. Choose the safest production method

Use this priority order:

1. Real photo crop/composite for technical details.
2. Programmatic layout for dimensions, arrows, text, icons, and specifications.
3. High-fidelity image editing with multiple product references for lifestyle and hero scenes.
4. Pure text-to-image only for empty backgrounds, never for the final technical product representation.

### 4. Generate independent files

Run one generation request per scene. Do not request one image containing several panels. Each file must communicate one primary message.

When scripts are available, run:

```bash
python scripts/generate.py examples/cold-plunge/product-oval.yaml
```

For another product, copy the YAML example, replace references and verified facts, then run the same command.

### 5. Quality control

Reject or regenerate an image when any of these occur:

- geometry, ports, fan, control panel, filter, screws, wheels, or branding changed
- round and oval SKUs are mixed
- product scale is physically implausible
- person intersects or clips through the product
- hoses or cables connect to impossible locations
- text or numbers are AI-generated and inaccurate
- product floats without contact shadow
- lighting direction conflicts with the environment
- a single file contains a collage, multiple panels, or a long detail-page layout

## Prompt rules

Every AI scene prompt must include:

- exact product preservation instruction
- selected SKU
- camera position and framing
- environment and lighting
- product scale and floor contact
- explicit prohibition on invented text/features
- instruction to return one standalone image

Do not ask the image model to render precise dimensions or long marketing copy. Add those programmatically afterward.

## Output rules

- Default format: WebP for generated scenes, PNG for technical graphics.
- Default size: 1536×1024 landscape.
- Save all files to one output folder with numeric prefixes.
- Write `manifest.json` containing file name, prompt, source references, status, and any errors.
- Return direct links to each separate output file when operating in an environment that supports file links.

## User preference

Unless the user explicitly says “做详情页长图” or “合成拼图”, always output separate images.
