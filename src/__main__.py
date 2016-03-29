#!/usr/bin/env python3

"""
`covertFS` is a command line based program created using the `cmd` module.
The `main.py` file contains all commands available and additional helper
functions.
"""

import os, cmd, subprocess, sys, shlex, time, argparse
from src.Image_Manipulation import lsbsteg
from src.Web_Connection.API_Keys import config
from src.Web_Connection import api_cons
from src.File_System import covertfs
from platform import system
from threading import Thread
if system() == 'Linux':
    torEnabled = subprocess.check_output(['ps', 'aux']).decode().find('/usr/bin/tor')
    if torEnabled > -1:
        import socks
        import socket
        print("Using tor, rerouting connection")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket


__version__ = "0.9.3"
__author__ = "Flores, Gorak, Hart, Sjoholm"


class Console(cmd.Cmd, object):
    def __init__(self, online_file_store, steg_class, encrypt_class, mountpoint, url, proxy, cmdLoopUsed, dbg = False):
        """
        The Console constructor.
        """
        cmd.Cmd.__init__(self)
        self.api = online_file_store  # name of API
        self.steg = steg_class      # name of steg class
        self.version = __version__
        self.dbg = dbg
        self.proxy = proxy
        self.cmdloopused = cmdLoopUsed
        self.url = url
        self.fs = covertfs.CovertFS()
        self.encryption = encrypt_class

        ###Information for the command prompt###
        self.preprompt = "covertFS: "
        self.folder = "/"
        self.prompt = self.preprompt + self.folder + "$ "
        self.intro = "Welcome to a Covert File System (v{}).".format(self.version)
        ########################################

        ###Online file store information###
        self.storeFactory = None
        self.storeFactoryClass = None
        self.baseURL = None
        if self.api == "sendspace":  # set defaults for sendspace API
            """
            Configure the Console for use with SendSpace
            """
            self.storeFactoryClass = api_cons.SendSpace
            self.baseURL = "https://www.sendspace.com/file/"
            if self.dbg:
                print("DEBUG: SendSpace loaded as API")

        elif self.api == "somethingelse":  # template for some other api
            print ("Invalid file store")
            return
        ###################################

        ###Steganography class setup###
        self.stegFactory = None
        if self.steg == "LSBsteg":
            self.stegFactoryClass = lsbsteg.Steg
            if self.dbg:
                print("DEBUG: LSBsteg loaded as steg")

        elif self.steg == "somethingelse": #template for some other steg class
            pass
        ###############################

        def inputxorKey():
            tempKey = input("Passcode? ")
            try:
                tempKey = int(tempKey)
                assert (tempKey)>-1 and (tempKey)<256
            except:
                print("Ensure passcode is an integer between 0 and 255.")
                return
            self.encryptKey = tempKey

        ###Encryption class setup###
        self.encryptClass = None
        self.encryptKey = None
        if self.encryption == 'xor':
            from Encryption import xor
            self.encryptClass = xor.XOR()
            while self.encryptKey == None:
                inputxorKey()
            if self.dbg:
                print("DEBUG: Encryption enabled, with xor set as the encryption class")

        elif self.encryption == "somethingelse": #template for some other encryption class
            pass
        #################################

        ###FUSE usability information###
        self.fuse_enabled = False
        try:
            if subprocess.call(['whereis','fusermount'], stdout = subprocess.DEVNULL) == 0:
                self.fuse_enabled = True
                self.mounted = False
                self.mp = mountpoint
                self.fuseFS = None
                if self.dbg:
                    print("DEBUG: FUSE enabled, with mountpoint set as ",self.mp)
        except:
            if self.dbg:
                print("DEBUG: FUSE not enabled")
            pass  # preventing the program from attempting to run on Windows or other monstrosities without FUSE
        ###############################

        self.init_factory()

    def init_factory(self):
        self.storeFactory = self.storeFactoryClass(self.proxy)
        self.stegFactory = self.stegFactoryClass(self.proxy, self.storeFactory)
        if self.dbg:
            print("DEBUG: Steg and API factories re-initialized")

    def down_and_set_file(self, filename):
        """Download a file. Put it in the filesystem."""
        downlink = self.fs._get_dir_entry(filename).downlink
        if self.dbg:
            print("DEBUG: Downlink found in file attributes: ",downlink)
        try:
            msg = self.download_file(downlink)
            if self.dbg:
                print("DEBUG: File fully decoded from URL")
        except:
            out = "File named '"+ filename+"'was not decoded correctly. It is no longer in the filesystem. To attempt to retry this operation, execute command 'downloadFile "+ downlink+"'."
            if self.dbg:
                print("ERROR: "+ out)
            else:
                print(out)
            return False
        self.fs.setcontents(filename, msg)
        if self.dbg:
            print("DEBUG: File '", filename,"' decoded correctly, stored in filesystem.")
        return True

