import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ExifTags
import os
import time

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
        datetime_val = exif.get("DateTimeOriginal", exif.get("DateTime", "N/A"))

        if isinstance(focal_length, tuple):
            focal_length = round(focal_length[0] / focal_length[1], 1)
        if isinstance(aperture, tuple):
            aperture = round(aperture[0] / aperture[1], 1)

        return [camera, lens, focal_length, aperture, datetime_val]
    except Exception:
        return ["N/A"] * 5

def process_exif(batch_size=5):
    for _ in range(min(batch_size, len(pending_exif))):
        item, file = pending_exif.pop(0)
        exif_vals = get_exif_info(file)
        tree.item(item, values=(os.path.basename(file),
                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(file))),
                                *exif_vals))
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
        ctime_val = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(file)))

        # 判断是否加载 EXIF
        if exif_var.get():
            camera = lens = focal = aperture = datetime_val = "N/A"
            item = tree.insert("", tk.END, text="", values=(filename, ctime_val, camera, lens, focal, aperture, datetime_val))
            filemap[item] = file
            filelist.append(file)
            pending_files.append((item, file))
            pending_exif.append((item, file))
        else:
            # EXIF 未勾选时，不加入 pending_exif
            item = tree.insert("", tk.END, text="", values=(filename, ctime_val, "N/A", "N/A", "N/A", "N/A", "N/A"))
            filemap[item] = file
            filelist.append(file)
            pending_files.append((item, file))

    progress["maximum"] = len(pending_files) + len(pending_exif)
    root.after(50, process_thumbnails)
    if exif_var.get():
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

# -------------------- EXIF Checkbox --------------------
def on_exif_toggle():
    if exif_var.get():
        for item in tree.get_children():
            file = filemap[item]
            pending_exif.append((item, file))
        progress["maximum"] = len(pending_files) + len(pending_exif)
        process_exif()

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
    top.title(os.path.basename(filepath))

    canvas = tk.Canvas(top, width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT)
    canvas.pack(expand=True, fill=tk.BOTH)

    current_index = filelist.index(filepath)
    zoomed = False
    photo_id = None
    start_x = start_y = 0
    photo = None

    def show_image(file, zoom=False):
        nonlocal photo, photo_id
        img = Image.open(file)
        if not zoom:
            img.thumbnail((PREVIEW_WIDTH, PREVIEW_HEIGHT))
        photo = ImageTk.PhotoImage(img, master=top)
        canvas.delete("all")
        photo_id = canvas.create_image(PREVIEW_WIDTH//2, PREVIEW_HEIGHT//2, image=photo)

    def show_at_index(index):
        nonlocal current_index, zoomed
        if 0 <= index < len(filelist):
            current_index = index
            zoomed = False
            show_image(filelist[current_index], zoom=False)

    def on_wheel(event):
        if event.delta < 0:
            show_at_index(current_index + 1)
        else:
            show_at_index(current_index - 1)

    def toggle_zoom(event):
        nonlocal zoomed
        zoomed = not zoomed
        show_image(filelist[current_index], zoom=zoomed)

    def start_drag(event):
        nonlocal start_x, start_y
        start_x = event.x
        start_y = event.y

    def do_drag(event):
        nonlocal start_x, start_y
        if photo_id is not None:
            dx = event.x - start_x
            dy = event.y - start_y
            canvas.move(photo_id, dx, dy)
            start_x = event.x
            start_y = event.y

    def on_left(event):
        show_at_index(current_index - 1)

    def on_right(event):
        show_at_index(current_index + 1)

    top.bind("<MouseWheel>", on_wheel)
    canvas.bind("<Double-Button-1>", toggle_zoom)
    canvas.bind("<Button-1>", start_drag)
    canvas.bind("<B1-Motion>", do_drag)
    top.bind("<Left>", on_left)
    top.bind("<Right>", on_right)

    show_image(filepath, zoom=False)
    top.focus_set()

# -------------------- 排序功能 --------------------
def treeview_sort_column(tv, col, reverse=False):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]) if t[0] != "N/A" else float('-inf'), reverse=reverse)
    except ValueError:
        l.sort(key=lambda t: t[0], reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# -------------------- 主窗口 --------------------
root = tk.Tk()
root.title("文件与EXIF信息列表")
root.geometry("1200x700")

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

# EXIF Checkbox
exif_var = tk.BooleanVar(value=False)
chk_exif = tk.Checkbutton(frame_top, text="加载EXIF", variable=exif_var, command=on_exif_toggle)
chk_exif.pack(side=tk.LEFT, padx=5)

# Treeview
columns = ("filename", "ctime", "camera", "lens", "focal", "aperture", "datetime")
tree = ttk.Treeview(root, columns=columns)
tree.column("#0", width=60, anchor="center")
tree.heading("#0", text="缩略图")
tree.heading("filename", text="文件名")
tree.heading("ctime", text="创建时间")
tree.heading("camera", text="相机")
tree.heading("lens", text="镜头")
tree.heading("focal", text="焦距(mm)")
tree.heading("aperture", text="光圈(F)")
tree.heading("datetime", text="拍摄时间")

tree.column("filename", width=180)
tree.column("ctime", width=140)
tree.column("camera", width=120)
tree.column("lens", width=200)
tree.column("focal", width=80, anchor="center")
tree.column("aperture", width=80, anchor="center")
tree.column("datetime", width=160)
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<Double-1>", on_double_click)

# 绑定列头排序
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))

# 进度条
progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.pack(fill=tk.X, pady=5, padx=5)

root.mainloop()
