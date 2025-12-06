import argparse
from pathlib import Path

from src.img_organizer import (
    iter_image_files,

    # 중복 이미지 처리
    find_exact_duplicates,
    move_exact_duplicates,

    # 유사 이미지 처리
    find_similar_images,
    move_similar_images,

    # 정리 기능
    sort_by_resolution,
    sort_by_extension,
    sort_by_date
)


def main():
    parser = argparse.ArgumentParser(description="이미지 정리 프로그램")
    parser.add_argument("root", help="이미지 폴더 경로")

    # 기능 선택 옵션들
    parser.add_argument("--move-duplicates", action="store_true",
                        help="완전 중복 이미지 자동 정리")

    parser.add_argument("--move-similar", action="store_true",
                        help="유사 이미지 자동 정리")

    parser.add_argument("--sort-resolution", action="store_true",
                        help="해상도 기준 자동 정리")

    parser.add_argument("--sort-ext", action="store_true",
                        help="확장자 기준 자동 정리")

    parser.add_argument("--sort-date", action="store_true",
                        help="EXIF 날짜 기준 자동 정리")

    args = parser.parse_args()
    root = Path(args.root)

    if not root.exists():
        print("[ERROR] 경로가 존재하지 않습니다:", root)
        return

    print("[INFO] 이미지 스캔 중...")
    files = iter_image_files(root)
    print(f"[INFO] 총 {len(files)}개의 이미지 발견\n")

    # ===============================
    # 1) 완전 중복 이미지 이동
    # ===============================
    if args.move_duplicates:
        print("[INFO] SHA256 기반 중복 이미지 검사 중...")
        exact = find_exact_duplicates(files)
        move_exact_duplicates(exact, root / "duplicates")
        print("[INFO] 중복 이미지 정리 완료.\n")

    # ===============================
    # 2) 유사 이미지 이동
    # ===============================
    if args.move_similar:
        print("[INFO] pHash 기반 유사 이미지 검사 중...")
        similar = find_similar_images(files)
        move_similar_images(similar, root / "similar")
        print("[INFO] 유사 이미지 정리 완료.\n")

    # ===============================
    # 3) 정리 기능 (해상도 / 확장자 / 날짜)
    # ===============================
    if args.sort_resolution:
        print("[INFO] 해상도 기준 정리 중...")
        sort_by_resolution(files, root / "sorted_resolution")

    if args.sort_ext:
        print("[INFO] 확장자 기준 정리 중...")
        sort_by_extension(files, root / "sorted_ext")

    if args.sort_date:
        print("[INFO] EXIF 날짜 기준 정리 중...")
        sort_by_date(files, root / "sorted_date")

    print("\n[INFO] 작업 완료!")


if __name__ == "__main__":
    main()
