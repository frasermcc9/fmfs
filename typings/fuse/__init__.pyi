"""
Author: Fraser McCallum
This type stub file was generated by pyright.
"""

import ctypes
import errno
import logging
import os
import warnings
import sys
from __future__ import absolute_import, division, print_function
from ctypes.util import find_library
from platform import machine, system
from signal import SIGINT, SIG_DFL, signal
from stat import S_IFDIR
from traceback import print_exc

log = ...
_system = ...
_machine = ...
if _system == "Windows":
    ...
if _system == "Windows" or _system.startswith("CYGWIN"):
    class c_timespec(ctypes.Structure):
        _fields_ = ...

else:
    class c_timespec(ctypes.Structure):
        _fields_ = ...


class c_utimbuf(ctypes.Structure):
    _fields_ = ...


class c_stat(ctypes.Structure):
    ...


_libfuse_path = ...
if not _libfuse_path:
    ...
if not _libfuse_path:
    ...
else:
    _libfuse = ...
if _system == "Darwin" and hasattr(_libfuse, "macfuse_version"):
    _system = ...
if _system in ("Darwin", "Darwin-MacFuse", "FreeBSD"):
    ENOTSUP = ...
    c_dev_t = ...
    c_fsblkcnt_t = ...
    c_fsfilcnt_t = ...
    c_gid_t = ...
    c_mode_t = ...
    c_off_t = ...
    c_pid_t = ...
    c_uid_t = ...
    setxattr_t = ...
    getxattr_t = ...
else:
    ENOTSUP = ...
    c_dev_t = ...
    c_fsblkcnt_t = ...
    c_fsfilcnt_t = ...
    c_gid_t = ...
    c_mode_t = ...
    c_off_t = ...
    c_pid_t = ...
    c_uid_t = ...
    setxattr_t = ...
    getxattr_t = ...
if _system == "FreeBSD":
    c_fsblkcnt_t = ...
    c_fsfilcnt_t = ...
    setxattr_t = ...
    getxattr_t = ...

    class c_statvfs(ctypes.Structure):
        _fields_ = ...

else:
    class c_statvfs(ctypes.Structure):
        _fields_ = ...

    class c_statvfs(ctypes.Structure):
        _fields_ = ...

if _system == "Windows" or _system.startswith("CYGWIN"):
    class fuse_file_info(ctypes.Structure):
        _fields_ = ...

else:
    class fuse_file_info(ctypes.Structure):
        _fields_ = ...


class fuse_context(ctypes.Structure):
    _fields_ = ...


class fuse_operations(ctypes.Structure):
    _fields_ = ...


def time_of_timespec(ts, use_ns=...): ...


def set_st_attrs(st, attrs, use_ns=...): ...


def fuse_get_context():
    "Returns a (uid, gid, pid) tuple"
    ...


def fuse_exit():
    """
    This will shutdown the FUSE mount and cause the call to FUSE(...) to
    return, similar to sending SIGINT to the process.

    Flags the native FUSE session as terminated and will cause any running FUSE
    event loops to exit on the next opportunity. (see fuse.c::fuse_exit)
    """
    ...


class FuseOSError(OSError):
    def __init__(self, errno) -> None: ...


