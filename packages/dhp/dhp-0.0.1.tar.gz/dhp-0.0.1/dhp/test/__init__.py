'''routines and snippets generally userful for testing'''

from contextlib import contextmanager
import io
import os
from tempfile import mkstemp

@contextmanager
def tempfile_containing(contents='', suffix=''):
    '''create a temporary file, with optional suffix and return the filename,
    cleanup when finished'''

    os_fd, temp_path = mkstemp(suffix=suffix)
    os.close(os_fd)     # close the os handle returned by mkstemp

    with io.open(temp_path, 'wb') as py_fh:
        py_fh.write(contents.encode('utf-8'))

    try:
        yield temp_path
    finally:
        os.remove(temp_path)
