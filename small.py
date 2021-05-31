#!/usr/bin/env python

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

from __future__ import absolute_import, division, print_function

import logging
import os
import platform
import sys
from errno import ENOENT, ENOTEMPTY
from stat import S_IFDIR, S_IFREG
from time import time
from typing import Any, Optional, Tuple

from fuse import FUSE, FuseOSError, LoggingMixIn, Operations

from constants import END_OF_METADATA
from structures.Directory import Directory
from structures.Filesystem import Filesystem
from structures.Filetable import FileTable
from structures.Metadata import Metadata
from util.FMLog import FMLog


class Small(LoggingMixIn, Operations):
    def __init__(self):
        self.fd = 0

    def create(self, path: str, mode: int, fi: Any = ...):
        fs = Filesystem()
        fs.create_file(path, mode)

        self.fd += 1

        return self.fd

    def getattr(self, path: str, fh=None):
        fs = Filesystem()
        item = fs.smart_resolver(path)
        return item.get_metadata().to_st_form()

    def getxattr(self, path: str, name: str, position: int = 0):
        return bytes()

    def mkdir(self, path: str, mode: int):
        fs = Filesystem()
        fs.create_dir(path, mode)

    def open(self, path: str, flags):
        self.fd += 1
        return self.fd

    def read(self, path: str, size: int, offset: int, fh):
        fs = Filesystem()

        item = fs.smart_resolver(path)
        contents = item.get_contents()
        offsetted = contents[offset : offset + size]

        return bytes(Directory.clear_nulls_from_bytes(offsetted))

    def readdir(self, path: str, fh):
        fs = Filesystem()

        files = fs.smart_resolver(path).get_files(strip_null=True)
        names = list(map(lambda x: x[0], files))

        return [".", ".."] + names

    def rename(self, old: str, new: str):
        fs = Filesystem()
        (old_path, _) = fs.get_path_and_base(old)
        (new_path, new_name) = fs.get_path_and_base(new)

        old_parent = fs.smart_resolver(old_path).upcast_dir()
        new_parent = fs.smart_resolver(new_path).upcast_dir()

        file_location = fs.path_resolver(old)

        old_parent.unlink_file(file_location)
        new_parent.link_file(file_location, new_name)

    def rmdir(self, path: str):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        fs = Filesystem()
        dir_to_remove = fs.dir_from_block(fs.path_resolver(path))
        if not dir_to_remove.deleteable():
            raise FuseOSError(ENOTEMPTY)

        (parent_path, _) = fs.get_path_and_base(path)
        parent_loc = fs.path_resolver(parent_path)
        parent_dir = fs.dir_from_block(parent_loc)
        parent_dir.remove_file(dir_to_remove.block)

        current_links = (
            Metadata.build_metadata(parent_dir.get_dir_data()[0]).NLINKS or 2
        )
        parent_dir.update_metadata(Metadata(NLINKS=current_links - 1))

    def statfs(self, path: str):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def unlink(self, path: str):
        fs = Filesystem()
        (dir_path, _) = fs.get_path_and_base(path)

        directory_block = fs.path_resolver(dir_path)
        file_dir = Directory(directory_block)

        file_location = fs.path_resolver(path)
        file_dir.remove_file(file_location)

    def utimens(self, path: str, times: Optional[Tuple[float, float]] = None):
        now = time()
        atime, mtime = times if times else (now, now)
        fs = Filesystem()
        block_location = fs.path_resolver(path)
        metadata = fs.get_block_metadata(block_location)
        metadata.ATIME = int(atime)
        metadata.MTIME = int(mtime)
        metadata.save_to_block(block_location)

    def write(self, path: str, data: bytes, offset: int, fh):
        fs = Filesystem()

        block_of_interest = fs.path_resolver(path)
        size = fs.edit_file(block_of_interest, data, offset)

        return size


if __name__ == "__main__":
    import argparse

    version = platform.python_version_tuple()
    if not (int(version[0]) == 3 and (int(version[1]) >= 8)):
        FMLog.error(
            f"Python 3.8.5 may be required. Features are used that might not be in your detected version, Python {platform.python_version()}."
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("mount")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Small(), args.mount, foreground=True)
