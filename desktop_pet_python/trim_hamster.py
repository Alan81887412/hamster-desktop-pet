from PIL import Image
from pathlib import Path

SRC_DIR = Path("assets/hamster")
OUT_DIR = Path("assets/hamster_trimmed")

OUT_DIR.mkdir(exist_ok=True)

for img_path in SRC_DIR.glob("*.png"):
    img = Image.open(img_path).convert("RGBA")

    bbox = img.getbbox()  # 依 alpha 自動算最小邊界
    if bbox:
        trimmed = img.crop(bbox)
    else:
        trimmed = img

    out_path = OUT_DIR / img_path.name
    trimmed.save(out_path)

    print(f"trimmed: {img_path.name}")
