from pathlib import Path
import hashlib
import imagehash
from PIL import Image
from src.file_utils import safe_copy


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
    return {k: v for v in m.items() if len(v) > 1}


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

    if size < 720:
        return "low_0-720p"
    elif size < 1080:
        return "mid_720-1080p"
    elif size < 1440:
        return "high_1080-1440p"
    else:
        return "ultra_1440p+"


# ====================== 진행률 지원 organize_images ======================
def organize_images(
    root: Path,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    auto=False,
    copy_mode=False,
    progress_callback=None,  # ★ 진행률 콜백 추가
):
    files = iter_image_files(root)
    logs = []
    summary = {}

    total_steps = len(files)
    current_step = 0

    def update_progress():
        nonlocal current_step
        if progress_callback:
            progress_callback(current_step, total_steps)

    if auto:
        move_duplicates = True
        move_similar = True
        sort_resolution = True
        logs.append("[AUTO] 모든 옵션이 자동으로 선택됨")

    # ---------- 정확한 중복 ----------
    if move_duplicates:
        logs.append("[중복] 정확한 중복 검사 시작")

        dup_map = find_exact_duplicates(files)
        out = root / "_duplicates"
        total_moved = 0

        for h, group in dup_map.items():
            keep = group[0]
            logs.append(f"[중복] 기준 이미지 유지 → {keep.name}")

            for p in group[1:]:
                dst = safe_copy(p, out / h[:8])
                logs.append(f"  - 복사됨: {p.name} → {dst}")
                total_moved += 1

            current_step += 1
            update_progress()

        summary["중복 정리 수"] = total_moved
        logs.append(f"[중복] 총 {total_moved}개 복사 완료")

    # ---------- 유사 이미지 ----------
    if move_similar:
        logs.append("[유사] 유사 이미지 검사 시작")

        groups = find_similar_images(files)
        out = root / "_similar"
        total_sim = 0

        for idx, group in enumerate(groups, 1):
            base = out / f"group_{idx}"
            keep = group[0]

            logs.append(f"[유사] 그룹 {idx} 대표 이미지 → {keep.name}")

            for p in group:
                dst = safe_copy(p, base)
                logs.append(f"  - 복사됨: {p.name} → {dst}")
                total_sim += 1

            current_step += 1
            update_progress()

        summary["유사 정리 수"] = total_sim
        logs.append(f"[유사] 총 {total_sim}개 복사 완료")

    # ---------- 해상도 정리 ----------
    if sort_resolution:
        logs.append("[해상도] 해상도 정리 시작")

        out = root / "_resolution"
        total_res = 0

        for p in files:
            r = get_resolution(p)
            if r:
                w, h = r
                folder = classify_resolution(w, h)
                dst = safe_copy(p, out / folder)
                logs.append(f"  - {p.name} → {dst}")
                total_res += 1

            current_step += 1
            update_progress()

        summary["해상도 정리 수"] = total_res
        logs.append(f"[해상도] 총 {total_res}개 복사 완료")

    return summary, logs
