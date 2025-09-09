import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

def populate_treeview(parent, path):
    try:
        items = os.listdir(path)
    except PermissionError:
        return
    for item in sorted(items):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            node = tree.insert(parent, "end", text=item, values=(full_path, "dir"), open=False)
            populate_treeview(node, full_path)
        else:
            ext = os.path.splitext(item)[1].lower()
            if ext in IMAGE_EXTS:
                tree.insert(parent, "end", text=item, values=(full_path, "img"))

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        tree.delete(*tree.get_children()) # clear existing items
        root_node = tree.insert("", "end", text=directory, values=(directory, "dir"), open=True)
        populate_treeview(root_node, directory)

def on_right_click(event):
    item_id = tree.identify_row(event.y)
    if not item_id:
        return

    tree.selection_set(item_id)
    item_type = tree.item(item_id, "values")[1]

    if item_type == "dir":
        folder_menu.post(event.x_root, event.y_root)
    elif item_type == "img":
        image_menu.post(event.x_root, event.y_root)

# ==== Context menu: Folders ====
def open_folder():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[0]
    messagebox.showinfo("Folder Operation", f"Open Folder: {path}")

def refresh_folder():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[0]
    tree.delete(*tree.get_children(item_id))
    populate_treeview(item_id, path)

# ==== Context menu: Images ====
def open_image():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[0]
    messagebox.showinfo("Image Operation", f"Open Image: {path}")

def delete_image():
    item_id = tree.selection()[0]
    path = tree.item(item_id, "values")[0]
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

btn = tk.Button(root, text="Browse", command=select_directory)
btn.pack(pady=5)

# Treeview with proper column setup
tree = ttk.Treeview(
    root,
    columns=("fullpath", "type"),
    show="tree headings"  # show both tree and headers
)
tree.pack(fill=tk.BOTH, expand=True)

# Configure columns
tree.heading("#0", text="Name")
tree.column("#0", width=250, anchor="w")

tree.heading("fullpath", text="Full Path")
tree.column("fullpath", width=400, anchor="w")

tree.heading("type", text="Type")
tree.column("type", width=80, anchor="center")

# Context menus
folder_menu = tk.Menu(root, tearoff=0)
folder_menu.add_command(label="Open Folder", command=open_folder)
folder_menu.add_command(label="Refresh", command=refresh_folder)

# Context menu: Images
image_menu = tk.Menu(root, tearoff=0)
image_menu.add_command(label="Open Image", command=open_image)
image_menu.add_command(label="Delete Image", command=delete_image)

tree.bind("<Button-3>", on_right_click)


root.mainloop()
