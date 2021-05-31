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

from __future__ import annotations

from enum import Enum
from time import time
from typing import Optional

from constants import START_OF_CONTENT
from disktools import (
    bytes_to_int,
    bytes_to_str,
    int_to_bytes,
    str_to_bytes,
    write_block,
)
from util.FMLog import FMLog

from structures.Filetable import FileTable


class MetadataField(Enum):
    NAME = 0
    SIZE = 1
    NLINKS = 2
    MODE = 3
    UID = 4
    GID = 5
    CTIME = 6
    MTIME = 7
    ATIME = 8
    LOCATION = 9
    TYPE = 10


class Metadata:
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
        self.MODE = MODE
        self.UID = UID
        self.GID = GID
        self.NLINKS = NLINKS
        self.SIZE = SIZE
        self.CTIME = CTIME
        self.MTIME = MTIME
        self.ATIME = ATIME
        self.LOCATION = LOCATION
        self.NAME = NAME
        self.TYPE = TYPE

    def form_bytes(self) -> bytearray:
        """ Get the bytearray representation of the metadata """
        return (
            str_to_bytes(self.NAME or "", 16)
            + int_to_bytes(self.SIZE or 0, 2)
            + int_to_bytes(self.NLINKS or 0, 1)
            + int_to_bytes(self.MODE or 0, 2)
            + int_to_bytes(self.UID or 0, 2)
            + int_to_bytes(self.GID or 0, 2)
            + int_to_bytes(self.CTIME or 0, 4)
            + int_to_bytes(self.MTIME or 0, 4)
            + int_to_bytes(self.ATIME or 0, 4)
            + int_to_bytes(self.LOCATION or 0, 1)
            + int_to_bytes(self.TYPE or 0, 1)
        )

    @staticmethod
    def build_metadata(metadata_bytes: bytearray) -> Metadata:
        return Metadata(
            NAME=bytes_to_str(metadata_bytes[0:16]),
            SIZE=bytes_to_int(metadata_bytes[16:18]),
            NLINKS=bytes_to_int(metadata_bytes[18:19]),
            MODE=bytes_to_int(metadata_bytes[19:21]),
            UID=bytes_to_int(metadata_bytes[21:23]),
            GID=bytes_to_int(metadata_bytes[23:25]),
            CTIME=bytes_to_int(metadata_bytes[25:29]),
            MTIME=bytes_to_int(metadata_bytes[29:33]),
            ATIME=bytes_to_int(metadata_bytes[33:37]),
            LOCATION=bytes_to_int(metadata_bytes[37:38]),
            TYPE=bytes_to_int(metadata_bytes[38:39]),
        )

    def print_metadata(self) -> None:
        elements = ""
        for attr, val in self.__dict__.items():
            elements += f"{attr}: {val}, "

    def save_to_block(self, block: int) -> None:
        """ Set the metadata space of the given block (from 0 to 38, inclusive) to this metadata. """
        full_block = FileTable().read_block(block)
        data_section = full_block[START_OF_CONTENT:]
        new_bytes = self.form_bytes() + data_section
        write_block(block, new_bytes)
        FMLog.success(f"Wrote new metadata to block {block}")

    def fetch_metadata(self, metadataKey: MetadataField) -> bytearray:
        """ Fetch a value in the metadata """
        return Metadata.fetch_metadata_static(self.form_bytes(), metadataKey)

    def to_st_form(self):
        return {
            "st_mode": self.MODE,
            "st_ctime": self.CTIME,
            "st_mtime": self.MTIME,
            "st_atime": self.ATIME,
            "st_nlink": self.NLINKS,
            "st_uid": self.UID,
            "st_gid": self.GID,
            "st_size": self.SIZE,
        }

    def update_all_times(self):
        """ Updates the times to now. Doesn't save, just edits the object. """
        now = time()
        self.ATIME = int(now)  # type: ignore
        self.CTIME = int(now)  # type: ignore
        self.MTIME = int(now)  # type: ignore

    @staticmethod
    def fetch_metadata_static(
        metadata_object: bytearray, metadataKey: MetadataField
    ) -> bytearray:
        if metadataKey == MetadataField.NAME:
            return metadata_object[0:16]
        if metadataKey == MetadataField.SIZE:
            return metadata_object[16:18]
        if metadataKey == MetadataField.NLINKS:
            return metadata_object[18:19]
        if metadataKey == MetadataField.MODE:
            return metadata_object[19:21]
        if metadataKey == MetadataField.UID:
            return metadata_object[21:23]
        if metadataKey == MetadataField.GID:
            return metadata_object[23:25]
        if metadataKey == MetadataField.CTIME:
            return metadata_object[25:29]
        if metadataKey == MetadataField.MTIME:
            return metadata_object[29:33]
        if metadataKey == MetadataField.ATIME:
            return metadata_object[33:37]
        if metadataKey == MetadataField.LOCATION:
            return metadata_object[37:38]
        if metadataKey == MetadataField.TYPE:
            return metadata_object[38:39]
