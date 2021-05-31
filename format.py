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
from structures.factories.MetadataFactory import MetadataFactory
from time import time
from disktools import BLOCK_SIZE, NUM_BLOCKS, write_block
from constants import END_OF_FILE, FREE_SPACE
from stat import S_IFDIR
from util.FMLog import FMLog

# Filetable
initial_table_block = bytearray([FREE_SPACE] * NUM_BLOCKS)
initial_table_block[0] = END_OF_FILE
initial_table_block[1] = END_OF_FILE

FMLog.warn("✔  Created filetable in disk block 0")

now = time()
dir_meta = (
    MetadataFactory()
    .set_with_params(
        LOCATION=0x01,
        MODE=(S_IFDIR | 0o755),
        ATIME=int(now),
        CTIME=int(now),
        MTIME=int(now),
        NLINKS=2,
        GID=os.getgid(),
        UID=os.getuid(),
        NAME="FMFS",
        TYPE=0,
        SIZE=64,
    )
    .construct()
    .form_bytes()
)

root_dir = bytearray([0] * (BLOCK_SIZE - len(dir_meta)))
write_block(0, initial_table_block)
write_block(1, dir_meta + root_dir)

FMLog.warn("✔  Created root directory in disk block 1")


FMLog.trace("🚀 Installation and initialization of the FM Filesystem is complete!")