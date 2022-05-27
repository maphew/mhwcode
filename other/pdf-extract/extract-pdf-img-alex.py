#!/usr/bin/env python3
#
# Adapted from https://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python
# by https://stackoverflow.com/users/3209908/alex-paramonov
#
import os
import sys
from pathlib import Path

# here = r"C:\Users\Matt\code\mhwcode\other\pdf-extract"
here = Path(__file__).parent.absolute()
print(here)
src = r"C:\Users\Matt\Downloads"

pdf_files = list(Path(src).glob("Scan*.pdf"))
# print(pdf_files)s


try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from PIL import Image
from PyPDF2 import PdfFileReader, generic
import zlib


def get_color_mode(obj):

    try:
        cspace = obj['/ColorSpace']
    except KeyError:
        return None

    if cspace == '/DeviceRGB':
        return "RGB"
    elif cspace == '/DeviceCMYK':
        return "CMYK"
    elif cspace == '/DeviceGray':
        return "P"

    if isinstance(cspace, generic.ArrayObject) and cspace[0] == '/ICCBased':
        color_map = obj['/ColorSpace'][1].getObject()['/N']
        if color_map == 1:
            return "P"
        elif color_map == 3:
            return "RGB"
        elif color_map == 4:
            return "CMYK"


def get_object_images(x_obj):
    images = []
    for obj_name in x_obj:
        sub_obj = x_obj[obj_name]

        if '/Resources' in sub_obj and '/XObject' in sub_obj['/Resources']:
            images += get_object_images(sub_obj['/Resources']['/XObject'].getObject())

        elif sub_obj['/Subtype'] == '/Image':
            zlib_compressed = '/FlateDecode' in sub_obj.get('/Filter', '')
            if zlib_compressed:
               sub_obj._data = zlib.decompress(sub_obj._data)

            images.append((
                get_color_mode(sub_obj),
                (sub_obj['/Width'], sub_obj['/Height']),
                sub_obj._data
            ))

    return images


def get_pdf_images(pdf_fp):
    images = []
    try:
        pdf_in = PdfFileReader(open(pdf_fp, "rb"))
    except:
        return images

    for p_n in range(pdf_in.numPages):

        page = pdf_in.getPage(p_n)

        try:
            page_x_obj = page['/Resources']['/XObject'].getObject()
        except KeyError:
            continue

        images += get_object_images(page_x_obj)

    return images


def extract_images_from(pdf_fp):
    count = 0
    for image in get_pdf_images(pdf_fp):
        (mode, size, data) = image
        try:
            img = Image.open(StringIO(data))
            count += 1
        except Exception as e:
            print ("Failed to read image with PIL: {}".format(e))
            continue
        # Do whatever you want with the image
        img.save(f'out/{pdf_fp.name}_{count}.{img.format}')
        print(f'out/{pdf_fp.name}_{count}.{img.format}')

if __name__ == "__main__":

    # if 'SPYDER_ENCODING' or 'PYZO_PREFIX' in os.environ.keys():
    #     pdf_fp = r'C:\users\Matt\Downloads\Scanned from a Xerox Multifunction Printer(1).pdf'
    #     here = r'C:\Users\Matt\code\mhwcode\other\pdf-extract'
    # else:
    #     pdf_fp = sys.argv[1]
    #     here = sys.argv[0]

    if not os.path.exists('out'):
        os.makedirs('out')

    for pdf in pdf_files:
        print(pdf)
        extract_images_from(pdf)


