"""test wildard import
"""
__revision__ = 0

from input.func_fixme import *
# This is an unresolved import which still generates the wildcard-import
# warning.
from unknown.package import *

def abcd():
    """use imports"""
    function()
