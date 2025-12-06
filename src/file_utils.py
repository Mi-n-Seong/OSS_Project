from pathlib import Path
import shutil


def ensure_dir(path: Path):
    """폴더가 없으면 생성"""
    path.mkdir(parents=True, exist_ok=True)


def move_files_to_group(group_folder: Path, files):
    """
    파일들을 지정한 그룹 폴더로 이동.
    이름 충돌 시 자동으로 숫자를 붙인다.
    """
    ensure_dir(group_folder)

    for f in files:
        dest = group_folder / f.name

        # 이름 중복 시 file_1, file_2 형태로 저장
        if dest.exists():
            base = f.stem
            ext = f.suffix
            i = 1
            while True:
                new_dest = group_folder / f"{base}_{i}{ext}"
                if not new_dest.exists():
                    dest = new_dest
                    break
                i += 1

        shutil.move(str(f), str(dest))
