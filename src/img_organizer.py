from pathlib import Path
import hashlib
import imagehash
from PIL import Image
from src.file_utils import safe_copy


SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def iter_image_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXT]


# ====================== SHA256 ======================
def sha256(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_exact_duplicates(files):
    m = {}
    for p in files:
        h = sha256(p)
        m.setdefault(h, []).append(p)
    return {k: v for k, v in m.items() if len(v) > 1}


# ====================== pHash ======================
def phash(path: Path):
    try:
        with Image.open(path) as img:
            return imagehash.phash(img)
    except:
        return None


def find_similar_images(files, threshold=6):
    hashes = {}
    for p in files:
        h = phash(p)
        if h:
            hashes[p] = h

    used = set()
    groups = []

    items = list(hashes.items())
    for i in range(len(items)):
        img1, h1 = items[i]
        if img1 in used:
            continue

        group = [img1]

        for j in range(i + 1, len(items)):
            img2, h2 = items[j]
            if img2 in used:
                continue

            if h1 - h2 <= threshold:
                group.append(img2)
                used.add(img2)

        if len(group) > 1:
            groups.append(group)
            used.update(group)

    return groups


# ====================== 해상도 범위 ======================
def get_resolution(path: Path):
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return None


def classify_resolution(w, h):
    size = max(w, h)

    if size < 720:
        return "low_0-720p"
    elif size < 1080:
        return "mid_720-1080p"
    elif size < 1440:
        return "high_1080-1440p"
    else:
        return "ultra_1440p+"

# ====================== 처리 ======================
def organize_images(
    root: Path,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    auto=False,
    copy_mode=False,
):
    files = iter_image_files(root)
    logs = []
    summary = {}

    if auto:
        move_duplicates = True
        move_similar = True
        sort_resolution = True
        logs.append("[AUTO] 모든 옵션 적용됨")

    # 정확한 중복
    if move_duplicates:
        dup_map = find_exact_duplicates(files)
        out = root / "_duplicates"
        for h, group in dup_map.items():
            keep = group[0]
            for p in group[1:]:
                safe_copy(p, out / h[:8])
        summary["중복 정리 수"] = sum(len(v) - 1 for v in dup_map.values())

    # 유사 이미지
    if move_similar:
        groups = find_similar_images(files)
        out = root / "_similar"
        for idx, g in enumerate(groups, 1):
            base = out / f"group_{idx}"
            for p in g:
                safe_copy(p, base)
        summary["유사 정리 수"] = len(groups)

    # 해상도 범위 정리
    if sort_resolution:
        out = root / "_resolution"
        for p in files:
            r = get_resolution(p)
            if r:
                w, h = r
                folder = classify_resolution(w, h)
                safe_copy(p, out / folder)

        summary["해상도 정리 수"] = len(files)

    return summary, logs
