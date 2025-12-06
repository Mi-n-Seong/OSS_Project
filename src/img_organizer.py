from pathlib import Path
import hashlib
from PIL import Image, ExifTags
import imagehash

from .file_utils import move_files_to_group


SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


# ------------------------------------------------------
#  이미지 파일 전체 수집
# ------------------------------------------------------
def iter_image_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_FORMATS]


# ------------------------------------------------------
#  1) 완전 중복 (SHA-256)
# ------------------------------------------------------
def find_exact_duplicates(files):
    """
    동일 파일(바이트 단위) SHA256 해시 비교
    """
    hash_dict = {}

    for f in files:
        try:
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            hash_dict.setdefault(h, []).append(f)
        except:
            continue

    # 2개 이상일 때만 중복
    return {h: paths for h, paths in hash_dict.items() if len(paths) > 1}


def move_exact_duplicates(duplicates: dict, dest_root: Path):
    """
    중복 이미지들을 그룹별로 이동
    """
    group_num = 1
    for _, files in duplicates.items():
        group_folder = dest_root / f"group_{group_num}"
        move_files_to_group(group_folder, files)
        group_num += 1


# ------------------------------------------------------
#  2) 유사 이미지 (Perceptual Hash - pHash)
# ------------------------------------------------------
def find_similar_images(files, threshold=5):
    """
    perceptual hash(pHash) 기반 유사 이미지 탐지
    threshold 값 이하이면 사실상 같은 이미지로 판단
    """
    phashes = []

    for f in files:
        try:
            ph = imagehash.phash(Image.open(f))
            phashes.append((f, ph))
        except:
            continue

    groups = []
    visited = set()

    for i in range(len(phashes)):
        if i in visited:
            continue

        base_file, base_hash = phashes[i]
        group = [base_file]
        visited.add(i)

        for j in range(i + 1, len(phashes)):
            if j in visited:
                continue

            f, h = phashes[j]
            if base_hash - h <= threshold:
                group.append(f)
                visited.add(j)

        if len(group) > 1:
            groups.append(group)

    return groups


def move_similar_images(groups, dest_root: Path):
    """
    유사 이미지 그룹 이동
    """
    for i, group in enumerate(groups, start=1):
        group_folder = dest_root / f"group_{i}"
        move_files_to_group(group_folder, group)


# ------------------------------------------------------
#  3) 정리 기능 (해상도 / 확장자 / 날짜)
# ------------------------------------------------------
def get_exif_date(path: Path):
    try:
        img = Image.open(path)
        exif = img._getexif()

        if not exif:
            return None

        for k, v in exif.items():
            if ExifTags.TAGS.get(k) == "DateTimeOriginal":
                # YYYY:MM:DD → YYYY-MM-DD
                return v.split()[0].replace(":", "-")

        return None
    except:
        return None


def sort_by_resolution(files, dest_root: Path):
    """
    해상도 낮음 / 보통 / 높음 으로 자동 분류
    """
    for f in files:
        try:
            img = Image.open(f)
            w, h = img.size

            if w < 640:
                folder = dest_root / "small"
            elif w < 1920:
                folder = dest_root / "medium"
            else:
                folder = dest_root / "large"

            move_files_to_group(folder, [f])
        except:
            continue


def sort_by_extension(files, dest_root: Path):
    """
    확장자별 정리
    """
    for f in files:
        ext = f.suffix.lower().replace(".", "")
        folder = dest_root / ext
        move_files_to_group(folder, [f])


def sort_by_date(files, dest_root: Path):
    """
    EXIF 기준 날짜별 정리
    """
    for f in files:
        date = get_exif_date(f)

        if date is None:
            folder = dest_root / "unknown"
        else:
            folder = dest_root / date

        move_files_to_group(folder, [f])
