#!/usr/bin/env python3
"""Export yWriter project to markdown. 

GUI variant using tkinter
Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

import sys
import webbrowser



class Ui():
    """Base class for UI facades, implementing a 'silent mode'.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """The application may use a subclass  
        for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """What's the converter going to do?"""
        self.infoWhatText = message

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message

    def start(self):
        """To be overridden by subclasses requiring
        special action to launch the user interaction.
        """


class YwCnv():
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, sourceFile, targetFile):
        """Convert sourceFile into targetFile and return a message.

        Positional arguments:
            sourceFile, targetFile -- Novel subclass instances.

        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with SUCCESS or ERROR.

        Error handling:
        - Check if sourceFile and targetFile are correctly initialized.
        - Ask for permission to overwrite targetFile.
        - Pass the error messages of the called methods of sourceFile and targetFile.
        - The success message comes from targetFile.write(), if called.       
        """

        # Initial error handling.

        if sourceFile.filePath is None:
            return 'ERROR: Source "' + os.path.normpath(sourceFile.filePath) + '" is not of the supported type.'

        if not sourceFile.file_exists():
            return 'ERROR: "' + os.path.normpath(sourceFile.filePath) + '" not found.'

        if targetFile.filePath is None:
            return 'ERROR: Target "' + os.path.normpath(targetFile.filePath) + '" is not of the supported type.'

        if targetFile.file_exists() and not self.confirm_overwrite(targetFile.filePath):
            return 'ERROR: Action canceled by user.'

        # Make the source object read the source file.

        message = sourceFile.read()

        if message.startswith('ERROR'):
            return message

        # Make the target object merge the source object's instance variables.

        message = targetFile.merge(sourceFile)

        if message.startswith('ERROR'):
            return message

        # Make the source object write the target file.

        return targetFile.write()

    def confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        This is a stub to be overridden by subclass methods.
        """
        return True



class FileFactory:
    """Base class for conversion object factory classes.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.

    This class emulates a "FileFactory" Interface.
    Instances can be used as stubs for factories instantiated at runtime.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a private instance variable.

        Positional arguments:
            fileClasses -- list of classes from which an instance can be returned.
        """
        self.fileClasses = fileClasses

    def make_file_objects(self, sourcePath, **kwargs):
        """A factory method stub.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the target file type.

        Return a tuple with three elements:
        - A message string starting with 'ERROR'
        - sourceFile: None
        - targetFile: None

        Factory method to be overridden by subclasses.
        Subclasses return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance
        """
        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None



class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a YwFile subclass instance, or None in case of error
        - targetFile: None
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        for fileClass in self.fileClasses:

            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return 'SUCCESS', sourceFile, None

        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None



class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the target file type.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']

        for fileClass in self.fileClasses:

            if fileClass.SUFFIX == suffix:

                if suffix is None:
                    suffix = ''

                targetFile = fileClass(
                    fileName + suffix + fileClass.EXTENSION, **kwargs)
                return 'SUCCESS', None, targetFile

        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None
        """

        for fileClass in self.fileClasses:

            if fileClass.SUFFIX is not None:

                if sourcePath.endswith(fileClass.SUFFIX + fileClass.EXTENSION):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return 'SUCCESS', sourceFile, None

        return 'ERROR: This document is not meant to be written back.', None, None



class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the source file type.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: None
        - targetFile: a YwFile subclass instance, or None in case of error

        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']

        if sourceSuffix:
            ywPathBasis = fileName.split(sourceSuffix)[0]

        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.

        for fileClass in self.fileClasses:

            if os.path.isfile(ywPathBasis + fileClass.EXTENSION):
                targetFile = fileClass(
                    ywPathBasis + fileClass.EXTENSION, **kwargs)
                return 'SUCCESS', None, targetFile

        return 'ERROR: No yWriter project to write.', None, None


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        run(sourcePath, suffix) -- Create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- List of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- List of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- List of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- List of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
        newFile -- string; path to the target file in case of success.   
    """

    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.

        self.exportSourceFactory = ExportSourceFactory(
            self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(
            self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(
            self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(
            self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

        self.newFile = None
        # Also indicates successful conversion.

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        sourcePath -- str; the source file path.
        suffix -- str; target file name suffix. 

        This is a template method that calls primitive operations by case.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(
                'ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        message, sourceFile, dummy = self.exportSourceFactory.make_file_objects(
            sourcePath, **kwargs)

        if message.startswith('SUCCESS'):
            # The source file is a yWriter project.

            message, dummy, targetFile = self.exportTargetFactory.make_file_objects(
                sourcePath, **kwargs)

            if message.startswith('SUCCESS'):
                self.export_from_yw(sourceFile, targetFile)

            else:
                self.ui.set_info_how(message)

        else:
            # The source file is not a yWriter project.

            message, sourceFile, dummy = self.importSourceFactory.make_file_objects(
                sourcePath, **kwargs)

            if message.startswith('SUCCESS'):
                kwargs['suffix'] = sourceFile.SUFFIX
                message, dummy, targetFile = self.importTargetFactory.make_file_objects(
                    sourcePath, **kwargs)

                if message.startswith('SUCCESS'):
                    self.import_to_yw(sourceFile, targetFile)

                else:
                    self.ui.set_info_how(message)

            else:
                # A new yWriter project might be required.

                message, sourceFile, targetFile = self.newProjectFactory.make_file_objects(
                    sourcePath, **kwargs)

                if message.startswith('SUCCESS'):
                    self.create_yw7(sourceFile, targetFile)

                else:
                    self.ui.set_info_how(message)

    def export_from_yw(self, sourceFile, targetFile):
        """Convert from yWriter project to other file format.

        sourceFile -- YwFile subclass instance.
        targetFile -- Any Novel subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')

        # Convert sourceFile into targetFile.

        message = self.convert(sourceFile, targetFile)

        # Pass the message to the UI.

        self.ui.set_info_how(message)

        # Save the new file pathname.

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.newFile = None

    def create_yw7(self, sourceFile, targetFile):
        """Create targetFile from sourceFile.

        sourceFile -- Any Novel subclass instance.
        targetFile -- YwFile subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf targetFile already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what(
            'Create a yWriter project file from ' + sourceFile.DESCRIPTION + '\nNew project: "' + os.path.normpath(targetFile.filePath) + '"')

        if targetFile.file_exists():
            self.ui.set_info_how(
                'ERROR: "' + os.path.normpath(targetFile.filePath) + '" already exists.')

        else:
            # Convert sourceFile into targetFile.

            message = self.convert(sourceFile, targetFile)

            # Pass the message to the UI.

            self.ui.set_info_how(message)

            # Save the new file pathname.

            if message.startswith('SUCCESS'):
                self.newFile = targetFile.filePath

            else:
                self.newFile = None

    def import_to_yw(self, sourceFile, targetFile):
        """Convert from any file format to yWriter project.

        sourceFile -- Any Novel subclass instance.
        targetFile -- YwFile subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')

        # Convert sourceFile into targetFile.

        message = self.convert(sourceFile, targetFile)

        # Pass the message to the UI.

        self.ui.set_info_how(message)

        # Delete the temporay file, if exists.

        self.delete_tempfile(sourceFile.filePath)

        # Save the new file pathname.

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.newFile = None

    def confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file, overriding the superclass method."""
        return self.ui.ask_yes_no('Overwrite existing file "' + os.path.normpath(filePath) + '"?')

    def delete_tempfile(self, filePath):
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

    def open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        webbrowser.open(self.newFile)
        sys.exit(0)




from urllib.parse import quote


class Novel():
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods: 
        read() -- Parse the file and store selected properties.
        merge(novel) -- Copy required attributes of the novel object.
        write() -- Write selected properties to the file.
        convert_to_yw(text) -- Return text, converted from source format to yw7 markup.
        convert_from_yw(text) -- Return text, converted from yw7 markup to target format.
        file_exists() -- Return True, if the file specified by filePath exists.

    Instance variables:
        title -- str; title
        desc -- str; description
        author -- str; author name
        fieldTitle1 -- str; field title 1
        fieldTitle2 -- str; field title 2
        fieldTitle3 -- str; field title 3
        fieldTitle4 -- str; field title 4
        chapters -- dict; key = chapter ID, value = Chapter instance.
        scenes -- dict; key = scene ID, value = Scene instance.
        srtChapters -- list of str; The novel's sorted chapter IDs. 
        locations -- dict; key = location ID, value = WorldElement instance.
        srtLocations -- list of str; The novel's sorted location IDs. 
        items -- dict; key = item ID, value = WorldElement instance.
        srtItems -- list of str; The novel's sorted item IDs. 
        characters -- dict; key = character ID, value = Character instance.
        srtCharacters -- list of str The novel's sorted character IDs.
        filePath -- str; path to the file represented by the class.   
    """

    DESCRIPTION = 'Novel'
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    def __init__(self, filePath, **kwargs):
        """Define instance variables.

        Positional argument:
            filePath -- string; path to the file represented by the class.
        """
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.author = None
        # str
        # xml: <PROJECT><AuthorName>

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
        # The order of the elements does not matter (the novel's
        # order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's
        # order of the scenes is defined by the order of the chapters
        # and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements
        # corresponds to the novel's order of the chapters.

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
        # The novel's item IDs. The order of its elements
        # corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements
        # corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a
        # supported type as specified by EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

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

        if filePath.lower().endswith(suffix + self.EXTENSION):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(
                suffix + self.EXTENSION, ''))

    def read(self):
        """Parse the file and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: read method is not implemented.'

    def merge(self, source):
        """Copy required attributes of the source object.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: merge method is not implemented.'

    def write(self):
        """Write selected properties to the file.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: write method is not implemented.'

    def convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        This is a stub to be overridden by subclass methods.
        """
        return text

    def convert_from_yw(self, text):
        """Return text, converted from yw7 markup to target format.
        This is a stub to be overridden by subclass methods.
        """
        return text

    def file_exists(self):
        """Return True, if the file specified by filePath exists. 
        Otherwise, return False.
        """
        if os.path.isfile(self.filePath):
            return True

        else:
            return False


