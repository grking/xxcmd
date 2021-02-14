"""A helper for remembering useful shell commands."""
import os
from subprocess import check_output
from .cmdmanager import CmdManager
from .dbitem import DBItem
from .main import main, __version__


# Inspect git version if we're in a git repo
__dev_version__ = ''
thisdir = os.path.dirname(os.path.realpath(__file__))
if os.path.isdir(os.path.join(thisdir, os.pardir, '.git')):
    ver = check_output('git describe --tags'.split())
    if ver:
        ver = ver.decode('utf-8').strip()
        __dev_version__ = ver


__all__ = ('DBItem', 'CmdManager', 'main', '__version__', '__dev_version__')
