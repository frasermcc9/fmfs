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
from typing import List, Tuple

from constants import END_OF_METADATA, START_OF_CONTENT, START_OF_METADATA
from fuse import FuseOSError
from util.FMLog import FMLog

import structures.Directory
from structures.Filetable import FileTable
from structures.Metadata import Metadata


class AbstractItem(object):
    def __init__(self, block: int) -> None:
        super().__init__()
        self.block = block

    def get_metadata(self) -> Metadata:
        data = FileTable().read_block(self.block)
        return Metadata.build_metadata(data[START_OF_METADATA:END_OF_METADATA])

    def get_contents(self) -> bytearray:
        data = FileTable().read_full_file(self.block)
        return data[START_OF_CONTENT:]

    def get_files(self, strip_null: bool = False) -> List[Tuple[str, int, int]]:
        return []

    def get_data(self) -> Tuple[Metadata, bytearray]:
        return (self.get_metadata(), self.get_contents())

    def save(self, new_data: bytearray, metadata_only_change: bool = False) -> None:
        filetable = FileTable()

        blocks_from_dir = filetable.get_file_blocks(self.block)

        locations = filetable.write_bytes_to_block(new_data, blocks_from_dir)

        if not metadata_only_change:
            self.update_metadata(Metadata(SIZE=len(locations) * 64))

        filetable.write_to_table(locations)

    def update_metadata(self, new_metadata: Metadata) -> None:
        (existing_metadata, normal_data) = self.get_data()

        new_metadata.ATIME = new_metadata.ATIME or existing_metadata.ATIME
        new_metadata.CTIME = new_metadata.CTIME or existing_metadata.CTIME
        new_metadata.MTIME = new_metadata.MTIME or existing_metadata.MTIME
        new_metadata.GID = new_metadata.GID or existing_metadata.GID
        new_metadata.UID = new_metadata.UID or existing_metadata.UID
        new_metadata.LOCATION = new_metadata.LOCATION or existing_metadata.LOCATION
        new_metadata.MODE = new_metadata.MODE or existing_metadata.MODE
        new_metadata.NLINKS = new_metadata.NLINKS or existing_metadata.NLINKS
        new_metadata.SIZE = new_metadata.SIZE or existing_metadata.SIZE
        new_metadata.TYPE = new_metadata.TYPE or existing_metadata.TYPE
        new_metadata.NAME = new_metadata.NAME or existing_metadata.NAME

        self.save(new_metadata.form_bytes() + normal_data, True)

    def type_from_metadata(self) -> int:
        self.get_metadata().print_metadata()
        type_of_item = self.get_metadata().TYPE
        if type_of_item is None:
            return -1
        return type_of_item

    def upcast_dir(self):
        if self.type_from_metadata() == 1:
            raise FuseOSError(EINVAL)
        return structures.Directory.Directory(self.block)
