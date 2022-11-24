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

#################################################################################################################################
#------------------------------------------------------------- Global ----------------------------------------------------------#
#################################################################################################################################


#################################################################################################################################
#------------------------------------------------------------- rp stdout--------------------------------------------------------#
#################################################################################################################################
class PrintLogger():
    """ pass reference to text widget """
    def __init__(self, textbox):
        self.textbox = textbox

    """ write text to textbox, scroll to end """
    def write(self, text):
        self.textbox.insert(END, text)

    """needed for file like object"""
    def flush(self):
        pass

#################################################################################################################################
#------------------------------------------------------------- tkinter ---------------------------------------------------------#
#################################################################################################################################
root = Tk()
root.title("Image Converter [Z.Kang]")
root.geometry("860x540")
root.minsize(860, 540)
root.maxsize(860, 540)

mainframe = ttk.Frame(root, padding = "20 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

#################################################################################################################################
# row 0 source path
#################################################################################################################################
ttk.Label(mainframe, text = "Source path:").grid(row = 0, column = 0, sticky = E, padx = 5, pady = 5)

srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width = 50, textvariable = srcPath)
srcPath_entry.grid(row = 0, column = 1, sticky = (W, E), padx = 5, pady = 5)

def selectSrcDir():
    filepath = os.path.normpath(filedialog.askdirectory())
    srcPath.set(filepath)
    # set destination path = source path + _OUT
    if(os.path.exists(filepath)):
        destPath.set(filepath + "_OUT")
ttk.Button(mainframe, text = "Browse", command = selectSrcDir).grid(row = 0, column = 2, sticky = W, padx = 5, pady = 5)

#################################################################################################################################
# row 1 destination path
#################################################################################################################################
ttk.Label(mainframe, text = "Destination path:").grid(row = 1, column = 0, sticky = E, padx = 5, pady = 5)

destPath = StringVar()
destPath_entry = ttk.Entry(mainframe, width = 50, textvariable = destPath)
destPath_entry.grid(row = 1, column = 1, sticky = (W, E), padx = 5, pady = 5)

def modDestDir():
    filepath = os.path.normpath(filedialog.askdirectory())
    destPath.set(filepath)
ttk.Button(mainframe, text = "Change", command = modDestDir).grid(row = 1, column = 2, sticky = W, padx = 5, pady = 5)

#################################################################################################################################
# row 2 - 3: Functions
#################################################################################################################################
ttk.Label(mainframe, text = "Functions:").grid(row = 2, column = 0, sticky = E, padx = 5, pady = 5)

""" rename """
renameFlag = StringVar()
renameFlag.set(1)
rename_checkbutton = ttk.Checkbutton(mainframe, text = "Rename", variable = renameFlag)
rename_checkbutton.grid(row = 2, column = 2, sticky = (W, E), padx = 5)
ttk.Label(mainframe, text = "1. Rename photos to Shotdata_Shotdevice").grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)

""" compress """
compressFlag = StringVar()
compressFlag.set(1)
compress_checkbutton = ttk.Checkbutton(mainframe, text = "Compress", variable = compressFlag)
compress_checkbutton.grid(row = 3, column = 2, sticky = (W, E), padx = 5)
ttk.Label(mainframe, text = "2. Compress photos (Reduce image size) using Python PIL").grid(row = 3, column = 1, sticky = W, padx = 5)

#################################################################################################################################
# row 4 - 20 log window
#################################################################################################################################
ttk.Label(mainframe, text = "Log:").grid(row = 4, column = 0, sticky = (N, E), padx = 5, pady = 10)

log_text = Text(mainframe, width = 90, height = 30, state = "disabled")
log_text.grid(row = 4, column = 1, sticky = (W, E), padx = 5, pady = 10, rowspan = 16)

logText_scrollbar = Scrollbar(mainframe, orient="vertical", command = log_text.yview)
logText_scrollbar.grid(row = 4, column = 1, sticky = (E, N, S), padx = 5, pady = 10, rowspan = 16)

log_text.configure(yscrollcommand = logText_scrollbar.set)

# change print output from terminal to tinker loh windows
pl = PrintLogger(log_text)
sys.stdout = pl

#################################################################################################################################
# row 5 execute
#################################################################################################################################
""" check if src and dest paths are valid """
def checkPath(srcFolder, destFolder):
    print(date.today().strftime("%Y.%m.%d") + ' ' + datetime.now().strftime("%H:%M:%S"))
    print("---------------------------------------------------------------------------------------")
    print("check path:")

    # check if source path is empty, exists or valid...
    if srcFolder == "":
        print("  Error: Source path is empty, please select...")
        return False
    if not os.path.exists(srcFolder):
        print("  Error: Source path doesn't exist, please reselect...")
        return False
    if not os.path.isdir(srcFolder):
        print("  Error: Source path invalid, please reselect...")
        return False

    # check if source folder is empty
    if not os.listdir(srcFolder):
        print("  Error: No images in source folder, please reselect...")
        return False
    else:
        if destFolder == "" or not os.path.isdir(destFolder):
            print("  Error: Destination path invalid, please reselect...")
            return False
        else:
            return True

###########################################################

