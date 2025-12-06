from pathlib import Path
import shutil

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def safe_copy(src: Path, dst_dir: Path):
    """
    파일을 이동하는 대신 '복사'하는 함수.
    같은 파일명이 있으면 _copy를 붙여서 충돌 방지.
    """
    ensure_dir(dst_dir)
    target = dst_dir / src.name

    # 이름 충돌 시 자동으로 이름 변경
    if target.exists():
        target = dst_dir / f"{src.stem}_copy{src.suffix}"

    shutil.copy2(src, target)  # ← copy2: 메타데이터까지 복사
    return target
