# python-brlcad: Open-source solid modeling in python.

The **python-brlcad** module provides a way to use [brlcad](http://brlcad.org/)
from inside python based on ctypes bindings. These ctypes bindings are
generated during install-time using
[ctypesgen](https://github.com/kanzure/ctypesgen).

## installing

```
pip install -U brlcad
```

or

```
git clone git@github.com:kanzure/python-brlcad.git
cd python-brlcad/
python setup.py install
```

### installing on windows

Use either mingw or cygwin to provide gcc during installation. There is a bug
in pip that causes a WindowsError to occur when installing this package, see
[the bug report](https://github.com/pypa/pip/pull/1263) for more details.

#### mingw

Install a Windows build of gcc (probably by installing mingw and adding
`C:\MingW\bin` to the PATH environment variable) and then run:

```
C:\Python27\Scripts\pip.exe install --upgrade brlcad
```

TODO: there may be a way to run this installation process while under `msys`
without updating the system PATH.

#### cygwin

Another option is to install cygwin and use cygwin gcc. However, it is
important to clarify that there is no cygwin brlcad build. Using cygwin gcc is
just a cheap shortcut for the Windows python installation process of
python-brlcad. Mainly this trick is useful for Windows users that already have
cygwin gcc.

To use cygwin gcc, start the python-brlcad install process in cygwin bash:

```
/cygdrive/c/Python27/Scripts/pip.exe install --upgrade brlcad
```

During the installation, ctypesgen will make use of cygwin gcc because of the
cygwin $PATH environment variable.

There is no brlcad build that targets cygwin.

## testing

```
nosetests
```

## usage

Sorry, not yet. Check the `examples/` folder.

# Known to work with..

Operating systems known to work:

* linux distros
* windows

Support for Mac OS X is planned but not yet implemented or tested.

## license

BSD.
