#!/usr/bin/env python3

"""
The `memfuse` module extends the `pyfuse` package, specifically the
`Operations` module.
'Operations' is linked to the Unix FUSE package with python ctypes, to make the
file system available to the user, without making system calls. The memfuse
module extends all necessary file system operations in a way that is accessible
by FUSE, effectively linking the CovertFS class to the FUSE package. When
mounted (using FUSE) onto the native Linux file system, memfuse provides access
to all files and directories in the CovertFS file system.
"""

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
import time, datetime
from .fs import path

from .fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

ST_DICT = dict(st_mode=0, st_nlink=0,
                    st_uid=0, st_gid=0,
                    st_size=0, st_atime=0,
                    st_mtime=0, st_ctime=0)


class MemFS(LoggingMixIn, Operations):
    """Subclass of operations. Links all necessary filesystem operations to CovertFS"""
    def __init__(self, memoryfs):
        """Constructor class. Sets the fs as the input memoryfs, so it can be retrieved later."""
        self.fs = memoryfs
        self.fd_map = []

    def _time(self, dt_obj):
        """Make a datetime object into a time float"""
        return time.mktime(dt_obj.timetuple())

    def _dir_size(self, dir_entry):
        """Helper function for getattr, returns the sum of all the file sizes in a directory"""
        size = 0
        for entry in dir_entry.contents.values():
            if entry.isfile():
                size += len(entry.data)
            else:
                size += self._dir_size(entry)
        return size

    def getattr(self, path, fh=None):
        """Function used extensively by the OS package FUSE for interaction with system calls"""
        if not (self.fs.exists(path)):
            raise FuseOSError(ENOENT)
        mem_file = self.fs._dir_entry(path)
        ent_att = mem_file.__dict__
        if mem_file.isfile():
            size = len(mem_file.data)
        else:
            size = self._dir_size(mem_file)

        return dict(st_mode=int(ent_att['file_mode']), st_nlink=ent_att['links'],
                    st_uid=ent_att['user_id'], st_gid=ent_att['group_id'],
                    st_size=size, st_atime=self._time(ent_att['accessed_time']),
                    st_mtime=self._time(ent_att['modified_time']), st_ctime=self._time(ent_att['created_time']))

    def mkdir(self, path, mode):
        """Make a directory in mounted filesystem"""
        self.fs.makedir(path)

    def rename(self, old, new):
        """Rename a file or directory in a mounted filesystem"""
        self.fs.rename(old, new)

    def readdir(self, path, fh):
        """Same as listing the contents of a directory"""
        return self.fs.listdir(path)

    def read(self, path, size, offset, fh):
        """Reads the contents of a file and returns the requested number of bytes"""
        self.utimens(path, (None, self.getattr(path)['st_mtime']))
        return self.fs.getcontents(path)[offset:offset + size -1] + b'\n'

    def rmdir(self, path):
        """Removes a directory from mounted filesystem"""
        self.fs.removedir(path)

    def utimens(self, path, times=None):
        """Changes the modified and access times of a file in the mounted filesystem"""
        #print("utimens on "+ path)
        if times == None:
            self.fs.settimes(path)
        else:
            self.fs.settimes(path, accessed_time=times[0], modified_time=times[1])

    def create(self, path, mode):
        """Makes a new file in mounted filesystem"""
        self.fs.setcontents(path)
        self.setxattr(path, "security.selinux", "", None)
        self.fd_map.append(path)
        return len(self.fd_map)-1

    def open(self, path, flags):
        """Opens the file at a given path in mounted filesystem"""
        if not self.fs.exists(path):
            raise FuseOSError(ENOENT)
        self.fd_map.append(path)
        self.utimens(path, (None, self.getattr(path)['st_mtime']))
        return len(self.fd_map)-1

    def write(self, path, data, offset, fh):
        """Writes the provided data to a file in the mounted filesystem"""
        in_data = self.fs.getcontents(path)
        self.fs.setcontents(path, data=in_data[:offset]+data)
        self.utimens(path)
        entry = self.fs._dir_entry(path)
        entry.downlink = None
        return len(data)

    def unlink(self, path):
        """Removes a file from the mounted filesystem"""
        self.fs.remove(path)

    def getxattr(self, path, name, position=0):
        """Returns an additional attribute of a file (such as SELinux information)"""
        if name in self.fs._dir_entry(path).xattrs:
            return self.fs.getxattr(path,name)
        return b'No such xattr'

    def listxattr(self, path):
        """Lists extra attributes of a file"""
        return self.fs.listxattrs(path)

    def setxattr(self, path, name, value, options, position=0):
        """Sets the extra attribute to given value"""
        self.fs.setxattr(path,name,value)

    def removexattr(self, path, name):
        """Removes the extra attribute from file"""
        self.fs.delxattr(path, name)

    def truncate(self, path, length, fh=None):
        """Shortens the size of a file by a certain amount"""
        in_data = self.fs.getcontents(path)
        if (len(in_data)> length & length>-1):
            self.fs.setcontents(path, data= in_data[:length])
        return len(in_data[:length])

    def flush(self, path, fh):
        """Writes all attributes and extra attributes of a file after it is done being accessed"""
        #print("flush called on "+ path)
        entry = self.fs._dir_entry(path)
        fi = entry.mem_file
        return fi.flush()

    def fsync(self, path, fdatasync, fh):
        """Same as flush"""
        #print("fsync called on "+ path)
        return self.flush(path,fh)

    #def release(self, path, fh):
    #    entry = self.fs._dir_entry(path)
    #    fi = entry.mem_file
    #    return fi.close()

def mount(memfs, mountpoint, db=False):
    """Actually mounts the given memoryfs onto the given mountpoint"""
    fuse = FUSE(memfs, mountpoint, foreground=True, debug=db)