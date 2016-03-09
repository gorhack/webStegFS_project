File_System package
*******************

Submodules
==========

covertfs module
---------------

The `covertfs` module extends the `pyfilesystem` package, using the `MemoryFS` file system.
The MemoryFS file system stores all directory and file info in main memory, to allow for instantaneous file access as well as to avoid writing any FS information to disk. This allows for plausible deniability. All filesystem-necessary commands (ls, cd, mkdir, rm etc) are extended in this module. 

The covertfs module includes CovertFile, a subclass of MemoryFile, CovertEntry, a subclass of MemoryEntry, and CovertFS, a subclass of MemoryFS. CovertFS uses CovertFile as the file factory, and CovertEntry as the entry factory.

.. automodule:: File_System.covertfs
    :members:
    :undoc-members:
    :show-inheritance:


memfuse module
--------------

The `memfuse` module extends the `pyfuse` package, specifically the `Operations` module.
'Operations' is linked to the Unix FUSE package with python ctypes, to make the file system available to the user, without making system calls. The memfuse module extends all necessary file system operations in a way that is accessible by FUSE, effectively linking the CovertFS class to the FUSE package. When mounted (using FUSE) onto the native Linux file system, memfuse provides access to all files and directories in the CovertFS file system.

.. automodule:: File_System.memfuse
    :members:
    :undoc-members:
    :show-inheritance:
