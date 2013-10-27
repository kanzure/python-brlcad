from setuptools import setup
from setuptools.command.install import install as InstallCommand
from setuptools.command.develop import develop as DevelopCommand

import glob
import os
import sys
import traceback

def run_before(command):
    """
    Default pre-install script.

    @param command: setuptools command instance, either an InstallCommand or
    DevelopCommand.
    """
    pass

def run_after(command):
    """
    Default post-install script.

    @param command: setuptools command instance, either an InstallCommand or
    DevelopCommand.
    """
    # the actual post install script is elsewhere, sorry :)
    import brlcad
    import brlcad.install.post_install

    #library_path = os.path.join(command.install_lib, "brlcad")
    #library_path = os.path.abspath(os.path.dirname(brlcad.__file__))
    egg_path = glob.glob(os.path.join(command.install_lib, "brlcad*.egg/"))[0]
    library_path = os.path.join(egg_path, "brlcad")

    try:
        brlcad.install.post_install.main(library_path=library_path)
    except Exception as exception:
        traceback.print_exc()

def hookify(command_subclass):
    """
    A decorator for subclasses of setuptools commands that calls a before_run
    hook and an after_run hook.
    """
    original_run = command_subclass.run

    def modified_run(self):
        """
        Call the original run implementation, but surround it with before_run
        and after_run calls.
        """
        self.run_before()

        # from setuptools/command/install.py
        #
        # Attempt to detect whether we were called from setup() or by another
        # command.  If we were called by setup(), our caller will be the
        # 'run_command' method in 'distutils.dist', and *its* caller will be
        # the 'run_commands' method.  If we were called any other way, our
        # immediate caller *might* be 'run_command', but it won't have been
        # called by 'run_commands'.  This is slightly kludgy, but seems to
        # work.
        caller = sys._getframe(2)
        caller_module = caller.f_globals.get('__name__','')
        caller_name = caller.f_code.co_name

        if caller_module != 'distutils.dist' or caller_name!='run_commands':
            # We weren't called from the command line or setup(), so we
            # should run in backward-compatibility mode to support bdist_*
            # commands.
           output =  original_run(self)
        else:
            output = self.do_egg_install()

        self.run_after()
        return output

    # attach the new implementation
    command_subclass.run = modified_run

    # set the same run_before everywhere
    if "run_before" not in command_subclass.__dict__:
        command_subclass.run_before = run_before

    # set the same run_after everywhere
    if "run_after" not in command_subclass.__dict__:
        command_subclass.run_after = run_after

    return command_subclass

@hookify
class CustomDevelopCommand(DevelopCommand):
    """
    Override the "develop" command to have the hooks.
    """
    pass

@hookify
class CustomInstallCommand(InstallCommand):
    """
    Override the "install" command to have the hooks.
    """
    pass

setup(
    name="brlcad",
    version="0.0.1",
    description="An attempt at a post-install script.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-brlcad",
    packages=["brlcad"],
    zip_safe=False,
    setup_requires=[
        "ctypesgen-dev",
    ],
    install_requires=[
        "ctypesgen-dev",
    ],
    dependency_links=[
        "https://github.com/kanzure/ctypesgen/tarball/short-preamble-setuptools#egg=ctypesgen-dev-0.0.1",
    ],
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
    },
)
