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

import os
from errno import EINVAL, ENOENT
from os.path import basename
from stat import S_IFDIR, S_IFREG
from structures.factories.DirFactory import DirFactory
from time import time
from typing import Tuple

from constants import END_OF_METADATA
from disktools import read_block
from fuse import FuseOSError
from util.FMLog import FMLog

from structures.AbstractItem import AbstractItem
from structures.factories.ItemFactory import ItemFactory
from structures.factories.MetadataFactory import MetadataFactory
from structures.File import File
from structures.Filetable import FileTable
from structures.Metadata import Metadata


class Filesystem(object):
    def __init__(self) -> None:
        super().__init__()

    def get_root(self):
        return DirFactory().root()

    def get_filetable(self) -> FileTable:
        return FileTable()

    def smart_resolver(self, path: str) -> AbstractItem:
        block = self.path_resolver(path)
        if block == -1:
            raise FuseOSError(ENOENT)
        item = AbstractItem(block)
        item_type = item.type_from_metadata()
        if item_type == 0:
            return DirFactory(block).construct()
        if item_type == 1:
            return File(block)
        raise FuseOSError(EINVAL)

    def path_resolver(self, path: str) -> int:
        """ Given a path, get the block index of the basename of the path. """
        if path == "/":
            return 1

        chunks = path.split(os.path.sep)[1:]

        last_chunk = chunks[-1]

        current_dir = self.get_root()
        found = False
        final_location = None
        is_at_end = False

        for chunk in chunks:
            possible_file = last_chunk == chunk
            found = False
            directory_files = current_dir.get_files(strip_null=True)
            for filename, file_location, filetype in directory_files:
                if filename == chunk:
                    # found a valid name
                    if filetype == 1 and not possible_file:
                        # impossible
                        FMLog.error(
                            "Filetype indicated this is a file, but the path states this should not be a file."
                        )
                        raise FuseOSError(EINVAL)
                    final_location = file_location
                    found = True
                    if possible_file:
                        is_at_end = True
                    else:
                        current_dir = self.dir_from_block(file_location)
                    break

            if not found:
                return -1

        if not is_at_end:
            raise FuseOSError(ENOENT)

        if not final_location:
            return -1

        return final_location

    def get_block_metadata(self, block_index: int) -> Metadata:
        file = read_block(block_index)
        return Metadata.build_metadata(file[0:END_OF_METADATA])

    def dir_from_block(self, block_index: int):
        data = self.get_block_metadata(block_index)
        if data.TYPE == 1:
            FMLog.error(f"Expected directory, found file")
            raise FuseOSError(ENOENT)
        return DirFactory(block_index).construct()

    def file_from_block(self, block_index: int):
        data = self.get_block_metadata(block_index)
        if data.TYPE == 0:
            FMLog.error(f"Expected file, found directory")
            raise FuseOSError(ENOENT)
        return File(block_index)

    def internal_item_maker(self, path: str, mode: int, f_type: int) -> AbstractItem:
        [dirname, filename] = self.get_path_and_base(path)
        block = self.path_resolver(dirname)
        dirent = self.dir_from_block(block_index=block)
        child_links = 1
        base_mode = S_IFREG

        if f_type == 0:
            current_links = dirent.get_metadata().NLINKS or 0
            dirent.update_metadata(Metadata(NLINKS=current_links + 1))
            child_links = 2
            base_mode = S_IFDIR

        return dirent.add_file(
            file_name=filename,
            data="",
            metadata=MetadataFactory(
                MODE=(base_mode | mode),
                ATIME=int(time()),
                MTIME=int(time()),
                CTIME=int(time()),
                SIZE=0 if f_type == 1 else 64,
                NLINKS=child_links,
                NAME=filename,
                TYPE=f_type,
                UID=os.getuid(),
                GID=os.getgid(),
            ).construct(),
        )

    def create_file(self, path: str, mode: int):
        return self.internal_item_maker(path, mode, 1)

    def create_dir(self, path: str, mode: int):
        return self.internal_item_maker(path, mode, 0)

    def edit_file(self, first_block: int, data: bytes, offset: int) -> int:
        """
        Returns the number of bytes written
        """
        filetable = FileTable()

        (metadata, old_data) = ItemFactory(first_block).create().get_data()

        data_to_keep = old_data[0:offset]
        file_size = len(data + data_to_keep)

        metadata.update_all_times()
        metadata.SIZE = file_size

        if not metadata.LOCATION:
            FMLog.error("Cannot edit file that does not have location in metadata")
            raise FuseOSError(ENOENT)

        to_write = metadata.form_bytes() + data_to_keep + bytearray(data)

        locations = filetable.write_bytes_to_block(
            to_write,
            filetable.get_file_blocks(metadata.LOCATION),
        )

        filetable.write_to_table(locations)

        return len(data)

    @staticmethod
    def get_path_and_base(path: str) -> Tuple[str, str]:
        """ Tuple return with (dir, path) """
        filename = basename(path)
        dirname = os.path.dirname(path)
        return (dirname, filename)
