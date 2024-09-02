# Copyright 2012 James McCauley
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
Lets you use Tk with POX.

Highly experimental.
"""

from collections import deque
from pox.core import core

log = core.getLogger()

#TODO: Bind revent events across thread

class MessageBoxer (object):
  def __init__ (self, tk):
    import tkinter.messagebox, tkinter.colorchooser, tkinter.simpledialog
    import tkinter.filedialog
    fields = "ERROR INFO QUESTION WARNING ABORTRETRYIGNORE OKCANCEL "
    fields += "RETRYCANCEL YESNO YESNOCANCEL ABORT RETRY IGNORE OK "
    fields += "CANCEL YES NO"
    for f in fields.split():
      setattr(self, f, getattr(tkMessageBox, f))

    methods = "showinfo showwarning showerror askquestion "
    methods += "askokcancel askyesno askretrycancel"
    self._addmethods(tkMessageBox, methods, tk)

    methods = "askinteger askfloat askstring"
    self._addmethods(tkSimpleDialog, methods, tk)

    methods = "askcolor"
    self._addmethods(tkColorChooser, methods, tk)

    methods = "askopenfilename asksaveasfilename"
    self._addmethods(tkFileDialog, methods, tk)

  def _addmethods (self, module, methods, tk):
    ...


class Tk (object):
  ...

  def run (self):
    ...


def launch ():
  ...