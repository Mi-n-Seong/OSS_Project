import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from src.img_organizer import organize_images


class ImageOrganizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✨ 이미지 정리 프로그램")
        self.root.geometry("720x600")
        self.root.configure(bg="#f3f4f6")

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TButton",
            font=("Pretendard", 11),
            padding=6,
            background="#4f46e5",
            foreground="white",
        )
        style.map(
            "TButton",
            background=[("active", "#4338ca")]
        )

        # ===== 상단 제목 =====
        title = tk.Label(
            self.root,
            text="📁 이미지 정리 프로그램",
            bg="#f3f4f6",
            fg="#111827",
            font=("Pretendard", 22, "bold"),
        )
        title.pack(pady=15)

        # ===== 폴더 선택 박스 =====
        box = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        box.pack(pady=10, padx=20, fill="x")

        tk.Label(box, text="정리할 폴더 선택", bg="white", fg="#374151", font=("Pretendard", 12)).pack(anchor="w", pady=4, padx=10)

        row = tk.Frame(box, bg="white")
        row.pack(fill="x", padx=10, pady=8)

        self.folder = tk.StringVar()
        tk.Entry(row, textvariable=self.folder, width=50, font=("Pretendard", 11)).pack(side="left", padx=5)
        ttk.Button(row, text="찾기", command=self.select_folder).pack(side="left", padx=5)

        # ===== 옵션 영역 카드 =====
        card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        card.pack(pady=10, padx=20, fill="x")

        tk.Label(card, text="정리 옵션", bg="white", fg="#111827", font=("Pretendard", 13, "bold")).pack(anchor="w", padx=10, pady=8)

        opts = tk.Frame(card, bg="white")
        opts.pack(anchor="w", padx=20)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_date = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        tk.Checkbutton(opts, text="정확한 중복 이미지 정리", variable=self.opt_dup, bg="white").pack(anchor="w")
        tk.Checkbutton(opts, text="유사 이미지 정리", variable=self.opt_sim, bg="white").pack(anchor="w")
        tk.Checkbutton(opts, text="해상도 기준 정리", variable=self.opt_res, bg="white").pack(anchor="w")
        tk.Checkbutton(opts, text="날짜 기준 정리", variable=self.opt_date, bg="white").pack(anchor="w")
        tk.Checkbutton(opts, text="자동 정리 (AUTO)", variable=self.opt_auto, bg="white").pack(anchor="w")

        # ===== 실행 버튼 =====
        ttk.Button(self.root, text="정리 실행", command=self.run).pack(pady=15)

        # ===== 로그 박스 =====
        log_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        log_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(log_frame, text="실행 로그", bg="white", fg="#111827", font=("Pretendard", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        self.log = tk.Text(log_frame, height=20, wrap="word")
        self.log.pack(fill="both", expand=True, padx=10, pady=5)

        self.root.mainloop()

    def log_write(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)
            self.log_write(f"[INFO] 선택된 폴더: {folder}")

    def run(self):
        if not self.folder.get():
            self.log_write("[ERROR] 폴더를 먼저 선택하세요.")
            return

        root = Path(self.folder.get())

        summary, logs = organize_images(
            root,
            move_duplicates=self.opt_dup.get(),
            move_similar=self.opt_sim.get(),
            sort_resolution=self.opt_res.get(),
            sort_date=self.opt_date.get(),
            auto=self.opt_auto.get(),
        )

        self.log_write("\n===== 처리 요약 =====")
        for k, v in summary.items():
            self.log_write(f"{k}: {v}")

        self.log_write("\n===== 상세 로그 =====")
        for line in logs:
            self.log_write(line)


if __name__ == "__main__":
    ImageOrganizerGUI()
