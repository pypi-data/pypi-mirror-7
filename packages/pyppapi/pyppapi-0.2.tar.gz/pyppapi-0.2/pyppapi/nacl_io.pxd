"""
Definitions for nacl_io Cython wrapper




"""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Matthew J. Turk
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

# This includes most of the functions that are necessary to set up the web
# filesystem and so on.

cdef extern from "sys/stat.h":
    ctypedef int mode_t

cdef extern from "sys/types.h":
    int mkdir(char *pathname, mode_t mode)

cdef extern from "sys/mount.h":
    int mount(char *source,
              char *target,
              char *filesystemtype,
              unsigned long mountflags,
              void *data)
    int umount(char *target)

cdef extern from "nacl_io/nacl_io.h":
    pass

from libc.string cimport strerror
from libc.errno cimport errno
