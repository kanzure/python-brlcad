# python-brlcad

The **python-brlcad** module provides a way to use brlcad from inside python
based on ctypes bindings. These ctypes bindings are generated during
install-time using ctypesgen.

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

Use either mingw or cygwin to provide gcc during installation.

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

not yet

## license

BSD.
