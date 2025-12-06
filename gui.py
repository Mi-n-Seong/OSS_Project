import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path

from src.img_organizer import organize_images


class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📂 이미지 자동 정리 프로그램")
        self.root.geometry("980x600")
        self.root.configure(bg="#f0f2f5")

        self.selected_folder = None
        self.image_list = []
        self.thumbnail_cache = {}

        # ========== 상단 프레임 ==========
        top_frame = tk.Frame(root, bg="#ffffff", height=80)
        top_frame.pack(fill="x")

        self.lbl_title = tk.Label(
            top_frame,
            text="이미지 정리 도구",
            font=("Malgun Gothic", 20, "bold"),
            bg="#ffffff"
        )
        self.lbl_title.pack(pady=10)

        # ========== 폴더 선택 버튼 ==========
        btn_frame = tk.Frame(root, bg="#f0f2f5")
        btn_frame.pack(pady=10)

        self.btn_select = tk.Button(
            btn_frame,
            text="📁 정리할 폴더 선택",
            font=("Malgun Gothic", 12),
            command=self.select_folder,
            bg="#4a90e2", fg="white", width=20
        )
        self.btn_select.pack()

        # ========== 본문 영역 (좌: 이미지 리스트 / 우: 미리보기) ==========
        main_frame = tk.Frame(root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 좌측 이미지 리스트
        left_frame = tk.Frame(main_frame, bg="#ffffff", width=260)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)

        lbl_list = tk.Label(left_frame, text="이미지 목록", font=("Malgun Gothic", 12, "bold"), bg="#ffffff")
        lbl_list.pack(pady=5)

        self.listbox = tk.Listbox(left_frame, font=("Malgun Gothic", 10))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)

        # 우측 이미지 미리보기
        preview_frame = tk.Frame(main_frame, bg="#ffffff")
        preview_frame.pack(side="right", fill="both", expand=True)

        lbl_preview = tk.Label(preview_frame, text="이미지 미리보기", font=("Malgun Gothic", 12, "bold"), bg="#ffffff")
        lbl_preview.pack(pady=5)

        self.canvas = tk.Canvas(preview_frame, bg="#ffffff")
        self.canvas.pack(fill="both", expand=True)

        # 하단 진행 프레임
        bottom_frame = tk.Frame(root, bg="#f0f2f5")
        bottom_frame.pack(fill="x")

        self.progress = ttk.Progressbar(bottom_frame, length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.btn_start = tk.Button(
            bottom_frame,
            text="🚀 자동 정리 시작",
            font=("Malgun Gothic", 13),
            bg="#27ae60", fg="white",
            command=self.run_organize
        )
        self.btn_start.pack(pady=5)

    # ========== 폴더 선택 ==========
    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.selected_folder = Path(folder)
        self.load_images()

    # ========== 리스트 로딩 ==========
    def load_images(self):
        self.image_list.clear()
        self.listbox.delete(0, tk.END)
        self.thumbnail_cache.clear()

        exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

        for p in self.selected_folder.rglob("*"):
            if p.suffix.lower() in exts:
                self.image_list.append(p)
                self.listbox.insert(tk.END, p.name)

    # ========== 미리보기 ==========
    def show_preview(self, event):
        if not self.listbox.curselection():
            return

        index = self.listbox.curselection()[0]
        img_path = self.image_list[index]

        if img_path in self.thumbnail_cache:
            img = self.thumbnail_cache[img_path]
        else:
            try:
                img = Image.open(img_path)
                img.thumbnail((600, 600))
                img = ImageTk.PhotoImage(img)
                self.thumbnail_cache[img_path] = img
            except:
                return

        self.canvas.delete("all")
        self.canvas.create_image(300, 300, image=img)
        self.canvas.image = img

    # ========== 자동 정리 실행 ==========
    def run_organize(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        total = len(self.image_list)
        if total == 0:
            messagebox.showinfo("안내", "이미지가 없습니다.")
            return

        self.progress["value"] = 0
        self.progress["maximum"] = total

        summary, logs = organize_images(
            self.selected_folder,
            move_duplicates=True,
            move_similar=True,
            sort_resolution=True,
            sort_ext=False,
            sort_date=False,
            copy_mode=True
        )

        # 진행률 갱신
        for i in range(total):
            self.progress["value"] += 1
            self.root.update()
        
        messagebox.showinfo("완료", "이미지 정리 완료!")


# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
