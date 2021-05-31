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


class DirFactory(object):
    def __init__(self, index: int = 1) -> None:
        self.index = index

    def construct(self):
        from structures.Directory import Directory

        return Directory(self.index)

    def root(self):
        from structures.Directory import Directory

        return Directory(1)
