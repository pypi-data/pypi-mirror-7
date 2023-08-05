KeepMePosted Documentation
==========================
This module provides an object-oriented event handling framework.  In this 
framework, events are registered by classes and then broadcasted by individual 
objects.  Listening for events from specific objects is made easy.

Simple Example
--------------
The most important parts of this framework are the Dispatcher class and the 
event() decorator.  Dispatcher is a base class for objects that that want to 
broadcast events and the event decorator is used to register events.

>>> from kemepo import Dispatcher, event
>>> class Button (Dispatcher):
        @event
        def on_press(self):
            print('Calling internal handler')

The method decorated by event() is taken to be the "internal handler", distinct 
from any "external observers" that may be attached using connect() later on.  
When an event is triggered using handle(), the internal handler is called 
before the external observers.  

>>> button = Button()
>>> button.connect(on_press=lambda: print('Calling external observer.'))
>>> button.handle('on_press')
Calling internal handler.
Calling external observer.

Installation
------------
KeepMePosted can be installed from PyPI::

    $ pip install kemepo

You can also download the source code directly from GitHub.  The code is made 
available under the MIT license.  If you find the code useful and want to make 
improvements, feel free to make pull requests::

    $ git clone https://github.com/kalekundert/KeepMePosted.git kemepo

Registering Events
------------------
Within this framework, objects can only broadcast events that have already been 
registered with their class.  Typically, events are registered when the class 
is created using the event() decorator:

>>> class CheckBox (Dispatcher):
        @event
        def on_check(self):
            print('Calling internal handler')

This registers a new event based on the given method.  The name of the event is 
the name of the method, and the method itself becomes the internal handler for 
that type of event.  Furthermore, the argument signature and the docstring of 
the handler are used for error checking and documentation, respectively.  This 
information is often useful even if the handler itself is left unimplemented.

It is possible to register new events without using the event decorator.  The 
advantage of doing this is that you can register events after the class has 
been created.  You also don't need to specify an internal handler (the second 
argument) when manually registering events, although doing so provides improved 
error checking and documentation, as discussed above.

>>> CheckBox.register_event('on_uncheck', lambda: None)

All that said, you should very rarely need to manually register events.  In the 
typical case, the event() decorator should be preferred.

Triggering Events
-----------------
There are two ways to trigger an event: handle() and notify().  The difference 
concerns the internal handler (i.e. the callback used the register the event), 
which is called by handle() and not called by notify().  Referring back to the 
button example from the first section:

>>> button.handle('on_press')
Calling internal handler.
Calling external observer.
>>> button.notify('on_press')
Calling external observer.

Usually you should use notify().  Use notify() only in cases where notify() 
would create infinite recursion.  If you simply don't want the internal handler 
to do anything, just leave it unimplemented.

Reacting to Events
------------------
Although only objects that inherit from Dispatcher can broadcast events, any 
callback can be used to react to events.  The connect() method provides a very 
flexible interface for connecting observers to dispatchers.  In particular, 
observers can be provided either as keyword arguments mapping event names to 
callbacks or as objects with method names matching event names.  

The former approach is probably more intuitive.  Any type of callable can be 
used as an observer callback, including functions and lambda functions.  

>>> def observer_function(): print("Calling an observer function.")
>>> button.connect(on_press=observer_function)
>>> button.connect(on_press=lambda: print("Calling an observer lambda."))

The latter approach provides a powerful way to listen to many events from the 
same object.  Provide any number of arguments to connect, and each will be 
searched for methods with names matching registered events.  Those methods will 
be connected as observers of those events.

>>> class Observer:
        def on_press(self):
            print("Calling an observer method.")

>>> observer_object = Observer()
>>> button.connect(observer_object)

No matter an observer is specified, it must have the same argument signature as 
the internal handler used to register the event.  A TypeError will be raised 
otherwise.

Events can be disconnected using the disconnect() method.

>>> button.disconnect(observer_function)
>>> button.disconnect(observer_object)

Error Checking
--------------
Strong error checking is possible because events are registered when the class
is created.  Exceptions are thrown if you attempt any of the following:

1. Connect to an undefined event.
2. Handle an undefined event.
3. Connect an observer that doesn't have the same argument signature as the 
   internal handler. 
4. Handle an event without providing the arugments expected by the internal 
   handler.
   
Docstring Generation
--------------------
One advantage of registering events using the event() decorator (e.g. before 
the class in question has been created) is that those events can be 
incorporated into the class docstring.  This is useful both for use with help() 
in the python interpreter and for use with Sphinx for online documentation.

To incorporate event documentation into the docstring of a Dispatcher subclass, 
just include the string '{events}'.  This will be replaced by a list of the 
events that are registered with that class.  (Note that only events registered 
using the event() decorator will be included.)  Replacement is done using 
standard string formatting, so this is roughly what's going on behind the 
scenes:

>>> cls.__doc__ = cls.__doc__.format(events=events_docstring)

You can control the exact format of the event documentation using the 
set_docstring_formatter() function.  This function takes one argument, which 
can either be the name of a built-in formatter or a custom formatter function.  

Currently, the two built-in formatters are named *pretty* and *sphinx*.  The 
*pretty* formatter is the default.  It's the more readable of the two and it's 
meant to look good in interpreter sessions, but it's not rendered very nicely 
by Sphinx (although it does produce legal restructured text).  The *sphinx* 
formatter is a more heavily marked-up alternative that looks better when 
rendered by Sphinx.  To use the *sphinx* formatter in Sphinx, but these lines 
in ``docs/conf.py``:

>>> import kemepo
>>> kemepo.set_docstring_formatter('sphinx')

This must be done before you import any of your Dispatcher subclasses, because 
the docstrings are created at the same time as the class itself.

If you want to write a custom formatter, provide a function that accepts a 
single OrderedDict argument.  This is a mapping between event names and 
EventMetaData objects, in the order that the events were defined.  Return a  
string to incorporate into the class docstring.  You may find the 
format_arg_spec() and format_description() functions useful.
