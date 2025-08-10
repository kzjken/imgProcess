import os
import time
import glob
from PIL import Image
import matplotlib.pyplot as plt

#####################################################################################
# Get EXIF info using PIL
#####################################################################################
def getExif(imageName: str) -> list:
    """
    Extract EXIF information from an image file.
    Returns a list: [DateTimeOriginal, CameraModel, Aperture, FocalLength, ShutterSpd]
    If EXIF is missing, returns ["None"] * 5.
    """
    listExif = []
    try:
        with Image.open(imageName) as image:
            dictExif = image._getexif() or {}
            DateTimeOriginal = str(dictExif.get(36867, "None"))
            CameraModel = str(dictExif.get(272, "None"))
            Aperture = str(dictExif.get(33437, "None"))
            FocalLength = str(dictExif.get(41989, "None"))
            ShutterSpd = str(dictExif.get(33434, "None"))
            listExif = [DateTimeOriginal, CameraModel, Aperture, FocalLength, ShutterSpd]
    except Exception as e:
        print(f"Error reading EXIF from {imageName}: {e}")
        listExif = ["None"] * 5
    return listExif

#####################################################################################
# Rename file according to EXIF and user structure
#####################################################################################
def renameAccExif(imageName, listEXIF, structure, index=1):
    """
    Generate a new filename based on EXIF info and user-selected structure.
    structure: list like ['index', 'date', 'time', 'camera', 'originalname', 'hash']
    """
    import hashlib

    DateTimeOriginal = listEXIF[0]
    CameraModel = listEXIF[1]
    filename, file_extension = os.path.splitext(os.path.basename(imageName))
    parts = []

    # Parse date and time
    if DateTimeOriginal != "None" and len(DateTimeOriginal) >= 10:
        date_part = DateTimeOriginal[:10].replace(':', '')
        time_part = DateTimeOriginal[11:].replace(':', '')
    else:
        fileModTime = time.localtime(os.stat(imageName).st_mtime)
        date_part = time.strftime("%Y%m%d", fileModTime)
        time_part = time.strftime("%H%M%S", fileModTime)

    # Calculate hash
    def get_file_md5(path):
        hash_md5 = hashlib.md5()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()[:8]
        except Exception as e:
            print(f"Error calculating hash for {path}: {e}")
            return "00000000"

    for key in structure:
        if key == 'index':
            parts.append(str(index))
        elif key == 'date':
            parts.append(date_part)
        elif key == 'time':
            parts.append(time_part)
        elif key == 'camera':
            if CameraModel != "None":
                parts.append(CameraModel.replace(' ', ''))
        elif key == 'originalname':
            parts.append(filename)
        elif key == 'hash':
            parts.append(get_file_md5(imageName))

    newname = '_'.join(parts) + file_extension
    return newname

#####################################################################################
# Rename and compress image
#####################################################################################
def renAndcompImg(src, dest, quality):
    """
    Save image to dest with given quality, keeping EXIF if present.
    If dest exists, do nothing.
    """
    try:
        img = Image.open(src)
        if os.path.exists(dest):
            print(f'File exists: {dest}')
            return
        save_kwargs = {'quality': quality, 'optimize': True}
        if 'exif' in img.info:
            save_kwargs['exif'] = img.info['exif']
        img.save(dest, **save_kwargs)
    except Exception as e:
        print(f"Error processing {src} -> {dest}: {e}")

def plot_focal_length_distribution(src_folder):
    """
    Scan all jpg images in src_folder, extract focal length, and plot a pie chart.
    """
    srcPathIncExtName = os.path.join(src_folder, "*.jpg")
    listImage = glob.glob(srcPathIncExtName)
    imageCount = len(listImage)
    if imageCount == 0:
        print(f"  Error: no images found in {src_folder}, please reselect!")
        print("="*80)
        return

    print(f"  {imageCount} images found in {src_folder}")
    print("="*80)

    listAllEXIF = []
    for srcName in listImage:
        exifList = getExif(srcName)
        exifList.insert(0, os.path.basename(srcName))
        listAllEXIF.append(exifList)

    focalLengthList = []
    for item in listAllEXIF:
        focalLengthList.append(item[4])
    noneFlCount = focalLengthList.count("None")
    focalLengthList = [float(x) for x in focalLengthList if x != "None"]

    # 统计各焦距出现次数
    from collections import Counter
    fl_counter = Counter(focalLengthList)
    labels = []
    values = []
    for fl, count in sorted(fl_counter.items()):
        labels.append(f"{fl}mm = {count}")
        values.append(count)

    if not values:
        print("No valid focal length data found.")
        return

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Focal Length Distribution")
    plt.show()