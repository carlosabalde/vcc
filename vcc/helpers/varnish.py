# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import ctypes


class VSL(object):
    def arg(self, arg, opt='\0'):
        raise NotImplementedError('Please implement this method.')

    def open(self, nb=0):
        raise NotImplementedError('Please implement this method.')

    def reopen(self, diag=0):
        raise NotImplementedError('Please implement this method.')

    def dispatch(self, func):
        raise NotImplementedError('Please implement this method.')


class VSL3(VSL):
    # See VSL_handler_f typedef (include/varnishapi.h).
    HANDLER_F = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,    # priv.
        ctypes.c_int,       # tag.
        ctypes.c_uint,      # fd.
        ctypes.c_uint,      # len.
        ctypes.c_uint,      # spec.
        ctypes.c_char_p,    # ptr.
        ctypes.c_ulonglong  # bitmap.
    )

    def __init__(self, lib):
        self.__lib = ctypes.cdll[lib]
        self.__vd = self.__lib.VSM_New()
        self.__lib.VSL_Setup(self.__vd)

    def arg(self, arg, opt='\0'):
        return self.__lib.VSL_Arg(self.__vd, ord(arg), opt)

    def open(self, nb=0):
        self.__lib.VSL_Open(self.__vd, 1)
        self.__lib.VSL_NonBlocking(self.__vd, nb)

    def reopen(self, diag=0):
        return self.__lib.VSM_ReOpen(self.__vd, diag)

    def dispatch(self, func):
        cb_func = VSL3.HANDLER_F(func)
        self.__lib.VSL_Dispatch(self.__vd, cb_func, self.__vd)
