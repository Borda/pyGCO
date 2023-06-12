# edit also setup.py!

import numpy

from gco.__about__ import *  # noqa: F403

# patch for numpy 1.24+
for name, tp in [("int", int), ("float", float), ("bool", bool)]:
    if not hasattr(numpy, name):
        setattr(numpy, name, tp)

try:
    from pygco import *  # noqa: F401 F403
except ImportError:
    from gco.pygco import *  # noqa: F401 F403
