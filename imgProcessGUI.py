from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import os
import glob
import imgProcess
import sys
from datetime import datetime
from datetime import date
import threading

# ========================== Global Variables ==========================
srcListJPG = []  # List to store source image file paths
destListJPG = []  # List to store destination image file paths

# ========================== Redirect stdout to GUI ==========================
class PrintLogger():
    """Redirect print output to the Tkinter Text widget."""
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.insert(END, text)

    def flush(self):
        pass

# ========================== Main Window Setup ==========================
root = Tk()
root.title("Image Converter V0.2 [Z.Kang]")
root.geometry("1100x700")
root.minsize(900, 600)

# Main frame for all widgets
mainframe = ttk.Frame(root, padding="20 10 20 10")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# ========================== Row 0: Source Path ==========================
# Label and entry for source folder
ttk.Label(mainframe, text="Source path:").grid(row=0, column=0, sticky=E, padx=5, pady=5)
srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width=60, textvariable=srcPath)
srcPath_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

def selectSrcDir():
    """Open dialog to select source directory and set default destination."""
    filepath = os.path.normpath(filedialog.askdirectory())
    srcPath.set(filepath)
    if os.path.exists(filepath):
        destPath.set(filepath + "_OUT")

ttk.Button(mainframe, text="Browse", command=selectSrcDir).grid(row=0, column=3, sticky=W, padx=5, pady=5)

# ========================== Row 1: Destination Path ==========================
# Label and entry for destination folder
ttk.Label(mainframe, text="Destination path:").grid(row=1, column=0, sticky=E, padx=5, pady=5)
destPath = StringVar()
destPath_entry = ttk.Entry(mainframe, width=60, textvariable=destPath)
destPath_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

def modDestDir():
    """Open dialog to select destination directory."""
    filepath = os.path.normpath(filedialog.askdirectory())
    destPath.set(filepath)

ttk.Button(mainframe, text="Change", command=modDestDir).grid(row=1, column=3, sticky=W, padx=5, pady=5)

# ========================== Row 2: Function Selection ==========================
# Function selection: Rename and Compress
ttk.Label(mainframe, text="Functions:").grid(row=2, column=0, sticky=E, padx=5, pady=5)
renameFlag = StringVar(value="1")  # "1" means checked
compressFlag = StringVar(value="1")
ttk.Checkbutton(mainframe, text="Rename", variable=renameFlag).grid(row=2, column=3, sticky=W, padx=5)
ttk.Label(mainframe, text="1. Rename photos according to EXIF (date, time, camera, etc.)").grid(row=2, column=1, columnspan=2, sticky=W, padx=5, pady=5)
ttk.Checkbutton(mainframe, text="Compress", variable=compressFlag).grid(row=3, column=3, sticky=W, padx=5)
ttk.Label(mainframe, text="2. Compress photos (reduce image size) using Python PIL").grid(row=3, column=1, columnspan=2, sticky=W, padx=5)

# ========================== Row 4: Rename Structure (Label + Checkboxes) ==========================
# Checkboxes for rename structure options
ttk.Label(mainframe, text="Rename Structure:").grid(row=4, column=0, sticky=E, padx=5, pady=5)
structure_options = [
    ("Index", "index"),
    ("Date", "date"),
    ("Time", "time"),
    ("OriginalName", "originalname"),
    ("Camera", "camera"),
    ("Hash", "hash"),
]
structure_vars = {}  # Store IntVar for each option
default_checked = {"date", "time", "camera"}
structure_frame = ttk.Frame(mainframe)
structure_frame.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=5)
for i, (label, key) in enumerate(structure_options):
    var = IntVar(value=1 if key in default_checked else 0)
    structure_vars[key] = var
    ttk.Checkbutton(structure_frame, text=label, variable=var).grid(row=0, column=i, sticky="w", padx=10)

def get_structure_selection():
    """Return the list of selected structure fields in order."""
    return [key for label, key in structure_options if structure_vars[key].get() == 1]

def set_structure_frame_state(enabled=True):
    """Enable or disable all checkboxes in the rename structure row."""
    state = "normal" if enabled else "disabled"
    for child in structure_frame.winfo_children():
        if isinstance(child, ttk.Checkbutton):
            child.state(["!disabled"] if enabled else ["disabled"])

def toggle_structure_frame(*args):
    """Callback to enable/disable rename structure checkboxes based on Rename flag."""
    if renameFlag.get() == '1':
        set_structure_frame_state(True)
    else:
        set_structure_frame_state(False)

# Trace the Rename checkbox to enable/disable structure options
renameFlag.trace_add('write', toggle_structure_frame)
toggle_structure_frame()  # Set initial state

