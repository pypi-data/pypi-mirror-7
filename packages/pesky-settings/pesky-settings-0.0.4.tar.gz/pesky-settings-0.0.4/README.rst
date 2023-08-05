pesky-settings
==============

pesky-settings is a library for managing application settings, merging data
from configuration files and command line arguments and converting to python
native data types.  Additionally, pesky-settings has an 'action' interface
which is useful for constructing hierarchical command sets.

pesky-settings is built on top of the venerable getopt and ConfigParser
packages from the python standard library, so it should work on any python
you can find (as opposed to optparse or argparse packages, which were
somewhat late additions to python 2).
