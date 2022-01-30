#!/usr/bin/env python3
"""Markdown converter for yWriter projects. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.pywriter_globals import ERROR
from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd

from pywmd.md_file import MdFile
from pywmd.md_converter import MdConverter


def run(sourcePath, silentMode=True, markdownMode=False, noSceneTitles=False):

    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('Markdown converter for yWriter projects')

    converter = MdConverter()
    converter.ui = ui
    kwargs = {'suffix': MdFile.SUFFIX, 'markdownMode': markdownMode,
              'noSceneTitles': noSceneTitles}
    converter.run(sourcePath, **kwargs)


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
        print(f'{ERROR}File not found.')
