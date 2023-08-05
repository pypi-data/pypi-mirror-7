"""
aspen.exceptions
++++++++++++++++

Exceptions used by Aspen
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aspen import Response


class LoadError(Exception):
    """Represent a problem loading a resource.
    """
    # Define this here to avoid import issues when json doesn't exist.


class CRLFInjection(Response):
    """
    A 400 Response (per #249) raised if there's a suspected CRLF Injection attack in the headers
    """
    def __init__(self):
        Response.__init__(self, code=400, body="Possible CRLF Injection detected.")