###Fuse/ Mounting elements###
    def background_upload(self):
        while self.mounted:
            time.sleep(1)
            for f in self.fs.walkfiles():
                entry = self.fs._dir_entry(f)
                if entry.downlink is None and f.rsplit('.')[-1] != 'swp':
                    print("STATUS: Uploading ", f)
                    entry.downlink = self.upload_file(bytearray(self.fs.getcontents(f)))

    def open_window(self):
        time.sleep(1)
        if system() == 'Linux':
            try:
                subprocess.call(['gnome-terminal', '--working-directory=' + os.getcwd()+ '/'+ self.mp, '--window'])
                if self.dbg:
                    print("DEBUG: New window opened, with the mounted FS as the cwd.")
            except:
                print("DEBUG: gnome-terminal not on this system")

    def do_mount(self, args):
        if self.dbg:
            print("DEBUG: Mount called")
        if self.fuse_enabled is False:
            print("ERROR: Only able to mount on systems with fuse installed")
            return
        from .File_System import memfuse
        self.fuseFS = memfuse.MemFS(self.fs)
        if self.dbg:
            print("DEBUG: MemFS has been created")
        newDir = False
        if not os.path.exists(self.mp):
            os.makedirs(self.mp)
            newDir = True
        if self.dbg:
            print("DEBUG: Mountpoint has been prepared")
        window = Thread(target=self.open_window)
        monitor = Thread(target=self.background_upload)
        window.start()
        if self.dbg:
            print("DEBUG: Window opened, about to mount")
        self.mounted=True
        monitor.start()
        memfuse.mount(self.fuseFS, self.mp)
        self.mounted=False
        if newDir:
            os.rmdir(self.mp)
        if not self.cmdloopused:
            print("STATUS: Uploading all files to online")
            self.do_uploadfs(self)
#############################

###Proxy stuff###
    def do_noproxy(self, args):
        """Turns off the built-in proxy.\n
        Use: noproxy"""
        self.proxy = None
        print("STATUS: Proxy turned off.")
        self.init_factory()

    def do_proxy(self, args):
        """Turns on the built-in proxy.\n
        Use: proxy"""
        print("STATUS: Proxy turned on.")
        self.proxy = default_proxies
        self.init_factory()
#################

