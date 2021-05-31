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

from errno import EINVAL, ENOENT
from typing import List, Optional, Tuple

from constants import END_OF_METADATA, START_OF_CONTENT, START_OF_METADATA
from disktools import int_to_bytes
from fuse import FuseOSError
from util.FMLog import FMLog

import structures.Filesystem
from structures.AbstractItem import AbstractItem
from structures.File import File
from structures.Filetable import FileTable
from structures.Metadata import Metadata


class Directory(AbstractItem):
    """A directory class. Directories are stored as blocks in the filesystem,
    like normal files. A directory is a list of metadata, followed by several
    bytes, which point to the block locations of all files within."""

    def __init__(self, block: int = 1) -> None:
        super().__init__(block=block)

    def fetch_directory_blocks(self) -> bytearray:
        return FileTable().read_full_file(self.block)

    def get_dir_data(self) -> Tuple[bytearray, bytearray]:
        """Fetch the directory data, returns a tuple containing the metadata of
        the directory, and then the actual directory data"""
        directory = FileTable().read_full_file(self.block)

        return (
            directory[START_OF_METADATA:END_OF_METADATA],
            directory[START_OF_CONTENT:],
        )

    def block_index_from_name(self, name: str) -> int:
        files = self.get_files()
        for file in files:
            (filename, location, _) = file
            if filename == name:
                return location
        raise FuseOSError(ENOENT)

    def smart_resolve(self, name: Optional[str], block: Optional[int]):
        if name is not None:
            block = self.block_index_from_name(name)

        if block is None:
            raise FuseOSError(EINVAL)

        fs = structures.Filesystem.Filesystem()
        metadata = fs.get_block_metadata(block)

        if metadata.TYPE == 1:
            return File(block)
        elif metadata.TYPE == 0:
            return Directory(block)
        else:
            raise FuseOSError(EINVAL)

    def get_files(self, strip_null: bool = False) -> List[Tuple[str, int, int]]:
        """Retusn a list of files (name, block location) in the directory.
        Files includes files and directories. If strip_null is set to true, then
        file names are stripped of all trailing null values."""
        (_, files) = self.get_dir_data()
        file_tuples: List[Tuple[str, int, int]] = []
        fs = structures.Filesystem.Filesystem()

        def fetch_name(block_index: int) -> str:
            metadata = fs.get_block_metadata(block_index)
            return metadata.NAME or ""

        def fetch_type(block_index: int) -> int:
            metadata = fs.get_block_metadata(block_index)
            file_type = metadata.TYPE
            if file_type == None:
                raise FuseOSError(EINVAL)
            return file_type

        for block_index in files:
            if block_index == 0:
                break
            filename = fetch_name(block_index)
            filetype = fetch_type(block_index)
            file_tuples.append((filename, block_index, filetype))
        if strip_null:
            return list(map(lambda x: (x[0].rstrip("\x00"), x[1], x[2]), file_tuples))

        return file_tuples

    def add_file(self, file_name: str, data: str, metadata: Metadata) -> AbstractItem:
        """Add a file to the filesystem, in this directory. This will write the
        file to the disk, add it to this directory entry, and add it to the
        filetable."""
        filetable = FileTable()

        # get a new block to place the file at
        first_loc = filetable.find_free_block()

        existing = self.ensure_uniqueness(file_name)
        if existing != -1:
            # file with this name exists, so destroy existing data
            filetable.purge_full_file(existing)

        # set the LOCATION metadata field to this location
        metadata.LOCATION = first_loc

        # Write the data to the blocks, then add these blocks to the filetable
        blocks_to_write = filetable.write_to_block(data, metadata.form_bytes())
        filetable.write_to_table(blocks_to_write)

        location_as_bytes = int_to_bytes(blocks_to_write[0], 1)
        [dir_metadata, dir_refs] = self.get_dir_data()
        dir_data = (
            dir_metadata + self.clear_nulls_from_bytes(dir_refs, 1) + location_as_bytes
        )

        self.save(dir_data)
        return self.smart_resolve(block=blocks_to_write[0], name=None)

    # TODO remove NLINKS by one if dir
    def remove_file(self, file_location: int) -> None:
        ft = FileTable()
        (metadata, new_data) = self.get_dir_data()

        # get the last item, replace the to-be-deleted with it
        new_data.remove(file_location)
        ft.purge_full_file(file_location)
        self.save(metadata + new_data)

    def unlink_file(self, file_location: int) -> None:
        """ Removes the file from this directory, without actually removing any of its data """
        (metadata, new_data) = self.get_dir_data()
        new_data.remove(file_location)
        self.save(metadata + new_data)

    def link_file(self, file_location: int, with_name: str) -> None:
        """ Links an existing file to this directory """
        (metadata, dir_data) = self.get_dir_data()
        new_dir_data = (
            metadata
            + self.clear_nulls_from_bytes(dir_data, 1)
            + int_to_bytes(file_location, 1)
        )
        self.save(new_dir_data)
        FMLog.success(
            f"Linked file to dirblock {self.block}, with data meta {metadata} and data {self.clear_nulls_from_bytes(dir_data,1)+bytearray(file_location)}"
        )

        file_meta = structures.Filesystem.Filesystem().get_block_metadata(file_location)
        file_meta.NAME = with_name
        file_meta.save_to_block(file_location)

    def ensure_uniqueness(self, filename: str) -> int:
        files = self.get_files(strip_null=True)
        for name, loc, _ in files:
            if name == filename:
                return loc
        return -1

    def deleteable(self) -> bool:
        return len(self.get_files()) == 0

    @staticmethod
    def slice_per(
        source: bytearray,
        step: int,
    ) -> List[bytearray]:
        return_array: List[bytearray] = []
        for index in range(0, len(source), step):
            return_array.append(source[index : index + step])
        return return_array

    @staticmethod
    def clear_nulls_from_bytes(source: bytearray, step: int = 1) -> bytearray:
        return_bytes: bytearray = bytearray()
        for index in range(0, len(source), step):
            if source[index] == 0:
                return return_bytes
            return_bytes += source[index : index + step]
        return return_bytes