import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ExifTags
import os

# 存放缩略图引用
thumbnails = {}
filemap = {}  # item_id -> 文件路径
filelist = []  # 文件顺序列表


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

    except Exception as e:
        return [f"Error: {e}"] + ["N/A"] * 4


def create_thumbnail(filepath, size=(50, 50)):
    """生成缩略图"""
    try:
        img = Image.open(filepath)
        img.thumbnail(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"缩略图生成失败: {e}")
        return None


def add_files_from_list(files):
    """从文件列表添加到TreeView"""
    for file in files:
        if file in filelist:  # 避免重复
            continue
        filename = os.path.basename(file)
        camera, lens, focal, aperture, datetime = get_exif_info(file)

        # 缩略图
        thumb = create_thumbnail(file, size=(50, 50))
        if thumb:
            item = tree.insert(
                "",
                tk.END,
                text="",
                image=thumb,
                values=(filename, camera, lens, focal, aperture, datetime),
            )
            thumbnails[file] = thumb
            filemap[item] = file
            filelist.append(file)


def add_files():
    files = filedialog.askopenfilenames(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff")]
    )
    if files:
        path_var.set(os.path.dirname(files[0]))  # 更新路径显示
        add_files_from_list(files)


def add_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_var.set(folder)  # 更新路径显示
        exts = (".jpg", ".jpeg", ".png", ".tiff")
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
        add_files_from_list(files)


def show_image(filepath, top, lbl):
    """显示图片到Label"""
    img = Image.open(filepath)
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    img.thumbnail((screen_w, screen_h))
    photo = ImageTk.PhotoImage(img)

    lbl.config(image=photo)
    lbl.image = photo
    top.title(os.path.basename(filepath))


def on_double_click(event):
    """双击行时放大预览"""
    item_id = tree.focus()
    if not item_id:
        return
    filepath = filemap.get(item_id)
    if not filepath:
        return

    top = tk.Toplevel(root)
    top.title(os.path.basename(filepath))

    lbl = tk.Label(top)
    lbl.pack()

    current_index = filelist.index(filepath)

    def show_at_index(index):
        nonlocal current_index
        if 0 <= index < len(filelist):
            current_index = index
            show_image(filelist[current_index], top, lbl)

    top.bind("<Left>", lambda e: show_at_index(current_index - 1))
    top.bind("<Right>", lambda e: show_at_index(current_index + 1))

    show_image(filepath, top, lbl)
    top.focus_set()


# 主窗口
root = tk.Tk()
root.title("文件与EXIF信息列表")
root.geometry("1100x600")

# 调整Treeview行高
style = ttk.Style()
style.configure("Treeview", rowheight=60)

# 顶部控制区域
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

# Treeview 表格
columns = ("filename", "camera", "lens", "focal", "aperture", "datetime")
tree = ttk.Treeview(root, columns=columns, show="tree headings")

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

# 绑定双击事件
tree.bind("<Double-1>", on_double_click)

root.mainloop()
