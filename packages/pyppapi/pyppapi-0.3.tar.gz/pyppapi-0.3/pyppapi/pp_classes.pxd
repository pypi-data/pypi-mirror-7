"""
Class definitions for PPB objects to be used in messaging.




"""
# distutils: language = c++

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Matthew J. Turk
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

from libc.stdint cimport int32_t, uint32_t
from libcpp.string cimport string
from libcpp cimport bool
from .ppapi_wrapper cimport PP_Var

cdef extern from "ppapi/cpp/var.h" namespace "pp":
    cdef cppclass Var:
        Var()
        Var(bool)
        Var(int32_t)
        Var(double)
        Var(char *)
        Var(PP_Var& var)
        PP_Var &pp_var()
        # Now conversions
        bool AsBool()
        int32_t AsInt()
        double AsDouble()
        string AsString()
        bool is_undefined()
        bool is_null()
        bool is_bool()
        bool is_string()
        bool is_object()
        bool is_array()
        bool is_dictionary()
        bool is_int()
        bool is_double()
        bool is_number()
        bool is_array_buffer()

cdef extern from "ppapi/cpp/var_array.h" namespace "pp":
    cdef cppclass VarArray(Var):
        VarArray()
        VarArray(const Var &var)
        Var Get(uint32_t index)
        bool Set(uint32_t index, const Var &value)
        uint32_t GetLength()
        bool SetLength(uint32_t length)
        VarArray GetKeys()

cdef extern from "ppapi/cpp/var_array_buffer.h" namespace "pp":
    cdef cppclass VarArrayBuffer(Var):
        VarArrayBuffer()
        VarArrayBuffer(const Var &var)
        VarArrayBuffer(uint32_t size_in_bytes)
        void *Map()
        void Unmap()

cdef extern from "ppapi/cpp/var_dictionary.h" namespace "pp":
    cdef cppclass VarDictionary(Var):
        VarDictionary()
        VarDictionary(const Var &var)
        Delete( const Var &key )
        Var Get (const Var &key)
        VarArray GetKeys()
        bool Set(Var &key, Var &value)
        bool HasKey(const Var &key)