class Chapter():
    """yWriter chapter representation.
    # xml: <CHAPTERS><CHAPTER>
    """

    chapterTitlePrefix = "Chapter "
    # str
    # Can be changed at runtime for non-English projects.

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.oldType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo

        self.isUnused = None
        # bool
        # xml: <Unused> -1

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

    def get_title(self):
        """Fix auto-chapter titles if necessary 
        """
        text = self.title

        if text:
            text = text.replace('Chapter ', self.chapterTitlePrefix)

        return text
import re


class Scene():
    """yWriter scene representation.
    # xml: <SCENES><SCENE>
    """

    # Emulate an enumeration for the scene status

    STATUS = [None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']
    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int # xml: <Status>

        self.sceneNotes = None
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

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('\[.+?\]|\.|\,| -', '', self._sceneContent)
        # Remove yWriter raw markup for word count

        wordList = text.split()
        self.wordCount = len(wordList)

        text = re.sub('\[.+?\]', '', self._sceneContent)
        # Remove yWriter raw markup for letter count

        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)



class WorldElement():
    """Story world element representation.
    # xml: <LOCATIONS><LOCATION> or # xml: <ITEMS><ITEM>
    """

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>


class Character(WorldElement):
    """yWriter character representation.
    # xml: <CHARACTERS><CHARACTER>
    """

    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        WorldElement.__init__(self)

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


import xml.etree.ElementTree as ET


