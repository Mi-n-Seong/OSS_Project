import hashlib
from pathlib import Path
from PIL import Image
import imagehash


def iter_image_files(root: Path):
    """root 폴더 안의 모든 이미지 파일을 재귀적으로 탐색"""
    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
    return [p for p in root.rglob("*") if p.suffix.lower() in exts]


def find_exact_duplicates(files):
    """SHA256 이용 완전 동일 이미지 탐지"""
    hash_dict = {}
    for f in files:
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        hash_dict.setdefault(h, []).append(f)

    # 2개 이상 모인 해시만 반환
    return {h: paths for h, paths in hash_dict.items() if len(paths) > 1}


def find_similar_images(files, threshold=5):
    """Perceptual Hash 사용 유사 이미지 탐지"""
    phashes = []
    for f in files:
        try:
            ph = imagehash.phash(Image.open(f))
            phashes.append((f, ph))
        except Exception:
            continue

    groups = []
    visited = set()

    for i in range(len(phashes)):
        if i in visited:
            continue
        base_f, base_h = phashes[i]
        group = [base_f]
        visited.add(i)

        for j in range(i + 1, len(phashes)):
            if j in visited:
                continue
            f, h = phashes[j]
            if base_h - h <= threshold:
                group.append(f)
                visited.add(j)

        if len(group) > 1:
            groups.append(group)

    return groups
