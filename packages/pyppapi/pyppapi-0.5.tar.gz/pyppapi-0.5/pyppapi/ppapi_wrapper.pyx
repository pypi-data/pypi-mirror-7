"""
Definitions for nacl_io Cython wrapper




"""
# distutils: language = c++

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Matthew J. Turk
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

from nacl_io cimport mount, strerror, umount, errno
from pp_classes cimport Var, VarArray, VarDictionary, VarArrayBuffer, bool, \
    Resource, FileSystem, IsFileSystem, PassRef
import numpy as np
cimport numpy as np
import types
import sys
import base64
import tempfile
import imp
import time
import os
cimport posix.unistd
from libc.math cimport ceil

cdef bool bTrue = True
cdef bool bFalse = False

cdef class NaClInstance:
    cdef const PPB_Messaging *ppb_messaging
    cdef PP_Instance pp_instance
    cdef public object filesystem_resources
    cdef public object automount

    def __init__(self):
        self.pp_instance = 0
        self.ppb_messaging = NULL
        self.automount = True
        self.filesystem_resources = {}
        # We should probably figure out how to get the instance here.
        self.ppb_messaging = setup_ppapi_connection(&self.pp_instance)
        if self.ppb_messaging == NULL or self.pp_instance == 0:
            print "Either ppb_messaging or pp_instance is NULL."
            raise RuntimeError

    def mount(self, source, target, filesystemtype, mountflags,
              char *mountopts = NULL):
        cdef int res
        res = mount(source, target, filesystemtype, mountflags, mountopts)
        if res:
            print "Error: %s" % (strerror(errno))
        return res

    def umount(self, pathname):
        cdef int res
        res = umount(pathname)
        if res:
            print "Error: %s" % (strerror(errno))
        return res

    def send_message(self, msg):
        # Any message we get is assumed to be a string, and if it is to be
        # JSON'd, it should have already been JSON-encoded.
        cdef char *msg_ = msg
        cdef Var vmsg = Var(msg_)
        cdef PP_Var message = vmsg.pp_var()
        self.ppb_messaging.PostMessage(self.pp_instance, message)

    def pylab(self):
        try:
            import matplotlib
        except Exception as e:
            print "Matplotlib not importable.  Not enabling backend."
            print "Exception: %s" % e
            return
        import matplotlib.backends.backend_agg as bagg
        from matplotlib._pylab_helpers import Gcf
        import pylab
        def pyppapi_draw_if_interactive():
            if matplotlib.is_interactive():
                figManager =  Gcf.get_active()
                if figManager is not None:
                    self._canvas_deliver(figManager.canvas)
        def pyppapi_show(mainloop = True):
            # We ignore mainloop here
            for manager in Gcf.get_all_fig_managers():
                self._canvas_deliver(manager.canvas)
        # Matplotlib has very nice backend overriding.
        # We should really use that.  This is just a hack.
        matplotlib.use("agg") # Hotfix for when we import pylab below
        new_agg = imp.new_module("pyppapi_agg")
        new_agg.__dict__.update(bagg.__dict__)
        new_agg.__dict__.update(
            {'show': pyppapi_show,
             'draw_if_interactive': pyppapi_draw_if_interactive})
        sys.modules["pyppapi_agg"] = new_agg
        bagg.draw_if_interactive = pyppapi_draw_if_interactive
        matplotlib.rcParams["backend"] = "module://pyppapi_agg"
        pylab.switch_backend("module://pyppapi_agg")
        print "Backend enabled."

    def _canvas_deliver(self, canvas):
        tf = tempfile.TemporaryFile()
        canvas.print_png(tf)
        tf.seek(0)
        img_data = base64.b64encode(tf.read())
        tf.close()
        self.send_message("img_data:" + img_data)

    def send_raw_object(self, obj):
        cdef Var v = convert_to_var(obj)
        cdef PP_Var message = v.pp_var()
        self.ppb_messaging.PostMessage(self.pp_instance, message)

    def send_object(self, obj):
        cdef Var v = convert_to_var(obj)
        cdef VarDictionary vd = VarDictionary()
        cdef char *key = "__ispyppapi__"
        vd.Set(Var(key), Var(bTrue))
        key = "message"
        vd.Set(Var(key), v)
        cdef PP_Var message = vd.pp_var()
        self.ppb_messaging.PostMessage(self.pp_instance, message)

    def wait_for_message(self, int timeout = 10, int sleeptime = 10000):
        # This will execute a blocking call to wait for a message.  Note that
        # it does not provide deserialization -- the message will be returned
        # as JSON text.  This adds overhead to numeric types.
        PSEventSetFilter(PSE_INSTANCE_HANDLEMESSAGE)
        cdef PSEvent *event = NULL
        t1 = time.time()
        cdef int ntries = <int> ceil(timeout * 1000000.0 / sleeptime)
        with nogil:
            while ntries > 0:
                event = PSEventTryAcquire()
                # Wait a bit so we aren't constantly spinning
                posix.unistd.usleep(sleeptime)
                if event != NULL:
                    if event.type != PSE_INSTANCE_HANDLEMESSAGE:
                        event = NULL
                    break
                ntries -= 1

        if event == NULL: return
        
        cdef Var message = Var(event.as_var)
        cdef Resource res
        cdef PP_Resource pp_res
        # We special-case a filesystem.
        rv = convert_from_var(message)
        # Now we manage our local event handling.
        if isinstance(rv, dict) and 'filesystem_name' in rv:
            fs_name = os.path.basename(rv['filesystem_name'])
            fs_res = rv['filesystem_resource']['filesystem_resource']
            self.filesystem_resources[fs_name] = fs_res
            # Now we will automount if appropriate.
            if self.automount:
                dest = os.path.join("/mnt", fs_name)
                if not os.path.exists(dest):
                    os.makedirs(dest)
                rv = self.mount("", dest, "html5fs", 0,
                    "SOURCE=%s,filesystem_resource=%s" % (fs_name, fs_res))
                print "Mounted %s as %s" % (fs_name, dest)
            return None
        PSEventRelease(event)
        return rv

