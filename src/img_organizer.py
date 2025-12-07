# src/img_organizer.py
from pathlib import Path
import hashlib
from PIL import Image
import imagehash
from src.file_utils import safe_copy, safe_delete

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def iter_image_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXT]


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


def get_resolution(path: Path):
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return None


def classify_resolution(w, h):
    size = max(w, h)
    if size < 720: return "low_0-720p"
    elif size < 1440: return "mid_720-1440p"
    elif size < 2880: return "high_1440-2880p"
    else: return "ultra_2880p+"


# ====================== 메인 처리 ======================
def organize_images(
    root: Path,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    auto=False,
    delete_duplicates=False,  # ★ 자동 삭제 ON
):
    files = iter_image_files(root)
    logs = []
    summary = {}

    # AUTO → 모든 기능 ON
    if auto:
        move_duplicates = True
        move_similar = True
        sort_resolution = True
        delete_duplicates = True
        logs.append("[AUTO] 모든 옵션 자동 적용")

    # --- 정확한 중복 ---
    if move_duplicates:
        dup_map = find_exact_duplicates(files)
        deleted_count = 0

        logs.append("[중복] 정확한 중복 검사 시작")

        for h, group in dup_map.items():
            keep = group[0]
            logs.append(f"[중복] 기준 이미지 유지: {keep}")

            # ★ 중복 자동 삭제
            for p in group[1:]:
                if delete_duplicates:
                    if safe_delete(p):
                        deleted_count += 1
                        logs.append(f"  삭제됨 → {p}")
                else:
                    pass  # 삭제 안 함

        summary["중복 삭제 수"] = deleted_count
        logs.append(f"[중복] 총 {deleted_count}개 삭제 완료")

    # --- 유사 이미지 ---
    if move_similar:
        groups = find_similar_images(files)
        out = root / "_similar"
        moved = 0

        logs.append("[유사] 유사 이미지 검사 시작")

        for idx, group in enumerate(groups, 1):
            keep = group[0]
            for p in group[1:]:
                dst = safe_copy(p, out / f"group_{idx}")
                logs.append(f"  유사 그룹 복사: {p} → {dst}")
                moved += 1

        summary["유사 정리 수"] = moved

    # --- 해상도 정리 ---
    if sort_resolution:
        out = root / "_resolution"
        count = 0

        logs.append("[해상도] 해상도 정리 시작")

        for p in files:
            r = get_resolution(p)
            if r:
                w, h = r
                dst = safe_copy(p, out / classify_resolution(w, h))
                logs.append(f"  복사됨: {p} → {dst}")
                count += 1

        summary["해상도 정리 수"] = count

    return summary, logs
