"""File sorter module.

This module provides functionality to sort large ammount of files
from a given root directory.
"""

__version__ = '0.1'
__author__ = 'Gijs Entius'

import os
import sys
import shutil
from datetime import datetime


def sort_files_recursive(from_dir):
    '''Function to sort files recursively
    '''
    if os.path.isdir(from_dir):
        for file in os.scandir(from_dir):
            if os.stat(file.path):
                sort_files_recursive()


# if os.name == 'nt':
#     pass