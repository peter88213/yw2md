#!/usr/bin/python3
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
from pywriter.config.configuration import Configuration
from pywriter.ui.ui import Ui
from yw2mdlib.md_converter import MdConverter
from yw2mdlib.yw2md_tk import Yw2mdTk

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
