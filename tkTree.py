import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ExifTags
import os

# -------------------- 全局变量 --------------------
filemap = {}        # Treeview item -> 文件路径
filelist = []       # 文件顺序
thumbnails = {}     # 缩略图缓存
pending_files = []  # 待生成缩略图队列
pending_exif = []   # 待解析 EXIF 队列

# 预览窗口大小
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600

# -------------------- EXIF 处理 --------------------
def get_exif_info(filepath):
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()
        if not exif_data:
            return ["N/A"] * 5

        exif = {}
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif[tag] = value

        camera = exif.get("Model", "N/A")
        lens = exif.get("LensModel", "N/A")
        focal_length = exif.get("FocalLength", "N/A")
        aperture = exif.get("FNumber", "N/A")
        datetime = exif.get("DateTimeOriginal", exif.get("DateTime", "N/A"))

        if isinstance(focal_length, tuple):
            focal_length = round(focal_length[0] / focal_length[1], 1)
        if isinstance(aperture, tuple):
            aperture = round(aperture[0] / aperture[1], 1)

        return [camera, lens, focal_length, aperture, datetime]
    except Exception:
        return ["N/A"] * 5

def process_exif(batch_size=5):
    for _ in range(min(batch_size, len(pending_exif))):
        item, file = pending_exif.pop(0)
        exif_vals = get_exif_info(file)
        tree.item(item, values=(os.path.basename(file), *exif_vals))
        progress["value"] += 1
    if pending_exif:
        root.after(50, process_exif)

# -------------------- 缩略图处理 --------------------
def create_thumbnail(filepath, size=(50, 50)):
    try:
        img = Image.open(filepath)
        img.thumbnail(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"缩略图生成失败: {e}")
        return None

def process_thumbnails(batch_size=5):
    for _ in range(min(batch_size, len(pending_files))):
        item, file = pending_files.pop(0)
        thumb = create_thumbnail(file, size=(50, 50))
        if thumb:
            thumbnails[file] = thumb
            tree.item(item, image=thumb)
            progress["value"] += 1
    if pending_files:
        root.after(50, process_thumbnails)

# -------------------- 添加文件/文件夹 --------------------
def add_files_from_list(files):
    for file in files:
        if file in filelist:
            continue
        filename = os.path.basename(file)
        item = tree.insert("", tk.END, text="", values=(filename, "N/A", "N/A", "N/A", "N/A", "N/A"))
        filemap[item] = file
        filelist.append(file)
        pending_files.append((item, file))
        pending_exif.append((item, file))
    progress["maximum"] = len(pending_files) + len(pending_exif)
    root.after(50, process_thumbnails)
    root.after(50, process_exif)

def add_files():
    files = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff")])
    if files:
        path_var.set(os.path.dirname(files[0]))
        add_files_from_list(files)

def add_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_var.set(folder)
        exts = (".jpg", ".jpeg", ".png", ".tiff")
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
        add_files_from_list(files)

# -------------------- 双击预览 --------------------
def on_double_click(event):
    item_id = tree.focus()
    if not item_id:
        return
    filepath = filemap.get(item_id)
    if not filepath:
        return

    top = tk.Toplevel(root)
    top.geometry(f"{PREVIEW_WIDTH}x{PREVIEW_HEIGHT}")
    lbl = tk.Label(top)
    lbl.pack(expand=True)
    top.title(os.path.basename(filepath))

    current_index = filelist.index(filepath)
    zoomed = False  # 双击放大状态

    def show_at_index(index):
        nonlocal current_index, zoomed
        if 0 <= index < len(filelist):
            current_index = index
            zoomed = False
            show_image(filelist[current_index], top, lbl, zoomed=False)

    def show_image(file, top_window, label, zoomed=False):
        try:
            img = Image.open(file)
            if not zoomed:
                img.thumbnail((PREVIEW_WIDTH, PREVIEW_HEIGHT))
            photo = ImageTk.PhotoImage(img, master=top_window)
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            print(f"显示图片失败: {e}")

    def on_wheel(event):
        delta = event.delta
        if delta < 0:
            show_at_index(current_index + 1)
        else:
            show_at_index(current_index - 1)

    def toggle_zoom(event):
        nonlocal zoomed
        zoomed = not zoomed
        show_image(filelist[current_index], top, lbl, zoomed=zoomed)

    top.bind("<MouseWheel>", on_wheel)
    lbl.bind("<Double-Button-1>", toggle_zoom)
    show_image(filepath, top, lbl, zoomed=False)
    top.focus_set()

# -------------------- 主窗口 --------------------
root = tk.Tk()
root.title("文件与EXIF信息列表")
root.geometry("1100x700")

style = ttk.Style()
style.configure("Treeview", rowheight=60)

# 顶部路径和按钮
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, pady=5, padx=5)

tk.Label(frame_top, text="Path:").pack(side=tk.LEFT, padx=5)
path_var = tk.StringVar()
entry_path = tk.Entry(frame_top, textvariable=path_var, width=60)
entry_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
btn_folder = tk.Button(frame_top, text="增加文件夹", command=add_folder)
btn_folder.pack(side=tk.LEFT, padx=5)
btn_file = tk.Button(frame_top, text="增加文件", command=add_files)
btn_file.pack(side=tk.LEFT, padx=5)

# Treeview
columns = ("filename", "camera", "lens", "focal", "aperture", "datetime")
tree = ttk.Treeview(root, columns=columns)
tree.column("#0", width=60, anchor="center")
tree.heading("#0", text="缩略图")
tree.heading("filename", text="文件名")
tree.heading("camera", text="相机")
tree.heading("lens", text="镜头")
tree.heading("focal", text="焦距(mm)")
tree.heading("aperture", text="光圈(F)")
tree.heading("datetime", text="拍摄时间")
tree.column("filename", width=180)
tree.column("camera", width=120)
tree.column("lens", width=200)
tree.column("focal", width=80, anchor="center")
tree.column("aperture", width=80, anchor="center")
tree.column("datetime", width=160)
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<Double-1>", on_double_click)

# 进度条放在 Treeview 下方，拉长宽度
progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.pack(fill=tk.X, pady=5, padx=5)

root.mainloop()
