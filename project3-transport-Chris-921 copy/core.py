# Copyright 2011-2022 James McCauley
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
Some of POX's core API and functionality is here, largely in the POXCore
class (an instance of which is available as pox.core.core).

This includes things like component rendezvous, logging, system status
(up and down events), etc.
"""

...


class POXCore (EventMixin):
  """
  A nexus of of the POX API.

  pox.core.core is a reference to an instance of this class.  This class
  serves a number of functions.

  An important one is that it can serve as a rendezvous point for
  components.  A component can register objects on core, and they can
  then be accessed on the core object (e.g., if you register foo, then
  there will then be a pox.core.core.foo).  In many cases, this means you
  won't need to import a module.

  Another purpose to the central registration is that it decouples
  functionality from a specific module.  If myL2Switch and yourL2Switch
  both register as "switch" and both provide the same API, then it doesn't
  matter.  Doing this with imports is a pain.

  Additionally, a number of commmon API functions are vailable here.
  """
  ...

  def call_later (_self, _func, *args, **kw):
    # first arg is `_self` rather than `self` in case the user wants
    # to specify self as a keyword argument
    """
    Call the given function with the given arguments within the context
    of the co-operative threading environment.
    It actually calls it sooner rather than later. ;)
    Much of POX is written without locks because it's all thread-safe
    with respect to itself, as it's written using the recoco co-operative
    threading library.  If you have a real thread outside of the
    co-operative thread context, you need to be careful about calling
    things within it.  This function provides a rather simple way that
    works for most situations: you give it a callable (like a method)
    and some arguments, and it will call that callable with those
    arguments from within the co-operative threader, taking care of
    synchronization for you.
    """

    ...

  def registerNew (self, __componentClass, *args, **kw):
    """
    Give it a class (and optional __init__ arguments), and it will
    create an instance and register it using the class name.  If the
    instance has a _core_name property, it will use that instead.
    It returns the new instance.
    core.registerNew(FooClass, arg) is roughly equivalent to
    core.register("FooClass", FooClass(arg)).
    """
    ...

  def register (self, name, component=None):
    """
    Makes the object "component" available as pox.core.core.name.

    If only one argument is specified, the given argument is registered
    using its class name as the name.
    """
    #TODO: weak references?
    if component is None:
      component = name
      name = component.__class__.__name__
      if hasattr(component, '_core_name'):
        # Default overridden
        name = component._core_name

    if name in self.components:
      log.warn("Warning: Registered '%s' multipled times" % (name,))
    self.components[name] = component
    self.raiseEventNoErrors(ComponentRegistered, name, component)
    self._try_waiters()

  def call_when_ready (self, callback, components=[], name=None, args=(),
                       kw={}):
    """
    Calls a callback when components are ready.
    """
    if callback is None:
      callback = lambda:None
      callback.__name__ = "<None>"
    if isinstance(components, str):
      components = [components]
    elif isinstance(components, set):
      components = list(components)
    else:
      try:
        _ = components[0]
        components = list(components)
      except:
        components = [components]
    if name is None:
      #TODO: Use inspect here instead
      name = getattr(callback, '__name__')
      if name is None:
        name = str(callback)
      else:
        name += "()"
        if hasattr(callback, '__self__'):
          name = getattr(callback.__self__.__class__,'__name__','')+'.'+name
      if hasattr(callback, '__module__'):
        # Is this a good idea?  If not here, we should do it in the
        # exception printing in try_waiter().
        name += " in " + callback.__module__
    entry = (callback, name, components, args, kw)
    self._waiters.append(entry)
    self._try_waiter(entry)

  def _try_waiter (self, entry):
    """
    Tries a waiting callback.

    Calls the callback, removes from _waiters, and returns True if
    all are satisfied.
    """
    ...

  def listen_to_dependencies (self, sink, components=None, attrs=True,
                              short_attrs=False, listen_args={}):
    """
    Look through *sink* for handlers named like _handle_component_event.
    Use that to build a list of components, and append any components
    explicitly specified by *components*.

    listen_args is a dict of "component_name"={"arg_name":"arg_value",...},
    allowing you to specify additional arguments to addListeners().

    When all the referenced components are registered, do the following:
    1) Set up all the event listeners
    2) Call "_all_dependencies_met" on *sink* if it exists
    3) If attrs=True, set attributes on *sink* for each component
       (e.g, sink._openflow_ would be set to core.openflow)

    For example, if topology is a dependency, a handler for topology's
    SwitchJoin event must be defined as so:
       def _handle_topology_SwitchJoin (self, ...):

    *NOTE*: The semantics of this function changed somewhat in the
            Summer 2012 milestone, though its intention remains the same.
    """
    ...
  
  ...

