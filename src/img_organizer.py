from pathlib import Path
import hashlib
import imagehash
from PIL import Image

from src.file_utils import safe_move
from src.metadata import get_resolution, get_file_date

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


# ============= 이미지 스캔 =============
def iter_image_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXT]


# ============= SHA256 중복 검사 =============
def sha256(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_exact_duplicates(files):
    mapping = {}
    for p in files:
        h = sha256(p)
        mapping.setdefault(h, []).append(p)
    return {h: g for h, g in mapping.items() if len(g) > 1}


def _handle_duplicates(files, root, logs, summary):
    dup = find_exact_duplicates(files)
    if not dup:
        logs.append("[중복] 중복된 이미지가 발견되지 않았습니다.")
        return

    out = root / "_duplicates"
    count = 0

    for h, group in dup.items():
        base = group[0]
        key = h[:8]

        logs.append(f"\n[중복 그룹 {key}] 기준 이미지: {base.name}")

        for p in group[1:]:
            moved = safe_move(p, out / key)
            logs.append(
                f" - '{p.name}' 파일은 '{base.name}' 와(과) 완전히 동일하여 "
                f"중복 폴더('{key}')로 이동되었습니다. → {moved}"
            )
            count += 1

    summary["정확 중복 정리"] = count
    logs.append(f"[중복] 총 {count}개의 중복 이미지를 정리했습니다.")


# ============= 유사 이미지 검사 =============
def phash(path: Path):
    try:
        with Image.open(path) as img:
            return imagehash.phash(img)
    except:
        return None


def find_similar_images(files, threshold=5):
    hashed = {}
    for p in files:
        h = phash(p)
        if h is not None:
            hashed[p] = h

    items = list(hashed.items())
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

            if h1 - h2 <= threshold:
                group.append(p2)
                used.add(p2)

        if len(group) > 1:
            groups.append(group)
            used.update(group)

    return groups


def _handle_similar(files, root, logs, summary):
    groups = find_similar_images(files)
    if not groups:
        logs.append("[유사] 비슷한 이미지 없음.")
        return

    out = root / "_similar"
    count = 0
    real_group_index = 1

    for idx, group in enumerate(groups, start=1):

        # 유사 이미지가 1개뿐이면 그룹 만들지 않음
        if len(group) < 2:
            continue

        base = group[0]
        gdir = out / f"group_{real_group_index}"

        logs.append(f"\n[유사] 그룹 {real_group_index} 생성 (기준 이미지: {base.name})")

        # 기준 이미지도 이동시키기
        moved_base = safe_move(base, gdir)
        logs.append(f" - 기준 이미지 '{base.name}' 이동됨 → {moved_base}")

        for p in group[1:]:
            moved = safe_move(p, gdir)
            logs.append(
                f" - '{p.name}' 파일은 '{base.name}' 와 유사하여 "
                f"그룹 {real_group_index}로 이동됨 → {moved}"
            )
            count += 1

        real_group_index += 1

    summary["유사 이미지 정리 수"] = count
    logs.append(f"[유사] 총 {count}개의 유사 이미지를 정리했습니다.")



# ============= 해상도 정리 =============
def _handle_resolution(files, root, logs, summary):
    out = root / "_by_resolution"
    count = 0

    for p in files:
        res = get_resolution(p)
        if not res:
            continue
        w, h = res
        moved = safe_move(p, out / f"{w}x{h}")
        logs.append(
            f"[해상도] '{p.name}' 파일은 해상도 {w}x{h}로 확인되어 "
            f"'{w}x{h}' 폴더로 이동되었습니다. → {moved}"
        )
        count += 1

    summary["해상도 정리"] = count


# ============= 날짜 정리 =============
def _handle_date(files, root, logs, summary):
    out = root / "_by_date"
    count = 0

    for p in files:
        date = get_file_date(p)
        moved = safe_move(p, out / date)
        logs.append(
            f"[날짜] '{p.name}' 파일은 날짜 '{date}' 기준으로 "
            f"'{date}' 폴더로 이동되었습니다. → {moved}"
        )
        count += 1

    summary["날짜 정리"] = count


# ============= 메인 정리 함수 =============
def organize_images(
    root: Path,
    *,
    move_duplicates=False,
    move_similar=False,
    sort_resolution=False,
    sort_date=False,
    auto=False,
):
    files = iter_image_files(root)
    logs = []
    summary = {"총 이미지 수": len(files)}

    logs.append(f"[INFO] 총 {len(files)}개의 이미지가 발견되었습니다.")

    if auto:
        logs.append("[INFO] 자동 정리(AUTO) 모드 활성화")
        move_duplicates = move_similar = sort_resolution = sort_date = True

    if move_duplicates:
        _handle_duplicates(files, root, logs, summary)
    if move_similar:
        _handle_similar(files, root, logs, summary)
    if sort_resolution:
        _handle_resolution(files, root, logs, summary)
    if sort_date:
        _handle_date(files, root, logs, summary)

    return summary, logs
