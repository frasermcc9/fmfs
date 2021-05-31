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

END_OF_FILE = 0xF0
FREE_SPACE = 0xFF
RESERVED_SPACE = 0xFE

FILE_TABLE_SPACE = 0x30

NUM_BLOCKS = 16
BLOCK_SIZE = 64
DISK_NAME = "my-disk"

START_OF_METADATA = 0
END_OF_METADATA = 39
START_OF_CONTENT = 39