""" check if functions are selected """
def checkCheckButton():
    invalidCounter = 0
    print("Check selected options:")
    # print(renameFlag.get() + compressFlag.get())

    if renameFlag.get() == '1':
        print("  Rename checked.")
    else:
        print("  Rename unchecked.")
        invalidCounter += 1# invalidCounter + 1

    if compressFlag.get() == '1':
        print("  Compress checked.")
    else:
        print("  Compress unchecked.")
        invalidCounter += 1

    # if renameFlag.get() == '0' and compressFlag.get() == '0':
    if invalidCounter > 1:
        print("Error: Please select at least one function...")
        return False
    else:
        return True

###########################################################

""" preview changes """
def preview(srcFolder, destFolder, extName):
    srcPathIncExtName = srcFolder + "\\*." + extName
    fileCounter = 0
    srcList = []
    destList = []

    # glob extName e.g. jpg files in srcFolder
    for srcName in glob.glob(srcPathIncExtName):
        # rename preview
        if renameFlag.get() == '1':
            exifList = imgProcess.getExif(srcName)
            destName = destFolder + "\\" + imgProcess.renameAccExif(srcName, exifList)
        else:
            destName = destFolder + "\\" + os.path.basename(srcName)
        srcList.append(srcName)
        destList.append(destName)

        # print rename behavior
        if renameFlag.get() == '1':
            print("  " + str(fileCounter + 1) + ': ' + os.path.basename(srcName) + " ==> " + os.path.basename(destName))
        else:
            print("  " + str(fileCounter + 1) + ': ' + os.path.basename(srcName))
        fileCounter += 1

    if fileCounter > 0:
        print("\n" + str(fileCounter) + " " + extName + " files found.")
        print("---------------------------------------------------------------------------------------")

        """ name conflict """
        if renameFlag.get() == '1':
            dupItemIndex = []
            dupItem = []
            for index, element in enumerate(destList):
                if destList.count(element) > 1:
                    if element not in dupItem:
                        print("Conflicts:" + str(destList.count(element)) + " " + os.path.basename(element) + ": suffix _X will be added.")
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
                            suffix += 1
        else:
            print("Reducing image size...")

        process_Button.configure(state = "normal")
        #compress_checkbutton.configure(state = "disable")
        #rename_checkbutton.configure(state = "disable")

        print("---------------------------------------------------------------------------------------")
        print("Please click execute to continue processing.")

    return fileCounter, srcList, destList

###########################################################

srcListJPG = []
destListJPG = []
# srcListJPEG = []
# destListJPEG = []
# srcListPNG = []
# destListPNG = []

###########################################################

def previewBtn():
    log_text.configure(state = "normal")
    log_text.delete('1.0', END)

    # path
    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()

    if checkPath(srcPath, destPath):
        print("OK")
        print("---------------------------------------------------------------------------------------")

        if checkCheckButton():
            print("function checked: ok.")
            print("=======================================================================================")
            print("Preview:")

            sumJPG, srcList, destList = preview(srcPath, destPath, "jpg")
            """ for other extension, e.g. jpeg """
            #sumJPEG, srcListJPEG, destListJPEG = preview(srcPath, destPath, "jpeg")

            srcListJPG.clear()
            destListJPG.clear()

            for item in srcList:
                srcListJPG.append(item)
            for item in destList:
                destListJPG.append(item)

        else:
            print("=======================================================================================")
            print("Abort, function check failed!")
            pass
    else:
        print("=======================================================================================")
        print("Abort, path check failed!")
        pass

    log_text.see(END)
    log_text.configure(state = "disable")

###########################################################

def process():
    log_text.configure(state = "normal")
    print("=======================================================================================")
    print("=======================================================================================")

    print("Start processing")

    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()
    if (os.path.exists(destPath) == False):
        if destPath == srcPath + "_OUT":
            os.makedirs(destPath)
        else:
            msgBoxReturn = messagebox.askquestion(title = "Message", message = "Destination \n" + destPath + "\ndoesn't exist, create?")
            if msgBoxReturn == "yes":
                os.makedirs(destPath)
                print("  Create destination folder: " + destPath)

    process_Button.configure(state = "disable")
    #compress_checkbutton.configure(state = "normal")
    #rename_checkbutton.configure(state = "normal")

    if compressFlag.get() == '1':
        for index, imageJPG in enumerate(srcListJPG):
            imgProcess.renAndcompImg(imageJPG, destListJPG[index], 85)
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
    else:
        for index, imageJPG in enumerate(srcListJPG):
            #imgProcess.renAndcompImg(imageJPG, destListJPG[index], 100)
            os.system("copy " + imageJPG + " " + destListJPG[index])
            print(str(index + 1) + ': ' + os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))

    print("=======================================================================================")
    print("END")

    log_text.see(END)
    log_text.configure(state = "disable")

###########################################################
###########################################################

preview_Button = ttk.Button(mainframe, text = "Preview", command = previewBtn)
preview_Button.grid(row = 4, column = 2, sticky = (N, S), padx = 5, pady = 10)

process_Button = ttk.Button(mainframe, text = "Execute", command = process, state = "disable")
process_Button.grid(row = 5, column = 2, sticky = (N, S), padx = 5, pady = 5, rowspan = 3)

root.mainloop()

#pyinstaller --noconsole imgProcessGUI.py