# ========================== Row 5: Buttons (Preview/Execute) ==========================
# Preview and Execute buttons
preview_Button = ttk.Button(mainframe, text="Preview", command=lambda: thread_it(previewBtn))
preview_Button.grid(row=5, column=2, sticky="e", padx=5, pady=5)
process_Button = ttk.Button(mainframe, text='Execute', command=lambda: thread_it(executeBtn), state="disable")
process_Button.grid(row=5, column=3, sticky="w", padx=5, pady=5)

# ========================== Row 6: Log Window (Text+Scrollbar in a Frame) ==========================
# Log area with vertical scrollbar
ttk.Label(mainframe, text="Log:").grid(row=6, column=0, sticky=(N, E), padx=5, pady=10)
log_frame = ttk.Frame(mainframe)
log_frame.grid(row=6, column=1, columnspan=3, sticky="nsew", padx=5, pady=10)
log_text = Text(log_frame, width=90, height=22, state="disabled")
log_text.pack(side=LEFT, fill=BOTH, expand=True)
logText_scrollbar = Scrollbar(log_frame, orient="vertical", command=log_text.yview)
logText_scrollbar.pack(side=RIGHT, fill=Y)
log_text.configure(yscrollcommand=logText_scrollbar.set)
Font_UserChanged = ("Comic Sans MS", 9)
log_text.configure(font=Font_UserChanged)

# ========================== Row 7: Progress Bar ==========================
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(mainframe, variable=progress_var, maximum=100, mode="determinate")
progress_bar.grid(row=7, column=1, columnspan=3, sticky="ew", padx=5, pady=(0, 10))
progress_bar.grid_remove()  # Hide progress bar initially

