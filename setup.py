from setuptools import setup
from setuptools.command.install import install as InstallCommand
from setuptools.command.develop import develop as DevelopCommand

import sys
import os

def run_before(self):
    """
    Default pre-install script.
    """
    pass

def run_after(self):
    """
    Default post-install script.
    """
    import thing_postinstall.post_install
    thing_postinstall.post_install.main()

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
        original_run(self)
        self.run_after()

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
    name="thing_postinstall",
    version="0.0.1",
    description="An attempt at a post-install script.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-brlcad",
    packages=["thing_postinstall"],
    setup_requires=[
        "ctypesgen",
        "pbs",
    ],
    dependency_links=[
        "https://github.com/kanzure/ctypesgen/tarball/master#egg=ctypesgen",
    ],
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
    },
)
