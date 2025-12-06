from pathlib import Path
import hashlib
import imagehash
from PIL import Image

# 🔥 절대 경로 import (중요!! ImportError 방지)
from src.file_utils import safe_move
from src.metadata import get_resolution, get_file_date, get_extension


SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


# ================= 이미지 스캔 =================

def iter_image_files(root: Path) -> list[Path]:
    """폴더 내부 모든 이미지 파일 재귀 탐색"""
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXT]


# ================= 정확한 중복 (SHA256) =================

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_exact_duplicates(files: list[Path]):
    hash_map: dict[str, list[Path]] = {}
    for p in files:
        h = sha256(p)
        hash_map.setdefault(h, []).append(p)
    return {k: v for k, v in hash_map.items() if len(v) > 1}


def _handle_duplicates(files, root: Path, logs, summary):
    dup_map = find_exact_duplicates(files)
    if not dup_map:
        logs.append("[중복] 정확한 중복 없음.")
        return

    out = root / "_duplicates"
    count = 0

    for h, paths in dup_map.items():
        keep = paths[0]
        logs.append(f"[중복] 그룹 (기준={keep.name})")

        for p in paths[1:]:
            moved = safe_move(p, out / h[:8])
            logs.append(f"  - 이동: {p.name} -> {moved}")
            count += 1

    summary["정확한 중복 이미지 정리 수"] = count
    logs.append(f"[중복] 총 {count}개 정리 완료.")


# ================= 유사 이미지 (pHash) =================

def phash(path: Path):
    try:
        with Image.open(path) as img:
            return imagehash.phash(img)
    except:
        return None


def find_similar_images(files: list[Path], threshold=5):
    hashes = {}
    for p in files:
        h = phash(p)
        if h is not None:
            hashes[p] = h

    items = list(hashes.items())
    used = set()
    groups = []

    for i in range(len(items)):
        p1, h1 = items[i]
        if p1 in used:
            continue

        group = [p1]
        for j in range(i + 1, len(items)):
            p2, h2 = items[j]
            if p2 in used:
                continue

            if h1 - h2 <= threshold:  # 유사도 판단
                group.append(p2)
                used.add(p2)

        if len(group) > 1:
            groups.append(group)
            used.update(group)

    return groups


def _handle_similar(files, root: Path, logs, summary):
    groups = find_similar_images(files, threshold=5)
    if not groups:
        logs.append("[유사] 유사 이미지 없음.")
        return

    out = root / "_similar"
    count = 0

    for idx, group in enumerate(groups, start=1):
        gdir = out / f"group_{idx}"
        logs.append(f"[유사] 그룹 {idx}:")

        keep = group[0]
        logs.append(f"  - 기준 이미지: {keep.name}")

        for p in group[1:]:
            moved = safe_move(p, gdir)
            logs.append(f"    이동: {p.name} -> {moved}")
            count += 1

    summary["유사 이미지 정리 수"] = count
    logs.append(f"[유사] 총 {count}개 정리 완료.")


# ================= 해상도 기준 정리 =================

def _handle_resolution(files, root: Path, logs, summary):
    out = root / "_by_resolution"
    count = 0

    for p in files:
        res = get_resolution(p)
        if not res:
            continue
        w, h = res
        moved = safe_move(p, out / f"{w}x{h}")
        logs.append(f"[해상도] {p.name} -> {moved}")
        count += 1

    summary["해상도 기준 정리 수"] = count
    logs.append(f"[해상도] 총 {count}개 정리 완료.")


# ================= 확장자 기준 정리 =================

def _handle_ext(files, root: Path, logs, summary):
    out = root / "_by_ext"
    count = 0

    for p in files:
        ext = get_extension(p) or "unknown"
        moved = safe_move(p, out / ext)
        logs.append(f"[확장자] {p.name} -> {moved}")
        count += 1

    summary["확장자 기준 정리 수"] = count
    logs.append(f"[확장자] 총 {count}개 정리 완료.")


# ================= 날짜 기준 정리 =================

def _handle_date(files, root: Path, logs, summary):
    out = root / "_by_date"
    count = 0

    for p in files:
        d = get_file_date(p)
        moved = safe_move(p, out / str(d))
        logs.append(f"[날짜] {p.name} -> {moved}")
        count += 1

    summary["날짜 기준 정리 수"] = count
    logs.append(f"[날짜] 총 {count}개 정리 완료.")


# ================= 메인 정리 함수 =================

def organize_images(
    root: Path,
    *,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    sort_ext=False,
    sort_date=False,
    auto=False,
):
    files = iter_image_files(root)

    logs = []
    summary = {"전체 이미지 수": len(files)}

    logs.append(f"[INFO] 총 {len(files)}개의 이미지 발견.")

    # auto 옵션 → 모든 기능 실행
    if auto:
        move_duplicates = move_similar = sort_resolution = sort_ext = sort_date = True
        logs.append("[INFO] 자동 정리 모드 활성화")

    if move_duplicates:
        _handle_duplicates(files, root, logs, summary)

    if move_similar:
        _handle_similar(files, root, logs, summary)

    if sort_resolution:
        _handle_resolution(files, root, logs, summary)

    if sort_ext:
        _handle_ext(files, root, logs, summary)

    if sort_date:
        _handle_date(files, root, logs, summary)

    return summary, logs
