import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

from src.img_organizer import organize_images


class ImageOrganizerGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("이미지 정리 프로그램")
        self.root.geometry("700x520")

        self.folder_path = tk.StringVar()

        self.build_ui()

    # ---------------- UI 구성 ---------------- #
    def build_ui(self):
        # 폴더 선택
        tk.Label(self.root, text="정리할 폴더:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.folder_path, width=60).pack()
        tk.Button(self.root, text="폴더 선택", command=self.select_folder).pack(pady=5)

        # 옵션 체크박스
        self.opt_duplicates = tk.BooleanVar()
        self.opt_similar = tk.BooleanVar()
        self.opt_resolution = tk.BooleanVar()
        self.opt_ext = tk.BooleanVar()
        self.opt_date = tk.BooleanVar()

        tk.Label(self.root, text="실행할 기능 선택:").pack(pady=5)
        tk.Checkbutton(self.root, text="정확한 중복 이미지 정리", variable=self.opt_duplicates).pack(anchor="w", padx=50)
        tk.Checkbutton(self.root, text="유사 이미지 정리 (pHash)", variable=self.opt_similar).pack(anchor="w", padx=50)
        tk.Checkbutton(self.root, text="해상도 기준 정리", variable=self.opt_resolution).pack(anchor="w", padx=50)
        tk.Checkbutton(self.root, text="확장자 기준 정리", variable=self.opt_ext).pack(anchor="w", padx=50)
        tk.Checkbutton(self.root, text="촬영/수정 날짜 기준 정리", variable=self.opt_date).pack(anchor="w", padx=50)

        # 실행 버튼
        tk.Button(self.root, text="선택한 옵션으로 정리 실행", command=self.run_selected).pack(pady=10)
        tk.Button(self.root, text="자동 정리 (모든 기능 실행)", command=self.run_auto).pack(pady=5)

        # 로그 출력
        tk.Label(self.root, text="실행 로그:").pack(pady=5)
        self.log_box = scrolledtext.ScrolledText(self.root, width=80, height=15)
        self.log_box.pack()

    # ---------------- 동작 ---------------- #

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def run_selected(self):
        folder = Path(self.folder_path.get())
        if not folder.exists():
            messagebox.showerror("오류", "폴더를 선택하세요!")
            return

        summary, logs = organize_images(
            folder,
            move_duplicates=self.opt_duplicates.get(),
            move_similar=self.opt_similar.get(),
            sort_resolution=self.opt_resolution.get(),
            sort_ext=self.opt_ext.get(),
            sort_date=self.opt_date.get(),
            auto=False
        )

        self.show_logs(summary, logs)

    def run_auto(self):
        folder = Path(self.folder_path.get())
        if not folder.exists():
            messagebox.showerror("오류", "폴더를 선택하세요!")
            return

        summary, logs = organize_images(folder, auto=True)
        self.show_logs(summary, logs)

    def show_logs(self, summary, logs):
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert(tk.END, "=== 실행 결과 요약 ===\n")
        for k, v in summary.items():
            self.log_box.insert(tk.END, f"{k}: {v}\n")

        self.log_box.insert(tk.END, "\n=== 상세 로그 ===\n")
        for line in logs:
            self.log_box.insert(tk.END, line + "\n")

    # ---------------- 실행 ---------------- #

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    ImageOrganizerGUI().start()
