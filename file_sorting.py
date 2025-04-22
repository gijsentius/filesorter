"""File sorter module.

This module provides functionality to sort large ammount of files
from a given root directory. The files will be sorted on modification
date.
"""

__version__ = '0.1'
__author__ = 'Gijs Entius'

import os
import shutil
import re 
from shutil import SameFileError
from datetime import datetime
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
import time


register_heif_opener()

SUPPORTED_EXTENSIONS = ["jpg", "jpeg", "png", "heic", "mov", "avi", "mp4"]


class FileDate():
    """Datastructure for handling file dates

    """
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}"

    def date_tuple(self):
        return (self.year, self.month, self.day)

    def date_epoch(self):
        return time.mktime(time.strptime(str(self), "%Y-%m-%d"))


class FileSorter():
    '''Class to sort files

    This class is used to sort files in various ways
    Example of the usage:

    '''
    def __init__(self):
        self.base_dir = ""
        self.move = False

    def _convert_timestamp(self, timestamp):
        '''Function to convert a unix timestamp to yyyy-mm-dd
        '''
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    def _get_modified_date(self, file):
        timestamp = self._convert_timestamp(os.stat(file).st_mtime)
        time_array = timestamp.split("-")
        return FileDate(time_array[0], time_array[1], time_array[2])

    def _get_date_from_filename(self, file):
        filename = file.name
        for extension in SUPPORTED_EXTENSIONS:
            match = re.search("^(IMG|WP|MOV|VID){0,1}[-|_]{0,1}([0-9]{8}){1}(_|-){1}.*" + extension + "$", filename)
            if match:
                return FileDate(match.group(2)[:4], match.group(2)[4:6], match.group(2)[6:8])

    def _get_date_from_exif(self, file):
        try:
            img = Image.open(file.path)
            img_exif = img.getexif()
            for k, v in img_exif.items():
                if k in ExifTags.TAGS and Image.ExifTags.TAGS[k] == "DateTime":
                    img_datetime = v.split(" ")[0].split(":")
                    return FileDate(img_datetime[0], img_datetime[1], img_datetime[2])
        except:
            pass

    def _update_mod_date(self, file, file_date):
        os.utime(file.path, (file_date.date_epoch(), file_date.date_epoch()))

    def _adjust_file_date(self, file):
        exif_date = self._get_date_from_exif(file)
        name_date = self._get_date_from_filename(file)
        mod_date = self._get_modified_date(file)

        if exif_date is not None:
            if str(exif_date) != str(mod_date):
                self._update_mod_date(file, exif_date)
            return exif_date.date_tuple()
        elif name_date is not None:
            if str(name_date) != str(mod_date):
                self._update_mod_date(file, name_date)
            return name_date.date_tuple()
        else:
            return mod_date.date_tuple()

    def _copy_file(self, file):
        '''Function to copy a file
        '''
        if file.name.split(".")[1].lower() not in SUPPORTED_EXTENSIONS:
            return

        year, month, day = self._adjust_file_date(file)

        if int(year) < 1901:
            year = "0001"
            month = "01"
            day = "01"

        os.makedirs(f"{self.base_dir}{year}/{month}/{day}", exist_ok=True)

        try:
            if self.move:
                shutil.move(file, f"{self.base_dir}{year}/{month}/{day}/{file.name}")
            else:
                shutil.copy2(file, f"{self.base_dir}{year}/{month}/{day}/{file.name}")
        except SameFileError:
            pass

    def _sort_files_recursive(self, from_dir):
        '''Function to sort files recursively
        '''
        if os.path.isdir(from_dir):
            for item in os.scandir(from_dir):
                if item.is_dir():
                    self._sort_files_recursive(item.path)
                else:
                    self._copy_file(item)
            if sum(1 for _ in os.scandir(from_dir)) == 0 and self.remove_empty_dir:
                print(f"Remove empty folder {from_dir}")
                os.rmdir(from_dir)
        else:
            print(f"{from_dir} is not a directory")

    def _check_base_dir(self, dir):
        if dir[-1] != "/":
            return dir + "/"
        else:
            return dir

    def sort_files(self, from_dir, to_dir="", extension="", move=False, remove_empty_dir=True):
        '''Function to sort file on month of modification
        '''
        if to_dir == "":
            self.base_dir = self._check_base_dir(os.getcwd())
        else:
            self.base_dir = self._check_base_dir(to_dir)
        self.move = move
        self.remove_empty_dir = remove_empty_dir

        print(f"Organizing files from {from_dir} to {self.base_dir} using {'move' if move else 'copy'}")
        self._sort_files_recursive(from_dir)
