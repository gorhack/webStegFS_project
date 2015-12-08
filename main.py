# Modified version of James Thiele (c) 2004 console.py
# Last updated 27 April 2004, downloaded 26 October 2015
# Location: http://www.eskimo.com/~jet/python/examples/cmd/

import os
import cmd
import subprocess
import sys
# import readline
import shlex
from Image_Manipulation import stegByteStream
from Web_Connection.API_Keys import config
from Web_Connection import api_cons
from File_System import fsClass


class Console(cmd.Cmd, object):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.preprompt = "covertFS: "
        self.folder = "/"
        self.prompt = self.preprompt + self.folder + "$ "
        self.intro = "Welcome to Covert File System's command line interface." 
        self.proxy = True

        self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)
        self.fs = fsClass.CovertFilesystem() 
        if len(sys.argv) > 1:  # has URL
            self.loadfs(url=sys.argv[1])
            self.folder = self.fs.current_dir

    # download a file from the url already in the file, from a fs.loadfs
    def down_and_set_file(self, filename):
        """Download a file. Put it in the filesystem."""
        conts = self.fs.getcontents(filename).decode()
        download_url, delete_url = conts.split(',')
        try:
            msg = stegByteStream.Steg(self.proxy).decode(
                self.sendSpace.downloadImage(download_url))
        except:
            print("A file in the system is corrupt, the file is not accessible. \
                File is not longer in FS")
            return False
        self.fs.setcontents(filename, msg+'\r'+download_url+','+delete_url)
        return True

    # Load a file system
    def loadfs(self, url=None):
        """Load the filesystem from a URL: Download pic, decode it, then send the string to the load function in fsClass."""
        if len(url) == 6:  # has short URL
            self.url = "https://www.sendspace.com/file/" + url
        else:  # has long URL
            self.url = url
        try:
            self.fs = fsClass.CovertFilesystem()
            self.fs.loadfs(stegByteStream.Steg(self.proxy).decode(
                self.sendSpace.downloadImage(self.url)))
            for f in self.fs.walkfiles():
                # fs is set up
                # go through and actually download the files
                print("Loading {}......".format(f))
                if not self.down_and_set_file(f):
                    self.rm(f)
            self.folder = self.fs.current_dir
            self.prompt = self.preprompt + self.folder + "$ "
            print("Loaded Covert File System")
        except:
            print("Invalid url given")

    def do_noproxy(self, args):
        """Disable proxy (default enabled)."""
        self.proxy = False
        self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)

    def do_proxy(self, args):
        """Re-enable proxy."""
        self.proxy = True
        self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)

    def do_loadfs(self, url):
        """Load a covert file system.\nUse: loadfs [url]"""
        if url is not None:
            self.loadfs(url)
        else:
            print("Use: loadfs [url]")

    def do_newfs(self, args):
        """Create a covert file system, return the URL of the old fs.\
        \nUse: newfs"""
        print("New file system created. Old file system located at ", end='')
        old_url = self.do_uploadfs(None)
        self.fs = fsClass.CovertFilesystem()
        self.folder = self.fs.current_dir
        self.prompt = self.preprompt + self.folder + "$ "

    def do_encodeimage(self, msg):
        """Encode a message to an image and upload to social media.\
        \nReturns the url.\nUse: encodeimage [message]"""
        try:
            img = stegByteStream.Steg(self.proxy).encode(msg)
            (download_url, delete_url) = self.sendSpace.upload(img)
            img.close()
        except:
            print("Unable to access online resources")
            return
        print("URL: " + download_url)

    def do_decodeimage(self, url):
        """Decode the message in an image.\nReturns the message in plain text.\
        \ndecodeimage [download url]"""
        try:
            msg = stegByteStream.Steg(self.proxy).decode(
                self.sendSpace.downloadImage(url))
            print("Decoded message: " + msg)
        except:
            print("Unable to access online resources, or the given URL is wrong")

    def do_ls(self, args):
            """List items in directory\nUse: ls [path]*"""
            out = None
            if len(args) == 0:
                out = (self.fs.ls())
            else:
                a = args.split()
                if len(a) != 1:
                    out = "Use: ls [path]*"
                    return
                else:
                    out = (self.fs.ls(a[0]))
            if type(out) == list:
                print(out)
            else:
                print(out)

    def do_cd(self, args):
        """Change directory to specified [path]\nUse: cd [path]*"""
        out = None
        if len(args) == 0:
            out = self.fs.cd()
        else:
            out = self.fs.cd(args)
        self.folder = self.fs.current_dir
        self.prompt = self.preprompt + self.folder + "$ "
        if type(out) == str:
            print(out)

    def do_uploadfs(self, args):
        """Upload covert fileSystem to sendspace"""
        return self.do_encodeimage(self.fs.save())

    def uploadfile(self, contents):
        """Helper function to upload file, return the download url."""
        img = stegByteStream.Steg(self.proxy).encode(contents)
        (download_url, delete_url) = self.sendSpace.upload(img)
        img.close()
        contents += '\r' + download_url + ',' + delete_url
        return contents
        

    def addfiletofs(self, path, contents):
        """Helper function to add a file to the fs."""
        upload_contents = self.uploadfile(contents).encode('utf-8')
        return self.fs.addfile(path, upload_contents)

    def do_upload(self, args):
        """Upload a local file to the covert file system.\
        \nUse: upload [local path] [covert path]"""
        out = None
        a = args.split()
        if len(a) > 2 or len(a) < 1:
            print("Use: upload [local path] [covert path]")
            return
        local_path = a[0]
        if len(a) == 1:
            covert_path = a[0]
        else:
            covert_path = a[1]
        try:
            fileCont = subprocess.check_output(
                ["cat " + local_path],
                shell=True
            )
        except:
            print("{} is not in current OS directory".format(local_path))
            return
        try:
            out = self.addfiletofs(covert_path, fileCont.decode())
            if type(out) == str:
                print(out)
        except:
            print("File too large. Working on a system to break up files")

    def san_file(self, file_contents):
        """Sanitize file before 1)viewing contents or 2)putting on host OS"""
        contents = file_contents.decode().rsplit('\r', 1)[0]
        return contents

    def do_download(self, args):
        """Download a covert file to the local file system.\
        \nUse: download [covert path] [local path]"""
        a = args.split()
        if len(a) != 2:  # local path file
            print("Use: download [covert path] [local path]")
            return
        else:
            covert_path = a[0]
            local_path = a[1]
            try:
                subprocess.check_output(
                    ["ls " + local_path.rsplit('/', 1)[0]], 
                    shell=True
                )
            except:
                print("Given directory does not exist")
                return
            try:
                covert_contents = self.fs.getcontents(covert_path)
            except:
                print("Given covert path does not exist")
                return
            with open(local_path, 'w') as f:
                f.write(self.san_file(covert_contents))

        # fs.addFile(local_path, covert_path)

    def do_cat(self, args):
        """View the contents of a file in the fileSystem\
        \nUse: cat [covert path] """
        a = args.split()
        if len(a) != 1:  # local path file
            print("Use: cat [covert path]")
            return
        else:
            covert_path = a[0]
            try:
                covert_contents = self.fs.getcontents(covert_path)
            except:
                print("Given covert path does not exist")
                return
            print(self.san_file(covert_contents))

    def do_rm(self, args):
        """Remove a file from the covert file system.\
        \nUse: rm [path]*"""
        a = args.split()
        if len(a) != 1:
            print("Use: rm [path]")
            return
        out = self.fs.rm(args)
        if type(out) == str:
            print(out)

    def do_mkfile(self, args):
        """Add a text file with a message to the file system.\
        \nUse: mkfile [path] [message]"""
        a = args.split()
        if len(a) < 2:
            print("Use: mkfile [path] [message]")
            return
        try:
            out = self.addfiletofs(a[0], ' '.join(a[1:]))
        except:
            print("File too large. Working on a system to break up files")
            return
        if type(out) == str:
            print(out)

    def do_mkdir(self, args):
        """Make a folder at the given path.\
        \nUse: mkdir [name]"""
        a = args.split()
        if len(a) != 1:
            print("Use: mkdir [name]")
            return
        out = self.fs.mkdir(args)
        if type(out) == str:
            print(out)

    def do_rmdir(self, args):
        """Remove a folder in the current directory.\
        \nUse: rmdir [name]"""
        a = args.split()
        if len(a) != 1 and len(a) != 2:
            print("Use: rmdir [name] [-f]*")
            return
        force = False
        if len(a) == 2 and args[1] == '-f':
            force = True
        out = self.fs.rmdir(a[0], force)
        if type(out) == str:
            print(out)

    # Command definitions ##
    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the console"""
        return -1

    # Command definitions to support Cmd object functionality ##
    def do_EOF(self, args):
        """Exit on system end of file character"""
        return self.do_exit(args)

    def do_shell(self, args):
        """Pass command to a system shell when line begins with '!'"""
        os.system(args)

    def do_help(self, args):
        """Get help on commands
             'help' or '?' with no arguments prints the list of commands
             'help <command>' or '? <command>' gives help on <command>
        """
        # The only reason to define this method
        # is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    # Override methods in Cmd object ##
    def completedefault(self, text, line, begidx, endidx):
        # Allow Tab autocompletion of file names
        return [i for i in self.fs.ls() if i.startswith(text)]
        # TODO:// update ls() to return a List

    def preloop(self):
        """Initialization before prompting user for commands.
             Despite the claims in the Cmd documentaion,
             Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)  # sets up command completion
        self._hist = []  # No history yet
        self._locals = {}  # Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
             Despite the claims in the Cmd documentaion,
             Cmd.postloop() is not a stub.
        """
        cmd.Cmd.postloop(self)  # Clean up command completion
        print("Exiting...")

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.
        """
        self._hist += [line.strip()]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
             If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
             In that case we execute the line as Python code.
        """
        args = self.parser.parse_args(shlex.split(line))
        if hasattr(args, 'func'):
            args.func(args)
        else:
            try:
                cmd.Cmd.default(self, line)
            except:
                print(e.__class__, ":", e)

if __name__ == '__main__':
    Console().cmdloop()