class FUSE(object):
    """
    This class is the lower level interface and should not be subclassed under
    normal use. Its methods are called by fuse.

    Assumes API version 2.6 or later.
    """

    OPTIONS = ...

    def __init__(
        self, operations, mountpoint, raw_fi=..., encoding=..., **kwargs
    ) -> None:
        """
        Setting raw_fi to True will cause FUSE to pass the fuse_file_info
        class as is to Operations, instead of just the fh field.

        This gives you access to direct_io, keep_cache, etc.
        """
        ...

    def getattr(self, path, buf): ...
    def readlink(self, path, buf, bufsize): ...
    def mknod(self, path, mode, dev): ...
    def mkdir(self, path, mode): ...
    def unlink(self, path): ...
    def rmdir(self, path): ...

    def symlink(self, source, target):
        "creates a symlink `target -> source` (e.g. ln -s source target)"
        ...

    def rename(self, old, new): ...

    def link(self, source, target):
        "creates a hard link `target -> source` (e.g. ln source target)"
        ...

    def chmod(self, path, mode): ...
    def chown(self, path, uid, gid): ...
    def truncate(self, path, length): ...
    def open(self, path, fip): ...
    def read(self, path, buf, size, offset, fip): ...
    def write(self, path, buf, size, offset, fip): ...
    def statfs(self, path, buf): ...
    def flush(self, path, fip): ...
    def release(self, path, fip): ...
    def fsync(self, path, datasync, fip): ...
    def setxattr(self, path, name, value, size, options, *args): ...
    def getxattr(self, path, name, value, size, *args): ...
    def listxattr(self, path, namebuf, size): ...
    def removexattr(self, path, name): ...
    def opendir(self, path, fip): ...
    def readdir(self, path, buf, filler, offset, fip): ...
    def releasedir(self, path, fip): ...
    def fsyncdir(self, path, datasync, fip): ...
    def init(self, conn): ...
    def destroy(self, private_data): ...
    def access(self, path, amode): ...
    def create(self, path, mode, fip): ...
    def ftruncate(self, path, length, fip): ...
    def fgetattr(self, path, buf, fip): ...
    def lock(self, path, fip, cmd, lock): ...
    def utimens(self, path, buf): ...
    def bmap(self, path, blocksize, idx): ...
    def ioctl(self, path, cmd, arg, fip, flags, data): ...


class Operations(object):
    """
    This class should be subclassed and passed as an argument to FUSE on
    initialization. All operations should raise a FuseOSError exception on
    error.

    When in doubt of what an operation should do, check the FUSE header file
    or the corresponding system call man page.
    """

    def __call__(self, op, *args): ...
    def access(self, path, amode): ...
    bmap = ...
    def chmod(self, path, mode): ...
    def chown(self, path, uid, gid): ...

    def create(self, path, mode, fi=...):
        """
        When raw_fi is False (default case), fi is None and create should
        return a numerical file handle.

        When raw_fi is True the file handle should be set directly by create
        and return 0.
        """
        ...

    def destroy(self, path):
        "Called on filesystem destruction. Path is always /"
        ...

    def flush(self, path, fh): ...
    def fsync(self, path, datasync, fh): ...
    def fsyncdir(self, path, datasync, fh): ...

    def getattr(self, path, fh=...):
        """
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incompatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        """
        ...

    def getxattr(self, path, name, position=...): ...

    def init(self, path):
        """
        Called on filesystem initialization. (Path is always /)

        Use it instead of __init__ if you start threads on initialization.
        """
        ...

    def ioctl(self, path, cmd, arg, fip, flags, data): ...

    def link(self, target, source):
        "creates a hard link `target -> source` (e.g. ln source target)"
        ...

    def listxattr(self, path): ...
    lock = ...
    def mkdir(self, path, mode): ...
    def mknod(self, path, mode, dev): ...

    def open(self, path, flags):
        """
        When raw_fi is False (default case), open should return a numerical
        file handle.

        When raw_fi is True the signature of open becomes:
            open(self, path, fi)

        and the file handle should be set directly.
        """
        ...

    def opendir(self, path):
        "Returns a numerical file handle."
        ...

    def read(self, path, size, offset, fh):
        "Returns a string containing the data requested."
        ...

    def readdir(self, path, fh):
        """
        Can return either a list of names, or a list of (name, attrs, offset)
        tuples. attrs is a dict as in getattr.
        """
        ...

    def readlink(self, path): ...
    def release(self, path, fh): ...
    def releasedir(self, path, fh): ...
    def removexattr(self, path, name): ...
    def rename(self, old, new): ...
    def rmdir(self, path): ...
    def setxattr(self, path, name, value, options, position=...): ...

    def statfs(self, path):
        """
        Returns a dictionary with keys identical to the statvfs C structure of
        statvfs(3).

        On Mac OS X f_bsize and f_frsize must be a power of 2
        (minimum 512).
        """
        ...

    def symlink(self, target, source):
        "creates a symlink `target -> source` (e.g. ln -s source target)"
        ...

    def truncate(self, path, length, fh=...): ...
    def unlink(self, path): ...

    def utimens(self, path, times=...):
        "Times is a (atime, mtime) tuple. If None use current time."
        ...

    def write(self, path, data, offset, fh): ...


class LoggingMixIn:
    log = ...
    def __call__(self, op, path, *args): ...