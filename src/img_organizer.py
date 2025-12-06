import os
import hashlib
from pathlib import Path

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


def find_duplicates(files):
    """
    파일 리스트를 받아 해시값 -> 파일 리스트로 매핑.
    동일한 해시값이 2개 이상이면 중복 그룹으로 판단.
    """
    hash_map = {}

    for p in files:
        h = get_file_hash(p)
        hash_map.setdefault(h, []).append(p)

    # 중복 그룹만 따로 반환
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return duplicates
