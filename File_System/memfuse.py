#!/usr/bin/env python

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
import time, datetime
import fs.path

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

ST_DICT = dict(st_mode=0, st_nlink=0,
                    st_uid=0, st_gid=0,
                    st_size=0, st_atime=0,
                    st_mtime=0, st_ctime=0)


class MemFS(LoggingMixIn, Operations):

    def __init__(self, memoryfs):

        self.fs = memoryfs
        self.fd_map = []

    def _time(self, dt_obj):
        return time.mktime(dt_obj.timetuple())

    def _dir_size(self, dir_entry):
        size = 0
        for entry in dir_entry.contents.values():
            if entry.isfile():
                size += len(entry.data)
            else:
                size += self._dir_size(entry)
        return size

    def getattr(self, path, fh=None):
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
        self.fs.makedir(path)

    def rename(self, old, new):
        self.fs.rename(old, new)

    def readdir(self, path, fh):
        return self.fs.listdir(path)

    def read(self, path, size, offset, fh):
        self.utimens(path, (None, self.getattr(path)['st_mtime']))
        return self.fs.getcontents(path)[offset:offset + size]

    def rmdir(self, path):
        self.fs.removedir(path)

    def utimens(self, path, times=None):
        #print("utimens on "+ path)
        if times == None:
            self.fs.settimes(path)
        else:
            self.fs.settimes(path, accessed_time=times[0], modified_time=times[1])

    def create(self, path, mode):
        self.fs.setcontents(path)
        self.setxattr(path, "security.selinux", "", None)
        self.fd_map.append(path)
        return len(self.fd_map)-1

    def open(self, path, flags):
        if not self.fs.exists(path):
            raise FuseOSError(ENOENT)
        self.fd_map.append(path)
        self.utimens(path, (None, self.getattr(path)['st_mtime']))
        return len(self.fd_map)-1

    def write(self, path, data, offset, fh):
        in_data = self.fs.getcontents(path)
        self.fs.setcontents(path, data=in_data[:offset]+data)
        self.utimens(path)
        entry = self.fs._dir_entry(path)
        entry.downlink = None
        return len(in_data[:offset]+data)

    def unlink(self, path):
        self.fs.remove(path)

    def getxattr(self, path, name, position=0):
        if name in self.fs._dir_entry(path).xattrs:
            return self.fs.getxattr(path,name)
        return b'No such xattr'

    def listxattr(self, path):
        return self.fs.listxattrs(path)

    def setxattr(self, path, name, value, options, position=0):
        self.fs.setxattr(path,name,value)

    def removexattr(self, path, name):
        self.fs.delxattr(path, name)

    def truncate(self, path, length, fh=None):
        in_data = self.fs.getcontents(path)
        if (len(in_data)> length & length>-1):
            self.fs.setcontents(path, data= in_data[:length])
        return len(in_data[:length])

    def flush(self, path, fh):
        #print("flush called on "+ path)
        entry = self.fs._dir_entry(path)
        fi = entry.mem_file
        return fi.flush()

    def fsync(self, path, fdatasync, fh):
        #print("fsync called on "+ path)
        return self.flush(path,fh)

    #def release(self, path, fh):
    #    entry = self.fs._dir_entry(path)
    #    fi = entry.mem_file
    #    return fi.close()

def mount(memfs, mountpoint, db=False):

    fuse = FUSE(memfs, mountpoint, foreground=True, debug=db)