from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import os
import glob
import imgProcess
import sys

#################################################################################################################################
#------------------------------------------------------------- Globale ---------------------------------------------------------#
#################################################################################################################################
#defaultDest = True


#################################################################################################################################
#------------------------------------------------------------- rp stdout--------------------------------------------------------#
#################################################################################################################################
class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass

#################################################################################################################################
#------------------------------------------------------------- tkinter ---------------------------------------------------------#
#################################################################################################################################
root = Tk()
root.title("Image Conventer [Z.Kang]")

mainframe = ttk.Frame(root, padding = "4 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

#################################################################################################################################
# row 0 path
#################################################################################################################################
ttk.Label(mainframe, text = "源文件路径:").grid(row = 0, column = 0, sticky = E, padx = 5, pady = 5)

srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width = 50, textvariable = srcPath)
srcPath_entry.grid(row = 0, column = 1, sticky = (W, E), padx = 5, pady = 5)

def selectSrcDir():  
    filepath = os.path.normpath(filedialog.askdirectory())
    srcPath.set(filepath)
    #destPath.set(filepath + "/" + os.path.basename(filepath) + "_Output")
    if(os.path.exists(filepath)):
        destPath.set(filepath + "_OUTPUT")
ttk.Button(mainframe, text = "选择文件夹", command = selectSrcDir).grid(row = 0, column = 2, sticky = W, padx = 5, pady = 5)

#################################################################################################################################
# row 1 path
#################################################################################################################################
ttk.Label(mainframe, text = "目标文件路径:").grid(row = 1, column = 0, sticky = E, padx = 5, pady = 5)

destPath = StringVar()
destPath_entry = ttk.Entry(mainframe, width = 50, textvariable = destPath)
destPath_entry.grid(row = 1, column = 1, sticky = (W, E), padx = 5, pady = 5)

def modDestDir():  
    filepath = os.path.normpath(filedialog.askdirectory())
    destPath.set(filepath)    
ttk.Button(mainframe, text = "修改文件夹", command = modDestDir).grid(row = 1, column = 2, sticky = W, padx = 5, pady = 5)

#################################################################################################################################
# row 2 - 4
#################################################################################################################################
ttk.Label(mainframe, text = "功能选项:").grid(row = 2, column = 0, sticky = E, padx = 5, pady = 5)

renameFlag = StringVar()
renameFlag.set(1)
rename_checkbutton = ttk.Checkbutton(mainframe, text = "重命名", variable = renameFlag, state = "disable")
rename_checkbutton.grid(row = 2, column = 2, sticky = (W, E), padx = 5)

ttk.Label(mainframe, text = "1. 重命名照片为拍摄时间_拍摄设备 (基础功能，必选)").grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)

compressFlag = StringVar()
compressFlag.set(1)
compress_checkbutton = ttk.Checkbutton(mainframe, text = "压缩图像", variable = compressFlag)
compress_checkbutton.grid(row = 3, column = 2, sticky = (W, E), padx = 5)
ttk.Label(mainframe, text = "2. 使用Python PIL进行图像压缩").grid(row = 3, column = 1, sticky = W, padx = 5)

#################################################################################################################################
# row 5 log window
#################################################################################################################################
ttk.Label(mainframe, text = "日志输出:").grid(row = 5, column = 0, sticky = (N, E), padx = 5, pady = 10)

log_text = Text(mainframe, width = 90, height = 10, state = "disabled")
log_text.grid(row = 5, column = 1, sticky = (W, E), padx = 5, pady = 10)#, columnspan = 2) 

logText_scrollbar = Scrollbar(mainframe, orient="vertical", command = log_text.yview)
logText_scrollbar.grid(row = 5, column = 1, sticky = (E, N, S), padx = 5, pady = 10)

log_text.configure(yscrollcommand = logText_scrollbar.set)

pl = PrintLogger(log_text) 
sys.stdout = pl             

#################################################################################################################################
# row 5 execute
#################################################################################################################################
def checkPath(workPath):
    if(os.path.exists(workPath) == False):
        msgBoxReturn = messagebox.askquestion(title = "提示", message = "目标文件夹\n" + workPath + "\n不存在, 是否创建？")
        if msgBoxReturn == "yes":
            os.makedirs(workPath)
            # if os.path.isdir(workPath):
            #     os.makedirs(workPath)
            # else:
            #     messagebox.showerror(title = "错误", message = "指定目标路径\n" + workPath + "\n无效，请重新选择！")    

def cpRenImage(srcFolder, destfolder, extName):
    srcPathIncExtName = srcFolder + "\\*." + extName
    filecounter = 0
    for srcName in glob.glob(srcPathIncExtName):
        destName = destfolder + "\\" + imgProcess.renameAccExif(srcName)

        if os.path.exists(destName):
            msgBoxReturn = messagebox.askquestion(title = "警告", message = os.path.basename(destName) + "已存在，是否覆盖？")    
            if msgBoxReturn == "yes":
                if compressFlag.get() == '1':
                    imgProcess.renAndcompImg(srcName, destName)
                    print(os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed and compressed")
                else:
                    os.system("copy  " + srcName + " " + destName)      
                    print(os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed")
                filecounter += 1
            else:
                print(os.path.basename(srcName) + " => " + os.path.basename(destName) + " : canceled")
        else:
            if compressFlag.get() == '1':
                imgProcess.renAndcompImg(srcName, destName)
                print(os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed and compressed")
            else:
                os.system("copy  " + srcName + " " + destName)      
                print(os.path.basename(srcName) + " => " + os.path.basename(destName) + " : renamed")    
            filecounter += 1
    return filecounter

def renameAll(src, dest):
    jpgConter = cpRenImage(src, dest, "jpg")
    jpepConter = cpRenImage(src, dest, "jpeg")
    pngConter = cpRenImage(src, dest, "png")

    print("=======================================================================")
    if jpgConter > 0:
        print("processed " + str(jpgConter) + " jpg files") 
    if jpepConter > 0:
        print("processed " + str(jpepConter) + " jpeg files")
    if pngConter > 0:
        print("processed " + str(pngConter) + " png files")

def process():  
    # print(renameFlag.get())
    # print(compressFlag.get())    
    log_text.configure(state = "normal")

    log_text.delete('1.0', END)    
 
    ### path
    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()

    checkPath(srcPath)
    if destPath != srcPath + "_Output":
        checkPath(destPath)
    else:
        if (os.path.exists(destPath) == False):
            os.makedirs(destPath)

    # check if source folder is empty
    if os.listdir(srcPath) == False:
        messagebox.showerror(title = "错误", message = "目标文件夹\n" + srcPath + "\内没有文件！")    

    renameAll(srcPath, destPath)

    # if compressFlag.get() == '1':
    #     renAndcompImg(destPath) 

    log_text.configure(state = "disable")

ttk.Button(mainframe, text = "执行操作", command = process).grid(row = 5, column = 2, sticky = N, padx = 5, pady = 10)

#ttk.Label(mainframe, text = "Z.Kang").grid(row = 5, column = 2, sticky = (S, E), padx = 5, pady = 5)

# # for child in mainframe.winfo_children(): 
# #     child.grid_configure(padx = 5, pady = 5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

root.mainloop()


#pyinstaller -F imgProcessGUI.py
