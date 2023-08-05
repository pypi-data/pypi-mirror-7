Dirty Hungarian Phrasebook
==========================
DHP is a library of snippets almost guaranteed to get you into trouble.

I obtained it from a vendor on the corner outside of PyCon.


Phrasebook Contents
--------------------

**dhp.test**

  * **tempfile_containing** - generate a temporary file that contains indicated contents and returns the filename for use.  When finished the tempfile is removed.

::

    from dhp.test import tempfile_containing

    contents = 'I will not by this record, it is scratched.'
    with tempfile_containing(contents) as fname:
        do_something(fname)


Supports
--------
Tested on Python 2.7, 3.2, 3.3, 3.4

.. image:: https://drone.io/bitbucket.org/dundeemt/yamjam/status.png
    :target: https://drone.io/bitbucket.org/dundeemt/yamjam/latest
    :alt: Build Status

Requirements
------------
None.

Installation
------------
Make sure to get the latest version.

  pip install dhp

