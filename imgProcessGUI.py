from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import imgProcess

# def calculate(*args):
#     try:
#         value = float(feet.get())
#         meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
#     except ValueError:
#         pass

root = Tk()
root.title("Photo Conventer [Z.Kang]")

mainframe = ttk.Frame(root, padding = "4 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

############################################## row 0 ########################################################
ttk.Label(mainframe, text = "源文件路径:").grid(row = 0, column = 0, sticky = E, padx = 5, pady = 5)

srcPath = StringVar()
srcPath_entry = ttk.Entry(mainframe, width = 50, textvariable = srcPath)
srcPath_entry.grid(row = 0, column = 1, sticky = (W, E), padx = 5, pady = 5)

def selectSrcDir():  
    filepath = filedialog.askdirectory()     
    srcPath.set(filepath)
    #destPath.set(filepath + "/" + os.path.basename(filepath) + "_Output")
    if(os.path.exists(filepath)):
        destPath.set(filepath + "_Output")
ttk.Button(mainframe, text = "选择文件夹", command = selectSrcDir).grid(row = 0, column = 2, sticky = W, padx = 5, pady = 5)

############################################## row 1 ########################################################
ttk.Label(mainframe, text = "目标文件路径:").grid(row = 1, column = 0, sticky = E, padx = 5, pady = 5)

destPath = StringVar()
destPath_entry = ttk.Entry(mainframe, width = 50, textvariable = destPath)
destPath_entry.grid(row = 1, column = 1, sticky = (W, E), padx = 5, pady = 5)

def modDestDir():  
    filepath = filedialog.askdirectory()     
    destPath.set(filepath)
ttk.Button(mainframe, text = "修改文件夹", command = modDestDir).grid(row = 1, column = 2, sticky = W, padx = 5, pady = 5)

############################################## row 2 ########################################################
ttk.Label(mainframe, text = "功能选项:").grid(row = 2, column = 0, sticky = E, padx = 5, pady = 5)

renameFlag = StringVar()
renameFlag.set(1)
rename_checkbutton = ttk.Checkbutton(mainframe, text = "重命名", variable = renameFlag)
rename_checkbutton.grid(row = 2, column = 2, sticky = (W, E), padx = 5)

ttk.Label(mainframe, text = "1. 重命名照片为拍摄时间_拍摄设备").grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)

compressFlag = StringVar()
compress_checkbutton = ttk.Checkbutton(mainframe, text = "压缩图像", variable = compressFlag)
compress_checkbutton.grid(row = 3, column = 2, sticky = (W, E), padx = 5)
ttk.Label(mainframe, text = "2. 使用Python PIL进行图像压缩").grid(row = 3, column = 1, sticky = W, padx = 5)

############################################## row 4 ########################################################



############################################## row 5 ########################################################
ttk.Label(mainframe, text = "日志输出:").grid(row = 5, column = 0, sticky = (N, E), padx = 5, pady = 10)

log_text = Text(mainframe, width = 60, height = 4, state = "disabled")
log_text.grid(row = 5, column = 1, sticky = (W, E), padx = 5, pady = 10)#, columnspan = 2) 

def process():  
    # print(renameFlag.get())
    # print(compressFlag.get())    
    srcPath = srcPath_entry.get()
    destPath = destPath_entry.get()
    log_text.configure(state = "normal")
    log_text.insert('end', "rename = " + renameFlag.get() + "\n")
    log_text.insert('end', "compress = " + compressFlag.get() + "\n")    
    log_text.insert('end', "srcPath = " + srcPath + "\n")    
    log_text.insert('end', "destPath = " + destPath + "\n")    
    log_text.configure(state = "disable")

    if(os.path.exists(destPath)):
        os.makedirs(destPath)

    print(imgProcess.checkSrcFolder(srcPath))
    print(imgProcess.findJpg(srcPath))


ttk.Button(mainframe, text = "执行操作", command = process).grid(row = 5, column = 2, sticky = (S, N), padx = 5, pady = 10)

#ttk.Label(mainframe, text = "Z.Kang").grid(row = 5, column = 2, sticky = (S, E), padx = 5, pady = 5)

# # for child in mainframe.winfo_children(): 
# #     child.grid_configure(padx = 5, pady = 5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

root.mainloop()