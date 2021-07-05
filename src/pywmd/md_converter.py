"""Provide a Markdown converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.new_project_factory import NewProjectFactory

from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywmd.md_file import MdFile


class MdConverter(YwCnvUi):
    """A converter class for Markdown export."""
    EXPORT_SOURCE_CLASSES = [Yw7File, Yw6File]
    EXPORT_TARGET_CLASSES = [MdFile]
    CREATE_SOURCE_CLASSES = [MdFile]

    def __init__(self):
        YwCnvUi.__init__(self)
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)