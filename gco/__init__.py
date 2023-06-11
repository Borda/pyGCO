# edit also setup.py!
__version__ = '3.0.8'
__version_info__ = tuple([int(i) for i in __version__.split('.')])

import numpy

# patch for numpy 1.24+
for name, tp in [("int", int), ("float", float), ("bool", bool)]:
    if not hasattr(numpy, name):
        setattr(numpy, name, tp)

try:
    from pygco import *  # noqa: F401 F403
except ImportError:
    from gco.pygco import *  # noqa: F401 F403
