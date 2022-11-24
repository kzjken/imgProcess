from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import os
import glob
import imgProcess
import sys

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

mainframe = ttk.Frame(root, padding = "20 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

#################################################################################################################################
# row 0 path
#################################################################################################################################
ttk.Label(mainframe, text = "Source path:").grid(row = 0, column = 0, sticky = E, padx = 5, pady = 5)

srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width = 50, textvariable = srcPath)
srcPath_entry.grid(row = 0, column = 1, sticky = (W, E), padx = 5, pady = 5)

def selectSrcDir():
    filepath = os.path.normpath(filedialog.askdirectory())
    srcPath.set(filepath)
    #destPath.set(filepath + "/" + os.path.basename(filepath) + "_Output")
    if(os.path.exists(filepath)):
        destPath.set(filepath + "_OUT")
ttk.Button(mainframe, text = "Browse", command = selectSrcDir).grid(row = 0, column = 2, sticky = W, padx = 5, pady = 5)

#################################################################################################################################
# row 1 path
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
# row 2 - 4
#################################################################################################################################
ttk.Label(mainframe, text = "Functions:").grid(row = 2, column = 0, sticky = E, padx = 5, pady = 5)

renameFlag = StringVar()
renameFlag.set(1)
rename_checkbutton = ttk.Checkbutton(mainframe, text = "Rename", variable = renameFlag)
rename_checkbutton.grid(row = 2, column = 2, sticky = (W, E), padx = 5)

ttk.Label(mainframe, text = "1. Rename photos to Shotdata_Shotdevice").grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)

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
def checkPath(srcFolder, destfolder):
    print("check path:")
    if srcFolder == "":
        #messagebox.showerror(title = "错误", message = "指定源文件路径无效，请重新选择！")
        print("  Error: Source path invalid, please reselect...")
        return False

    # check if source folder is empty
    if not os.listdir(srcFolder):
        #messagebox.showerror(title = "错误", message = "目标文件夹\n" + srcFolder + "\内没有文件！")
        print("  Error: No images in source folder, please reselect...")
        return False
    else:
        if destfolder == "":
            #messagebox.showerror(title = "错误", message = "指定目标文件路径无效，请重新选择！")
            print("  Error: Destination path invalid, please reselect...")
            return False
        else:
            return True
            # if (os.path.exists(destfolder) == False):
            #     if destfolder == srcFolder + "_OUTPUT":
            #         os.makedirs(destfolder)
            #         print("  目标文件夹" + destfolder + "已创建。")
            #         return True
            #     else:
            #         msgBoxReturn = messagebox.askquestion(title = "提示", message = "目标文件夹\n" + destfolder + "\n不存在, 是否创建？")
            #         if msgBoxReturn == "yes":
            #             os.makedirs(destfolder)
            #             return True
            #         else:
            #             return False
            # else:
            #     return True

def checkCheckButton():
    print("Check selected options:")
    #print(renameFlag.get() + compressFlag.get() + "   " + type(renameFlag.get()))

    if renameFlag.get() == '0' and compressFlag.get() == '0':
        print("  Error: Please select at least one function...")
        return False
    else:
        return True

def preview(srcFolder, destfolder, extName):
    srcPathIncExtName = srcFolder + "\\*." + extName
    filecounter = 0
    srcList = []
    destList = []
    for srcName in glob.glob(srcPathIncExtName):
        if renameFlag.get() == '1':
            exifList = imgProcess.getExif(srcName)
            destName = destfolder + "\\" + imgProcess.renameAccExif(srcName, exifList)
        else:
            destName = destfolder + "\\" + os.path.basename(srcName)

        srcList.append(srcName)
        destList.append(destName)
        if renameFlag.get() == '1':
            print("  " + str(filecounter + 1) + ': ' + os.path.basename(srcName) + " ==> " + os.path.basename(destName))
        else:
            print("  " + str(filecounter + 1) + ': ' + os.path.basename(srcName))
        filecounter += 1

    if filecounter > 0:
        print("\n" + str(filecounter) + " " + extName + "files found.")
        print("---------------------------------------------------------------------------------------")

        if renameFlag.get() == '1':
            dupItemIndex = []
            dupItem = []
            for index, element in enumerate(destList):
                if destList.count(element) > 1:
                    if element not in dupItem:
                        print("Conflicts:" + str(destList.count(element)) + " " + os.path.basename(element) + ": suffix _X will be added as follow:")
                        dupItem.append(element)
                    dupItemIndex.append(index)

            if len(dupItem) > 0:
                # print("结果如下：")
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

    return filecounter, srcList, destList

