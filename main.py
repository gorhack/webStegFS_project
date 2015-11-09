# start with command line interface
# cmd-support for line-oriented command interpreters: https://docs.python.org/2/library/cmd.html
# http://stackoverflow.com/questions/17352630/creating-a-terminal-program-with-python
# https://pymotw.com/2/cmd/

## console.py
## Author:   James Thiele
## Date:     27 April 2004
## Version:  1.0
## Location: http://www.eskimo.com/~jet/python/examples/cmd/
## Copyright (c) 2004, James Thiele

import os
import cmd
import readline
import argparse
import shlex
from Image_Manipulation import stegByteStream
from Web_Connection.API_Keys import config
from Web_Connection import api_cons
import fsClass

class Console(cmd.Cmd):

  def __init__(self):
    self.url = args.url # url to the file system. TODO:// Decode 
    cmd.Cmd.__init__(self)
    self.prompt = "covertFS$ "
    self.intro  = "Welcome to Covert File System's command line interface."  ## defaults to None

    fs = fsClass.fileSystem("root/ root/alpha.txt,a.url,aDel.url root/bravo.txt,b.url,bDel.url")
    print(fs.loadFS('test'))
    self.fs = fs
    self.sendSpace = api_cons.SendSpace(config.sendSpaceKey)
    self.steg = stegByteStream.Steg()
    # tmp/

  def do_encodeImage(self, msg):
    self.steg.encode(msg)
    (download_url,delete_url) = self.sendSpace.upload()
    print("URL: " + download_url)

  def do_decodeImage(self, url):
    self.steg.assignImage(url)
    msg = self.steg.decode()
    print("Decoded message: " + msg)

  def do_ls(self, args):
    """List items in directory"""
    print(self.fs.ls()) #TODO:// ls [path]

  def do_cd(self, args):
    """Change directory to specified [path]\nUse: cd [path]*"""
    self.fs.cd(args)

  def do_addFile(self, args):
    """addFile in Development.\nAdd a local file to the covert file system.\nUse: addFile [local path] [covert path]"""
    a = args.split()
    local_path = ''
    covert_path = ''
    if len(a)==1: #local path file
      local_path = a[0]
    elif len(a)==2:
      local_path=a[0]
      covert_path=a[1]
    else:
      print('*** invalid number of arguments\naddFile [local path] [covert path]*')
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

  def do_addMessage(self, args):
    """addMessage in Development.\nAdd a text file with a message to the file system.\nUse: addMessage [name] [message] [path]*"""
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
      print('*** invalid number of arguments\naddMessage [name] [message] [path]*')
      return
    print("Command not implemented")

  def do_mkdir(self, args):
    """mkdir in Development.\nMake a folder in the current directory.\nUse: mkdir [name]"""
    print("Command not implemented")
    #self.fs.mkdir(args)

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
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--url', required=True,  default='', help='URL to folder')
  args = parser.parse_args()
  console = Console()
  console.cmdloop()
