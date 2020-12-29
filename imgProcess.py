import os
import time
from PIL import Image

#####################################################################################
# rename file according shot time and device
#####################################################################################
def renameAccExif(jpgFile):
    # a. read exif
    image = Image.open(jpgFile)
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
        fileModTime = time.localtime(os.stat(jpgFile).st_mtime)
        filenameRaw = time.strftime("%Y%m%d_%H%M%S", fileModTime)

    #print(filenameRaw)    

    filenameRaw = filenameRaw.replace(':','')
    filenameRaw = filenameRaw.replace(' ','_')

    # c. new filename part 2: device part
    if CameraModel != "None":
        filenameRaw = filenameRaw + "_" + CameraModel
    filenameRaw = filenameRaw.replace(' ','')
    
    filenameRaw += ".jpg"
    return filenameRaw
