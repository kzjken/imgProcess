import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

def format_size(size_bytes):
    """Convert bytes to human-readable string"""
    for unit in ['B','KB','MB','GB','TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def format_mtime(path):
    """Return modification time as string"""
    # return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(path)))

def populate_treeview(parent, path):
    try:
        items = os.listdir(path)
    except PermissionError:
        return
    for item in sorted(items):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            # Folder entry: size empty
            mtime = format_mtime(full_path)
            node = tree.insert(parent, "end", text=item,
                               values=("Folder", mtime, "", full_path))
            populate_treeview(node, full_path)
        else:
            ext = os.path.splitext(item)[1].lower()
            if ext in IMAGE_EXTS:
                size = format_size(os.path.getsize(full_path))
                mtime = format_mtime(full_path)
                tree.insert(parent, "end", text=item,
                            values=(ext.lstrip("."), mtime, size, full_path))

def load_directory(directory):
    if directory and os.path.isdir(directory):
        tree.delete(*tree.get_children())  # clear existing items
        root_node = tree.insert("", "end", text=directory,
                                values=("Folder", format_mtime(directory), "", directory), open=True)
        populate_treeview(root_node, directory)

        # for child in tree.get_children(root_node):
        #     tree.item(child, open=True)
        path_var.set(directory)
    else:
        messagebox.showerror("Error", f"Invalid path: {directory}")

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        load_directory(directory)

def on_enter_path(event=None):
    directory = path_var.get().strip()
    if os.path.isdir(directory):
        load_directory(directory)
    else:
        messagebox.showerror("Error", f"Invalid path: {directory}")

def on_right_click(event):
    item_id = tree.identify_row(event.y)
    if not item_id:
        return
    tree.selection_set(item_id)
    item_type = tree.item(item_id, "values")[0]  # Type is now first column
    if item_type == "Folder":
        folder_menu.post(event.x_root, event.y_root)
    else:
        image_menu.post(event.x_root, event.y_root)

# ==== Context menu: Folders ====
def open_folder():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[3]  # Full Path is now last column
    messagebox.showinfo("Folder Operation", f"Open Folder: {path}")

def refresh_folder():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[3]  # Full Path
    tree.delete(*tree.get_children(item_id))
    populate_treeview(item_id, path)

# ==== Context menu: Images ====
def open_image():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[3]
    messagebox.showinfo("Image Operation", f"Open Image: {path}")

def delete_image():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[3]
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {path}?")
    if confirm:
        try:
            os.remove(path)
            tree.delete(item_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ==== GUI ====
root = tk.Tk()
root.title("NamImager [Name Image]")

# Frame for textbox + Browse button in one line
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=5, pady=5)

path_var = tk.StringVar()
path_entry = tk.Entry(top_frame, textvariable=path_var)
path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
path_entry.bind("<Return>", on_enter_path)

btn = tk.Button(top_frame, text="Browse", command=select_directory)
btn.pack(side=tk.LEFT, padx=5)

# Treeview with columns: Type, Modified Time, Size, Full Path (Full Path last)
tree = ttk.Treeview(root, columns=("type", "mtime", "size", "fullpath"), show="tree headings")
tree.pack(fill=tk.BOTH, expand=True)

tree.heading("#0", text="Name")
tree.column("#0", width=250, anchor="w")

tree.heading("type", text="Type")
tree.column("type", width=80, anchor="center")

tree.heading("mtime", text="Modified Time")
tree.column("mtime", width=150, anchor="center")

tree.heading("size", text="Size")
tree.column("size", width=80, anchor="e")

tree.heading("fullpath", text="Full Path")
tree.column("fullpath", width=400, anchor="w")

# Context menus
folder_menu = tk.Menu(root, tearoff=0)
folder_menu.add_command(label="Open Folder", command=open_folder)
folder_menu.add_command(label="Refresh", command=refresh_folder)

image_menu = tk.Menu(root, tearoff=0)
image_menu.add_command(label="Open Image", command=open_image)
image_menu.add_command(label="Delete Image", command=delete_image)

tree.bind("<Button-3>", on_right_click)

root.mainloop()
