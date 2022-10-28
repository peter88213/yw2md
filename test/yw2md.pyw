#!/usr/bin/env python3
"""Markdown converter for yWriter projects.

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import argparse
from pathlib import Path
from configparser import ConfigParser


class Configuration:
    """Application configuration, representing an INI file.

        INI file sections:
        <self._sLabel> - Strings
        <self._oLabel> - Boolean values

    Public methods:
        set(settings={}, options={}) -- set the entire configuration without writing the INI file.
        read(iniFile) -- read a configuration file.
        write(iniFile) -- save the configuration to iniFile.

    Public instance variables:    
        settings - dictionary of strings
        options - dictionary of boolean values
    """

    def __init__(self, settings={}, options={}):
        """Initalize attribute variables.

        Optional arguments:
            settings -- default settings (dictionary of strings)
            options -- default options (dictionary of boolean values)
        """
        self.settings = None
        self.options = None
        self._sLabel = 'SETTINGS'
        self._oLabel = 'OPTIONS'
        self.set(settings, options)

    def set(self, settings=None, options=None):
        """Set the entire configuration without writing the INI file.

        Optional arguments:
            settings -- new settings (dictionary of strings)
            options -- new options (dictionary of boolean values)
        """
        if settings is not None:
            self.settings = settings.copy()
        if options is not None:
            self.options = options.copy()

    def read(self, iniFile):
        """Read a configuration file.
        
        Positional arguments:
            iniFile -- str: path configuration file path.
            
        Settings and options that can not be read in, remain unchanged.
        """
        config = ConfigParser()
        config.read(iniFile, encoding='utf-8')
        if config.has_section(self._sLabel):
            section = config[self._sLabel]
            for setting in self.settings:
                fallback = self.settings[setting]
                self.settings[setting] = section.get(setting, fallback)
        if config.has_section(self._oLabel):
            section = config[self._oLabel]
            for option in self.options:
                fallback = self.options[option]
                self.options[option] = section.getboolean(option, fallback)

    def write(self, iniFile):
        """Save the configuration to iniFile.

        Positional arguments:
            iniFile -- str: path configuration file path.
        """
        config = ConfigParser()
        if self.settings:
            config.add_section(self._sLabel)
            for settingId in self.settings:
                config.set(self._sLabel, settingId, str(self.settings[settingId]))
        if self.options:
            config.add_section(self._oLabel)
            for settingId in self.options:
                if self.options[settingId]:
                    config.set(self._oLabel, settingId, 'Yes')
                else:
                    config.set(self._oLabel, settingId, 'No')
        with open(iniFile, 'w', encoding='utf-8') as f:
            config.write(f)
import re
import gettext
import locale

ERROR = '!'

__all__ = ['ERROR', '_',
           'LOCALE_PATH',
           'CURRENT_LANGUAGE',
           'ADDITIONAL_WORD_LIMITS',
           'NO_WORD_LIMITS',
           'NON_LETTERS',
           'string_to_list',
           'list_to_string',
           'get_languages',
           ]

#--- Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getlocale()[0][:2]
try:
    t = gettext.translation('pywriter', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words

NON_LETTERS = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')
# this is to be replaced by empty strings, thus excluding markup, comments, and linefeeds
# from letter counting


def string_to_list(text, divider=';'):
    """Convert a string into a list with unique elements.
    
    Positional arguments:
        text -- string containing divider-separated substrings.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Split a string into a list of strings. Retain the order, but discard duplicates.
    Remove leading and trailing spaces, if any.
    Return a list of strings.
    If an error occurs, return an empty list.
    """
    elements = []
    try:
        tempList = text.split(divider)
        for element in tempList:
            element = element.strip()
            if element and not element in elements:
                elements.append(element)
        return elements

    except:
        return []


def list_to_string(elements, divider=';'):
    """Join strings from a list.
    
    Positional arguments:
        elements -- list of elements to be concatenated.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Return a string which is the concatenation of the 
    members of the list of strings "elements", separated by 
    a comma plus a space. The space allows word wrap in 
    spreadsheet cells.
    If an error occurs, return an empty string.
    """
    try:
        text = divider.join(elements)
        return text

    except:
        return ''


LANGUAGE_TAG = re.compile('\[lang=(.*?)\]')


def get_languages(text):
    """Return a generator object with the language codes appearing in text.
    
    Example:
    - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
    - language code: 'en-AU'
    """
    if text:
        m = LANGUAGE_TAG.search(text)
        while m:
            text = text[m.span()[1]:]
            yield m.group(1)
            m = LANGUAGE_TAG.search(text)



class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- launch the GUI, if any.
        show_warning(message) -- Stub for displaying a warning message.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """

    def show_warning(self, message):
        """Stub for displaying a warning message."""


def open_document(document):
    """Open a document with the operating system's standard application."""
    try:
        os.startfile(os.path.normpath(document))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(document))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(document))
                # Mac
            except:
                pass


class YwCnv:
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, source, target):
        """Convert source into target and return a message.

        Positional arguments:
            source, target -- Novel subclass instances.

        Operation:
        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with the ERROR constant in case of error.

        Error handling:
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Pass the error messages of the called methods of source and target.
        - The success message comes from target.write(), if called.       
        """
        if source.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(source.filePath)}".'

        if not os.path.isfile(source.filePath):
            return f'{ERROR}{_("File not found")}: "{os.path.normpath(source.filePath)}".'

        if target.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(target.filePath)}".'

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            return f'{ERROR}{_("Action canceled by user")}.'

        message = source.read()
        if message.startswith(ERROR):
            return message

        message = target.merge(source)
        if message.startswith(ERROR):
            return message

        return target.write()

    def _confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        
        Positional argument:
            fileName -- path to the target file.
        
        This is a stub to be overridden by subclass methods.
        """
        return True


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, os.path.normpath(target.filePath)))
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'{ERROR}{_("File already exists")}: "{os.path.normpath(target.filePath)}".')
        else:
            message = self.convert(source, target)
            self.ui.set_info_how(message)
            self._delete_tempfile(source.filePath)
            if message.startswith(ERROR):
                self.newFile = None
            else:
                self.newFile = target.filePath

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        self._delete_tempfile(source.filePath)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath
            if target.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(os.path.normpath(filePath)))

    def _delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""
        if filePath.endswith('.html'):
            # Might it be a temporary text document?
            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass
        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?
            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)


class FileFactory:
    """Base class for conversion object factory classes.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a "private" instance variable.

        Optional arguments:
            _fileClasses -- list of classes from which an instance can be returned.
        """
        self._fileClasses = fileClasses


class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a YwFile subclass instance, or None in case of error
        - targetFile: None
        """
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return 'Source object created.', sourceFile, None

        return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(sourcePath)}".', None, None


class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX == suffix:
                if suffix is None:
                    suffix = ''
                targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile

        return f'{ERROR}{_("Export type is not supported")}: "{suffix}".', None, None


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None
        """
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return 'Source object created.', sourceFile, None

        return f'{ERROR}{_("This document is not meant to be written back")}.', None, None


class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a YwFile subclass instance, or None in case of error
        """
        fileName, __ = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']
        if sourceSuffix:
            # Remove the suffix from the source file name.
            # This should also work if the file name already contains the suffix,
            # e.g. "test_notes_notes.odt".
            e = fileName.split(sourceSuffix)
            if len(e) > 1:
                e.pop()
            ywPathBasis = ''.join(e)
        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.
        for fileClass in self._fileClasses:
            if os.path.isfile(f'{ywPathBasis}{fileClass.EXTENSION}'):
                targetFile = fileClass(f'{ywPathBasis}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile

        return f'{ERROR}{_("No yWriter project to write")}.', None, None


class YwCnvFf(YwCnvUi):
    """Class for Novel file conversion using factory methods to create target and source classes.

    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- list of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- list of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- list of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- list of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
    """
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Create strategy class instances.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            suffix -- str: target file name suffix.

        This is a template method that calls superclass methods as primitive operations by case.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}{_("File not found")}: "{os.path.normpath(sourcePath)}".')
            return

        message, source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        if message.startswith(ERROR):
            # The source file is not a yWriter project.
            message, source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                # A new yWriter project might be required.
                message, source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.create_yw7(source, target)
            else:
                # Try to update an existing yWriter project.
                kwargs['suffix'] = source.SUFFIX
                message, __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.import_to_yw(source, target)
        else:
            # The source file is a yWriter project.
            message, __, target = self.exportTargetFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                self.ui.set_info_how(message)
            else:
                self.export_from_yw(source, target)
from html import unescape
import xml.etree.ElementTree as ET
from urllib.parse import quote


class BasicElement:
    """Basic element representation (may be a project note).
    
    Public instance variables:
        title -- str: title (name).
        desc -- str: description.
        kwVar -- dict: custom keyword variables.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.


class Chapter(BasicElement):
    """yWriter chapter representation.
    
    Public instance variables:
        chLevel -- int: chapter level (part/chapter).
        chType -- int: chapter type (Normal/Notes/Todo/Unused).
        suppressChapterTitle -- bool: uppress chapter title when exporting.
        isTrash -- bool: True, if the chapter is the project's trash bin.
        suppressChapterBreak -- bool: Suppress chapter break when exporting.
        srtScenes -- list of str: the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.chType = None
        # int
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # 3= Unused
        # Applies to projects created by yWriter version 7.0.7.2+.
        #
        # xml: <ChapterType>
        # xml: <Type>
        # xml: <Unused>
        #
        # This is how yWriter 7.1.3.0 reads the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        # -------+--------+------+--------------------
        # Normal | N/A    | N/A  | N/A         | 0
        # Normal | N/A    | 0    | N/A         | 0
        # Notes  | x      | 1    | N/A         | 1
        # Unused | -1     | 0    | N/A         | 3
        # Normal | N/A    | x    | 0           | 0
        # Notes  | x      | x    | 1           | 1
        # Todo   | x      | x    | 2           | 2
        # Unused | -1     | x    | x           | 3
        #
        # This is how yWriter 7.1.3.0 writes the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        #--------+--------+------+-------------+------
        # Normal | N/A    | 0    | 0           | 0
        # Notes  | -1     | 1    | 1           | 1
        # Todo   | -1     | 1    | 2           | 2
        # Unused | -1     | 1    | 0           | 3

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.


class Scene(BasicElement):
    """yWriter scene representation.
    
    Public instance variables:
        sceneContent -- str: scene content (property with getter and setter).
        wordCount - int: word count (derived; updated by the sceneContent setter).
        letterCount - int: letter count (derived; updated by the sceneContent setter).
        scType -- int: Scene type (Normal/Notes/Todo/Unused).
        doNotExport -- bool: True if the scene is not to be exported to RTF.
        status -- int: scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        notes -- str: scene notes in a single string.
        tags -- list of scene tags. 
        field1 -- int: scene ratings field 1.
        field2 -- int: scene ratings field 2.
        field3 -- int: scene ratings field 3.
        field4 -- int: scene ratings field 4.
        appendToPrev -- bool: if True, append the scene without a divider to the previous scene.
        isReactionScene -- bool: if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot -- bool: if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal -- str: the main actor's scene goal. 
        conflict -- str: what hinders the main actor to achieve his goal.
        outcome -- str: what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date -- str: specific start date in ISO format (yyyy-mm-dd).
        time -- str: specific start time in ISO format (hh:mm).
        minute -- str: unspecific start time: minutes.
        hour -- str: unspecific start time: hour.
        day -- str: unspecific start time: day.
        lastsMinutes -- str: scene duration: minutes.
        lastsHours -- str: scene duration: hours.
        lastsDays -- str: scene duration: days. 
        image -- str:  path to an image related to the scene. 
    """
    STATUS = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.scType = None
        # Scene type (Normal/Notes/Todo/Unused).
        #
        # xml: <Unused>
        # xml: <Fields><Field_SceneType>
        #
        # This is how yWriter 7.1.3.0 reads the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Notes  | x      | 1              | 1
        # Todo   | x      | 2              | 2
        # Unused | -1     | N/A            | 3
        # Unused | -1     | 0              | 3
        # Normal | N/A    | N/A            | 0
        # Normal | N/A    | 0              | 0
        #
        # This is how yWriter 7.1.3.0 writes the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Normal | N/A    | N/A            | 0
        # Notes  | -1     | 1              | 1
        # Todo   | -1     | 2              | 2
        # Unused | -1     | 0              | 3

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.notes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

        self.image = None
        # str
        # xml: <ImageFile>

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)


class WorldElement(BasicElement):
    """Story world element representation (may be location or item).
    
    Public instance variables:
        image -- str: image file path.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.image = None
        # str
        # xml: <ImageFile>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>



class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes -- str: character notes.
        bio -- str: character biography.
        goals -- str: character's goals in the story.
        fullName -- str: full name (the title inherited may be a short name).
        isMajor -- bool: True, if it's a major character.
    """
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>


class Novel(BasicElement):
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- Parse the file and get the instance variables.
        merge(source) -- Update instance variables from a source instance.
        write() -- Write instance variables to the file.
        get_languages() -- Determine the languages used in the document.
        check_locale() -- Check the document's locale (language code and country code).

    Public instance variables:
        authorName -- str: author's name.
        author bio -- str: information about the author.
        fieldTitle1 -- str: scene rating field title 1.
        fieldTitle2 -- str: scene rating field title 2.
        fieldTitle3 -- str: scene rating field title 3.
        fieldTitle4 -- str: scene rating field title 4.
        chapters -- dict: (key: ID; value: chapter instance).
        scenes -- dict: (key: ID, value: scene instance).
        srtChapters -- list: the novel's sorted chapter IDs.
        locations -- dict: (key: ID, value: WorldElement instance).
        srtLocations -- list: the novel's sorted location IDs.
        items -- dict: (key: ID, value: WorldElement instance).
        srtItems -- list: the novel's sorted item IDs.
        characters -- dict: (key: ID, value: character instance).
        srtCharacters -- list: the novel's sorted character IDs.
        projectNotes -- dict:  (key: ID, value: projectNote instance).
        srtPrjNotes -- list: the novel's sorted project notes.
        projectName -- str: URL-coded file name without suffix and extension. 
        projectPath -- str: URL-coded path to the project directory. 
        filePath -- str: path to the file (property with getter and setter). 
    """
    DESCRIPTION = _('Novel')
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    CHAPTER_CLASS = Chapter
    SCENE_CLASS = Scene
    CHARACTER_CLASS = Character
    WE_CLASS = WorldElement
    PN_CLASS = BasicElement

    _PRJ_KWVAR = ()
    _CHP_KWVAR = ()
    _SCN_KWVAR = ()
    _CRT_KWVAR = ()
    _LOC_KWVAR = ()
    _ITM_KWVAR = ()
    _PNT_KWVAR = ()
    # Keyword variables for custom fields in the .yw7 XML file.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.  
            
        Extends the superclass constructor.          
        """
        super().__init__()

        self.authorName = None
        # str
        # xml: <PROJECT><AuthorName>

        self.authorBio = None
        # str
        # xml: <PROJECT><Bio>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.languages = None
        # list of str
        # List of non-document languages occurring as scene markup.
        # Format: ll-CC, where ll is the language code, and CC is the country code.

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self.projectNotes = {}
        # dict
        # xml: <PROJECTNOTES>
        # key = note ID, value = note instance.
        # The order of the elements does not matter.

        self.srtPrjNotes = []
        # list of str
        # The novel's projectNote IDs. The order of its elements corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self.projectPath = None
        # str
        # URL-coded path to the project directory.

        self.languageCode = None
        self.countryCode = None

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Read method is not implemented.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Merge method is not implemented.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Write method is not implemented.'

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def get_languages(self):
        """Determine the languages used in the document.
        
        Populate the self.languages list with all language codes found in the scene contents.        
        Example:
        - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
        - language code: 'en-AU'
        """
        self.languages = []
        for scId in self.scenes:
            text = self.scenes[scId].sceneContent
            if text:
                for language in get_languages(text):
                    if not language in self.languages:
                        self.languages.append(language)

    def check_locale(self):
        """Check the document's locale (language code and country code).
        
        If the locale is missing, set the system locale.  
        If the locale doesn't look plausible, set "no language".        
        """
        if not self.languageCode or not self.countryCode:
            # Language or country isn't set.
            sysLng, sysCtr = locale.getlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            # Plausibility check: code must have two characters.
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
                    # keep the setting
        except:
            # code isn't a string
            pass
        # Existing language or country field looks not plausible
        self.languageCode = 'zxx'
        self.countryCode = 'none'



