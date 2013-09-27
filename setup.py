from setuptools import setup
from setuptools.command.install import install as InstallCommand
from setuptools.command.develop import develop as DevelopCommand

def pre_install():
    print "PRE_INSTALL"

def post_install():
    print "POST_INSTALL"

def setuptoolcommandify(command_subclass):
    """
    A decorator for subclasses of setuptool commands that calls a pre_run hook
    and a post_run hook.
    """
    original_run = command_subclass.run

    def modified_run(self):
        """
        Call the original run implementation, but wrap it with pre-run and
        post-run hooks.
        """
        self.pre_run()
        original_run(self)
        self.post_run()

    # attach the new implementation
    command_subclass.run = modified_run

    return command_subclass

class CustomCommandMixin(object):
    """
    Just a way to get the hooks into the subclasses in a DRY manner. Override
    these defaults if something more specific has to happen in a particular
    command.
    """

    def pre_run(self):
        return pre_install()

    def post_run(self):
        return post_install()

@setuptoolcommandify
class CustomDevelopCommand(DevelopCommand, CustomCommandMixin):
    pass

@setuptoolcommandify
class CustomInstallCommand(InstallCommand, CustomCommandMixin):
    pass

setup(
    name="thing_postinstall",
    version="0.0.1",
    description="An attempt at a post-install script.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-brlcad",
    packages=["thing_postinstall"],
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
    },
)