###File system operations###
    def loadfs(self):
        try:
            self.fs = covertfs.CovertFS()
            if self.dbg:
                print("DEBUG: New, empty filesystem initiated.")
            fs_string = self.download_file(self.url).decode()
            if self.dbg:
                print("DEBUG: Filesystem metadata decoded: ")
                print(fs_string[12:-1])
            if not fs_string[0:10] == 'filesystem':
                print("ERROR: no files in this file system. You more than likely have the wrong passcode")
            self.fs.loadfs(fs_string)
            if self.dbg:
                print("DEBUG: New filesystem loaded.")
            for f in self.fs.walkfiles():
                print("Loading {}......".format(f))
                if not self.down_and_set_file(f):
                    self.do_rm(f)
                    if self.dbg:
                        print("DEBUG: File named '",f,"' was successfully removed from the filesystem.")
            self.folder = self.fs.current_dir
            self.prompt = self.preprompt + self.folder + "$ "
            print("Loaded Covert File System")
        except:
            print("Filesystem load was not successful. This could be because of a bad filesystem image URL, or connection problems.")#TODO: mid-program connection testing

    def do_loadfs(self, url):
        """Load a covert file system.\n
        Use: loadfs [url]"""
        if url is not None:
            self.url = url
            if self.dbg:
                print("DEBUG: Loading a file system from url")
            self.loadfs()
        else:
            print("Use: loadfs [url]")

    def do_newfs(self, args):
        """
        Create a covert file system, return the URL of the old fs.\n
        Use: newfs
        """
        print("STATUS: New file system created. Old file system located at ", end='')
        old_url = self.do_uploadfs(None)
        self.fs = covertfs.CovertFS()
        self.folder = self.fs.current_dir
        self.prompt = self.preprompt + self.folder + "$ "

    def do_uploadfs(self, args):
        """Upload covert fileSystem to the web"""
        if self.dbg:
            print("DEBUG: About to walk through files")
        for f in self.fs.walkfiles():
            entry = self.fs._dir_entry(f)
            if entry.downlink is None:
                print("STATUS: Uploading ", f)
                entry.downlink = self.upload_file(bytearray(self.fs.getcontents(f)))
        if self.dbg:
            print("DEBUG: All files uploaded, uploading fs_string")
        print("File system at: ", self.upload_file(bytearray(self.fs.save().encode('utf-8'))))
############################

###File upload downloads###

    def do_encodemsg(self, message):
        """
        Encode a message and upload to social media.\n
        Returns the url.\n
        Use: encodemsg [message]"""
        my_msg = bytearray(message.encode())
        if self.dbg:
            print("DEBUG: About to upload encoded message")
        self.upload_file(my_msg)

    def do_decodemsg(self, in_url):
        """Decode the message in an image.\n
        Returns the message in plain text.\n
        decodeimage [download url]"""
        url = self.baseURL + in_url if len(in_url) == 6 else in_url
        if self.dbg:
            print("DEBUG: Url obtained ({}), about to download, decode, and print".format(url))
        msg = self.download_file(url)

        print(msg.decode())

    def download_file(self, url):
        print("downloading...")
        msg = self.stegFactory.decodeImageFromURL(url)
        print("download success!")
        if self.dbg:
            print("DEBUG: Contents downloaded")
        if self.encryptClass:
            msg = self.encryptClass.decrypt(self.encryptKey, msg)
            if self.dbg:
                print("DEBUG: Contents decrypted")
        return msg

    def upload_file(self, contents):
        """Helper function to upload file, return the download url."""
        if self.dbg:
            print("DEBUG: Sending data to steg factory for encoding")
        if self.encryptClass:
            contents = self.encryptClass.encrypt(self.encryptKey, contents)
            if self.dbg:
                print("DEBUG: Contents encrypted. About to upload")
        url = self.stegFactory.encode(contents)
        if self.dbg:
            print("DEBUG: URL of uploaded file: ", url)
        return url

    def add_file_to_fs(self, fspath, contents):
        """Helper function to add a file to the fs."""
        print("STATUS: Uploading ", fspath)
        contents_bytes = bytearray(contents.encode())
        downlink = self.upload_file(contents_bytes.copy())
        if self.dbg:
            print("DEBUG: Adding file to file system")
        self.fs.addfile(fspath, contents_bytes)
        entry = self.fs._dir_entry(self.fs.current_dir+fspath)
        entry.downlink = downlink

    def do_mkfile(self, args):
        """
        Create a text file with a message to the file system.\n
        Use: mkfile [path] [message]
        """
        a = args.split()
        if len(a) < 2:
            print("Use: mkfile [path] [message]")
            return
        upload = Thread(target=self.add_file_to_fs, args = [a[0], ' '.join(a[1:])])
        upload.start()

    def san_file(self, file_contents):
        """Sanitize file before 1)viewing contents or 2)putting on host OS"""
        contents = file_contents.decode()
        if self.dbg:
            print("DEBUG: File sanitized")
        return contents



