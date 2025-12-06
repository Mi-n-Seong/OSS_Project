import os
import hashlib
from pathlib import Path

from PIL import Image
import imagehash   # perceptual hash

# 처리할 이미지 확장자 목록
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def iter_image_files(root: Path):
    """
    입력 폴더(root) 하위 모든 이미지 파일 경로를 리스트로 반환.
    """
    files = []
    for path, dirs, filenames in os.walk(root):
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext in IMAGE_EXTS:
                files.append(Path(path) / name)
    return files


# -------------------------------
# 1) 완전 중복 탐지 (SHA256)
# -------------------------------

def get_file_hash(path: Path, chunk_size: int = 8192):
    """
    이미지 파일의 SHA256 해시값 생성.
    """
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def find_exact_duplicates(files):
    """
    SHA256 기반 완전 중복 탐지
    """
    hash_map = {}

    for p in files:
        h = get_file_hash(p)
        hash_map.setdefault(h, []).append(p)

    exact = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return exact


# -------------------------------
# 2) 유사 이미지 탐지 (Perceptual Hash)
# -------------------------------

def get_phash(path: Path):
    """
    Perceptual hash 기반 이미지 유사도 계산
    """
    try:
        img = Image.open(path)
        return imagehash.phash(img)
    except Exception:
        return None


def hamming_distance(h1, h2):
    """해밍 거리 계산"""
    return abs(h1 - h2)


def find_similar_images(files, threshold=5):
    """
    perceptual hash 기반 유사 이미지 탐지.
    threshold = 허용 거리 (작을수록 엄격)
    """
    phash_map = {}
    for p in files:
        h = get_phash(p)
        if h is not None:
            phash_map[p] = h

    checked = set()
    groups = []

    paths = list(phash_map.keys())

    for i in range(len(paths)):
        base = paths[i]
        if base in checked:
            continue

        base_hash = phash_map[base]
        group = [base]

        for j in range(i + 1, len(paths)):
            comp = paths[j]
            if comp in checked:
                continue

            dist = hamming_distance(base_hash, phash_map[comp])
            if dist <= threshold:
                group.append(comp)
                checked.add(comp)

        if len(group) > 1:
            groups.append(group)

        checked.add(base)

    return groups
