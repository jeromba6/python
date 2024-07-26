#!/usr/bin/env python3

"""
Script rename images based on exif data
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from PIL import Image
from PIL.ExifTags import TAGS


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Adjust time in exif data of images')
    parser.add_argument('images', nargs='+', help='Image file(s)')
    parser.add_argument('-r', '--rename',
                        dest='rename', 
                        action='store_true',
                        default=False,
                        help='Rename images instead of makeing a copy (default: False)')
    parser.add_argument('-d', '--destination',
                        dest='destination', 
                        action='store',
                        default=None,
                        required=False,
                        help='Destination directory for renamed images (default: same as source)')
    parser.add_argument('-s', '--exif-source',
                        dest='source', 
                        action='store_true',
                        default=False,
                        help='Add exif source to filename (default: False)')
    parser.add_argument('-f', '--force',
                        dest='force', 
                        action='store_true',
                        default=False,
                        help='Perform the action (default: dry-run)')
    args = parser.parse_args()

    count = 0

    for image_path in args.images:
        if not os.path.exists(image_path):
            print(f'Image file not found: {image_path}')
            sys.exit(1)
        source_dir = os.path.dirname(image_path)
        source_ext = os.path.splitext(image_path)[1]
        if source_ext:
            destination_ext = source_ext.lower()

        exif_data = get_exif_data(image_path)
        if not exif_data:
            print('No exif data found in image')
            sys.exit(1)

        exif_source = ''
        if args.source:
            if exif_data[271] or exif_data[272]:
                exif_source = '-'
            if 271 in exif_data:
                exif_source += exif_data[271]
            if 272 in exif_data:
                exif_source += '_' + exif_data[272]

        exif_datetime = get_exif_datetime(exif_data)
        if not exif_datetime:
            print('No datetime found in exif data')
            sys.exit(1)

        if args.destination:
            destination_dir = args.destination
        else:
            destination_dir = source_dir
        new_filename = exif_datetime.strftime('%Y-%m-%d_%H.%M.%S') + exif_source + destination_ext
        destination_path = os.path.join(destination_dir, new_filename)

        if image_path == destination_path:
            print(f'Image {image_path} already has the correct name')
            continue

        file_name_count = 0
        while os.path.exists(destination_path):
            new_filename = exif_datetime.strftime('%Y-%m-%d_%H.%M.%S') + '-' + str(file_name_count) + destination_ext
            destination_path = os.path.join(destination_dir, new_filename)
            file_name_count += 1
        action = 'Renaming' if args.rename else 'Copying'
        if not args.force:
            action = 'Dry-run: ' + action
        print(f'{action} image {image_path} to {destination_path}')
        if args.force:
            if args.rename:
                os.rename(image_path, destination_path)
            else:
                os.copy(image_path, destination_path)
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


if __name__ == '__main__':
    main()
