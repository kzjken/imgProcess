import os
import time
from PIL import Image
import imagehash

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
def format_index(idx, list_length):
    width = max(1, len(str(list_length - 1)))
    return f"{idx:0{width}d}"

def renameAccExif(imageName, listEXIF, structure, listLength, index=1):
    """
    Generate a new filename based on EXIF info and user-selected structure.
    structure: list like ['index', 'date', 'time', 'camera', 'originalname', 'hash']
    """
    # import hashlib

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

    # # Calculate hash
    # def get_file_md5(path):
    #     hash_md5 = hashlib.md5()
    #     try:
    #         with open(path, "rb") as f:
    #             for chunk in iter(lambda: f.read(4096), b""):
    #                 hash_md5.update(chunk)
    #         return hash_md5.hexdigest()[:8]
    #     except Exception as e:
    #         print(f"Error calculating hash for {path}: {e}")
    #         return "00000000"

    def get_image_phash(file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with Image.open(file_path) as img:
                phash = imagehash.phash(img)
                return str(phash)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            # send2trash(file_path)
            return None

    for key in structure:
        if key == 'foldername':
            folder_name = os.path.basename(os.path.dirname(imageName))
            parts.append(folder_name.replace(' ', ''))
        elif key == 'index':
            parts.append(str(format_index(index, listLength)))
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
            parts.append(get_image_phash(imageName))

    newname = '_'.join(parts) + file_extension
    return newname.replace('\x00', '')

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