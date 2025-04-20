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


class FileSorter():
    '''Class to sort files

    This class is used to sort files in various ways
    Example of the usage:

    '''
    def __init__(self):
        self.base_dir = ""
        self.photo_mode = True

    def _convert_timestamp(self, timestamp):
        '''Function to convert a unix timestamp to yyyy-mm-dd
        '''
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    def _copy_file(self, file):
        '''Function to copy a file
        '''
        filename = file.name
        match = re.search("^(IMG_){0,1}([0-9]{8}){1}_.*jpg$", filename)

        if match:
            year = match.group(2)[:4]
            month = match.group(2)[4:6]
            day = match.group(2)[6:8]
        elif not self.photo_mode:
            timestamp = self._convert_timestamp(os.stat(file).st_mtime)
            time_array = timestamp.split("-")
            year = time_array[0]
            month = time_array[1]
            day = time_array[2]
        else:
            return

        os.makedirs(f"{self.base_dir}{year}/{month}/{day}", exist_ok=True)

        try:
            shutil.copy2(file, f"{self.base_dir}{year}/{month}/{day}/{filename}")
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
        else:
            print(from_dir, " is not a directory")

    def _check_base_dir(self, dir):
        if dir[-1] != "/":
            return dir + "/"
        else:
            return dir

    def sort_files_on_month(self, from_dir, to_dir=""):
        '''Function to sort file on month of modification
        '''
        if to_dir == "":
            self.base_dir = self._check_base_dir(os.getcwd())
        else:
            self.base_dir = self._check_base_dir(to_dir)
        self._sort_files_recursive(from_dir)
