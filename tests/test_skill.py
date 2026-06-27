from pathlib import Path

from product_image_skill.config import load_config
from product_image_skill.prompts import build_scene_prompt


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "cold-plunge" / "product-oval.yaml"


def test_example_config_loads() -> None:
    config, base_dir = load_config(CONFIG)
    assert base_dir.name == "cold-plunge"
    assert config.product.sku == "cold-plunge-oval-1hp"
    assert len(config.scenes) == 12
    assert len({scene.filename for scene in config.scenes}) == 12


def test_prompt_enforces_separate_output_and_product_lock() -> None:
    config, _ = load_config(CONFIG)
    prompt = build_scene_prompt(config, config.scenes[0])
    assert "exactly ONE standalone" in prompt
    assert "Do not create a collage" in prompt
    assert config.product.sku in prompt
    assert "changing the oval tub into a round tub" in prompt