def cpRenImage(srcFolder, destfolder, extName):
    srcPathIncExtName = srcFolder + "\\*." + extName
    filecounter = 0
    for srcName in glob.glob(srcPathIncExtName):
        if renameFlag.get() == '1':
            destName = destfolder + "\\" + imgProcess.renameAccExif(srcName)
        else:
            destName = destfolder + "\\" + os.path.basename(srcName)

        if os.path.exists(destName):
            msgBoxReturn = messagebox.askquestion(title = "!!!", message = os.path.basename(destName) + " exits, overwrite？")
            if msgBoxReturn == "yes":
                if compressFlag.get() == '1':
                    imgProcess.renAndcompImg(srcName, destName)
                    print(str(filecounter + 1) + ': ' + os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed and compressed")
                else:
                    os.system("copy  " + srcName + " " + destName)
                    print(str(filecounter + 1) + ': ' + os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed")
                filecounter += 1
            else:
                print(str(filecounter + 1) + ': ' + os.path.basename(srcName) + " => " + os.path.basename(destName) + " : canceled")
        else:
            if compressFlag.get() == '1':
                imgProcess.renAndcompImg(srcName, destName)
                print(str(filecounter + 1) + ': ' + os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed and compressed")
            else:
                os.system("copy  " + srcName + " " + destName)
                print(str(filecounter + 1) + ': ' + os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed")
            filecounter += 1
    return filecounter

srcListJPG = []
destListJPG = []
srcListJPEG = []
destListJPEG = []
srcListPNG = []
destListPNG = []
def preperation():
    log_text.configure(state = "normal")
    log_text.delete('1.0', END)

    ### path
    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()
    # print("源文件夹 = " + srcPath)
    # print("目标文件夹 = " + destPath)
    # print("=======================================================================")

    if checkPath(srcPath, destPath):
        print("OK")
        print("---------------------------------------------------------------------------------------")

        if checkCheckButton():
            print("function checked: ok.")
            print("=======================================================================================")
            print("Preview:")
            ############### mainfunction ################
            sumJPG, srcList, destList = preview(srcPath, destPath, "jpg")

            srcListJPG.clear()
            destListJPG.clear()
            for item in srcList:
                srcListJPG.append(item)
            for item in destList:
                destListJPG.append(item)

            #sumJPEG, srcListJPEG, destListJPEG = preview(srcPath, destPath, "jpeg")
            #process_Button.configure(text = "执行操作", command = process)
        else:
            print("=======================================================================================")
            print("Abort 1!")
            pass
    else:
        print("=======================================================================================")
        print("Abort 2!")
        pass

    log_text.see(END)
    log_text.configure(state = "disable")

def process():
    log_text.configure(state = "normal")
    print("=======================================================================================")
    print("=======================================================================================")

    print("Start processing")

    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()
    if (os.path.exists(destPath) == False):
        if destPath == srcPath + "_OUTPUT":
            os.makedirs(destPath)
        else:
            msgBoxReturn = messagebox.askquestion(title = "Message", message = "Destination \n" + destPath + "\ndoesn't exist, create？")
            if msgBoxReturn == "yes":
                os.makedirs(destPath)
                print("  Create destination folder: " + destPath)
    print("---------------------------------------------------------------------------------------")

    process_Button.configure(state = "disable")
    #compress_checkbutton.configure(state = "normal")
    #rename_checkbutton.configure(state = "normal")

    # print(compressFlag.get())
    # print(srcListJPG)
    # print(destListJPG)

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

preperation_Button = ttk.Button(mainframe, text = "Preview", command = preperation)
preperation_Button.grid(row = 4, column = 2, sticky = (N, S), padx = 5, pady = 10)

process_Button = ttk.Button(mainframe, text = "Execute", command = process, state = "disable")
process_Button.grid(row = 5, column = 2, sticky = (N, S), padx = 5, pady = 5, rowspan = 3)

#################################################################################################################################
# row 7 -
#################################################################################################################################
# def breakProcess():
#     sys.exit("Stop")

# ttk.Button(mainframe, text = "中止操作", command = breakProcess).grid(row = 8, column = 2, sticky = N, padx = 5, pady = 0)
# ttk.Button(mainframe, text = "是").grid(row = 9, column = 2, sticky = N, padx = 5, pady = 0)
# ttk.Button(mainframe, text = "否").grid(row = 10, column = 2, sticky = N, padx = 5, pady = 0)
#ttk.Button(mainframe, text = "yes").grid(row = 9, column = 2, sticky = N, padx = 5, pady = 0)



#ttk.Label(mainframe, text = "Z.Kang").grid(row = 5, column = 2, sticky = (S, E), padx = 5, pady = 5)

# # for child in mainframe.winfo_children():
# #     child.grid_configure(padx = 5, pady = 5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

root.mainloop()


#pyinstaller --noconsole imgProcessGUI.py