def create_id(elements):
    """Return an unused ID for a new element.
    
    Positional arguments:
        elements -- list or dictionary containing all existing IDs
    """
    i = 1
    while str(i) in elements:
        i += 1
    return str(i)



class Splitter:
    """Helper class for scene and chapter splitting.
    
    When importing scenes to yWriter, they may contain manually inserted scene and chapter dividers.
    The Splitter class updates a Novel instance by splitting such scenes and creating new chapters and scenes. 
    
    Public methods:
        split_scenes(novel) -- Split scenes by inserted chapter and scene dividers.
        
    Public class constants:
        PART_SEPARATOR -- marker indicating the beginning of a new part, splitting a scene.
        CHAPTER_SEPARATOR -- marker indicating the beginning of a new chapter, splitting a scene.
        DESC_SEPARATOR -- marker separating title and description of a chapter or scene.
    """
    PART_SEPARATOR = '#'
    CHAPTER_SEPARATOR = '##'
    SCENE_SEPARATOR = '###'
    DESC_SEPARATOR = '|'
    _CLIP_TITLE = 20
    # Maximum length of newly generated scene titles.

    def split_scenes(self, novel):
        """Split scenes by inserted chapter and scene dividers.
        
        Update a Novel instance by generating new chapters and scenes 
        if there are dividers within the scene content.
        
        Positional argument: 
            novel -- Novel instance to update.
        
        Return True if the sructure has changed, 
        otherwise return False.        
        """

        def create_chapter(chapterId, title, desc, level):
            """Create a new chapter and add it to the novel.
            
            Positional arguments:
                chapterId -- str: ID of the chapter to create.
                title -- str: title of the chapter to create.
                desc -- str: description of the chapter to create.
                level -- int: chapter level (part/chapter).           
            """
            newChapter = novel.CHAPTER_CLASS()
            newChapter.title = title
            newChapter.desc = desc
            newChapter.chLevel = level
            newChapter.chType = 0
            novel.chapters[chapterId] = newChapter

        def create_scene(sceneId, parent, splitCount, title, desc):
            """Create a new scene and add it to the novel.
            
            Positional arguments:
                sceneId -- str: ID of the scene to create.
                parent -- Scene instance: parent scene.
                splitCount -- int: number of parent's splittings.
                title -- str: title of the scene to create.
                desc -- str: description of the scene to create.
            """
            WARNING = '(!)'

            # Mark metadata of split scenes.
            newScene = novel.SCENE_CLASS()
            if title:
                newScene.title = title
            elif parent.title:
                if len(parent.title) > self._CLIP_TITLE:
                    title = f'{parent.title[:self._CLIP_TITLE]}...'
                else:
                    title = parent.title
                newScene.title = f'{title} Split: {splitCount}'
            else:
                newScene.title = f'_("New Scene") Split: {splitCount}'
            if desc:
                newScene.desc = desc
            if parent.desc and not parent.desc.startswith(WARNING):
                parent.desc = f'{WARNING}{parent.desc}'
            if parent.goal and not parent.goal.startswith(WARNING):
                parent.goal = f'{WARNING}{parent.goal}'
            if parent.conflict and not parent.conflict.startswith(WARNING):
                parent.conflict = f'{WARNING}{parent.conflict}'
            if parent.outcome and not parent.outcome.startswith(WARNING):
                parent.outcome = f'{WARNING}{parent.outcome}'

            # Reset the parent's status to Draft, if not Outline.
            if parent.status > 2:
                parent.status = 2
            newScene.status = parent.status
            newScene.scType = parent.scType
            newScene.date = parent.date
            newScene.time = parent.time
            newScene.day = parent.day
            newScene.hour = parent.hour
            newScene.minute = parent.minute
            newScene.lastsDays = parent.lastsDays
            newScene.lastsHours = parent.lastsHours
            newScene.lastsMinutes = parent.lastsMinutes
            novel.scenes[sceneId] = newScene

        # Get the maximum chapter ID and scene ID.
        chIdMax = 0
        scIdMax = 0
        for chId in novel.srtChapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        for scId in novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

        # Process chapters and scenes.
        scenesSplit = False
        srtChapters = []
        for chId in novel.srtChapters:
            srtChapters.append(chId)
            chapterId = chId
            srtScenes = []
            for scId in novel.chapters[chId].srtScenes:
                srtScenes.append(scId)
                if not novel.scenes[scId].sceneContent:
                    continue

                sceneId = scId
                lines = novel.scenes[scId].sceneContent.split('\n')
                newLines = []
                inScene = True
                sceneSplitCount = 0

                # Search scene content for dividers.
                for line in lines:
                    heading = line.strip('# ').split(self.DESC_SEPARATOR)
                    title = heading[0]
                    try:
                        desc = heading[1]
                    except:
                        desc = ''
                    if line.startswith(self.SCENE_SEPARATOR):
                        # Split the scene.
                        novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                        newLines = []
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, title, desc)
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    elif line.startswith(self.CHAPTER_SEPARATOR):
                        # Start a new chapter.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Chapter')
                        create_chapter(chapterId, title, desc, 0)
                        srtChapters.append(chapterId)
                        scenesSplit = True
                    elif line.startswith(self.PART_SEPARATOR):
                        # start a new part.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Part')
                        create_chapter(chapterId, title, desc, 1)
                        srtChapters.append(chapterId)
                    elif not inScene:
                        # Append a scene without heading to a new chapter or part.
                        newLines.append(line)
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, '', '')
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    else:
                        newLines.append(line)
                novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
            novel.chapters[chapterId].srtScenes = srtScenes
        novel.srtChapters = srtChapters
        return scenesSplit


