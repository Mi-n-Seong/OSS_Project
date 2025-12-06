from pathlib import Path
import argparse
from src.img_organizer import (
    iter_image_files,
    find_exact_duplicates,
    find_similar_images
)

def main():
    parser = argparse.ArgumentParser(description="이미지 중복 검사 도구")
    parser.add_argument("root", help="정리할 이미지 폴더 경로")
    args = parser.parse_args()

    root = Path(args.root)

    if not root.exists():
        print("[ERROR] 경로가 존재하지 않습니다:", root)
        return

    print("[INFO] 이미지 스캔 중...")
    files = iter_image_files(root)
    print(f"[INFO] 이미지 파일 {len(files)}개 발견\n")

    # 완전 중복 (SHA256)
    print("[INFO] SHA256 기반 완전 중복 검사 중...")
    exact = find_exact_duplicates(files)

    if exact:
        print(f"\n[INFO] 완전 중복 그룹 {len(exact)}개 발견!")
        for i, (h, paths) in enumerate(exact.items(), start=1):
            print(f"[Exact Group {i}] 해시 = {h}")
            for p in paths:
                print(" -", p)
            print()
    else:
        print("[INFO] 완전 중복 없음.\n")

    # 유사 이미지 (phash)
    print("[INFO] perceptual hash 기반 유사 이미지 검사 중...")
    similar_groups = find_similar_images(files, threshold=5)

    if similar_groups:
        print(f"\n[INFO] 유사 이미지 그룹 {len(similar_groups)}개 발견!")
        for i, group in enumerate(similar_groups, start=1):
            print(f"[Similar Group {i}]")
            for p in group:
                print(" -", p)
            print()
    else:
        print("[INFO] 유사 이미지 없음.\n")


if __name__ == "__main__":
    main()