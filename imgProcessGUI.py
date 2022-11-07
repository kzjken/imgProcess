from os import path
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

mainframe = ttk.Frame(root, padding = "20 3 12 12")
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
rename_checkbutton = ttk.Checkbutton(mainframe, text = "重命名", variable = renameFlag)
rename_checkbutton.grid(row = 2, column = 2, sticky = (W, E), padx = 5)

ttk.Label(mainframe, text = "1. 重命名照片为拍摄时间_拍摄设备").grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)

compressFlag = StringVar()
compressFlag.set(1)
compress_checkbutton = ttk.Checkbutton(mainframe, text = "压缩图像", variable = compressFlag)
compress_checkbutton.grid(row = 3, column = 2, sticky = (W, E), padx = 5)
ttk.Label(mainframe, text = "2. 使用Python PIL进行图像压缩").grid(row = 3, column = 1, sticky = W, padx = 5)

#################################################################################################################################
# row 4 - 20 log window
#################################################################################################################################
ttk.Label(mainframe, text = "日志输出:").grid(row = 4, column = 0, sticky = (N, E), padx = 5, pady = 10)

log_text = Text(mainframe, width = 90, height = 30, state = "disabled")
log_text.grid(row = 4, column = 1, sticky = (W, E), padx = 5, pady = 10, rowspan = 16)

logText_scrollbar = Scrollbar(mainframe, orient="vertical", command = log_text.yview)
logText_scrollbar.grid(row = 4, column = 1, sticky = (E, N, S), padx = 5, pady = 10, rowspan = 16)

log_text.configure(yscrollcommand = logText_scrollbar.set)

pl = PrintLogger(log_text)
sys.stdout = pl

#################################################################################################################################
# row 5 execute
#################################################################################################################################
def checkPath(srcFolder, destfolder):
    print("检查路径：")
    if srcFolder == "":
        #messagebox.showerror(title = "错误", message = "指定源文件路径无效，请重新选择！")
        print("  错误：指定源文件路径无效，请选择！")
        return False

    # check if source folder is empty
    if not os.listdir(srcFolder):
        #messagebox.showerror(title = "错误", message = "目标文件夹\n" + srcFolder + "\内没有文件！")
        print("  错误：指定源文件夹内没有文件，请重新选择！")
        return False
    else:
        if destfolder == "":
            #messagebox.showerror(title = "错误", message = "指定目标文件路径无效，请重新选择！")
            print("  错误：指定目标文件路径无效，请选择！")
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
    print("检查功能项：")
    #print(renameFlag.get() + compressFlag.get() + "   " + type(renameFlag.get()))

    if renameFlag.get() == '0' and compressFlag.get() == '0':
        print("  错误：请至少选择一个功能选项！")
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
            print("  " + os.path.basename(srcName) + " ==> " + os.path.basename(destName))
        else:
            print("  " + os.path.basename(srcName))
        filecounter += 1

    if filecounter > 0:
        print("\n找到" + str(filecounter) + "个" + extName + "文件")
        print("---------------------------------------------------------------------------------------")

        if renameFlag.get() == '1':
            dupItemIndex = []
            dupItem = []
            for index, element in enumerate(destList):
                if destList.count(element) > 1:
                    if element not in dupItem:
                        print("根据命名规则，目标文件" + os.path.basename(element) + "出现" + str(destList.count(element)) + "次，将增加数字后缀")
                        dupItem.append(element)
                    dupItemIndex.append(index)

            if len(dupItem) > 0:
                print("结果如下：")
                for item in dupItem:
                    suffix = 0
                    for index in dupItemIndex:
                        if destList[index] == item:
                            filename, file_extension = os.path.splitext(destList[index])
                            destList[index] = filename + '_' + str(suffix) + file_extension
                            print("  " + os.path.basename(destList[index]) + " ==> " + os.path.basename(destList[index]))
                            suffix += 1
        else:
            print("将对所有文件进行低损压缩。")

        process_Button.configure(state = "normal")
        #compress_checkbutton.configure(state = "disable")
        #rename_checkbutton.configure(state = "disable")

        print("---------------------------------------------------------------------------------------")
        print("继续操作，请点击“执行操作”按钮")

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
        print("路径正常")
        print("---------------------------------------------------------------------------------------")

        if checkCheckButton():
            print("功能项已选")
            print("=======================================================================================")
            print("预览：")
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
            print("中止1！")
            pass
    else:
        print("=======================================================================================")
        print("中止2！")
        pass

    log_text.see(END)
    log_text.configure(state = "disable")

def process():
    log_text.configure(state = "normal")
    print("=======================================================================================")
    print("=======================================================================================")

    print("开始处理")

    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()
    if (os.path.exists(destPath) == False):
        if destPath == srcPath + "_OUTPUT":
            os.makedirs(destPath)
        else:
            msgBoxReturn = messagebox.askquestion(title = "提示", message = "目标文件夹\n" + destPath + "\n不存在, 是否创建？")
            if msgBoxReturn == "yes":
                os.makedirs(destPath)
    print("  创建目标文件夹" + destPath)
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
            print(os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))
    else:
        for index, imageJPG in enumerate(srcListJPG):
            #imgProcess.renAndcompImg(imageJPG, destListJPG[index], 100)
            os.system("copy " + imageJPG + " " + destListJPG[index])
            print(os.path.basename(imageJPG) + " ==> " + os.path.basename(destListJPG[index]))

    print("=======================================================================================")
    print("END")

    log_text.see(END)
    log_text.configure(state = "disable")

preperation_Button = ttk.Button(mainframe, text = "预览", command = preperation)
preperation_Button.grid(row = 4, column = 2, sticky = (N, S), padx = 5, pady = 10)

process_Button = ttk.Button(mainframe, text = "执行操作", command = process, state = "disable")
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
