# ************************************************************************
#
# Copyright 2021 Fraser McCallum.
# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property of
# Fraser McCallum (the author) and his affiliates, if any. The intellectual and
# technical concepts contained herein are proprietary to the author, and are
# protected by copyright law. Dissemination of this information or reproduction
# of this material is strictly forbidden unless prior written permission is
# obtained from the author.
# ************************************************************************

from errno import EINVAL

import structures.Directory
from constants import END_OF_METADATA, START_OF_METADATA
from fuse import FuseOSError
from structures.AbstractItem import AbstractItem
from structures.factories.MetadataFactory import MetadataFactory
from structures.File import File
from structures.Filetable import FileTable


class ItemFactory(object):
    def __init__(self, block_index: int) -> None:
        super().__init__()
        self.block_index = block_index

    def create(self) -> AbstractItem:
        data = FileTable().read_block(self.block_index)
        metadata = data[START_OF_METADATA:END_OF_METADATA]
        item_type = MetadataFactory().set_with_bytes(metadata).construct().TYPE

        if item_type == 0:
            return structures.Directory.Directory(self.block_index)
        if item_type == 1:
            return File(self.block_index)
        raise FuseOSError(EINVAL)
