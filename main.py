## Modified version of James Thiele (c) 2004 console.py
## Last updated 27 April 2004, downloaded 26 October 2015
## Location: http://www.eskimo.com/~jet/python/examples/cmd/

import os
import cmd
import subprocess
import sys
import readline
import shlex
from Image_Manipulation import stegByteStream
from Web_Connection.API_Keys import config
from Web_Connection import api_cons
import fsClass

class Console(cmd.Cmd, object):

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.prompt = "covertFS$ "
    self.intro  = "Welcome to Covert File System's command line interface." 

    self.sendSpace = api_cons.SendSpace(config.sendSpaceKey)
    self.fs = None
    if len(sys.argv) > 1: # has URL
      self.loadfs(sys.argv[1])
    else: # no URL
      self.loadfs("")
  
  ### Load a file system
  def loadfs(self, url):
    if len(url) == 0:
      fs = fsClass.fileSystem('')
      self.fs = fs.newFS()
      print("Creating new File System...to load a covert File System: loadfs [url]\n")
    else:
      if len(url) == 6: # has short URL
        self.url = "https://www.sendspace.com/file/" + url
      else: # has long URL
        self.url = url
      self.fs = fsClass.fileSystem(stegByteStream.Steg().decode(self.sendSpace.downloadImage(self.url)))
      self.fs.loadFS()
      print("Loaded Covert File System\n")
  
  def do_loadfs(self, url):
    """Load a covert file system.\nUse: loadfs [url]"""
    self.loadfs(url)

  def do_encodeimage(self, msg):
    """Encode a message to an image and upload to social media.\nReturns the url.\nUse: encodeimage [message]"""
    img = stegByteStream.Steg().encode(msg)
    (download_url,delete_url) = self.sendSpace.upload(img)
    img.close()
    print("URL: " + download_url)

  def do_createdownloadlink(self, url):
    print("URL: " + self.sendSpace.downloadImage(url))

  def do_decodeimage(self, url):
    """Decode the message in an image.\nReturns the message in plain text.\ndecodeimage [direct download url]"""
    msg = stegByteStream.Steg().decode(self.sendSpace.downloadImage(url))
    print("Decoded message: " + msg)

  def do_ls(self, args):
    """List items in directory"""
    print(self.fs.ls()) #TODO:// ls [path]

  def do_cd(self, args):
    """Change directory to specified [path]\nUse: cd [path]*"""
    self.fs.cd(args)

  def do_uploadfs(self, args):
    """Upload covert fileSystem to sendspace"""
    self.do_encodeimage(self.fs.writeFS())

  def do_upload(self, args):
    """upload in Development.\nUpload a local file to the covert file system.\nUse: upload [local path] [covert path]"""
    a = args.split()
    local_path = ''
    covert_path = ''
    if len(a)==1: #local path file
      local_path = a[0]
      covert_path=a[0]
    elif len(a)==2:
      local_path=a[0]
      covert_path=a[1]
    else:
      print('*** invalid number of arguments\nupload [local path] [covert path]*')
      return
    try:
      fileCont = subprocess.check_output(["type", (local_path)],shell=True).decode('ascii')[:-1]
    except:
      print ("{} is not in current OS directory".format(local_path))
      return
    img = stegByteStream.Steg().encode(fileCont)
    (download_url,delete_url) = self.sendSpace.upload(img)
    img.close()
    print(self.fs.addFile(covert_path, download_url, delete_url))

    #print("Command not implemented")
    #fs.addFile(local_path, covert_path)

  def do_download(self, args):
    """download in Development.\nDownload a covert file to the local file system.\nUse: download [covert path] [local path]"""
    print(args)
    a = args.split()
    local_path = ''
    covert_path = ''
    if len(a)==1: #local path file
      local_path = a[0]
    elif len(a)==2:
      local_path=a[0]
      covert_path=a[1]
    else:
      print('*** invalid number of arguments\ndownload [covert path] [local path]*')
      return

    print("Command not implemented")
    #fs.addFile(local_path, covert_path)

  def do_rm(self, args):
    """rm in Development.\nRemove a file from the covert file system.\nUse: rm [path]*"""
    path = ''
    a = args.split()
    if len(a)==0:
      path=''
    elif len(a)==1:
      path = a[0]
    else:
      print('*** invalid number of arguments\nrm [path]*')
      return 
    print("Command not implemented")
    #self.fs.rm(path)

  def do_mkfile(self, args):
    """mkfile in Development.\nAdd a text file with a message to the file system.\nUse: mkfile [name] [message] [path]*"""
    name = ''
    message = ''
    path = ''
    a = args.split()
    if len(a)==2:
      name=a[0]
      message=a[1]
    elif len(a)==3:
      name=a[0]
      message=a[1]
      path=a[2]
    else:
      print('*** invalid number of arguments\nmkfile [name] [message] [path]*')
      return
    print("Command not implemented")

  def do_mkdir(self, dirname):
    """mkdir in Development.\nMake a folder in the current directory.\nUse: mkdir [name]"""
    self.fs.mkdir(dirname)

  def do_rmdir(self, args):
    """rmdir in Development.\nRemove a folder in the current directory.\nUse: rmdir [name]"""
    print("Command not implemented")
    #self.fs.rmdir(args)

  def do_save(self, args):
    """save in Development.\nSave covert file to local storage.\nUse: save [covert path] [local path]"""
    print("Command not implemented")

  ## Command definitions ##
  def do_hist(self, args):
    """Print a list of commands that have been entered"""
    print(self._hist)

  def do_exit(self, args):
    """Exits from the console"""
    return -1

  ## Command definitions to support Cmd object functionality ##
  def do_EOF(self, args):
    """Exit on system end of file character"""
    return self.do_exit(args)

  def do_shell(self, args):
    """Pass command to a system shell when line begins with '!'"""
    os.system(args)

  def do_help(self, args):
    """Get help on commands
       'help' or '?' with no arguments prints a list of commands for which help is available
       'help <command>' or '? <command>' gives help on <command>
    """
    ## The only reason to define this method is for the help text in the doc string
    cmd.Cmd.do_help(self, args)

  ## Override methods in Cmd object ##
  def completedefault(self, text, line, begidx, endidx):
    # Allow Tab autocompletion of file names
    return [i for i in self.fs.ls() if i.startswith(text)] # TODO:// update ls() to return a List

  def preloop(self):
    """Initialization before prompting user for commands.
       Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
    """
    cmd.Cmd.preloop(self)   ## sets up command completion
    self._hist    = []      ## No history yet
    self._locals  = {}      ## Initialize execution namespace for user
    self._globals = {}

  def postloop(self):
    """Take care of any unfinished business.
       Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
    """
    cmd.Cmd.postloop(self)   ## Clean up command completion
    print("Exiting...")

  def precmd(self, line):
    """ This method is called after the line has been input but before
        it has been interpreted. If you want to modifdy the input line
        before execution (for example, variable substitution) do it here.
    """
    self._hist += [ line.strip() ]
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
        print(e.__class__,":",e)

if __name__ == '__main__':
  Console().cmdloop()
