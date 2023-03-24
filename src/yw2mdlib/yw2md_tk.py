""""Provide a tkinter GUI class for the yWriter/Markdown converter.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw-reporter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import tkinter as tk
from tkinter import ttk
from pywriter.pywriter_globals import *
from pywriter.ui.main_tk import MainTk
from pywriter.yw.yw7_file import Yw7File
from yw2mdlib.md_file import MdFile


class Yw2mdTk(MainTk):
    """A tkinter GUI class for the yWriter/Markdown converter.
    
    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        open_project(fileName) -- select a valid project file and display the path.
        reverse_direction() -- swap source and target file names.
        convert_file() -- call the converter's conversion method, if a source file is selected.

    Public instance variables:
        converter -- converter strategy class.

    Adds a "Swap" and a "Run" entry to the main menu.
    Extends the superclass by redefining class constants and instance variables
    and processing application-specific keyword arguments.
    """
    _EXPORT_DESC = 'Export yWriter chapters and scenes to a Markdown document'
    _IMPORT_DESC = 'Create a yWriter project from a Markdown document'

    def __init__(self, title, **kwargs):
        """Add 'Options' checkboxes to the GUI main window.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
                    
        Required keyword arguments:
            yw_last_open -- initial file.
            file_types -- list of tuples for file selection (display text, extension).
            markdown_mode -- bool: if True, the scenes in the yWriter project are Markdown formatted.
            scene_titles -- bool: if True, associate comments at the beginning of the scene with scene titles
        
        Extends the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self._fileTypes = kwargs['file_types']
        self.converter = None
        self._sourcePath = None
        self._ywExtension = Yw7File.EXTENSION
        self._docExtension = MdFile.EXTENSION
        row1Cnt = 1
        self._header = tk.Label(self.mainWindow, text='Options')
        self._header.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)
        row1Cnt += 1
        self._sceneTitles = tk.BooleanVar(value=self.kwargs['scene_titles'])
        self._sceneTitlesCheckbox = ttk.Checkbutton(self.mainWindow,
                                                   text='Comments at the beginning of a scene are scene titles.',
                                                   variable=self._sceneTitles, onvalue=True, offvalue=False)
        self._sceneTitlesCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)
        row1Cnt += 1
        self._markdownMode = tk.BooleanVar(value=self.kwargs['markdown_mode'])
        self._markdownModeCheckbox = ttk.Checkbutton(self.mainWindow,
                                                    text='The scenes in the yWriter project are Markdown formatted.',
                                                    variable=self._markdownMode, onvalue=True, offvalue=False)
        self._markdownModeCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

    def _build_main_menu(self):
        """Add main menu entries.
        
        Extends the superclass template method. 
        """
        super()._build_main_menu()
        self.mainMenu.add_command(label=_('Swap'), command=self.reverse_direction)
        self.mainMenu.entryconfig(_('Swap'), state='disabled')
        self.mainMenu.add_command(label=_('Run'), command=self.convert_file)
        self.mainMenu.entryconfig(_('Run'), state='disabled')

    def disable_menu(self):
        """Disable menu entries when no project is open.
        
        Extends the superclass method.      
        """
        super().disable_menu()
        self.mainMenu.entryconfig(_('Run'), state='disabled')
        self.mainMenu.entryconfig(_('Swap'), state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open.
        
        Extends the superclass method.
        """
        super().enable_menu()
        self.mainMenu.entryconfig(_('Run'), state='normal')
        self.mainMenu.entryconfig(_('Swap'), state='normal')

    def open_project(self, fileName):
        """Select a valid project file and display the path.
        
        Positional arguments:
            fileName -- str: project file path.
            
        Return True on success, otherwise return False.
        Extends the superclass method.
        """
        fileName = super().select_project(fileName)
        if not fileName:
            return False
        self.kwargs['yw_last_open'] = fileName
        self._sourcePath = fileName
        self.enable_menu()
        if fileName.endswith(self._ywExtension):
            self.root.title(f'{self._EXPORT_DESC} - {self.title}')
        elif fileName.endswith(self._docExtension):
            self.root.title(f'{self._IMPORT_DESC} - {self.title}')
        self.show_path(f'{norm_path(fileName)}')
        return True

    def reverse_direction(self):
        """Swap source and target file names."""
        fileName, fileExtension = os.path.splitext(self._sourcePath)
        if fileExtension == self._ywExtension:
            self._sourcePath = f'{fileName}{self._docExtension}'
            self.show_path(norm_path(self._sourcePath))
            self.root.title(f'{self._IMPORT_DESC} - {self.title}')
            self.show_status('')
        elif fileExtension == self._docExtension:
            self._sourcePath = f'{fileName}{self._ywExtension}'
            self.show_path(norm_path(self._sourcePath))
            self.root.title(f'{self._EXPORT_DESC} - {self.title}')
            self.show_status('')

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        
        Write selected options to the keyword arguments.
        Extends the super class method.
        """
        self.kwargs['markdown_mode'] = self._markdownMode.get()
        self.kwargs['scene_titles'] = self._sceneTitles.get()
        self.show_status('')
        self.kwargs['yw_last_open'] = self._sourcePath
        self.converter.run(self._sourcePath, **self.kwargs)

