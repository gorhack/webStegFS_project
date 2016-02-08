File_System package
*******************

Submodules
==========

covertfs module
---------------

The `covertfs` module extends the `pyfilesystem` package, using the `MemoryFS` file system.
The MemoryFS file system stores all directory and file info in main memory, to allow for instantaneous file access as well as to avoid writing any FS information to disk. This allows for plausible deniability.

.. automodule:: File_System.covertfs
    :members:
    :undoc-members:
    :show-inheritance:


memfuse module
--------------

The `memfuse` module extends the `pyfilesystem` package, using the `MemoryFS` file system.
Please change all this stuff. It's probably not right.

.. automodule:: File_System.memfuse
    :members:
    :undoc-members:
    :show-inheritance:
