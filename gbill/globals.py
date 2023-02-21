import sys
import os

from . import APP_NAME

def get_datadir() -> str:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    * linux: ~/.local/share
    * macOS: ~/Library/Application Support
    * windows: C:\\Users\\<UserName>\\AppData\\Local
    """
    system = sys.platform
    path = ''

    if system == "win32":
        path = os.path.normpath(os.environ['LOCALAPPDATA'])
    elif system == "darwin":
        path = os.path.expanduser('~/Library/Application Support/')
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser("~/.local/share"))
    
    return path

# create your program's directory

APP_DIR = os.path.join(get_datadir(), APP_NAME)
os.makedirs(APP_DIR, exist_ok=True)
