#!/usr/bin/env python3
"""Export yWriter project to markdown. 

GUI variant using tkinter
Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywmd.md_converter import MdConverter
from pywmd.md_ui import MdUi

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk


def run(sourcePath):

    ui = MdUi('Markdown converter for yWriter projects @release')
    # instantiate a user interface object

    if sourcePath is not None:

        if os.path.isfile(sourcePath):
            ui.sourcePath = sourcePath
            ui.set_info_what(
                'File: ' + os.path.normpath(sourcePath))
            ui.root.runButton.config(state='normal')

        else:
            sourcePath = None

    converter = MdConverter()
    # instantiate a converter object

    # Create a bidirectional association between the
    # user interface object and the converter object.

    converter.ui = ui
    # make the user interface's methods visible to the converter

    ui.converter = converter
    # make the converter's methods visible to the user interface

    ui.start()


if __name__ == '__main__':

    try:
        sourcePath = sys.argv[1].replace('\\', '/')

    except:
        sourcePath = None

    run(sourcePath)
