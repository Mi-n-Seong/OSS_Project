# src/file_utils.py
from pathlib import Path
import shutil
from send2trash import send2trash


def safe_copy(src: Path, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / src.name
    shutil.copy2(src, dst)
    return dst


def safe_delete(path: Path):
    """파일을 휴지통으로 이동"""
    try:
        send2trash(str(path))
        return True
    except Exception as e:
        print(f"삭제 실패: {path} → {e}")
        return False
