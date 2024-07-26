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
import piexif


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Adjust time in exif data of images')
    parser.add_argument('time', help='Time to adjust in format [DAYS:]HH:MM:SS')
    parser.add_argument('images', nargs='+', help='Image file(s)')
    parser.add_argument('-s', '--subtract', dest='substract', default=False, action='store_true', help='Subtract time from exif data (default: add)')
    parser.add_argument('-m', '--make', dest='make', default=None, help='Filter images by exif make of camera data')
    parser.add_argument('-t', '--type', dest='type', default=None, help='Filter images by exif type of camera data')
    parser.add_argument('-d', '--dry-run', dest='dry_run', default=False, action='store_true' , help='Dry run (default: False)')
    args = parser.parse_args()

    time = args.time.split(':')
    if len(time) == 4:
        time = [int(time[0]) * 24 + int(time[1]), time[2], time[3]]
    if len(time) != 3:
        print('Invalid time format. Use [DAYS:]HH:MM:SS')
        sys.exit(1)

    delta_time = timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
    if args.substract:
        delta_time = -delta_time

    count = 0

    print(f'Time to adjust: {delta_time}')
    print()

    for image_path in args.images:
        if not os.path.exists(image_path):
            print(f'Image file not found: {image_path}')
            sys.exit(1)

        print(f'Processing image: {image_path}')

        exif_data = get_exif_data(image_path)
        if not exif_data:
            print('No exif data found in image')
            sys.exit(1)

        exif_datetime = get_exif_datetime(exif_data)
        if not exif_datetime:
            print('No datetime found in exif data')
            sys.exit(1)

        if args.make:
            make = exif_data.get(271)
            if make != args.make:
                print(f'Camera make does not match: {make}')
                continue

        if args.type:
            type = exif_data.get(272)
            if type != args.type:
                print(f'Camera type does not match: {type}')
                continue

        new_datetime = exif_datetime + delta_time

        print(f'Original datetime: {exif_datetime}')
        print(f'New datetime: {new_datetime}')

        if not args.dry_run:
            set_exif_datetime(image_path, new_datetime)
            print('Time adjusted successfully')
        print()

        count += 1
    print(f'{count} images processed')
    if args.dry_run:
        print('Dry run: no changes were made')


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
