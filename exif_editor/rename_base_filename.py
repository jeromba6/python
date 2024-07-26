#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rename files in a directory with a timestamp in the filename YYYYMMDD_HHMMSS to YYYY-MM-DD_HH.MM.SS.ext
"""

import os
import re
import argparse
import datetime
import ffmpeg

def main():
    parser = argparse.ArgumentParser(description='Rename files in a directory with a timestamp in the filename YYYYMMDD_HHMMSS to YYYY-MM-DD_HH.MM.SS.ext')
    parser.add_argument('filelist', help='File list to rename', nargs='+')
    parser.add_argument('-f', '--force',
                        dest='force', 
                        action='store_true',
                        default=False,
                        help='Make changes otherwise it\'s a dry-run (default: False)')
    args = parser.parse_args()  


    for filename_full in args.filelist:
        if os.path.isdir(filename_full):
            print(f'{filename_full} is a directory, so skipping it.')
            continue
        directory = os.path.dirname(filename_full)
        filename = os.path.basename(filename_full)
        file_ext = os.path.splitext(filename)[1].lower()
        if re.search(r'\d{8}_\d{6}', filename):
            timestamp = re.search(r'(\d{8}_\d{6})', filename).group(1)
            recorded = re.sub(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', r'\1-\2-\3T\4.\5.\6', timestamp)
        elif re.search(r'\d{4}-\d{2}-\d{2}_\d{2}.\d{2}.\d{2}', filename):
            recorded = filename.replace('_', 'T').strip(file_ext)
        else:
            print(f'{filename} does not match the pattern, so trying to get metadata')
            metadata = get_metadata(filename_full)
            recorded = metadata.get('recording_time', 'N/A').split('.')[0]
        if recorded == 'N/A':
            print(f'No recording time found for {filename}')
            continue
        recorded = recorded.replace(':', '.')
        new_filename = re.sub(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', r'\1-\2-\3T\4.\5.\6', recorded)
        new_filename = os.path.join(directory, new_filename + file_ext)
        if filename == os.path.basename(new_filename):
            print(f'{filename} is already in the correct format')
        else:
            print(f'{filename} -> {new_filename}')
            if args.force:
                os.rename(os.path.join(directory, filename), new_filename)


            
def get_metadata(file_path):
    """
    Get metadata from mp4 file
    """
    metadata = {}
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})
        tags = format_info.get('tags', {})
        recording_time = tags.get('creation_time', 'N/A')
        metadata['recording_time'] = recording_time
    except ffmpeg.Error as e:
        metadata['recording_time'] = 'N/A'
        print(f'Error extracting recording time: {e}', file=sys.stderr)
    return metadata

            
            


if __name__ == '__main__':
    main()
