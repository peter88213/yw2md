#!/usr/bin/env python3
"""Export yWriter project to markdown. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.md.md_file import MdFile
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.ui_cmd import UiCmd
from pywriter.converter.file_factory import FileFactory
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywriter.yw.yw7_tree_creator import Yw7TreeCreator
from pywriter.yw.yw_project_creator import YwProjectCreator


class MdFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def __init__(self, markdownMode=False):
        self.markdownMode = markdownMode

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
            targetFile = MdFile(fileName + suffix + MdFile.EXTENSION)
            targetFile.SUFFIX = suffix

        else:
            sourceFile = MdFile(sourcePath, self.markdownMode)
            targetFile = Yw7File(fileName + Yw7File.EXTENSION)
            targetFile.ywTreeBuilder = Yw7TreeCreator()
            targetFile.ywProjectMerger = YwProjectCreator()

        return 'SUCCESS', sourceFile, targetFile


class Converter(YwCnvUi):
    """yWriter converter with a command line UI. 
    """

    def __init__(self, silentMode, markdownMode=False):
        YwCnvUi.__init__(self)
        self.fileFactory = MdFileFactory(markdownMode)

        if not silentMode:
            self.userInterface = UiCmd('Export yWriter project to Markdown')


def run(sourcePath, silentMode=True, markdownMode=False):
    Converter(silentMode, markdownMode).run(sourcePath, MdFile.SUFFIX)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Markdown converter for yWriter projects.',
        epilog='')
    parser.add_argument('sourcePath', metavar='Source file',
                        help="The path of the source file for the conversion. "
                        "If it's a yWriter project file with extension 'yw6' or 'yw7', "
                        "a new Markdoen formatted text document will be created. "
                        "Otherwise, the source file will be considered a Markdown "
                        "formatted file to be converted to a new yWriter 7 project. "
                        "Existing yWriter projects are not overwritten. "
                        "Headings are considered chapter titles. Scenes within "
                        "chapters are separated by '" + MdFile.SCENE_DIVIDER +
                        "'. All scenes are Markdown formatted, so do not use "
                        "yWriter's built-in exporters.")
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    parser.add_argument('--md',
                        action="store_true",
                        help='when creating a yWriter project, use markdown for the scenes')
    args = parser.parse_args()

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    if args.md:
        markdownMode = True

    else:
        markdownMode = False

    if os.path.isfile(args.sourcePath):
        run(args.sourcePath, silentMode, markdownMode)

    else:
        print('ERROR: File not found.')