# Configure column and row weights for resizing
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=0)
mainframe.columnconfigure(3, weight=0)
mainframe.rowconfigure(6, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(6, weight=1)

# Redirect print output to the log window
pl = PrintLogger(log_text)
sys.stdout = pl

# ========================== Utility Functions ==========================
def checkPath(srcFolder, destFolder):
    """Check if source and destination paths are valid."""
    print(date.today().strftime("%Y.%m.%d") + ' ' + datetime.now().strftime("%H:%M:%S"))
    print("---------------------------------------------------------------------------------------")
    print("check path:")
    if srcFolder == "":
        print("  Error: Source path is empty, please select...")
        messagebox.showerror("Error", "Source path is empty, please select a folder.")
        return False
    if not os.path.exists(srcFolder):
        print("  Error: Source path doesn't exist, please reselect...")
        messagebox.showerror("Error", "Source path doesn't exist, please reselect.")
        return False
    if not os.path.isdir(srcFolder):
        print("  Error: Source path invalid, please reselect...")
        messagebox.showerror("Error", "Source path is not a folder, please reselect.")
        return False
    if not os.listdir(srcFolder):
        print("  Error: No images in source folder, please reselect...")
        messagebox.showerror("Error", "No images in source folder, please reselect.")
        return False
    if destFolder == "":
        print("  Error: Destination path invalid, please reselect...")
        messagebox.showerror("Error", "Destination path is empty, please reselect.")
        return False
    return True

def checkCheckButton():
    """Check if at least one function is selected (Rename or Compress)."""
    invalidCounter = 0
    print("Check selected options:")
    if renameFlag.get() == '1':
        print("  Rename checked.")
    else:
        print("  Rename unchecked.")
        invalidCounter += 1
    if compressFlag.get() == '1':
        print("  Compress checked.")
    else:
        print("  Compress unchecked.")
        invalidCounter += 1
    if invalidCounter > 1:
        print("Error: Please select at least one function...")
        return False
    return True

# ========================== Preview Function ==========================
def preview(srcFolder, destFolder, extName):
    """Preview the changes before processing."""
    srcPathIncExtName = srcFolder + "\\*." + extName
    fileCounter = 0
    srcList = []
    destList = []
    structure = get_structure_selection()
    file_list = glob.glob(srcPathIncExtName)
    total_files = len(file_list)
    if total_files > 0:
        progress_bar.grid()
        progress_var.set(0)
        root.update_idletasks()
    for srcName in file_list:
        if renameFlag.get() == '1':
            exifList = imgProcess.getExif(srcName)
            destName = destFolder + "\\" + imgProcess.renameAccExif(
                srcName, exifList, structure, index=fileCounter+1
            )
        else:
            destName = destFolder + "\\" + os.path.basename(srcName)
        srcList.append(srcName)
        destList.append(destName)
        if renameFlag.get() == '1':
            print("  " + str(fileCounter + 1) + ': ' + os.path.basename(srcName) + " ==> " + os.path.basename(destName))
            log_text.see(END)
        else:
            print("  " + str(fileCounter + 1) + ': ' + os.path.basename(srcName))
            log_text.see(END)
        fileCounter += 1
        if total_files > 0:
            progress_var.set(fileCounter / total_files * 100)
            root.update_idletasks()
    if total_files > 0:
        progress_var.set(100)
        root.update_idletasks()
        progress_bar.grid_remove()
    if fileCounter > 0:
        print("\n" + str(fileCounter) + " " + extName + " files found.")
        print("---------------------------------------------------------------------------------------")
        # Check for name conflicts in destination filenames
        if renameFlag.get() == '1':
            dupItemIndex = []
            dupItem = []
            for index, element in enumerate(destList):
                if destList.count(element) > 1:
                    if element not in dupItem:
                        print("Conflicts:" + str(destList.count(element)) + " " + os.path.basename(element) + ": suffix _X will be added.")
                        log_text.see(END)
                        dupItem.append(element)
                    dupItemIndex.append(index)
            if len(dupItem) > 0:
                for item in dupItem:
                    suffix = 0
                    for index in dupItemIndex:
                        if destList[index] == item:
                            filename, file_extension = os.path.splitext(destList[index])
                            destList[index] = filename + '_' + str(suffix) + file_extension
                            print("  " + os.path.basename(destList[index]) + " ==> " + os.path.basename(destList[index]))
                            log_text.see(END)
                            suffix += 1
        else:
            print("Reducing image size...")
        process_Button.configure(state="normal")
        print("---------------------------------------------------------------------------------------")
        print("Please click execute to continue processing.")
    return fileCounter, srcList, destList

# ========================== Preview Button Callback ==========================
def previewBtn():
    """Callback for Preview button. Shows preview of actions in log."""
    log_text.configure(state="normal")
    log_text.delete('1.0', END)
    srcPathVal = srcPath_entry.get()
    destPathVal = destPath_entry.get()
    if checkPath(srcPathVal, destPathVal):
        print("OK")
        print("---------------------------------------------------------------------------------------")
        if checkCheckButton():
            print("function checked: ok.")
            print("=======================================================================================")
            print("Preview:")
            sumJPG, srcList, destList = preview(srcPathVal, destPathVal, "jpg")
            srcListJPG.clear()
            destListJPG.clear()
            for item in srcList:
                srcListJPG.append(item)
            for item in destList:
                destListJPG.append(item)
        else:
            print("=======================================================================================")
            print("Abort, function check failed!")
    else:
        print("=======================================================================================")
        print("Abort, path check failed!")
    log_text.see(END)
    log_text.configure(state="disabled")

# ========================== Execute Button Callback ==========================
def executeBtn():
    """Callback for Execute button. Processes images as previewed."""
    log_text.configure(state="normal")
    print("=======================================================================================")
    print("=======================================================================================")
    print("Start processing")
    srcPathVal = srcPath_entry.get()
    destPathVal = destPath_entry.get()
    # Create destination folder if it does not exist
    if not os.path.exists(destPathVal):
        if destPathVal == srcPathVal + "_OUT":
            os.makedirs(destPathVal)
        else:
            msgBoxReturn = messagebox.askquestion(title="Message", message="Destination \n" + destPathVal + "\ndoesn't exist, create?")
            if msgBoxReturn == "yes":
                os.makedirs(destPathVal)
                print("  Create destination folder: " + destPathVal)
    process_Button.configure(state="disable")
    total_files = len(srcListJPG)
    if total_files > 0:
        progress_bar.grid()
        progress_var.set(0)
        root.update_idletasks()
    # Process images: compress or just copy
    if compressFlag.get() == '1':
        for index, imageJPG in enumerate(srcListJPG):
            imgProcess.renAndcompImg(imageJPG, destListJPG[index], 85)
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
            log_text.see(END)
            if total_files > 0:
                progress_var.set((index + 1) / total_files * 100)
                root.update_idletasks()
    else:
        for index, imageJPG in enumerate(srcListJPG):
            os.system("copy " + imageJPG + " " + destListJPG[index])
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
            log_text.see(END)
            if total_files > 0:
                progress_var.set((index + 1) / total_files * 100)
                root.update_idletasks()
    if total_files > 0:
        progress_var.set(100)
        root.update_idletasks()
        progress_bar.grid_remove()
    print("=======================================================================================")
    print("END")
    log_text.see(END)
    log_text.configure(state="disabled")

# ========================== Thread Helper ==========================
def thread_it(func, *args):
    """Run a function in a separate thread to avoid blocking the GUI."""
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

root.mainloop()
