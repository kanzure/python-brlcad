import distutils.core
from distutils.command.install import install as Installer

def post_install():
    """
    After regular installation is complete, this function acts as a
    post-install script to generate the bindings against whatever version of
    BRL-CAD is installed.
    """
    import ctypesgen.ctypesgencore as ctypesgencore
    print "ctypesgen version: " + str(ctypesgencore.__version__)

class CustomInstaller(Installer):
    def run(self):
        Installer.run(self)
        post_install()

distutils.core.setup(
    name="thing_postinstall",
    version="0.0.1",
    description="An attempt at a post-install script.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-brlcad",
    packages=["thing_postinstall"],
    cmdclass={
        "install": CustomInstaller,
    },
)