def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = f'\n{level * "  "}'
    if elem:
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class Yw7File(Novel):
    """yWriter 7 project file representation.

    Public methods: 
        read() -- parse the yWriter xml file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the yWriter xml file.
        is_locked() -- check whether the yw7 file is locked by yWriter.
        remove_custom_fields() -- Remove custom fields from the yWriter file.

    Public instance variables:
        tree -- xml element tree of the yWriter project
        scenesSplit -- bool: True, if a scene or chapter is split during merging.
    """
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    _PRJ_KWVAR = (
        'Field_LanguageCode',
        'Field_CountryCode',
        )

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None
        self.scenesSplit = False

        #--- Initialize custom keyword variables.
        for field in self._PRJ_KWVAR:
            self.kwVar[field] = None

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def read_project(root):
            #--- Read attributes at project level from the xml element tree.
            prj = root.find('PROJECT')

            if prj.find('Title') is not None:
                self.title = prj.find('Title').text

            if prj.find('AuthorName') is not None:
                self.authorName = prj.find('AuthorName').text

            if prj.find('Bio') is not None:
                self.authorBio = prj.find('Bio').text

            if prj.find('Desc') is not None:
                self.desc = prj.find('Desc').text

            if prj.find('FieldTitle1') is not None:
                self.fieldTitle1 = prj.find('FieldTitle1').text

            if prj.find('FieldTitle2') is not None:
                self.fieldTitle2 = prj.find('FieldTitle2').text

            if prj.find('FieldTitle3') is not None:
                self.fieldTitle3 = prj.find('FieldTitle3').text

            if prj.find('FieldTitle4') is not None:
                self.fieldTitle4 = prj.find('FieldTitle4').text

            #--- Initialize custom keyword variables.
            for fieldName in self._PRJ_KWVAR:
                self.kwVar[fieldName] = None

            #--- Read project custom fields.
            for prjFields in prj.findall('Fields'):
                for fieldName in self._PRJ_KWVAR:
                    field = prjFields.find(fieldName)
                    if field is not None:
                        self.kwVar[fieldName] = field.text

            # This is for projects written with v7.6 - v7.10:
            if self.kwVar['Field_LanguageCode']:
                self.languageCode = self.kwVar['Field_LanguageCode']
            if self.kwVar['Field_CountryCode']:
                self.countryCode = self.kwVar['Field_CountryCode']

        def read_locations(root):
            #--- Read locations from the xml element tree.
            self.srtLocations = []
            # This is necessary for re-reading.
            for loc in root.iter('LOCATION'):
                lcId = loc.find('ID').text
                self.srtLocations.append(lcId)
                self.locations[lcId] = self.WE_CLASS()

                if loc.find('Title') is not None:
                    self.locations[lcId].title = loc.find('Title').text

                if loc.find('ImageFile') is not None:
                    self.locations[lcId].image = loc.find('ImageFile').text

                if loc.find('Desc') is not None:
                    self.locations[lcId].desc = loc.find('Desc').text

                if loc.find('AKA') is not None:
                    self.locations[lcId].aka = loc.find('AKA').text

                if loc.find('Tags') is not None:
                    if loc.find('Tags').text is not None:
                        tags = string_to_list(loc.find('Tags').text)
                        self.locations[lcId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self._LOC_KWVAR:
                    self.locations[lcId].kwVar[fieldName] = None

                #--- Read location custom fields.
                for lcFields in loc.findall('Fields'):
                    for fieldName in self._LOC_KWVAR:
                        field = lcFields.find(fieldName)
                        if field is not None:
                            self.locations[lcId].kwVar[fieldName] = field.text

        def read_items(root):
            #--- Read items from the xml element tree.
            self.srtItems = []
            # This is necessary for re-reading.
            for itm in root.iter('ITEM'):
                itId = itm.find('ID').text
                self.srtItems.append(itId)
                self.items[itId] = self.WE_CLASS()

                if itm.find('Title') is not None:
                    self.items[itId].title = itm.find('Title').text

                if itm.find('ImageFile') is not None:
                    self.items[itId].image = itm.find('ImageFile').text

                if itm.find('Desc') is not None:
                    self.items[itId].desc = itm.find('Desc').text

                if itm.find('AKA') is not None:
                    self.items[itId].aka = itm.find('AKA').text

                if itm.find('Tags') is not None:
                    if itm.find('Tags').text is not None:
                        tags = string_to_list(itm.find('Tags').text)
                        self.items[itId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self._ITM_KWVAR:
                    self.items[itId].kwVar[fieldName] = None

                #--- Read item custom fields.
                for itFields in itm.findall('Fields'):
                    for fieldName in self._ITM_KWVAR:
                        field = itFields.find(fieldName)
                        if field is not None:
                            self.items[itId].kwVar[fieldName] = field.text

        def read_characters(root):
            #--- Read characters from the xml element tree.
            self.srtCharacters = []
            # This is necessary for re-reading.
            for crt in root.iter('CHARACTER'):
                crId = crt.find('ID').text
                self.srtCharacters.append(crId)
                self.characters[crId] = self.CHARACTER_CLASS()

                if crt.find('Title') is not None:
                    self.characters[crId].title = crt.find('Title').text

                if crt.find('ImageFile') is not None:
                    self.characters[crId].image = crt.find('ImageFile').text

                if crt.find('Desc') is not None:
                    self.characters[crId].desc = crt.find('Desc').text

                if crt.find('AKA') is not None:
                    self.characters[crId].aka = crt.find('AKA').text

                if crt.find('Tags') is not None:
                    if crt.find('Tags').text is not None:
                        tags = string_to_list(crt.find('Tags').text)
                        self.characters[crId].tags = self._strip_spaces(tags)

                if crt.find('Notes') is not None:
                    self.characters[crId].notes = crt.find('Notes').text

                if crt.find('Bio') is not None:
                    self.characters[crId].bio = crt.find('Bio').text

                if crt.find('Goals') is not None:
                    self.characters[crId].goals = crt.find('Goals').text

                if crt.find('FullName') is not None:
                    self.characters[crId].fullName = crt.find('FullName').text

                if crt.find('Major') is not None:
                    self.characters[crId].isMajor = True
                else:
                    self.characters[crId].isMajor = False

                #--- Initialize custom keyword variables.
                for fieldName in self._CRT_KWVAR:
                    self.characters[crId].kwVar[fieldName] = None

                #--- Read character custom fields.
                for crFields in crt.findall('Fields'):
                    for fieldName in self._CRT_KWVAR:
                        field = crFields.find(fieldName)
                        if field is not None:
                            self.characters[crId].kwVar[fieldName] = field.text

        def read_projectnotes(root):
            #--- Read project notes from the xml element tree.
            self.srtPrjNotes = []
            # This is necessary for re-reading.

            try:
                for pnt in root.find('PROJECTNOTES'):
                    if pnt.find('ID') is not None:
                        pnId = pnt.find('ID').text
                        self.srtPrjNotes.append(pnId)
                        self.projectNotes[pnId] = self.PN_CLASS()
                        if pnt.find('Title') is not None:
                            self.projectNotes[pnId].title = pnt.find('Title').text
                        if pnt.find('Desc') is not None:
                            self.projectNotes[pnId].desc = pnt.find('Desc').text

                    #--- Initialize project note custom fields.
                    for fieldName in self._PNT_KWVAR:
                        self.projectNotes[pnId].kwVar[fieldName] = None

                    #--- Read project note custom fields.
                    for pnFields in pnt.findall('Fields'):
                        field = pnFields.find(fieldName)
                        if field is not None:
                            self.projectNotes[pnId].kwVar[fieldName] = field.text
            except:
                pass

        def read_projectvars(root):
            #--- Read relevant project variables from the xml element tree.
            try:
                for projectvar in root.find('PROJECTVARS'):
                    if projectvar.find('Title') is not None:
                        title = projectvar.find('Title').text
                        if title == 'Language':
                            if projectvar.find('Desc') is not None:
                                self.languageCode = projectvar.find('Desc').text

                        elif title == 'Country':
                            if projectvar.find('Desc') is not None:
                                self.countryCode = projectvar.find('Desc').text

                        elif title.startswith('lang='):
                            try:
                                __, langCode = title.split('=')
                                if self.languages is None:
                                    self.languages = []
                                self.languages.append(langCode)
                            except:
                                pass
            except:
                pass

        def read_scenes(root):
            #--- Read attributes at scene level from the xml element tree.
            for scn in root.iter('SCENE'):
                scId = scn.find('ID').text
                self.scenes[scId] = self.SCENE_CLASS()

                if scn.find('Title') is not None:
                    self.scenes[scId].title = scn.find('Title').text

                if scn.find('Desc') is not None:
                    self.scenes[scId].desc = scn.find('Desc').text

                if scn.find('SceneContent') is not None:
                    sceneContent = scn.find('SceneContent').text
                    if sceneContent is not None:
                        self.scenes[scId].sceneContent = sceneContent

                #--- Read scene type.

                # This is how yWriter 7.1.3.0 reads the scene type:
                #
                # Type   |<Unused>|Field_SceneType>|scType
                #--------+--------+----------------+------
                # Notes  | x      | 1              | 1
                # Todo   | x      | 2              | 2
                # Unused | -1     | N/A            | 3
                # Unused | -1     | 0              | 3
                # Normal | N/A    | N/A            | 0
                # Normal | N/A    | 0              | 0

                self.scenes[scId].scType = 0

                #--- Initialize custom keyword variables.
                for fieldName in self._SCN_KWVAR:
                    self.scenes[scId].kwVar[fieldName] = None

                for scFields in scn.findall('Fields'):
                    #--- Read scene custom fields.
                    for fieldName in self._SCN_KWVAR:
                        field = scFields.find(fieldName)
                        if field is not None:
                            self.scenes[scId].kwVar[fieldName] = field.text

                    # Read scene type, if any.
                    if scFields.find('Field_SceneType') is not None:
                        if scFields.find('Field_SceneType').text == '1':
                            self.scenes[scId].scType = 1
                        elif scFields.find('Field_SceneType').text == '2':
                            self.scenes[scId].scType = 2
                if scn.find('Unused') is not None:
                    if self.scenes[scId].scType == 0:
                        self.scenes[scId].scType = 3

                #--- Export when RTF.
                if scn.find('ExportCondSpecific') is None:
                    self.scenes[scId].doNotExport = False
                elif scn.find('ExportWhenRTF') is not None:
                    self.scenes[scId].doNotExport = False
                else:
                    self.scenes[scId].doNotExport = True

                if scn.find('Status') is not None:
                    self.scenes[scId].status = int(scn.find('Status').text)

                if scn.find('Notes') is not None:
                    self.scenes[scId].notes = scn.find('Notes').text

                if scn.find('Tags') is not None:
                    if scn.find('Tags').text is not None:
                        tags = string_to_list(scn.find('Tags').text)
                        self.scenes[scId].tags = self._strip_spaces(tags)

                if scn.find('Field1') is not None:
                    self.scenes[scId].field1 = scn.find('Field1').text

                if scn.find('Field2') is not None:
                    self.scenes[scId].field2 = scn.find('Field2').text

                if scn.find('Field3') is not None:
                    self.scenes[scId].field3 = scn.find('Field3').text

                if scn.find('Field4') is not None:
                    self.scenes[scId].field4 = scn.find('Field4').text

                if scn.find('AppendToPrev') is not None:
                    self.scenes[scId].appendToPrev = True
                else:
                    self.scenes[scId].appendToPrev = False

                if scn.find('SpecificDateTime') is not None:
                    dateTime = scn.find('SpecificDateTime').text.split(' ')
                    for dt in dateTime:
                        if '-' in dt:
                            self.scenes[scId].date = dt
                        elif ':' in dt:
                            self.scenes[scId].time = dt
                else:
                    if scn.find('Day') is not None:
                        self.scenes[scId].day = scn.find('Day').text

                    if scn.find('Hour') is not None:
                        self.scenes[scId].hour = scn.find('Hour').text

                    if scn.find('Minute') is not None:
                        self.scenes[scId].minute = scn.find('Minute').text

                if scn.find('LastsDays') is not None:
                    self.scenes[scId].lastsDays = scn.find('LastsDays').text

                if scn.find('LastsHours') is not None:
                    self.scenes[scId].lastsHours = scn.find('LastsHours').text

                if scn.find('LastsMinutes') is not None:
                    self.scenes[scId].lastsMinutes = scn.find('LastsMinutes').text

                if scn.find('ReactionScene') is not None:
                    self.scenes[scId].isReactionScene = True
                else:
                    self.scenes[scId].isReactionScene = False

                if scn.find('SubPlot') is not None:
                    self.scenes[scId].isSubPlot = True
                else:
                    self.scenes[scId].isSubPlot = False

                if scn.find('Goal') is not None:
                    self.scenes[scId].goal = scn.find('Goal').text

                if scn.find('Conflict') is not None:
                    self.scenes[scId].conflict = scn.find('Conflict').text

                if scn.find('Outcome') is not None:
                    self.scenes[scId].outcome = scn.find('Outcome').text

                if scn.find('ImageFile') is not None:
                    self.scenes[scId].image = scn.find('ImageFile').text

                if scn.find('Characters') is not None:
                    for characters in scn.find('Characters').iter('CharID'):
                        crId = characters.text
                        if crId in self.srtCharacters:
                            if self.scenes[scId].characters is None:
                                self.scenes[scId].characters = []
                            self.scenes[scId].characters.append(crId)

                if scn.find('Locations') is not None:
                    for locations in scn.find('Locations').iter('LocID'):
                        lcId = locations.text
                        if lcId in self.srtLocations:
                            if self.scenes[scId].locations is None:
                                self.scenes[scId].locations = []
                            self.scenes[scId].locations.append(lcId)

                if scn.find('Items') is not None:
                    for items in scn.find('Items').iter('ItemID'):
                        itId = items.text
                        if itId in self.srtItems:
                            if self.scenes[scId].items is None:
                                self.scenes[scId].items = []
                            self.scenes[scId].items.append(itId)

        def read_chapters(root):
            #--- Read attributes at chapter level from the xml element tree.
            self.srtChapters = []
            # This is necessary for re-reading.
            for chp in root.iter('CHAPTER'):
                chId = chp.find('ID').text
                self.chapters[chId] = self.CHAPTER_CLASS()
                self.srtChapters.append(chId)

                if chp.find('Title') is not None:
                    self.chapters[chId].title = chp.find('Title').text

                if chp.find('Desc') is not None:
                    self.chapters[chId].desc = chp.find('Desc').text

                if chp.find('SectionStart') is not None:
                    self.chapters[chId].chLevel = 1
                else:
                    self.chapters[chId].chLevel = 0

                # This is how yWriter 7.1.3.0 reads the chapter type:
                #
                # Type   |<Unused>|<Type>|<ChapterType>|chType
                # -------+--------+------+--------------------
                # Normal | N/A    | N/A  | N/A         | 0
                # Normal | N/A    | 0    | N/A         | 0
                # Notes  | x      | 1    | N/A         | 1
                # Unused | -1     | 0    | N/A         | 3
                # Normal | N/A    | x    | 0           | 0
                # Notes  | x      | x    | 1           | 1
                # Todo   | x      | x    | 2           | 2
                # Unused | -1     | x    | x           | 3

                self.chapters[chId].chType = 0
                if chp.find('Unused') is not None:
                    yUnused = True
                else:
                    yUnused = False
                if chp.find('ChapterType') is not None:
                    # The file may be created with yWriter version 7.0.7.2+
                    yChapterType = chp.find('ChapterType').text
                    if yChapterType == '2':
                        self.chapters[chId].chType = 2
                    elif yChapterType == '1':
                        self.chapters[chId].chType = 1
                    elif yUnused:
                        self.chapters[chId].chType = 3
                else:
                    # The file may be created with a yWriter version prior to 7.0.7.2
                    if chp.find('Type') is not None:
                        yType = chp.find('Type').text
                        if yType == '1':
                            self.chapters[chId].chType = 1
                        elif yUnused:
                            self.chapters[chId].chType = 3

                self.chapters[chId].suppressChapterTitle = False
                if self.chapters[chId].title is not None:
                    if self.chapters[chId].title.startswith('@'):
                        self.chapters[chId].suppressChapterTitle = True

                #--- Initialize custom keyword variables.
                for fieldName in self._CHP_KWVAR:
                    self.chapters[chId].kwVar[fieldName] = None

                #--- Read chapter fields.
                for chFields in chp.findall('Fields'):
                    if chFields.find('Field_SuppressChapterTitle') is not None:
                        if chFields.find('Field_SuppressChapterTitle').text == '1':
                            self.chapters[chId].suppressChapterTitle = True
                    self.chapters[chId].isTrash = False
                    if chFields.find('Field_IsTrash') is not None:
                        if chFields.find('Field_IsTrash').text == '1':
                            self.chapters[chId].isTrash = True
                    self.chapters[chId].suppressChapterBreak = False
                    if chFields.find('Field_SuppressChapterBreak') is not None:
                        if chFields.find('Field_SuppressChapterBreak').text == '1':
                            self.chapters[chId].suppressChapterBreak = True

                    #--- Read chapter custom fields.
                    for fieldName in self._CHP_KWVAR:
                        field = chFields.find(fieldName)
                        if field is not None:
                            self.chapters[chId].kwVar[fieldName] = field.text

                #--- Read chapter's scene list.
                self.chapters[chId].srtScenes = []
                if chp.find('Scenes') is not None:
                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        if scId in self.scenes:
                            self.chapters[chId].srtScenes.append(scId)

        #--- Begin reading.
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'
        try:
            self.tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}{_("Can not process file")}: "{os.path.normpath(self.filePath)}".'

        root = self.tree.getroot()
        read_project(root)
        read_locations(root)
        read_items(root)
        read_characters(root)
        read_projectvars(root)
        read_projectnotes(root)
        read_scenes(root)
        read_chapters(root)
        self.adjust_scene_types()
        return 'yWriter project data read in.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def merge_lists(srcLst, tgtLst):
            """Insert srcLst items to tgtLst, if missing.
            """
            j = 0
            for item in srcLst:
                if not item in tgtLst:
                    tgtLst.insert(j, item)
                    j += 1
                else:
                    j = tgtLst.index(item) + 1

        if os.path.isfile(self.filePath):
            message = self.read()
            # initialize data
            if message.startswith(ERROR):
                return message

        #--- Merge and re-order locations.
        if source.srtLocations:
            self.srtLocations = source.srtLocations
            temploc = self.locations
            self.locations = {}
            for lcId in source.srtLocations:

                # Build a new self.locations dictionary sorted like the source.
                self.locations[lcId] = self.WE_CLASS()
                if not lcId in temploc:
                    # A new location has been added
                    temploc[lcId] = self.WE_CLASS()
                if source.locations[lcId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.locations[lcId].title = source.locations[lcId].title
                else:
                    self.locations[lcId].title = temploc[lcId].title
                if source.locations[lcId].image is not None:
                    self.locations[lcId].image = source.locations[lcId].image
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].desc is not None:
                    self.locations[lcId].desc = source.locations[lcId].desc
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].aka is not None:
                    self.locations[lcId].aka = source.locations[lcId].aka
                else:
                    self.locations[lcId].aka = temploc[lcId].aka
                if source.locations[lcId].tags is not None:
                    self.locations[lcId].tags = source.locations[lcId].tags
                else:
                    self.locations[lcId].tags = temploc[lcId].tags
                for fieldName in self._LOC_KWVAR:
                    try:
                        self.locations[lcId].kwVar[fieldName] = source.locations[lcId].kwVar[fieldName]
                    except:
                        self.locations[lcId].kwVar[fieldName] = temploc[lcId].kwVar.get(fieldName, None)

        #--- Merge and re-order items.
        if source.srtItems:
            self.srtItems = source.srtItems
            tempitm = self.items
            self.items = {}
            for itId in source.srtItems:

                # Build a new self.items dictionary sorted like the source.
                self.items[itId] = self.WE_CLASS()
                if not itId in tempitm:
                    # A new item has been added
                    tempitm[itId] = self.WE_CLASS()
                if source.items[itId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.items[itId].title = source.items[itId].title
                else:
                    self.items[itId].title = tempitm[itId].title
                if source.items[itId].image is not None:
                    self.items[itId].image = source.items[itId].image
                else:
                    self.items[itId].image = tempitm[itId].image
                if source.items[itId].desc is not None:
                    self.items[itId].desc = source.items[itId].desc
                else:
                    self.items[itId].desc = tempitm[itId].desc
                if source.items[itId].aka is not None:
                    self.items[itId].aka = source.items[itId].aka
                else:
                    self.items[itId].aka = tempitm[itId].aka
                if source.items[itId].tags is not None:
                    self.items[itId].tags = source.items[itId].tags
                else:
                    self.items[itId].tags = tempitm[itId].tags
                for fieldName in self._ITM_KWVAR:
                    try:
                        self.items[itId].kwVar[fieldName] = source.items[itId].kwVar[fieldName]
                    except:
                        self.items[itId].kwVar[fieldName] = tempitm[itId].kwVar.get(fieldName, None)

        #--- Merge and re-order characters.
        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            tempchr = self.characters
            self.characters = {}
            for crId in source.srtCharacters:

                # Build a new self.characters dictionary sorted like the source.
                self.characters[crId] = self.CHARACTER_CLASS()
                if not crId in tempchr:
                    # A new character has been added
                    tempchr[crId] = self.CHARACTER_CLASS()
                if source.characters[crId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.characters[crId].title = source.characters[crId].title
                else:
                    self.characters[crId].title = tempchr[crId].title
                if source.characters[crId].image is not None:
                    self.characters[crId].image = source.characters[crId].image
                else:
                    self.characters[crId].image = tempchr[crId].image
                if source.characters[crId].desc is not None:
                    self.characters[crId].desc = source.characters[crId].desc
                else:
                    self.characters[crId].desc = tempchr[crId].desc
                if source.characters[crId].aka is not None:
                    self.characters[crId].aka = source.characters[crId].aka
                else:
                    self.characters[crId].aka = tempchr[crId].aka
                if source.characters[crId].tags is not None:
                    self.characters[crId].tags = source.characters[crId].tags
                else:
                    self.characters[crId].tags = tempchr[crId].tags
                if source.characters[crId].notes is not None:
                    self.characters[crId].notes = source.characters[crId].notes
                else:
                    self.characters[crId].notes = tempchr[crId].notes
                if source.characters[crId].bio is not None:
                    self.characters[crId].bio = source.characters[crId].bio
                else:
                    self.characters[crId].bio = tempchr[crId].bio
                if source.characters[crId].goals is not None:
                    self.characters[crId].goals = source.characters[crId].goals
                else:
                    self.characters[crId].goals = tempchr[crId].goals
                if source.characters[crId].fullName is not None:
                    self.characters[crId].fullName = source.characters[crId].fullName
                else:
                    self.characters[crId].fullName = tempchr[crId].fullName
                if source.characters[crId].isMajor is not None:
                    self.characters[crId].isMajor = source.characters[crId].isMajor
                else:
                    self.characters[crId].isMajor = tempchr[crId].isMajor
                for fieldName in self._CRT_KWVAR:
                    try:
                        self.characters[crId].kwVar[fieldName] = source.characters[crId].kwVar[fieldName]
                    except:
                        self.characters[crId].kwVar[fieldName] = tempchr[crId].kwVar.get(fieldName, None)

        #--- Merge and re-order projectNotes.
        if source.srtPrjNotes:
            self.srtPrjNotes = source.srtPrjNotes
            tempPrjn = self.projectNotes
            self.projectNotes = {}
            for pnId in source.srtPrjNotes:

                # Build a new self.projectNotes dictionary sorted like the source.
                self.projectNotes[pnId] = self.PN_CLASS()
                if not pnId in tempPrjn:
                    # A new projecNote has been added
                    tempPrjn[pnId] = self.PN_CLASS()

                if source.projectNotes[pnId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.projectNotes[pnId].title = source.projectNotes[pnId].title
                else:
                    self.projectNotes[pnId].title = tempPrjn[pnId].title

                if source.projectNotes[pnId].desc is not None:
                    self.projectNotes[pnId].desc = source.projectNotes[pnId].desc
                else:
                    self.projectNotes[pnId].desc = tempPrjn[pnId].desc

                for fieldName in self._prn_KWVAR:
                    try:
                        self.projectNotes[pnId].kwVar[fieldName] = source.projectNotes[pnId].kwVar[fieldName]
                    except:
                        self.projectNotes[pnId].kwVar[fieldName] = tempPrjn[pnId].kwVar.get(fieldName, None)

        #--- Merge scenes.
        sourceHasSceneContent = False
        for scId in source.scenes:
            if not scId in self.scenes:
                self.scenes[scId] = self.SCENE_CLASS()

            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = source.scenes[scId].title
            if source.scenes[scId].desc is not None:
                self.scenes[scId].desc = source.scenes[scId].desc

            if source.scenes[scId].sceneContent is not None:
                self.scenes[scId].sceneContent = source.scenes[scId].sceneContent
                sourceHasSceneContent = True
            if source.scenes[scId].scType is not None:
                self.scenes[scId].scType = source.scenes[scId].scType

            if source.scenes[scId].status is not None:
                self.scenes[scId].status = source.scenes[scId].status

            if source.scenes[scId].notes is not None:
                self.scenes[scId].notes = source.scenes[scId].notes

            if source.scenes[scId].tags is not None:
                self.scenes[scId].tags = source.scenes[scId].tags

            if source.scenes[scId].field1 is not None:
                self.scenes[scId].field1 = source.scenes[scId].field1

            if source.scenes[scId].field2 is not None:
                self.scenes[scId].field2 = source.scenes[scId].field2

            if source.scenes[scId].field3 is not None:
                self.scenes[scId].field3 = source.scenes[scId].field3

            if source.scenes[scId].field4 is not None:
                self.scenes[scId].field4 = source.scenes[scId].field4

            if source.scenes[scId].appendToPrev is not None:
                self.scenes[scId].appendToPrev = source.scenes[scId].appendToPrev

            if source.scenes[scId].date or source.scenes[scId].time:
                if source.scenes[scId].date is not None:
                    self.scenes[scId].date = source.scenes[scId].date
                if source.scenes[scId].time is not None:
                    self.scenes[scId].time = source.scenes[scId].time
            elif source.scenes[scId].minute or source.scenes[scId].hour or source.scenes[scId].day:
                self.scenes[scId].date = None
                self.scenes[scId].time = None

            if source.scenes[scId].minute is not None:
                self.scenes[scId].minute = source.scenes[scId].minute

            if source.scenes[scId].hour is not None:
                self.scenes[scId].hour = source.scenes[scId].hour

            if source.scenes[scId].day is not None:
                self.scenes[scId].day = source.scenes[scId].day

            if source.scenes[scId].lastsMinutes is not None:
                self.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes

            if source.scenes[scId].lastsHours is not None:
                self.scenes[scId].lastsHours = source.scenes[scId].lastsHours

            if source.scenes[scId].lastsDays is not None:
                self.scenes[scId].lastsDays = source.scenes[scId].lastsDays

            if source.scenes[scId].isReactionScene is not None:
                self.scenes[scId].isReactionScene = source.scenes[scId].isReactionScene

            if source.scenes[scId].isSubPlot is not None:
                self.scenes[scId].isSubPlot = source.scenes[scId].isSubPlot

            if source.scenes[scId].goal is not None:
                self.scenes[scId].goal = source.scenes[scId].goal

            if source.scenes[scId].conflict is not None:
                self.scenes[scId].conflict = source.scenes[scId].conflict

            if source.scenes[scId].outcome is not None:
                self.scenes[scId].outcome = source.scenes[scId].outcome

            if source.scenes[scId].characters is not None:
                self.scenes[scId].characters = []
                for crId in source.scenes[scId].characters:
                    if crId in self.characters:
                        self.scenes[scId].characters.append(crId)

            if source.scenes[scId].locations is not None:
                self.scenes[scId].locations = []
                for lcId in source.scenes[scId].locations:
                    if lcId in self.locations:
                        self.scenes[scId].locations.append(lcId)

            if source.scenes[scId].items is not None:
                self.scenes[scId].items = []
                for itId in source.scenes[scId].items:
                    if itId in self.items:
                        self.scenes[scId].items.append(itId)

            for fieldName in self._SCN_KWVAR:
                try:
                    self.scenes[scId].kwVar[fieldName] = source.scenes[scId].kwVar[fieldName]
                except:
                    pass

        #--- Merge chapters.
        for chId in source.chapters:
            if not chId in self.chapters:
                self.chapters[chId] = self.CHAPTER_CLASS()

            if source.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                self.chapters[chId].title = source.chapters[chId].title

            if source.chapters[chId].desc is not None:
                self.chapters[chId].desc = source.chapters[chId].desc

            if source.chapters[chId].chLevel is not None:
                self.chapters[chId].chLevel = source.chapters[chId].chLevel

            if source.chapters[chId].chType is not None:
                self.chapters[chId].chType = source.chapters[chId].chType

            if source.chapters[chId].suppressChapterTitle is not None:
                self.chapters[chId].suppressChapterTitle = source.chapters[chId].suppressChapterTitle

            if source.chapters[chId].suppressChapterBreak is not None:
                self.chapters[chId].suppressChapterBreak = source.chapters[chId].suppressChapterBreak

            if source.chapters[chId].isTrash is not None:
                self.chapters[chId].isTrash = source.chapters[chId].isTrash

            for fieldName in self._CHP_KWVAR:
                try:
                    self.chapters[chId].kwVar[fieldName] = source.chapters[chId].kwVar[fieldName]
                except:
                    pass

            #--- Merge the chapter's scene list.
            # New scenes may be added.
            # Existing scenes may be moved to another chapter.
            # Deletion of scenes is not considered.
            # The scene's sort order may not change.

            # Remove scenes that have been moved to another chapter from the scene list.
            srtScenes = []
            for scId in self.chapters[chId].srtScenes:
                if scId in source.chapters[chId].srtScenes or not scId in source.scenes:
                    # The scene has not moved to another chapter or isn't imported
                    srtScenes.append(scId)
            self.chapters[chId].srtScenes = srtScenes

            # Add new or moved scenes to the scene list.
            merge_lists(source.chapters[chId].srtScenes, self.chapters[chId].srtScenes)

        #--- Merge project attributes.
        if source.title:
            # avoids deleting the title, if it is empty by accident
            self.title = source.title

        if source.desc is not None:
            self.desc = source.desc

        if source.authorName is not None:
            self.authorName = source.authorName

        if source.authorBio is not None:
            self.authorBio = source.authorBio

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4

        if source.languageCode is not None:
            self.languageCode = source.languageCode

        if source.countryCode is not None:
            self.countryCode = source.countryCode

        if source.languages is not None:
            self.languages = source.languages

        for fieldName in self._PRJ_KWVAR:
            try:
                self.kwVar[fieldName] = source.kwVar[fieldName]
            except:
                pass

        # Add new chapters to the chapter list.
        # Deletion of chapters is not considered.
        # The sort order of chapters may not change.
        merge_lists(source.srtChapters, self.srtChapters)

        # Split scenes by inserted part/chapter/scene dividers.
        # This must be done after regular merging
        # in order to avoid creating duplicate IDs.
        if sourceHasSceneContent:
            sceneSplitter = Splitter()
            self.scenesSplit = sceneSplitter.split_scenes(self)
        self.adjust_scene_types()
        return 'yWriter project data updated or created.'

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'

        if self.languages is None:
            self.get_languages()
        self._build_element_tree()
        message = self._write_element_tree(self)
        if message.startswith(ERROR):
            return message

        return self._postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def build_scene_subtree(xmlScn, prjScn):
            if prjScn.title is not None:
                try:
                    xmlScn.find('Title').text = prjScn.title
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Title').text = prjScn.title
            if xmlScn.find('BelongsToChID') is None:
                for chId in self.chapters:
                    if scId in self.chapters[chId].srtScenes:
                        ET.SubElement(xmlScn, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:
                try:
                    xmlScn.find('Desc').text = prjScn.desc
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Desc').text = prjScn.desc

            if xmlScn.find('SceneContent') is None:
                ET.SubElement(xmlScn, 'SceneContent').text = prjScn.sceneContent

            if xmlScn.find('WordCount') is None:
                ET.SubElement(xmlScn, 'WordCount').text = str(prjScn.wordCount)

            if xmlScn.find('LetterCount') is None:
                ET.SubElement(xmlScn, 'LetterCount').text = str(prjScn.letterCount)

            #--- Write scene type.
            #
            # This is how yWriter 7.1.3.0 writes the scene type:
            #
            # Type   |<Unused>|Field_SceneType>|scType
            #--------+--------+----------------+------
            # Normal | N/A    | N/A            | 0
            # Notes  | -1     | 1              | 1
            # Todo   | -1     | 2              | 2
            # Unused | -1     | 0              | 3

            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if prjScn.scType is None:
                prjScn.scType = 0
            yUnused, ySceneType = scTypeEncoding[prjScn.scType]

            # <Unused> (remove, if scene is "Normal").
            if yUnused:
                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'
            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            # <Fields><Field_SceneType> (remove, if scene is "Normal")
            scFields = xmlScn.find('Fields')
            if scFields is not None:
                fieldScType = scFields.find('Field_SceneType')
                if ySceneType is None:
                    if fieldScType is not None:
                        scFields.remove(fieldScType)
                else:
                    try:
                        fieldScType.text = ySceneType
                    except(AttributeError):
                        ET.SubElement(scFields, 'Field_SceneType').text = ySceneType
            elif ySceneType is not None:
                scFields = ET.SubElement(xmlScn, 'Fields')
                ET.SubElement(scFields, 'Field_SceneType').text = ySceneType

            #--- Write scene custom fields.
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar.get(field, None):
                    if scFields is None:
                        scFields = ET.SubElement(xmlScn, 'Fields')
                    try:
                        scFields.find(field).text = self.scenes[scId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(scFields, field).text = self.scenes[scId].kwVar[field]
                elif scFields is not None:
                    try:
                        scFields.remove(scFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScn.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScn, 'Status').text = str(prjScn.status)

            if prjScn.notes is not None:
                try:
                    xmlScn.find('Notes').text = prjScn.notes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Notes').text = prjScn.notes

            if prjScn.tags is not None:
                try:
                    xmlScn.find('Tags').text = list_to_string(prjScn.tags)
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Tags').text = list_to_string(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScn.find('Field1').text = prjScn.field1
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScn.find('Field2').text = prjScn.field2
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScn.find('Field3').text = prjScn.field3
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScn.find('Field4').text = prjScn.field4
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScn.find('AppendToPrev') is None:
                    ET.SubElement(xmlScn, 'AppendToPrev').text = '-1'
            elif xmlScn.find('AppendToPrev') is not None:
                xmlScn.remove(xmlScn.find('AppendToPrev'))

            # Date/time information
            if (prjScn.date is not None) and (prjScn.time is not None):
                dateTime = f'{prjScn.date} {prjScn.time}'
                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScn, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScn, 'SpecificDateMode').text = '-1'

                    if xmlScn.find('Day') is not None:
                        xmlScn.remove(xmlScn.find('Day'))

                    if xmlScn.find('Hour') is not None:
                        xmlScn.remove(xmlScn.find('Hour'))

                    if xmlScn.find('Minute') is not None:
                        xmlScn.remove(xmlScn.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.hour is not None) or (prjScn.minute is not None):

                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateTime'))

                if xmlScn.find('SpecificDateMode') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateMode'))
                if prjScn.day is not None:
                    try:
                        xmlScn.find('Day').text = prjScn.day
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Day').text = prjScn.day
                if prjScn.hour is not None:
                    try:
                        xmlScn.find('Hour').text = prjScn.hour
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Hour').text = prjScn.hour
                if prjScn.minute is not None:
                    try:
                        xmlScn.find('Minute').text = prjScn.minute
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Minute').text = prjScn.minute

            if prjScn.lastsDays is not None:
                try:
                    xmlScn.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScn.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScn.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.isReactionScene:
                if xmlScn.find('ReactionScene') is None:
                    ET.SubElement(xmlScn, 'ReactionScene').text = '-1'
            elif xmlScn.find('ReactionScene') is not None:
                xmlScn.remove(xmlScn.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScn.find('SubPlot') is None:
                    ET.SubElement(xmlScn, 'SubPlot').text = '-1'
            elif xmlScn.find('SubPlot') is not None:
                xmlScn.remove(xmlScn.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScn.find('Goal').text = prjScn.goal
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScn.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScn.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScn.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    ET.SubElement(xmlScn, 'ImageFile').text = prjScn.image

            #--- Characters/locations/items
            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')
                try:
                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)
                except(AttributeError):
                    characters = ET.SubElement(xmlScn, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(characters, 'CharID').text = crId

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')
                try:
                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)
                except(AttributeError):
                    locations = ET.SubElement(xmlScn, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(locations, 'LocID').text = lcId

            if prjScn.items is not None:
                items = xmlScn.find('Items')
                try:
                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)
                except(AttributeError):
                    items = ET.SubElement(xmlScn, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(items, 'ItemID').text = itId

        def build_chapter_subtree(xmlChp, prjChp, sortOrder):
            try:
                xmlChp.find('SortOrder').text = str(sortOrder)
            except(AttributeError):
                ET.SubElement(xmlChp, 'SortOrder').text = str(sortOrder)
            try:
                xmlChp.find('Title').text = prjChp.title
            except(AttributeError):
                ET.SubElement(xmlChp, 'Title').text = prjChp.title

            if prjChp.desc is not None:
                try:
                    xmlChp.find('Desc').text = prjChp.desc
                except(AttributeError):
                    ET.SubElement(xmlChp, 'Desc').text = prjChp.desc

            if xmlChp.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChp.remove(xmlChp.find('SectionStart'))
            elif prjChp.chLevel == 1:
                ET.SubElement(xmlChp, 'SectionStart').text = '-1'

            # This is how yWriter 7.1.3.0 writes the chapter type:
            #
            # Type   |<Unused>|<Type>|<ChapterType>|chType
            #--------+--------+------+-------------+------
            # Normal | N/A    | 0    | 0           | 0
            # Notes  | -1     | 1    | 1           | 1
            # Todo   | -1     | 1    | 2           | 2
            # Unused | -1     | 1    | 0           | 3

            chTypeEncoding = (
                (False, '0', '0'),
                (True, '1', '1'),
                (True, '1', '2'),
                (True, '1', '0'),
                )
            if prjChp.chType is None:
                prjChp.chType = 0
            yUnused, yType, yChapterType = chTypeEncoding[prjChp.chType]
            try:
                xmlChp.find('ChapterType').text = yChapterType
            except(AttributeError):
                ET.SubElement(xmlChp, 'ChapterType').text = yChapterType
            try:
                xmlChp.find('Type').text = yType
            except(AttributeError):
                ET.SubElement(xmlChp, 'Type').text = yType
            if yUnused:
                if xmlChp.find('Unused') is None:
                    ET.SubElement(xmlChp, 'Unused').text = '-1'
            elif xmlChp.find('Unused') is not None:
                xmlChp.remove(xmlChp.find('Unused'))

            #--- Write chapter fields.
            chFields = xmlChp.find('Fields')
            if prjChp.suppressChapterTitle:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterTitle').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterTitle') is not None:
                    chFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterBreak').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterBreak') is not None:
                    chFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_IsTrash').text = '1'
            elif chFields is not None:
                if chFields.find('Field_IsTrash') is not None:
                    chFields.remove(chFields.find('Field_IsTrash'))

            #--- Write chapter custom fields.
            for field in self._CHP_KWVAR:
                if prjChp.kwVar.get(field, None):
                    if chFields is None:
                        chFields = ET.SubElement(xmlChp, 'Fields')
                    try:
                        chFields.find(field).text = prjChp.kwVar[field]
                    except(AttributeError):
                        ET.SubElement(chFields, field).text = prjChp.kwVar[field]
                elif chFields is not None:
                    try:
                        chFields.remove(chFields.find(field))
                    except:
                        pass

            #--- Rebuild the chapter's scene list.
            try:
                xScnList = xmlChp.find('Scenes')
                xmlChp.remove(xScnList)
            except:
                pass
            if prjChp.srtScenes:
                sortSc = ET.SubElement(xmlChp, 'Scenes')
                for scId in prjChp.srtScenes:
                    ET.SubElement(sortSc, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc, sortOrder):
            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = list_to_string(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

            #--- Write location custom fields.
            lcFields = xmlLoc.find('Fields')
            for field in self._LOC_KWVAR:
                if self.locations[lcId].kwVar.get(field, None):
                    if lcFields is None:
                        lcFields = ET.SubElement(xmlLoc, 'Fields')
                    try:
                        lcFields.find(field).text = self.locations[lcId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(lcFields, field).text = self.locations[lcId].kwVar[field]
                elif lcFields is not None:
                    try:
                        lcFields.remove(lcFields.find(field))
                    except:
                        pass

        def build_prjNote_subtree(xmlPnt, prjPnt, sortOrder):
            if prjPnt.title is not None:
                ET.SubElement(xmlPnt, 'Title').text = prjPnt.title

            if prjPnt.desc is not None:
                ET.SubElement(xmlPnt, 'Desc').text = prjPnt.desc

            ET.SubElement(xmlPnt, 'SortOrder').text = str(sortOrder)

        def add_projectvariable(title, desc, tags):
            # Note:
            # prjVars, projectvars are caller's variables
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            # side effect
            projectvar = ET.SubElement(projectvars, 'PROJECTVAR')
            ET.SubElement(projectvar, 'ID').text = pvId
            ET.SubElement(projectvar, 'Title').text = title
            ET.SubElement(projectvar, 'Desc').text = desc
            ET.SubElement(projectvar, 'Tags').text = tags

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = list_to_string(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

            #--- Write item custom fields.
            itFields = xmlItm.find('Fields')
            for field in self._ITM_KWVAR:
                if self.items[itId].kwVar.get(field, None):
                    if itFields is None:
                        itFields = ET.SubElement(xmlItm, 'Fields')
                    try:
                        itFields.find(field).text = self.items[itId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(itFields, field).text = self.items[itId].kwVar[field]
                elif itFields is not None:
                    try:
                        itFields.remove(itFields.find(field))
                    except:
                        pass

        def build_character_subtree(xmlCrt, prjCrt, sortOrder):
            if prjCrt.title is not None:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title

            if prjCrt.desc is not None:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc

            if prjCrt.image is not None:
                ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image

            ET.SubElement(xmlCrt, 'SortOrder').text = str(sortOrder)

            if prjCrt.notes is not None:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes

            if prjCrt.aka is not None:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka

            if prjCrt.tags is not None:
                ET.SubElement(xmlCrt, 'Tags').text = list_to_string(prjCrt.tags)

            if prjCrt.bio is not None:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio

            if prjCrt.goals is not None:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals

            if prjCrt.fullName is not None:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName

            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'

            #--- Write character custom fields.
            crFields = xmlCrt.find('Fields')
            for field in self._CRT_KWVAR:
                if self.characters[crId].kwVar.get(field, None):
                    if crFields is None:
                        crFields = ET.SubElement(xmlCrt, 'Fields')
                    try:
                        crFields.find(field).text = self.characters[crId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(crFields, field).text = self.characters[crId].kwVar[field]
                elif crFields is not None:
                    try:
                        crFields.remove(crFields.find(field))
                    except:
                        pass

        def build_project_subtree(xmlPrj):
            VER = '7'
            try:
                xmlPrj.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlPrj, 'Ver').text = VER

            if self.title is not None:
                try:
                    xmlPrj.find('Title').text = self.title
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Title').text = self.title

            if self.desc is not None:
                try:
                    xmlPrj.find('Desc').text = self.desc
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Desc').text = self.desc

            if self.authorName is not None:
                try:
                    xmlPrj.find('AuthorName').text = self.authorName
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'AuthorName').text = self.authorName

            if self.authorBio is not None:
                try:
                    xmlPrj.find('Bio').text = self.authorBio
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Bio').text = self.authorBio

            if self.fieldTitle1 is not None:
                try:
                    xmlPrj.find('FieldTitle1').text = self.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle1').text = self.fieldTitle1

            if self.fieldTitle2 is not None:
                try:
                    xmlPrj.find('FieldTitle2').text = self.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle2').text = self.fieldTitle2

            if self.fieldTitle3 is not None:
                try:
                    xmlPrj.find('FieldTitle3').text = self.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle3').text = self.fieldTitle3

            if self.fieldTitle4 is not None:
                try:
                    xmlPrj.find('FieldTitle4').text = self.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle4').text = self.fieldTitle4

            if self.languageCode:
                self.kwVar['Field_LanguageCode'] = self.languageCode
            if self.countryCode:
                self.kwVar['Field_CountryCode'] = self.countryCode

            #--- Write project custom fields.

            # This is for projects written with v7.6 - v7.10:
            self.kwVar['Field_LanguageCode'] = None
            self.kwVar['Field_CountryCode'] = None

            prjFields = xmlPrj.find('Fields')
            for field in self._PRJ_KWVAR:
                setting = self.kwVar.get(field, None)
                if setting:
                    if prjFields is None:
                        prjFields = ET.SubElement(xmlPrj, 'Fields')
                    try:
                        prjFields.find(field).text = setting
                    except(AttributeError):
                        ET.SubElement(prjFields, field).text = setting
                else:
                    try:
                        prjFields.remove(prjFields.find(field))
                    except:
                        pass

        TAG = 'YWRITER7'
        xmlScenes = {}
        xmlChapters = {}
        try:
            # Try processing an existing tree.
            root = self.tree.getroot()
            xmlPrj = root.find('PROJECT')
            locations = root.find('LOCATIONS')
            items = root.find('ITEMS')
            characters = root.find('CHARACTERS')
            prjNotes = root.find('PROJECTNOTES')
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
            scenes = ET.SubElement(root, 'SCENES')
            chapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlPrj)

        #--- Process locations.

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.
        for xmlLoc in locations.findall('LOCATION'):
            locations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.
        sortOrder = 0
        for lcId in self.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId
            build_location_subtree(xmlLoc, self.locations[lcId], sortOrder)

        #--- Process items.

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.
        for xmlItm in items.findall('ITEM'):
            items.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.
        sortOrder = 0
        for itId in self.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(items, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId
            build_item_subtree(xmlItm, self.items[itId], sortOrder)

        #--- Process characters.

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.
        for xmlCrt in characters.findall('CHARACTER'):
            characters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.
        sortOrder = 0
        for crId in self.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId
            build_character_subtree(xmlCrt, self.characters[crId], sortOrder)

        #--- Process project notes.

        # Remove PROJECTNOTE entries in order to rewrite
        # the PROJECTNOTES section in a modified sort order.
        if prjNotes is not None:
            for xmlPnt in prjNotes.findall('PROJECTNOTE'):
                prjNotes.remove(xmlPnt)
            if not self.srtPrjNotes:
                root.remove(prjNotes)
        elif self.srtPrjNotes:
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
        if self.srtPrjNotes:
            # Add the new XML prjNote subtrees to the project tree.
            sortOrder = 0
            for pnId in self.srtPrjNotes:
                sortOrder += 1
                xmlPnt = ET.SubElement(prjNotes, 'PROJECTNOTE')
                ET.SubElement(xmlPnt, 'ID').text = pnId
                build_prjNote_subtree(xmlPnt, self.projectNotes[pnId], sortOrder)

        #--- Process project variables.
        if self.languages or self.languageCode or self.countryCode:
            self.check_locale()
            projectvars = root.find('PROJECTVARS')
            if projectvars is None:
                projectvars = ET.SubElement(root, 'PROJECTVARS')
            prjVars = []
            # list of all project variable IDs
            languages = self.languages.copy()
            hasLanguageCode = False
            hasCountryCode = False
            for projectvar in projectvars.findall('PROJECTVAR'):
                prjVars.append(projectvar.find('ID').text)
                title = projectvar.find('Title').text

                # Collect language codes.
                if title.startswith('lang='):
                    try:
                        __, langCode = title.split('=')
                        languages.remove(langCode)
                    except:
                        pass

                # Get the document's locale.
                elif title == 'Language':
                    projectvar.find('Desc').text = self.languageCode
                    hasLanguageCode = True

                elif title == 'Country':
                    projectvar.find('Desc').text = self.countryCode
                    hasCountryCode = True

            # Define project variables for the missing locale.
            if not hasLanguageCode:
                add_projectvariable('Language',
                                    self.languageCode,
                                    '0')

            if not hasCountryCode:
                add_projectvariable('Country',
                                    self.countryCode,
                                    '0')

            # Define project variables for the missing language code tags.
            for langCode in languages:
                add_projectvariable(f'lang={langCode}',
                                    f'<HTM <SPAN LANG="{langCode}"> /HTM>',
                                    '0')
                add_projectvariable(f'/lang={langCode}',
                                    f'<HTM </SPAN> /HTM>',
                                    '0')
                # adding new IDs to the prjVars list

        #--- Process scenes.

        # Save the original XML scene subtrees
        # and remove them from the project tree.
        for xmlScn in scenes.findall('SCENE'):
            scId = xmlScn.find('ID').text
            xmlScenes[scId] = xmlScn
            scenes.remove(xmlScn)

        # Add the new XML scene subtrees to the project tree.
        for scId in self.scenes:
            if not scId in xmlScenes:
                xmlScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlScenes[scId], self.scenes[scId])
            scenes.append(xmlScenes[scId])

        #--- Process chapters.

        # Save the original XML chapter subtree
        # and remove it from the project tree.
        for xmlChp in chapters.findall('CHAPTER'):
            chId = xmlChp.find('ID').text
            xmlChapters[chId] = xmlChp
            chapters.remove(xmlChp)

        # Add the new XML chapter subtrees to the project tree.
        sortOrder = 0
        for chId in self.srtChapters:
            sortOrder += 1
            if not chId in xmlChapters:
                xmlChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlChapters[chId], self.chapters[chId], sortOrder)
            chapters.append(xmlChapters[chId])

        # Modify the scene contents of an existing xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            if self.scenes[scId].sceneContent is not None:
                scn.find('SceneContent').text = self.scenes[scId].sceneContent
                scn.find('WordCount').text = str(self.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(self.scenes[scId].letterCount)
            try:
                scn.remove(scn.find('RTFFile'))
            except:
                pass

        indent(root)
        self.tree = ET.ElementTree(root)

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        if os.path.isfile(ywProject.filePath):
            os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            backedUp = True
        else:
            backedUp = False
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(ywProject.filePath)}".'

        return 'yWriter XML tree written.'

    def _postprocess_xml_file(self, filePath):
        '''Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath -- str: path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Return a message beginning with the ERROR constant in case of error.
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        '''
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(f'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(f'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(filePath)}".'

        return f'{_("File written")}: "{os.path.normpath(filePath)}".'

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def reset_custom_variables(self):
        """Set custom keyword variables to an empty string.
        
        Thus the write() method will remove the associated custom fields
        from the .yw7 XML file. 
        Return True, if a keyword variable has changed (i.e information is lost).
        """
        hasChanged = False
        for field in self._PRJ_KWVAR:
            if self.kwVar.get(field, None):
                self.kwVar[field] = ''
                hasChanged = True
        for chId in self.chapters:
            # Deliberatey not iterate srtChapters: make sure to get all chapters.
            for field in self._CHP_KWVAR:
                if self.chapters[chId].kwVar.get(field, None):
                    self.chapters[chId].kwVar[field] = ''
                    hasChanged = True
        for scId in self.scenes:
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar.get(field, None):
                    self.scenes[scId].kwVar[field] = ''
                    hasChanged = True
        return hasChanged

    def adjust_scene_types(self):
        """Make sure that scenes in non-"Normal" chapters inherit the chapter's type."""
        for chId in self.srtChapters:
            if self.chapters[chId].chType != 0:
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].scType = self.chapters[chId].chType

from html.parser import HTMLParser


def read_html_file(filePath):
    """Open a html file being encoded utf-8 or ANSI.
    
    Return a tuple:
    message = Message beginning with the ERROR constant in case of error.
    content = The file content in a single string. None in case of error.
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        try:
            with open(filePath, 'r') as f:
                content = (f.read())
        except(FileNotFoundError):
            return f'{ERROR}{_("File not found")}: "{os.path.normpath(filePath)}".', None

    return 'HTML data read in.', content


class HtmlFile(Novel, HTMLParser):
    """Generic HTML file representation.
    
    Public methods:
        handle_starttag -- identify scenes and chapters.
        handle comment --
        read --
    """
    EXTENSION = '.html'
    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def __init__(self, filePath, **kwargs):
        """Initialize the HTML parser and local instance variables for parsing.
        
        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        The HTML parser works like a state machine. 
        Scene ID, chapter ID and processed lines must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        HTMLParser.__init__(self)
        self._lines = []
        self._scId = None
        self._chId = None
        self._newline = False
        self._language = ''
        self._doNothing = False

    def _convert_to_yw(self, text):
        """Convert html formatting tags to yWriter 7 raw markup.
        
        Positional arguments:
            text -- string to convert.
        
        Return a yw7 markup string.
        Overrides the superclass method.
        """
        #--- Put everything in one line.
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')

        return text

    def _preprocess(self, text):
        """Process HTML text before parsing.
        
        Positional arguments:
            text -- str: HTML text to be processed.
        """
        return self._convert_to_yw(text)

    def _postprocess(self):
        """Process the plain text after parsing.
        
        This is a hook for subclasses.
        """

    def handle_starttag(self, tag, attrs):
        """Identify scenes and chapters.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides HTMLparser.handle_starttag() called by the parser to handle the start of a tag. 
        This method is applicable to HTML files that are divided into chapters and scenes. 
        For differently structured HTML files  do override this method in a subclass.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('ScID'):
                    self._scId = re.search('[0-9]+', attrs[0][1]).group()
                    self.scenes[self._scId] = self.SCENE_CLASS()
                    self.chapters[self._chId].srtScenes.append(self._scId)
                elif attrs[0][1].startswith('ChID'):
                    self._chId = re.search('[0-9]+', attrs[0][1]).group()
                    self.chapters[self._chId] = self.CHAPTER_CLASS()
                    self.chapters[self._chId].srtScenes = []
                    self.srtChapters.append(self._chId)

    def handle_comment(self, data):
        """Process inline comments within scene content.
        
        Positional arguments:
            data -- str: comment text. 
        
        Overrides HTMLparser.handle_comment() called by the parser when a comment is encountered.
        """
        if self._scId is not None:
            self._lines.append(f'{self._COMMENT_START}{data}{self._COMMENT_END}')

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a template method for subclasses tailored to the 
        content of the respective HTML file.
        """
        message, content = read_html_file(self._filePath)
        if message.startswith(ERROR):
            return message

        content = self._preprocess(content)
        self.feed(content)
        self._postprocess()
        return 'Created novel structure from HTML data.'


class HtmlFormatted(HtmlFile):
    """HTML file representation.

    Provide methods and data for processing chapters with formatted text.
    """
    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def __init__(self, filePath, **kwargs):
        """Add instance variables.

        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.languages = []

    def _cleanup_scene(self, text):
        """Clean up yWriter markup.
        
        Positional arguments:
            text -- string to clean up.
        
        Return a yw7 markup string.
        """
        #--- Remove redundant tags.
        # In contrast to Office Writer, yWriter accepts markup reaching across linebreaks.
        tags = ['i', 'b']
        for language in self.languages:
            tags.append(f'lang={language}')
        for tag in tags:
            text = text.replace(f'[/{tag}][{tag}]', '')
            text = text.replace(f'[/{tag}]\n[{tag}]', '\n')
            text = text.replace(f'[/{tag}]\n> [{tag}]', '\n> ')

        #--- Remove misplaced formatting tags.
        # text = re.sub('\[\/*[b|i]\]', '', text)
        return text



class HtmlImport(HtmlFormatted):
    """HTML 'work in progress' file representation.

    Import untagged chapters and scenes.
    """
    DESCRIPTION = _('Work in progress')
    SUFFIX = ''
    _SCENE_DIVIDER = '* * *'
    _LOW_WORDCOUNT = 10

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The HTML parser works like a state machine. 
        Chapter and scene count must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'p':
            if self._scId is None and self._chId is not None:
                self._lines = []
                self._scCount += 1
                self._scId = str(self._scCount)
                self.scenes[self._scId] = self.SCENE_CLASS()
                self.chapters[self._chId].srtScenes.append(self._scId)
                self.scenes[self._scId].status = '1'
                self.scenes[self._scId].title = f'Scene {self._scCount}'
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.languages:
                        self.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass
        elif tag == 'br':
            self._newline = True
        elif tag == 'em' or tag == 'i':
            self._lines.append('[i]')
        elif tag == 'strong' or tag == 'b':
            self._lines.append('[b]')
        elif tag == 'span':
            if attrs[0][0] == 'lang':
                self._language = attrs[0][1]
                if not self._language in self.languages:
                    self.languages.append(self._language)
                self._lines.append(f'[lang={self._language}]')
        elif tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.chapters[self._chId] = self.CHAPTER_CLASS()
            self.chapters[self._chId].srtScenes = []
            self.srtChapters.append(self._chId)
            self.chapters[self._chId].chType = 0
            if tag == 'h1':
                self.chapters[self._chId].chLevel = 1
            else:
                self.chapters[self._chId].chLevel = 0
        elif tag == 'div':
            self._scId = None
            self._chId = None
        elif tag == 'meta':
            if attrs[0][1].lower() == 'author':
                self.authorName = attrs[1][1]
            if attrs[0][1].lower() == 'description':
                self.desc = attrs[1][1]
        elif tag == 'title':
            self._lines = []
        elif tag == 'body':
            for attr in attrs:
                if attr[0] == 'lang':
                    try:
                        lngCode, ctrCode = attr[1].split('-')
                        self.languageCode = lngCode
                        self.countryCode = ctrCode
                    except:
                        pass
                    break
        elif tag == 'li':
                self._lines.append(f'{self._BULLET} ')
        elif tag == 'ul':
                self._doNothing = True
        elif tag == 'blockquote':
            self._lines.append(f'{self._INDENT} ')
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.languages:
                        self.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides HTMLparser.handle_endtag() called by the HTML parser to handle the end tag of an element.
        """
        if tag in ('p', 'blockquote'):
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''
            self._lines.append('\n')
            self._newline = True
            if self._scId is not None:
                sceneText = ''.join(self._lines).rstrip()
                sceneText = self._cleanup_scene(sceneText)
                self.scenes[self._scId].sceneContent = sceneText
                if self.scenes[self._scId].wordCount < self._LOW_WORDCOUNT:
                    self.scenes[self._scId].status = self.SCENE_CLASS.STATUS.index('Outline')
                else:
                    self.scenes[self._scId].status = self.SCENE_CLASS.STATUS.index('Draft')
        elif tag == 'em' or tag == 'i':
            self._lines.append('[/i]')
        elif tag == 'strong' or tag == 'b':
            self._lines.append('[/b]')
        elif tag == 'span':
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''
        elif tag in ('h1', 'h2'):
            self.chapters[self._chId].title = ''.join(self._lines)
            self._lines = []
        elif tag == 'title':
            self.title = ''.join(self._lines)

    def handle_comment(self, data):
        """Process inline comments within scene content.
        
        Positional arguments:
            data -- str: comment text. 
        
        Use marked comments at scene start as scene titles.
        Overrides HTMLparser.handle_comment() called by the parser when a comment is encountered.
        """
        if self._scId is not None:
            if not self._lines:
                # Comment is at scene start
                try:
                    self.scenes[self._scId].title = data.strip()
                except:
                    pass
                return

            self._lines.append(f'{self._COMMENT_START}{data.strip()}{self._COMMENT_END}')

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides HTMLparser.handle_data() called by the parser to process arbitrary data.
        """
        if self._doNothing:
            self._doNothing = False
        elif self._scId is not None and self._SCENE_DIVIDER in data:
            self._scId = None
        else:
            if self._newline:
                data = data.rstrip()
                self._newline = False
            self._lines.append(data)


class HtmlOutline(HtmlFile):
    """HTML outline file representation.

    Import an outline without chapter and scene tags.
    """
    DESCRIPTION = _('Novel outline')
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The HTML parser works like a state machine. 
        Chapter and scene count must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.chapters[self._chId] = self.CHAPTER_CLASS()
            self.chapters[self._chId].srtScenes = []
            self.srtChapters.append(self._chId)
            self.chapters[self._chId].chType = 0
            if tag == 'h1':
                self.chapters[self._chId].chLevel = 1
            else:
                self.chapters[self._chId].chLevel = 0
        elif tag == 'h3':
            self._lines = []
            self._scCount += 1
            self._scId = str(self._scCount)
            self.scenes[self._scId] = self.SCENE_CLASS()
            self.chapters[self._chId].srtScenes.append(self._scId)
            self.scenes[self._scId].sceneContent = ''
            self.scenes[self._scId].status = self.SCENE_CLASS.STATUS.index('Outline')
        elif tag == 'div':
            self._scId = None
            self._chId = None
        elif tag == 'meta':
            if attrs[0][1].lower() == 'author':
                self.authorName = attrs[1][1]
            if attrs[0][1].lower() == 'description':
                self.desc = attrs[1][1]
        elif tag == 'title':
            self._lines = []
        elif tag == 'body':
            for attr in attrs:
                if attr[0].lower() == 'lang':
                    try:
                        lngCode, ctrCode = attr[1].split('-')
                        self.languageCode = lngCode
                        self.countryCode = ctrCode
                    except:
                        pass
                    break

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if tag == 'p':
            self._lines.append('\n')
            if self._scId is not None:
                self.scenes[self._scId].desc = ''.join(self._lines)
            elif self._chId is not None:
                self.chapters[self._chId].desc = ''.join(self._lines)
        elif tag in ('h1', 'h2'):
            self.chapters[self._chId].title = ''.join(self._lines)
            self._lines = []
        elif tag == 'h3':
            self.scenes[self._scId].title = ''.join(self._lines)
            self._lines = []
        elif tag == 'title':
            self.title = ''.join(self._lines)

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        self._lines.append(data.strip())


class NewProjectFactory(FileFactory):
    """A factory class that instantiates a document object to read, 
    and a new yWriter project.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.

    Class constant:
        DO_NOT_IMPORT -- list of suffixes from file classes not meant to be imported.    
    """
    DO_NOT_IMPORT = ['_xref', '_brf_synopsis']

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source and a target object for creation of a new yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance
        """
        if not self._canImport(sourcePath):
            return f'{ERROR}{_("This document is not meant to be written back")}.', None, None

        fileName, __ = os.path.splitext(sourcePath)
        targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
        if sourcePath.endswith('.html'):
            # The source file might be an outline or a "work in progress".
            message, content = read_html_file(sourcePath)
            if message.startswith(ERROR):
                return message, None, None

            if "<h3" in content.lower():
                sourceFile = HtmlOutline(sourcePath, **kwargs)
            else:
                sourceFile = HtmlImport(sourcePath, **kwargs)
            return 'Source and target objects created.', sourceFile, targetFile

        else:
            for fileClass in self._fileClasses:
                if fileClass.SUFFIX is not None:
                    if sourcePath.endswith(f'{fileClass.SUFFIX}{fileClass.EXTENSION}'):
                        sourceFile = fileClass(sourcePath, **kwargs)
                        return 'Source and target objects created.', sourceFile, targetFile

            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(sourcePath)}".', None, None

    def _canImport(self, sourcePath):
        """Check whether the source file can be imported to yWriter.
        
        Positional arguments: 
            sourcePath -- str: path of the file to be ckecked.
        
        Return True, if the file located at sourcepath is of an importable type.
        Otherwise, return False.
        """
        fileName, __ = os.path.splitext(sourcePath)
        for suffix in self.DO_NOT_IMPORT:
            if fileName.endswith(suffix):
                return False

        return True


from string import Template


class Filter:
    """Filter an entity (chapter/scene/character/location/item) by filter criteria.
    
    Public methods:
        accept(source, eId) -- check whether an entity matches the filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- Novel instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    
    Public methods:
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the export file.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _notesPartTemplate = ''
    _todoPartTemplate = ''
    _notesChapterTemplate = ''
    _todoChapterTemplate = ''
    _unusedChapterTemplate = ''
    _notExportedChapterTemplate = ''
    _sceneTemplate = ''
    _firstSceneTemplate = ''
    _appendedSceneTemplate = ''
    _notesSceneTemplate = ''
    _todoSceneTemplate = ''
    _unusedSceneTemplate = ''
    _notExportedSceneTemplate = ''
    _sceneDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _notExportedChapterEndTemplate = ''
    _notesChapterEndTemplate = ''
    _todoChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''
    _projectNoteTemplate = ''

    _DIVIDER = ', '

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._sceneFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if source.title is not None:
            self.title = source.title
        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc
        else:
            self.desc = ''

        if source.authorName is not None:
            self.authorName = source.authorName
        else:
            self.authorName = ''

        if source.authorBio is not None:
            self.authorBio = source.authorBio
        else:
            self.authorBio = ''

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1
        else:
            self.fieldTitle1 = 'Field 1'

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2
        else:
            self.fieldTitle2 = 'Field 2'

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3
        else:
            self.fieldTitle3 = 'Field 3'

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4
        else:
            self.fieldTitle4 = 'Field 4'

        if source.srtChapters:
            self.srtChapters = source.srtChapters

        if source.scenes is not None:
            self.scenes = source.scenes

        if source.chapters is not None:
            self.chapters = source.chapters

        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters

        if source.srtLocations:
            self.srtLocations = source.srtLocations
            self.locations = source.locations

        if source.srtItems:
            self.srtItems = source.srtItems
            self.items = source.items

        if source.srtPrjNotes:
            self.srtPrjNotes = source.srtPrjNotes
            self.projectNotes = source.projectNotes

        if source.kwVar:
            self.kwVar = source.kwVar

        if source.languageCode is not None:
            self.languageCode = source.languageCode

        if source.countryCode is not None:
            self.countryCode = source.countryCode

        if source.languages is not None:
            self.languages = source.languages

        return 'Export data updated from novel.'

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_yw(self.title, True),
            Desc=self._convert_from_yw(self.desc),
            AuthorName=self._convert_from_yw(self.authorName, True),
            AuthorBio=self._convert_from_yw(self.authorBio, True),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
        )
        return projectTemplateMapping

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_yw(self.chapters[chId].title, True),
            Desc=self._convert_from_yw(self.chapters[chId].desc),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section.
        
        Positional arguments:
            scId -- str: scene ID.
            sceneNumber -- int: scene number to be displayed.
            wordsTotal -- int: accumulated wordcount.
            lettersTotal -- int: accumulated lettercount.
        
        This is a template method that can be extended or overridden by subclasses.
        """

        #--- Create a comma separated tag list.
        if sceneNumber == 0:
            sceneNumber = ''
        if self.scenes[scId].tags is not None:
            tags = list_to_string(self.scenes[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []
            for crId in self.scenes[scId].characters:
                sChList.append(self.characters[crId].title)
            sceneChars = list_to_string(sChList, divider=self._DIVIDER)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)
            sceneLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sceneLocs = ''

        #--- Create a comma separated item list.
        if self.scenes[scId].items is not None:
            sItList = []
            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)
            sceneItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sceneItems = ''

        #--- Create A/R marker string.
        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

        #--- Create a combined scDate information.
        if self.scenes[scId].date is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scDay = ''
            scDate = self.scenes[scId].date
            cmbDate = self.scenes[scId].date
        else:
            scDate = ''
            if self.scenes[scId].day is not None:
                scDay = self.scenes[scId].day
                cmbDate = f'Day {self.scenes[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Create a combined time information.
        if self.scenes[scId].time is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scHour = ''
            scMinute = ''
            scTime = self.scenes[scId].time
            cmbTime = self.scenes[scId].time.rsplit(':', 1)[0]
        else:
            scTime = ''
            if self.scenes[scId].hour or self.scenes[scId].minute:
                if self.scenes[scId].hour:
                    scHour = self.scenes[scId].hour
                else:
                    scHour = '00'
                if self.scenes[scId].minute:
                    scMinute = self.scenes[scId].minute
                else:
                    scMinute = '00'
                cmbTime = f'{scHour.zfill(2)}:{scMinute.zfill(2)}'
            else:
                scHour = ''
                scMinute = ''
                cmbTime = ''

        #--- Create a combined duration information.
        if self.scenes[scId].lastsDays is not None and self.scenes[scId].lastsDays != '0':
            lastsDays = self.scenes[scId].lastsDays
            days = f'{self.scenes[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.scenes[scId].lastsHours is not None and self.scenes[scId].lastsHours != '0':
            lastsHours = self.scenes[scId].lastsHours
            hours = f'{self.scenes[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.scenes[scId].lastsMinutes is not None and self.scenes[scId].lastsMinutes != '0':
            lastsMinutes = self.scenes[scId].lastsMinutes
            minutes = f'{self.scenes[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self._convert_from_yw(self.scenes[scId].title, True),
            Desc=self._convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self._convert_from_yw(self.scenes[scId].sceneContent),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=scDate,
            Time=scTime,
            Day=scDay,
            Hour=scHour,
            Minute=scMinute,
            ScDate=cmbDate,
            ScTime=cmbTime,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self._convert_from_yw(self.scenes[scId].goal),
            Conflict=self._convert_from_yw(self.scenes[scId].conflict),
            Outcome=self._convert_from_yw(self.scenes[scId].outcome),
            Tags=self._convert_from_yw(tags, True),
            Image=self.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self._convert_from_yw(self.scenes[scId].notes),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return sceneMapping

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId -- str: character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.characters[crId].tags is not None:
            tags = list_to_string(self.characters[crId].tags, divider=self._DIVIDER)
        else:
            tags = ''
        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_yw(self.characters[crId].title, True),
            Desc=self._convert_from_yw(self.characters[crId].desc),
            Tags=self._convert_from_yw(tags),
            Image=self.characters[crId].image,
            AKA=self._convert_from_yw(self.characters[crId].aka, True),
            Notes=self._convert_from_yw(self.characters[crId].notes),
            Bio=self._convert_from_yw(self.characters[crId].bio),
            Goals=self._convert_from_yw(self.characters[crId].goals),
            FullName=self._convert_from_yw(self.characters[crId].fullName, True),
            Status=characterStatus,
            ProjectName=self._convert_from_yw(self.projectName),
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId -- str: location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.locations[lcId].tags is not None:
            tags = list_to_string(self.locations[lcId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_yw(self.locations[lcId].title, True),
            Desc=self._convert_from_yw(self.locations[lcId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.locations[lcId].image,
            AKA=self._convert_from_yw(self.locations[lcId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId -- str: item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.items[itId].tags is not None:
            tags = list_to_string(self.items[itId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_yw(self.items[itId].title, True),
            Desc=self._convert_from_yw(self.items[itId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.items[itId].image,
            AKA=self._convert_from_yw(self.items[itId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_prjNoteMapping(self, pnId):
        """Return a mapping dictionary for a project note.
        
        Positional arguments:
            pnId -- str: project note ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        itemMapping = dict(
            ID=pnId,
            Title=self._convert_from_yw(self.projectNotes[pnId].title, True),
            Desc=self._convert_from_yw(self.projectNotes[pnId].desc, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_fileHeader(self):
        """Process the file header.
        
        Apply the file header template, substituting placeholders 
        according to the file header mapping dictionary.
        Return a list of strings.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        
        Positional arguments:
            chId -- str: chapter ID.
            sceneNumber -- int: number of previously processed scenes.
            wordsTotal -- int: accumulated wordcount of the previous scenes.
            lettersTotal -- int: accumulated lettercount of the previous scenes.
            doNotExport -- bool: scene belongs to a chapter that is not to be exported.
        
        Iterate through a sorted scene list and apply the templates, 
        substituting placeholders according to the scene mapping dictionary.
        Skip scenes not accepted by the scene filter.
        
        Return a tuple:
            lines -- list of strings: the lines of the processed scene.
            sceneNumber -- int: number of all processed scenes.
            wordsTotal -- int: accumulated wordcount of all processed scenes.
            lettersTotal -- int: accumulated lettercount of all processed scenes.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSceneInChapter = True
        for scId in self.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue

            sceneContent = self.scenes[scId].sceneContent
            if sceneContent is None:
                sceneContent = ''

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.
            if self.scenes[scId].scType == 2:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].scType == 1:
                # Scene is "Notes" type.
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].scType == 3 or self.chapters[chId].chType == 3:
                if self._unusedSceneTemplate:
                    template = Template(self._unusedSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:
                if self._notExportedSceneTemplate:
                    template = Template(self._notExportedSceneTemplate)
                else:
                    continue

            elif sceneContent.startswith('<HTML>'):
                continue

            elif sceneContent.startswith('<TEX>'):
                continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount
                template = Template(self._sceneTemplate)
                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self._appendedSceneTemplate:
                    template = Template(self._appendedSceneTemplate)
            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self._sceneDivider)
            if firstSceneInChapter and self._firstSceneTemplate:
                template = Template(self._firstSceneTemplate)
            lines.append(template.safe_substitute(self._get_sceneMapping(
                        scId, dispNumber, wordsTotal, lettersTotal)))
            firstSceneInChapter = False
        return lines, sceneNumber, wordsTotal, lettersTotal

    def _get_chapters(self):
        """Process the chapters and nested scenes.
        
        Iterate through the sorted chapter list and apply the templates, 
        substituting placeholders according to the chapter mapping dictionary.
        For each chapter call the processing of its included scenes.
        Skip chapters not accepted by the chapter filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0
        for chId in self.srtChapters:
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.
            # Has the chapter only scenes not to be exported?
            sceneCount = 0
            notExportCount = 0
            doNotExport = False
            template = None
            for scId in self.chapters[chId].srtScenes:
                sceneCount += 1
                if self.scenes[scId].doNotExport:
                    notExportCount += 1
            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True
            if self.chapters[chId].chType == 2:
                # Chapter is "Todo" type.
                if self.chapters[chId].chLevel == 1:
                    # Chapter is "Todo Part" type.
                    if self._todoPartTemplate:
                        template = Template(self._todoPartTemplate)
                elif self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type.
                if self.chapters[chId].chLevel == 1:
                    # Chapter is "Notes Part" type.
                    if self._notesPartTemplate:
                        template = Template(self._notesPartTemplate)
                elif self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.chapters[chId].chType == 3:
                # Chapter is "unused" type.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif doNotExport:
                if self._notExportedChapterTemplate:
                    template = Template(self._notExportedChapterTemplate)
            elif self.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            #--- Process scenes.
            sceneLines, sceneNumber, wordsTotal, lettersTotal = self._get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            #--- Process chapter ending.
            template = None
            if self.chapters[chId].chType == 2:
                if self._todoChapterEndTemplate:
                    template = Template(self._todoChapterEndTemplate)
            elif self.chapters[chId].chType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif self.chapters[chId].chType == 3:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif doNotExport:
                if self._notExportedChapterEndTemplate:
                    template = Template(self._notExportedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characters(self):
        """Process the characters.
        
        Iterate through the sorted character list and apply the template, 
        substituting placeholders according to the character mapping dictionary.
        Skip characters not accepted by the character filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_locations(self):
        """Process the locations.
        
        Iterate through the sorted location list and apply the template, 
        substituting placeholders according to the location mapping dictionary.
        Skip locations not accepted by the location filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_items(self):
        """Process the items. 
        
        Iterate through the sorted item list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_projectNotes(self):
        """Process the project notes. 
        
        Iterate through the sorted project note list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.srtPrjNotes:
            map = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(map))
        return lines

    def _get_text(self):
        """Call all processing methods.
        
        Return a string to be written to the output file.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_projectNotes())
        lines.append(self._fileFooter)
        return ''.join(lines)

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message beginning with the ERROR constant in case of error.
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
                backedUp = True
            except:
                return f'{ERROR}{_("Cannot overwrite file")}: "{os.path.normpath(self.filePath)}".'

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(self.filePath)}".'

        return f'{_("File written")}: "{os.path.normpath(self.filePath)}".'

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text is None:
            text = ''
        return(text)

    def _remove_inline_code(self, text):
        """Remove inline raw code from text and return the result."""
        if text:
            text = text.replace('<RTFBRK>', '')
            YW_SPECIAL_CODES = ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg')
            for specialCode in YW_SPECIAL_CODES:
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)
        else:
            text = ''
        return text


class MdFile(FileExport):
    """Markdown file representation.

    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = 'Markdown file'
    EXTENSION = '.md'
    SUFFIX = ''
    SCENE_DIVIDER = '* * *'
    _fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''
    _partTemplate = '\n# ${Title}\n\n'
    _chapterTemplate = '\n## ${Title}\n\n'
    _sceneTemplate = '<!---${Title}--->${SceneContent}\n\n'
    _sceneDivider = f'\n\n{SCENE_DIVIDER}\n\n'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            markdown_mode -- bool: if True, the scenes in the yWriter project are Markdown formatted.
            scene_titles -- bool: if True, associate comments at the beginning of the scene with scene titles
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._markdownMode = kwargs['markdown_mode']
        self._sceneTitles = kwargs['scene_titles']
        if not self._sceneTitles:
            self._sceneTemplate = self._sceneTemplate.replace('<!---${Title}--->', '')

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        Suppress the chapter title if necessary.
        Extends the superclass method.
        """
        chapterMapping = super()._get_chapterMapping(chId, chapterNumber)
        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''
        return chapterMapping

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to Markdown.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if quick:
            # Just clean up a one-liner without sophisticated formatting.
            if text is None:
                return ''
            else:
                return text

        MD_REPLACEMENTS = [
            ('[i] ', ' [i]'),
            ('[b] ', ' [b]'),
            ('[s] ', ' [s]'),
            ('[i]', '*'),
            ('[/i]', '*'),
            ('[b]', '**'),
            ('[/b]', '**'),
            ('/*', '<!---'),
            ('*/', '--->'),
            ('  ', ' '),
        ]
        if not self._markdownMode:
            MD_REPLACEMENTS.insert(0, ('\n', '\n\n'))
        try:
            for yw, md in MD_REPLACEMENTS:
                text = text.replace(yw, md)
            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
            # Remove highlighting, alignment, and underline tags
        except AttributeError:
            text = ''
        return text

    def _convert_to_yw(self, text):
        """Convert Markdown to yWriter 7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        Return a yw7 markup string.
        Overrides the superclass method.
        """
        if not self._markdownMode:
            text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
            text = re.sub('\*([^ ].+?[^ ])\*', '[i]\\1[/i]', text)
            MD_REPLACEMENTS = [
                ('\n\n', '\n'),
                ('<!---', '/*'),
                ('--->', '*/'),
            ]
            try:
                for md, yw in MD_REPLACEMENTS:
                    text = text.replace(md, yw)
            except AttributeError:
                text = ''
        return text

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        LOW_WORDCOUNT = 10
        # Defines the difference between "Outline" and "Draft"

        def write_scene_content(scId, lines):
            if scId is not None:
                text = '\n'.join(lines)
                self.scenes[scId].sceneContent = text
                if self.scenes[scId].wordCount < LOW_WORDCOUNT:
                    self.scenes[scId].status = Scene.STATUS.index('Outline')
                else:
                    self.scenes[scId].status = Scene.STATUS.index('Draft')

        chCount = 0
        scCount = 0
        lines = []
        chId = None
        scId = None
        try:
            with open(self.filePath, encoding='utf-8') as f:
                mdText = f.read()
                cnvText = self._convert_to_yw(mdText)
                mdLines = (cnvText).split('\n')
        except(FileNotFoundError):
            return f'{ERROR}"{os.path.normpath(self.filePath)}" not found.'

        except:
            return f'{ERROR}Can not parse "{os.path.normpath(self.filePath)}".'

        if self._markdownMode:
            commentStart = '<!---'
            commentEnd = '--->'
        else:
            commentStart = '/*'
            commentEnd = '*/'
        for mdLine in mdLines:
            if mdLine.startswith('#'):

                # Write previous scene.
                write_scene_content(scId, lines)
                scId = None

                # Add a chapter.
                chCount += 1
                chId = str(chCount)
                self.chapters[chId] = Chapter()
                title = mdLine.split('# ')[1]
                self.chapters[chId].title = title
                self.srtChapters.append(chId)
                self.chapters[chId].chType = 0
                if mdLine.startswith('# '):
                    self.chapters[chId].chLevel = 1
                else:
                    self.chapters[chId].chLevel = 0
                self.chapters[chId].srtScenes = []
            elif self.SCENE_DIVIDER in mdLine:
                # Write previous scene.
                write_scene_content(scId, lines)
                scId = None
            elif scId is not None:
                lines.append(mdLine)
            elif mdLine and chId is not None:
                # Add a scene; drop the first line if empty.
                scCount += 1
                scId = str(scCount)
                self.scenes[scId] = Scene()
                self.chapters[chId].srtScenes.append(scId)
                self.scenes[scId].status = '1'
                self.scenes[scId].title = f'Scene {scCount}'
                if self._sceneTitles and mdLine.startswith(commentStart):
                    # The scene title is prefixed as a comment.
                    try:
                        scTitle, scContent = mdLine.split(
                            sep=commentEnd, maxsplit=1)
                        self.scenes[scId].title = scTitle.lstrip(commentStart)
                        lines = [scContent]
                    except:
                        lines = [mdLine]
                else:
                    lines = [mdLine]
        return 'Markdown formatted text converted to novel structure.'


class MdConverter(YwCnvFf):
    """A converter class for Markdown export."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [MdFile]
    CREATE_SOURCE_CLASSES = [MdFile]

    def __init__(self):
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


class MainTk(Ui):
    """A tkinter GUI root class.

    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        start() -- start the Tk main loop.
        select_project(self, fileName) -- return a project file path.
        open_project(fileName) -- create a yWriter project instance and read the file.
        close_project() -- close the yWriter project without saving and reset the user interface.
        ask_yes_no(text) -- query yes or no with a pop-up box.
        set_info_how(message) -- show how the converter is doing.
        show_status(message) -- put text on the status bar.
        show_path(message) -- put text on the path bar."
        restore_status() -- overwrite error message with the status before.
        on_quit() -- save keyword arguments before exiting the program.
        show_warning(message) -- Display a warning message box.
        
    Public instance variables: 
        title -- str: Application title.
        statusText -- str: Text to be displayed at the status bar.
        kwargs -- keyword arguments buffer.
        ywPrj -- yWriter project to work with.
        root -- tk top level window.
        mainMenu -- top level menubar.
        mainWindow -- tk frame in the top level window.
        statusBar -- tk label in the top level window.
        pathBar -- tk label in the top level window.
        fileMenu -- "File" submenu in main menu. 
    """
    _KEY_RESTORE_STATUS = ('<Escape>', 'Esc')
    _KEY_OPEN_PROJECT = ('<Control-o>', 'Ctrl-O')
    _KEY_QUIT_PROGRAM = ('<Control-q>', 'Ctrl-Q')
    _YW_CLASS = Yw7File

    def __init__(self, title, **kwargs):
        """Initialize the GUI window and instance variables.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
         
        Required keyword arguments:
            yw_last_open -- str: initial file.
            root_geometry -- str: geometry of the root window.
        
        Operation:
        - Create a main menu to be extended by subclasses.
        - Create a title bar for the project title.
        - Open a main window frame to be used by subclasses.
        - Create a status bar to be used by subclasses.
        - Create a path bar for the project file path.
        
        Extends the superclass constructor.
        """
        super().__init__(title)
        self._fileTypes = [(_('yWriter 7 project'), '.yw7')]
        self.title = title
        self._statusText = ''
        self.kwargs = kwargs
        self.ywPrj = None
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.root.title(title)
        if kwargs['root_geometry']:
            self.root.geometry(kwargs['root_geometry'])
        self.mainMenu = tk.Menu(self.root)

        self._build_main_menu()
        # Hook for subclasses

        self.root.config(menu=self.mainMenu)
        self.mainWindow = tk.Frame()
        self.mainWindow.pack(expand=True, fill='both')
        self.statusBar = tk.Label(self.root, text='', anchor='w', padx=5, pady=2)
        self.statusBar.pack(expand=False, fill='both')
        self.pathBar = tk.Label(self.root, text='', anchor='w', padx=5, pady=3)
        self.pathBar.pack(expand=False, fill='both')

        #--- Event bindings.
        self.root.bind(self._KEY_RESTORE_STATUS[0], self.restore_status)
        self.root.bind(self._KEY_OPEN_PROJECT[0], self._open_project)
        self.root.bind(self._KEY_QUIT_PROGRAM[0], self.on_quit)

    def _build_main_menu(self):
        """Add main menu entries.
        
        This is a template method that can be overridden by subclasses. 
        """
        self.fileMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('File'), menu=self.fileMenu)
        self.fileMenu.add_command(label=_('Open...'), accelerator=self._KEY_OPEN_PROJECT[1], command=lambda: self.open_project(''))
        self.fileMenu.add_command(label=_('Close'), command=self.close_project)
        self.fileMenu.entryconfig(_('Close'), state='disabled')
        self.fileMenu.add_command(label=_('Exit'), accelerator=self._KEY_QUIT_PROGRAM[1], command=self.on_quit)

    def disable_menu(self):
        """Disable menu entries when no project is open.
        
        To be extended by subclasses.
        """
        self.fileMenu.entryconfig(_('Close'), state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open.
        
        To be extended by subclasses.
        """
        self.fileMenu.entryconfig(_('Close'), state='normal')

    def start(self):
        """Start the Tk main loop.
        
        Note: This can not be done in the constructor method.
        """
        self.root.mainloop()

    def select_project(self, fileName):
        """Return a project file path.

        Positional arguments:
            fileName -- str: project file path.
            
        Optional arguments:
            fileTypes -- list of tuples for file selection (display text, extension).

        Priority:
        1. use file name argument
        2. open file select dialog

        On error, return an empty string.
        """
        initDir = os.path.dirname(self.kwargs['yw_last_open'])
        if not initDir:
            initDir = './'
        if not fileName or not os.path.isfile(fileName):
            fileName = filedialog.askopenfilename(filetypes=self._fileTypes, defaultextension='.yw7', initialdir=initDir)
        if not fileName:
            return ''

        return fileName

    def open_project(self, fileName):
        """Create a yWriter project instance and read the file.

        Positional arguments:
            fileName -- str: project file path.
            
        Display project title and file path.
        Return True on success, otherwise return False.
        To be extended by subclasses.
        """
        self.show_status(self._statusText)
        fileName = self.select_project(fileName)
        if not fileName:
            return False

        if self.ywPrj is not None:
            self.close_project()
        self.kwargs['yw_last_open'] = fileName
        self.ywPrj = self._YW_CLASS(fileName)
        message = self.ywPrj.read()
        if message.startswith(ERROR):
            self.close_project()
            self.set_info_how(message)
            return False

        self.show_path(f'{os.path.normpath(self.ywPrj.filePath)}')
        self.set_title()
        self.enable_menu()
        return True

    def set_title(self):
        """Set the main window title. 
        
        'Document title by author - application'
        """
        if self.ywPrj.title:
            titleView = self.ywPrj.title
        else:
            titleView = _('Untitled project')
        if self.ywPrj.authorName:
            authorView = self.ywPrj.authorName
        else:
            authorView = _('Unknown author')
        self.root.title(f'{titleView} {_("by")} {authorView} - {self.title}')

    def _open_project(self, event=None):
        """Create a yWriter project instance and read the file.
        
        This non-public method is meant for event handling.
        """
        self.open_project('')

    def close_project(self, event=None):
        """Close the yWriter project without saving and reset the user interface.
        
        To be extended by subclasses.
        """
        self.ywPrj = None
        self.root.title(self.title)
        self.show_status('')
        self.show_path('')
        self.disable_menu()

    def ask_yes_no(self, text):
        """Query yes or no with a pop-up box.
        
        Positional arguments:
            text -- question to be asked in the pop-up box. 
            
        Overrides the superclass method.       
        """
        return messagebox.askyesno(self.title, text)

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Display the message at the status bar.
        Overrides the superclass method.
        """
        if message.startswith(ERROR):
            self.statusBar.config(bg='red')
            self.statusBar.config(fg='white')
            self.infoHowText = message.split(ERROR, maxsplit=1)[1].strip()
        else:
            self.statusBar.config(bg='green')
            self.statusBar.config(fg='white')
            self.infoHowText = message
        self.statusBar.config(text=self.infoHowText)

    def show_status(self, message):
        """Put text on the status bar."""
        self._statusText = message
        self.statusBar.config(bg=self.root.cget('background'))
        self.statusBar.config(fg='black')
        self.statusBar.config(text=message)

    def show_path(self, message):
        """Put text on the path bar."""
        self._pathText = message
        self.pathBar.config(text=message)

    def restore_status(self, event=None):
        """Overwrite error message with the status before."""
        self.show_status(self._statusText)

    def on_quit(self, event=None):
        """Save keyword arguments before exiting the program."""
        self.kwargs['root_geometry'] = self.root.winfo_geometry()
        self.root.quit()

    def show_warning(self, message):
        """Display a warning message box."""
        messagebox.showwarning(self.title, message)


class MainTkCnv(MainTk):
    """A tkinter GUI base class for yWriter file conversion.

    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        open_project(fileName) -- select a valid project file and display the path.
        reverse_direction() -- swap source and target file names.
        convert_file() -- call the converter's conversion method, if a source file is selected.

    Public instance variables:
        converter -- converter strategy class.

    Adds a "Swap" and a "Run" entry to the main menu.
    """
    _EXPORT_DESC = 'Export from yWriter.'
    _IMPORT_DESC = 'Import to yWriter.'

    def __init__(self, title, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
                    
        Required keyword arguments:
            yw_last_open -- initial file.
            file_types -- list of tuples for file selection (display text, extension).
        
        Extends the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self._fileTypes = kwargs['file_types']
        self.converter = None
        self._sourcePath = None
        self._ywExtension = Yw7File.EXTENSION
        self._docExtension = None

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
            self.root.title(f'{self._EXPORT_DESC} - {self._title}')
        elif fileName.endswith(self._docExtension):
            self.root.title(f'{self._IMPORT_DESC} - {self._title}')
        self.show_path(f'{os.path.normpath(fileName)}')
        return True

    def reverse_direction(self):
        """Swap source and target file names."""
        fileName, fileExtension = os.path.splitext(self._sourcePath)
        if fileExtension == self._ywExtension:
            self._sourcePath = f'{fileName}{self._docExtension}'
            self.show_path(os.path.normpath(self._sourcePath))
            self.root.title(f'{self._IMPORT_DESC} - {self._title}')
            self.show_status('')
        elif fileExtension == self._docExtension:
            self._sourcePath = f'{fileName}{self._ywExtension}'
            self.show_path(os.path.normpath(self._sourcePath))
            self.root.title(f'{self._EXPORT_DESC} - {self._title}')
            self.show_status('')

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected."""
        self.show_status('')
        self.kwargs['yw_last_open'] = self._sourcePath
        self.converter.run(self._sourcePath, **self.kwargs)



class Yw2mdTk(MainTkCnv):
    """A tkinter GUI class for the yWriter/Markdown converter.
    
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

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        
        Write selected options to the keyword arguments.
        Extends the super class method.
        """
        self.kwargs['markdown_mode'] = self._markdownMode.get()
        self.kwargs['scene_titles'] = self._sceneTitles.get()
        super().convert_file()


SUFFIX = ''
APPNAME = 'yw2md'
SETTINGS = dict(
    yw_last_open='',
    root_geometry='730x200',
)
OPTIONS = dict(
    markdown_mode=False,
    scene_titles=True,
)
FILE_TYPES = [
    ('yWriter 7 project', '.yw7'),
    ('Markdown file', '.md'),
]


def run(sourcePath, silentMode=True, installDir='.', markdownMode=None, noTitles=None):

    #--- Load configuration
    iniFile = f'{installDir}/{APPNAME}.ini'
    configuration = Configuration(SETTINGS, OPTIONS)
    configuration.read(iniFile)
    kwargs = dict(
        suffix=SUFFIX,
        file_types=FILE_TYPES,
    )
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)
    if markdownMode is not None:
        kwargs['markdown_mode'] = markdownMode
    if noTitles is not None:
        kwargs['scene_titles'] = not noTitles
    converter = MdConverter()
    if silentMode:
        converter.ui = Ui('')
        converter.run(sourcePath, **kwargs)
    else:
        converter.ui = Yw2mdTk('yWriter Markdown converter @release', **kwargs)
        converter.ui.converter = converter

        #--- Get initial project path.
        if not sourcePath or not os.path.isfile(sourcePath):
            sourcePath = kwargs['yw_last_open']

        #--- Instantiate the viewer object.
        converter.ui.open_project(sourcePath)
        converter.ui.start()

        #--- Save project specific configuration
        for keyword in converter.ui.kwargs:
            if keyword in configuration.options:
                configuration.options[keyword] = converter.ui.kwargs[keyword]
            elif keyword in configuration.settings:
                configuration.settings[keyword] = converter.ui.kwargs[keyword]
        configuration.write(iniFile)


if __name__ == '__main__':
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.pywriter/{APPNAME}/config'
    except:
        installDir = '.'
    os.makedirs(installDir, exist_ok=True)
    if len(sys.argv) == 1:
        run('', False, installDir, markdownMode=None, noTitles=None)
    else:
        parser = argparse.ArgumentParser(
            description='Markdown converter for yWriter projects.',
            epilog='')
        parser.add_argument('sourcePath', metavar='Sourcefile',
                            help="The path of the source file for the conversion. "
                            "If it's a yWriter project file with extension 'yw6' or 'yw7', "
                            "a new Markdown formatted text document will be created. "
                            "Otherwise, the source file will be considered a Markdown "
                            "formatted file to be converted to a new yWriter 7 project. "
                            "Existing yWriter projects are not overwritten.")
        parser.add_argument('--silent',
                            action="store_true",
                            help='suppress error messages and the request to confirm overwriting')
        parser.add_argument('--md',
                            action="store_true",
                            help='the scenes in the yWriter project are Markdown formatted')
        parser.add_argument('--notitles',
                            action="store_true",
                            help='do not associate comments at the beginning of the scene with scene titles')
        args = parser.parse_args()
        run(args.sourcePath, args.silent, installDir, args.md, args.notitles)
