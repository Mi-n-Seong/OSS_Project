import hashlib
from pathlib import Path
from PIL import Image, ExifTags
import imagehash

from .file_utils import move_files_to_group


SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


def iter_image_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_FORMATS]


# ---------------------------------------------------------
# 1) 완전 중복 탐지 (SHA256)
# ---------------------------------------------------------
def find_exact_duplicates(files):
    hash_dict = {}
    for f in files:
        try:
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            hash_dict.setdefault(h, []).append(f)
        except:
            pass
    return {h: v for h, v in hash_dict.items() if len(v) > 1}


def move_exact_duplicates(duplicates, dest):
    for i, (_, group) in enumerate(duplicates.items(), 1):
        move_files_to_group(dest / f"group_{i}", group)


# ---------------------------------------------------------
# 2) 유사 이미지 탐지 (pHash)
# ---------------------------------------------------------
def find_similar_images(files, threshold=5):
    ph = []
    for f in files:
        try:
            ph.append((f, imagehash.phash(Image.open(f))))
        except:
            pass

    visited = set()
    groups = []

    for i in range(len(ph)):
        if i in visited:
            continue
        base, bh = ph[i]
        group = [base]
        visited.add(i)

        for j in range(i + 1, len(ph)):
            if j in visited:
                continue
            f, h = ph[j]
            if bh - h <= threshold:
                group.append(f)
                visited.add(j)

        if len(group) > 1:
            groups.append(group)

    return groups


def move_similar_images(groups, dest):
    for i, group in enumerate(groups, 1):
        move_files_to_group(dest / f"group_{i}", group)


# ---------------------------------------------------------
# 3) 해상도/확장자/날짜 정리
# ---------------------------------------------------------
def sort_by_resolution(files, dest):
    for f in files:
        try:
            w, h = Image.open(f).size
            if w < 640:
                folder = dest / "small"
            elif w < 1920:
                folder = dest / "medium"
            else:
                folder = dest / "large"
            move_files_to_group(folder, [f])
        except:
            pass


def sort_by_extension(files, dest):
    for f in files:
        ext = f.suffix.lower().replace(".", "")
        move_files_to_group(dest / ext, [f])


def get_exif_date(path: Path):
    try:
        img = Image.open(path)
        ex = img._getexif()
        if not ex:
            return None
        for k, v in ex.items():
            if ExifTags.TAGS.get(k) == "DateTimeOriginal":
                return v.split()[0].replace(":", "-")
    except:
        pass
    return None


def sort_by_date(files, dest):
    for f in files:
        date = get_exif_date(f)
        if not date:
            move_files_to_group(dest / "unknown", [f])
        else:
            move_files_to_group(dest / date, [f])


# ---------------------------------------------------------
# 4) 스마트 정리 — 제일 큰 해상도만 남기기
# ---------------------------------------------------------
def resolution_of(path: Path):
    try:
        return Image.open(path).size
    except:
        return (0, 0)


def smart_keep_best(groups, dest):
    for i, group in enumerate(groups, 1):
        best = max(group, key=lambda f: resolution_of(f)[0] * resolution_of(f)[1])
        others = [f for f in group if f != best]
        move_files_to_group(dest / f"group_{i}", others)


# ---------------------------------------------------------
# 5) 자동 rename
# ---------------------------------------------------------
def auto_rename(files, dest):
    for f in files:
        date = get_exif_date(f)
        if not date:
            move_files_to_group(dest / "unknown", [f])
        else:
            new_name = f"IMG_{date}{f.suffix}"
            folder = dest / date
            move_files_to_group(folder, [f.rename(f.with_name(new_name))])
