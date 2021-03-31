__version__ = '3.0.7'
__version_info__ = (3, 0, 7)

try:
    from pygco import *  # noqa: F401 F403
except ImportError:
    from gco.pygco import *  # noqa: F401 F403
