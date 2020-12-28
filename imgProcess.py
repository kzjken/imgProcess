import glob
import datetime
import os
import time
from PIL import Image


#####################################################################################
# check if srcFolder is empty
#####################################################################################
def checkSrcFolder(srcFolder):
    if not os.listdir(srcFolder):
        return 0
    else:
        return 1

#####################################################################################
# find jpeg
#####################################################################################
def findJpeg(srcFolder):
    srcPathIncJpeg = srcFolder + "\\*.jpeg"
    filecounter = 0
    for filepath in glob.glob(srcPathIncJpeg):
        prePath, ext = os.path.splitext(filepath)
        #os.rename(filepath, prePath + ".jpg")
        filecounter += 1
    #print(filecounter, "jpeg ==> jpg, done")
    return filecounter

#####################################################################################
# 3. save original jpg filepathes in a list
#####################################################################################
# srcPathIncJpg = srcFolder + "\\*.jpg"
# orgJpgList = glob.glob(srcPathIncJpg)
def findJpg(srcFolder):
    srcPathIncJpg = srcFolder + "\\*.jpg"
    jpgList = glob.glob(srcPathIncJpg)
    return len(jpgList)
        
