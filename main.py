
여기서 **라이브러리 이름이랑 GitHub 링크를 한 줄씩 더 적어주면 카피 문제 완전히 회피 가능**.

---

## 6. 최소 동작하는 코드 뼈대 (MVP용)

이건 **“정말로 돌아가는 기본 버전”** 뼈대야.  
파일 스캔 + 중복 탐지 + 이동 + 리포트까지 한 파일 안에 다 넣은 버전.

`main.py`:

```python
import argparse
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image  # requirements.txt에 Pillow 추가할 것


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def iter_image_files(root: Path) -> List[Path]:
    files = []
    for path, dirs, filenames in os.walk(root):
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext in IMAGE_EXTS:
                files.append(Path(path) / name)
    return files


def get_file_hash(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_image_size(path: Path) -> Tuple[int, int]:
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except Exception:
        return (0, 0)


def find_duplicates(files: List[Path]) -> Dict[str, List[Path]]:
    """해시값 -> 파일 리스트"""
    hash_map: Dict[str, List[Path]] = {}
    for p in files:
        file_hash = get_file_hash(p)
        hash_map.setdefault(file_hash, []).append(p)
    # 2개 이상인 것만 중복 그룹으로 사용
    dupes = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return dupes


def write_report(duplicates: Dict[str, List[Path]], output_path: Path):
    with output_path.open("w", encoding="utf-8") as f:
        if not duplicates:
            f.write("No duplicates found.\n")
            return

        for i, (h, paths) in enumerate(duplicates.items(), start=1):
            f.write(f"[Group {i}] {len(paths)} duplicate files (hash={h})\n")
            for p in paths:
                w, h_ = get_image_size(p)
                size = p.stat().st_size
                f.write(f" - {p}  ({w}x{h_}, {size} bytes)\n")
            f.write("\n")


def move_duplicates(duplicates: Dict[str, List[Path]], target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    for hash_value, paths in duplicates.items():
        # 첫 번째 파일은 원본으로 남기고, 나머지를 이동
        originals = paths[0]
        for p in paths[1:]:
            new_path = target_dir / p.name
            # 이름이 겹치면 뒤에 숫자 붙이기
            counter = 1
            while new_path.exists():
                new_path = target_dir / f"{p.stem}_{counter}{p.suffix}"
                counter += 1
            p.rename(new_path)


def main():
    parser = argparse.ArgumentParser(
        description="이미지 중복 탐지 및 정리 도구"
    )
    parser.add_argument("root", help="이미지를 스캔할 기준 폴더 경로")
    parser.add_argument(
        "--report",
        help="중복 결과를 저장할 리포트 파일 경로 (예: report.txt)",
        default=None,
    )
    parser.add_argument(
        "--move-duplicates",
        help="중복 파일을 이동시킬 폴더 경로 (예: duplicates)",
        default=None,
    )

    args = parser.parse_args()
    root = Path(args.root)

    if not root.exists():
        print(f"[ERROR] 경로가 존재하지 않습니다: {root}")
        return

    print(f"[INFO] 스캔 시작: {root}")
    files = iter_image_files(root)
    print(f"[INFO] 이미지 파일 {len(files)}개 발견")

    duplicates = find_duplicates(files)

    if not duplicates:
        print("[INFO] 중복 이미지가 없습니다.")
    else:
        print(f"[INFO] 중복 그룹 {len(duplicates)}개 발견")
        for i, (h, paths) in enumerate(duplicates.items(), start=1):
            print(f"[Group {i}] {len(paths)} files")
            for p in paths:
                print(f" - {p}")
        print()

    # 리포트 파일 저장
    if args.report:
        report_path = Path(args.report)
        write_report(duplicates, report_path)
        print(f"[INFO] 리포트를 {report_path} 에 저장했습니다.")

    # 중복 파일 이동
    if args.move_duplicates and duplicates:
        target_dir = Path(args.move_duplicates)
        move_duplicates(duplicates, target_dir)
        print(f"[INFO] 중복 파일을 {target_dir} 로 이동했습니다.")


if __name__ == "__main__":
    main()
