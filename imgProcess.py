import os
import time
from PIL import Image
# debug only
# import glob

#####################################################################################
# getExif via PIL
#####################################################################################
def getExif(imageName):
    listExif = []
    image = Image.open(imageName)
    dictExif = image.getexif()
    # print(dictExif)
    # DateTimeOriginal = str(dictExif.get(36867))
    DateTimeOriginal = str(dictExif.get(306))
    CameraModel = str(dictExif.get(272))
    Aperture = str(dictExif.get(33437))
    FocalLength = str(dictExif.get(41989))
    ShutterSpd = str(dictExif.get(33434))

    listExif.append(DateTimeOriginal)
    listExif.append(CameraModel)
    listExif.append(Aperture)
    listExif.append(FocalLength)
    listExif.append(ShutterSpd)
    image.close()

    return listExif

#####################################################################################
# rename file according shot time and device
#####################################################################################
def renameAccExif(imageName, listEXIF):
    DateTimeOriginal = listEXIF[0]
    CameraModel = listEXIF[1]

    # new filename part 1: time
    filenameRaw = ""
    if DateTimeOriginal != "None":
        filenameRaw = DateTimeOriginal
    else:
        fileModTime = time.localtime(os.stat(imageName).st_mtime)
        filenameRaw = time.strftime("%Y%m%d_%H%M%S", fileModTime)

    #print(filenameRaw)

    filenameRaw = filenameRaw.replace(':','')
    filenameRaw = filenameRaw.replace(' ','_')

    # new filename part 2: device part
    if CameraModel != "None":
        filenameRaw = filenameRaw + "_" + CameraModel
    filenameRaw = filenameRaw.replace(' ','')

    filename, file_extension = os.path.splitext(imageName)
    filenameRaw += file_extension

    return filenameRaw

#####################################################################################
# rename and compressed image
#####################################################################################
def renAndcompImg(src, dest, quality):
    img = Image.open(src)
    if 'exif' in img.info.keys():
        exif_dict = img.info["exif"]
        if os.path.exists(dest):
            print('file exists!')
        else:
            img.save(dest, quality = quality, optimize = True, exif = exif_dict)
    else:
        if not os.path.exists(dest):
            img.save(dest, quality = quality, optimize = True)

# #####################################################################################
# # debug only
# #####################################################################################
# renameFlag = 1
# def preview(srcFolder, destfolder, extName):
#     srcPathIncExtName = srcFolder + "\\*." + extName
#     filecounter = 0
#     srcList = []
#     destList = []
#     for srcName in glob.glob(srcPathIncExtName):
#         # if renameFlag.get() == '1':
#         if renameFlag:
#             # exifList = imgProcess.getExif(srcName)
#             exifList = getExif(srcName)
#             # destName = destfolder + "\\" + imgProcess.renameAccExif(srcName, exifList)
#             destName = destfolder + "\\" + renameAccExif(srcName, exifList)
#         else:
#             destName = destfolder + "\\" + os.path.basename(srcName)

#         srcList.append(srcName)
#         destList.append(destName)
#         # if renameFlag.get() == '1':
#         if renameFlag:
#             print("  " + str(filecounter + 1) + ': ' + os.path.basename(srcName) + " ==> " + os.path.basename(destName))
#         else:
#             print("  " + str(filecounter + 1) + ': ' + os.path.basename(srcName))
#         filecounter += 1

#     if filecounter > 0:
#         print("\n找到" + str(filecounter) + "个" + extName + "文件")
#         print("---------------------------------------------------------------------------------------")

#         # if renameFlag.get() == '1':
#         if renameFlag:
#             dupItemIndex = []
#             dupItem = []
#             for index, element in enumerate(destList):
#                 if destList.count(element) > 1:
#                     if element not in dupItem:
#                         print("根据命名规则，目标文件" + os.path.basename(element) + "出现" + str(destList.count(element)) + "次，将增加数字后缀")
#                         dupItem.append(element)
#                     dupItemIndex.append(index)

#             if len(dupItem) > 0:
#                 print("结果如下：")
#                 for item in dupItem:
#                     suffix = 0
#                     for index in dupItemIndex:
#                         if destList[index] == item:
#                             filename, file_extension = os.path.splitext(destList[index])
#                             destList[index] = filename + '_' + str(suffix) + file_extension
#                             print("  " + os.path.basename(destList[index]) + " ==> " + os.path.basename(destList[index]))
#                             suffix += 1
#         else:
#             print("将对所有文件进行低损压缩。")

#         # process_Button.configure(state = "normal")
#         #compress_checkbutton.configure(state = "disable")
#         #rename_checkbutton.configure(state = "disable")

#         print("---------------------------------------------------------------------------------------")
#         print("继续操作，请点击“执行操作”按钮")

#     return filecounter, srcList, destList

# def main():
#     srcPath = r'Z:\Fotos\手机\7. X8\Snapseed'
#     destPath = r'Z:\Fotos\手机\7. X8\Snapseed_OPT'
#     print(srcPath)
#     print(destPath)
#     sumJPG, srcList, destList = preview(srcPath, destPath, "jpeg")
#     # for idx, item in enumerate(srcList):
#     #     print(str(idx) + ': ' + item + ' ==> ' + destList[idx])

# if __name__ == "__main__":
#     main()