from PIL import Image, ImageFile
from os import listdir,mkdir,path
from os.path import isfile, join, splitext
import imageio
import cv2
import numpy as np

def resize_image(image_path,image_size):
    im = Image.open(image_path)
    new = im.resize((image_size,image_size), resample=3)
    return new


def generate_new_resolution(source_folder,image_size=('2K',2048)):
    dest_folder = '{}_{}'.format(source_folder,image_size[0])
    if not path.exists(dest_folder):
        try:
            mkdir(dest_folder)
        except OSError:
            print ("Creation of the directory %s failed" % dest_folder)
        else:
            print ("Successfully created the directory %s" % dest_folder)
    for f in listdir(source_folder):
        print(f)
        file_path = join(source_folder, f)
        if not file_path:
            continue
        outfile = join(dest_folder,f)
        if splitext(f)[1] == '.exr':
            image = imageio.imread(file_path,format='EXR-FI')
            res = cv2.resize(image, dsize=(image_size[1], image_size[1]), interpolation=cv2.INTER_CUBIC)
            imageio.imwrite(outfile,res,format='EXR-FI')
        elif splitext(f)[1] == '.jpg':
            new = resize_image(file_path,image_size[1])
            new.save(outfile,"JPEG")


source_folder = '/home/henri/Téléchargements/Brick_Rubble_rhlxZ_8K_3d_ms/textures'
generate_new_resolution(source_folder,('4K',4096))
generate_new_resolution(source_folder,('2K',2048))
generate_new_resolution(source_folder,('1K',1024))
