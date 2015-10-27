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
from Image_Manipulation import lsbsteg
from Web_Connection import *

class Console(cmd.Cmd):

  def __init__(self):
    self.url = args.url
    cmd.Cmd.__init__(self)
    self.prompt = "covertFS$ "
    self.intro  = "Welcome to Covert File System's command line interface."  ## defaults to None

    self.parser = argparse.ArgumentParser()
    
    ###
    ### Creating commands with arguments example 
    ### http://stackoverflow.com/questions/12750393/python-using-argparse-with-cmd
    ###
    subparsers = self.parser.add_subparsers()
    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--foo", default="Hello")
    test_parser.add_argument("--bar", default="World")
    test_parser.set_defaults(func=self._do_test)

  def _do_test(self,args):
    print(args.foo, args.bar)

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
