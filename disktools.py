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

from __future__ import division, print_function

import os
from typing import Any
from util.FMLog import FMLog

NUM_BLOCKS = 16
BLOCK_SIZE = 64
DISK_NAME = "my-disk"


def low_level_format() -> None:
    """Creates the file system space on disk.
    Warning: calling this erases any existing data in the file system.
    """
    with open(DISK_NAME, "w+b") as disk:
        for _ in range(NUM_BLOCKS):
            block = bytearray([0] * BLOCK_SIZE)
            disk.write(block)
        disk.flush()


def read_block(block_num: int) -> bytearray:
    """Reads block_num block from the file system.
    Return: a bytearray of BLOCK_SIZE
    """
    if block_num >= NUM_BLOCKS:
        raise IOError("Block number out of range")
    with open(DISK_NAME, "rb") as disk:
        disk.seek(block_num * BLOCK_SIZE)
        return bytearray(disk.read(BLOCK_SIZE))  # .encode())


def write_block(block_num: int, data: Any) -> None:
    """Writes data to the block_num block."""
    if block_num >= NUM_BLOCKS:
        raise IOError("Block number out of range")
    with open(DISK_NAME, "r+b") as disk:
        disk.seek(block_num * BLOCK_SIZE)
        disk.write(data)


def print_block(block_num: int) -> None:
    """Prints block_num block data."""
    data = read_block(block_num)
    print(
        "block:", block_num, " length of data:", len(data), " type of data:", type(data)
    )
    for b in data:
        print(b, end=" ")
    print()


def int_to_bytes(value: int, num_bytes: int) -> bytearray:
    """Store positive integer value in a big-endian bytearray of num_bytes."""
    bytes = bytearray(num_bytes)
    for i in range(num_bytes - 1, -1, -1):
        nbyte = value % 256
        bytes[i] = nbyte
        value = value // 256
    return bytes


def bytes_to_int(bytes: bytearray) -> int:
    """Convert a big-endian bytearray into a positive integer."""
    value = 0
    for i in bytes[:-1]:
        value += i
        value *= 256
    value += bytes[-1]
    return value


def str_to_bytes(value: str, num_bytes: int) -> bytearray:
    while len(value) < num_bytes:
        value += "\0"
    return bytearray(value.encode("ascii"))


def bytes_to_str(bytes_in: bytearray) -> str:
    return bytes_in.decode("ascii")


if __name__ == "__main__":
    low_level_format()
    os.system("od --address-radix=x -t x1 -a my-disk")
