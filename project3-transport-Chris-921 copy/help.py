# Copyright 2013 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Attempts to give help on other components
"""

from __future__ import print_function
import pox.boot as boot
from pox.lib.util import first_of
import inspect
import sys

def _show_args (f,name):
  #TODO: Refactor with pox.boot

  if name == "launch": name = "default launcher"

  out = []

  EMPTY = "<Unspecified>"

  argnames,varargs,kws,defaults = inspect.getargspec(f)
  argcount = len(argnames)
  defaults = list((f.__defaults__) or [])
  defaults = [EMPTY] * (argcount - len(defaults)) + defaults

  args = {}
  for n, a in enumerate(argnames):
    args[a] = [EMPTY,EMPTY]
    if n < len(defaults):
      args[a][0] = defaults[n]
  multi = False
  if '__INSTANCE__' in args:
    multi = True
    del args['__INSTANCE__']

  if len(args) == 0:
    if argcount or kws:
      out.append(" Multiple.")
      varargs = kws = None
    else:
      out.append(" None.")
  else:
    out.append(" {0:25} {1:25}".format("Name", "Default"))
    out.append(" {0:25} {0:25}".format("-" * 15))

    for k,v in args.items():
      k = k.replace("_","-")
      out.append(" {0:25} {1:25}".format(k,str(v[0])))

  if len(out):
    out.insert(0, "Parameters for {0}:".format(name))
    out.append("")

  if multi:
    out.append(" Note: This can be invoked multiple times.")
  if varargs or kws:
    out.append(" Note: This can be invoked with parameters not listed here.")

  out = '\n'.join(out)

  return out.strip()


def launch (no_args = False, short = False, **kw):
  ...
