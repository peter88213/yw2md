"""Provide a Markdown converter class for yWriter projects. 

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from pywriter.converter.new_project_factory import NewProjectFactory

from pywriter.yw.yw7_file import Yw7File
from yw2mdlib.md_file import MdFile


class MdConverter(YwCnvFf):
    """A converter class for Markdown export."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [MdFile]
    CREATE_SOURCE_CLASSES = [MdFile]

    def __init__(self):
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
