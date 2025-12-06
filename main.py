from pathlib import Path
from src.img_organizer import iter_image_files, find_duplicates


def main():
    # 사용자에게 이미지 폴더 경로 입력 받기
    root_str = input("정리할 이미지 폴더 경로를 입력하세요: ")
    root = Path(root_str)

    if not root.exists():
        print("[ERROR] 경로가 존재하지 않습니다.")
        return

    print("[INFO] 이미지 스캔 중...")
    files = iter_image_files(root)
    print(f"[INFO] 이미지 파일 {len(files)}개 발견\n")

    print("[INFO] 중복 검사 중...")
    duplicates = find_duplicates(files)

    if not duplicates:
        print("[INFO] 중복 이미지 없음")
        return

    print(f"[INFO] 중복 그룹 {len(duplicates)}개 발견!\n")

    # 중복 그룹 출력
    for i, (h, paths) in enumerate(duplicates.items(), start=1):
        print(f"[Group {i}] 해시 = {h}")
        for p in paths:
            print(" -", p)
        print()


if __name__ == "__main__":
    main()
