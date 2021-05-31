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

from disktools import bytes_to_int, bytes_to_str, str_to_bytes, int_to_bytes
from structures.Metadata import Metadata
from typing import Optional


class MetadataFactory(object):
    def __init__(
        self,
        MODE: Optional[int] = None,
        UID: Optional[int] = None,
        GID: Optional[int] = None,
        NLINKS: Optional[int] = None,
        SIZE: Optional[int] = None,
        CTIME: Optional[int] = None,
        MTIME: Optional[int] = None,
        ATIME: Optional[int] = None,
        LOCATION: Optional[int] = None,
        NAME: Optional[str] = None,
        TYPE: Optional[int] = None,
    ):
        self.mode = MODE
        self.uid = UID
        self.gid = GID
        self.nlinks = NLINKS
        self.size = SIZE
        self.ctime = CTIME
        self.mtime = MTIME
        self.atime = ATIME
        self.location = LOCATION
        self.name = NAME
        self.type = TYPE

    def set_with_params(
        self,
        MODE: Optional[int] = None,
        UID: Optional[int] = None,
        GID: Optional[int] = None,
        NLINKS: Optional[int] = None,
        SIZE: Optional[int] = None,
        CTIME: Optional[int] = None,
        MTIME: Optional[int] = None,
        ATIME: Optional[int] = None,
        LOCATION: Optional[int] = None,
        NAME: Optional[str] = None,
        TYPE: Optional[int] = None,
    ):
        self.mode = MODE
        self.uid = UID
        self.gid = GID
        self.nlinks = NLINKS
        self.size = SIZE
        self.ctime = CTIME
        self.mtime = MTIME
        self.atime = ATIME
        self.location = LOCATION
        self.name = NAME
        self.type = TYPE
        return self

    def set_with_bytes(self, metadata_bytes: bytearray):
        self.name = bytes_to_str(metadata_bytes[0:16])
        self.size = bytes_to_int(metadata_bytes[16:18])
        self.nlinks = bytes_to_int(metadata_bytes[18:19])
        self.mode = bytes_to_int(metadata_bytes[19:21])
        self.uid = bytes_to_int(metadata_bytes[21:23])
        self.gid = bytes_to_int(metadata_bytes[23:25])
        self.ctime = bytes_to_int(metadata_bytes[25:29])
        self.mtime = bytes_to_int(metadata_bytes[29:33])
        self.atime = bytes_to_int(metadata_bytes[33:37])
        self.location = bytes_to_int(metadata_bytes[37:38])
        self.type = bytes_to_int(metadata_bytes[38:39])
        return self

    def construct(self) -> Metadata:
        return Metadata.build_metadata(
            str_to_bytes(self.name or "", 16)
            + int_to_bytes(self.size or 0, 2)
            + int_to_bytes(self.nlinks or 0, 1)
            + int_to_bytes(self.mode or 0, 2)
            + int_to_bytes(self.uid or 0, 2)
            + int_to_bytes(self.gid or 0, 2)
            + int_to_bytes(self.ctime or 0, 4)
            + int_to_bytes(self.mtime or 0, 4)
            + int_to_bytes(self.atime or 0, 4)
            + int_to_bytes(self.location or 0, 1)
            + int_to_bytes(self.type or 0, 1)
        )