#! /usr/bin/env python
"""Experimental module for Python 2.6 compatibility."""

import sys
import logging
import io
import types
import zipfile
from wsgiref.simple_server import ServerHandler


def finish_content(self):
    # ugly patch for python 2.6; see the following for details:
    # http://stackoverflow.com/questions/3857029/does-wsgi-override-content-length-header
    if not self.headers_sent:
        if (self.environ.get('REQUEST_METHOD', '') != 'HEAD' or
                'Content-Length' not in self.headers):
            self.headers['Content-Length'] = 0
        self.send_headers()


def is_zipfile(filename):
    # patched to accept a file that is already open we use the
    # _EndRecData method directly, we're all grown-ups here
    try:
        if isinstance(filename, (types.StringTypes)):
            fpin = open(filename, "rb")
            endrec = zipfile._EndRecData(fpin)
            fpin.close()
        else:
            endrec = zipfile._EndRecData(filename)
        if endrec:
            return True
    except IOError:
        pass
    return False


if sys.hexversion < 0x02070000:
    logging.info("Adding missing constants to py26.io")
    io.SEEK_SET = 0
    io.SEEK_CUR = 1
    io.SEEK_END = 2

    class memoryview(object):       # noqa

        def __init__(self):
            raise TypeError("memoryview object not available in py26")

    logging.info("Patching wsgiref.simple_server.ServerHandler for HEAD bug")
    ServerHandler.finish_content = finish_content

    logging.info("Patching zipfile.is_zipfile for open files")
    zipfile.is_zipfile = is_zipfile

    py26 = True
else:
    py26 = False
