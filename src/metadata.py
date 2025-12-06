import csv
from PIL import Image
from pathlib import Path


def write_metadata_csv(files, output_csv: Path):
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["파일명", "해상도", "용량(KB)"])

        for img in files:
            try:
                w, h = Image.open(img).size
                size = img.stat().st_size // 1024
                writer.writerow([img.name, f"{w}x{h}", size])
            except:
                pass
