# System Dependent Variables
from platform import system

OP_S = system()
HIDDEN_PREFIX = "~$" if OP_S == "Windows" else "."

try:
    import win32file
except ImportError:
    win32file = None
