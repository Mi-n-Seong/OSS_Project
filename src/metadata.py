from pathlib import Path
from datetime import datetime
from PIL import Image


def get_resolution(path: Path):
    try:
        with Image.open(path) as img:
            return img.size  # (w, h)
    except:
        return None


def get_exif_datetime(path: Path):
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if 36867 in exif:
                date_str = exif[36867]
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except:
        pass
    return None


def get_file_date(path: Path):
    exif_dt = get_exif_datetime(path)
    if exif_dt:
        return exif_dt.date()
    return datetime.fromtimestamp(path.stat().st_mtime).date()


def get_extension(path: Path):
    return path.suffix.lower().replace(".", "")


def get_file_size(path: Path):
    return path.stat().st_size
