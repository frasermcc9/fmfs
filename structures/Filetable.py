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

from typing import List
from constants import BLOCK_SIZE, FREE_SPACE, END_OF_FILE
from disktools import read_block, write_block
from errno import ENOSPC
from util.FMLog import FMLog


class FileTable(object):
    def __init__(self) -> None:
        self.block = 0

    def get_filetable(self) -> bytearray:
        return self.read_block(self.block)

    def read_block(self, at_location: int) -> bytearray:
        return read_block(at_location)

    def read_full_file(self, at_location: int) -> bytearray:
        filetable_snapshot = self.get_filetable()
        current_block = at_location
        next_block = filetable_snapshot[at_location]
        return_array: bytearray = bytearray()
        while True:
            return_array += read_block(current_block)
            current_block = next_block
            if current_block == END_OF_FILE:
                break
            next_block = filetable_snapshot[current_block]
        return return_array

    def purge_full_file(self, at_location: int) -> None:
        current_block = at_location
        filetable_snapshot = self.get_filetable()

        next_block = filetable_snapshot[at_location]
        while True:
            filetable_snapshot[current_block] = FREE_SPACE
            write_block(current_block, bytearray([0] * BLOCK_SIZE))
            current_block = next_block
            if current_block == END_OF_FILE:
                break
            next_block = filetable_snapshot[current_block]
        write_block(0, filetable_snapshot)

    def get_file_blocks(self, start_block: int) -> List[int]:
        filetable_snapshot = self.get_filetable()
        blocks: List[int] = []
        current_block = start_block
        while True:
            blocks.append(current_block)
            current_block = filetable_snapshot[current_block]
            if current_block == END_OF_FILE:
                break

        return blocks

    def find_free_block(self, exclude: List[int] = []):
        filetable = self.get_filetable()
        iterator = 0
        for i in filetable:
            if i == FREE_SPACE and (not iterator in exclude):
                return iterator
            iterator += 1
        raise IOError(ENOSPC, "ENOSPC: No space left on device")

    def write_to_block(self, data: str, metadata: bytearray) -> List[int]:
        data_as_bytes = metadata + bytearray(data.encode(encoding="ascii"))
        size = len(data_as_bytes)

        split_blocks = [
            data_as_bytes[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE]
            for i in range((size + BLOCK_SIZE - 1) // BLOCK_SIZE)
        ]

        written_blocks: List[int] = []

        for i in split_blocks:
            free: int = self.find_free_block(written_blocks)
            write_block(free, i)
            written_blocks.append(free)
        return written_blocks

    def write_bytes_to_block(
        self, data: bytearray, overwrite: List[int] = [], print: bool = False
    ) -> List[int]:
        # print(overwrite)
        # print(data)
        data_as_bytes = data
        size = len(data_as_bytes)

        split_blocks = [
            data_as_bytes[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE]
            for i in range((size + BLOCK_SIZE - 1) // BLOCK_SIZE)
        ]

        written_blocks: List[int] = []

        def get_block_to_write(level: int) -> int:
            if level < len(overwrite):
                return overwrite[level]
            return self.find_free_block(written_blocks)

        iterator = 0

        for i in split_blocks:
            free: int = get_block_to_write(iterator)
            write_block(free, i)
            written_blocks.append(free)
            iterator += 1

        return written_blocks

    def write_to_table(self, locations: List[int]) -> None:
        filetable = self.get_filetable()
        location_len = len(locations)
        for i in range(location_len):
            location = locations[i]
            if i + 1 == location_len:
                filetable[location] = END_OF_FILE
            else:
                filetable[location] = locations[i + 1]
        to_write = filetable
        write_block(0, to_write)