class Yw7TreeBuilder():
    """Build yWriter 7 project xml tree."""

    TAG = 'YWRITER7'
    VER = '7'

    def build_element_tree(self, ywProject):
        """Modify the yWriter project attributes of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        """

        def build_scene_subtree(xmlScn, prjScn):

            if prjScn.title is not None:

                try:
                    xmlScn.find('Title').text = prjScn.title

                except(AttributeError):
                    ET.SubElement(xmlScn, 'Title').text = prjScn.title

            if xmlScn.find('BelongsToChID') is None:

                for chId in ywProject.chapters:

                    if scId in ywProject.chapters[chId].srtScenes:
                        ET.SubElement(xmlScn, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:

                try:
                    xmlScn.find('Desc').text = prjScn.desc

                except(AttributeError):
                    ET.SubElement(xmlScn, 'Desc').text = prjScn.desc

            # Scene content is overwritten in subclasses.

            if xmlScn.find('SceneContent') is None:
                ET.SubElement(
                    xmlScn, 'SceneContent').text = prjScn.sceneContent

            if xmlScn.find('WordCount') is None:
                ET.SubElement(xmlScn, 'WordCount').text = str(
                    prjScn.wordCount)

            if xmlScn.find('LetterCount') is None:
                ET.SubElement(xmlScn, 'LetterCount').text = str(
                    prjScn.letterCount)

            if prjScn.isUnused:

                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'

            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            if prjScn.isNotesScene:

                try:
                    scFields = xmlScn.find('Fields')

                except(AttributeError):
                    scFields = ET.SubElement(xmlScn, 'Fields')

                if scFields.find('Field_SceneType') is None:
                    ET.SubElement(scFields, 'Field_SceneType').text = '1'

            elif xmlScn.find('Fields') is not None:
                scFields = xmlScn.find('Fields')

                if scFields.find('Field_SceneType') is not None:

                    if scFields.find('Field_SceneType').text == '1':
                        scFields.remove(scFields.find('Field_SceneType'))

            if prjScn.isTodoScene:

                try:
                    scFields = xmlScn.find('Fields')

                except(AttributeError):
                    scFields = ET.SubElement(xmlScn, 'Fields')

                if scFields.find('Field_SceneType') is None:
                    ET.SubElement(scFields, 'Field_SceneType').text = '2'

            elif xmlScn.find('Fields') is not None:
                scFields = xmlScn.find('Fields')

                if scFields.find('Field_SceneType') is not None:

                    if scFields.find('Field_SceneType').text == '2':
                        scFields.remove(scFields.find('Field_SceneType'))

            if prjScn.status is not None:
                try:
                    xmlScn.find('Status').text = str(prjScn.status)

                except:
                    ET.SubElement(xmlScn, 'Status').text = str(prjScn.status)

            if prjScn.sceneNotes is not None:

                try:
                    xmlScn.find('Notes').text = prjScn.sceneNotes

                except(AttributeError):
                    ET.SubElement(xmlScn, 'Notes').text = prjScn.sceneNotes

            if prjScn.tags is not None:

                try:
                    xmlScn.find('Tags').text = ';'.join(prjScn.tags)

                except(AttributeError):
                    ET.SubElement(xmlScn, 'Tags').text = ';'.join(prjScn.tags)

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
                dateTime = prjScn.date + ' ' + prjScn.time

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
                    ET.SubElement(
                        xmlScn, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:

                try:
                    xmlScn.find('LastsMinutes').text = prjScn.lastsMinutes

                except(AttributeError):
                    ET.SubElement(
                        xmlScn, 'LastsMinutes').text = prjScn.lastsMinutes

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

            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')

                for oldCrId in characters.findall('CharID'):
                    characters.remove(oldCrId)

                for crId in prjScn.characters:
                    ET.SubElement(characters, 'CharID').text = crId

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')

                for oldLcId in locations.findall('LocID'):
                    locations.remove(oldLcId)

                for lcId in prjScn.locations:
                    ET.SubElement(locations, 'LocID').text = lcId

            if prjScn.items is not None:
                items = xmlScn.find('Items')

                for oldItId in items.findall('ItemID'):
                    items.remove(oldItId)

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

            if prjChp.oldType is not None:

                try:
                    xmlChp.find('Type').text = str(prjChp.oldType)

                except(AttributeError):
                    ET.SubElement(xmlChp, 'Type').text = str(prjChp.oldType)

            if prjChp.chType is not None:

                try:
                    xmlChp.find('ChapterType').text = str(prjChp.chType)

                except(AttributeError):
                    ET.SubElement(xmlChp, 'ChapterType').text = str(
                        prjChp.chType)

            if prjChp.isUnused:

                if xmlChp.find('Unused') is None:
                    ET.SubElement(xmlChp, 'Unused').text = '-1'

            elif xmlChp.find('Unused') is not None:
                xmlChp.remove(xmlChp.find('Unused'))

            if prjChp.srtScenes:

                if xmlChp.find('Scenes') is None:
                    sortSc = ET.SubElement(xmlChp, 'Scenes')

                    for scId in prjChp.srtScenes:
                        ET.SubElement(sortSc, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc, sortOrder):
            ET.SubElement(xmlLoc, 'ID').text = lcId

            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = ';'.join(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            ET.SubElement(xmlItm, 'ID').text = itId

            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = ';'.join(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

        def build_character_subtree(xmlCrt, prjCrt, sortOrder):
            ET.SubElement(xmlCrt, 'ID').text = crId

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
                ET.SubElement(xmlCrt, 'Tags').text = ';'.join(
                    prjCrt.tags)

            if prjCrt.bio is not None:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio

            if prjCrt.goals is not None:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals

            if prjCrt.fullName is not None:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName

            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'

        def build_project_subtree(xmlPrj, ywProject):

            try:
                xmlPrj.find('Ver').text = self.VER

            except(AttributeError):
                ET.SubElement(xmlPrj, 'Ver').text = self.VER

            if ywProject.title is not None:

                try:
                    xmlPrj.find('Title').text = ywProject.title

                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Title').text = ywProject.title

            if ywProject.desc is not None:

                try:
                    xmlPrj.find('Desc').text = ywProject.desc

                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Desc').text = ywProject.desc

            if ywProject.author is not None:

                try:
                    xmlPrj.find('AuthorName').text = ywProject.author

                except(AttributeError):
                    ET.SubElement(xmlPrj, 'AuthorName').text = ywProject.author

            if ywProject.fieldTitle1 is not None:

                try:
                    xmlPrj.find('FieldTitle1').text = ywProject.fieldTitle1

                except(AttributeError):
                    ET.SubElement(
                        xmlPrj, 'FieldTitle1').text = ywProject.fieldTitle1

            if ywProject.fieldTitle2 is not None:

                try:
                    xmlPrj.find('FieldTitle2').text = ywProject.fieldTitle2

                except(AttributeError):
                    ET.SubElement(
                        xmlPrj, 'FieldTitle2').text = ywProject.fieldTitle2

            if ywProject.fieldTitle3 is not None:

                try:
                    xmlPrj.find('FieldTitle3').text = ywProject.fieldTitle3

                except(AttributeError):
                    ET.SubElement(
                        xmlPrj, 'FieldTitle3').text = ywProject.fieldTitle3

            if ywProject.fieldTitle4 is not None:

                try:
                    xmlPrj.find('FieldTitle4').text = ywProject.fieldTitle4

                except(AttributeError):
                    ET.SubElement(
                        xmlPrj, 'FieldTitle4').text = ywProject.fieldTitle4

        xmlScenes = {}
        xmlChapters = {}

        try:
            root = ywProject.tree.getroot()
            xmlPrj = root.find('PROJECT')
            locations = root.find('LOCATIONS')
            items = root.find('ITEMS')
            characters = root.find('CHARACTERS')
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')

        except(AttributeError):
            root = ET.Element(self.TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
            scenes = ET.SubElement(root, 'SCENES')
            chapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlPrj, ywProject)

        #--- Process locations.
        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.

        for xmlLoc in locations.findall('LOCATION'):
            locations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.

        sortOrder = 0

        for lcId in ywProject.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(locations, 'LOCATION')
            build_location_subtree(
                xmlLoc, ywProject.locations[lcId], sortOrder)

        #--- Process items.
        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.

        for xmlItm in items.findall('ITEM'):
            items.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.

        sortOrder = 0

        for itId in ywProject.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(items, 'ITEM')
            build_item_subtree(xmlItm, ywProject.items[itId], sortOrder)

        #--- Process characters.
        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.

        for xmlCrt in characters.findall('CHARACTER'):
            characters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.

        sortOrder = 0

        for crId in ywProject.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(characters, 'CHARACTER')
            build_character_subtree(
                xmlCrt, ywProject.characters[crId], sortOrder)

        #--- Process scenes.
        # Save the original XML scene subtrees
        # and remove them from the project tree.

        for xmlScn in scenes.findall('SCENE'):
            scId = xmlScn.find('ID').text
            xmlScenes[scId] = xmlScn
            scenes.remove(xmlScn)

        # Add the new XML scene subtrees to the project tree.

        for scId in ywProject.scenes:

            if not scId in xmlScenes:
                xmlScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlScenes[scId], 'ID').text = scId

            build_scene_subtree(xmlScenes[scId], ywProject.scenes[scId])
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

        for chId in ywProject.srtChapters:
            sortOrder += 1

            if not chId in xmlChapters:
                xmlChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlChapters[chId], 'ID').text = chId

            build_chapter_subtree(
                xmlChapters[chId], ywProject.chapters[chId], sortOrder)

            chapters.append(xmlChapters[chId])

        self.indent_xml(root)
        ywProject.tree = ET.ElementTree(root)

        # Write version-dependent scene contents to the xml element tree.

        return self.put_scene_contents(ywProject)

    def put_scene_contents(self, ywProject):
        """Modify the scene contents of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        Strategy method for the yw7 file format variant.
        """

        root = ywProject.tree.getroot()

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if ywProject.scenes[scId].sceneContent is not None:
                scn.find(
                    'SceneContent').text = ywProject.scenes[scId].sceneContent
                scn.find('WordCount').text = str(
                    ywProject.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(
                    ywProject.scenes[scId].letterCount)

            try:
                scn.remove(scn.find('RTFFile'))

            except:
                pass

        return 'SUCCESS'

    def indent_xml(self, elem, level=0):
        """xml pretty printer

        Kudos to to Fredrik Lundh. 
        Source: http://effbot.org/zone/element-lib.htm#prettyprint
        """
        i = "\n" + level * "  "

        if len(elem):

            if not elem.text or not elem.text.strip():
                elem.text = i + "  "

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

            for elem in elem:
                self.indent_xml(elem, level + 1)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i



class Utf8TreeReader():
    """Read utf-8 encoded yWriter xml project file."""

    def read_element_tree(self, ywProject):
        """Parse the yWriter xml file located at filePath, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            ywProject.tree = ET.parse(ywProject.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(ywProject.filePath) + '".'

        return 'SUCCESS: XML element tree read in.'



class Utf8TreeWriter():
    """Write utf-8 encoded yWriter project file."""

    def write_element_tree(self, ywProject):
        """Write back the xml element tree to a yWriter xml file located at filePath.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            ywProject.tree.write(
                ywProject.filePath, xml_declaration=False, encoding='utf-8')

        except(PermissionError):
            return 'ERROR: "' + os.path.normpath(ywProject.filePath) + '" is write protected.'

        return 'SUCCESS'

from html import unescape


class Utf8Postprocessor():
    """Postprocess ANSI encoded yWriter project."""

    def __init__(self):
        """Initialize instance variables."""
        self.cdataTags = ['Title', 'AuthorName', 'Bio', 'Desc',
                           'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                           'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                           'AKA', 'ImageFile', 'FullName', 'Goals',
                           'Notes', 'RTFFile', 'SceneContent',
                           'Outcome', 'Goal', 'Conflict']
        # Names of yWriter xml elements containing CDATA.
        # ElementTree.write omits CDATA tags, so they have to be inserted
        # afterwards.

    def format_xml(self, text):
        '''Postprocess the xml file created by ElementTree:
           Insert the missing CDATA tags,
           and replace xml entities by plain text.
        '''
        lines = text.split('\n')
        newlines = []

        for line in lines:

            for tag in self.cdataTags:
                line = re.sub('\<' + tag + '\>', '<' +
                              tag + '><![CDATA[', line)
                line = re.sub('\<\/' + tag + '\>',
                              ']]></' + tag + '>', line)

            newlines.append(line)

        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)

        return text

    def postprocess_xml_file(self, filePath):
        '''Postprocess the xml file created by ElementTree:
        Put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text.
        Return a message beginning with SUCCESS or ERROR.
        '''

        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()

        text = self.format_xml(text)
        text = '<?xml version="1.0" encoding="utf-8"?>\n' + text

        try:

            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Can not write "' + os.path.normpath(filePath) + '".'

        return 'SUCCESS: "' + os.path.normpath(filePath) + '" written.'


class Yw7File(Novel):
    """yWriter 7 project file representation.

    Additional attributes:
        ywTreeReader -- strategy class to read yWriter project files.
        ywTreeBuilder -- strategy class to build an xml tree.
        ywTreeWriter -- strategy class to write yWriter project files.
        ywPostprocessor -- strategy class to postprocess yWriter project files.
        tree -- xml element tree of the yWriter project
    """

    DESCRIPTION = 'yWriter 7 project'
    EXTENSION = '.yw7'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables:
        Extend the superclass constructor by adding.
        """
        Novel.__init__(self, filePath)

        self.ywTreeReader = Utf8TreeReader()
        self.ywTreeBuilder = Yw7TreeBuilder()
        self.ywTreeWriter = Utf8TreeWriter()
        self.ywPostprocessor = Utf8Postprocessor()
        self.tree = None

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []

        for line in lines:
            stripped.append(line.lstrip().rstrip())

        return stripped

    def read(self):
        """Parse the yWriter xml file, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        if self.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        message = self.ywTreeReader.read_element_tree(self)

        if message.startswith('ERROR'):
            return message

        root = self.tree.getroot()

        #--- Read locations from the xml element tree.

        for loc in root.iter('LOCATION'):
            lcId = loc.find('ID').text
            self.srtLocations.append(lcId)
            self.locations[lcId] = WorldElement()

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
                    tags = loc.find('Tags').text.split(';')
                    self.locations[lcId].tags = self._strip_spaces(tags)

        #--- Read items from the xml element tree.

        for itm in root.iter('ITEM'):
            itId = itm.find('ID').text
            self.srtItems.append(itId)
            self.items[itId] = WorldElement()

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
                    tags = itm.find('Tags').text.split(';')
                    self.items[itId].tags = self._strip_spaces(tags)

        #--- Read characters from the xml element tree.

        for crt in root.iter('CHARACTER'):
            crId = crt.find('ID').text
            self.srtCharacters.append(crId)
            self.characters[crId] = Character()

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
                    tags = crt.find('Tags').text.split(';')
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

        #--- Read attributes at novel level from the xml element tree.

        prj = root.find('PROJECT')

        if prj.find('Title') is not None:
            self.title = prj.find('Title').text

        if prj.find('AuthorName') is not None:
            self.author = prj.find('AuthorName').text

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

        #--- Read attributes at chapter level from the xml element tree.

        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text
            self.chapters[chId] = Chapter()
            self.srtChapters.append(chId)

            if chp.find('Title') is not None:
                self.chapters[chId].title = chp.find('Title').text

            if chp.find('Desc') is not None:
                self.chapters[chId].desc = chp.find('Desc').text

            if chp.find('SectionStart') is not None:
                self.chapters[chId].chLevel = 1

            else:
                self.chapters[chId].chLevel = 0

            if chp.find('Type') is not None:
                self.chapters[chId].oldType = int(chp.find('Type').text)

            if chp.find('ChapterType') is not None:
                self.chapters[chId].chType = int(chp.find('ChapterType').text)

            if chp.find('Unused') is not None:
                self.chapters[chId].isUnused = True

            else:
                self.chapters[chId].isUnused = False

            self.chapters[chId].suppressChapterTitle = False

            if self.chapters[chId].title is not None:

                if self.chapters[chId].title.startswith('@'):
                    self.chapters[chId].suppressChapterTitle = True

            for chFields in chp.findall('Fields'):

                if chFields.find('Field_SuppressChapterTitle') is not None:

                    if chFields.find('Field_SuppressChapterTitle').text == '1':
                        self.chapters[chId].suppressChapterTitle = True

                if chFields.find('Field_IsTrash') is not None:

                    if chFields.find('Field_IsTrash').text == '1':
                        self.chapters[chId].isTrash = True

                    else:
                        self.chapters[chId].isTrash = False

                if chFields.find('Field_SuppressChapterBreak') is not None:

                    if chFields.find('Field_SuppressChapterBreak').text == '1':
                        self.chapters[chId].suppressChapterBreak = True

                    else:
                        self.chapters[chId].suppressChapterBreak = False

                else:
                    self.chapters[chId].suppressChapterBreak = False

            self.chapters[chId].srtScenes = []

            if chp.find('Scenes') is not None:

                if not self.chapters[chId].isTrash:

                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        self.chapters[chId].srtScenes.append(scId)

        #--- Read attributes at scene level from the xml element tree.

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            self.scenes[scId] = Scene()

            if scn.find('Title') is not None:
                self.scenes[scId].title = scn.find('Title').text

            if scn.find('Desc') is not None:
                self.scenes[scId].desc = scn.find('Desc').text

            if scn.find('RTFFile') is not None:
                self.scenes[scId].rtfFile = scn.find('RTFFile').text

            # This is relevant for yW5 files with no SceneContent:

            if scn.find('WordCount') is not None:
                self.scenes[scId].wordCount = int(
                    scn.find('WordCount').text)

            if scn.find('LetterCount') is not None:
                self.scenes[scId].letterCount = int(
                    scn.find('LetterCount').text)

            if scn.find('SceneContent') is not None:
                sceneContent = scn.find('SceneContent').text

                if sceneContent is not None:
                    self.scenes[scId].sceneContent = sceneContent

            if scn.find('Unused') is not None:
                self.scenes[scId].isUnused = True

            else:
                self.scenes[scId].isUnused = False

            for scFields in scn.findall('Fields'):

                if scFields.find('Field_SceneType') is not None:

                    if scFields.find('Field_SceneType').text == '1':
                        self.scenes[scId].isNotesScene = True

                    if scFields.find('Field_SceneType').text == '2':
                        self.scenes[scId].isTodoScene = True

            if scn.find('ExportCondSpecific') is None:
                self.scenes[scId].doNotExport = False

            elif scn.find('ExportWhenRTF') is not None:
                self.scenes[scId].doNotExport = False

            else:
                self.scenes[scId].doNotExport = True

            if scn.find('Status') is not None:
                self.scenes[scId].status = int(scn.find('Status').text)

            if scn.find('Notes') is not None:
                self.scenes[scId].sceneNotes = scn.find('Notes').text

            if scn.find('Tags') is not None:

                if scn.find('Tags').text is not None:
                    tags = scn.find('Tags').text.split(';')
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

            if scn.find('Characters') is not None:
                for crId in scn.find('Characters').iter('CharID'):

                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []

                    self.scenes[scId].characters.append(crId.text)

            if scn.find('Locations') is not None:
                for lcId in scn.find('Locations').iter('LocID'):

                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []

                    self.scenes[scId].locations.append(lcId.text)

            if scn.find('Items') is not None:
                for itId in scn.find('Items').iter('ItemID'):

                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []

                    self.scenes[scId].items.append(itId.text)

        # Make sure that ToDo, Notes, and Unused type is inherited from the
        # chapter.

        for chId in self.chapters:

            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type.

                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isTodoScene = True
                    self.scenes[scId].isUnused = True

            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type.

                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isNotesScene = True
                    self.scenes[scId].isUnused = True

            elif self.chapters[chId].isUnused:

                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isUnused = True

        return 'SUCCESS: ' + str(len(self.scenes)) + ' Scenes read from "' + os.path.normpath(self.filePath) + '".'

    def merge(self, source):
        """Copy required attributes of the source object.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        if self.file_exists():
            message = self.read()
            # initialize data

            if message.startswith('ERROR'):
                return message

        #--- Merge and re-order locations.

        if source.srtLocations != []:
            self.srtLocations = source.srtLocations
            temploc = self.locations
            self.locations = {}

            for lcId in source.srtLocations:

                # Build a new self.locations dictionary sorted like the
                # source

                self.locations[lcId] = WorldElement()

                if not lcId in temploc:
                    # A new location has been added
                    temploc[lcId] = WorldElement()

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

        #--- Merge and re-order items.

        if source.srtItems != []:
            self.srtItems = source.srtItems
            tempitm = self.items
            self.items = {}

            for itId in source.srtItems:

                # Build a new self.items dictionary sorted like the
                # source

                self.items[itId] = WorldElement()

                if not itId in tempitm:
                    # A new item has been added
                    tempitm[itId] = WorldElement()

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

        #--- Merge and re-order characters.

        if source.srtCharacters != []:
            self.srtCharacters = source.srtCharacters
            tempchr = self.characters
            self.characters = {}

            for crId in source.srtCharacters:

                # Build a new self.characters dictionary sorted like the
                # source

                self.characters[crId] = Character()

                if not crId in tempchr:
                    # A new character has been added
                    tempchr[crId] = Character()

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

        #--- Merge scenes.

        mismatchCount = 0

        for scId in source.scenes:

            if not scId in self.scenes:
                self.scenes[scId] = Scene()
                mismatchCount += 1

            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = source.scenes[scId].title

            if source.scenes[scId].desc is not None:
                self.scenes[scId].desc = source.scenes[scId].desc

            if source.scenes[scId].sceneContent is not None:
                self.scenes[scId].sceneContent = source.scenes[scId].sceneContent

            if source.scenes[scId].isUnused is not None:
                self.scenes[scId].isUnused = source.scenes[scId].isUnused

            if source.scenes[scId].isNotesScene is not None:
                self.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene

            if source.scenes[scId].isTodoScene is not None:
                self.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene

            if source.scenes[scId].status is not None:
                self.scenes[scId].status = source.scenes[scId].status

            if source.scenes[scId].sceneNotes is not None:
                self.scenes[scId].sceneNotes = source.scenes[scId].sceneNotes

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

            if source.scenes[scId].date is not None:
                self.scenes[scId].date = source.scenes[scId].date

            if source.scenes[scId].time is not None:
                self.scenes[scId].time = source.scenes[scId].time

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
                        self.scenes[scId].append(itId)

        #--- Merge chapters.

        scenesAssigned = []

        for chId in source.chapters:

            if not chId in self.chapters:
                self.chapters[chId] = Chapter()
                mismatchCount += 1

            if source.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                self.chapters[chId].title = source.chapters[chId].title

            if source.chapters[chId].desc is not None:
                self.chapters[chId].desc = source.chapters[chId].desc

            if source.chapters[chId].chLevel is not None:
                self.chapters[chId].chLevel = source.chapters[chId].chLevel

            if source.chapters[chId].oldType is not None:
                self.chapters[chId].oldType = source.chapters[chId].oldType

            if source.chapters[chId].chType is not None:
                self.chapters[chId].chType = source.chapters[chId].chType

            if source.chapters[chId].isUnused is not None:
                self.chapters[chId].isUnused = source.chapters[chId].isUnused

            if source.chapters[chId].suppressChapterTitle is not None:
                self.chapters[chId].suppressChapterTitle = source.chapters[chId].suppressChapterTitle

            if source.chapters[chId].suppressChapterBreak is not None:
                self.chapters[chId].suppressChapterBreak = source.chapters[chId].suppressChapterBreak

            if source.chapters[chId].isTrash is not None:
                self.chapters[chId].isTrash = source.chapters[chId].isTrash

            if source.chapters[chId].srtScenes is not None:
                self.chapters[chId].srtScenes = []

                for scId in source.chapters[chId].srtScenes:

                    if (scId in self.scenes) and not (scId in scenesAssigned):
                        self.chapters[chId].srtScenes.append(scId)
                        scenesAssigned.append(scId)

        #--- Merge project attributes.

        if source.title:
            # avoids deleting the title, if it is empty by accident
            self.title = source.title

        if source.desc is not None:
            self.desc = source.desc

        if source.author is not None:
            self.author = source.author

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4

        # if source.srtChapters != []:
        if self.srtChapters == []:
            self.srtChapters = []

            for chId in source.srtChapters:
                self.srtChapters.append(chId)

        if self.tree is not None:

            # The project structure must match the target.

            if mismatchCount != 0:
                return 'ERROR: Project structure mismatch.'

        return 'SUCCESS'

    def write(self):
        """Open the yWriter xml file located at filePath and 
        replace a set of attributes not being None.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        if self.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        message = self.ywTreeBuilder.build_element_tree(self)

        if message.startswith('ERROR'):
            return message

        message = self.ywTreeWriter.write_element_tree(self)

        if message.startswith('ERROR'):
            return message

        return self.ywPostprocessor.postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        if os.path.isfile(self.filePath + '.lock'):
            return True

        else:
            return False


from html.parser import HTMLParser




def read_html_file(filePath):
    """Open a html file being encoded utf-8 or ANSI.
    Return a tuple:
    [0] = Message beginning with SUCCESS or ERROR.
    [1] = The file content in a single string. 
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            text = (f.read())
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        try:
            with open(filePath, 'r') as f:
                text = (f.read())

        except(FileNotFoundError):
            return ('ERROR: "' + os.path.normpath(filePath) + '" not found.', None)

    return ('SUCCESS', text)




class HtmlFile(Novel, HTMLParser):
    """Generic HTML file representation."""

    EXTENSION = '.html'
    COMMENT_START = '/*'
    COMMENT_END = '*/'
    SC_TITLE_BRACKET = '~'

    def __init__(self, filePath, **kwargs):
        Novel.__init__(self, filePath)
        HTMLParser.__init__(self)
        self._lines = []
        self._scId = None
        self._chId = None

    def convert_to_yw(self, text):
        """Convert html tags to yWriter 6/7 raw markup. 
        Return a yw6/7 markup string.
        """

        # Clean up polluted HTML code.

        text = re.sub('</*font.*?>', '', text)
        text = re.sub('</*span.*?>', '', text)
        text = re.sub('</*FONT.*?>', '', text)
        text = re.sub('</*SPAN.*?>', '', text)

        # Put everything in one line.

        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')

        while '  ' in text:
            text = text.replace('  ', ' ').rstrip().lstrip()

        # Replace HTML tags by yWriter markup.

        text = text.replace('<i>', '[i]')
        text = text.replace('<I>', '[i]')
        text = text.replace('</i>', '[/i]')
        text = text.replace('</I>', '[/i]')
        text = text.replace('</em>', '[/i]')
        text = text.replace('</EM>', '[/i]')
        text = text.replace('<b>', '[b]')
        text = text.replace('<B>', '[b]')
        text = text.replace('</b>', '[/b]')
        text = text.replace('</B>', '[/b]')
        text = text.replace('</strong>', '[/b]')
        text = text.replace('</STRONG>', '[/b]')
        text = re.sub('<em.*?>', '[i]', text)
        text = re.sub('<EM.*?>', '[i]', text)
        text = re.sub('<strong.*?>', '[b]', text)
        text = re.sub('<STRONG.*?>', '[b]', text)

        # Remove orphaned tags.

        text = text.replace('[/b][b]', '')
        text = text.replace('[/i][i]', '')
        text = text.replace('[/b][b]', '')

        # Convert author's comments

        text = text.replace('<!--', '/*')
        text = text.replace('-->', '*/')

        return text

    def preprocess(self, text):
        """Clean up the HTML code and strip yWriter 6/7 raw markup. 
        This prevents accidentally applied formatting from being 
        transferred to the yWriter metadata. If rich text is 
        applicable, such as in scenes, overwrite this method 
        in a subclass) 
        """
        text = self.convert_to_yw(text)

        # Remove misplaced formatting tags.

        text = re.sub('\[\/*[b|i]\]', '', text)
        return text

    def postprocess(self):
        """Process the plain text after parsing.
        This is a hook for subclasses.
        """

    def handle_starttag(self, tag, attrs):
        """Identify scenes and chapters.
        Override HTMLparser.handle_starttag().
        This method is applicable to HTML files that are divided into 
        chapters and scenes. For differently structured HTML files 
        do override this method in a subclass.
        """
        if tag == 'div':

            if attrs[0][0] == 'id':

                if attrs[0][1].startswith('ScID'):
                    self._scId = re.search('[0-9]+', attrs[0][1]).group()
                    self.scenes[self._scId] = Scene()
                    self.chapters[self._chId].srtScenes.append(self._scId)

                elif attrs[0][1].startswith('ChID'):
                    self._chId = re.search('[0-9]+', attrs[0][1]).group()
                    self.chapters[self._chId] = Chapter()
                    self.chapters[self._chId].srtScenes = []
                    self.srtChapters.append(self._chId)

    def read(self):
        """Read and parse a html file, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        This is a template method for subclasses tailored to the 
        content of the respective HTML file.
        """
        result = read_html_file(self.filePath)

        if result[0].startswith('ERROR'):
            return (result[0])

        text = self.preprocess(result[1])
        self.feed(text)
        self.postprocess()

        return 'SUCCESS'


class HtmlImport(HtmlFile):
    """HTML 'work in progress' file representation.

    Import untagged chapters and scenes.
    """

    DESCRIPTION = 'Work in progress'
    SUFFIX = ''

    _SCENE_DIVIDER = '* * *'
    _LOW_WORDCOUNT = 10

    def __init__(self, filePath, **kwargs):
        HtmlFile.__init__(self, filePath)
        self._chCount = 0
        self._scCount = 0

    def preprocess(self, text):
        """Process the html text before parsing.
        """
        return self.convert_to_yw(text)

    def handle_starttag(self, tag, attrs):

        if tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.chapters[self._chId] = Chapter()
            self.chapters[self._chId].srtScenes = []
            self.srtChapters.append(self._chId)
            self.chapters[self._chId].oldType = '0'

            if tag == 'h1':
                self.chapters[self._chId].chLevel = 1

            else:
                self.chapters[self._chId].chLevel = 0

        elif tag == 'p':

            if self._scId is None and self._chId is not None:
                self._lines = []
                self._scCount += 1
                self._scId = str(self._scCount)
                self.scenes[self._scId] = Scene()
                self.chapters[self._chId].srtScenes.append(self._scId)
                self.scenes[self._scId].status = '1'
                self.scenes[self._scId].title = 'Scene ' + str(self._scCount)

        elif tag == 'div':
            self._scId = None
            self._chId = None

        elif tag == 'meta':

            if attrs[0][1].lower() == 'author':
                self.author = attrs[1][1]

            if attrs[0][1].lower() == 'description':
                self.desc = attrs[1][1]

        elif tag == 'title':
            self._lines = []

    def handle_endtag(self, tag):

        if tag == 'p':
            self._lines.append('\n')

            if self._scId is not None:
                self.scenes[self._scId].sceneContent = ''.join(self._lines)

                if self.scenes[self._scId].wordCount < self._LOW_WORDCOUNT:
                    self.scenes[self._scId].status = Scene.STATUS.index(
                        'Outline')

                else:
                    self.scenes[self._scId].status = Scene.STATUS.index(
                        'Draft')

        elif tag in ('h1', 'h2'):
            self.chapters[self._chId].title = ''.join(self._lines)
            self._lines = []

        elif tag == 'title':
            self.title = ''.join(self._lines)

    def handle_data(self, data):
        """Collect data within scene sections.
        Overwrites HTMLparser.handle_data().
        """
        if self._scId is not None and self._SCENE_DIVIDER in data:
            self._scId = None

        else:
            data = data.lstrip().rstrip()

            # Convert prefixed comment into scene title.

            if self._lines == [] and data.startswith(self.COMMENT_START):

                try:
                    scTitle, scContent = data.split(
                        sep=self.COMMENT_END, maxsplit=1)

                    if self.SC_TITLE_BRACKET in scTitle:
                        scTitle = scTitle.split(self.SC_TITLE_BRACKET)[1]

                    else:
                        scTitle = scTitle.lstrip(self.COMMENT_START)

                    self.scenes[self._scId].title = scTitle.lstrip().rstrip()
                    data = scContent

                except:
                    pass

            self._lines.append(data)



class HtmlOutline(HtmlFile):
    """HTML outline file representation.

    Import an outline without chapter and scene tags.
    """

    DESCRIPTION = 'Novel outline'
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        HtmlFile.__init__(self, filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_starttag(self, tag, attrs):

        if tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.chapters[self._chId] = Chapter()
            self.chapters[self._chId].srtScenes = []
            self.srtChapters.append(self._chId)
            self.chapters[self._chId].oldType = '0'

            if tag == 'h1':
                self.chapters[self._chId].chLevel = 1

            else:
                self.chapters[self._chId].chLevel = 0

        elif tag == 'h3':
            self._lines = []
            self._scCount += 1
            self._scId = str(self._scCount)
            self.scenes[self._scId] = Scene()
            self.chapters[self._chId].srtScenes.append(self._scId)
            self.scenes[self._scId].sceneContent = ''
            self.scenes[self._scId].status = Scene.STATUS.index('Outline')

        elif tag == 'div':
            self._scId = None
            self._chId = None

        elif tag == 'meta':

            if attrs[0][1].lower() == 'author':
                self.author = attrs[1][1]

            if attrs[0][1].lower() == 'description':
                self.desc = attrs[1][1]

        elif tag == 'title':
            self._lines = []

    def handle_endtag(self, tag):

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
        Overwrites HTMLparser.handle_data().
        """
        self._lines.append(data.rstrip().lstrip())



class NewProjectFactory(FileFactory):
    """A factory class that instantiates a document object to read, 
    and a new yWriter project.

    Class constant:
        DO_NOT_IMPORT -- list of suffixes from file classes not meant to be imported.    
    """

    DO_NOT_IMPORT = ['_xref']

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source and a target object for creation of a new yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance
        """
        if not self.canImport(sourcePath):
            return 'ERROR: This document is not meant to be written back.', None, None

        fileName, fileExtension = os.path.splitext(sourcePath)
        targetFile = Yw7File(fileName + Yw7File.EXTENSION, **kwargs)

        if sourcePath.endswith('.html'):

            # The source file might be an outline or a "work in progress".

            result = read_html_file(sourcePath)

            if result[0].startswith('SUCCESS'):

                if "<h3" in result[1].lower():
                    sourceFile = HtmlOutline(sourcePath, **kwargs)

                else:
                    sourceFile = HtmlImport(sourcePath, **kwargs)

                return 'SUCCESS', sourceFile, targetFile

            else:
                return 'ERROR: Cannot read "' + os.path.normpath(sourcePath) + '".', None, None

        else:
            for fileClass in self.fileClasses:

                if fileClass.SUFFIX is not None:

                    if sourcePath.endswith(fileClass.SUFFIX + fileClass.EXTENSION):
                        sourceFile = fileClass(sourcePath, **kwargs)
                        return 'SUCCESS', sourceFile, targetFile

            return 'ERROR: File type of  "' + os.path.normpath(sourcePath) + '" not supported.', None, None

    def canImport(self, sourcePath):
        """Return True, if the file located at sourcepath is of an importable type.
        Otherwise, return False.
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        for suffix in self.DO_NOT_IMPORT:

            if fileName.endswith(suffix):
                return False

        return True





class Yw6TreeBuilder(Yw7TreeBuilder):
    """Build yWriter 6 project xml tree."""

    TAG = 'YWRITER6'
    VER = '5'

    def put_scene_contents(self, ywProject):
        """Modify the scene contents of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        root = ywProject.tree.getroot()

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if ywProject.scenes[scId].sceneContent is not None:
                scn.find(
                    'SceneContent').text = ywProject.scenes[scId].sceneContent
                scn.find('WordCount').text = str(
                    ywProject.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(
                    ywProject.scenes[scId].letterCount)

        return 'SUCCESS'


class Yw6File(Yw7File):
    """yWriter 6 project file representation."""

    DESCRIPTION = 'yWriter 6 project'
    EXTENSION = '.yw6'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        Extend the superclass constructor by changing
        the ywTreeBuilder strategy. 
        """
        Yw7File.__init__(self, filePath)

        self.ywTreeBuilder = Yw6TreeBuilder()

from string import Template



class Filter():
    """Strategy class, implementing filtering criteria 
    for template-based export.
    """

    def accept(self, source, id):
        """Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods
        implementing filters.
        """
        return True


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''

    fileHeader = ''
    partTemplate = ''
    chapterTemplate = ''
    notesChapterTemplate = ''
    todoChapterTemplate = ''
    unusedChapterTemplate = ''
    notExportedChapterTemplate = ''
    sceneTemplate = ''
    firstSceneTemplate = ''
    appendedSceneTemplate = ''
    notesSceneTemplate = ''
    todoSceneTemplate = ''
    unusedSceneTemplate = ''
    notExportedSceneTemplate = ''
    sceneDivider = ''
    chapterEndTemplate = ''
    unusedChapterEndTemplate = ''
    notExportedChapterEndTemplate = ''
    notesChapterEndTemplate = ''
    characterTemplate = ''
    locationTemplate = ''
    itemTemplate = ''
    fileFooter = ''

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        initializing a filter class.
        """
        Novel.__init__(self, filePath, **kwargs)
        self.sceneFilter = Filter()
        self.chapterFilter = Filter()
        self.characterFilter = Filter()
        self.locationFilter = Filter()
        self.itemFilter = Filter()

    def get_string(self, elements):
        """Return a string which is the concatenation of the 
        members of the list of strings "elements", separated by 
        a comma plus a space. The space allows word wrap in 
        spreadsheet cells.
        """
        text = (', ').join(elements)
        return text

    def get_list(self, text):
        """Split a sequence of strings into a list of strings
        using a comma as delimiter. Remove leading and trailing
        spaces, if any.
        """
        elements = []
        tempList = text.split(',')

        for element in tempList:
            elements.append(element.lstrip().rstrip())

        return elements

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        This is a stub to be overridden by subclass methods.
        """

        if text is None:
            text = ''

        return(text)

    def merge(self, source):
        """Copy required attributes of the source object.
        Return a message beginning with SUCCESS or ERROR.
        """

        if source.title is not None:
            self.title = source.title

        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc

        else:
            self.desc = ''

        if source.author is not None:
            self.author = source.author

        else:
            self.author = ''

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

        if source.srtChapters != []:
            self.srtChapters = source.srtChapters

        if source.scenes is not None:
            self.scenes = source.scenes

        if source.chapters is not None:
            self.chapters = source.chapters

        if source.srtCharacters != []:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters

        if source.srtLocations != []:
            self.srtLocations = source.srtLocations
            self.locations = source.locations

        if source.srtItems != []:
            self.srtItems = source.srtItems
            self.items = source.items

        return 'SUCCESS'

    def get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section. 
        """
        projectTemplateMapping = dict(
            Title=self.title,
            Desc=self.convert_from_yw(self.desc),
            AuthorName=self.author,
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
        )
        return projectTemplateMapping

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self.chapters[chId].get_title(),
            Desc=self.convert_from_yw(self.chapters[chId].desc),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section. 
        """
        # Create a comma separated tag list.

        if sceneNumber == 0:
            sceneNumber = ''

        if self.scenes[scId].tags is not None:
            tags = self.get_string(self.scenes[scId].tags)

        else:
            tags = ''

        # Create a comma separated character list.

        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters

            sChList = []

            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)

            sceneChars = self.get_string(sChList)
            viewpointChar = sChList[0]

        except:
            sceneChars = ''
            viewpointChar = ''

        # Create a comma separated location list.

        if self.scenes[scId].locations is not None:
            sLcList = []

            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)

            sceneLocs = self.get_string(sLcList)

        else:
            sceneLocs = ''

        # Create a comma separated item list.

        if self.scenes[scId].items is not None:
            sItList = []

            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)

            sceneItems = self.get_string(sItList)

        else:
            sceneItems = ''

        # Create A/R marker string.

        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER

        else:
            reactionScene = Scene.ACTION_MARKER

        # Create a combined date information.

        if self.scenes[scId].date is not None:
            day = ''
            date = self.scenes[scId].date
            scDate = self.scenes[scId].date

        else:
            date = ''

            if self.scenes[scId].day is not None:
                day = self.scenes[scId].day
                scDate = 'Day ' + self.scenes[scId].day

            else:
                day = ''
                scDate = ''

        # Create a combined time information.

        if self.scenes[scId].time is not None:
            hour = ''
            minute = ''
            time = self.scenes[scId].time
            scTime = self.scenes[scId].time.rsplit(':', 1)[0]

        else:
            time = ''

            if self.scenes[scId].hour is not None:
                hour = self.scenes[scId].hour
                minute = self.scenes[scId].minute
                scTime = self.scenes[scId].hour.zfill(2) + \
                    ':' + self.scenes[scId].minute.zfill(2)

            else:
                hour = ''
                minute = ''
                scTime = ''

        # Create a combined duration information.

        if self.scenes[scId].lastsDays is not None:
            lastsDays = self.scenes[scId].lastsDays
            days = self.scenes[scId].lastsDays + 'd '

        else:
            lastsDays = ''
            days = ''

        if self.scenes[scId].lastsHours is not None:
            lastsHours = self.scenes[scId].lastsHours
            hours = self.scenes[scId].lastsHours + 'h '

        else:
            lastsHours = ''
            hours = ''

        if self.scenes[scId].lastsMinutes is not None:
            lastsMinutes = self.scenes[scId].lastsMinutes
            minutes = self.scenes[scId].lastsMinutes + 'min'

        else:
            lastsMinutes = ''
            minutes = ''

        duration = days + hours + minutes

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self.scenes[scId].title,
            Desc=self.convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self.convert_from_yw(
                self.scenes[scId].sceneContent),
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=date,
            Time=time,
            Day=day,
            Hour=hour,
            Minute=minute,
            ScDate=scDate,
            ScTime=scTime,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self.convert_from_yw(self.scenes[scId].goal),
            Conflict=self.convert_from_yw(self.scenes[scId].conflict),
            Outcome=self.convert_from_yw(self.scenes[scId].outcome),
            Tags=tags,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self.convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )

        return sceneMapping

    def get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        """

        if self.characters[crId].tags is not None:
            tags = self.get_string(self.characters[crId].tags)

        else:
            tags = ''

        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER

        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self.characters[crId].title,
            Desc=self.convert_from_yw(self.characters[crId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.characters[crId].aka),
            Notes=self.convert_from_yw(self.characters[crId].notes),
            Bio=self.convert_from_yw(self.characters[crId].bio),
            Goals=self.convert_from_yw(self.characters[crId].goals),
            FullName=FileExport.convert_from_yw(
                self, self.characters[crId].fullName),
            Status=characterStatus,
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        """

        if self.locations[lcId].tags is not None:
            tags = self.get_string(self.locations[lcId].tags)

        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self.locations[lcId].title,
            Desc=self.convert_from_yw(self.locations[lcId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.locations[lcId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section. 
        """

        if self.items[itId].tags is not None:
            tags = self.get_string(self.items[itId].tags)

        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self.items[itId].title,
            Desc=self.convert_from_yw(self.items[itId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.items[itId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def get_fileHeader(self):
        """Process the file header.
        Return a list of strings.
        """
        lines = []
        template = Template(self.fileHeader)
        lines.append(template.safe_substitute(
            self.get_fileHeaderMapping()))
        return lines

    def get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        Return a list of strings.
        """
        lines = []
        firstSceneInChapter = True

        for scId in self.chapters[chId].srtScenes:
            dispNumber = 0

            if not self.sceneFilter.accept(self, scId):
                continue

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.

            if self.scenes[scId].isTodoScene:

                if self.todoSceneTemplate != '':
                    template = Template(self.todoSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isNotesScene:
                # Scene is "Notes" type.

                if self.notesSceneTemplate != '':
                    template = Template(self.notesSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isUnused or self.chapters[chId].isUnused:

                if self.unusedSceneTemplate != '':
                    template = Template(self.unusedSceneTemplate)

                else:
                    continue

            elif self.chapters[chId].oldType == 1:
                # Scene is "Info" type (old file format).

                if self.notesSceneTemplate != '':
                    template = Template(self.notesSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:

                if self.notExportedSceneTemplate != '':
                    template = Template(self.notExportedSceneTemplate)

                else:
                    continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount

                template = Template(self.sceneTemplate)

                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self.appendedSceneTemplate != '':
                    template = Template(self.appendedSceneTemplate)

            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self.sceneDivider)

            if firstSceneInChapter and self.firstSceneTemplate != '':
                template = Template(self.firstSceneTemplate)

            lines.append(template.safe_substitute(self.get_sceneMapping(
                scId, dispNumber, wordsTotal, lettersTotal)))

            firstSceneInChapter = False

        return lines, sceneNumber, wordsTotal, lettersTotal

    def get_chapters(self):
        """Process the chapters and nested scenes.
        Return a list of strings.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0

        for chId in self.srtChapters:
            dispNumber = 0

            if not self.chapterFilter.accept(self, chId):
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
                # Chapter is "ToDo" type (implies "unused").

                if self.todoChapterTemplate != '':
                    template = Template(self.todoChapterTemplate)

            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type (implies "unused").

                if self.notesChapterTemplate != '':
                    template = Template(self.notesChapterTemplate)

            elif self.chapters[chId].isUnused:
                # Chapter is "really" unused.

                if self.unusedChapterTemplate != '':
                    template = Template(self.unusedChapterTemplate)

            elif self.chapters[chId].oldType == 1:
                # Chapter is "Info" type (old file format).

                if self.notesChapterTemplate != '':
                    template = Template(self.notesChapterTemplate)

            elif doNotExport:

                if self.notExportedChapterTemplate != '':
                    template = Template(self.notExportedChapterTemplate)

            elif self.chapters[chId].chLevel == 1 and self.partTemplate != '':
                template = Template(self.partTemplate)

            else:
                template = Template(self.chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber

            if template is not None:
                lines.append(template.safe_substitute(
                    self.get_chapterMapping(chId, dispNumber)))

            # Process scenes.

            sceneLines, sceneNumber, wordsTotal, lettersTotal = self.get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            # Process chapter ending.

            template = None

            if self.chapters[chId].chType == 2:

                if self.todoChapterEndTemplate != '':
                    template = Template(self.todoChapterEndTemplate)

            elif self.chapters[chId].chType == 1:

                if self.notesChapterEndTemplate != '':
                    template = Template(self.notesChapterEndTemplate)

            elif self.chapters[chId].isUnused:

                if self.unusedChapterEndTemplate != '':
                    template = Template(self.unusedChapterEndTemplate)

            elif self.chapters[chId].oldType == 1:

                if self.notesChapterEndTemplate != '':
                    template = Template(self.notesChapterEndTemplate)

            elif doNotExport:

                if self.notExportedChapterEndTemplate != '':
                    template = Template(self.notExportedChapterEndTemplate)

            elif self.chapterEndTemplate != '':
                template = Template(self.chapterEndTemplate)

            if template is not None:
                lines.append(template.safe_substitute(
                    self.get_chapterMapping(chId, dispNumber)))

        return lines

    def get_characters(self):
        """Process the characters.
        Return a list of strings.
        """
        lines = []
        template = Template(self.characterTemplate)

        for crId in self.srtCharacters:

            if self.characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(
                    self.get_characterMapping(crId)))

        return lines

    def get_locations(self):
        """Process the locations.
        Return a list of strings.
        """
        lines = []
        template = Template(self.locationTemplate)

        for lcId in self.srtLocations:

            if self.locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(
                    self.get_locationMapping(lcId)))

        return lines

    def get_items(self):
        """Process the items.
        Return a list of strings.
        """
        lines = []
        template = Template(self.itemTemplate)

        for itId in self.srtItems:

            if self.itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(
                    self.get_itemMapping(itId)))

        return lines

    def get_text(self):
        """Assemple the whole text applying the templates.
        Return a string to be written to the output file.
        """
        lines = self.get_fileHeader()
        lines.extend(self.get_chapters())
        lines.extend(self.get_characters())
        lines.extend(self.get_locations())
        lines.extend(self.get_items())
        lines.append(self.fileFooter)
        return ''.join(lines)

    def write(self):
        """Create a template-based output file. 
        Return a message string starting with 'SUCCESS' or 'ERROR'.
        """
        text = self.get_text()

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Cannot write "' + os.path.normpath(self.filePath) + '".'

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'


class MdFile(FileExport):
    """Markdown file representation
    """

    DESCRIPTION = 'Markdown file'
    EXTENSION = '.md'
    SUFFIX = ''

    SCENE_DIVIDER = '* * *'

    fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''

    partTemplate = '\n# ${Title}\n\n'

    chapterTemplate = '\n## ${Title}\n\n'

    sceneTemplate = '<!---${Title}--->${SceneContent}\n\n'

    sceneDivider = '\n\n' + SCENE_DIVIDER + '\n\n'

    def __init__(self, filePath, **kwargs):
        FileExport.__init__(self, filePath)
        self.markdownMode = kwargs['markdownMode']
        self.noSceneTitles = kwargs['noSceneTitles']

        if self.noSceneTitles:
            self.sceneTemplate = self.sceneTemplate.replace(
                '<!---${Title}--->', '')

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = FileExport.get_chapterMapping(
            self, chId, chapterNumber)

        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''

        return chapterMapping

    def convert_from_yw(self, text):
        """Convert yw7 markup to Markdown.
        """

        MD_REPLACEMENTS = [
            ['[i]', '*'],
            ['[/i]', '*'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['/*', '<!---'],
            ['*/', '--->'],
            ['  ', ' '],
        ]

        if not self.markdownMode:
            MD_REPLACEMENTS[:0] = [['\n', '\n\n']]

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)

    def convert_to_yw(self, text):
        """Convert Markdown to yw7 markup.
        """
        if not self.markdownMode:
            text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
            text = re.sub('\*([^ ].+?[^ ])\*', '[i]\\1[/i]', text)

            MD_REPLACEMENTS = [
                ['\n\n', '\n'],
                ['<!---', '/*'],
                ['--->', '*/'],
            ]

            try:

                for r in MD_REPLACEMENTS:
                    text = text.replace(r[0], r[1])

            except AttributeError:
                text = ''

        return(text)

    def read(self):
        """Parse the Markdown file located at filePath
        Return a message beginning with SUCCESS or ERROR.
        """
        LOW_WORDCOUNT = 10

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
                cnvText = self.convert_to_yw(mdText)
                mdLines = (cnvText).split('\n')

        except(FileNotFoundError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" not found.'

        except:
            return 'ERROR: Can not parse "' + os.path.normpath(self.filePath) + '".'

        if self.markdownMode:
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
                self.chapters[chId].oldType = '0'

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
                self.scenes[scId].title = 'Scene ' + str(scCount)

                if not self.noSceneTitles and mdLine.startswith(commentStart):

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

        return 'SUCCESS'


class MdConverter(YwCnvUi):
    """A converter class for Markdown export."""
    EXPORT_SOURCE_CLASSES = [Yw7File, Yw6File]
    EXPORT_TARGET_CLASSES = [MdFile]
    CREATE_SOURCE_CLASSES = [MdFile]

    def __init__(self):
        YwCnvUi.__init__(self)
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
from tkinter import *
from tkinter import messagebox



class UiTk(Ui):
    """UI subclass implementing a Tkinter facade."""

    def __init__(self, title):
        """Extend the Ui constructor. """
        Ui.__init__(self, title)

        self.root = Tk()
        self.root.title(title)

        self.appInfo = Label(self.root, text='')
        self.successInfo = Label(self.root)
        self.successInfo.config(height=1, width=60)
        self.processInfo = Label(self.root, text='')
        self.root.quitButton = Button(text="Quit", command=quit)
        self.root.quitButton.config(height=1, width=10)

        self.rowCount = 1
        self.appInfo.grid(row=self.rowCount, column=1, padx=5, pady=5)
        self.rowCount += 1
        self.successInfo.grid(row=self.rowCount, column=1, padx=10, pady=10)
        self.rowCount += 1
        self.processInfo.grid(row=self.rowCount, column=1, pady=10)
        self.rowCount += 1
        self.root.quitButton.grid(row=self.rowCount, column=1, pady=10)

    def ask_yes_no(self, text):
        """Override the Ui method."""
        return messagebox.askyesno('WARNING', text)

    def set_info_what(self, message):
        """What's the converter going to do?"""

        self.infoWhatText = message
        self.appInfo.config(text=message)

    def set_info_how(self, message):
        """How's the converter doing?"""

        self.infoHowText = message
        self.processInfo.config(text=message)

        if message.startswith('SUCCESS'):
            self.successInfo.config(bg='green')

        else:
            self.successInfo.config(bg='red')

    def start(self):
        """Start the Tk main loop."""
        self.root.mainloop()

    def show_open_button(self, open_cmd):
        """Add an 'Open' button to the main window."""
        self.root.openButton = Button(text="Open", command=open_cmd)
        self.root.openButton.config(height=1, width=10)
        self.rowCount += 1
        self.root.openButton.grid(row=self.rowCount, column=1, pady=10)

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

SCT_DESCRIPTION = 'Comments at the beginning of a scene are scene titles.'
MDM_DESCRIPTION = 'The scenes in the yWriter project are Markdown formatted.'


class MyGui(UiTk):
    """Extend the Tkinter GUI, 
    and link it to the application.
    """

    def __init__(self, title, description=None):
        """Make the converter object visible to the user interface 
        in order to make method calls possible.
        Add the widgets needed to invoke the converter manually.
        """
        self.converter = None
        self.infoWhatText = ''
        self.infoHowText = ''
        # UiTk.__init__(self, title)

        self.root = Tk()
        self.root.title(title)

        self.header = Label(self.root, text='Options')
        self.appInfo = Label(self.root, text='')
        self.appInfo.config(height=2, width=60)

        self.successInfo = Label(self.root)
        self.successInfo.config(height=1, width=50)

        self.processInfo = Label(self.root, text='')

        self.SceneTitles = BooleanVar()
        self.SceneTitles.set(False)
        self.root.SceneTitlesCheckbox = ttk.Checkbutton(
            text=SCT_DESCRIPTION, variable=self.SceneTitles, onvalue=False, offvalue=True)

        self.markdownMode = BooleanVar()
        self.root.markdownModeCheckbox = ttk.Checkbutton(
            text=MDM_DESCRIPTION, variable=self.markdownMode, onvalue=True, offvalue=False)

        self.root.selectButton = Button(
            text="Select file", command=self.select_file)
        self.root.selectButton.config(height=1, width=10)

        self.root.runButton = Button(text='Convert', command=self.convert_file)
        self.root.runButton.config(height=1, width=10)
        self.root.runButton.config(state='disabled')

        self.root.quitButton = Button(text='Quit', command=quit)
        self.root.quitButton.config(height=1, width=10)

        self.header.grid(row=1, column=1, sticky=W, padx=20, columnspan=3)
        self.root.SceneTitlesCheckbox.grid(
            row=2, column=1, sticky=W, padx=20, columnspan=3)
        self.root.markdownModeCheckbox.grid(
            row=3, column=1, sticky=W, padx=20, columnspan=3)
        self.appInfo.grid(row=5, column=1, pady=10, columnspan=3)

        self.root.selectButton.grid(
            row=6, column=1, pady=10)
        self.root.runButton.grid(row=6, column=2, pady=10)
        self.root.quitButton.grid(row=6, column=3, pady=10)

        self.successInfo.grid(row=7, column=1, columnspan=3)
        self.processInfo.grid(row=8, column=1, columnspan=3, pady=10)

        self.sourcePath = None
        self.set_info_what('No file selected')
        self.startDir = os.getcwd()

    def start(self):
        """Start the user interface.
        Note: This can not be done in the __init__() method.
        """
        self.root.mainloop()

    def select_file(self):
        """Open a file dialog in order to set the sourcePath property.
        """
        self.processInfo.config(text='')
        self.successInfo.config(
            bg=self.root.cget("background"))

        if self.sourcePath is not None:
            self.startDir = os.path.dirname(self.sourcePath)

        file = filedialog.askopenfile(initialdir=self.startDir)

        if file:
            self.sourcePath = file.name

        if self.sourcePath:
            self.set_info_what(
                'File: ' + os.path.normpath(self.sourcePath))
            self.root.runButton.config(state='normal')

        else:
            self.set_info_what('No file selected')
            self.root.runButton.config(state='disabled')

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        """
        self.processInfo.config(text='')
        self.successInfo.config(
            bg=self.root.cget("background"))

        if self.sourcePath:
            kwargs = {'suffix': '', 'markdownMode': self.markdownMode.get(),
                      'noSceneTitles': self.SceneTitles.get()}
            self.converter.run(self.sourcePath, **kwargs)


def run(sourcePath):

    ui = MyGui('Markdown converter for yWriter projects @release')
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