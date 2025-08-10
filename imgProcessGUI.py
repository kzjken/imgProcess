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
srcListJPG = []
destListJPG = []

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

mainframe = ttk.Frame(root, padding="20 10 20 10")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# ========================== Row 0: Source Path ==========================
ttk.Label(mainframe, text="Source path:").grid(row=0, column=0, sticky=E, padx=5, pady=5)
srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width=60, textvariable=srcPath)
srcPath_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
def selectSrcDir():
    filepath = os.path.normpath(filedialog.askdirectory())
    srcPath.set(filepath)
    if os.path.exists(filepath):
        destPath.set(filepath + "_OUT")
ttk.Button(mainframe, text="Browse", command=selectSrcDir).grid(row=0, column=3, sticky=W, padx=5, pady=5)

# ========================== Row 1: Destination Path ==========================
ttk.Label(mainframe, text="Destination path:").grid(row=1, column=0, sticky=E, padx=5, pady=5)
destPath = StringVar()
destPath_entry = ttk.Entry(mainframe, width=60, textvariable=destPath)
destPath_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
def modDestDir():
    filepath = os.path.normpath(filedialog.askdirectory())
    destPath.set(filepath)
ttk.Button(mainframe, text="Change", command=modDestDir).grid(row=1, column=3, sticky=W, padx=5, pady=5)

# ========================== Row 2: Function Selection ==========================
ttk.Label(mainframe, text="Functions:").grid(row=2, column=0, sticky=E, padx=5, pady=5)
renameFlag = StringVar(value="1")
compressFlag = StringVar(value="1")
ttk.Checkbutton(mainframe, text="Rename", variable=renameFlag).grid(row=2, column=3, sticky=W, padx=5)
ttk.Label(mainframe, text="1. Rename photos according to EXIF (date, time, camera, etc.)").grid(row=2, column=1, columnspan=2, sticky=W, padx=5, pady=5)
ttk.Checkbutton(mainframe, text="Compress", variable=compressFlag).grid(row=3, column=3, sticky=W, padx=5)
ttk.Label(mainframe, text="2. Compress photos (reduce image size) using Python PIL").grid(row=3, column=1, columnspan=2, sticky=W, padx=5)

# ========================== Row 4: Rename Structure (Label + Checkboxes) ==========================
ttk.Label(mainframe, text="Rename Structure:").grid(row=4, column=0, sticky=E, padx=5, pady=5)
structure_options = [
    ("Index", "index"),
    ("Date", "date"),
    ("Time", "time"),
    ("OriginalName", "originalname"),
    ("Camera", "camera"),
    ("Hash", "hash"),
]
structure_vars = {}
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

# ========================== Row 5: Buttons (Preview/Execute, right aligned) ==========================
button_frame = ttk.Frame(mainframe)
button_frame.grid(row=5, column=0, columnspan=4, sticky="e", padx=5, pady=10)
preview_Button = ttk.Button(button_frame, text="Preview", command=lambda: thread_it(previewBtn))
preview_Button.pack(side=RIGHT, padx=10)
process_Button = ttk.Button(button_frame, text='Execute', command=lambda: thread_it(executeBtn), state="disable")
process_Button.pack(side=RIGHT, padx=10)

# ========================== Row 6: Log Window ==========================
ttk.Label(mainframe, text="Log:").grid(row=6, column=0, sticky=(N, E), padx=5, pady=10)
log_text = Text(mainframe, width=120, height=22, state="disabled")
log_text.grid(row=6, column=1, columnspan=2, sticky="nsew", padx=5, pady=10)
logText_scrollbar = Scrollbar(mainframe, orient="vertical", command=log_text.yview)
logText_scrollbar.grid(row=6, column=3, sticky="ns", padx=2, pady=10)
log_text.configure(yscrollcommand=logText_scrollbar.set)
Font_UserChanged = ("Comic Sans MS", 9)
log_text.configure(font=Font_UserChanged)

# Make log area expand with window
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
        return False
    if not os.path.exists(srcFolder):
        print("  Error: Source path doesn't exist, please reselect...")
        return False
    if not os.path.isdir(srcFolder):
        print("  Error: Source path invalid, please reselect...")
        return False
    if not os.listdir(srcFolder):
        print("  Error: No images in source folder, please reselect...")
        return False
    if destFolder == "":
        print("  Error: Destination path invalid, please reselect...")
        return False
    return True

def checkCheckButton():
    """Check if at least one function is selected."""
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
    for srcName in glob.glob(srcPathIncExtName):
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
    if fileCounter > 0:
        print("\n" + str(fileCounter) + " " + extName + " files found.")
        print("---------------------------------------------------------------------------------------")
        # Check for name conflicts
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
    log_text.configure(state="normal")
    print("=======================================================================================")
    print("=======================================================================================")
    print("Start processing")
    srcPathVal = srcPath_entry.get()
    destPathVal = destPath_entry.get()
    if not os.path.exists(destPathVal):
        if destPathVal == srcPathVal + "_OUT":
            os.makedirs(destPathVal)
        else:
            msgBoxReturn = messagebox.askquestion(title="Message", message="Destination \n" + destPathVal + "\ndoesn't exist, create?")
            if msgBoxReturn == "yes":
                os.makedirs(destPathVal)
                print("  Create destination folder: " + destPathVal)
    process_Button.configure(state="disable")
    if compressFlag.get() == '1':
        for index, imageJPG in enumerate(srcListJPG):
            imgProcess.renAndcompImg(imageJPG, destListJPG[index], 85)
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
            log_text.see(END)
    else:
        for index, imageJPG in enumerate(srcListJPG):
            os.system("copy " + imageJPG + " " + destListJPG[index])
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
            log_text.see(END)
    print("=======================================================================================")
    print("END")
    log_text.see(END)
    log_text.configure(state="disabled")

# ========================== Thread Helper ==========================
def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

root.mainloop()
