"""Provide a factory class for import source and target objects.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.file_factory import FileFactory

from pywriter.yw.yw7_new_file import Yw7NewFile
from pywmd.md_file import MdFile


class NewProjectFactory(FileFactory):
    """A factory class that instantiates source and target file objects."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Factory method.
        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance

        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == MdFile.EXTENSION:

            # The source file might be an outline or a "work in progress".

            targetFile = Yw7NewFile(
                fileName + Yw7NewFile.EXTENSION, **kwargs)

            sourceFile = MdFile(sourcePath, **kwargs)

        else:
            return 'ERROR: File type of  "' + os.path.normpath(sourcePath) + '" not supported.', None, None

        return 'SUCCESS', sourceFile, targetFile
