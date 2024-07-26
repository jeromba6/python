#!/usr/bin/env python3

"""
Script to adjust time in exif data of images
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from PIL import Image
from PIL.ExifTags import TAGS
# import piexif


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Filter images by exif data')
    parser.add_argument('filter', help='Filter to select images')
    parser.add_argument('images', nargs='+', help='Image file(s)')
    parser.add_argument('-s', '--subtract', dest='substract', default=False, action='store_true', help='Subtract time from exif data (default: add)')
    args = parser.parse_args()
    count = 0

    for image_path in args.images:
        if not os.path.exists(image_path):
            print(f'Image file not found: {image_path}')
            sys.exit(1)

        # print(f'Processing image: {image_path}')

        exif_data = get_exif_data(image_path)
        if not exif_data:
            print(f'No exif data found in image: {image_path}')
            sys.exit(1)
        if 271 in exif_data:
            print(f'Exif data: {exif_data[271]}')
        else:
            print(f'File {image_path} has no exif data')
            print(f'exif_data: {exif_data}')
            exit()
        
        if args.filter in exif_data[271]:
            print(f'Filter found in image so deleting image: {image_path}')
            os.remove(image_path)

        count += 1
    print(f'{count} images processed')


def get_exif_data(image_path):
    """
    Get exif data from image
    """
    image = Image.open(image_path)
    exif_data = image._getexif()
    return exif_data


def get_exif_datetime(exif_data):
    """
    Get datetime from exif data
    """
    for tag, value in exif_data.items():
        if TAGS.get(tag) == 'DateTimeOriginal':
            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')


def set_exif_datetime(image_path, new_datetime):
    """
    Set datetime in exif data
    """
    image = Image.open(image_path)
    exif_dict = piexif.load(image.info['exif'])

    new_datetime_str = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_datetime_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime_str

    exif_bytes = piexif.dump(exif_dict)
    image.save(image_path, exif=exif_bytes)


if __name__ == '__main__':
    main()
