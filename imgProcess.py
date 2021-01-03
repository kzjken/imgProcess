import os
import time
from PIL import Image

#####################################################################################
# rename file according shot time and device
#####################################################################################
def renameAccExif(imageName):
    # a. read exif
    image = Image.open(imageName)
    dictExif = image.getexif()    
    #print("DateTimeOriginal:", dictExif.get(36867), ", Model:", dictExif.get(272))    
    DateTimeOriginal = str(dictExif.get(36867))
    CameraModel = str(dictExif.get(272))
    image.close()

    # b. new filename part 1: time    
    filenameRaw = ""
    if DateTimeOriginal != "None":
        filenameRaw = DateTimeOriginal
    else:
        fileModTime = time.localtime(os.stat(imageName).st_mtime)
        filenameRaw = time.strftime("%Y%m%d_%H%M%S", fileModTime)

    #print(filenameRaw)    

    filenameRaw = filenameRaw.replace(':','')
    filenameRaw = filenameRaw.replace(' ','_')

    # c. new filename part 2: device part
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
        img.save(dest, quality = quality, optimize = True, exif = exif_dict)
    else:
        img.save(dest, quality = quality, optimize = True)