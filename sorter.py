#!/usr/bin/env python3

"""File sorter module.

This module provides functionality to sort large ammount of files
from a given root directory. The files will be sorted on modification
date.
"""

__version__ = '0.1'
__author__ = 'Gijs Entius'

import argparse

from file_sorting import FileSorter

if __name__ == "__main__":
    sorter = FileSorter()
    parser = argparse.ArgumentParser(
        description='Sort files on modification date')
    parser.add_argument('-s', '--source',
        help='The source directory of the files to sort')
    parser.add_argument('-o', '--output', default="",
        help='The output directory of the files to sort')
    parser.add_argument('-e', '--extension', default="",
        help='The extension of files to sort')
    parser.add_argument('--move', action='store_const', const=True,
        help='Enables moving files instead of copying')
    args = parser.parse_args()

    sorter.sort_files(args.source, args.output, args.extension, args.move)
