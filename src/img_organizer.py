from pathlib import Path
import hashlib
import imagehash
from PIL import Image
from send2trash import send2trash  # 휴지통 이동
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


# ====================== 해상도 ======================
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


# ====================== 메인 처리 함수 ======================
def organize_images(
    root: Path,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    auto=False,
    copy_mode=False,
    delete_duplicates=False,       # 🔥 삭제 옵션 추가
):
    files = iter_image_files(root)
    logs = []
    summary = {}

    if auto:
        move_duplicates = True
        move_similar = True
        sort_resolution = True
        logs.append("[AUTO] 모든 옵션이 자동으로 선택됨")

    # ---------- 정확한 중복 ----------
    if move_duplicates:
        logs.append("[중복] 정확한 중복 검사 시작")
        dup_map = find_exact_duplicates(files)

        deleted_count = 0

        for h, group in dup_map.items():
            keep = group[0]
            logs.append(f"[중복] 기준 이미지 유지 → {keep.name}")

            for p in group[1:]:

                if delete_duplicates:
                    # 휴지통 이동
                    send2trash(str(p))
                    logs.append(f"  - 삭제됨(휴지통 이동): {p.name}")
                    deleted_count += 1

                else:
                    # 복사 정리 모드
                    dst = safe_copy(p, (root / "_duplicates" / h[:8]))
                    logs.append(f"  - 복사됨: {p.name} → {dst}")

        summary["정확한 중복 삭제 수"] = deleted_count

    # ---------- 유사 이미지 ----------
    if move_similar:
        logs.append("[유사] 유사 이미지 검사 시작")

        groups = find_similar_images(files)
        out = root / "_similar"
        total = 0

        for idx, g in enumerate(groups, 1):
            base = out / f"group_{idx}"
            keep = g[0]
            logs.append(f"[유사] 그룹 {idx} 대표 이미지 → {keep.name}")

            for p in g[1:]:
                dst = safe_copy(p, base)
                logs.append(f"  - 유사 이미지 복사됨: {p.name} → {dst}")
                total += 1

        summary["유사 정리 수"] = total

    # ---------- 해상도 정리 ----------
    if sort_resolution:
        logs.append("[해상도] 해상도 정리 시작")

        out = root / "_resolution"
        total = 0

        for p in files:
            r = get_resolution(p)
            if r:
                w, h = r
                folder = classify_resolution(w, h)
                dst = safe_copy(p, out / folder)
                logs.append(f"  - {p.name} → {dst}")
                total += 1

        summary["해상도 정리 수"] = total

    return summary, logs