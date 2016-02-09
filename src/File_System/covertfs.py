from File_System import memoryfs
import stat
import fs.path
import time, os, datetime

class CovertFile(memoryfs.MemoryFile):

    def __init__(self, path, memory_fs, mem_file, mode, lock):
        super(CovertFile, self).__init__(path, memory_fs, mem_file, mode, lock)

class CovertEntry(memoryfs.DirEntry):

    def __init__(self, type, name, contents=None):
        super(CovertEntry, self).__init__(type, name, contents)
        if type == "dir":
            self.file_mode = stat.S_IFDIR | 0o0755
            self.links = 2
        else:
            self.file_mode = stat.S_IFREG | 0o0666
            self.links = 1
        self.group_id = os.getgid()
        self.user_id = os.getuid()

        #Web-based stuff
        self.downlink = None

        #If FUSE is not being used
        self.current_dir = '/'

class CovertFS(memoryfs.MemoryFS):

    def __init__(self):
        """
        The constructor. Extends the superclass constructor.
        """
        super(CovertFS, self).__init__(file_factory = CovertFile)

        self.dir_entry_factory = CovertEntry
        self.root = self._make_dir_entry('dir', 'root')
        self.current_dir = '/'

    def _datetime(self, time_obj):
        return datetime.datetime.fromtimestamp(time.mktime(time.localtime(time_obj)))

    def _time(self, dt_obj):
        return time.mktime(dt_obj.timetuple())

###################################################################
#               Functions for both FUSE and cmdloop               #
###################################################################

    def settimes(self, path, accessed_time=None, modified_time=None):
        """Sets accessed and modified times of a file or directory after file operations take place"""
        now = time.time()
        if accessed_time is None:
            accessed_time = now
        if modified_time is None:
            modified_time = now

        dir_entry = self._get_dir_entry(path)
        if dir_entry is not None:
            dir_entry.accessed_time = self._datetime(accessed_time)
            dir_entry.modified_time = self._datetime(modified_time)
            return True
        return False

    def setcreate(self, path, timeIn=None):
        """Sets the creation time of a file or directory. Used when the filesystem is loaded from online repository"""
        now = time.time()
        if timeIn==None:
            timeIn=now

        dir_entry = self._get_dir_entry(path)
        if dir_entry is not None:
            dir_entry.created_time = self._datetime(float(timeIn))

    def loadfs(self, fsstring):
        """
        Iterates through a string that represents the filesystem
        (either pulled from online, or given as a test string),
        makes necessary directories, and creates necessary files
        (empty for now) that are then loaded by main.py.
        """
        for fol in fsstring.split("\n")[:-1]:
            foldercontents = fol.split(' ')
            curpath = foldercontents[0]
            if curpath != '/':
                self.makedir(curpath)
            for filestring in foldercontents[1:]:
                fileinfo = filestring.split(',')
                filename = fileinfo[0]
                downlink = fileinfo[1]
                ctime = float(fileinfo[2])
                filepath = curpath + filename
                self.setcontents(filepath, '')
                dir_entry = self._dir_entry(filepath)
                dir_entry.downlink = downlink
                self.setcreate(filepath, timeIn=ctime)

    def save(self):
        """
        Turns the entire filesystem into a string to be uploaded.
        Returns that string.
        """
        save_string = ''
        for directory, files in self.walk():
            save_string += directory
            if directory[-1] != '/':
                save_string += '/'
            for f in files:
                normpath = fs.path.normpath(directory)
                parent_dir = self._get_dir_entry(normpath)
                file_object = parent_dir.contents[f]
                downlink = file_object.downlink
                ctime = self._time(file_object.created_time)
                save_string += ' ' + f + ',' + downlink + ',' + str(ctime)
            save_string += '\n'
        return save_string

###################################################################
#                       Functions for cmdloop                     #
###################################################################

    def sanitize_path(self, path=None):
        """
        This method takes a user-input path and makes it
        method-readable, by adding the current path to the
        front (if the desired path doesn't start with /) or
        returning the root path if no path is given.
        """
        if path == '/':
            return ('/', 'dir')
        elif path is None or path == '.':
            return (self.current_dir, 'dir')
        elif path == '..':
            if self.current_dir == '/':
                return (self.current_dir, 'dir')
            else:
                return (self.current_dir.rsplit('/', 2)[0]+'/', 'dir')
        else:
            if path[0] == '/':
                fullpath = path
            else:
                fullpath = self.current_dir + path
            if self.exists(fullpath):
                if self.isdir(fullpath):
                    return fullpath, 'dir'
                else:
                    return fullpath, 'fil'
            else:
                return fullpath, 'non'

    def ls(self, path=None):
        """
        Returns a list of the files and directories in the given
        path, or the current directory if no path is given.
        Error if given path does not exist, or is a file.
        """
        san_path, node = self.sanitize_path(path)
        if node == 'dir':
            return self.listdir(san_path)
        elif node == 'fil':
            return ("File path given, directory path required")
        else:
            return ("Path given does not exist")

    def cd(self, path='/'):
        """
        Changes current directory. Superclass has no concept of
        current directory (all calls are made from root dir), so
        this method is purely local.
        Error if given path does not exist, or is a file.
        """
        if path == '/':
            self.current_dir = path
            return 1
        else:
            san_path, node = self.sanitize_path(path)
            if san_path[-1] != '/':
                san_path += '/'
            if node == 'dir':
                self.current_dir = san_path
                return 1
            elif node == 'fil':
                return "File path given, directory path required"
            else:
                return "Path given does not exist"

    def mkdir(self, path):
        """
        Makes a new directory at given path.
        Error if path is a directory already, or a file.
        """
        san_path, node = self.sanitize_path(path)
        if san_path[-1] != '/':
            san_path += '/'
        if node == 'dir':
            return ("Directory already exists")
        elif node == 'fil':
            return ("Path is a file. Use another name")
        else:
            self.makedir(san_path, recursive=True)
            return 1

    def rmdir(self, path=None, force=False):
        """
        Removes empty directory at given path, or non-empty
        directory if force option is given.
        Error if path is not a directory.
        """
        san_path, node = self.sanitize_path(path)
        if san_path[-1] != '/':
            san_path += '/'
        if node == 'fil':
            return ("Given path is a file; use rm")
        elif node == 'non':
            print(san_path)
            return ("Given path is not existent")
        else:
            try:
                self.removedir(san_path, force=force)
                return 1
            except:
                return ("Directory is not empty. Use force option to delete")

    def check_parent_dir(self, path):
        """
        Checks to ensure parent directory is present before
        attempting to add a file to it.
        """
        if path.find("/") == -1 or path.count("/") == 1 and path.find("/") == 0:
            return True
        san_path, node = self.sanitize_path(path)
        if self.exists(san_path.rsplit('/', 1)[0] + '/'):
            return True
        return False

    def addfile(self, path, contents):
        """
        Add a file, with given contents, to given path.
        Error if path is a file, directory, or if parent directory
        is not present.
        """
        san_path, node = self.sanitize_path(path)
        if not self.check_parent_dir(path):
            return ("Parent directory does not exist. Use mkdir")
        elif node == 'fil':
            return ("File already exists: file not added")
        elif node == 'dir':
            return ("Given path is a directory; name your file something else")
        else:
            self.setcontents(san_path, data=contents)
            return 1

    def rm(self, path):
        """
        Removes file at given path.
        Error if no such file.
        """
        san_path, node = self.sanitize_path(path)
        if node == 'fil':
            self.remove(san_path)
            return 1
        elif node == 'dir':
            return ("Directory path given, file path required: use rmdir to remove directories")
        else:
            return ("Path given does not exist")