cdef Var _map_np_to_vararraybuffer(np.ndarray[any_np_type, ndim=1] src):
    cdef uint32_t arr_size = src.dtype.itemsize * src.size
    cdef VarArrayBuffer vba = VarArrayBuffer(arr_size)
    cdef any_np_type* arr = <any_np_type *> vba.Map()
    cdef int i
    for i in range(src.size):
        arr[i] = src[i]
    return vba

cdef Var ndarray_to_var(np.ndarray array):
    # This actually creates a VarDictionary with the array spec
    cdef VarDictionary vd = VarDictionary()
    cdef Var vba
    cdef char *key, *val, *array_type
    # Specify type
    key = "__isarray__"
    vd.Set(Var(key), Var(bTrue))
    # Shape parameter
    cdef VarArray shape = VarArray()
    shape.SetLength(1)
    shape.Set(0, Var(<int32_t> array.size))
    key = "shape"
    vd.Set(Var(key), shape)
    # Action, which currently is always None
    key = "action"
    val = "None"
    vd.Set(Var(key), Var(val))
    # Now the actual data and array type
    if array.dtype == np.int8:
        array_type = "Int8"
        vba = _map_np_to_vararraybuffer[np.int8_t](array)
    elif array.dtype == np.uint8:
        array_type = "Uint8"
        vba = _map_np_to_vararraybuffer[np.uint8_t](array)
    elif array.dtype == np.int16:
        array_type = "Int16"
        vba = _map_np_to_vararraybuffer[np.int16_t](array)
    elif array.dtype == np.uint16:
        array_type = "Uint16"
        vba = _map_np_to_vararraybuffer[np.uint16_t](array)
    elif array.dtype == np.int32:
        array_type = "Int32"
        vba = _map_np_to_vararraybuffer[np.int32_t](array)
    elif array.dtype == np.uint32:
        array_type = "Uint32"
        vba = _map_np_to_vararraybuffer[np.uint32_t](array)
    elif array.dtype == np.float32:
        array_type = "Float32"
        vba = _map_np_to_vararraybuffer[np.float32_t](array)
    elif array.dtype == np.float64:
        array_type = "Float64"
        vba = _map_np_to_vararraybuffer[np.float64_t](array)
    else:
        raise NotImplementedError
    key = "array_type"
    vd.Set(Var(key), Var(array_type))
    key = "data"
    vd.Set(Var(key), vba)
    return vd

cdef Var convert_to_var(obj):
    # We have dispatchers for various types of data types
    cdef uint32_t i, size
    cdef int32_t iv
    cdef double dv
    cdef char* stype
    cdef Var v, vk, vv
    cdef VarDictionary vd
    cdef VarArray va
    if isinstance(obj, dict):
        # This may not work if the keys are not all strings
        for key in obj:
            vk = convert_to_var(key)
            vv = convert_to_var(obj[key])
            vd.Set(vk, vv)
        v = vd
    elif obj is True:
        v = Var(bTrue)
    elif obj is False:
        v = Var(bFalse)
    elif isinstance(obj, types.StringTypes):
        stype = obj
        v = Var(stype)
    elif isinstance(obj, np.ndarray):
        v = ndarray_to_var(obj)
    elif isinstance(obj, (tuple, list)):
        size = len(obj)
        va.SetLength(size)
        for i in range(size):
            va.Set(i, convert_to_var(obj[i]))
        v = va
    elif isinstance(obj, (int, long)):
        iv = obj
        v = Var(iv)
    elif isinstance(obj, float):
        dv = obj
        v = Var(dv)
    else:
        raise NotImplementedError(type(obj))
    return v

cdef object convert_from_var(Var var):
    cdef uint32_t i, size
    cdef int32_t iv
    cdef double dv
    cdef char* stype
    cdef bool bv
    cdef object rv
    cdef Var v, vk, vv
    cdef VarDictionary vd
    cdef VarArray va
    cdef Resource res
    cdef PP_Resource pp_res
    if var.is_undefined():
        rv = None
    elif var.is_null():
        rv = None
    elif var.is_bool():
        rv = var.AsBool()
    elif var.is_string():
        rv = var.AsString()
    elif var.is_int():
        rv = var.AsInt()
    elif var.is_double():
        rv = var.AsDouble()
    elif var.is_array():
        va = VarArray(var)
        size = va.GetLength()
        rv = []
        for i in range(size):
            vv = va.Get(i)
            t = convert_from_var(vv)
            rv.append(convert_from_var(vv))
    elif var.is_dictionary():
        # We get our keys, convert them, and then iterate.
        vd = VarDictionary(var)
        va = vd.GetKeys()
        size = va.GetLength()
        rv = {}
        for i in range(size):
            vk = va.Get(i)
            vv = vd.Get(vk)
            rv[convert_from_var(vk)] = convert_from_var(vv)
    elif var.is_object():
        raise NotImplementedError
    elif var.is_array_buffer():
        raise NotImplementedError
    elif var.is_resource():
        # This is where we catch things we know about.
        res = var.AsResource()
        if IsFileSystem(res):
            pp_res = res.pp_resource()
            rv = {'filesystem_resource': pp_res}
        else:
            raise NotImplementedError
    else:
        raise RuntimeError
    return rv