###Direct file manipulations within file system###
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
        upload = Thread(target=self.add_file_to_fs, args = [covert_path, fileCont.decode()])
        upload.start()

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
                covert_contents = self.fs.getcontents(self.fs.current_dir + covert_path)
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
##################################################

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
        print('Command "' + line + '" not recognized')
        # args = self.parser.parse_args(shlex.split(line))
        # if hasattr(args, 'func'):
        #    args.func(args)
        # else:
        #    try:
        #        cmd.Cmd.default(self, line)
        #    except:
        #        print(e.__class__, ":", e)

default_proxies = {'https': 'https://165.139.149.169:3128',
                   'http': 'http://165.139.149.169:3128'}


def proxy_test(proxyL):
    import requests
    try:
        r = requests.get('http://google.com', timeout=5)
        assert(r.status_code is 200)
    except:
        print("Not connected to Internet! Defeats purpose of the whole web-based thing...")
        return
    # now test proxy functionality
    try:
        # Add something in here later to actually test proxy with given file store. Use google for now.
        r = requests.get('http://www.sendspace.com', proxies=proxyL, timeout=5)
        print(r)
        assert(r.status_code == 200)
    except:
        print("Given (or default) proxy is down, or took too long to be useful")
        return
    else:
        print("Proxy is operational")
        return proxyL


def proxy_parser(proxyString=None):
    if proxyString is None:
        return proxy_test(default_proxies)
    proxy = proxyString.split(':')[0]
    port = proxyString.split(':')[1]
    import ipaddress
    try:
        print(ipaddress.ip_address(proxy))
        assert(int(port) > 0 & int(port) < 65536)
    except:
        print("Invalid ip address for proxy. Enter the proxy again.")
        return
    proxDict = {'https': 'https'+proxy+':'+port,
                'http': 'http'+proxy+':'+port}
    return proxDict#proxy_test(proxDict)

def main():
    parser = argparse.ArgumentParser(description="Calls the main function of CovertFS")
    parser.add_argument('url', type=str, default='', nargs='?',
                        help='Specify the url to load a filesystem from')
    parser.add_argument('-c', dest='cmdloop', default=False, action='store_true',
                        help='Use the command loop to access the filesystem')
    parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Enable debug print statements. For dev use')
    parser.add_argument('-w', dest='website', type=str, default='sendspace',
                        help='Use alternate online file stores from command line')
    parser.add_argument('-p', dest="proxy", type=str, default='noproxy', nargs='?',
                        help='Use a specific proxy to access the web file store. \
                        There is a default if none provided. \
                        Format is simply an ip address with port at the end (e.x. 1.2.3.4:8080)')
    parser.add_argument('-e', dest='encryption', type=str, default='noencrypt', nargs='?',
                        help='Use a specific encryption. To be extended later')
    parser.add_argument('-m', dest="mountpoint", type=str, default='covertMount',
                        help='Specify a foldername to mount the FUSE module at')
    parser.add_argument('-s', dest='steganography', default='LSBsteg', nargs='?',
                        help='Use an alternate steganography class for encoding in images')

    args = parser.parse_args()
    print(args)

    run = True
    if args.proxy == 'noproxy':
        proxy = None
    else:
        proxy = proxy_parser(args.proxy)
        if proxy is None:
            run = False

    if args.encryption == 'noencrypt':
        encrypt = None
    else:
        if args.encryption == None:
            args.encryption = 'xor'  # xor is the default encryption class. In the absence of an argument for -e, xor is used.
        encrypt = args.encryption

    if run:
        cons = Console(args.website, args.steganography, encrypt, args.mountpoint, args.url, proxy, args.cmdloop, args.debug)

        if args.url:
            cons.loadfs()
        if args.cmdloop:
            cons.cmdloop()
        else:
            cons.do_mount(None)
