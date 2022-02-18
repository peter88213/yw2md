#!/usr/bin/env python3
""""Provide a tkinter GUI class for the yWriter/Markdown converter.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-reporter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import tkinter as tk
from tkinter import ttk

from pywriter.ui.main_tk_cnv import MainTkCnv
from pywmd.md_file import MdFile


class Yw2mdTk(MainTkCnv):
    """A tkinter GUI class for the yWriter/Markdown converter.
    Extend the superclass by redefining class constants and instance variables
    and processing application-specific keyword arguments.
    """    
    _EXPORT_DESC = 'Export yWriter chapters and scenes to a Markdown document.'
    _IMPORT_DESC = 'Create a yWriter project from a Markdown document.'

    def __init__(self, title, **kwargs):
        """Put a text box to the GUI main window.
        Extend the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self._docExtension = MdFile.EXTENSION

        #--- Row 1: "Levels" checkboxes (chapters, scenes)

        row1Cnt = 1
        self._header = tk.Label(self._mainWindow, text='Options')
        self._header.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self._sceneTitles = tk.BooleanVar(value=self.kwargs['scene_titles'])
        self._sceneTitlesCheckbox = ttk.Checkbutton(self._mainWindow,
                                                   text='Comments at the beginning of a scene are scene titles.', 
                                                   variable=self._sceneTitles, onvalue=True, offvalue=False)
        self._sceneTitlesCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self._markdownMode = tk.BooleanVar(value=self.kwargs['markdown_mode'])
        self._markdownModeCheckbox = ttk.Checkbutton(self._mainWindow,
                                                    text='The scenes in the yWriter project are Markdown formatted.', 
                                                    variable=self._markdownMode, onvalue=True, offvalue=False)
        self._markdownModeCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)


    def _convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        """
        self.kwargs['markdown_mode'] = self._markdownMode.get()
        self.kwargs['scene_titles'] = self._sceneTitles.get()
        super()._convert_file()

