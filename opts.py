#!/bin/false
# CLI options helper
# Released under the terms of the BSD license, outlined below:

# Copyright (c) 2010, Davyd McColl
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of Davyd McColl nor the names of any other contributors 
#   may be used to endorse or promote products derived from this software 
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys

class Options:
  def __init__(self, usage_header = "", unconsumed_help = ""):
    self.options = dict()
    # put something like "MyApp V1.2.3.4" here
    self.usage_header = usage_header
    # help for trailing arguments which do not have an argument spec, such as an expected URI or filename
    self.unconsumed_help = unconsumed_help
    self.cols = self.get_console_cols()
    self.unconsumed = []

  def get_console_cols(self):
    try:
      if sys.platform == "win32" or sys.platform == "win64":
        # taken from http://code.activestate.com/recipes/440694/
        from ctypes import windll, create_string_buffer
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
          import struct
          (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
          return right-left -1
        else:
          return 78
      elif sys.platform == "posix":
        import struct, fcntl, termios
        s = struct.pack("HHHH", 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack("HHHH", x)[1]
        if width < 80:
          width = 78
        return width -2
      else:
        return 80
    except Exception, e:
      print("Can't determine console columns (" + str(e) + "); defaulting to 80")
      return 78

  def add_opt(self, opt, help = "(no help)", aliases = [], consumes = 0, 
      consumes_help = "", default=None, short_help="", required=False, datatype="string"):
    if consumes == 0 and len(consumes_help) > 0:
      # default consumes value to number of items in the help listing
      consumes = len(consumes_help.split(" " ))
    o = Option(opt, help, aliases, consumes, consumes_help, default, short_help, datatype)
    o.required = required
    self.options[opt] = o

  def _print(self, s, indent = 0):
    words = s.split(" ")
    line = ""
    while (len(words)):
      if len(words[0]) + len(line) > self.cols:
        print((" " * indent) + line)
        line = ""
      if len(line) > 0:
        line += " "
      line += words[0]
      words = words[1:]
    if len(line):
      print((" " * indent) + line)

  def get_max_lhsw(self):
    lhsw = 0
    opts = self.options.keys()
    for o in opts:
      self.options[o].cols = self.cols
      self.options[o].prepare()
      if self.options[o].lhsw > lhsw:
        lhsw = self.options[o].lhsw
    if lhsw > (self.cols / 2):
      lhsw = self.cols / 2
    return lhsw

  def usage(self, long=False):
    # make sure cols are up to date
    self.cols = self.get_console_cols()
    
    if (len(self.usage_header)):
      self._print(self.usage_header)
    tmp = ""
    opts = self.options.keys()
    if len(opts):
      tmp = " {options}"
    self._print("Usage: " + os.path.basename(sys.argv[0]) + tmp + " " + self.unconsumed_help)
    if len(opts):
      self._print("where options are of:", 1)
    opts.sort()
    lhsw = self.get_max_lhsw()

    for o in opts:
      self.options[o].lhsw = lhsw
      self.options[o].usage(long)

    if long:
      self._print("data types:", 1)
      self._print("bool:   yes/no/true/false/1/0", 2)
      self._print("string: any characters", 2)
      self._print("int:    any whole numeric value", 2)
      self._print("float:  any numeric value", 2)
  
  def bool2str(self, b):
    if b:
      return "True"
    else:
      return "False"

  def dump(self):
    opts = self.options.keys()
    opts.sort()
    for o in opts:
      print(o)
      opt = self.options[o]
      print(" required: " + self.bool2str(opt.required))
      print(" selected: " + self.bool2str(opt.selected))
      print(" value:    " + str(opt.value))
      print(" default:  " + str(opt.default))

  def check_type(self, val, opt):
    try:
      if opt.datatype == "string":
        return str(val)
      if opt.datatype == "int":
        return int(val)
      if opt.datatype == "float":
        return float(val)
      if opt.datatype == "bool":
        arg = arg.lower()
        if ["yes", "true", "1"].count(arg) > 0:
          return True
        else:
          return False
    except Exception, e:
      print("Option '" + opt.opt + "' requires an option of type '" + opt.datatype + "'")
      sys.exit(1)
    raise Exception("Unhandled datatype '" + opt.datatype + "' for option '" + opt.opt + "'")


  def parseargs(self):
    # take advantage of python's objects-by-reference schema
    last_consumer = None
    opts = self.options.keys()

    for arg in sys.argv[1:]:
      if arg == "-h":
        self.usage(False)
        sys.exit(0)
      if arg == "--help":
        self.usage(True)
        sys.exit(0)
      if arg == "--":
        last_consumer = None
        continue
      if opts.count(arg) == 0:
        if last_consumer == None:
          self.unconsumed.append(arg)
      else:
        last_consumer = None
      
      if last_consumer == None:
        for o in opts:
          if o == arg:
            last_consumer = self.options[o]
            if not last_consumer.selected:
              last_consumer.selected = True
              if last_consumer.consumes > 1 or last_consumer.consumes < 0:
                last_consumer.value = []
              elif last_consumer.consumes == 1:
                last_consumer.value = ""
              else:
                # this option doesn't consume other args
                last_consumer = None
            break
      else:
        if last_consumer.consumes < 2 and last_consumer.consumes > 0:
          last_consumer.value = self.check_type(arg, last_consumer)
          last_consumer = None
        else:
          last_consumer.value.append(self.check_type(arg, last_consumer))
          if len(last_consumer.value) == last_consumer.consumes:
            last_consumer = None

  def required_missing(self, print_missing = True):
    missing = dict()
    for o in self.options.keys():
      if self.options[o].required and not self.options[o].selected:
        missing[o] = self.options[o]

    missing_opts = missing.keys()
    if len(missing_opts):
      if print_missing:
        missing_opts.sort()
        if len(missing_opts) == 1:
          s = " was"
        else:
          s = "s were"
        print("The following required option" + s + " not supplied:")
        self.cols = self.get_console_cols()
        lhsw = self.get_max_lhsw()
        for o in missing_opts:
          missing[o].lhsw = lhsw
          missing[o].usage(skipaliases=True)
      return True
    return False

  def validate(self, opt):
    opts = self.options.keys()
    if opts.count(opt) == 0:
      raise Exception("Option '" + opt + "' not handled by Options class")

  def value(self, opt):
    self.validate(opt)
    return self.options[opt].value 

  def selected(self, opt):
    self.validate(opt)
    return self.options[opt].selected

class Option:
  def __init__(self, opt, help, aliases, consumes, consumes_help, default, short_help, datatype="string"):
    self.opt = opt
    self.datatype = datatype
    self.consumes = consumes
    self.aliases = aliases
    self.help = help
    self.short_help = short_help
    self.consumes_help = consumes_help
    self.lhsw = 0
    self.rhsw = 0
    self.cols = 0
    self.selected = False
    self.required = False
    self.newline_before_help = False
    self.default = default
    if self.consumes < 2:
      self.value = default
    else:
      self.value = default
    self.indent = 2

  def prepare(self):
    self.lhsw = self.leftw()
    self.sanitise_leftw()

  def sanitise_leftw(self):
    if self.lhsw > (self.cols / 2):
      self.lhsw = 0
      self.newline_before_help = True

  def leftw(self):
    """Returns the minimum colwidth required to display the
        LHS of the help for this option"""
    self.aliases.sort()
    w = len(self.opt) + len(self.consumes_help) + 1
    for a in self.aliases:
      ll = len(a) + len(self.consumes_help) + 1
      if ll > w:
        w = ll
    return w + self.indent + 2

  def pad(self, s, w, padwith = " "):
    while len(s) < w:
      s += padwith
    return s

  def format_rhs(self, s):
    lines = []
    words = s.split(" ")
    current_line = (self.indent * " ") + (" " * self.lhsw) 
    while len(words):
      word = words[0]
      if len(word) + len(current_line) >= self.cols:
        if len(lines) == 0:
          current_line = current_line[self.lhsw + self.indent:]
        lines.append(current_line)
        current_line = (self.indent * " ") + (" " * self.lhsw)
      if len(current_line):
        current_line += " "
      current_line +=  word
      words = words[1:]
    if len(lines) == 0:
      current_line = current_line[self.lhsw + self.indent:]
    if len(current_line.strip()) > 0:
      lines.append(current_line)
    return "\n".join(lines)
    
  def usage(self, long=False, skipaliases=False):
    """Prints out usage for this option"""
    if self.lhsw == 0:
      self.lhsw = self.leftw()
    self.sanitise_leftw()
    if self.cols == 0:
      self.cols = 80
    if self.rhsw == 0:
      self.rhsw = self.cols - self.lhsw
    self.aliases.sort()
    s = self.opt
    if len(self.consumes_help) > 0:
      s += " " + self.consumes_help
    s = self.pad(s, self.lhsw)
    sys.stdout.write((" " * self.indent) + s)
    if not skipaliases:
      for a in self.aliases:
        a = (" " * self.indent) + a
        if len(self.consumes_help):
          a += " " + self.consumes_help
        sys.stdout.write("\n" + self.pad(a, self.lhsw))
    if (self.newline_before_help):
      sys.stdout.write("\n" + (self.lhsw * " "))
    if long or len(self.short_help) == 0:
      sys.stdout.write(self.format_rhs(self.help))
      if long:
        if self.default == None:
          sys.stdout.write(self.format_rhs("default: (none)\n"))
        else:
          sys.stdout.write(self.format_rhs("default: " + self.default + "\n"))
        sys.stdout.write(self.format_rhs("data type: " + self.datatype + "\n"))
    else:
      sys.stdout.write(self.format_rhs(self.short_help))
    sys.stdout.write("\n\n")
    sys.stdout.flush()
    



