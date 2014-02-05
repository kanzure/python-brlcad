
# installing on windows

On windows none of the required components is installed by default.
This file describes the steps taken on a tested install of python-brlcad,
you might want to check them if having trouble getting python-brlcad to work. 

## installing python and pip

If don't already have python installed, please get the right version from:

http://www.python.org/getit/

Be sure you take the 2.7.x version and not 3.x.y, and that it is the right
32 or 64 bit version matching your OS.

Once you installed python, you'll also need to install pip - it doesn't come
with the default installation.

The following web page has easy instructions but I'm not sure how trustworthy
it is, so you might fare better searching the web for "python pip windows".

http://docs.python-guide.org/en/latest/starting/install/win/

I include the short version here in case of the above link goes broken:

Install setuptools: run the python script available here:
https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

Install pip: run the python script available here:
https://raw.github.com/pypa/pip/master/contrib/get-pip.py

If you can't get pip installed, you can get by with installing setuptools
only and go for installing python-brlcad from the source package.

## provide a C preprocessor

python-brlcad uses ctypesgen under the hood, which in turns needs a C 
preprocessor to parse the library headers. While any other C preprocessor could
work, gcc is the only one extensively tested and known to work well.

To provide gcc on windows during installation you can use either mingw or cygwin.
There is a bug in pip that causes a WindowsError to occur when installing
this package, see [the bug report](https://github.com/pypa/pip/pull/1263) for more details.

There is a bug in ctypesgen that prevents the mingw gcc method from working on
Windows, so start with the cygwin method and then try mingw if that doesn't
work.

### cygwin

One option is to install cygwin and use cygwin gcc. However, it is
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

### mingw

Install a Windows build of gcc (probably by installing mingw and adding
`C:\MingW\bin` to the PATH environment variable). For a really minimal
install you can follow the steps below; if you know how to do that or already
have MinGW installed skip to the next section.

Install mingw-get-setup.exe from:
http://sourceforge.net/projects/mingw/files/

The `MinGW Installation Manager` should run automatically now, if not start
it manually from the Windows `Start Menu/All programs`. Select `Basic Setup`
and choose the `mingw*-base` package, then Click `Installation/Apply Changes`.

If you installed MinGW in the default `%SystemRoot%:\MinGW` directory, skip to
the next section, the python-brlcad install script will find it there.

Otherwise you'll need to add the MinGW bin directory (defaults to
`C:\MinGW\bin`) to the PATH environment variable: on my Windows that
was accessible by right clicking on `Computer` in the Explorer, select
`Properties`, then `Advanced system settings`, then `Environment Variables`.
You need then to find the PATH variable (or add it if it doesn't exist), and
add `C:\MinGW\bin` at the end of it (separate it with a `;` if PATH already
has some other entries).

## installing python-brlcad

Run in a command window:
 
```
C:\Python27\Scripts\pip.exe install --upgrade brlcad
```


