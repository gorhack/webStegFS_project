#!/usr/bin/env python3

import os
import cmd
import subprocess
import sys
import shlex
import fs
from Image_Manipulation import stegByteStream
from Web_Connection.API_Keys import config
from Web_Connection import api_cons
from File_System import fsClass

"""@package api_cons

Documentation for the api_cons module.
The api_cons module creates an anonymous connection to a given social media
file hosting website and provides connection, uploadImage, and downloadImage
parameters.
"""


class Console(cmd.Cmd, object):
    def __init__(self):
        """
        The Console constructor.
        """
        cmd.Cmd.__init__(self)
        self.api = "sendspace"  # change settings based on the api
        self.version = 0.9

        if self.version == 0.9:  # set basic defaults for version 0.9
            """
            Configure the Console for use with the current version
            """
            # number of characters to encode in each image
            self.max_message_length = 136
            # unique sequence of characters used to determine if another
            # image is decoded in the current image
            self.url_identifier = "URLLIB->"
            self.proxy = False  # use the built-in proxy

        self.preprompt = "covertFS: "
        self.folder = "/"
        self.prompt = self.preprompt + self.folder + "$ "
        self.intro = "Welcome to a Covert File System (v{}).".format(self.version)
        self.proxy = False

        if self.api == "sendspace":  # set defaults for sendspace API
            """
            Configure the Console for use with SendSpace
            """
            self.url_size = 6  # length of download URL returned by sendspace
            self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)
            self.url = None


        self.fs = fsClass.CovertFilesystem()
        if len(sys.argv) > 1:  # has URL parameter
            self.loadfs(url=sys.argv[1])
            self.folder = self.fs.current_dir

    def down_and_set_file(self, filename):
        """Download a file. Put it in the filesystem."""
        filepath, fname = fs.path.pathsplit(filename)
        print(filepath)
        normpath = fs.path.normpath(filepath)
        parent_dir = self._get_dir_entry(normpath)
        file_object = parent_dir.contents[fname]
        downlink = file_object.downlink
        try:
            msg = stegByteStream.Steg(self.proxy).decodeImageFromURL(
                self.sendSpace.downloadImage(downlink))

        except:
            print("A file in the system is corrupt, the file is not accessible. File is not longer in FS")
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
            print('about to load')
            self.fs.loadfs(stegByteStream.Steg(self.proxy).decodeImageFromURL(
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
        """Turns off the built-in proxy.\n
        Use: noproxy"""
        self.proxy = False
        print("Proxy turned off.")
        #self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)

    def do_proxy(self, args):
        """Turns on the built-in proxy.\n
        Use: proxy"""
        print("Proxy turned on.")
        self.proxy = True
        #self.sendSpace = api_cons.SendSpace(config.sendSpaceKey, self.proxy)

    def do_loadfs(self, url):
        """Load a covert file system.\n
        Use: loadfs [url]"""
        if url is not None:
            self.loadfs(url)
        else:
            print("Use: loadfs [url]")

    def do_newfs(self, args):
        """
        Create a covert file system, return the URL of the old fs.\n
        Use: newfs
        """
        print("New file system created. Old file system located at ", end='')
        old_url = self.do_uploadfs(None)
        self.fs = fsClass.CovertFilesystem()
        self.folder = self.fs.current_dir
        self.prompt = self.preprompt + self.folder + "$ "

    def do_encodeimage(self, msg):
        """
        Encode a message to an image and upload to social media.\n
        Returns the url.\n
        Use: encodeimage [message]"""
        if self.test:
            download_url, delete_url = ('foo.url', 'bar.url')
        else:
            count = 0
            # determine how many times we will break up the image
            chunks = [msg[i:i+self.max_message_length] for i in range(0, len(msg), self.max_message_length)]
            total = len(chunks)
            # apend the number of total images for status update
            append_url = ' ' + str(total)
            while (len(chunks) > 0):
                count += 1
                # TODO:// log, not print
                print("encoding image {}/{}".format(count, total))
                try:
                    chunk = chunks.pop()  # encode starting with the last image
                    # encode the image and append the data to the URL
                    img = stegByteStream.Steg(self.proxy).encode(chunk +
                                                                 append_url)
                    # upload the image
                    if self.api == 'sendspace':
                        (download_url, delete_url) = self.sendSpace.upload(img)
                        img.close()  # close the image
                        # set the append url to contain the current image's
                        # download URL. This allows the images to be
                        # downloaded as a linked list.
                        append_url = self.url_identifier + download_url + ' ' + str(total)
                except Exception as e:
                    print("Unable to access online resources " + str(e))
                    return 0
        # print the last images download URL
        print(append_url[:-(len(str(total)) + 1)])
        count = 0
        return 0

    def do_createdownloadlink(self, url):
        """
        Create a direct download link from a url.
        """
        try:
            if self.api == "sendspace":
                print("URL: " + self.sendSpace.downloadImage(url))
            return
        except:
            print("Unable to access online resources")
            return
        print("URL: " + download_url)

    def do_decodeimage(self, url):
        """Decode the message in an image.\n
        Returns the message in plain text.\n
        decodeimage [download url]"""
        msg = ''
        next_url = url
        id_length = len(self.url_identifier) + 6
        count = 0
        total = 0
        try:
            if self.api == 'sendspace':
                msg += stegByteStream.Steg(
                          self.proxy).decodeImageFromURL(
                          self.sendSpace.downloadImage(url))
            # determine how many total images the current image contains
            total = msg[-(len(msg) - (msg.rfind(' ') + 1)):]
            if total == '1':
                # only 1 image total, safe to print message
                print("Decoded message: " + msg[:-2])  # strip ' 1'
                return 0
            len_total = len(total) + 1  # add 1 for space
            offset = id_length + len_total
            while(next_url != "*NO URL*"):  # arbitrary stop decoding
                count += 1  # track current image number to decode
                print("decoding image {}/{}".format(count, str(total)))

                if (msg[-offset:-(6 + len_total)] == self.url_identifier):
                    next_url = msg[-(6 + len_total):-len_total]
                    msg = msg[:-(offset)]
                    if self.api == 'sendspace':
                        msg += stegByteStream.Steg(
                              self.proxy).decodeImageFromURL(
                              self.sendSpace.downloadImage(next_url))
                else:
                    next_url = "*NO URL*"

            print("Decoded message: " + msg[:-len_total])
            return 0
        except Exception as e:
            print("Unable to access online resources, or the given URL is wrong " + str(e))
            return 0

    def do_ls(self, args):
            """List items in directory\n
            Use: ls [path]*"""
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
        """Change directory to specified [path]\n
        Use: cd [path]*"""
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
        """Upload covert fileSystem to the web"""
        if self.api == 'sendspace':
            return self.do_encodeimage(self.fs.save())

    def uploadfile(self, contents):
        """Helper function to upload file, return the download url."""
        img = stegByteStream.Steg(self.proxy).encode(contents)
        (downlink, delete_url) = self.sendSpace.upload(img)
        img.close()
        return contents, downlink
        

    def addfiletofs(self, path, contents):
        """Helper function to add a file to the fs."""
        upload_contents, downlink = self.uploadfile(contents)
        self.fs.addfile(path, upload_contents.encode('utf-8'))
        filepath, fname = fs.path.pathsplit(path)
        normpath = fs.path.normpath(filepath)
        parent_dir = self.fs._get_dir_entry(normpath)
        file_object = parent_dir.contents[fname]
        file_object.downlink = downlink
        parent_dir.contents[fname] = file_object


    def do_upload(self, args):
        """Upload a local file to the covert file system.\n
        Use: upload [local path] [covert path]"""
        out = None
        a = args.split()
        if len(a) > 2 or len(a) < 1:
            print("Use: upload [local path] [covert path]")
            return
        local_path = a[0]
        covert_path = a[0]
        if len(a) > 2:
            covert_path = a[1]
        covert_path, node = self.fs.sanitize_path(covert_path)
        try:
            fileCont = subprocess.check_output(
                ["cat " + local_path],
                shell=True
            )
        except:
            print("{} is not in current OS directory".format(local_path))
            return
        out = self.addfiletofs(covert_path, fileCont.decode())
        try:
            #out = self.addfiletofs(covert_path, fileCont.decode())
            if type(out) == str:
                print(out)
        except:
            print("Parent directory does not exist in covert FS")

    def san_file(self, file_contents):
        """Sanitize file before 1)viewing contents or 2)putting on host OS"""
        contents = file_contents.decode().rsplit('\r', 1)[0]
        return contents

    def do_download(self, args):
        """Download a covert file to the local file system.\n
        Use: download [covert path] [local path]"""
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
        """
        View the contents of a file in the file system.\n
        Use: cat [covert path]
        """
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
        """
        Remove a file from the covert file system.\n
        Use: rm [path]*"""
        a = args.split()
        if len(a) != 1:
            print("Use: rm [path]")
            return
        out = self.fs.rm(args)
        if type(out) == str:
            print(out)

    def do_mkfile(self, args):
        """
        Create a text file with a message to the file system.\n
        Use: mkfile [path] [message]
        """
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
        """Make a folder at the given path.\n
        Use: mkdir [path]"""
        a = args.split()
        if len(a) != 1:
            print("Use: mkdir [name]")
            return
        out = self.fs.mkdir(args)
        if type(out) == str:
            print(out)

    def do_rmdir(self, args):
        """Remove a folder in the current directory.\n
        Use: rmdir [path]"""
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
        """
        Get help on commands
          'help' or '?' with no arguments prints the list of commands
          'help <command>' or '? <command>' gives help on <command>
        """
        # The only reason to define this method
        # is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    # Override methods in Cmd object ##
    def completedefault(self, text, line, begidx, endidx):
        """Allow Tab autocompletion of file names."""
        # TODO:// tmp current directory to walk down path
        return [i for i in self.fs.ls() if i.startswith(text)]

    def preloop(self):
        """
        Initialization before prompting user for commands.
        Despite the claims in the Cmd documentaion,
        Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)  # sets up command completion
        self._hist = []  # No history yet
        self._locals = {}  # Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """
        Take care of any unfinished business.
        Despite the claims in the Cmd documentaion,
        Cmd.postloop() is not a stub.
        """
        cmd.Cmd.postloop(self)  # Clean up command completion
        print("Exiting...")

    def precmd(self, line):
        """
        This method is called after the line has been input but before
        it has been interpreted. If you want to modifdy the input line
        before execution (for example, variable substitution) do it here.
        """
        self._hist += [line.strip()]
        return line

    def postcmd(self, stop, line):
        """
        If you want to stop the console, return something that evaluates to true.
        If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """
        Called on an input line when the command prefix is not recognized.
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
