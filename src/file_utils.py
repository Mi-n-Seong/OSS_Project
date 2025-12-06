from pathlib import Path
import shutil

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def safe_move(src: Path, dst_dir: Path):
    """같은 이름이 있으면 _copy 붙여서 이동"""
    ensure_dir(dst_dir)
    target = dst_dir / src.name
    if target.exists():
        target = dst_dir / f"{src.stem}_copy{src.suffix}"
    shutil.move(str(src), str(target))
    return target
