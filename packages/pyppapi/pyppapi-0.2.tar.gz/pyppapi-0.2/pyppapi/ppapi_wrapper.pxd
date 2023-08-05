"""
Definitions for PPAPI Simple events




"""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Matthew J. Turk
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

cimport numpy as np
import numpy as np
from libc.stdint cimport int32_t, int64_t, uint32_t

cdef extern from "ppapi/c/pp_instance.h" nogil:
    ctypedef int32_t PP_Instance

cdef extern from "ppapi/c/pp_bool.h" nogil:
    enum PP_Bool:
        PP_FALSE
        PP_TRUE

cdef extern from "ppapi/c/pp_resource.h" nogil:
    ctypedef int32_t PP_Resource

cdef extern from "ppapi/c/pp_var.h" nogil:
    enum PP_VarType:
        PP_VARTYPE_UNDEFINED
        PP_VARTYPE_NULL
        PP_VARTYPE_BOOL
        PP_VARTYPE_INT32
        PP_VARTYPE_DOUBLE
        PP_VARTYLE_STRING
        PP_VARTYPE_OBJECT
        PP_VARTYPE_ARRAY
        PP_VARTYPE_DICTIONARY
        PP_VARTYPE_ARRAY_BUFFER
        PP_VARTYPE_RESOURCE
        
    union PP_VarValue:
        PP_Bool as_bool
        int32_t as_int
        double as_double
        int64_t as_id

    struct PP_Var:
        PP_VarType type
        int32_t padding
        PP_VarValue value

cdef extern from "ppapi_simple/ps_event.h":
    ctypedef enum PSEventType:
        PSE_NONE
        PSE_INSTANCE_HANDLEINPUT
        PSE_INSTANCE_HANDLEMESSAGE
        PSE_INSTANCE_DIDCHANGEVIEW
        PSE_INSTANCE_DIDCHANGEFOCUS
        PSE_GRAPHICS3D_GRAPHICS3DCONTEXTLOST
        PSE_MOUSELOCK_MOUSELOCKLOST
        PSE_ALL

    ctypedef uint32_t PSEventTypeMask

    ctypedef struct PSEvent:
        PSEventType type
        PP_Bool as_bool
        PP_Resource as_resource
        PP_Var as_var

    PSEvent* PSEventTryAcquire()
    PSEvent* PSEventWaitAcquire()
    void PSEventRelease(PSEvent* event)
    void PSEventSetFilter(PSEventTypeMask mask)

cdef extern from "ppapi/c/ppb_messaging.h" nogil:
    ctypedef struct PPB_Messaging:
        void (*PostMessage)(PP_Instance instance, PP_Var message)

cdef extern nogil:
    const PPB_Messaging *setup_ppapi_connection(PP_Instance *instance)

ctypedef fused any_np_type:
    np.int8_t
    np.uint8_t
    np.int16_t
    np.uint16_t
    np.int32_t
    np.uint32_t
    np.float32_t
    np.float64_t
