# Product Image Generator Skill

A Codex/agent skill plus a runnable Python batch generator for ecommerce and independent-store product images.

It takes real product references and produces multiple **separate** assets in one run. The included cold-plunge example is configured for a 1 HP chiller and an oval tub.

## What it generates

- Hero image
- Studio front and 3/4 images
- Complete-system image
- Bathroom, home-gym, outdoor, and wellness scenes
- Filter, cooling-fan, and control-panel detail cards
- Programmatic dimension graphic

The generator does not create a collage unless the configuration explicitly requests one.

## Repository structure

```text
.agents/skills/product-image-generator/SKILL.md  Codex repository skill
SKILL.md                                        Installable skill root
scripts/generate.py                             One-command entry point
src/product_image_skill/                        Python implementation
examples/cold-plunge/                           Ready-to-edit product configs
examples/cold-plunge/references/                User-supplied references
```

## Quick start

### 1. Install

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e .
```

### 2. Set the API key

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-key"

# macOS/Linux
export OPENAI_API_KEY="your-key"
```

### 3. Generate the complete set

```bash
python scripts/generate.py examples/cold-plunge/product-oval.yaml
```

Outputs are written to:

```text
outputs/cold-plunge-oval/
```

Use the round-tub variant with:

```bash
python scripts/generate.py examples/cold-plunge/product-round.yaml
```

## Draft mode

To validate the configuration and build prompts without spending image-generation credits:

```bash
python scripts/generate.py examples/cold-plunge/product-oval.yaml --dry-run
```

## Cost and speed controls

Edit the YAML:

```yaml
api:
  model: gpt-image-2
  quality: low       # low for drafts, medium/high for final production
  size: 1536x1024
  output_format: webp
  output_compression: 85
```

The batch process makes one API request per AI-generated scene. Technical detail cards and the dimension graphic are rendered locally with Pillow.

## Product integrity strategy

The generator sends multiple product reference images to the image-editing endpoint and adds a strict product-lock block to every prompt. Technical graphics are not delegated to the image model.

For maximum fidelity:

1. Use clean front and 3/4 product images.
2. Add a side/rear image when ports or filters must remain visible.
3. Keep each SKU in a separate YAML file.
4. Use verified facts only.
5. Review generated outputs before publishing.

## Install as a Codex skill

Use the repository directly in a Codex project, or copy the root folder to your user skills directory. The repository also contains `.agents/skills/product-image-generator/SKILL.md`, so Codex can activate the skill while working inside this repository.

## License

MIT. The example reference images remain the property of their owner and are included only as user-provided project inputs.
