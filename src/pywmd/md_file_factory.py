"""Instantiate the objects for Markdown file conversion. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.file_factory import FileFactory
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywriter.yw.yw7_tree_creator import Yw7TreeCreator
from pywriter.yw.yw_project_creator import YwProjectCreator

from pywmd.md_file import MdFile


class MdFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def __init__(self, markdownMode=False, noSceneTitles=False):
        self.markdownMode = markdownMode
        self.noSceneTitles = noSceneTitles

    def get_file_objects(self, sourcePath, suffix):
        """Return a tuple with three elements:
        * A message string starting with 'SUCCESS' or 'ERROR'
        * sourceFile: a Novel subclass instance
        * targetFile: a Novel subclass instance
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath)
            isYwProject = True

        elif fileExtension == Yw6File.EXTENSION:
            sourceFile = Yw6File(sourcePath)
            isYwProject = True

        else:
            isYwProject = False

        if isYwProject:
            targetFile = MdFile(
                fileName + suffix + MdFile.EXTENSION, self.markdownMode, self.noSceneTitles)
            targetFile.SUFFIX = suffix

        else:
            sourceFile = MdFile(
                sourcePath, self.markdownMode, self.noSceneTitles)
            targetFile = Yw7File(fileName + Yw7File.EXTENSION)
            targetFile.ywTreeBuilder = Yw7TreeCreator()
            targetFile.ywProjectMerger = YwProjectCreator()

        return 'SUCCESS', sourceFile, targetFile
