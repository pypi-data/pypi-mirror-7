from __future__ import absolute_import

from ..version_info import PY3

if PY3:
    from http.client import *
else:
    from httplib import *
