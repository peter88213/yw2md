#!/usr/bin/env python3
"""Markdown converter for yWriter projects. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from pywriter.ui.ui_tk import UiTk
from pywriter.md.md_file import MdFile
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.file_factory import FileFactory
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywriter.yw.yw7_tree_creator import Yw7TreeCreator
from pywriter.yw.yw_project_creator import YwProjectCreator


class MdFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def __init__(self, markdownMode=False, noSceneTitles=False):
        self.markdownMode = markdownMode
        self.noSceneTitles = noSceneTitles

    def get_file_objects(self, sourcePath, suffix=MdFile.SUFFIX):
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


def run(sourcePath, silentMode=True, markdownMode=False, noSceneTitles=False):

    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('yw2md')

    converter = YwCnvUi()
    converter.ui = ui
    converter.fileFactory = MdFileFactory(markdownMode, noSceneTitles)
    converter.run(sourcePath, MdFile.SUFFIX)


if __name__ == '__main__':
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

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    if args.md:
        markdownMode = True

    else:
        markdownMode = False

    if args.notitles:
        noSceneTitles = True

    else:
        noSceneTitles = False

    if os.path.isfile(args.sourcePath):
        run(args.sourcePath, silentMode, markdownMode, noSceneTitles)

    else:
        print('ERROR: File not found.')
