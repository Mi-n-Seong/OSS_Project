from pathlib import Path
import shutil


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def safe_copy(src: Path, dst_dir: Path):
    """
    파일 복사.
    - 목적지에 파일이 이미 있으면 _copy, _copy2 ... 순서로 이름 자동 생성
    - PermissionError 방지
    """
    ensure_dir(dst_dir)

    base = src.stem
    ext = src.suffix

    target = dst_dir / f"{base}{ext}"

    counter = 1
    # 파일이 존재하는 동안 새로운 이름 찾기
    while target.exists():
        target = dst_dir / f"{base}_copy{counter}{ext}"
        counter += 1

    shutil.copy2(src, target)  # 메타데이터 포함 복사
    return target
