"""
    Mosek/Python Module. An Python interface to Mosek.

    Copyright (c) MOSEK ApS, Denmark. All rights reserved.
"""


import weakref
import threading
import re
import platform
import os
import pathlib
try:
    import numpy
except ImportError:
    raise ImportError('Mosek module requires numpy (http://www.numpy.org/)')
try:
    import ctypes
except ImportError:
    raise ImportError('Mosek module requires ctypes')

try:
    from mosek.mosekorigin import __mosekinstpath__
except ImportError:
    __mosekinstpath__ = None

# Due to a bug in some python versions, lookup may fail in a multithreaded context if not preloaded.
import codecs
codecs.lookup('utf-8')

class TypeAcceptError(Exception):
    pass

class MSKException(Exception):
    pass
class MosekException(MSKException):
    def __init__(self,res,msg):
        MSKException.__init__(self,msg)
        self.msg   = msg
        self.errno = res
    def __str__(self):
        return "%s(%d): %s" % (str(self.errno), self.errno, self.msg)

class Error(MosekException):
    pass

class EnumBase(int):
    """
    Base class for enums.
    """
    enumnamere = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*$')
    def __new__(cls,value):
        if isinstance(value,int):
            return cls._valdict[value]
        elif isinstance(value,str):
            return cls._namedict[value.split('.')[-1]]
        else:
            raise TypeError("Invalid type for enum construction (%s)" % value)
    def __str__(self):
        return '%s.%s' % (self.__class__.__name__,self.__name__)
    def __repr__(self):
        return self.__name__

    @classmethod
    def members(cls):
        return iter(cls._values)

    @classmethod
    def _initialize(cls, names,values=None):
        for n in names:
            if not cls.enumnamere.match(n):
                raise ValueError("Invalid enum item name '%s' in %s" % (n,cls.__name__))
        if values is None:
            values = range(len(names))
        if len(values) != len(names):
            raise ValueError("Lengths of names and values do not match")

        items = []
        for (n,v) in zip(names,values):
            item = int.__new__(cls,v)
            item.__name__ = n
            setattr(cls,n,item)
            items.append(item)

        cls._values   = items
        cls.values    = items
        cls._namedict = dict([ (v.__name__,v) for v in items ])
        cls._valdict  = dict([ (v,v) for v in items ]) # map int -> enum value (sneaky, eh?)


def Enum(name,names,values=None):
    """
    Create a new enum class with the given names and values.

    Parameters:
     [name]   A string denoting the name of the enum.
     [names]  A list of strings denoting the names of the individual enum values.
     [values] (optional) A list of integer values of the enums. If given, the
       list must have same length as the [names] parameter. If not given, the
       default values 0, 1, ... will be used.
    """
    e = type(name,(EnumBase,),{})
    e._initialize(names,values)
    return e

# module initialization
import platform
if platform.system() == 'Windows':
    __library_factory__ = ctypes.WinDLL
    __callback_factory__ = ctypes.WINFUNCTYPE # stdcall
elif platform.system() in [ 'Darwin', 'Linux' ]:
    __library_factory__ = ctypes.CDLL
    __callback_factory__ = ctypes.CFUNCTYPE # cdecl


def loadmosek(vmajor,vminor):
    __libname = None#__makelibname(libbasename)
    ptrsize   = ctypes.sizeof(ctypes.c_void_p) # figure out if python is 32bit or 64bit
    bits,pf = platform.architecture()
    arch    = platform.machine()

    if platform.system() == 'Windows':
        if arch not in ['x86_64','AMD64']:
            assert False, "Platform not supported"
        if   bits == '64bit':
            pfname = 'win64x86'
            __libname = f'mosek64_{vmajor}_{vminor}.dll'
        elif bits == '32bit':
            pfname = 'win32x86'
            __libname = f'mosek{vmajor}_{vminor}.dll'
        else:
            assert False, "Platform not supported"
    elif platform.system() == 'Darwin':
        if   bits == '64bit':
            if arch in ['x86_64','AMD64']:
                pfname = 'osx64x86'
            elif arch in ['arm64']:
                pfname = 'osxaarch64'
            else:
                assert False, "Platform not supported"
        else:
            assert False, "Platform not supported"
        __libname = f'libmosek64.{vmajor}.{vminor}.dylib'
    elif platform.system() == 'Linux':
        if   bits == '64bit':
            if arch in ['x86_64','AMD64']:
                pfname = 'linux64x86'
            elif arch in ['aarch64']:
                pfname = 'linuxaarch64'
            else:
                assert False, "Platform not supported"
        else:
            assert False, "Platform not supported"
        __libname = f'libmosek64.so.{vmajor}.{vminor}'
    else:
        raise ImportError("Unsupported system or architecture")

    if platform.system() == 'Windows':
        kernel32 = ctypes.WinDLL('Kernel32')
        kernel32.GetDllDirectoryA.argtypes = [ ctypes.c_int32, ctypes.c_char_p ]
        kernel32.GetDllDirectoryA.restype  = ctypes.c_int32
        kernel32.SetDllDirectoryA.argtypes = [ ctypes.c_char_p ]
        kernel32.SetDllDirectoryA.restype  = ctypes.c_int32

    dlldirs = [ ]
    if __mosekinstpath__ is not None:
        dlldirs.append(os.path.join(__mosekinstpath__))

    library = None
    libdir  = None
    liberr = []
    currdir = os.getcwd()
    for dlldir in dlldirs:
        try:
            os.chdir(dlldir)
            library = __library_factory__(str(pathlib.Path(dlldir).joinpath(__libname)))
            libdir = dlldir
            break
        except OSError as e:
            liberr.append(dlldir)
    os.chdir(currdir)
   
    if library is None:
        # attempt to load from using global path settings
        try:
            library = __library_factory__(__libname)
        except OSError as e:
            liberr.append('PATH')

    if library is None:    
        raise ImportError(f'Failed to import dll "{__libname}" from {liberr}')

    return library,libdir


_mosek_major_ver = 10
_mosek_minor_ver = 0
__library__,__dlldir__ = loadmosek(_mosek_major_ver,_mosek_minor_ver)

__progress_cb_type__ = __callback_factory__(ctypes.c_int,  # return int
                                            ctypes.POINTER(ctypes.c_void_p), # task
                                            ctypes.c_void_p,  # handle
                                            ctypes.c_int,  # caller
                                            ctypes.c_void_p,#ctypes.POINTER(ctypes.c_double),  # dinf
                                            ctypes.c_void_p,#ctypes.POINTER(ctypes.c_int), # iinf
                                            ctypes.c_void_p,#ctypes.POINTER(ctypes.c_longlong))# liinf
                                        )

__stream_cb_type__   = __callback_factory__(None, ctypes.c_void_p, ctypes.c_char_p)

__write_cb_type__   = __callback_factory__(ctypes.c_size_t,
                                           ctypes.c_void_p,    # handle
                                           ctypes.c_void_p,    # data
                                           ctypes.c_size_t)    # count

__library__.MSK_makeenv.restype      =   ctypes.c_int
__library__.MSK_makeenv.argtypes     = [ ctypes.POINTER(ctypes.c_void_p),
                                         ctypes.c_char_p ]
__library__.MSK_deleteenv.argtypes   = [ ctypes.POINTER(ctypes.c_void_p) ] # envp
__library__.MSK_deleteenv.restype    =   ctypes.c_int
__library__.MSK_maketask.argtypes    = [ ctypes.c_void_p,# env
                                         ctypes.c_int, # maxnumcon
                                         ctypes.c_int, # maxnumvar
                                         ctypes.POINTER(ctypes.c_void_p)] # taskp
__library__.MSK_maketask.restype     =   ctypes.c_int
__library__.MSK_deletetask.argtypes  = [ ctypes.POINTER(ctypes.c_void_p) ] # envp
__library__.MSK_deletetask.restype   =   ctypes.c_int
__library__.MSK_putcallbackfunc.argtypes      = [ ctypes.c_void_p, __progress_cb_type__, ctypes.c_void_p ]
__library__.MSK_putcallbackfunc.restype       =   ctypes.c_int
__library__.MSK_linkfunctotaskstream.argtypes = [ ctypes.c_void_p,    # task 
                                                  ctypes.c_int,       # whichstream
                                                  ctypes.c_void_p,    # handle
                                                  __stream_cb_type__ ] # func
__library__.MSK_linkfunctotaskstream.restype  =   ctypes.c_int
__library__.MSK_linkfunctoenvstream.argtypes  = [ ctypes.c_void_p,    # env 
                                                  ctypes.c_int,       # whichstream
                                                  ctypes.c_void_p,    # handle
                                                  __stream_cb_type__ ] # func
__library__.MSK_linkfunctoenvstream.restype   =   ctypes.c_int
__library__.MSK_clonetask.restype     = ctypes.c_int
__library__.MSK_clonetask.argtypes    = [ ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p) ]
__library__.MSK_getlasterror64.restype  = ctypes.c_int
__library__.MSK_getlasterror64.argtypes = [ ctypes.c_void_p, # task
                                          ctypes.POINTER(ctypes.c_int), # lastrescode
                                          ctypes.c_int64, # maxlen
                                          ctypes.POINTER(ctypes.c_int64), # msg len
                                          ctypes.c_char_p, ] # msg
__library__.MSK_putresponsefunc.restype  = ctypes.c_int
__library__.MSK_putresponsefunc.argtypes = [ ctypes.c_void_p,  # task
                                             ctypes.c_void_p,  # func
                                             ctypes.c_void_p ] # handle
__library__.MSK_enablegarcolenv.argtypes = [ ctypes.c_void_p ] 
__library__.MSK_enablegarcolenv.restype  =   ctypes.c_int 

__library__.MSK_freeenv.restype  = None
__library__.MSK_freeenv.argtypes  = [ ctypes.c_void_p, ctypes.c_void_p ]

__library__.MSK_freetask.restype  = None
__library__.MSK_freetask.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]

__library__.MSK_writedatahandle.restype   = ctypes.c_int
__library__.MSK_writedatahandle.argtypes  = [ ctypes.c_void_p,     # task
                                              __write_cb_type__,   # func,
                                              ctypes.c_void_p,     # handle
                                              ctypes.c_int,        # format
                                              ctypes.c_int ]       # compress

__library__.MSK_analyzeproblem.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_analyzeproblem.restype = ctypes.c_int32
__library__.MSK_analyzenames.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_analyzenames.restype = ctypes.c_int32
__library__.MSK_analyzesolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_analyzesolution.restype = ctypes.c_int32
__library__.MSK_initbasissolve.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_initbasissolve.restype = ctypes.c_int32
__library__.MSK_solvewithbasis.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_solvewithbasis.restype = ctypes.c_int32
__library__.MSK_basiscond.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_basiscond.restype = ctypes.c_int32
__library__.MSK_appendcons.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_appendcons.restype = ctypes.c_int32
__library__.MSK_appendvars.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_appendvars.restype = ctypes.c_int32
__library__.MSK_removecons.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_removecons.restype = ctypes.c_int32
__library__.MSK_removevars.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_removevars.restype = ctypes.c_int32
__library__.MSK_removebarvars.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_removebarvars.restype = ctypes.c_int32
__library__.MSK_removecones.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_removecones.restype = ctypes.c_int32
__library__.MSK_appendbarvars.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_appendbarvars.restype = ctypes.c_int32
__library__.MSK_appendcone.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_appendcone.restype = ctypes.c_int32
__library__.MSK_appendconeseq.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_appendconeseq.restype = ctypes.c_int32
__library__.MSK_appendconesseq.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32),ctypes.c_int32 ]
__library__.MSK_appendconesseq.restype = ctypes.c_int32
__library__.MSK_chgconbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_chgconbound.restype = ctypes.c_int32
__library__.MSK_chgvarbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_chgvarbound.restype = ctypes.c_int32
__library__.MSK_getaij.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaij.restype = ctypes.c_int32
__library__.MSK_getapiecenumnz.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getapiecenumnz.restype = ctypes.c_int32
__library__.MSK_getacolnumnz.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getacolnumnz.restype = ctypes.c_int32
__library__.MSK_getacol.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getacol.restype = ctypes.c_int32
__library__.MSK_getacolslice64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getacolslice64.restype = ctypes.c_int32
__library__.MSK_getarownumnz.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getarownumnz.restype = ctypes.c_int32
__library__.MSK_getarow.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getarow.restype = ctypes.c_int32
__library__.MSK_getacolslicenumnz64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getacolslicenumnz64.restype = ctypes.c_int32
__library__.MSK_getarowslicenumnz64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getarowslicenumnz64.restype = ctypes.c_int32
__library__.MSK_getarowslice64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getarowslice64.restype = ctypes.c_int32
__library__.MSK_getatrip.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getatrip.restype = ctypes.c_int32
__library__.MSK_getarowslicetrip.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getarowslicetrip.restype = ctypes.c_int32
__library__.MSK_getacolslicetrip.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getacolslicetrip.restype = ctypes.c_int32
__library__.MSK_getconbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getconbound.restype = ctypes.c_int32
__library__.MSK_getvarbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getvarbound.restype = ctypes.c_int32
__library__.MSK_getconboundslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getconboundslice.restype = ctypes.c_int32
__library__.MSK_getvarboundslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getvarboundslice.restype = ctypes.c_int32
__library__.MSK_getcj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getcj.restype = ctypes.c_int32
__library__.MSK_getc.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getc.restype = ctypes.c_int32
__library__.MSK_getcfix.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getcfix.restype = ctypes.c_int32
__library__.MSK_getcone.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getcone.restype = ctypes.c_int32
__library__.MSK_getconeinfo.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getconeinfo.restype = ctypes.c_int32
__library__.MSK_getclist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getclist.restype = ctypes.c_int32
__library__.MSK_getcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getcslice.restype = ctypes.c_int32
__library__.MSK_getdouinf.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdouinf.restype = ctypes.c_int32
__library__.MSK_getdouparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdouparam.restype = ctypes.c_int32
__library__.MSK_getdualobj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdualobj.restype = ctypes.c_int32
__library__.MSK_getintinf.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getintinf.restype = ctypes.c_int32
__library__.MSK_getlintinf.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getlintinf.restype = ctypes.c_int32
__library__.MSK_getintparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getintparam.restype = ctypes.c_int32
__library__.MSK_getmaxnumanz64.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getmaxnumanz64.restype = ctypes.c_int32
__library__.MSK_getmaxnumcon.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getmaxnumcon.restype = ctypes.c_int32
__library__.MSK_getmaxnumvar.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getmaxnumvar.restype = ctypes.c_int32
__library__.MSK_getbarvarnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getbarvarnamelen.restype = ctypes.c_int32
__library__.MSK_getbarvarname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getbarvarname.restype = ctypes.c_int32
__library__.MSK_getbarvarnameindex.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getbarvarnameindex.restype = ctypes.c_int32
__library__.MSK_generatebarvarnames.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generatebarvarnames.restype = ctypes.c_int32
__library__.MSK_generatevarnames.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generatevarnames.restype = ctypes.c_int32
__library__.MSK_generateconnames.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generateconnames.restype = ctypes.c_int32
__library__.MSK_generateconenames.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generateconenames.restype = ctypes.c_int32
__library__.MSK_generateaccnames.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generateaccnames.restype = ctypes.c_int32
__library__.MSK_generatedjcnames.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_char_p,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int64,ctypes.POINTER(ctypes.c_char_p) ]
__library__.MSK_generatedjcnames.restype = ctypes.c_int32
__library__.MSK_putconname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_putconname.restype = ctypes.c_int32
__library__.MSK_putvarname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_putvarname.restype = ctypes.c_int32
__library__.MSK_putconename.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_putconename.restype = ctypes.c_int32
__library__.MSK_putbarvarname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_putbarvarname.restype = ctypes.c_int32
__library__.MSK_putdomainname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_char_p ]
__library__.MSK_putdomainname.restype = ctypes.c_int32
__library__.MSK_putdjcname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_char_p ]
__library__.MSK_putdjcname.restype = ctypes.c_int32
__library__.MSK_putaccname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_char_p ]
__library__.MSK_putaccname.restype = ctypes.c_int32
__library__.MSK_getvarnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getvarnamelen.restype = ctypes.c_int32
__library__.MSK_getvarname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getvarname.restype = ctypes.c_int32
__library__.MSK_getconnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getconnamelen.restype = ctypes.c_int32
__library__.MSK_getconname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getconname.restype = ctypes.c_int32
__library__.MSK_getconnameindex.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getconnameindex.restype = ctypes.c_int32
__library__.MSK_getvarnameindex.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getvarnameindex.restype = ctypes.c_int32
__library__.MSK_getconenamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getconenamelen.restype = ctypes.c_int32
__library__.MSK_getconename.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getconename.restype = ctypes.c_int32
__library__.MSK_getconenameindex.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getconenameindex.restype = ctypes.c_int32
__library__.MSK_getdomainnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getdomainnamelen.restype = ctypes.c_int32
__library__.MSK_getdomainname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getdomainname.restype = ctypes.c_int32
__library__.MSK_getdjcnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getdjcnamelen.restype = ctypes.c_int32
__library__.MSK_getdjcname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getdjcname.restype = ctypes.c_int32
__library__.MSK_getaccnamelen.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getaccnamelen.restype = ctypes.c_int32
__library__.MSK_getaccname.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getaccname.restype = ctypes.c_int32
__library__.MSK_getnumanz.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumanz.restype = ctypes.c_int32
__library__.MSK_getnumanz64.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumanz64.restype = ctypes.c_int32
__library__.MSK_getnumcon.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumcon.restype = ctypes.c_int32
__library__.MSK_getnumcone.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumcone.restype = ctypes.c_int32
__library__.MSK_getnumconemem.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumconemem.restype = ctypes.c_int32
__library__.MSK_getnumintvar.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumintvar.restype = ctypes.c_int32
__library__.MSK_getnumparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumparam.restype = ctypes.c_int32
__library__.MSK_getnumqconknz64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumqconknz64.restype = ctypes.c_int32
__library__.MSK_getnumqobjnz64.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumqobjnz64.restype = ctypes.c_int32
__library__.MSK_getnumvar.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumvar.restype = ctypes.c_int32
__library__.MSK_getnumbarvar.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getnumbarvar.restype = ctypes.c_int32
__library__.MSK_getmaxnumbarvar.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getmaxnumbarvar.restype = ctypes.c_int32
__library__.MSK_getdimbarvarj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getdimbarvarj.restype = ctypes.c_int32
__library__.MSK_getlenbarvarj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getlenbarvarj.restype = ctypes.c_int32
__library__.MSK_getobjname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getobjname.restype = ctypes.c_int32
__library__.MSK_getobjnamelen.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getobjnamelen.restype = ctypes.c_int32
__library__.MSK_getprimalobj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getprimalobj.restype = ctypes.c_int32
__library__.MSK_getprobtype.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getprobtype.restype = ctypes.c_int32
__library__.MSK_getqconk64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getqconk64.restype = ctypes.c_int32
__library__.MSK_getqobj64.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getqobj64.restype = ctypes.c_int32
__library__.MSK_getqobjij.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getqobjij.restype = ctypes.c_int32
__library__.MSK_getsolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsolution.restype = ctypes.c_int32
__library__.MSK_getsolutionnew.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsolutionnew.restype = ctypes.c_int32
__library__.MSK_getsolsta.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getsolsta.restype = ctypes.c_int32
__library__.MSK_getprosta.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getprosta.restype = ctypes.c_int32
__library__.MSK_getskc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getskc.restype = ctypes.c_int32
__library__.MSK_getskx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getskx.restype = ctypes.c_int32
__library__.MSK_getskn.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getskn.restype = ctypes.c_int32
__library__.MSK_getxc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getxc.restype = ctypes.c_int32
__library__.MSK_getxx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getxx.restype = ctypes.c_int32
__library__.MSK_gety.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_gety.restype = ctypes.c_int32
__library__.MSK_getslc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getslc.restype = ctypes.c_int32
__library__.MSK_getaccdoty.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccdoty.restype = ctypes.c_int32
__library__.MSK_getaccdotys.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccdotys.restype = ctypes.c_int32
__library__.MSK_evaluateacc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_evaluateacc.restype = ctypes.c_int32
__library__.MSK_evaluateaccs.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_evaluateaccs.restype = ctypes.c_int32
__library__.MSK_getsuc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsuc.restype = ctypes.c_int32
__library__.MSK_getslx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getslx.restype = ctypes.c_int32
__library__.MSK_getsux.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsux.restype = ctypes.c_int32
__library__.MSK_getsnx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsnx.restype = ctypes.c_int32
__library__.MSK_getskcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getskcslice.restype = ctypes.c_int32
__library__.MSK_getskxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getskxslice.restype = ctypes.c_int32
__library__.MSK_getxcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getxcslice.restype = ctypes.c_int32
__library__.MSK_getxxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getxxslice.restype = ctypes.c_int32
__library__.MSK_getyslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getyslice.restype = ctypes.c_int32
__library__.MSK_getslcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getslcslice.restype = ctypes.c_int32
__library__.MSK_getsucslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsucslice.restype = ctypes.c_int32
__library__.MSK_getslxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getslxslice.restype = ctypes.c_int32
__library__.MSK_getsuxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsuxslice.restype = ctypes.c_int32
__library__.MSK_getsnxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsnxslice.restype = ctypes.c_int32
__library__.MSK_getbarxj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarxj.restype = ctypes.c_int32
__library__.MSK_getbarxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarxslice.restype = ctypes.c_int32
__library__.MSK_getbarsj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarsj.restype = ctypes.c_int32
__library__.MSK_getbarsslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarsslice.restype = ctypes.c_int32
__library__.MSK_putskc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putskc.restype = ctypes.c_int32
__library__.MSK_putskx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putskx.restype = ctypes.c_int32
__library__.MSK_putxc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putxc.restype = ctypes.c_int32
__library__.MSK_putxx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putxx.restype = ctypes.c_int32
__library__.MSK_puty.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_puty.restype = ctypes.c_int32
__library__.MSK_putslc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putslc.restype = ctypes.c_int32
__library__.MSK_putsuc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsuc.restype = ctypes.c_int32
__library__.MSK_putslx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putslx.restype = ctypes.c_int32
__library__.MSK_putsux.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsux.restype = ctypes.c_int32
__library__.MSK_putsnx.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsnx.restype = ctypes.c_int32
__library__.MSK_putaccdoty.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putaccdoty.restype = ctypes.c_int32
__library__.MSK_putskcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putskcslice.restype = ctypes.c_int32
__library__.MSK_putskxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putskxslice.restype = ctypes.c_int32
__library__.MSK_putxcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putxcslice.restype = ctypes.c_int32
__library__.MSK_putxxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putxxslice.restype = ctypes.c_int32
__library__.MSK_putyslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putyslice.restype = ctypes.c_int32
__library__.MSK_putslcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putslcslice.restype = ctypes.c_int32
__library__.MSK_putsucslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsucslice.restype = ctypes.c_int32
__library__.MSK_putslxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putslxslice.restype = ctypes.c_int32
__library__.MSK_putsuxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsuxslice.restype = ctypes.c_int32
__library__.MSK_putsnxslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsnxslice.restype = ctypes.c_int32
__library__.MSK_putbarxj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbarxj.restype = ctypes.c_int32
__library__.MSK_putbarsj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbarsj.restype = ctypes.c_int32
__library__.MSK_getpviolcon.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpviolcon.restype = ctypes.c_int32
__library__.MSK_getpviolvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpviolvar.restype = ctypes.c_int32
__library__.MSK_getpviolbarvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpviolbarvar.restype = ctypes.c_int32
__library__.MSK_getpviolcones.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpviolcones.restype = ctypes.c_int32
__library__.MSK_getpviolacc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpviolacc.restype = ctypes.c_int32
__library__.MSK_getpvioldjc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpvioldjc.restype = ctypes.c_int32
__library__.MSK_getdviolcon.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdviolcon.restype = ctypes.c_int32
__library__.MSK_getdviolvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdviolvar.restype = ctypes.c_int32
__library__.MSK_getdviolbarvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdviolbarvar.restype = ctypes.c_int32
__library__.MSK_getdviolcones.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdviolcones.restype = ctypes.c_int32
__library__.MSK_getdviolacc.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdviolacc.restype = ctypes.c_int32
__library__.MSK_getsolutioninfo.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsolutioninfo.restype = ctypes.c_int32
__library__.MSK_getsolutioninfonew.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsolutioninfonew.restype = ctypes.c_int32
__library__.MSK_getdualsolutionnorms.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdualsolutionnorms.restype = ctypes.c_int32
__library__.MSK_getprimalsolutionnorms.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getprimalsolutionnorms.restype = ctypes.c_int32
__library__.MSK_getsolutionslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsolutionslice.restype = ctypes.c_int32
__library__.MSK_getreducedcosts.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getreducedcosts.restype = ctypes.c_int32
__library__.MSK_getstrparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getstrparam.restype = ctypes.c_int32
__library__.MSK_getstrparamlen.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getstrparamlen.restype = ctypes.c_int32
__library__.MSK_gettasknamelen.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_gettasknamelen.restype = ctypes.c_int32
__library__.MSK_gettaskname.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_gettaskname.restype = ctypes.c_int32
__library__.MSK_getvartype.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getvartype.restype = ctypes.c_int32
__library__.MSK_getvartypelist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getvartypelist.restype = ctypes.c_int32
__library__.MSK_inputdata64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.c_double,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_inputdata64.restype = ctypes.c_int32
__library__.MSK_isdouparname.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_isdouparname.restype = ctypes.c_int32
__library__.MSK_isintparname.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_isintparname.restype = ctypes.c_int32
__library__.MSK_isstrparname.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_isstrparname.restype = ctypes.c_int32
__library__.MSK_linkfiletotaskstream.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_linkfiletotaskstream.restype = ctypes.c_int32
__library__.MSK_primalrepair.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_primalrepair.restype = ctypes.c_int32
__library__.MSK_infeasibilityreport.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_infeasibilityreport.restype = ctypes.c_int32
__library__.MSK_toconic.argtypes = [ ctypes.c_voidp ]
__library__.MSK_toconic.restype = ctypes.c_int32
__library__.MSK_optimizetrm.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_optimizetrm.restype = ctypes.c_int32
__library__.MSK_commitchanges.argtypes = [ ctypes.c_voidp ]
__library__.MSK_commitchanges.restype = ctypes.c_int32
__library__.MSK_getatruncatetol.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getatruncatetol.restype = ctypes.c_int32
__library__.MSK_putatruncatetol.argtypes = [ ctypes.c_voidp,ctypes.c_double ]
__library__.MSK_putatruncatetol.restype = ctypes.c_int32
__library__.MSK_putaij.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putaij.restype = ctypes.c_int32
__library__.MSK_putaijlist64.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putaijlist64.restype = ctypes.c_int32
__library__.MSK_putacol.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putacol.restype = ctypes.c_int32
__library__.MSK_putarow.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putarow.restype = ctypes.c_int32
__library__.MSK_putarowslice64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putarowslice64.restype = ctypes.c_int32
__library__.MSK_putarowlist64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putarowlist64.restype = ctypes.c_int32
__library__.MSK_putacolslice64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putacolslice64.restype = ctypes.c_int32
__library__.MSK_putacollist64.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putacollist64.restype = ctypes.c_int32
__library__.MSK_putbaraij.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbaraij.restype = ctypes.c_int32
__library__.MSK_putbaraijlist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbaraijlist.restype = ctypes.c_int32
__library__.MSK_putbararowlist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbararowlist.restype = ctypes.c_int32
__library__.MSK_getnumbarcnz.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumbarcnz.restype = ctypes.c_int32
__library__.MSK_getnumbaranz.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumbaranz.restype = ctypes.c_int32
__library__.MSK_getbarcsparsity.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getbarcsparsity.restype = ctypes.c_int32
__library__.MSK_getbarasparsity.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getbarasparsity.restype = ctypes.c_int32
__library__.MSK_getbarcidxinfo.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getbarcidxinfo.restype = ctypes.c_int32
__library__.MSK_getbarcidxj.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getbarcidxj.restype = ctypes.c_int32
__library__.MSK_getbarcidx.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarcidx.restype = ctypes.c_int32
__library__.MSK_getbaraidxinfo.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getbaraidxinfo.restype = ctypes.c_int32
__library__.MSK_getbaraidxij.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getbaraidxij.restype = ctypes.c_int32
__library__.MSK_getbaraidx.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbaraidx.restype = ctypes.c_int32
__library__.MSK_getnumbarcblocktriplets.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumbarcblocktriplets.restype = ctypes.c_int32
__library__.MSK_putbarcblocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbarcblocktriplet.restype = ctypes.c_int32
__library__.MSK_getbarcblocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarcblocktriplet.restype = ctypes.c_int32
__library__.MSK_putbarablocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbarablocktriplet.restype = ctypes.c_int32
__library__.MSK_getnumbarablocktriplets.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumbarablocktriplets.restype = ctypes.c_int32
__library__.MSK_getbarablocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getbarablocktriplet.restype = ctypes.c_int32
__library__.MSK_putmaxnumafe.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumafe.restype = ctypes.c_int32
__library__.MSK_getnumafe.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumafe.restype = ctypes.c_int32
__library__.MSK_appendafes.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_appendafes.restype = ctypes.c_int32
__library__.MSK_putafefentry.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putafefentry.restype = ctypes.c_int32
__library__.MSK_putafefentrylist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafefentrylist.restype = ctypes.c_int32
__library__.MSK_emptyafefrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_emptyafefrow.restype = ctypes.c_int32
__library__.MSK_emptyafefcol.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_emptyafefcol.restype = ctypes.c_int32
__library__.MSK_emptyafefrowlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_emptyafefrowlist.restype = ctypes.c_int32
__library__.MSK_emptyafefcollist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_emptyafefcollist.restype = ctypes.c_int32
__library__.MSK_putafefrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafefrow.restype = ctypes.c_int32
__library__.MSK_putafefrowlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafefrowlist.restype = ctypes.c_int32
__library__.MSK_putafefcol.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafefcol.restype = ctypes.c_int32
__library__.MSK_getafefrownumnz.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getafefrownumnz.restype = ctypes.c_int32
__library__.MSK_getafefnumnz.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getafefnumnz.restype = ctypes.c_int32
__library__.MSK_getafefrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafefrow.restype = ctypes.c_int32
__library__.MSK_getafeftrip.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafeftrip.restype = ctypes.c_int32
__library__.MSK_putafebarfentry.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafebarfentry.restype = ctypes.c_int32
__library__.MSK_putafebarfentrylist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafebarfentrylist.restype = ctypes.c_int32
__library__.MSK_putafebarfrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafebarfrow.restype = ctypes.c_int32
__library__.MSK_emptyafebarfrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_emptyafebarfrow.restype = ctypes.c_int32
__library__.MSK_emptyafebarfrowlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_emptyafebarfrowlist.restype = ctypes.c_int32
__library__.MSK_putafebarfblocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafebarfblocktriplet.restype = ctypes.c_int32
__library__.MSK_getafebarfnumblocktriplets.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getafebarfnumblocktriplets.restype = ctypes.c_int32
__library__.MSK_getafebarfblocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafebarfblocktriplet.restype = ctypes.c_int32
__library__.MSK_getafebarfnumrowentries.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getafebarfnumrowentries.restype = ctypes.c_int32
__library__.MSK_getafebarfrowinfo.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getafebarfrowinfo.restype = ctypes.c_int32
__library__.MSK_getafebarfrow.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafebarfrow.restype = ctypes.c_int32
__library__.MSK_putafeg.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_double ]
__library__.MSK_putafeg.restype = ctypes.c_int32
__library__.MSK_putafeglist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafeglist.restype = ctypes.c_int32
__library__.MSK_getafeg.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafeg.restype = ctypes.c_int32
__library__.MSK_getafegslice.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getafegslice.restype = ctypes.c_int32
__library__.MSK_putafegslice.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putafegslice.restype = ctypes.c_int32
__library__.MSK_putmaxnumdjc.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumdjc.restype = ctypes.c_int32
__library__.MSK_getnumdjc.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumdjc.restype = ctypes.c_int32
__library__.MSK_getdjcnumdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumdomain.restype = ctypes.c_int32
__library__.MSK_getdjcnumdomaintot.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumdomaintot.restype = ctypes.c_int32
__library__.MSK_getdjcnumafe.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumafe.restype = ctypes.c_int32
__library__.MSK_getdjcnumafetot.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumafetot.restype = ctypes.c_int32
__library__.MSK_getdjcnumterm.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumterm.restype = ctypes.c_int32
__library__.MSK_getdjcnumtermtot.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcnumtermtot.restype = ctypes.c_int32
__library__.MSK_putmaxnumacc.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumacc.restype = ctypes.c_int32
__library__.MSK_getnumacc.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumacc.restype = ctypes.c_int32
__library__.MSK_appendacc.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_appendacc.restype = ctypes.c_int32
__library__.MSK_appendaccs.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_appendaccs.restype = ctypes.c_int32
__library__.MSK_appendaccseq.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_appendaccseq.restype = ctypes.c_int32
__library__.MSK_appendaccsseq.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_appendaccsseq.restype = ctypes.c_int32
__library__.MSK_putacc.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putacc.restype = ctypes.c_int32
__library__.MSK_putacclist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putacclist.restype = ctypes.c_int32
__library__.MSK_putaccb.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putaccb.restype = ctypes.c_int32
__library__.MSK_putaccbj.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.c_double ]
__library__.MSK_putaccbj.restype = ctypes.c_int32
__library__.MSK_getaccdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccdomain.restype = ctypes.c_int32
__library__.MSK_getaccn.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccn.restype = ctypes.c_int32
__library__.MSK_getaccntot.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccntot.restype = ctypes.c_int32
__library__.MSK_getaccafeidxlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccafeidxlist.restype = ctypes.c_int32
__library__.MSK_getaccb.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccb.restype = ctypes.c_int32
__library__.MSK_getaccs.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccs.restype = ctypes.c_int32
__library__.MSK_getaccfnumnz.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccfnumnz.restype = ctypes.c_int32
__library__.MSK_getaccftrip.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccftrip.restype = ctypes.c_int32
__library__.MSK_getaccgvector.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccgvector.restype = ctypes.c_int32
__library__.MSK_getaccbarfnumblocktriplets.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getaccbarfnumblocktriplets.restype = ctypes.c_int32
__library__.MSK_getaccbarfblocktriplet.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getaccbarfblocktriplet.restype = ctypes.c_int32
__library__.MSK_appenddjcs.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_appenddjcs.restype = ctypes.c_int32
__library__.MSK_putdjc.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_putdjc.restype = ctypes.c_int32
__library__.MSK_putdjcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double),ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_putdjcslice.restype = ctypes.c_int32
__library__.MSK_getdjcdomainidxlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcdomainidxlist.restype = ctypes.c_int32
__library__.MSK_getdjcafeidxlist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcafeidxlist.restype = ctypes.c_int32
__library__.MSK_getdjcb.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getdjcb.restype = ctypes.c_int32
__library__.MSK_getdjctermsizelist.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjctermsizelist.restype = ctypes.c_int32
__library__.MSK_getdjcs.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdjcs.restype = ctypes.c_int32
__library__.MSK_putconbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putconbound.restype = ctypes.c_int32
__library__.MSK_putconboundlist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putconboundlist.restype = ctypes.c_int32
__library__.MSK_putconboundlistconst.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putconboundlistconst.restype = ctypes.c_int32
__library__.MSK_putconboundslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putconboundslice.restype = ctypes.c_int32
__library__.MSK_putconboundsliceconst.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putconboundsliceconst.restype = ctypes.c_int32
__library__.MSK_putvarbound.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putvarbound.restype = ctypes.c_int32
__library__.MSK_putvarboundlist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putvarboundlist.restype = ctypes.c_int32
__library__.MSK_putvarboundlistconst.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putvarboundlistconst.restype = ctypes.c_int32
__library__.MSK_putvarboundslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putvarboundslice.restype = ctypes.c_int32
__library__.MSK_putvarboundsliceconst.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putvarboundsliceconst.restype = ctypes.c_int32
__library__.MSK_putcfix.argtypes = [ ctypes.c_voidp,ctypes.c_double ]
__library__.MSK_putcfix.restype = ctypes.c_int32
__library__.MSK_putcj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putcj.restype = ctypes.c_int32
__library__.MSK_putobjsense.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putobjsense.restype = ctypes.c_int32
__library__.MSK_getobjsense.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getobjsense.restype = ctypes.c_int32
__library__.MSK_putclist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putclist.restype = ctypes.c_int32
__library__.MSK_putcslice.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putcslice.restype = ctypes.c_int32
__library__.MSK_putbarcj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putbarcj.restype = ctypes.c_int32
__library__.MSK_putcone.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putcone.restype = ctypes.c_int32
__library__.MSK_putmaxnumdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumdomain.restype = ctypes.c_int32
__library__.MSK_getnumdomain.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumdomain.restype = ctypes.c_int32
__library__.MSK_appendrplusdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendrplusdomain.restype = ctypes.c_int32
__library__.MSK_appendrminusdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendrminusdomain.restype = ctypes.c_int32
__library__.MSK_appendrdomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendrdomain.restype = ctypes.c_int32
__library__.MSK_appendrzerodomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendrzerodomain.restype = ctypes.c_int32
__library__.MSK_appendquadraticconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendquadraticconedomain.restype = ctypes.c_int32
__library__.MSK_appendrquadraticconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendrquadraticconedomain.restype = ctypes.c_int32
__library__.MSK_appendprimalexpconedomain.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendprimalexpconedomain.restype = ctypes.c_int32
__library__.MSK_appenddualexpconedomain.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appenddualexpconedomain.restype = ctypes.c_int32
__library__.MSK_appendprimalgeomeanconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendprimalgeomeanconedomain.restype = ctypes.c_int32
__library__.MSK_appenddualgeomeanconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appenddualgeomeanconedomain.restype = ctypes.c_int32
__library__.MSK_appendprimalpowerconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendprimalpowerconedomain.restype = ctypes.c_int32
__library__.MSK_appenddualpowerconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appenddualpowerconedomain.restype = ctypes.c_int32
__library__.MSK_appendsvecpsdconedomain.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendsvecpsdconedomain.restype = ctypes.c_int32
__library__.MSK_getdomaintype.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getdomaintype.restype = ctypes.c_int32
__library__.MSK_getdomainn.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getdomainn.restype = ctypes.c_int32
__library__.MSK_getpowerdomaininfo.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getpowerdomaininfo.restype = ctypes.c_int32
__library__.MSK_getpowerdomainalpha.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getpowerdomainalpha.restype = ctypes.c_int32
__library__.MSK_appendsparsesymmat.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendsparsesymmat.restype = ctypes.c_int32
__library__.MSK_appendsparsesymmatlist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_appendsparsesymmatlist.restype = ctypes.c_int32
__library__.MSK_getsymmatinfo.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getsymmatinfo.restype = ctypes.c_int32
__library__.MSK_getnumsymmat.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getnumsymmat.restype = ctypes.c_int32
__library__.MSK_getsparsesymmat.argtypes = [ ctypes.c_voidp,ctypes.c_int64,ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_getsparsesymmat.restype = ctypes.c_int32
__library__.MSK_putdouparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putdouparam.restype = ctypes.c_int32
__library__.MSK_putintparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_putintparam.restype = ctypes.c_int32
__library__.MSK_putmaxnumcon.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putmaxnumcon.restype = ctypes.c_int32
__library__.MSK_putmaxnumcone.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putmaxnumcone.restype = ctypes.c_int32
__library__.MSK_getmaxnumcone.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getmaxnumcone.restype = ctypes.c_int32
__library__.MSK_putmaxnumvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putmaxnumvar.restype = ctypes.c_int32
__library__.MSK_putmaxnumbarvar.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putmaxnumbarvar.restype = ctypes.c_int32
__library__.MSK_putmaxnumanz.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumanz.restype = ctypes.c_int32
__library__.MSK_putmaxnumqnz.argtypes = [ ctypes.c_voidp,ctypes.c_int64 ]
__library__.MSK_putmaxnumqnz.restype = ctypes.c_int32
__library__.MSK_getmaxnumqnz64.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getmaxnumqnz64.restype = ctypes.c_int32
__library__.MSK_putnadouparam.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_double ]
__library__.MSK_putnadouparam.restype = ctypes.c_int32
__library__.MSK_putnaintparam.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_putnaintparam.restype = ctypes.c_int32
__library__.MSK_putnastrparam.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p ]
__library__.MSK_putnastrparam.restype = ctypes.c_int32
__library__.MSK_putobjname.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_putobjname.restype = ctypes.c_int32
__library__.MSK_putparam.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p ]
__library__.MSK_putparam.restype = ctypes.c_int32
__library__.MSK_putqcon.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putqcon.restype = ctypes.c_int32
__library__.MSK_putqconk.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putqconk.restype = ctypes.c_int32
__library__.MSK_putqobj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putqobj.restype = ctypes.c_int32
__library__.MSK_putqobjij.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putqobjij.restype = ctypes.c_int32
__library__.MSK_putsolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsolution.restype = ctypes.c_int32
__library__.MSK_putsolutionnew.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_putsolutionnew.restype = ctypes.c_int32
__library__.MSK_putconsolutioni.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putconsolutioni.restype = ctypes.c_int32
__library__.MSK_putvarsolutionj.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double ]
__library__.MSK_putvarsolutionj.restype = ctypes.c_int32
__library__.MSK_putsolutionyi.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double ]
__library__.MSK_putsolutionyi.restype = ctypes.c_int32
__library__.MSK_putstrparam.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_putstrparam.restype = ctypes.c_int32
__library__.MSK_puttaskname.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_puttaskname.restype = ctypes.c_int32
__library__.MSK_putvartype.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_putvartype.restype = ctypes.c_int32
__library__.MSK_putvartypelist.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putvartypelist.restype = ctypes.c_int32
__library__.MSK_readdataformat.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_readdataformat.restype = ctypes.c_int32
__library__.MSK_readdataautoformat.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readdataautoformat.restype = ctypes.c_int32
__library__.MSK_readparamfile.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readparamfile.restype = ctypes.c_int32
__library__.MSK_readsolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_readsolution.restype = ctypes.c_int32
__library__.MSK_readjsonsol.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readjsonsol.restype = ctypes.c_int32
__library__.MSK_readsummary.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_readsummary.restype = ctypes.c_int32
__library__.MSK_resizetask.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int64,ctypes.c_int64 ]
__library__.MSK_resizetask.restype = ctypes.c_int32
__library__.MSK_checkmemtask.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_checkmemtask.restype = ctypes.c_int32
__library__.MSK_getmemusagetask.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_getmemusagetask.restype = ctypes.c_int32
__library__.MSK_setdefaults.argtypes = [ ctypes.c_voidp ]
__library__.MSK_setdefaults.restype = ctypes.c_int32
__library__.MSK_solutiondef.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_solutiondef.restype = ctypes.c_int32
__library__.MSK_deletesolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_deletesolution.restype = ctypes.c_int32
__library__.MSK_onesolutionsummary.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32 ]
__library__.MSK_onesolutionsummary.restype = ctypes.c_int32
__library__.MSK_solutionsummary.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_solutionsummary.restype = ctypes.c_int32
__library__.MSK_updatesolutioninfo.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_updatesolutioninfo.restype = ctypes.c_int32
__library__.MSK_optimizersummary.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_optimizersummary.restype = ctypes.c_int32
__library__.MSK_strtoconetype.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_strtoconetype.restype = ctypes.c_int32
__library__.MSK_strtosk.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_strtosk.restype = ctypes.c_int32
__library__.MSK_writedata.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_writedata.restype = ctypes.c_int32
__library__.MSK_writetask.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_writetask.restype = ctypes.c_int32
__library__.MSK_writebsolution.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_writebsolution.restype = ctypes.c_int32
__library__.MSK_readbsolution.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_readbsolution.restype = ctypes.c_int32
__library__.MSK_writesolutionfile.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_writesolutionfile.restype = ctypes.c_int32
__library__.MSK_readsolutionfile.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readsolutionfile.restype = ctypes.c_int32
__library__.MSK_readtask.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readtask.restype = ctypes.c_int32
__library__.MSK_readopfstring.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readopfstring.restype = ctypes.c_int32
__library__.MSK_readlpstring.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readlpstring.restype = ctypes.c_int32
__library__.MSK_readjsonstring.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readjsonstring.restype = ctypes.c_int32
__library__.MSK_readptfstring.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_readptfstring.restype = ctypes.c_int32
__library__.MSK_writeparamfile.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_writeparamfile.restype = ctypes.c_int32
__library__.MSK_getinfeasiblesubproblem.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_voidp) ]
__library__.MSK_getinfeasiblesubproblem.restype = ctypes.c_int32
__library__.MSK_writesolution.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p ]
__library__.MSK_writesolution.restype = ctypes.c_int32
__library__.MSK_writejsonsol.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_writejsonsol.restype = ctypes.c_int32
__library__.MSK_primalsensitivity.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_primalsensitivity.restype = ctypes.c_int32
__library__.MSK_sensitivityreport.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_sensitivityreport.restype = ctypes.c_int32
__library__.MSK_dualsensitivity.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_dualsensitivity.restype = ctypes.c_int32
__library__.MSK_optimizermt.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_optimizermt.restype = ctypes.c_int32
__library__.MSK_asyncoptimize.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_asyncoptimize.restype = ctypes.c_int32
__library__.MSK_asyncstop.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p ]
__library__.MSK_asyncstop.restype = ctypes.c_int32
__library__.MSK_asyncpoll.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_asyncpoll.restype = ctypes.c_int32
__library__.MSK_asyncgetresult.argtypes = [ ctypes.c_voidp,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_asyncgetresult.restype = ctypes.c_int32
__library__.MSK_putoptserverhost.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_putoptserverhost.restype = ctypes.c_int32
__library__.MSK_optimizebatch.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double,ctypes.c_int32,ctypes.c_int64,ctypes.POINTER(ctypes.c_void_p),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_optimizebatch.restype = ctypes.c_int32
__library__.MSK_checkoutlicense.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_checkoutlicense.restype = ctypes.c_int32
__library__.MSK_checkinlicense.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_checkinlicense.restype = ctypes.c_int32
__library__.MSK_checkinall.argtypes = [ ctypes.c_voidp ]
__library__.MSK_checkinall.restype = ctypes.c_int32
__library__.MSK_expirylicenses.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int64) ]
__library__.MSK_expirylicenses.restype = ctypes.c_int32
__library__.MSK_resetexpirylicenses.argtypes = [ ctypes.c_voidp ]
__library__.MSK_resetexpirylicenses.restype = ctypes.c_int32
__library__.MSK_echointro.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_echointro.restype = ctypes.c_int32
__library__.MSK_getcodedesc.argtypes = [ ctypes.c_int32,ctypes.POINTER(ctypes.c_char),ctypes.POINTER(ctypes.c_char) ]
__library__.MSK_getcodedesc.restype = ctypes.c_int32
__library__.MSK_getversion.argtypes = [ ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_getversion.restype = ctypes.c_int32
__library__.MSK_linkfiletoenvstream.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_char_p,ctypes.c_int32 ]
__library__.MSK_linkfiletoenvstream.restype = ctypes.c_int32
__library__.MSK_putlicensedebug.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putlicensedebug.restype = ctypes.c_int32
__library__.MSK_putlicensecode.argtypes = [ ctypes.c_voidp,ctypes.POINTER(ctypes.c_int32) ]
__library__.MSK_putlicensecode.restype = ctypes.c_int32
__library__.MSK_putlicensewait.argtypes = [ ctypes.c_voidp,ctypes.c_int32 ]
__library__.MSK_putlicensewait.restype = ctypes.c_int32
__library__.MSK_putlicensepath.argtypes = [ ctypes.c_voidp,ctypes.c_char_p ]
__library__.MSK_putlicensepath.restype = ctypes.c_int32
__library__.MSK_axpy.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_double,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_axpy.restype = ctypes.c_int32
__library__.MSK_dot.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_dot.restype = ctypes.c_int32
__library__.MSK_gemv.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.c_double,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_gemv.restype = ctypes.c_int32
__library__.MSK_gemm.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.c_double,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_gemm.restype = ctypes.c_int32
__library__.MSK_syrk.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.POINTER(ctypes.c_double),ctypes.c_double,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_syrk.restype = ctypes.c_int32
__library__.MSK_computesparsecholesky.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.c_double,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.POINTER(ctypes.c_int32)),ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),ctypes.POINTER(ctypes.POINTER(ctypes.c_int32)),ctypes.POINTER(ctypes.POINTER(ctypes.c_int64)),ctypes.POINTER(ctypes.c_int64),ctypes.POINTER(ctypes.POINTER(ctypes.c_int32)),ctypes.POINTER(ctypes.POINTER(ctypes.c_double)) ]
__library__.MSK_computesparsecholesky.restype = ctypes.c_int32
__library__.MSK_sparsetriangularsolvedense.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_int64),ctypes.c_int64,ctypes.POINTER(ctypes.c_int32),ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_sparsetriangularsolvedense.restype = ctypes.c_int32
__library__.MSK_potrf.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_potrf.restype = ctypes.c_int32
__library__.MSK_syeig.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_syeig.restype = ctypes.c_int32
__library__.MSK_syevd.argtypes = [ ctypes.c_voidp,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double) ]
__library__.MSK_syevd.restype = ctypes.c_int32
__library__.MSK_licensecleanup.argtypes = [  ]
__library__.MSK_licensecleanup.restype = ctypes.c_int32


basindtype = Enum("basindtype", ["always","if_feasible","never","no_error","reservered"], [1,3,0,2,4])
boundkey = Enum("boundkey", ["fr","fx","lo","ra","up"], [3,2,0,4,1])
mark = Enum("mark", ["lo","up"], [0,1])
simdegen = Enum("simdegen", ["aggressive","free","minimum","moderate","none"], [2,1,4,3,0])
transpose = Enum("transpose", ["no","yes"], [0,1])
uplo = Enum("uplo", ["lo","up"], [0,1])
simreform = Enum("simreform", ["aggressive","free","off","on"], [3,2,0,1])
simdupvec = Enum("simdupvec", ["free","off","on"], [2,0,1])
simhotstart = Enum("simhotstart", ["free","none","status_keys"], [1,0,2])
intpnthotstart = Enum("intpnthotstart", ["dual","none","primal","primal_dual"], [2,0,1,3])
purify = Enum("purify", ["auto","dual","none","primal","primal_dual"], [4,2,0,1,3])
callbackcode = Enum("callbackcode", ["begin_bi","begin_conic","begin_dual_bi","begin_dual_sensitivity","begin_dual_setup_bi","begin_dual_simplex","begin_dual_simplex_bi","begin_infeas_ana","begin_intpnt","begin_license_wait","begin_mio","begin_optimizer","begin_presolve","begin_primal_bi","begin_primal_repair","begin_primal_sensitivity","begin_primal_setup_bi","begin_primal_simplex","begin_primal_simplex_bi","begin_qcqo_reformulate","begin_read","begin_root_cutgen","begin_simplex","begin_simplex_bi","begin_solve_root_relax","begin_to_conic","begin_write","conic","dual_simplex","end_bi","end_conic","end_dual_bi","end_dual_sensitivity","end_dual_setup_bi","end_dual_simplex","end_dual_simplex_bi","end_infeas_ana","end_intpnt","end_license_wait","end_mio","end_optimizer","end_presolve","end_primal_bi","end_primal_repair","end_primal_sensitivity","end_primal_setup_bi","end_primal_simplex","end_primal_simplex_bi","end_qcqo_reformulate","end_read","end_root_cutgen","end_simplex","end_simplex_bi","end_solve_root_relax","end_to_conic","end_write","im_bi","im_conic","im_dual_bi","im_dual_sensivity","im_dual_simplex","im_intpnt","im_license_wait","im_lu","im_mio","im_mio_dual_simplex","im_mio_intpnt","im_mio_primal_simplex","im_order","im_presolve","im_primal_bi","im_primal_sensivity","im_primal_simplex","im_qo_reformulate","im_read","im_root_cutgen","im_simplex","im_simplex_bi","intpnt","new_int_mio","primal_simplex","read_opf","read_opf_section","solving_remote","update_dual_bi","update_dual_simplex","update_dual_simplex_bi","update_presolve","update_primal_bi","update_primal_simplex","update_primal_simplex_bi","update_simplex","write_opf"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92])
checkconvexitytype = Enum("checkconvexitytype", ["full","none","simple"], [2,0,1])
compresstype = Enum("compresstype", ["free","gzip","none","zstd"], [1,2,0,3])
conetype = Enum("conetype", ["dexp","dpow","pexp","ppow","quad","rquad","zero"], [3,5,2,4,0,1,6])
domaintype = Enum("domaintype", ["dual_exp_cone","dual_geo_mean_cone","dual_power_cone","primal_exp_cone","primal_geo_mean_cone","primal_power_cone","quadratic_cone","r","rminus","rplus","rquadratic_cone","rzero","svec_psd_cone"], [7,11,9,6,10,8,4,0,3,2,5,1,12])
nametype = Enum("nametype", ["gen","lp","mps"], [0,2,1])
symmattype = Enum("symmattype", ["sparse"], [0])
dataformat = Enum("dataformat", ["cb","extension","free_mps","json_task","lp","mps","op","ptf","task"], [7,0,4,8,2,1,3,6,5])
solformat = Enum("solformat", ["b","extension","json_task","task"], [1,0,3,2])
dinfitem = Enum("dinfitem", ["ana_pro_scalarized_constraint_matrix_density","bi_clean_dual_time","bi_clean_primal_time","bi_clean_time","bi_dual_time","bi_primal_time","bi_time","intpnt_dual_feas","intpnt_dual_obj","intpnt_factor_num_flops","intpnt_opt_status","intpnt_order_time","intpnt_primal_feas","intpnt_primal_obj","intpnt_time","mio_clique_separation_time","mio_cmir_separation_time","mio_construct_solution_obj","mio_dual_bound_after_presolve","mio_gmi_separation_time","mio_implied_bound_time","mio_initial_feasible_solution_obj","mio_knapsack_cover_separation_time","mio_lipro_separation_time","mio_obj_abs_gap","mio_obj_bound","mio_obj_int","mio_obj_rel_gap","mio_probing_time","mio_root_cutgen_time","mio_root_optimizer_time","mio_root_presolve_time","mio_root_time","mio_time","mio_user_obj_cut","optimizer_time","presolve_eli_time","presolve_lindep_time","presolve_time","presolve_total_primal_perturbation","primal_repair_penalty_obj","qcqo_reformulate_max_perturbation","qcqo_reformulate_time","qcqo_reformulate_worst_cholesky_column_scaling","qcqo_reformulate_worst_cholesky_diag_scaling","read_data_time","remote_time","sim_dual_time","sim_feas","sim_obj","sim_primal_time","sim_time","sol_bas_dual_obj","sol_bas_dviolcon","sol_bas_dviolvar","sol_bas_nrm_barx","sol_bas_nrm_slc","sol_bas_nrm_slx","sol_bas_nrm_suc","sol_bas_nrm_sux","sol_bas_nrm_xc","sol_bas_nrm_xx","sol_bas_nrm_y","sol_bas_primal_obj","sol_bas_pviolcon","sol_bas_pviolvar","sol_itg_nrm_barx","sol_itg_nrm_xc","sol_itg_nrm_xx","sol_itg_primal_obj","sol_itg_pviolacc","sol_itg_pviolbarvar","sol_itg_pviolcon","sol_itg_pviolcones","sol_itg_pvioldjc","sol_itg_pviolitg","sol_itg_pviolvar","sol_itr_dual_obj","sol_itr_dviolacc","sol_itr_dviolbarvar","sol_itr_dviolcon","sol_itr_dviolcones","sol_itr_dviolvar","sol_itr_nrm_bars","sol_itr_nrm_barx","sol_itr_nrm_slc","sol_itr_nrm_slx","sol_itr_nrm_snx","sol_itr_nrm_suc","sol_itr_nrm_sux","sol_itr_nrm_xc","sol_itr_nrm_xx","sol_itr_nrm_y","sol_itr_primal_obj","sol_itr_pviolacc","sol_itr_pviolbarvar","sol_itr_pviolcon","sol_itr_pviolcones","sol_itr_pviolvar","to_conic_time","write_data_time"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100])
feature = Enum("feature", ["pton","pts"], [1,0])
dparam = Enum("dparam", ["ana_sol_infeas_tol","basis_rel_tol_s","basis_tol_s","basis_tol_x","check_convexity_rel_tol","data_sym_mat_tol","data_sym_mat_tol_huge","data_sym_mat_tol_large","data_tol_aij_huge","data_tol_aij_large","data_tol_bound_inf","data_tol_bound_wrn","data_tol_c_huge","data_tol_cj_large","data_tol_qij","data_tol_x","intpnt_co_tol_dfeas","intpnt_co_tol_infeas","intpnt_co_tol_mu_red","intpnt_co_tol_near_rel","intpnt_co_tol_pfeas","intpnt_co_tol_rel_gap","intpnt_qo_tol_dfeas","intpnt_qo_tol_infeas","intpnt_qo_tol_mu_red","intpnt_qo_tol_near_rel","intpnt_qo_tol_pfeas","intpnt_qo_tol_rel_gap","intpnt_tol_dfeas","intpnt_tol_dsafe","intpnt_tol_infeas","intpnt_tol_mu_red","intpnt_tol_path","intpnt_tol_pfeas","intpnt_tol_psafe","intpnt_tol_rel_gap","intpnt_tol_rel_step","intpnt_tol_step_size","lower_obj_cut","lower_obj_cut_finite_trh","mio_djc_max_bigm","mio_max_time","mio_rel_gap_const","mio_tol_abs_gap","mio_tol_abs_relax_int","mio_tol_feas","mio_tol_rel_dual_bound_improvement","mio_tol_rel_gap","optimizer_max_time","presolve_tol_abs_lindep","presolve_tol_aij","presolve_tol_primal_infeas_perturbation","presolve_tol_rel_lindep","presolve_tol_s","presolve_tol_x","qcqo_reformulate_rel_drop_tol","semidefinite_tol_approx","sim_lu_tol_rel_piv","simplex_abs_tol_piv","upper_obj_cut","upper_obj_cut_finite_trh"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60])
liinfitem = Enum("liinfitem", ["ana_pro_scalarized_constraint_matrix_num_columns","ana_pro_scalarized_constraint_matrix_num_nz","ana_pro_scalarized_constraint_matrix_num_rows","bi_clean_dual_deg_iter","bi_clean_dual_iter","bi_clean_primal_deg_iter","bi_clean_primal_iter","bi_dual_iter","bi_primal_iter","intpnt_factor_num_nz","mio_anz","mio_intpnt_iter","mio_num_dual_illposed_cer","mio_num_prim_illposed_cer","mio_presolved_anz","mio_simplex_iter","rd_numacc","rd_numanz","rd_numdjc","rd_numqnz","simplex_iter"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
iinfitem = Enum("iinfitem", ["ana_pro_num_con","ana_pro_num_con_eq","ana_pro_num_con_fr","ana_pro_num_con_lo","ana_pro_num_con_ra","ana_pro_num_con_up","ana_pro_num_var","ana_pro_num_var_bin","ana_pro_num_var_cont","ana_pro_num_var_eq","ana_pro_num_var_fr","ana_pro_num_var_int","ana_pro_num_var_lo","ana_pro_num_var_ra","ana_pro_num_var_up","intpnt_factor_dim_dense","intpnt_iter","intpnt_num_threads","intpnt_solve_dual","mio_absgap_satisfied","mio_clique_table_size","mio_construct_solution","mio_initial_feasible_solution","mio_node_depth","mio_num_active_nodes","mio_num_branch","mio_num_clique_cuts","mio_num_cmir_cuts","mio_num_gomory_cuts","mio_num_implied_bound_cuts","mio_num_int_solutions","mio_num_knapsack_cover_cuts","mio_num_lipro_cuts","mio_num_relax","mio_num_repeated_presolve","mio_numbin","mio_numbinconevar","mio_numcon","mio_numcone","mio_numconevar","mio_numcont","mio_numcontconevar","mio_numdexpcones","mio_numdjc","mio_numdpowcones","mio_numint","mio_numintconevar","mio_numpexpcones","mio_numppowcones","mio_numqcones","mio_numrqcones","mio_numvar","mio_obj_bound_defined","mio_presolved_numbin","mio_presolved_numbinconevar","mio_presolved_numcon","mio_presolved_numcone","mio_presolved_numconevar","mio_presolved_numcont","mio_presolved_numcontconevar","mio_presolved_numdexpcones","mio_presolved_numdjc","mio_presolved_numdpowcones","mio_presolved_numint","mio_presolved_numintconevar","mio_presolved_numpexpcones","mio_presolved_numppowcones","mio_presolved_numqcones","mio_presolved_numrqcones","mio_presolved_numvar","mio_relgap_satisfied","mio_total_num_cuts","mio_user_obj_cut","opt_numcon","opt_numvar","optimize_response","presolve_num_primal_perturbations","purify_dual_success","purify_primal_success","rd_numbarvar","rd_numcon","rd_numcone","rd_numintvar","rd_numq","rd_numvar","rd_protype","sim_dual_deg_iter","sim_dual_hotstart","sim_dual_hotstart_lu","sim_dual_inf_iter","sim_dual_iter","sim_numcon","sim_numvar","sim_primal_deg_iter","sim_primal_hotstart","sim_primal_hotstart_lu","sim_primal_inf_iter","sim_primal_iter","sim_solve_dual","sol_bas_prosta","sol_bas_solsta","sol_itg_prosta","sol_itg_solsta","sol_itr_prosta","sol_itr_solsta","sto_num_a_realloc"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105])
inftype = Enum("inftype", ["dou_type","int_type","lint_type"], [0,1,2])
iomode = Enum("iomode", ["read","readwrite","write"], [0,2,1])
iparam = Enum("iparam", ["ana_sol_basis","ana_sol_print_violated","auto_sort_a_before_opt","auto_update_sol_info","basis_solve_use_plus_one","bi_clean_optimizer","bi_ignore_max_iter","bi_ignore_num_error","bi_max_iterations","cache_license","check_convexity","compress_statfile","infeas_generic_names","infeas_prefer_primal","infeas_report_auto","infeas_report_level","intpnt_basis","intpnt_diff_step","intpnt_hotstart","intpnt_max_iterations","intpnt_max_num_cor","intpnt_max_num_refinement_steps","intpnt_off_col_trh","intpnt_order_gp_num_seeds","intpnt_order_method","intpnt_purify","intpnt_regularization_use","intpnt_scaling","intpnt_solve_form","intpnt_starting_point","license_debug","license_pause_time","license_suppress_expire_wrns","license_trh_expiry_wrn","license_wait","log","log_ana_pro","log_bi","log_bi_freq","log_check_convexity","log_cut_second_opt","log_expand","log_feas_repair","log_file","log_include_summary","log_infeas_ana","log_intpnt","log_local_info","log_mio","log_mio_freq","log_order","log_presolve","log_response","log_sensitivity","log_sensitivity_opt","log_sim","log_sim_freq","log_sim_minor","log_storage","max_num_warnings","mio_branch_dir","mio_conic_outer_approximation","mio_construct_sol","mio_cut_clique","mio_cut_cmir","mio_cut_gmi","mio_cut_implied_bound","mio_cut_knapsack_cover","mio_cut_lipro","mio_cut_selection_level","mio_data_permutation_method","mio_feaspump_level","mio_heuristic_level","mio_max_num_branches","mio_max_num_relaxs","mio_max_num_root_cut_rounds","mio_max_num_solutions","mio_memory_emphasis_level","mio_mode","mio_node_optimizer","mio_node_selection","mio_numerical_emphasis_level","mio_perspective_reformulate","mio_presolve_aggregator_use","mio_probing_level","mio_propagate_objective_constraint","mio_qcqo_reformulation_method","mio_rins_max_nodes","mio_root_optimizer","mio_root_repeat_presolve_level","mio_seed","mio_symmetry_level","mio_vb_detection_level","mt_spincount","ng","num_threads","opf_write_header","opf_write_hints","opf_write_line_length","opf_write_parameters","opf_write_problem","opf_write_sol_bas","opf_write_sol_itg","opf_write_sol_itr","opf_write_solutions","optimizer","param_read_case_name","param_read_ign_error","presolve_eliminator_max_fill","presolve_eliminator_max_num_tries","presolve_level","presolve_lindep_abs_work_trh","presolve_lindep_rel_work_trh","presolve_lindep_use","presolve_max_num_pass","presolve_max_num_reductions","presolve_use","primal_repair_optimizer","ptf_write_parameters","ptf_write_solutions","ptf_write_transform","read_debug","read_keep_free_con","read_mps_format","read_mps_width","read_task_ignore_param","remote_use_compression","remove_unused_solutions","sensitivity_all","sensitivity_optimizer","sensitivity_type","sim_basis_factor_use","sim_degen","sim_detect_pwl","sim_dual_crash","sim_dual_phaseone_method","sim_dual_restrict_selection","sim_dual_selection","sim_exploit_dupvec","sim_hotstart","sim_hotstart_lu","sim_max_iterations","sim_max_num_setbacks","sim_non_singular","sim_primal_crash","sim_primal_phaseone_method","sim_primal_restrict_selection","sim_primal_selection","sim_refactor_freq","sim_reformulation","sim_save_lu","sim_scaling","sim_scaling_method","sim_seed","sim_solve_form","sim_stability_priority","sim_switch_optimizer","sol_filter_keep_basic","sol_filter_keep_ranged","sol_read_name_width","sol_read_width","solution_callback","timing_level","write_bas_constraints","write_bas_head","write_bas_variables","write_compression","write_data_param","write_free_con","write_generic_names","write_generic_names_io","write_ignore_incompatible_items","write_int_constraints","write_int_head","write_int_variables","write_json_indentation","write_lp_full_obj","write_lp_line_width","write_mps_format","write_mps_int","write_sol_barvariables","write_sol_constraints","write_sol_head","write_sol_ignore_invalid_names","write_sol_variables","write_task_inc_sol","write_xml_mode"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186])
branchdir = Enum("branchdir", ["down","far","free","guided","near","pseudocost","root_lp","up"], [2,4,0,6,3,7,5,1])
miqcqoreformmethod = Enum("miqcqoreformmethod", ["diag_sdp","eigen_val_method","free","linearization","none","relax_sdp"], [4,3,0,2,1,5])
miodatapermmethod = Enum("miodatapermmethod", ["cyclic_shift","none","random"], [1,0,2])
miocontsoltype = Enum("miocontsoltype", ["itg","itg_rel","none","root"], [2,3,0,1])
miomode = Enum("miomode", ["ignored","satisfied"], [0,1])
mionodeseltype = Enum("mionodeseltype", ["best","first","free","pseudo"], [2,1,0,3])
mpsformat = Enum("mpsformat", ["cplex","free","relaxed","strict"], [3,2,1,0])
objsense = Enum("objsense", ["maximize","minimize"], [1,0])
onoffkey = Enum("onoffkey", ["off","on"], [0,1])
optimizertype = Enum("optimizertype", ["conic","dual_simplex","free","free_simplex","intpnt","mixed_int","primal_simplex"], [0,1,2,3,4,5,6])
orderingtype = Enum("orderingtype", ["appminloc","experimental","force_graphpar","free","none","try_graphpar"], [1,2,4,0,5,3])
presolvemode = Enum("presolvemode", ["free","off","on"], [2,0,1])
parametertype = Enum("parametertype", ["dou_type","int_type","invalid_type","str_type"], [1,2,0,3])
problemitem = Enum("problemitem", ["con","cone","var"], [1,2,0])
problemtype = Enum("problemtype", ["conic","lo","mixed","qcqo","qo"], [3,0,4,2,1])
prosta = Enum("prosta", ["dual_feas","dual_infeas","ill_posed","prim_and_dual_feas","prim_and_dual_infeas","prim_feas","prim_infeas","prim_infeas_or_unbounded","unknown"], [3,5,7,1,6,2,4,8,0])
xmlwriteroutputtype = Enum("xmlwriteroutputtype", ["col","row"], [1,0])
rescode = Enum("rescode", ["err_acc_afe_domain_mismatch","err_acc_invalid_entry_index","err_acc_invalid_index","err_ad_invalid_codelist","err_afe_invalid_index","err_api_array_too_small","err_api_cb_connect","err_api_fatal_error","err_api_internal","err_appending_too_big_cone","err_arg_is_too_large","err_arg_is_too_small","err_argument_dimension","err_argument_is_too_large","err_argument_is_too_small","err_argument_lenneq","err_argument_perm_array","err_argument_type","err_axis_name_specification","err_bar_var_dim","err_basis","err_basis_factor","err_basis_singular","err_blank_name","err_cbf_duplicate_acoord","err_cbf_duplicate_bcoord","err_cbf_duplicate_con","err_cbf_duplicate_int","err_cbf_duplicate_obj","err_cbf_duplicate_objacoord","err_cbf_duplicate_pow_cones","err_cbf_duplicate_pow_star_cones","err_cbf_duplicate_psdcon","err_cbf_duplicate_psdvar","err_cbf_duplicate_var","err_cbf_invalid_con_type","err_cbf_invalid_dimension_of_cones","err_cbf_invalid_dimension_of_psdcon","err_cbf_invalid_domain_dimension","err_cbf_invalid_exp_dimension","err_cbf_invalid_int_index","err_cbf_invalid_num_psdcon","err_cbf_invalid_number_of_cones","err_cbf_invalid_power","err_cbf_invalid_power_cone_index","err_cbf_invalid_power_star_cone_index","err_cbf_invalid_psdcon_block_index","err_cbf_invalid_psdcon_index","err_cbf_invalid_psdcon_variable_index","err_cbf_invalid_psdvar_dimension","err_cbf_invalid_var_type","err_cbf_no_variables","err_cbf_no_version_specified","err_cbf_obj_sense","err_cbf_parse","err_cbf_power_cone_is_too_long","err_cbf_power_cone_mismatch","err_cbf_power_star_cone_mismatch","err_cbf_syntax","err_cbf_too_few_constraints","err_cbf_too_few_ints","err_cbf_too_few_psdvar","err_cbf_too_few_variables","err_cbf_too_many_constraints","err_cbf_too_many_ints","err_cbf_too_many_variables","err_cbf_unhandled_power_cone_type","err_cbf_unhandled_power_star_cone_type","err_cbf_unsupported","err_cbf_unsupported_change","err_con_q_not_nsd","err_con_q_not_psd","err_cone_index","err_cone_overlap","err_cone_overlap_append","err_cone_parameter","err_cone_rep_var","err_cone_size","err_cone_type","err_cone_type_str","err_data_file_ext","err_dimension_specification","err_djc_afe_domain_mismatch","err_djc_domain_termsize_mismatch","err_djc_invalid_index","err_djc_invalid_term_size","err_djc_total_num_terms_mismatch","err_djc_unsupported_domain_type","err_domain_dimension","err_domain_dimension_psd","err_domain_invalid_index","err_domain_power_invalid_alpha","err_domain_power_negative_alpha","err_domain_power_nleft","err_dup_name","err_duplicate_aij","err_duplicate_barvariable_names","err_duplicate_cone_names","err_duplicate_constraint_names","err_duplicate_djc_names","err_duplicate_domain_names","err_duplicate_fij","err_duplicate_variable_names","err_end_of_file","err_factor","err_feasrepair_cannot_relax","err_feasrepair_inconsistent_bound","err_feasrepair_solving_relaxed","err_file_license","err_file_open","err_file_read","err_file_write","err_final_solution","err_first","err_firsti","err_firstj","err_fixed_bound_values","err_flexlm","err_format_string","err_global_inv_conic_problem","err_huge_aij","err_huge_c","err_huge_fij","err_identical_tasks","err_in_argument","err_index","err_index_arr_is_too_large","err_index_arr_is_too_small","err_index_is_not_unique","err_index_is_too_large","err_index_is_too_small","err_inf_dou_index","err_inf_dou_name","err_inf_in_double_data","err_inf_int_index","err_inf_int_name","err_inf_lint_index","err_inf_lint_name","err_inf_type","err_infeas_undefined","err_infinite_bound","err_int64_to_int32_cast","err_internal","err_internal_test_failed","err_inv_aptre","err_inv_bk","err_inv_bkc","err_inv_bkx","err_inv_cone_type","err_inv_cone_type_str","err_inv_marki","err_inv_markj","err_inv_name_item","err_inv_numi","err_inv_numj","err_inv_optimizer","err_inv_problem","err_inv_qcon_subi","err_inv_qcon_subj","err_inv_qcon_subk","err_inv_qcon_val","err_inv_qobj_subi","err_inv_qobj_subj","err_inv_qobj_val","err_inv_sk","err_inv_sk_str","err_inv_skc","err_inv_skn","err_inv_skx","err_inv_var_type","err_invalid_aij","err_invalid_ampl_stub","err_invalid_b","err_invalid_barvar_name","err_invalid_cfix","err_invalid_cj","err_invalid_compression","err_invalid_con_name","err_invalid_cone_name","err_invalid_fij","err_invalid_file_format_for_affine_conic_constraints","err_invalid_file_format_for_cfix","err_invalid_file_format_for_cones","err_invalid_file_format_for_disjunctive_constraints","err_invalid_file_format_for_free_constraints","err_invalid_file_format_for_nonlinear","err_invalid_file_format_for_quadratic_terms","err_invalid_file_format_for_ranged_constraints","err_invalid_file_format_for_sym_mat","err_invalid_file_name","err_invalid_format_type","err_invalid_g","err_invalid_idx","err_invalid_iomode","err_invalid_max_num","err_invalid_name_in_sol_file","err_invalid_obj_name","err_invalid_objective_sense","err_invalid_problem_type","err_invalid_sol_file_name","err_invalid_stream","err_invalid_surplus","err_invalid_sym_mat_dim","err_invalid_task","err_invalid_utf8","err_invalid_var_name","err_invalid_wchar","err_invalid_whichsol","err_json_data","err_json_format","err_json_missing_data","err_json_number_overflow","err_json_string","err_json_syntax","err_last","err_lasti","err_lastj","err_lau_arg_k","err_lau_arg_m","err_lau_arg_n","err_lau_arg_trans","err_lau_arg_transa","err_lau_arg_transb","err_lau_arg_uplo","err_lau_invalid_lower_triangular_matrix","err_lau_invalid_sparse_symmetric_matrix","err_lau_not_positive_definite","err_lau_singular_matrix","err_lau_unknown","err_license","err_license_cannot_allocate","err_license_cannot_connect","err_license_expired","err_license_feature","err_license_invalid_hostid","err_license_max","err_license_moseklm_daemon","err_license_no_server_line","err_license_no_server_support","err_license_old_server_version","err_license_server","err_license_server_version","err_license_version","err_link_file_dll","err_living_tasks","err_lower_bound_is_a_nan","err_lp_dup_slack_name","err_lp_empty","err_lp_file_format","err_lp_free_constraint","err_lp_incompatible","err_lp_indicator_var","err_lp_invalid_con_name","err_lp_invalid_var_name","err_lp_write_conic_problem","err_lp_write_geco_problem","err_lu_max_num_tries","err_max_len_is_too_small","err_maxnumbarvar","err_maxnumcon","err_maxnumcone","err_maxnumqnz","err_maxnumvar","err_mio_internal","err_mio_invalid_node_optimizer","err_mio_invalid_root_optimizer","err_mio_no_optimizer","err_mismatching_dimension","err_missing_license_file","err_mixed_conic_and_nl","err_mps_cone_overlap","err_mps_cone_repeat","err_mps_cone_type","err_mps_duplicate_q_element","err_mps_file","err_mps_inv_field","err_mps_inv_marker","err_mps_inv_sec_order","err_mps_invalid_bound_key","err_mps_invalid_con_key","err_mps_invalid_indicator_constraint","err_mps_invalid_indicator_quadratic_constraint","err_mps_invalid_indicator_value","err_mps_invalid_indicator_variable","err_mps_invalid_key","err_mps_invalid_obj_name","err_mps_invalid_objsense","err_mps_invalid_sec_name","err_mps_mul_con_name","err_mps_mul_csec","err_mps_mul_qobj","err_mps_mul_qsec","err_mps_no_objective","err_mps_non_symmetric_q","err_mps_null_con_name","err_mps_null_var_name","err_mps_splitted_var","err_mps_tab_in_field2","err_mps_tab_in_field3","err_mps_tab_in_field5","err_mps_undef_con_name","err_mps_undef_var_name","err_mps_write_cplex_invalid_cone_type","err_mul_a_element","err_name_is_null","err_name_max_len","err_nan_in_blc","err_nan_in_blx","err_nan_in_buc","err_nan_in_bux","err_nan_in_c","err_nan_in_double_data","err_negative_append","err_negative_surplus","err_newer_dll","err_no_bars_for_solution","err_no_barx_for_solution","err_no_basis_sol","err_no_doty","err_no_dual_for_itg_sol","err_no_dual_infeas_cer","err_no_init_env","err_no_optimizer_var_type","err_no_primal_infeas_cer","err_no_snx_for_bas_sol","err_no_solution_in_callback","err_non_unique_array","err_nonconvex","err_nonlinear_equality","err_nonlinear_ranged","err_not_power_domain","err_null_env","err_null_pointer","err_null_task","err_num_arguments","err_numconlim","err_numvarlim","err_obj_q_not_nsd","err_obj_q_not_psd","err_objective_range","err_older_dll","err_opf_dual_integer_solution","err_opf_duplicate_bound","err_opf_duplicate_cone_entry","err_opf_duplicate_constraint_name","err_opf_incorrect_tag_param","err_opf_invalid_cone_type","err_opf_invalid_tag","err_opf_mismatched_tag","err_opf_premature_eof","err_opf_syntax","err_opf_too_large","err_optimizer_license","err_overflow","err_param_index","err_param_is_too_large","err_param_is_too_small","err_param_name","err_param_name_dou","err_param_name_int","err_param_name_str","err_param_type","err_param_value_str","err_platform_not_licensed","err_postsolve","err_pro_item","err_prob_license","err_ptf_format","err_ptf_incompatibility","err_ptf_inconsistency","err_ptf_undefined_item","err_qcon_subi_too_large","err_qcon_subi_too_small","err_qcon_upper_triangle","err_qobj_upper_triangle","err_read_format","err_read_lp_missing_end_tag","err_read_lp_nonexisting_name","err_remove_cone_variable","err_repair_invalid_problem","err_repair_optimization_failed","err_sen_bound_invalid_lo","err_sen_bound_invalid_up","err_sen_format","err_sen_index_invalid","err_sen_index_range","err_sen_invalid_regexp","err_sen_numerical","err_sen_solution_status","err_sen_undef_name","err_sen_unhandled_problem_type","err_server_access_token","err_server_address","err_server_certificate","err_server_connect","err_server_problem_size","err_server_protocol","err_server_status","err_server_tls_client","err_server_token","err_shape_is_too_large","err_size_license","err_size_license_con","err_size_license_intvar","err_size_license_numcores","err_size_license_var","err_slice_size","err_sol_file_invalid_number","err_solitem","err_solver_probtype","err_space","err_space_leaking","err_space_no_info","err_sparsity_specification","err_sym_mat_duplicate","err_sym_mat_huge","err_sym_mat_invalid","err_sym_mat_invalid_col_index","err_sym_mat_invalid_row_index","err_sym_mat_invalid_value","err_sym_mat_not_lower_tringular","err_task_incompatible","err_task_invalid","err_task_write","err_thread_cond_init","err_thread_create","err_thread_mutex_init","err_thread_mutex_lock","err_thread_mutex_unlock","err_toconic_constr_not_conic","err_toconic_constr_q_not_psd","err_toconic_constraint_fx","err_toconic_constraint_ra","err_toconic_objective_not_psd","err_too_small_a_truncation_value","err_too_small_max_num_nz","err_too_small_maxnumanz","err_unallowed_whichsol","err_unb_step_size","err_undef_solution","err_undefined_objective_sense","err_unhandled_solution_status","err_unknown","err_upper_bound_is_a_nan","err_upper_triangle","err_whichitem_not_allowed","err_whichsol","err_write_lp_format","err_write_lp_non_unique_name","err_write_mps_invalid_name","err_write_opf_invalid_var_name","err_writing_file","err_xml_invalid_problem_type","err_y_is_undefined","ok","trm_internal","trm_internal_stop","trm_lost_race","trm_max_iterations","trm_max_num_setbacks","trm_max_time","trm_mio_num_branches","trm_mio_num_relaxs","trm_num_max_num_int_solutions","trm_numerical_problem","trm_objective_range","trm_stall","trm_user_callback","wrn_ana_almost_int_bounds","wrn_ana_c_zero","wrn_ana_close_bounds","wrn_ana_empty_cols","wrn_ana_large_bounds","wrn_dropped_nz_qobj","wrn_duplicate_barvariable_names","wrn_duplicate_cone_names","wrn_duplicate_constraint_names","wrn_duplicate_variable_names","wrn_eliminator_space","wrn_empty_name","wrn_ignore_integer","wrn_incomplete_linear_dependency_check","wrn_invalid_mps_name","wrn_invalid_mps_obj_name","wrn_large_aij","wrn_large_bound","wrn_large_cj","wrn_large_con_fx","wrn_large_fij","wrn_large_lo_bound","wrn_large_up_bound","wrn_license_expire","wrn_license_feature_expire","wrn_license_server","wrn_lp_drop_variable","wrn_lp_old_quad_format","wrn_mio_infeasible_final","wrn_modified_double_parameter","wrn_mps_split_bou_vector","wrn_mps_split_ran_vector","wrn_mps_split_rhs_vector","wrn_name_max_len","wrn_no_dualizer","wrn_no_global_optimizer","wrn_no_infeasibility_report_when_matrix_variables","wrn_nz_in_upr_tri","wrn_open_param_file","wrn_param_ignored_cmio","wrn_param_name_dou","wrn_param_name_int","wrn_param_name_str","wrn_param_str_value","wrn_presolve_outofspace","wrn_presolve_primal_pertubations","wrn_sol_file_ignored_con","wrn_sol_file_ignored_var","wrn_sol_filter","wrn_spar_max_len","wrn_sym_mat_large","wrn_too_few_basis_vars","wrn_too_many_basis_vars","wrn_undef_sol_file_name","wrn_using_generic_names","wrn_write_changed_names","wrn_write_discarded_cfix","wrn_write_lp_duplicate_con_names","wrn_write_lp_duplicate_var_names","wrn_write_lp_invalid_con_names","wrn_write_lp_invalid_var_names","wrn_zero_aij","wrn_zeros_in_sparse_col","wrn_zeros_in_sparse_row"], [20602,20601,20600,3102,20500,3001,3002,3005,3999,1311,1227,1226,1201,5005,5004,1197,1299,1198,1083,3920,1266,1610,1615,1070,7117,7116,7108,7111,7107,7115,7130,7131,7201,7124,7110,7113,7141,7202,7114,7127,7122,7200,7140,7132,7134,7135,7205,7203,7204,7125,7112,7102,7105,7101,7100,7133,7138,7139,7106,7119,7120,7126,7118,7103,7121,7104,7136,7137,7123,7210,1294,1293,1300,1302,1307,1320,1303,1301,1305,1306,1055,1082,20702,20704,20700,20703,20705,20701,20401,20402,20400,20404,20405,20406,1071,1385,4502,4503,4500,4505,4504,20100,4501,1059,1650,1700,1702,1701,1007,1052,1053,1054,1560,1570,1285,1287,1420,1014,1072,1503,1380,1375,20102,3101,1200,1235,1222,1221,1205,1204,1203,1219,1230,1451,1220,1231,1225,1234,1232,3910,1400,3800,3000,3500,1253,1255,1256,1257,1272,1271,2501,2502,1280,2503,2504,1550,1500,1405,1406,1404,1407,1401,1402,1403,1270,1269,1267,1274,1268,1258,1473,3700,20150,1079,1469,1474,1800,1076,1078,20101,4012,4001,4005,4011,4003,4010,4006,4002,4000,1056,1283,20103,1246,1801,1247,1170,1075,1445,6000,1057,1062,1275,3950,1064,2900,1077,2901,1228,1179,1178,1180,1177,1176,1175,1571,1286,1288,7012,7010,7011,7018,7015,7016,7017,7002,7019,7001,7000,7005,1000,1020,1021,1001,1018,1025,1016,1017,1028,1027,1003,1015,1026,1002,1040,1066,1390,1152,1151,1157,1155,1150,1160,1171,1154,1163,1164,2800,1289,1242,1240,1304,1243,1241,5010,7701,7700,1551,1074,1008,1501,1118,1119,1117,1121,1100,1101,1102,1115,1108,1107,1130,1133,1132,1131,1129,1128,1122,1109,1112,1116,1114,1113,1110,1120,1103,1104,1111,1125,1126,1127,1105,1106,7750,1254,1760,1750,1461,1471,1462,1472,1470,1450,1578,1573,1036,3916,3915,1600,22010,2950,2001,1063,1552,2000,2953,2500,5000,1291,1290,1292,20403,1060,1065,1061,1199,1250,1251,1296,1295,1260,1035,1146,1138,1143,1139,1141,1140,1142,1137,1136,1134,1144,1013,1590,1210,1215,1216,1206,1207,1208,1209,1218,1217,1019,1580,1281,1006,1184,1181,1183,1182,1409,1408,1417,1415,1090,1159,1162,1310,1710,1711,3054,3053,3050,3055,3052,3056,3058,3057,3051,3080,8007,8004,8005,8000,8008,8001,8002,8006,8003,1202,1005,1010,1012,3900,1011,1572,1350,1237,1259,1051,1080,1081,1073,3944,1482,1480,3941,3940,3943,3942,2560,2561,2562,1049,1048,1045,1046,1047,7803,7800,7801,7802,7804,1421,1245,1252,1248,3100,22000,1446,6010,1050,1391,6020,1238,1236,1158,1161,1153,1156,1166,3600,1449,0,100030,100031,100027,100000,100020,100001,100009,100008,100015,100025,100002,100006,100007,904,901,903,902,900,201,852,853,850,851,801,502,250,800,504,505,62,51,57,54,980,52,53,500,509,501,85,80,270,970,72,71,70,65,950,251,930,200,50,516,510,511,512,515,802,803,351,352,300,66,960,400,405,350,503,830,831,857,855,856,854,63,710,705])
rescodetype = Enum("rescodetype", ["err","ok","trm","unk","wrn"], [3,0,2,4,1])
scalingtype = Enum("scalingtype", ["free","none"], [0,1])
scalingmethod = Enum("scalingmethod", ["free","pow2"], [1,0])
sensitivitytype = Enum("sensitivitytype", ["basis"], [0])
simseltype = Enum("simseltype", ["ase","devex","free","full","partial","se"], [2,3,0,1,5,4])
solitem = Enum("solitem", ["slc","slx","snx","suc","sux","xc","xx","y"], [3,5,7,4,6,0,1,2])
solsta = Enum("solsta", ["dual_feas","dual_illposed_cer","dual_infeas_cer","integer_optimal","optimal","prim_and_dual_feas","prim_feas","prim_illposed_cer","prim_infeas_cer","unknown"], [3,8,6,9,1,4,2,7,5,0])
soltype = Enum("soltype", ["bas","itg","itr"], [1,2,0])
solveform = Enum("solveform", ["dual","free","primal"], [2,0,1])
sparam = Enum("sparam", ["bas_sol_file_name","data_file_name","debug_file_name","int_sol_file_name","itr_sol_file_name","mio_debug_string","param_comment_sign","param_read_file_name","param_write_file_name","read_mps_bou_name","read_mps_obj_name","read_mps_ran_name","read_mps_rhs_name","remote_optserver_host","remote_tls_cert","remote_tls_cert_path","sensitivity_file_name","sensitivity_res_file_name","sol_filter_xc_low","sol_filter_xc_upr","sol_filter_xx_low","sol_filter_xx_upr","stat_key","stat_name","write_lp_gen_var_name"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
stakey = Enum("stakey", ["bas","fix","inf","low","supbas","unk","upr"], [1,5,6,3,2,0,4])
startpointtype = Enum("startpointtype", ["constant","free","guess","satisfy_bounds"], [2,0,1,3])
streamtype = Enum("streamtype", ["err","log","msg","wrn"], [2,0,1,3])
value = Enum("value", ["license_buffer_length","max_str_len"], [21,1024])
variabletype = Enum("variabletype", ["type_cont","type_int"], [0,1])




class Env:
  """
  The MOSEK environment.
  """
  def __init__(self,licensefile=None,debugfile=None,globalenv=False):
      self.__nativep = ctypes.c_void_p(0)
      self.__library = __library__

      debugfile = debugfile.encode('utf-8',errors="replace") if debugfile else None
      if not globalenv:
          res = self.__library.MSK_makeenv(ctypes.byref(self.__nativep),debugfile)
          if res != 0:
              raise Error(rescode(res),"Error %d" % res)
      try:
          if licensefile is not None:
              licensefile = licensefile.encode('utf-8',errors="replace")
              res = self.__library.MSK_putlicensepath(self.__nativep,licensefile)
              if res != 0:
                  raise Error(rescode(res),"Error %d" % res)

          # user stream functions:
          self.__stream_func   = 4 * [ None ]
          # strema proxy functions and wrappers:
          self.__stream_cb   = 4 * [ None ]
          for whichstream in range(4):
              # Note: Apparently closures doesn't work when the function is wrapped in a C function... So we use default parameter value instead.
              def stream_proxy(handle, msg, whichstream=whichstream):
                  func = self.__stream_func[whichstream]
                  try:
                      if func:
                          func(msg.decode('utf-8',errors="replace"))
                  except:
                      pass
              self.__stream_cb[whichstream] = __stream_cb_type__(stream_proxy)
          self.__enablegarcolenv()
      except:
          self.__library.MSK_deleteenv(ctypes.byref(self.__nativep))
          raise

  def __getlasterror(self,res):
      return rescode(res),""

  def set_Stream(self,whichstream,func):
      if isinstance(whichstream, streamtype):
          self.__stream_func[whichstream] = func
          if func is None:
              res = self.__library.MSK_linkfunctoenvstream(self.__nativep,whichstream,None,None)
          else:
              res = self.__library.MSK_linkfunctoenvstream(self.__nativep,whichstream,None,self.__stream_cb[whichstream])
      else:
          raise TypeError("Invalid stream %s" % whichstream)
  def __enablegarcolenv(self):
      if self.__nativep.value is not None:
        self.__library.MSK_enablegarcolenv(self.__nativep)

  def _getNativeP(self):
      return self.__nativep
  def __del__(self):
    if self.__nativep is not None:
      for f in feature.members():
        __library__.MSK_checkinlicense(self.__nativep,f)
      if self.__nativep.value is not None:
          self.__library.MSK_deleteenv(ctypes.byref(self.__nativep))
      del self.__stream_func
      del self.__stream_cb
      del self.__library
    self.__nativep  = None
  def Task(self,maxnumcon=0,maxnumvar=0):
    return Task(self,maxnumcon,maxnumvar)
  
  # Implementation of disposable protocol  
  def __enter__(self):
      return self

  def __exit__(self,exc_type,exc_value,traceback):
      self.__del__()
  def __optimizebatch_7(self,israce,maxtime,numthreads,task,trmcode,rcode):
    numtask = len(task) if task is not None else 0
    if task is not None:
      __tmp_1174 = (ctypes.c_void_p*len(task))()
      for __tmp_1176,__tmp_1175 in enumerate(task):
        __tmp_1174[__tmp_1176] = __tmp_1175._Task__nativep
    else:
      __tmp_1174 = None
    if trmcode is None:
      _tmparray_trmcode_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(trmcode) < numtask:
        raise ValueError("argument trmcode is too short")
      _tmparray_trmcode_ = (ctypes.c_int32*len(trmcode))()
    if rcode is None:
      _tmparray_rcode_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(rcode) < numtask:
        raise ValueError("argument rcode is too short")
      _tmparray_rcode_ = (ctypes.c_int32*len(rcode))()
    _res_optimizebatch = __library__.MSK_optimizebatch(self.__nativep,israce,maxtime,numthreads,numtask,__tmp_1174,_tmparray_trmcode_,_tmparray_rcode_)
    if _res_optimizebatch != 0:
      _,_msg_optimizebatch = self.__getlasterror(_res_optimizebatch)
      raise Error(rescode(_res_optimizebatch),_msg_optimizebatch)
    if trmcode is not None:
      for __tmp_1177,__tmp_1178 in enumerate(_tmparray_trmcode_):
        trmcode[__tmp_1177] = rescode(__tmp_1178)
    if rcode is not None:
      for __tmp_1179,__tmp_1180 in enumerate(_tmparray_rcode_):
        rcode[__tmp_1179] = rescode(__tmp_1180)
  def __optimizebatch_5(self,israce,maxtime,numthreads,task):
    numtask = len(task) if task is not None else 0
    if task is not None:
      __tmp_1181 = (ctypes.c_void_p*len(task))()
      for __tmp_1183,__tmp_1182 in enumerate(task):
        __tmp_1181[__tmp_1183] = __tmp_1182._Task__nativep
    else:
      __tmp_1181 = None
    _tmparray_trmcode_ = (ctypes.c_int32*numtask)()
    _tmparray_rcode_ = (ctypes.c_int32*numtask)()
    _res_optimizebatch = __library__.MSK_optimizebatch(self.__nativep,israce,maxtime,numthreads,numtask,__tmp_1181,_tmparray_trmcode_,_tmparray_rcode_)
    if _res_optimizebatch != 0:
      _,_msg_optimizebatch = self.__getlasterror(_res_optimizebatch)
      raise Error(rescode(_res_optimizebatch),_msg_optimizebatch)
    trmcode = list(map(lambda _i: rescode(_i),_tmparray_trmcode_))
    rcode = list(map(lambda _i: rescode(_i),_tmparray_rcode_))
    return (trmcode,rcode)
  def optimizebatch(self,*args,**kwds):
    """
    Optimize a number of tasks in parallel using a specified number of threads.
  
    optimizebatch(israce,
                  maxtime,
                  numthreads,
                  task,
                  trmcode,
                  rcode)
    optimizebatch(israce,maxtime,numthreads,task) -> (trmcode,rcode)
      [israce : bool]  If nonzero, then the function is terminated after the first task has been completed.  
      [maxtime : float64]  Time limit for the function.  
      [numthreads : int32]  Number of threads to be employed.  
      [rcode : array(mosek.rescode)]  The response code for each task.  
      [task : array(str)]  An array of tasks to optimize in parallel.  
      [trmcode : array(mosek.rescode)]  The termination code for each task.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 7: return self.__optimizebatch_7(*args,**kwds)
    elif len(args)+len(kwds)+1 == 5: return self.__optimizebatch_5(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __checkoutlicense_2(self,feature : feature):
    _res_checkoutlicense = __library__.MSK_checkoutlicense(self.__nativep,feature)
    if _res_checkoutlicense != 0:
      _,_msg_checkoutlicense = self.__getlasterror(_res_checkoutlicense)
      raise Error(rescode(_res_checkoutlicense),_msg_checkoutlicense)
  def checkoutlicense(self,*args,**kwds):
    """
    Check out a license feature from the license server ahead of time.
  
    checkoutlicense()
    """
    return self.__checkoutlicense_2(*args,**kwds)
  def __checkinlicense_2(self,feature : feature):
    _res_checkinlicense = __library__.MSK_checkinlicense(self.__nativep,feature)
    if _res_checkinlicense != 0:
      _,_msg_checkinlicense = self.__getlasterror(_res_checkinlicense)
      raise Error(rescode(_res_checkinlicense),_msg_checkinlicense)
  def checkinlicense(self,*args,**kwds):
    """
    Check in a license feature back to the license server ahead of time.
  
    checkinlicense()
    """
    return self.__checkinlicense_2(*args,**kwds)
  def __checkinall_1(self):
    _res_checkinall = __library__.MSK_checkinall(self.__nativep)
    if _res_checkinall != 0:
      _,_msg_checkinall = self.__getlasterror(_res_checkinall)
      raise Error(rescode(_res_checkinall),_msg_checkinall)
  def checkinall(self,*args,**kwds):
    """
    Check in all unused license features to the license token server.
  
    checkinall()
    """
    return self.__checkinall_1(*args,**kwds)
  def __expirylicenses_1(self):
    expiry_ = ctypes.c_int64()
    _res_expirylicenses = __library__.MSK_expirylicenses(self.__nativep,ctypes.byref(expiry_))
    if _res_expirylicenses != 0:
      _,_msg_expirylicenses = self.__getlasterror(_res_expirylicenses)
      raise Error(rescode(_res_expirylicenses),_msg_expirylicenses)
    expiry = expiry_.value
    return (expiry_.value)
  def expirylicenses(self,*args,**kwds):
    """
    Reports when the first license feature expires.
  
    expirylicenses() -> (expiry)
      [expiry : int64]  If nonnegative, then it is the minimum number days to expiry of any feature that has been checked out.  
    """
    return self.__expirylicenses_1(*args,**kwds)
  def __resetexpirylicenses_1(self):
    _res_resetexpirylicenses = __library__.MSK_resetexpirylicenses(self.__nativep)
    if _res_resetexpirylicenses != 0:
      _,_msg_resetexpirylicenses = self.__getlasterror(_res_resetexpirylicenses)
      raise Error(rescode(_res_resetexpirylicenses),_msg_resetexpirylicenses)
  def resetexpirylicenses(self,*args,**kwds):
    """
    Reset the license expiry reporting startpoint.
  
    resetexpirylicenses()
    """
    return self.__resetexpirylicenses_1(*args,**kwds)
  def __echointro_2(self,longver):
    _res_echointro = __library__.MSK_echointro(self.__nativep,longver)
    if _res_echointro != 0:
      _,_msg_echointro = self.__getlasterror(_res_echointro)
      raise Error(rescode(_res_echointro),_msg_echointro)
  def echointro(self,*args,**kwds):
    """
    Prints an intro to message stream.
  
    echointro(longver)
      [longver : int32]  If non-zero, then the intro is slightly longer.  
    """
    return self.__echointro_2(*args,**kwds)
  @staticmethod
  def __getcodedesc_1(code : rescode):
    symname = (ctypes.c_char*value.max_str_len)()
    str = (ctypes.c_char*value.max_str_len)()
    _res_getcodedesc = __library__.MSK_getcodedesc(code,symname,str)
    if _res_getcodedesc != 0:
      raise Error(rescode(_res_getcodedesc),"")
    return (symname.value.decode("utf-8",errors="ignore"),str.value.decode("utf-8",errors="ignore"))
  @staticmethod
  def getcodedesc(*args,**kwds):
    """
    Obtains a short description of a response code.
  
    getcodedesc() -> (symname,str)
      [str : str]  Obtains a short description of a response code.  
      [symname : str]  Symbolic name corresponding to the code.  
    """
    return Env.__getcodedesc_1(*args,**kwds)
  @staticmethod
  def __getversion_0():
    major_ = ctypes.c_int32()
    minor_ = ctypes.c_int32()
    revision_ = ctypes.c_int32()
    _res_getversion = __library__.MSK_getversion(ctypes.byref(major_),ctypes.byref(minor_),ctypes.byref(revision_))
    if _res_getversion != 0:
      raise Error(rescode(_res_getversion),"")
    major = major_.value
    minor = minor_.value
    revision = revision_.value
    return (major_.value,minor_.value,revision_.value)
  @staticmethod
  def getversion(*args,**kwds):
    """
    Obtains MOSEK version information.
  
    getversion() -> (major,minor,revision)
      [major : int32]  Major version number.  
      [minor : int32]  Minor version number.  
      [revision : int32]  Revision number.  
    """
    return Env.__getversion_0(*args,**kwds)
  def __linkfiletoenvstream_4(self,whichstream : streamtype,filename,append):
    _res_linkfiletoenvstream = __library__.MSK_linkfiletoenvstream(self.__nativep,whichstream,filename.encode("UTF-8"),append)
    if _res_linkfiletoenvstream != 0:
      _,_msg_linkfiletoenvstream = self.__getlasterror(_res_linkfiletoenvstream)
      raise Error(rescode(_res_linkfiletoenvstream),_msg_linkfiletoenvstream)
  def linkfiletostream(self,*args,**kwds):
    """
    Directs all output from a stream to a file.
  
    linkfiletostream(filename,append)
      [append : int32]  If this argument is 0 the file will be overwritten, otherwise it will be appended to.  
      [filename : str]  A valid file name.  
    """
    return self.__linkfiletoenvstream_4(*args,**kwds)
  def __putlicensedebug_2(self,licdebug):
    _res_putlicensedebug = __library__.MSK_putlicensedebug(self.__nativep,licdebug)
    if _res_putlicensedebug != 0:
      _,_msg_putlicensedebug = self.__getlasterror(_res_putlicensedebug)
      raise Error(rescode(_res_putlicensedebug),_msg_putlicensedebug)
  def putlicensedebug(self,*args,**kwds):
    """
    Enables debug information for the license system.
  
    putlicensedebug(licdebug)
      [licdebug : int32]  Enable output of license check-out debug information.  
    """
    return self.__putlicensedebug_2(*args,**kwds)
  def __putlicensecode_2(self,code):
    copyback_code = False
    if code is None:
      code_ = None
      _tmparray_code_ = None
    else:
      if len(code) < int(value.license_buffer_length):
        raise ValueError("argument code is too short")
      _tmparray_code_ = (ctypes.c_int32*len(code))(*code)
    _res_putlicensecode = __library__.MSK_putlicensecode(self.__nativep,_tmparray_code_)
    if _res_putlicensecode != 0:
      _,_msg_putlicensecode = self.__getlasterror(_res_putlicensecode)
      raise Error(rescode(_res_putlicensecode),_msg_putlicensecode)
  def putlicensecode(self,*args,**kwds):
    """
    Input a runtime license code.
  
    putlicensecode(code)
      [code : array(int32)]  A license key string.  
    """
    return self.__putlicensecode_2(*args,**kwds)
  def __putlicensewait_2(self,licwait):
    _res_putlicensewait = __library__.MSK_putlicensewait(self.__nativep,licwait)
    if _res_putlicensewait != 0:
      _,_msg_putlicensewait = self.__getlasterror(_res_putlicensewait)
      raise Error(rescode(_res_putlicensewait),_msg_putlicensewait)
  def putlicensewait(self,*args,**kwds):
    """
    Control whether mosek should wait for an available license if no license is available.
  
    putlicensewait(licwait)
      [licwait : int32]  Enable waiting for a license.  
    """
    return self.__putlicensewait_2(*args,**kwds)
  def __putlicensepath_2(self,licensepath):
    _res_putlicensepath = __library__.MSK_putlicensepath(self.__nativep,licensepath.encode("UTF-8"))
    if _res_putlicensepath != 0:
      _,_msg_putlicensepath = self.__getlasterror(_res_putlicensepath)
      raise Error(rescode(_res_putlicensepath),_msg_putlicensepath)
  def putlicensepath(self,*args,**kwds):
    """
    Set the path to the license file.
  
    putlicensepath(licensepath)
      [licensepath : str]  A path specifying where to search for the license.  
    """
    return self.__putlicensepath_2(*args,**kwds)
  def __axpy_5(self,n,alpha,x,y):
    copyback_x = False
    if x is None:
      x_ = None
      _tmparray_x_ = None
    else:
      if len(x) < int(n):
        raise ValueError("argument x is too short")
      _tmparray_x_ = (ctypes.c_double*len(x))(*x)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      if len(y) < int(n):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_axpy = __library__.MSK_axpy(self.__nativep,n,alpha,_tmparray_x_,_tmparray_y_)
    if _res_axpy != 0:
      _,_msg_axpy = self.__getlasterror(_res_axpy)
      raise Error(rescode(_res_axpy),_msg_axpy)
    if y is not None:
      for __tmp_1184,__tmp_1185 in enumerate(_tmparray_y_):
        y[__tmp_1184] = __tmp_1185
  def axpy(self,*args,**kwds):
    """
    Computes vector addition and multiplication by a scalar.
  
    axpy(n,alpha,x,y)
      [alpha : float64]  The scalar that multiplies x.  
      [n : int32]  Length of the vectors.  
      [x : array(float64)]  The x vector.  
      [y : array(float64)]  The y vector.  
    """
    return self.__axpy_5(*args,**kwds)
  def __dot_4(self,n,x,y):
    copyback_x = False
    if x is None:
      x_ = None
      _tmparray_x_ = None
    else:
      if len(x) < int(n):
        raise ValueError("argument x is too short")
      _tmparray_x_ = (ctypes.c_double*len(x))(*x)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      if len(y) < int(n):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    xty_ = ctypes.c_double()
    _res_dot = __library__.MSK_dot(self.__nativep,n,_tmparray_x_,_tmparray_y_,ctypes.byref(xty_))
    if _res_dot != 0:
      _,_msg_dot = self.__getlasterror(_res_dot)
      raise Error(rescode(_res_dot),_msg_dot)
    xty = xty_.value
    return (xty_.value)
  def dot(self,*args,**kwds):
    """
    Computes the inner product of two vectors.
  
    dot(n,x,y) -> (xty)
      [n : int32]  Length of the vectors.  
      [x : array(float64)]  The x vector.  
      [xty : float64]  The result of the inner product.  
      [y : array(float64)]  The y vector.  
    """
    return self.__dot_4(*args,**kwds)
  def __gemv_9(self,transa : transpose,m,n,alpha,a,x,beta,y):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * m)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    copyback_x = False
    if x is None:
      x_ = None
      _tmparray_x_ = None
    else:
      if len(x) < int((n if (transa == transpose.no) else m)):
        raise ValueError("argument x is too short")
      _tmparray_x_ = (ctypes.c_double*len(x))(*x)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      if len(y) < int((m if (transa == transpose.no) else n)):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_gemv = __library__.MSK_gemv(self.__nativep,transa,m,n,alpha,_tmparray_a_,_tmparray_x_,beta,_tmparray_y_)
    if _res_gemv != 0:
      _,_msg_gemv = self.__getlasterror(_res_gemv)
      raise Error(rescode(_res_gemv),_msg_gemv)
    if y is not None:
      for __tmp_1188,__tmp_1189 in enumerate(_tmparray_y_):
        y[__tmp_1188] = __tmp_1189
  def gemv(self,*args,**kwds):
    """
    Computes dense matrix times a dense vector product.
  
    gemv(m,n,alpha,a,x,beta,y)
      [a : array(float64)]  A pointer to the array storing matrix A in a column-major format.  
      [alpha : float64]  A scalar value multiplying the matrix A.  
      [beta : float64]  A scalar value multiplying the vector y.  
      [m : int32]  Specifies the number of rows of the matrix A.  
      [n : int32]  Specifies the number of columns of the matrix A.  
      [x : array(float64)]  A pointer to the array storing the vector x.  
      [y : array(float64)]  A pointer to the array storing the vector y.  
    """
    return self.__gemv_9(*args,**kwds)
  def __gemm_11(self,transa : transpose,transb : transpose,m,n,k,alpha,a,b,beta,c):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((m * k)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int((k * n)):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      if len(c) < int((m * n)):
        raise ValueError("argument c is too short")
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    _res_gemm = __library__.MSK_gemm(self.__nativep,transa,transb,m,n,k,alpha,_tmparray_a_,_tmparray_b_,beta,_tmparray_c_)
    if _res_gemm != 0:
      _,_msg_gemm = self.__getlasterror(_res_gemm)
      raise Error(rescode(_res_gemm),_msg_gemm)
    if c is not None:
      for __tmp_1192,__tmp_1193 in enumerate(_tmparray_c_):
        c[__tmp_1192] = __tmp_1193
  def gemm(self,*args,**kwds):
    """
    Performs a dense matrix multiplication.
  
    gemm(m,n,k,alpha,a,b,beta,c)
      [a : array(float64)]  The pointer to the array storing matrix A in a column-major format.  
      [alpha : float64]  A scalar value multiplying the result of the matrix multiplication.  
      [b : array(float64)]  The pointer to the array storing matrix B in a column-major format.  
      [beta : float64]  A scalar value that multiplies C.  
      [c : array(float64)]  The pointer to the array storing matrix C in a column-major format.  
      [k : int32]  Specifies the common dimension along which op(A) and op(B) are multiplied.  
      [m : int32]  Indicates the number of rows of matrix C.  
      [n : int32]  Indicates the number of columns of matrix C.  
    """
    return self.__gemm_11(*args,**kwds)
  def __syrk_9(self,uplo : uplo,trans : transpose,n,k,alpha,a,beta,c):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * k)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      if len(c) < int((n * n)):
        raise ValueError("argument c is too short")
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    _res_syrk = __library__.MSK_syrk(self.__nativep,uplo,trans,n,k,alpha,_tmparray_a_,beta,_tmparray_c_)
    if _res_syrk != 0:
      _,_msg_syrk = self.__getlasterror(_res_syrk)
      raise Error(rescode(_res_syrk),_msg_syrk)
    if c is not None:
      for __tmp_1196,__tmp_1197 in enumerate(_tmparray_c_):
        c[__tmp_1196] = __tmp_1197
  def syrk(self,*args,**kwds):
    """
    Performs a rank-k update of a symmetric matrix.
  
    syrk(n,k,alpha,a,beta,c)
      [a : array(float64)]  The pointer to the array storing matrix A in a column-major format.  
      [alpha : float64]  A scalar value multiplying the result of the matrix multiplication.  
      [beta : float64]  A scalar value that multiplies C.  
      [c : array(float64)]  The pointer to the array storing matrix C in a column-major format.  
      [k : int32]  Indicates the number of rows or columns of A, and its rank.  
      [n : int32]  Specifies the order of C.  
    """
    return self.__syrk_9(*args,**kwds)
  def __computesparsecholesky_8(self,numthreads,ordermethod,tolsingular,anzc,aptrc,asubc,avalc):
    n = min(len(anzc) if anzc is not None else 0,len(aptrc) if aptrc is not None else 0)
    copyback_anzc = False
    if anzc is None:
      anzc_ = None
      _tmparray_anzc_ = None
    else:
      _tmparray_anzc_ = (ctypes.c_int32*len(anzc))(*anzc)
    copyback_aptrc = False
    if aptrc is None:
      aptrc_ = None
      _tmparray_aptrc_ = None
    else:
      _tmparray_aptrc_ = (ctypes.c_int64*len(aptrc))(*aptrc)
    copyback_asubc = False
    if asubc is None:
      asubc_ = None
      _tmparray_asubc_ = None
    else:
      _tmparray_asubc_ = (ctypes.c_int32*len(asubc))(*asubc)
    copyback_avalc = False
    if avalc is None:
      avalc_ = None
      _tmparray_avalc_ = None
    else:
      _tmparray_avalc_ = (ctypes.c_double*len(avalc))(*avalc)
    perm = ctypes.POINTER(ctypes.c_int32)()
    diag = ctypes.POINTER(ctypes.c_double)()
    lnzc = ctypes.POINTER(ctypes.c_int32)()
    lptrc = ctypes.POINTER(ctypes.c_int64)()
    lensubnval_ = ctypes.c_int64()
    lsubc = ctypes.POINTER(ctypes.c_int32)()
    lvalc = ctypes.POINTER(ctypes.c_double)()
    _res_computesparsecholesky = __library__.MSK_computesparsecholesky(self.__nativep,numthreads,ordermethod,tolsingular,n,_tmparray_anzc_,_tmparray_aptrc_,_tmparray_asubc_,_tmparray_avalc_,ctypes.byref(perm),ctypes.byref(diag),ctypes.byref(lnzc),ctypes.byref(lptrc),ctypes.byref(lensubnval_),ctypes.byref(lsubc),ctypes.byref(lvalc))
    if _res_computesparsecholesky != 0:
      _,_msg_computesparsecholesky = self.__getlasterror(_res_computesparsecholesky)
      raise Error(rescode(_res_computesparsecholesky),_msg_computesparsecholesky)
    perm_len = n
    perm_res = numpy.array(perm[:perm_len],numpy.int32)
    __library__.MSK_freeenv(self.__nativep,perm)
    diag_len = n
    diag_res = numpy.array(diag[:diag_len],numpy.float64)
    __library__.MSK_freeenv(self.__nativep,diag)
    lnzc_len = n
    lnzc_res = numpy.array(lnzc[:lnzc_len],numpy.int32)
    __library__.MSK_freeenv(self.__nativep,lnzc)
    lptrc_len = n
    lptrc_res = numpy.array(lptrc[:lptrc_len],numpy.int64)
    __library__.MSK_freeenv(self.__nativep,lptrc)
    lensubnval = lensubnval_.value
    lsubc_len = lensubnval
    lsubc_res = numpy.array(lsubc[:lsubc_len],numpy.int32)
    __library__.MSK_freeenv(self.__nativep,lsubc)
    lvalc_len = lensubnval
    lvalc_res = numpy.array(lvalc[:lvalc_len],numpy.float64)
    __library__.MSK_freeenv(self.__nativep,lvalc)
    return (perm_res,diag_res,lnzc_res,lptrc_res,lensubnval_.value,lsubc_res,lvalc_res)
  def computesparsecholesky(self,*args,**kwds):
    """
    Computes a Cholesky factorization of sparse matrix.
  
    computesparsecholesky(numthreads,
                          ordermethod,
                          tolsingular,
                          anzc,
                          aptrc,
                          asubc,
                          avalc) -> 
                         (perm,
                          diag,
                          lnzc,
                          lptrc,
                          lensubnval,
                          lsubc,
                          lvalc)
      [anzc : array(int32)]  anzc[j] is the number of nonzeros in the jth column of A.  
      [aptrc : array(int64)]  aptrc[j] is a pointer to the first element in column j.  
      [asubc : array(int32)]  Row indexes for each column stored in increasing order.  
      [avalc : array(float64)]  The value corresponding to row indexed stored in asubc.  
      [diag : array(float64)]  The diagonal elements of matrix D.  
      [lensubnval : int64]  Number of elements in lsubc and lvalc.  
      [lnzc : array(int32)]  lnzc[j] is the number of non zero elements in column j.  
      [lptrc : array(int64)]  lptrc[j] is a pointer to the first row index and value in column j.  
      [lsubc : array(int32)]  Row indexes for each column stored in increasing order.  
      [lvalc : array(float64)]  The values corresponding to row indexed stored in lsubc.  
      [numthreads : int32]  The number threads that can be used to do the computation. 0 means the code makes the choice.  
      [ordermethod : int32]  If nonzero, then a sparsity preserving ordering will be employed.  
      [perm : array(int32)]  Permutation array used to specify the permutation matrix P computed by the function.  
      [tolsingular : float64]  A positive parameter controlling when a pivot is declared zero.  
    """
    return self.__computesparsecholesky_8(*args,**kwds)
  def __sparsetriangularsolvedense_7(self,transposed : transpose,lnzc,lptrc,lsubc,lvalc,b):
    n = min(len(b) if b is not None else 0,len(lnzc) if lnzc is not None else 0,len(lptrc) if lptrc is not None else 0)
    copyback_lnzc = False
    if lnzc is None:
      lnzc_ = None
      _tmparray_lnzc_ = None
    else:
      if len(lnzc) < int(n):
        raise ValueError("argument lnzc is too short")
      _tmparray_lnzc_ = (ctypes.c_int32*len(lnzc))(*lnzc)
    copyback_lptrc = False
    if lptrc is None:
      lptrc_ = None
      _tmparray_lptrc_ = None
    else:
      if len(lptrc) < int(n):
        raise ValueError("argument lptrc is too short")
      _tmparray_lptrc_ = (ctypes.c_int64*len(lptrc))(*lptrc)
    lensubnval = min(len(lsubc) if lsubc is not None else 0,len(lvalc) if lvalc is not None else 0)
    copyback_lsubc = False
    if lsubc is None:
      lsubc_ = None
      _tmparray_lsubc_ = None
    else:
      if len(lsubc) < int(lensubnval):
        raise ValueError("argument lsubc is too short")
      _tmparray_lsubc_ = (ctypes.c_int32*len(lsubc))(*lsubc)
    copyback_lvalc = False
    if lvalc is None:
      lvalc_ = None
      _tmparray_lvalc_ = None
    else:
      if len(lvalc) < int(lensubnval):
        raise ValueError("argument lvalc is too short")
      _tmparray_lvalc_ = (ctypes.c_double*len(lvalc))(*lvalc)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(n):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_sparsetriangularsolvedense = __library__.MSK_sparsetriangularsolvedense(self.__nativep,transposed,n,_tmparray_lnzc_,_tmparray_lptrc_,lensubnval,_tmparray_lsubc_,_tmparray_lvalc_,_tmparray_b_)
    if _res_sparsetriangularsolvedense != 0:
      _,_msg_sparsetriangularsolvedense = self.__getlasterror(_res_sparsetriangularsolvedense)
      raise Error(rescode(_res_sparsetriangularsolvedense),_msg_sparsetriangularsolvedense)
    if b is not None:
      for __tmp_1200,__tmp_1201 in enumerate(_tmparray_b_):
        b[__tmp_1200] = __tmp_1201
  def sparsetriangularsolvedense(self,*args,**kwds):
    """
    Solves a sparse triangular system of linear equations.
  
    sparsetriangularsolvedense(lnzc,lptrc,lsubc,lvalc,b)
      [b : array(float64)]  The right-hand side of linear equation system to be solved as a dense vector.  
      [lnzc : array(int32)]  lnzc[j] is the number of nonzeros in column j.  
      [lptrc : array(int64)]  lptrc[j] is a pointer to the first row index and value in column j.  
      [lsubc : array(int32)]  Row indexes for each column stored sequentially.  
      [lvalc : array(float64)]  The value corresponding to row indexed stored lsubc.  
    """
    return self.__sparsetriangularsolvedense_7(*args,**kwds)
  def __potrf_4(self,uplo : uplo,n,a):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * n)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    _res_potrf = __library__.MSK_potrf(self.__nativep,uplo,n,_tmparray_a_)
    if _res_potrf != 0:
      _,_msg_potrf = self.__getlasterror(_res_potrf)
      raise Error(rescode(_res_potrf),_msg_potrf)
    if a is not None:
      for __tmp_1204,__tmp_1205 in enumerate(_tmparray_a_):
        a[__tmp_1204] = __tmp_1205
  def potrf(self,*args,**kwds):
    """
    Computes a Cholesky factorization of a dense matrix.
  
    potrf(n,a)
      [a : array(float64)]  A symmetric matrix stored in column-major order.  
      [n : int32]  Dimension of the symmetric matrix.  
    """
    return self.__potrf_4(*args,**kwds)
  def __syeig_5(self,uplo : uplo,n,a,w):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * n)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    copyback_w = False
    if w is None:
      w_ = None
      _tmparray_w_ = None
    else:
      if len(w) < int(n):
        raise ValueError("argument w is too short")
      _tmparray_w_ = (ctypes.c_double*len(w))(*w)
    _res_syeig = __library__.MSK_syeig(self.__nativep,uplo,n,_tmparray_a_,_tmparray_w_)
    if _res_syeig != 0:
      _,_msg_syeig = self.__getlasterror(_res_syeig)
      raise Error(rescode(_res_syeig),_msg_syeig)
    if w is not None:
      for __tmp_1208,__tmp_1209 in enumerate(_tmparray_w_):
        w[__tmp_1208] = __tmp_1209
  def __syeig_4(self,uplo : uplo,n,a):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * n)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    w = numpy.zeros(n,numpy.float64)
    _res_syeig = __library__.MSK_syeig(self.__nativep,uplo,n,_tmparray_a_,ctypes.cast(w.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_syeig != 0:
      _,_msg_syeig = self.__getlasterror(_res_syeig)
      raise Error(rescode(_res_syeig),_msg_syeig)
    return (w)
  def syeig(self,*args,**kwds):
    """
    Computes all eigenvalues of a symmetric dense matrix.
  
    syeig(n,a,w)
    syeig(n,a) -> (w)
      [a : array(float64)]  Input matrix A.  
      [n : int32]  Dimension of the symmetric input matrix.  
      [w : array(float64)]  Array of length at least n containing the eigenvalues of A.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__syeig_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__syeig_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __syevd_5(self,uplo : uplo,n,a,w):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * n)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    copyback_w = False
    if w is None:
      w_ = None
      _tmparray_w_ = None
    else:
      if len(w) < int(n):
        raise ValueError("argument w is too short")
      _tmparray_w_ = (ctypes.c_double*len(w))(*w)
    _res_syevd = __library__.MSK_syevd(self.__nativep,uplo,n,_tmparray_a_,_tmparray_w_)
    if _res_syevd != 0:
      _,_msg_syevd = self.__getlasterror(_res_syevd)
      raise Error(rescode(_res_syevd),_msg_syevd)
    if a is not None:
      for __tmp_1211,__tmp_1212 in enumerate(_tmparray_a_):
        a[__tmp_1211] = __tmp_1212
    if w is not None:
      for __tmp_1213,__tmp_1214 in enumerate(_tmparray_w_):
        w[__tmp_1213] = __tmp_1214
  def __syevd_4(self,uplo : uplo,n,a):
    copyback_a = False
    if a is None:
      a_ = None
      _tmparray_a_ = None
    else:
      if len(a) < int((n * n)):
        raise ValueError("argument a is too short")
      _tmparray_a_ = (ctypes.c_double*len(a))(*a)
    w = numpy.zeros(n,numpy.float64)
    _res_syevd = __library__.MSK_syevd(self.__nativep,uplo,n,_tmparray_a_,ctypes.cast(w.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_syevd != 0:
      _,_msg_syevd = self.__getlasterror(_res_syevd)
      raise Error(rescode(_res_syevd),_msg_syevd)
    if a is not None:
      for __tmp_1215,__tmp_1216 in enumerate(_tmparray_a_):
        a[__tmp_1215] = __tmp_1216
    return (w)
  def syevd(self,*args,**kwds):
    """
    Computes all the eigenvalues and eigenvectors of a symmetric dense matrix, and thus its eigenvalue decomposition.
  
    syevd(n,a,w)
    syevd(n,a) -> (w)
      [a : array(float64)]  Input matrix A.  
      [n : int32]  Dimension of the symmetric input matrix.  
      [w : array(float64)]  Array of length at least n containing the eigenvalues of A.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__syevd_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__syevd_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  @staticmethod
  def __licensecleanup_0():
    _res_licensecleanup = __library__.MSK_licensecleanup()
    if _res_licensecleanup != 0:
      raise Error(rescode(_res_licensecleanup),"")
  @staticmethod
  def licensecleanup(*args,**kwds):
    """
    Stops all threads and delete all handles used by the license system.
  
    licensecleanup()
    """
    return Env.__licensecleanup_0(*args,**kwds)


class Task:
  """
  The MOSEK task class. This object contains information about one optimization problem.
  """
  
  def __init__(self,env=None,maxnumcon=0,maxnumvar=0,nativep=None,other=None):
      """
      Construct a new Task object.
      
      Task(env=None,maxnumcon=0,maxnumvar=0,nativep=None,other=None)
        env: mosek.Env. 
        maxnumcon: int. Reserve space for this number of constraints. Default is 0. 
        maxnumcvar: int. Reserve space for this number of variables. Default is 0. 
        nativep: native pointer. For internal use only.
        other: mosek.Task. Another task.
      
      Valid usage:
        Specifying "env", and optionally "maxnumcon" and "maxnumvar" will create a new Task.
        Specifying "nativep" will create a new Task from the native mosek task defined by the pointer.
        Specifying "other" will create a new Task as a copy of the other task. 
      """
      self.__library = __library__
      self__nativep = None

      if isinstance(env,Task):
          other = env
          env = None
      
      try: 
          if nativep is not None:
              self.__nativep = nativep
              res = 0
          elif other is not None:
              self.__nativep = ctypes.c_void_p()
              res = self.__library.MSK_clonetask(other.__nativep, ctypes.byref(self.__nativep))
          elif env is None:
              self.__nativep = ctypes.c_void_p()
              res = self.__library.MSK_maketask(None,maxnumcon,maxnumvar,ctypes.byref(self.__nativep))
          elif isinstance(env,Env):
              self.__nativep = ctypes.c_void_p()
              res = self.__library.MSK_maketask(env._getNativeP(),maxnumcon,maxnumvar,ctypes.byref(self.__nativep))
          else:
              raise TypeError('Expected an Env for argument')
          if res != 0:
              raise Error(rescode(res),"Error %d" % res)

          # user progress function:
          self.__progress_func = None
          self.__infocallback_func = None
          # callback proxy function definition:

          def progress_proxy(nativep, handle, caller, dinfptr, iinfptr, liinfptr):
              r = 0
              try:
                  caller = callbackcode(caller)
                  f = self.__infocallback_func
                  if f is not None:
                      r = f(caller,
                            ctypes.cast(dinfptr, ctypes.POINTER(ctypes.c_double))[:len(dinfitem._values)]    if dinfptr  is not None else None,
                            ctypes.cast(iinfptr, ctypes.POINTER(ctypes.c_int))[:len(iinfitem._values)]       if iinfptr  is not None else None,
                            ctypes.cast(liinfptr,ctypes.POINTER(ctypes.c_longlong))[:len(liinfitem._values)] if liinfptr is not None else None,
                        )
                  f = self.__progress_func
                  if f is not None:
                      r = f(caller)
                  if not isinstance(r,int):
                      r = 0
              except:
                  import traceback
                  traceback.print_exc()
                  return -1
              return r

          # callback proxy C wrapper:
          self.__progress_cb = __progress_cb_type__(progress_proxy)
        
          # user stream functions: 
          self.__stream_func   = 4 * [ None ]
          # stream proxy functions and wrappers:
          self.__stream_cb   = 4 * [ None ]
          for whichstream in range(4): 
              # Note: Apparently closures doesn't work when the function is wrapped in a C function... So we use default parameter value instead.
              def stream_proxy(handle, msg, whichstream=whichstream):                  
                  func = self.__stream_func[whichstream]
                  if func is not None: func = func 
                  if func is not None:
                    try:
                        func(msg.decode('utf-8',errors="replace"))
                    except:
                        pass
              self.__stream_cb[whichstream] = __stream_cb_type__(stream_proxy)
          assert self.__nativep
          self.__schandle = None
      except:
          if hasattr(self,'_Task__nativep') and self.__nativep is not None:
              self.__library.MSK_deletetask(ctypes.byref(self.__nativep))
              self.__nativep = None
          raise
      
  def __del__(self):
      if self.__nativep is not None:
          self.__library.MSK_deletetask(ctypes.byref(self.__nativep))
          del self.__library
          del self.__schandle
          del self.__progress_func
          del self.__progress_cb
          del self.__stream_func
          del self.__stream_cb
      self.__nativep = None
  
  def __enter__(self):
      return self

  def __exit__(self,exc_type,exc_value,traceback):
      self.__del__()

  def __getlasterror(self,res):
      msglen = ctypes.c_int64(1024)
      lasterr = ctypes.c_int()
      r = self.__library.MSK_getlasterror64(self.__nativep, ctypes.byref(lasterr), 0, ctypes.byref(msglen),None)
      if r == 0:
          #msg = (ctypes.c_char * (msglen.value+1))()
          len = (msglen.value+1)
          msg = ctypes.create_string_buffer(len)
          r = self.__library.MSK_getlasterror64(self.__nativep, ctypes.byref(lasterr), len, None,msg)
          if r == 0:
              result,msg = lasterr.value,msg.value.decode('utf-8',errors="replace")
          else:
              result,msg = lasterr.value,''
      else:
          result,msg = res,''
      return result,msg


  def set_Progress(self,func):
      """
      Set the progress callback function. If func is None, progress callbacks are detached and disabled.
      """
      if func is None:
          self.__progress_func = None
          #res = self.__library.MSK_putcallbackfunc(self.__nativep,None,None)
      else:
          self.__progress_func = func
          res = self.__library.MSK_putcallbackfunc(self.__nativep,self.__progress_cb,None)

  def set_InfoCallback(self,func):
      """
      Set the progress callback function. If func is None, progress
      callbacks are detached and disabled.
      """
      if func is None:
          self.__infocallback_func = None
          #res = self.__library.MSK_putcallbackfunc(self.__nativep,None,None)
      else:
          self.__infocallback_func = func
          res = self.__library.MSK_putcallbackfunc(self.__nativep,self.__progress_cb,None)
          
  def set_Stream(self,whichstream,func):
      if isinstance(whichstream, streamtype):
          if func is None:
              self.__stream_func[whichstream] = None
              res = self.__library.MSK_linkfunctotaskstream(self.__nativep,whichstream,None,ctypes.cast(None,__stream_cb_type__))
          else:
              self.__stream_func[whichstream] = func
              res = self.__library.MSK_linkfunctotaskstream(self.__nativep,whichstream,None,self.__stream_cb[whichstream])
      else:
          raise TypeError("Invalid stream %s" % whichstream)

  def writedatastream(self,dformat,compress,stream):
      if   not isinstance(dformat, dataformat):
          raise TypeError("Invalid data format %s" % dformat)
      elif not isinstance(compress,compresstype):
          raise TypeError("Invalid compression format %s" % compress)
      else:
          def write_proxy(handle, buffer, count):
              if stream is not None:
                try:
                    stream.write(bytes((ctypes.c_ubyte*count).from_address(buffer)))
                except:
                    pass
              return count
          res = self.__library.MSK_writedatahandle(self.__nativep,__write_cb_type__(write_proxy),None,dformat,compress)
          if res != 0:
            _,msg = self.__getlasterror(res)
            raise Error(rescode(res),msg)

  def __analyzeproblem_2(self,whichstream : streamtype):
    _res_analyzeproblem = __library__.MSK_analyzeproblem(self.__nativep,whichstream)
    if _res_analyzeproblem != 0:
      _,_msg_analyzeproblem = self.__getlasterror(_res_analyzeproblem)
      raise Error(rescode(_res_analyzeproblem),_msg_analyzeproblem)
  def analyzeproblem(self,*args,**kwds):
    """
    Analyze the data of a task.
  
    analyzeproblem()
    """
    return self.__analyzeproblem_2(*args,**kwds)
  def __analyzenames_3(self,whichstream : streamtype,nametype : nametype):
    _res_analyzenames = __library__.MSK_analyzenames(self.__nativep,whichstream,nametype)
    if _res_analyzenames != 0:
      _,_msg_analyzenames = self.__getlasterror(_res_analyzenames)
      raise Error(rescode(_res_analyzenames),_msg_analyzenames)
  def analyzenames(self,*args,**kwds):
    """
    Analyze the names and issue an error for the first invalid name.
  
    analyzenames()
    """
    return self.__analyzenames_3(*args,**kwds)
  def __analyzesolution_3(self,whichstream : streamtype,whichsol : soltype):
    _res_analyzesolution = __library__.MSK_analyzesolution(self.__nativep,whichstream,whichsol)
    if _res_analyzesolution != 0:
      _,_msg_analyzesolution = self.__getlasterror(_res_analyzesolution)
      raise Error(rescode(_res_analyzesolution),_msg_analyzesolution)
  def analyzesolution(self,*args,**kwds):
    """
    Print information related to the quality of the solution.
  
    analyzesolution()
    """
    return self.__analyzesolution_3(*args,**kwds)
  def __initbasissolve_2(self,basis):
    copyback_basis = False
    if basis is None:
      basis_ = None
      _tmparray_basis_ = None
    else:
      __tmp_0 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_0))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(basis) < int(__tmp_0.value):
        raise ValueError("argument basis is too short")
      _tmparray_basis_ = (ctypes.c_int32*len(basis))(*basis)
    _res_initbasissolve = __library__.MSK_initbasissolve(self.__nativep,_tmparray_basis_)
    if _res_initbasissolve != 0:
      _,_msg_initbasissolve = self.__getlasterror(_res_initbasissolve)
      raise Error(rescode(_res_initbasissolve),_msg_initbasissolve)
    if basis is not None:
      for __tmp_2,__tmp_3 in enumerate(_tmparray_basis_):
        basis[__tmp_2] = __tmp_3
  def __initbasissolve_1(self):
    __tmp_4 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_4))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    basis = numpy.zeros(__tmp_4.value,numpy.int32)
    _res_initbasissolve = __library__.MSK_initbasissolve(self.__nativep,ctypes.cast(basis.ctypes,ctypes.POINTER(ctypes.c_int32)))
    if _res_initbasissolve != 0:
      _,_msg_initbasissolve = self.__getlasterror(_res_initbasissolve)
      raise Error(rescode(_res_initbasissolve),_msg_initbasissolve)
    return (basis)
  def initbasissolve(self,*args,**kwds):
    """
    Prepare a task for basis solver.
  
    initbasissolve(basis)
    initbasissolve() -> (basis)
      [basis : array(int32)]  The array of basis indexes to use.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__initbasissolve_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__initbasissolve_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __solvewithbasis_5(self,transp,numnz,sub,val):
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      __tmp_7 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_7))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(sub) < int(__tmp_7.value):
        raise ValueError("argument sub is too short")
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      __tmp_11 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_11))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(val) < int(__tmp_11.value):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    numnzout_ = ctypes.c_int32()
    _res_solvewithbasis = __library__.MSK_solvewithbasis(self.__nativep,transp,numnz,_tmparray_sub_,_tmparray_val_,ctypes.byref(numnzout_))
    if _res_solvewithbasis != 0:
      _,_msg_solvewithbasis = self.__getlasterror(_res_solvewithbasis)
      raise Error(rescode(_res_solvewithbasis),_msg_solvewithbasis)
    if sub is not None:
      for __tmp_9,__tmp_10 in enumerate(_tmparray_sub_):
        sub[__tmp_9] = __tmp_10
    if val is not None:
      for __tmp_13,__tmp_14 in enumerate(_tmparray_val_):
        val[__tmp_13] = __tmp_14
    numnzout = numnzout_.value
    return (numnzout_.value)
  def solvewithbasis(self,*args,**kwds):
    """
    Solve a linear equation system involving a basis matrix.
  
    solvewithbasis(transp,numnz,sub,val) -> (numnzout)
      [numnz : int32]  Input (number of non-zeros in right-hand side).  
      [numnzout : int32]  Output (number of non-zeros in solution vector).  
      [sub : array(int32)]  Input (indexes of non-zeros in right-hand side) and output (indexes of non-zeros in solution vector).  
      [transp : bool]  Controls which problem formulation is solved.  
      [val : array(float64)]  Input (right-hand side values) and output (solution vector values).  
    """
    return self.__solvewithbasis_5(*args,**kwds)
  def __basiscond_1(self):
    nrmbasis_ = ctypes.c_double()
    nrminvbasis_ = ctypes.c_double()
    _res_basiscond = __library__.MSK_basiscond(self.__nativep,ctypes.byref(nrmbasis_),ctypes.byref(nrminvbasis_))
    if _res_basiscond != 0:
      _,_msg_basiscond = self.__getlasterror(_res_basiscond)
      raise Error(rescode(_res_basiscond),_msg_basiscond)
    nrmbasis = nrmbasis_.value
    nrminvbasis = nrminvbasis_.value
    return (nrmbasis_.value,nrminvbasis_.value)
  def basiscond(self,*args,**kwds):
    """
    Computes conditioning information for the basis matrix.
  
    basiscond() -> (nrmbasis,nrminvbasis)
      [nrmbasis : float64]  An estimate for the 1-norm of the basis.  
      [nrminvbasis : float64]  An estimate for the 1-norm of the inverse of the basis.  
    """
    return self.__basiscond_1(*args,**kwds)
  def __appendcons_2(self,num):
    _res_appendcons = __library__.MSK_appendcons(self.__nativep,num)
    if _res_appendcons != 0:
      _,_msg_appendcons = self.__getlasterror(_res_appendcons)
      raise Error(rescode(_res_appendcons),_msg_appendcons)
  def appendcons(self,*args,**kwds):
    """
    Appends a number of constraints to the optimization task.
  
    appendcons(num)
      [num : int32]  Number of constraints which should be appended.  
    """
    return self.__appendcons_2(*args,**kwds)
  def __appendvars_2(self,num):
    _res_appendvars = __library__.MSK_appendvars(self.__nativep,num)
    if _res_appendvars != 0:
      _,_msg_appendvars = self.__getlasterror(_res_appendvars)
      raise Error(rescode(_res_appendvars),_msg_appendvars)
  def appendvars(self,*args,**kwds):
    """
    Appends a number of variables to the optimization task.
  
    appendvars(num)
      [num : int32]  Number of variables which should be appended.  
    """
    return self.__appendvars_2(*args,**kwds)
  def __removecons_2(self,subset):
    num = len(subset) if subset is not None else 0
    copyback_subset = False
    if subset is None:
      subset_ = None
      _tmparray_subset_ = None
    else:
      _tmparray_subset_ = (ctypes.c_int32*len(subset))(*subset)
    _res_removecons = __library__.MSK_removecons(self.__nativep,num,_tmparray_subset_)
    if _res_removecons != 0:
      _,_msg_removecons = self.__getlasterror(_res_removecons)
      raise Error(rescode(_res_removecons),_msg_removecons)
  def removecons(self,*args,**kwds):
    """
    Removes a number of constraints.
  
    removecons(subset)
      [subset : array(int32)]  Indexes of constraints which should be removed.  
    """
    return self.__removecons_2(*args,**kwds)
  def __removevars_2(self,subset):
    num = len(subset) if subset is not None else 0
    copyback_subset = False
    if subset is None:
      subset_ = None
      _tmparray_subset_ = None
    else:
      _tmparray_subset_ = (ctypes.c_int32*len(subset))(*subset)
    _res_removevars = __library__.MSK_removevars(self.__nativep,num,_tmparray_subset_)
    if _res_removevars != 0:
      _,_msg_removevars = self.__getlasterror(_res_removevars)
      raise Error(rescode(_res_removevars),_msg_removevars)
  def removevars(self,*args,**kwds):
    """
    Removes a number of variables.
  
    removevars(subset)
      [subset : array(int32)]  Indexes of variables which should be removed.  
    """
    return self.__removevars_2(*args,**kwds)
  def __removebarvars_2(self,subset):
    num = len(subset) if subset is not None else 0
    copyback_subset = False
    if subset is None:
      subset_ = None
      _tmparray_subset_ = None
    else:
      _tmparray_subset_ = (ctypes.c_int32*len(subset))(*subset)
    _res_removebarvars = __library__.MSK_removebarvars(self.__nativep,num,_tmparray_subset_)
    if _res_removebarvars != 0:
      _,_msg_removebarvars = self.__getlasterror(_res_removebarvars)
      raise Error(rescode(_res_removebarvars),_msg_removebarvars)
  def removebarvars(self,*args,**kwds):
    """
    Removes a number of symmetric matrices.
  
    removebarvars(subset)
      [subset : array(int32)]  Indexes of symmetric matrices which should be removed.  
    """
    return self.__removebarvars_2(*args,**kwds)
  def __removecones_2(self,subset):
    num = len(subset) if subset is not None else 0
    copyback_subset = False
    if subset is None:
      subset_ = None
      _tmparray_subset_ = None
    else:
      _tmparray_subset_ = (ctypes.c_int32*len(subset))(*subset)
    _res_removecones = __library__.MSK_removecones(self.__nativep,num,_tmparray_subset_)
    if _res_removecones != 0:
      _,_msg_removecones = self.__getlasterror(_res_removecones)
      raise Error(rescode(_res_removecones),_msg_removecones)
  def removecones(self,*args,**kwds):
    """
    Removes a number of conic constraints from the problem.
  
    removecones(subset)
      [subset : array(int32)]  Indexes of cones which should be removed.  
    """
    return self.__removecones_2(*args,**kwds)
  def __appendbarvars_2(self,dim):
    num = len(dim) if dim is not None else 0
    copyback_dim = False
    if dim is None:
      dim_ = None
      _tmparray_dim_ = None
    else:
      _tmparray_dim_ = (ctypes.c_int32*len(dim))(*dim)
    _res_appendbarvars = __library__.MSK_appendbarvars(self.__nativep,num,_tmparray_dim_)
    if _res_appendbarvars != 0:
      _,_msg_appendbarvars = self.__getlasterror(_res_appendbarvars)
      raise Error(rescode(_res_appendbarvars),_msg_appendbarvars)
  def appendbarvars(self,*args,**kwds):
    """
    Appends semidefinite variables to the problem.
  
    appendbarvars(dim)
      [dim : array(int32)]  Dimensions of symmetric matrix variables to be added.  
    """
    return self.__appendbarvars_2(*args,**kwds)
  def __appendcone_4(self,ct : conetype,conepar,submem):
    nummem = len(submem) if submem is not None else 0
    copyback_submem = False
    if submem is None:
      submem_ = None
      _tmparray_submem_ = None
    else:
      _tmparray_submem_ = (ctypes.c_int32*len(submem))(*submem)
    _res_appendcone = __library__.MSK_appendcone(self.__nativep,ct,conepar,nummem,_tmparray_submem_)
    if _res_appendcone != 0:
      _,_msg_appendcone = self.__getlasterror(_res_appendcone)
      raise Error(rescode(_res_appendcone),_msg_appendcone)
  def appendcone(self,*args,**kwds):
    """
    Appends a new conic constraint to the problem.
  
    appendcone(conepar,submem)
      [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [submem : array(int32)]  Variable subscripts of the members in the cone.  
    """
    return self.__appendcone_4(*args,**kwds)
  def __appendconeseq_5(self,ct : conetype,conepar,nummem,j):
    _res_appendconeseq = __library__.MSK_appendconeseq(self.__nativep,ct,conepar,nummem,j)
    if _res_appendconeseq != 0:
      _,_msg_appendconeseq = self.__getlasterror(_res_appendconeseq)
      raise Error(rescode(_res_appendconeseq),_msg_appendconeseq)
  def appendconeseq(self,*args,**kwds):
    """
    Appends a new conic constraint to the problem.
  
    appendconeseq(conepar,nummem,j)
      [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [j : int32]  Index of the first variable in the conic constraint.  
      [nummem : int32]  Number of member variables in the cone.  
    """
    return self.__appendconeseq_5(*args,**kwds)
  def __appendconesseq_5(self,ct,conepar,nummem,j):
    num = min(len(ct) if ct is not None else 0,len(conepar) if conepar is not None else 0,len(nummem) if nummem is not None else 0)
    if ct is None:
      _tmparray_ct_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_ct_ = (ctypes.c_int32*len(ct))(*ct)
    copyback_conepar = False
    if conepar is None:
      conepar_ = None
      _tmparray_conepar_ = None
    else:
      _tmparray_conepar_ = (ctypes.c_double*len(conepar))(*conepar)
    copyback_nummem = False
    if nummem is None:
      nummem_ = None
      _tmparray_nummem_ = None
    else:
      _tmparray_nummem_ = (ctypes.c_int32*len(nummem))(*nummem)
    _res_appendconesseq = __library__.MSK_appendconesseq(self.__nativep,num,_tmparray_ct_,_tmparray_conepar_,_tmparray_nummem_,j)
    if _res_appendconesseq != 0:
      _,_msg_appendconesseq = self.__getlasterror(_res_appendconesseq)
      raise Error(rescode(_res_appendconesseq),_msg_appendconesseq)
  def appendconesseq(self,*args,**kwds):
    """
    Appends multiple conic constraints to the problem.
  
    appendconesseq(ct,conepar,nummem,j)
      [conepar : array(float64)]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [ct : array(mosek.conetype)]  Specifies the type of the cone.  
      [j : int32]  Index of the first variable in the first cone to be appended.  
      [nummem : array(int32)]  Numbers of member variables in the cones.  
    """
    return self.__appendconesseq_5(*args,**kwds)
  def __chgconbound_5(self,i,lower,finite,value):
    _res_chgconbound = __library__.MSK_chgconbound(self.__nativep,i,lower,finite,value)
    if _res_chgconbound != 0:
      _,_msg_chgconbound = self.__getlasterror(_res_chgconbound)
      raise Error(rescode(_res_chgconbound),_msg_chgconbound)
  def chgconbound(self,*args,**kwds):
    """
    Changes the bounds for one constraint.
  
    chgconbound(i,lower,finite,value)
      [finite : int32]  If non-zero, then the given value is assumed to be finite.  
      [i : int32]  Index of the constraint for which the bounds should be changed.  
      [lower : int32]  If non-zero, then the lower bound is changed, otherwise the upper bound is changed.  
      [value : float64]  New value for the bound.  
    """
    return self.__chgconbound_5(*args,**kwds)
  def __chgvarbound_5(self,j,lower,finite,value):
    _res_chgvarbound = __library__.MSK_chgvarbound(self.__nativep,j,lower,finite,value)
    if _res_chgvarbound != 0:
      _,_msg_chgvarbound = self.__getlasterror(_res_chgvarbound)
      raise Error(rescode(_res_chgvarbound),_msg_chgvarbound)
  def chgvarbound(self,*args,**kwds):
    """
    Changes the bounds for one variable.
  
    chgvarbound(j,lower,finite,value)
      [finite : int32]  If non-zero, then the given value is assumed to be finite.  
      [j : int32]  Index of the variable for which the bounds should be changed.  
      [lower : int32]  If non-zero, then the lower bound is changed, otherwise the upper bound is changed.  
      [value : float64]  New value for the bound.  
    """
    return self.__chgvarbound_5(*args,**kwds)
  def __getaij_3(self,i,j):
    aij_ = ctypes.c_double()
    _res_getaij = __library__.MSK_getaij(self.__nativep,i,j,ctypes.byref(aij_))
    if _res_getaij != 0:
      _,_msg_getaij = self.__getlasterror(_res_getaij)
      raise Error(rescode(_res_getaij),_msg_getaij)
    aij = aij_.value
    return (aij_.value)
  def getaij(self,*args,**kwds):
    """
    Obtains a single coefficient in linear constraint matrix.
  
    getaij(i,j) -> (aij)
      [aij : float64]  Returns the requested coefficient.  
      [i : int32]  Row index of the coefficient to be returned.  
      [j : int32]  Column index of the coefficient to be returned.  
    """
    return self.__getaij_3(*args,**kwds)
  def __getapiecenumnz_5(self,firsti,lasti,firstj,lastj):
    numnz_ = ctypes.c_int32()
    _res_getapiecenumnz = __library__.MSK_getapiecenumnz(self.__nativep,firsti,lasti,firstj,lastj,ctypes.byref(numnz_))
    if _res_getapiecenumnz != 0:
      _,_msg_getapiecenumnz = self.__getlasterror(_res_getapiecenumnz)
      raise Error(rescode(_res_getapiecenumnz),_msg_getapiecenumnz)
    numnz = numnz_.value
    return (numnz_.value)
  def getapiecenumnz(self,*args,**kwds):
    """
    Obtains the number non-zeros in a rectangular piece of the linear constraint matrix.
  
    getapiecenumnz(firsti,lasti,firstj,lastj) -> (numnz)
      [firsti : int32]  Index of the first row in the rectangular piece.  
      [firstj : int32]  Index of the first column in the rectangular piece.  
      [lasti : int32]  Index of the last row plus one in the rectangular piece.  
      [lastj : int32]  Index of the last column plus one in the rectangular piece.  
      [numnz : int32]  Number of non-zero elements in the rectangular piece of the linear constraint matrix.  
    """
    return self.__getapiecenumnz_5(*args,**kwds)
  def __getacolnumnz_2(self,i):
    nzj_ = ctypes.c_int32()
    _res_getacolnumnz = __library__.MSK_getacolnumnz(self.__nativep,i,ctypes.byref(nzj_))
    if _res_getacolnumnz != 0:
      _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
      raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
    nzj = nzj_.value
    return (nzj_.value)
  def getacolnumnz(self,*args,**kwds):
    """
    Obtains the number of non-zero elements in one column of the linear constraint matrix
  
    getacolnumnz(i) -> (nzj)
      [i : int32]  Index of the column.  
      [nzj : int32]  Number of non-zeros in the j'th column of (A).  
    """
    return self.__getacolnumnz_2(*args,**kwds)
  def __getacol_4(self,j,subj,valj):
    nzj_ = ctypes.c_int32()
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      __tmp_27 = ctypes.c_int32()
      _res_getacolnumnz = __library__.MSK_getacolnumnz(self.__nativep,j,ctypes.byref(__tmp_27))
      if _res_getacolnumnz != 0:
        _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
        raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
      if len(subj) < int(__tmp_27.value):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valj = False
    if valj is None:
      valj_ = None
      _tmparray_valj_ = None
    else:
      __tmp_31 = ctypes.c_int32()
      _res_getacolnumnz = __library__.MSK_getacolnumnz(self.__nativep,j,ctypes.byref(__tmp_31))
      if _res_getacolnumnz != 0:
        _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
        raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
      if len(valj) < int(__tmp_31.value):
        raise ValueError("argument valj is too short")
      _tmparray_valj_ = (ctypes.c_double*len(valj))(*valj)
    _res_getacol = __library__.MSK_getacol(self.__nativep,j,ctypes.byref(nzj_),_tmparray_subj_,_tmparray_valj_)
    if _res_getacol != 0:
      _,_msg_getacol = self.__getlasterror(_res_getacol)
      raise Error(rescode(_res_getacol),_msg_getacol)
    nzj = nzj_.value
    if subj is not None:
      for __tmp_29,__tmp_30 in enumerate(_tmparray_subj_):
        subj[__tmp_29] = __tmp_30
    if valj is not None:
      for __tmp_33,__tmp_34 in enumerate(_tmparray_valj_):
        valj[__tmp_33] = __tmp_34
    return (nzj_.value)
  def __getacol_2(self,j):
    nzj_ = ctypes.c_int32()
    __tmp_35 = ctypes.c_int32()
    _res_getacolnumnz = __library__.MSK_getacolnumnz(self.__nativep,j,ctypes.byref(__tmp_35))
    if _res_getacolnumnz != 0:
      _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
      raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
    subj = numpy.zeros(__tmp_35.value,numpy.int32)
    __tmp_38 = ctypes.c_int32()
    _res_getacolnumnz = __library__.MSK_getacolnumnz(self.__nativep,j,ctypes.byref(__tmp_38))
    if _res_getacolnumnz != 0:
      _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
      raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
    valj = numpy.zeros(__tmp_38.value,numpy.float64)
    _res_getacol = __library__.MSK_getacol(self.__nativep,j,ctypes.byref(nzj_),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(valj.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getacol != 0:
      _,_msg_getacol = self.__getlasterror(_res_getacol)
      raise Error(rescode(_res_getacol),_msg_getacol)
    nzj = nzj_.value
    return (nzj_.value,subj,valj)
  def getacol(self,*args,**kwds):
    """
    Obtains one column of the linear constraint matrix.
  
    getacol(j,subj,valj) -> (nzj)
    getacol(j) -> (nzj,subj,valj)
      [j : int32]  Index of the column.  
      [nzj : int32]  Number of non-zeros in the column obtained.  
      [subj : array(int32)]  Row indices of the non-zeros in the column obtained.  
      [valj : array(float64)]  Numerical values in the column obtained.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getacol_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getacol_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getacolslice64_7(self,first,last,ptrb,ptre,sub,val):
    __tmp_41 = ctypes.c_int64()
    _res_getacolslicenumnz64 = __library__.MSK_getacolslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_41))
    if _res_getacolslicenumnz64 != 0:
      _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
      raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
    maxnumnz = __tmp_41.value;
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      if len(ptrb) < int((last - first)):
        raise ValueError("argument ptrb is too short")
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      if len(ptre) < int((last - first)):
        raise ValueError("argument ptre is too short")
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      if len(sub) < int(maxnumnz):
        raise ValueError("argument sub is too short")
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      if len(val) < int(maxnumnz):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getacolslice64 = __library__.MSK_getacolslice64(self.__nativep,first,last,maxnumnz,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_sub_,_tmparray_val_)
    if _res_getacolslice64 != 0:
      _,_msg_getacolslice64 = self.__getlasterror(_res_getacolslice64)
      raise Error(rescode(_res_getacolslice64),_msg_getacolslice64)
    if ptrb is not None:
      for __tmp_43,__tmp_44 in enumerate(_tmparray_ptrb_):
        ptrb[__tmp_43] = __tmp_44
    if ptre is not None:
      for __tmp_45,__tmp_46 in enumerate(_tmparray_ptre_):
        ptre[__tmp_45] = __tmp_46
    if sub is not None:
      for __tmp_47,__tmp_48 in enumerate(_tmparray_sub_):
        sub[__tmp_47] = __tmp_48
    if val is not None:
      for __tmp_49,__tmp_50 in enumerate(_tmparray_val_):
        val[__tmp_49] = __tmp_50
  def __getacolslice64_3(self,first,last):
    __tmp_51 = ctypes.c_int64()
    _res_getacolslicenumnz64 = __library__.MSK_getacolslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_51))
    if _res_getacolslicenumnz64 != 0:
      _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
      raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
    maxnumnz = __tmp_51.value;
    ptrb = numpy.zeros((last - first),numpy.int64)
    ptre = numpy.zeros((last - first),numpy.int64)
    sub = numpy.zeros(maxnumnz,numpy.int32)
    val = numpy.zeros(maxnumnz,numpy.float64)
    _res_getacolslice64 = __library__.MSK_getacolslice64(self.__nativep,first,last,maxnumnz,ctypes.cast(ptrb.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(ptre.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(sub.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getacolslice64 != 0:
      _,_msg_getacolslice64 = self.__getlasterror(_res_getacolslice64)
      raise Error(rescode(_res_getacolslice64),_msg_getacolslice64)
    return (ptrb,ptre,sub,val)
  def getacolslice(self,*args,**kwds):
    """
    Obtains a sequence of columns from the coefficient matrix.
  
    getacolslice(first,last,ptrb,ptre,sub,val)
    getacolslice(first,last) -> (ptrb,ptre,sub,val)
      [first : int32]  Index of the first column in the sequence.  
      [last : int32]  Index of the last column in the sequence plus one.  
      [ptrb : array(int64)]  Column start pointers.  
      [ptre : array(int64)]  Column end pointers.  
      [sub : array(int32)]  Contains the row subscripts.  
      [val : array(float64)]  Contains the coefficient values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 7: return self.__getacolslice64_7(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getacolslice64_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getarownumnz_2(self,i):
    nzi_ = ctypes.c_int32()
    _res_getarownumnz = __library__.MSK_getarownumnz(self.__nativep,i,ctypes.byref(nzi_))
    if _res_getarownumnz != 0:
      _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
      raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
    nzi = nzi_.value
    return (nzi_.value)
  def getarownumnz(self,*args,**kwds):
    """
    Obtains the number of non-zero elements in one row of the linear constraint matrix
  
    getarownumnz(i) -> (nzi)
      [i : int32]  Index of the row.  
      [nzi : int32]  Number of non-zeros in the i'th row of `A`.  
    """
    return self.__getarownumnz_2(*args,**kwds)
  def __getarow_4(self,i,subi,vali):
    nzi_ = ctypes.c_int32()
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      __tmp_57 = ctypes.c_int32()
      _res_getarownumnz = __library__.MSK_getarownumnz(self.__nativep,i,ctypes.byref(__tmp_57))
      if _res_getarownumnz != 0:
        _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
        raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
      if len(subi) < int(__tmp_57.value):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_vali = False
    if vali is None:
      vali_ = None
      _tmparray_vali_ = None
    else:
      __tmp_61 = ctypes.c_int32()
      _res_getarownumnz = __library__.MSK_getarownumnz(self.__nativep,i,ctypes.byref(__tmp_61))
      if _res_getarownumnz != 0:
        _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
        raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
      if len(vali) < int(__tmp_61.value):
        raise ValueError("argument vali is too short")
      _tmparray_vali_ = (ctypes.c_double*len(vali))(*vali)
    _res_getarow = __library__.MSK_getarow(self.__nativep,i,ctypes.byref(nzi_),_tmparray_subi_,_tmparray_vali_)
    if _res_getarow != 0:
      _,_msg_getarow = self.__getlasterror(_res_getarow)
      raise Error(rescode(_res_getarow),_msg_getarow)
    nzi = nzi_.value
    if subi is not None:
      for __tmp_59,__tmp_60 in enumerate(_tmparray_subi_):
        subi[__tmp_59] = __tmp_60
    if vali is not None:
      for __tmp_63,__tmp_64 in enumerate(_tmparray_vali_):
        vali[__tmp_63] = __tmp_64
    return (nzi_.value)
  def __getarow_2(self,i):
    nzi_ = ctypes.c_int32()
    __tmp_65 = ctypes.c_int32()
    _res_getarownumnz = __library__.MSK_getarownumnz(self.__nativep,i,ctypes.byref(__tmp_65))
    if _res_getarownumnz != 0:
      _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
      raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
    subi = numpy.zeros(__tmp_65.value,numpy.int32)
    __tmp_68 = ctypes.c_int32()
    _res_getarownumnz = __library__.MSK_getarownumnz(self.__nativep,i,ctypes.byref(__tmp_68))
    if _res_getarownumnz != 0:
      _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
      raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
    vali = numpy.zeros(__tmp_68.value,numpy.float64)
    _res_getarow = __library__.MSK_getarow(self.__nativep,i,ctypes.byref(nzi_),ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(vali.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getarow != 0:
      _,_msg_getarow = self.__getlasterror(_res_getarow)
      raise Error(rescode(_res_getarow),_msg_getarow)
    nzi = nzi_.value
    return (nzi_.value,subi,vali)
  def getarow(self,*args,**kwds):
    """
    Obtains one row of the linear constraint matrix.
  
    getarow(i,subi,vali) -> (nzi)
    getarow(i) -> (nzi,subi,vali)
      [i : int32]  Index of the row.  
      [nzi : int32]  Number of non-zeros in the row obtained.  
      [subi : array(int32)]  Column indices of the non-zeros in the row obtained.  
      [vali : array(float64)]  Numerical values of the row obtained.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getarow_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getarow_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getacolslicenumnz64_3(self,first,last):
    numnz_ = ctypes.c_int64()
    _res_getacolslicenumnz64 = __library__.MSK_getacolslicenumnz64(self.__nativep,first,last,ctypes.byref(numnz_))
    if _res_getacolslicenumnz64 != 0:
      _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
      raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
    numnz = numnz_.value
    return (numnz_.value)
  def getacolslicenumnz(self,*args,**kwds):
    """
    Obtains the number of non-zeros in a slice of columns of the coefficient matrix.
  
    getacolslicenumnz(first,last) -> (numnz)
      [first : int32]  Index of the first column in the sequence.  
      [last : int32]  Index of the last column plus one in the sequence.  
      [numnz : int64]  Number of non-zeros in the slice.  
    """
    return self.__getacolslicenumnz64_3(*args,**kwds)
  def __getarowslicenumnz64_3(self,first,last):
    numnz_ = ctypes.c_int64()
    _res_getarowslicenumnz64 = __library__.MSK_getarowslicenumnz64(self.__nativep,first,last,ctypes.byref(numnz_))
    if _res_getarowslicenumnz64 != 0:
      _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
      raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
    numnz = numnz_.value
    return (numnz_.value)
  def getarowslicenumnz(self,*args,**kwds):
    """
    Obtains the number of non-zeros in a slice of rows of the coefficient matrix.
  
    getarowslicenumnz(first,last) -> (numnz)
      [first : int32]  Index of the first row in the sequence.  
      [last : int32]  Index of the last row plus one in the sequence.  
      [numnz : int64]  Number of non-zeros in the slice.  
    """
    return self.__getarowslicenumnz64_3(*args,**kwds)
  def __getarowslice64_7(self,first,last,ptrb,ptre,sub,val):
    __tmp_71 = ctypes.c_int64()
    _res_getarowslicenumnz64 = __library__.MSK_getarowslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_71))
    if _res_getarowslicenumnz64 != 0:
      _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
      raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
    maxnumnz = __tmp_71.value;
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      if len(ptrb) < int((last - first)):
        raise ValueError("argument ptrb is too short")
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      if len(ptre) < int((last - first)):
        raise ValueError("argument ptre is too short")
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      if len(sub) < int(maxnumnz):
        raise ValueError("argument sub is too short")
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      if len(val) < int(maxnumnz):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getarowslice64 = __library__.MSK_getarowslice64(self.__nativep,first,last,maxnumnz,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_sub_,_tmparray_val_)
    if _res_getarowslice64 != 0:
      _,_msg_getarowslice64 = self.__getlasterror(_res_getarowslice64)
      raise Error(rescode(_res_getarowslice64),_msg_getarowslice64)
    if ptrb is not None:
      for __tmp_73,__tmp_74 in enumerate(_tmparray_ptrb_):
        ptrb[__tmp_73] = __tmp_74
    if ptre is not None:
      for __tmp_75,__tmp_76 in enumerate(_tmparray_ptre_):
        ptre[__tmp_75] = __tmp_76
    if sub is not None:
      for __tmp_77,__tmp_78 in enumerate(_tmparray_sub_):
        sub[__tmp_77] = __tmp_78
    if val is not None:
      for __tmp_79,__tmp_80 in enumerate(_tmparray_val_):
        val[__tmp_79] = __tmp_80
  def __getarowslice64_3(self,first,last):
    __tmp_81 = ctypes.c_int64()
    _res_getarowslicenumnz64 = __library__.MSK_getarowslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_81))
    if _res_getarowslicenumnz64 != 0:
      _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
      raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
    maxnumnz = __tmp_81.value;
    ptrb = numpy.zeros((last - first),numpy.int64)
    ptre = numpy.zeros((last - first),numpy.int64)
    sub = numpy.zeros(maxnumnz,numpy.int32)
    val = numpy.zeros(maxnumnz,numpy.float64)
    _res_getarowslice64 = __library__.MSK_getarowslice64(self.__nativep,first,last,maxnumnz,ctypes.cast(ptrb.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(ptre.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(sub.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getarowslice64 != 0:
      _,_msg_getarowslice64 = self.__getlasterror(_res_getarowslice64)
      raise Error(rescode(_res_getarowslice64),_msg_getarowslice64)
    return (ptrb,ptre,sub,val)
  def getarowslice(self,*args,**kwds):
    """
    Obtains a sequence of rows from the coefficient matrix.
  
    getarowslice(first,last,ptrb,ptre,sub,val)
    getarowslice(first,last) -> (ptrb,ptre,sub,val)
      [first : int32]  Index of the first row in the sequence.  
      [last : int32]  Index of the last row in the sequence plus one.  
      [ptrb : array(int64)]  Row start pointers.  
      [ptre : array(int64)]  Row end pointers.  
      [sub : array(int32)]  Contains the column subscripts.  
      [val : array(float64)]  Contains the coefficient values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 7: return self.__getarowslice64_7(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getarowslice64_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getatrip_4(self,subi,subj,val):
    __tmp_87 = ctypes.c_int64()
    _res_getnumanz64 = __library__.MSK_getnumanz64(self.__nativep,ctypes.byref(__tmp_87))
    if _res_getnumanz64 != 0:
      _,_msg_getnumanz64 = self.__getlasterror(_res_getnumanz64)
      raise Error(rescode(_res_getnumanz64),_msg_getnumanz64)
    maxnumnz = __tmp_87.value;
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(maxnumnz):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxnumnz):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      if len(val) < int(maxnumnz):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getatrip = __library__.MSK_getatrip(self.__nativep,maxnumnz,_tmparray_subi_,_tmparray_subj_,_tmparray_val_)
    if _res_getatrip != 0:
      _,_msg_getatrip = self.__getlasterror(_res_getatrip)
      raise Error(rescode(_res_getatrip),_msg_getatrip)
    if subi is not None:
      for __tmp_89,__tmp_90 in enumerate(_tmparray_subi_):
        subi[__tmp_89] = __tmp_90
    if subj is not None:
      for __tmp_91,__tmp_92 in enumerate(_tmparray_subj_):
        subj[__tmp_91] = __tmp_92
    if val is not None:
      for __tmp_93,__tmp_94 in enumerate(_tmparray_val_):
        val[__tmp_93] = __tmp_94
  def __getatrip_1(self):
    __tmp_95 = ctypes.c_int64()
    _res_getnumanz64 = __library__.MSK_getnumanz64(self.__nativep,ctypes.byref(__tmp_95))
    if _res_getnumanz64 != 0:
      _,_msg_getnumanz64 = self.__getlasterror(_res_getnumanz64)
      raise Error(rescode(_res_getnumanz64),_msg_getnumanz64)
    maxnumnz = __tmp_95.value;
    subi = numpy.zeros(maxnumnz,numpy.int32)
    subj = numpy.zeros(maxnumnz,numpy.int32)
    val = numpy.zeros(maxnumnz,numpy.float64)
    _res_getatrip = __library__.MSK_getatrip(self.__nativep,maxnumnz,ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getatrip != 0:
      _,_msg_getatrip = self.__getlasterror(_res_getatrip)
      raise Error(rescode(_res_getatrip),_msg_getatrip)
    return (subi,subj,val)
  def getatrip(self,*args,**kwds):
    """
    Obtains the A matrix in sparse triplet format.
  
    getatrip(subi,subj,val)
    getatrip() -> (subi,subj,val)
      [subi : array(int32)]  Constraint subscripts.  
      [subj : array(int32)]  Column subscripts.  
      [val : array(float64)]  Values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getatrip_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getatrip_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getarowslicetrip_6(self,first,last,subi,subj,val):
    __tmp_100 = ctypes.c_int64()
    _res_getarowslicenumnz64 = __library__.MSK_getarowslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_100))
    if _res_getarowslicenumnz64 != 0:
      _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
      raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
    maxnumnz = __tmp_100.value;
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(maxnumnz):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxnumnz):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      if len(val) < int(maxnumnz):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getarowslicetrip = __library__.MSK_getarowslicetrip(self.__nativep,first,last,maxnumnz,_tmparray_subi_,_tmparray_subj_,_tmparray_val_)
    if _res_getarowslicetrip != 0:
      _,_msg_getarowslicetrip = self.__getlasterror(_res_getarowslicetrip)
      raise Error(rescode(_res_getarowslicetrip),_msg_getarowslicetrip)
    if subi is not None:
      for __tmp_102,__tmp_103 in enumerate(_tmparray_subi_):
        subi[__tmp_102] = __tmp_103
    if subj is not None:
      for __tmp_104,__tmp_105 in enumerate(_tmparray_subj_):
        subj[__tmp_104] = __tmp_105
    if val is not None:
      for __tmp_106,__tmp_107 in enumerate(_tmparray_val_):
        val[__tmp_106] = __tmp_107
  def __getarowslicetrip_3(self,first,last):
    __tmp_108 = ctypes.c_int64()
    _res_getarowslicenumnz64 = __library__.MSK_getarowslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_108))
    if _res_getarowslicenumnz64 != 0:
      _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
      raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
    maxnumnz = __tmp_108.value;
    subi = numpy.zeros(maxnumnz,numpy.int32)
    subj = numpy.zeros(maxnumnz,numpy.int32)
    val = numpy.zeros(maxnumnz,numpy.float64)
    _res_getarowslicetrip = __library__.MSK_getarowslicetrip(self.__nativep,first,last,maxnumnz,ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getarowslicetrip != 0:
      _,_msg_getarowslicetrip = self.__getlasterror(_res_getarowslicetrip)
      raise Error(rescode(_res_getarowslicetrip),_msg_getarowslicetrip)
    return (subi,subj,val)
  def getarowslicetrip(self,*args,**kwds):
    """
    Obtains a sequence of rows from the coefficient matrix in sparse triplet format.
  
    getarowslicetrip(first,last,subi,subj,val)
    getarowslicetrip(first,last) -> (subi,subj,val)
      [first : int32]  Index of the first row in the sequence.  
      [last : int32]  Index of the last row in the sequence plus one.  
      [subi : array(int32)]  Constraint subscripts.  
      [subj : array(int32)]  Column subscripts.  
      [val : array(float64)]  Values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getarowslicetrip_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getarowslicetrip_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getacolslicetrip_6(self,first,last,subi,subj,val):
    __tmp_113 = ctypes.c_int64()
    _res_getacolslicenumnz64 = __library__.MSK_getacolslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_113))
    if _res_getacolslicenumnz64 != 0:
      _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
      raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
    maxnumnz = __tmp_113.value;
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(maxnumnz):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxnumnz):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      if len(val) < int(maxnumnz):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getacolslicetrip = __library__.MSK_getacolslicetrip(self.__nativep,first,last,maxnumnz,_tmparray_subi_,_tmparray_subj_,_tmparray_val_)
    if _res_getacolslicetrip != 0:
      _,_msg_getacolslicetrip = self.__getlasterror(_res_getacolslicetrip)
      raise Error(rescode(_res_getacolslicetrip),_msg_getacolslicetrip)
    if subi is not None:
      for __tmp_115,__tmp_116 in enumerate(_tmparray_subi_):
        subi[__tmp_115] = __tmp_116
    if subj is not None:
      for __tmp_117,__tmp_118 in enumerate(_tmparray_subj_):
        subj[__tmp_117] = __tmp_118
    if val is not None:
      for __tmp_119,__tmp_120 in enumerate(_tmparray_val_):
        val[__tmp_119] = __tmp_120
  def __getacolslicetrip_3(self,first,last):
    __tmp_121 = ctypes.c_int64()
    _res_getacolslicenumnz64 = __library__.MSK_getacolslicenumnz64(self.__nativep,first,last,ctypes.byref(__tmp_121))
    if _res_getacolslicenumnz64 != 0:
      _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
      raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
    maxnumnz = __tmp_121.value;
    subi = numpy.zeros(maxnumnz,numpy.int32)
    subj = numpy.zeros(maxnumnz,numpy.int32)
    val = numpy.zeros(maxnumnz,numpy.float64)
    _res_getacolslicetrip = __library__.MSK_getacolslicetrip(self.__nativep,first,last,maxnumnz,ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getacolslicetrip != 0:
      _,_msg_getacolslicetrip = self.__getlasterror(_res_getacolslicetrip)
      raise Error(rescode(_res_getacolslicetrip),_msg_getacolslicetrip)
    return (subi,subj,val)
  def getacolslicetrip(self,*args,**kwds):
    """
    Obtains a sequence of columns from the coefficient matrix in triplet format.
  
    getacolslicetrip(first,last,subi,subj,val)
    getacolslicetrip(first,last) -> (subi,subj,val)
      [first : int32]  Index of the first column in the sequence.  
      [last : int32]  Index of the last column in the sequence plus one.  
      [subi : array(int32)]  Constraint subscripts.  
      [subj : array(int32)]  Column subscripts.  
      [val : array(float64)]  Values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getacolslicetrip_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getacolslicetrip_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getconbound_2(self,i):
    bk = ctypes.c_int()
    bl_ = ctypes.c_double()
    bu_ = ctypes.c_double()
    _res_getconbound = __library__.MSK_getconbound(self.__nativep,i,ctypes.byref(bk),ctypes.byref(bl_),ctypes.byref(bu_))
    if _res_getconbound != 0:
      _,_msg_getconbound = self.__getlasterror(_res_getconbound)
      raise Error(rescode(_res_getconbound),_msg_getconbound)
    bl = bl_.value
    bu = bu_.value
    return (boundkey(bk.value),bl_.value,bu_.value)
  def getconbound(self,*args,**kwds):
    """
    Obtains bound information for one constraint.
  
    getconbound(i) -> (bk,bl,bu)
      [bk : mosek.boundkey]  Bound keys.  
      [bl : float64]  Values for lower bounds.  
      [bu : float64]  Values for upper bounds.  
      [i : int32]  Index of the constraint for which the bound information should be obtained.  
    """
    return self.__getconbound_2(*args,**kwds)
  def __getvarbound_2(self,i):
    bk = ctypes.c_int()
    bl_ = ctypes.c_double()
    bu_ = ctypes.c_double()
    _res_getvarbound = __library__.MSK_getvarbound(self.__nativep,i,ctypes.byref(bk),ctypes.byref(bl_),ctypes.byref(bu_))
    if _res_getvarbound != 0:
      _,_msg_getvarbound = self.__getlasterror(_res_getvarbound)
      raise Error(rescode(_res_getvarbound),_msg_getvarbound)
    bl = bl_.value
    bu = bu_.value
    return (boundkey(bk.value),bl_.value,bu_.value)
  def getvarbound(self,*args,**kwds):
    """
    Obtains bound information for one variable.
  
    getvarbound(i) -> (bk,bl,bu)
      [bk : mosek.boundkey]  Bound keys.  
      [bl : float64]  Values for lower bounds.  
      [bu : float64]  Values for upper bounds.  
      [i : int32]  Index of the variable for which the bound information should be obtained.  
    """
    return self.__getvarbound_2(*args,**kwds)
  def __getconboundslice_6(self,first,last,bk,bl,bu):
    if bk is None:
      _tmparray_bk_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(bk) < (last - first):
        raise ValueError("argument bk is too short")
      _tmparray_bk_ = (ctypes.c_int32*len(bk))()
    copyback_bl = False
    if bl is None:
      bl_ = None
      _tmparray_bl_ = None
    else:
      if len(bl) < int((last - first)):
        raise ValueError("argument bl is too short")
      _tmparray_bl_ = (ctypes.c_double*len(bl))(*bl)
    copyback_bu = False
    if bu is None:
      bu_ = None
      _tmparray_bu_ = None
    else:
      if len(bu) < int((last - first)):
        raise ValueError("argument bu is too short")
      _tmparray_bu_ = (ctypes.c_double*len(bu))(*bu)
    _res_getconboundslice = __library__.MSK_getconboundslice(self.__nativep,first,last,_tmparray_bk_,_tmparray_bl_,_tmparray_bu_)
    if _res_getconboundslice != 0:
      _,_msg_getconboundslice = self.__getlasterror(_res_getconboundslice)
      raise Error(rescode(_res_getconboundslice),_msg_getconboundslice)
    if bk is not None:
      for __tmp_126,__tmp_127 in enumerate(_tmparray_bk_):
        bk[__tmp_126] = boundkey(__tmp_127)
    if bl is not None:
      for __tmp_128,__tmp_129 in enumerate(_tmparray_bl_):
        bl[__tmp_128] = __tmp_129
    if bu is not None:
      for __tmp_130,__tmp_131 in enumerate(_tmparray_bu_):
        bu[__tmp_130] = __tmp_131
  def __getconboundslice_3(self,first,last):
    _tmparray_bk_ = (ctypes.c_int32*(last - first))()
    bl = numpy.zeros((last - first),numpy.float64)
    bu = numpy.zeros((last - first),numpy.float64)
    _res_getconboundslice = __library__.MSK_getconboundslice(self.__nativep,first,last,_tmparray_bk_,ctypes.cast(bl.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(bu.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getconboundslice != 0:
      _,_msg_getconboundslice = self.__getlasterror(_res_getconboundslice)
      raise Error(rescode(_res_getconboundslice),_msg_getconboundslice)
    bk = list(map(lambda _i: boundkey(_i),_tmparray_bk_))
    return (bk,bl,bu)
  def getconboundslice(self,*args,**kwds):
    """
    Obtains bounds information for a slice of the constraints.
  
    getconboundslice(first,last,bk,bl,bu)
    getconboundslice(first,last) -> (bk,bl,bu)
      [bk : array(mosek.boundkey)]  Bound keys.  
      [bl : array(float64)]  Values for lower bounds.  
      [bu : array(float64)]  Values for upper bounds.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getconboundslice_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getconboundslice_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getvarboundslice_6(self,first,last,bk,bl,bu):
    if bk is None:
      _tmparray_bk_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(bk) < (last - first):
        raise ValueError("argument bk is too short")
      _tmparray_bk_ = (ctypes.c_int32*len(bk))()
    copyback_bl = False
    if bl is None:
      bl_ = None
      _tmparray_bl_ = None
    else:
      if len(bl) < int((last - first)):
        raise ValueError("argument bl is too short")
      _tmparray_bl_ = (ctypes.c_double*len(bl))(*bl)
    copyback_bu = False
    if bu is None:
      bu_ = None
      _tmparray_bu_ = None
    else:
      if len(bu) < int((last - first)):
        raise ValueError("argument bu is too short")
      _tmparray_bu_ = (ctypes.c_double*len(bu))(*bu)
    _res_getvarboundslice = __library__.MSK_getvarboundslice(self.__nativep,first,last,_tmparray_bk_,_tmparray_bl_,_tmparray_bu_)
    if _res_getvarboundslice != 0:
      _,_msg_getvarboundslice = self.__getlasterror(_res_getvarboundslice)
      raise Error(rescode(_res_getvarboundslice),_msg_getvarboundslice)
    if bk is not None:
      for __tmp_134,__tmp_135 in enumerate(_tmparray_bk_):
        bk[__tmp_134] = boundkey(__tmp_135)
    if bl is not None:
      for __tmp_136,__tmp_137 in enumerate(_tmparray_bl_):
        bl[__tmp_136] = __tmp_137
    if bu is not None:
      for __tmp_138,__tmp_139 in enumerate(_tmparray_bu_):
        bu[__tmp_138] = __tmp_139
  def __getvarboundslice_3(self,first,last):
    _tmparray_bk_ = (ctypes.c_int32*(last - first))()
    bl = numpy.zeros((last - first),numpy.float64)
    bu = numpy.zeros((last - first),numpy.float64)
    _res_getvarboundslice = __library__.MSK_getvarboundslice(self.__nativep,first,last,_tmparray_bk_,ctypes.cast(bl.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(bu.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getvarboundslice != 0:
      _,_msg_getvarboundslice = self.__getlasterror(_res_getvarboundslice)
      raise Error(rescode(_res_getvarboundslice),_msg_getvarboundslice)
    bk = list(map(lambda _i: boundkey(_i),_tmparray_bk_))
    return (bk,bl,bu)
  def getvarboundslice(self,*args,**kwds):
    """
    Obtains bounds information for a slice of the variables.
  
    getvarboundslice(first,last,bk,bl,bu)
    getvarboundslice(first,last) -> (bk,bl,bu)
      [bk : array(mosek.boundkey)]  Bound keys.  
      [bl : array(float64)]  Values for lower bounds.  
      [bu : array(float64)]  Values for upper bounds.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getvarboundslice_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getvarboundslice_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getcj_2(self,j):
    cj_ = ctypes.c_double()
    _res_getcj = __library__.MSK_getcj(self.__nativep,j,ctypes.byref(cj_))
    if _res_getcj != 0:
      _,_msg_getcj = self.__getlasterror(_res_getcj)
      raise Error(rescode(_res_getcj),_msg_getcj)
    cj = cj_.value
    return (cj_.value)
  def getcj(self,*args,**kwds):
    """
    Obtains one objective coefficient.
  
    getcj(j) -> (cj)
      [cj : float64]  The c coefficient value.  
      [j : int32]  Index of the variable for which the c coefficient should be obtained.  
    """
    return self.__getcj_2(*args,**kwds)
  def __getc_2(self,c):
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      __tmp_142 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_142))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(c) < int(__tmp_142.value):
        raise ValueError("argument c is too short")
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    _res_getc = __library__.MSK_getc(self.__nativep,_tmparray_c_)
    if _res_getc != 0:
      _,_msg_getc = self.__getlasterror(_res_getc)
      raise Error(rescode(_res_getc),_msg_getc)
    if c is not None:
      for __tmp_144,__tmp_145 in enumerate(_tmparray_c_):
        c[__tmp_144] = __tmp_145
  def __getc_1(self):
    __tmp_146 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_146))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    c = numpy.zeros(__tmp_146.value,numpy.float64)
    _res_getc = __library__.MSK_getc(self.__nativep,ctypes.cast(c.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getc != 0:
      _,_msg_getc = self.__getlasterror(_res_getc)
      raise Error(rescode(_res_getc),_msg_getc)
    return (c)
  def getc(self,*args,**kwds):
    """
    Obtains all objective coefficients.
  
    getc(c)
    getc() -> (c)
      [c : array(float64)]  Linear terms of the objective as a dense vector. The length is the number of variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__getc_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getc_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getcfix_1(self):
    cfix_ = ctypes.c_double()
    _res_getcfix = __library__.MSK_getcfix(self.__nativep,ctypes.byref(cfix_))
    if _res_getcfix != 0:
      _,_msg_getcfix = self.__getlasterror(_res_getcfix)
      raise Error(rescode(_res_getcfix),_msg_getcfix)
    cfix = cfix_.value
    return (cfix_.value)
  def getcfix(self,*args,**kwds):
    """
    Obtains the fixed term in the objective.
  
    getcfix() -> (cfix)
      [cfix : float64]  Fixed term in the objective.  
    """
    return self.__getcfix_1(*args,**kwds)
  def __getcone_3(self,k,submem):
    ct = ctypes.c_int()
    conepar_ = ctypes.c_double()
    nummem_ = ctypes.c_int32()
    copyback_submem = False
    if submem is None:
      submem_ = None
      _tmparray_submem_ = None
    else:
      __tmp_149 = ctypes.c_int32()
      __tmp_150 = ctypes.c_double()
      __tmp_151 = ctypes.c_int32()
      _res_getconeinfo = __library__.MSK_getconeinfo(self.__nativep,k,ctypes.byref(__tmp_149),ctypes.byref(__tmp_150),ctypes.byref(__tmp_151))
      if _res_getconeinfo != 0:
        _,_msg_getconeinfo = self.__getlasterror(_res_getconeinfo)
        raise Error(rescode(_res_getconeinfo),_msg_getconeinfo)
      if len(submem) < int(__tmp_151.value):
        raise ValueError("argument submem is too short")
      _tmparray_submem_ = (ctypes.c_int32*len(submem))(*submem)
    _res_getcone = __library__.MSK_getcone(self.__nativep,k,ctypes.byref(ct),ctypes.byref(conepar_),ctypes.byref(nummem_),_tmparray_submem_)
    if _res_getcone != 0:
      _,_msg_getcone = self.__getlasterror(_res_getcone)
      raise Error(rescode(_res_getcone),_msg_getcone)
    conepar = conepar_.value
    nummem = nummem_.value
    if submem is not None:
      for __tmp_153,__tmp_154 in enumerate(_tmparray_submem_):
        submem[__tmp_153] = __tmp_154
    return (conetype(ct.value),conepar_.value,nummem_.value)
  def __getcone_2(self,k):
    ct = ctypes.c_int()
    conepar_ = ctypes.c_double()
    nummem_ = ctypes.c_int32()
    __tmp_155 = ctypes.c_int32()
    __tmp_156 = ctypes.c_double()
    __tmp_157 = ctypes.c_int32()
    _res_getconeinfo = __library__.MSK_getconeinfo(self.__nativep,k,ctypes.byref(__tmp_155),ctypes.byref(__tmp_156),ctypes.byref(__tmp_157))
    if _res_getconeinfo != 0:
      _,_msg_getconeinfo = self.__getlasterror(_res_getconeinfo)
      raise Error(rescode(_res_getconeinfo),_msg_getconeinfo)
    submem = numpy.zeros(__tmp_157.value,numpy.int32)
    _res_getcone = __library__.MSK_getcone(self.__nativep,k,ctypes.byref(ct),ctypes.byref(conepar_),ctypes.byref(nummem_),ctypes.cast(submem.ctypes,ctypes.POINTER(ctypes.c_int32)))
    if _res_getcone != 0:
      _,_msg_getcone = self.__getlasterror(_res_getcone)
      raise Error(rescode(_res_getcone),_msg_getcone)
    conepar = conepar_.value
    nummem = nummem_.value
    return (conetype(ct.value),conepar_.value,nummem_.value,submem)
  def getcone(self,*args,**kwds):
    """
    Obtains a cone.
  
    getcone(k,submem) -> (ct,conepar,nummem)
    getcone(k) -> (ct,conepar,nummem,submem)
      [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [ct : mosek.conetype]  Specifies the type of the cone.  
      [k : int32]  Index of the cone.  
      [nummem : int32]  Number of member variables in the cone.  
      [submem : array(int32)]  Variable subscripts of the members in the cone.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getcone_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getcone_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getconeinfo_2(self,k):
    ct = ctypes.c_int()
    conepar_ = ctypes.c_double()
    nummem_ = ctypes.c_int32()
    _res_getconeinfo = __library__.MSK_getconeinfo(self.__nativep,k,ctypes.byref(ct),ctypes.byref(conepar_),ctypes.byref(nummem_))
    if _res_getconeinfo != 0:
      _,_msg_getconeinfo = self.__getlasterror(_res_getconeinfo)
      raise Error(rescode(_res_getconeinfo),_msg_getconeinfo)
    conepar = conepar_.value
    nummem = nummem_.value
    return (conetype(ct.value),conepar_.value,nummem_.value)
  def getconeinfo(self,*args,**kwds):
    """
    Obtains information about a cone.
  
    getconeinfo(k) -> (ct,conepar,nummem)
      [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [ct : mosek.conetype]  Specifies the type of the cone.  
      [k : int32]  Index of the cone.  
      [nummem : int32]  Number of member variables in the cone.  
    """
    return self.__getconeinfo_2(*args,**kwds)
  def __getclist_3(self,subj,c):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      if len(c) < int(num):
        raise ValueError("argument c is too short")
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    _res_getclist = __library__.MSK_getclist(self.__nativep,num,_tmparray_subj_,_tmparray_c_)
    if _res_getclist != 0:
      _,_msg_getclist = self.__getlasterror(_res_getclist)
      raise Error(rescode(_res_getclist),_msg_getclist)
    if c is not None:
      for __tmp_160,__tmp_161 in enumerate(_tmparray_c_):
        c[__tmp_160] = __tmp_161
  def __getclist_2(self,subj):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    c = numpy.zeros(num,numpy.float64)
    _res_getclist = __library__.MSK_getclist(self.__nativep,num,_tmparray_subj_,ctypes.cast(c.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getclist != 0:
      _,_msg_getclist = self.__getlasterror(_res_getclist)
      raise Error(rescode(_res_getclist),_msg_getclist)
    return (c)
  def getclist(self,*args,**kwds):
    """
    Obtains a sequence of coefficients from the objective.
  
    getclist(subj,c)
    getclist(subj) -> (c)
      [c : array(float64)]  Linear terms of the requested list of the objective as a dense vector.  
      [subj : array(int32)]  A list of variable indexes.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getclist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getclist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getcslice_4(self,first,last,c):
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      if len(c) < int((last - first)):
        raise ValueError("argument c is too short")
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    _res_getcslice = __library__.MSK_getcslice(self.__nativep,first,last,_tmparray_c_)
    if _res_getcslice != 0:
      _,_msg_getcslice = self.__getlasterror(_res_getcslice)
      raise Error(rescode(_res_getcslice),_msg_getcslice)
    if c is not None:
      for __tmp_163,__tmp_164 in enumerate(_tmparray_c_):
        c[__tmp_163] = __tmp_164
  def __getcslice_3(self,first,last):
    c = numpy.zeros((last - first),numpy.float64)
    _res_getcslice = __library__.MSK_getcslice(self.__nativep,first,last,ctypes.cast(c.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getcslice != 0:
      _,_msg_getcslice = self.__getlasterror(_res_getcslice)
      raise Error(rescode(_res_getcslice),_msg_getcslice)
    return (c)
  def getcslice(self,*args,**kwds):
    """
    Obtains a sequence of coefficients from the objective.
  
    getcslice(first,last,c)
    getcslice(first,last) -> (c)
      [c : array(float64)]  Linear terms of the requested slice of the objective as a dense vector.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getcslice_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getcslice_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdouinf_2(self,whichdinf : dinfitem):
    dvalue_ = ctypes.c_double()
    _res_getdouinf = __library__.MSK_getdouinf(self.__nativep,whichdinf,ctypes.byref(dvalue_))
    if _res_getdouinf != 0:
      _,_msg_getdouinf = self.__getlasterror(_res_getdouinf)
      raise Error(rescode(_res_getdouinf),_msg_getdouinf)
    dvalue = dvalue_.value
    return (dvalue_.value)
  def getdouinf(self,*args,**kwds):
    """
    Obtains a double information item.
  
    getdouinf() -> (dvalue)
      [dvalue : float64]  The value of the required double information item.  
    """
    return self.__getdouinf_2(*args,**kwds)
  def __getdouparam_2(self,param : dparam):
    parvalue_ = ctypes.c_double()
    _res_getdouparam = __library__.MSK_getdouparam(self.__nativep,param,ctypes.byref(parvalue_))
    if _res_getdouparam != 0:
      _,_msg_getdouparam = self.__getlasterror(_res_getdouparam)
      raise Error(rescode(_res_getdouparam),_msg_getdouparam)
    parvalue = parvalue_.value
    return (parvalue_.value)
  def getdouparam(self,*args,**kwds):
    """
    Obtains a double parameter.
  
    getdouparam() -> (parvalue)
      [parvalue : float64]  Parameter value.  
    """
    return self.__getdouparam_2(*args,**kwds)
  def __getdualobj_2(self,whichsol : soltype):
    dualobj_ = ctypes.c_double()
    _res_getdualobj = __library__.MSK_getdualobj(self.__nativep,whichsol,ctypes.byref(dualobj_))
    if _res_getdualobj != 0:
      _,_msg_getdualobj = self.__getlasterror(_res_getdualobj)
      raise Error(rescode(_res_getdualobj),_msg_getdualobj)
    dualobj = dualobj_.value
    return (dualobj_.value)
  def getdualobj(self,*args,**kwds):
    """
    Computes the dual objective value associated with the solution.
  
    getdualobj() -> (dualobj)
      [dualobj : float64]  Objective value corresponding to the dual solution.  
    """
    return self.__getdualobj_2(*args,**kwds)
  def __getintinf_2(self,whichiinf : iinfitem):
    ivalue_ = ctypes.c_int32()
    _res_getintinf = __library__.MSK_getintinf(self.__nativep,whichiinf,ctypes.byref(ivalue_))
    if _res_getintinf != 0:
      _,_msg_getintinf = self.__getlasterror(_res_getintinf)
      raise Error(rescode(_res_getintinf),_msg_getintinf)
    ivalue = ivalue_.value
    return (ivalue_.value)
  def getintinf(self,*args,**kwds):
    """
    Obtains an integer information item.
  
    getintinf() -> (ivalue)
      [ivalue : int32]  The value of the required integer information item.  
    """
    return self.__getintinf_2(*args,**kwds)
  def __getlintinf_2(self,whichliinf : liinfitem):
    ivalue_ = ctypes.c_int64()
    _res_getlintinf = __library__.MSK_getlintinf(self.__nativep,whichliinf,ctypes.byref(ivalue_))
    if _res_getlintinf != 0:
      _,_msg_getlintinf = self.__getlasterror(_res_getlintinf)
      raise Error(rescode(_res_getlintinf),_msg_getlintinf)
    ivalue = ivalue_.value
    return (ivalue_.value)
  def getlintinf(self,*args,**kwds):
    """
    Obtains a long integer information item.
  
    getlintinf() -> (ivalue)
      [ivalue : int64]  The value of the required long integer information item.  
    """
    return self.__getlintinf_2(*args,**kwds)
  def __getintparam_2(self,param : iparam):
    parvalue_ = ctypes.c_int32()
    _res_getintparam = __library__.MSK_getintparam(self.__nativep,param,ctypes.byref(parvalue_))
    if _res_getintparam != 0:
      _,_msg_getintparam = self.__getlasterror(_res_getintparam)
      raise Error(rescode(_res_getintparam),_msg_getintparam)
    parvalue = parvalue_.value
    return (parvalue_.value)
  def getintparam(self,*args,**kwds):
    """
    Obtains an integer parameter.
  
    getintparam() -> (parvalue)
      [parvalue : int32]  Parameter value.  
    """
    return self.__getintparam_2(*args,**kwds)
  def __getmaxnumanz64_1(self):
    maxnumanz_ = ctypes.c_int64()
    _res_getmaxnumanz64 = __library__.MSK_getmaxnumanz64(self.__nativep,ctypes.byref(maxnumanz_))
    if _res_getmaxnumanz64 != 0:
      _,_msg_getmaxnumanz64 = self.__getlasterror(_res_getmaxnumanz64)
      raise Error(rescode(_res_getmaxnumanz64),_msg_getmaxnumanz64)
    maxnumanz = maxnumanz_.value
    return (maxnumanz_.value)
  def getmaxnumanz(self,*args,**kwds):
    """
    Obtains number of preallocated non-zeros in the linear constraint matrix.
  
    getmaxnumanz() -> (maxnumanz)
      [maxnumanz : int64]  Number of preallocated non-zero linear matrix elements.  
    """
    return self.__getmaxnumanz64_1(*args,**kwds)
  def __getmaxnumcon_1(self):
    maxnumcon_ = ctypes.c_int32()
    _res_getmaxnumcon = __library__.MSK_getmaxnumcon(self.__nativep,ctypes.byref(maxnumcon_))
    if _res_getmaxnumcon != 0:
      _,_msg_getmaxnumcon = self.__getlasterror(_res_getmaxnumcon)
      raise Error(rescode(_res_getmaxnumcon),_msg_getmaxnumcon)
    maxnumcon = maxnumcon_.value
    return (maxnumcon_.value)
  def getmaxnumcon(self,*args,**kwds):
    """
    Obtains the number of preallocated constraints in the optimization task.
  
    getmaxnumcon() -> (maxnumcon)
      [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
    """
    return self.__getmaxnumcon_1(*args,**kwds)
  def __getmaxnumvar_1(self):
    maxnumvar_ = ctypes.c_int32()
    _res_getmaxnumvar = __library__.MSK_getmaxnumvar(self.__nativep,ctypes.byref(maxnumvar_))
    if _res_getmaxnumvar != 0:
      _,_msg_getmaxnumvar = self.__getlasterror(_res_getmaxnumvar)
      raise Error(rescode(_res_getmaxnumvar),_msg_getmaxnumvar)
    maxnumvar = maxnumvar_.value
    return (maxnumvar_.value)
  def getmaxnumvar(self,*args,**kwds):
    """
    Obtains the maximum number variables allowed.
  
    getmaxnumvar() -> (maxnumvar)
      [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
    """
    return self.__getmaxnumvar_1(*args,**kwds)
  def __getbarvarnamelen_2(self,i):
    len_ = ctypes.c_int32()
    _res_getbarvarnamelen = __library__.MSK_getbarvarnamelen(self.__nativep,i,ctypes.byref(len_))
    if _res_getbarvarnamelen != 0:
      _,_msg_getbarvarnamelen = self.__getlasterror(_res_getbarvarnamelen)
      raise Error(rescode(_res_getbarvarnamelen),_msg_getbarvarnamelen)
    len = len_.value
    return (len_.value)
  def getbarvarnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a semidefinite variable.
  
    getbarvarnamelen(i) -> (len)
      [i : int32]  Index of the variable.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getbarvarnamelen_2(*args,**kwds)
  def __getbarvarname_2(self,i):
    __tmp_166 = ctypes.c_int32()
    _res_getbarvarnamelen = __library__.MSK_getbarvarnamelen(self.__nativep,i,ctypes.byref(__tmp_166))
    if _res_getbarvarnamelen != 0:
      _,_msg_getbarvarnamelen = self.__getlasterror(_res_getbarvarnamelen)
      raise Error(rescode(_res_getbarvarnamelen),_msg_getbarvarnamelen)
    sizename = (1 + __tmp_166.value);
    name = (ctypes.c_char*sizename)()
    _res_getbarvarname = __library__.MSK_getbarvarname(self.__nativep,i,sizename,name)
    if _res_getbarvarname != 0:
      _,_msg_getbarvarname = self.__getlasterror(_res_getbarvarname)
      raise Error(rescode(_res_getbarvarname),_msg_getbarvarname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getbarvarname(self,*args,**kwds):
    """
    Obtains the name of a semidefinite variable.
  
    getbarvarname(i) -> (name)
      [i : int32]  Index of the variable.  
      [name : str]  The requested name is copied to this buffer.  
    """
    return self.__getbarvarname_2(*args,**kwds)
  def __getbarvarnameindex_2(self,somename):
    asgn_ = ctypes.c_int32()
    index_ = ctypes.c_int32()
    _res_getbarvarnameindex = __library__.MSK_getbarvarnameindex(self.__nativep,somename.encode("UTF-8"),ctypes.byref(asgn_),ctypes.byref(index_))
    if _res_getbarvarnameindex != 0:
      _,_msg_getbarvarnameindex = self.__getlasterror(_res_getbarvarnameindex)
      raise Error(rescode(_res_getbarvarnameindex),_msg_getbarvarnameindex)
    asgn = asgn_.value
    index = index_.value
    return (asgn_.value,index_.value)
  def getbarvarnameindex(self,*args,**kwds):
    """
    Obtains the index of semidefinite variable from its name.
  
    getbarvarnameindex(somename) -> (asgn,index)
      [asgn : int32]  Non-zero if the name somename is assigned to some semidefinite variable.  
      [index : int32]  The index of a semidefinite variable with the name somename (if one exists).  
      [somename : str]  The name of the variable.  
    """
    return self.__getbarvarnameindex_2(*args,**kwds)
  def __generatebarvarnames_7(self,subj,fmt,dims,sp,namedaxisidxs,names):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_170 = (ctypes.c_char_p*len(names))()
      for __tmp_172,__tmp_171 in enumerate(names):
        __tmp_170[__tmp_172] = __tmp_171.encode("utf-8")
    else:
      __tmp_170 = None
    _res_generatebarvarnames = __library__.MSK_generatebarvarnames(self.__nativep,num,_tmparray_subj_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_170)
    if _res_generatebarvarnames != 0:
      _,_msg_generatebarvarnames = self.__getlasterror(_res_generatebarvarnames)
      raise Error(rescode(_res_generatebarvarnames),_msg_generatebarvarnames)
  def generatebarvarnames(self,*args,**kwds):
    """
    Generates systematic names for variables.
  
    generatebarvarnames(subj,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The variable name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [subj : array(int32)]  Indexes of the variables.  
    """
    return self.__generatebarvarnames_7(*args,**kwds)
  def __generatevarnames_7(self,subj,fmt,dims,sp,namedaxisidxs,names):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_176 = (ctypes.c_char_p*len(names))()
      for __tmp_178,__tmp_177 in enumerate(names):
        __tmp_176[__tmp_178] = __tmp_177.encode("utf-8")
    else:
      __tmp_176 = None
    _res_generatevarnames = __library__.MSK_generatevarnames(self.__nativep,num,_tmparray_subj_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_176)
    if _res_generatevarnames != 0:
      _,_msg_generatevarnames = self.__getlasterror(_res_generatevarnames)
      raise Error(rescode(_res_generatevarnames),_msg_generatevarnames)
  def generatevarnames(self,*args,**kwds):
    """
    Generates systematic names for variables.
  
    generatevarnames(subj,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The variable name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [subj : array(int32)]  Indexes of the variables.  
    """
    return self.__generatevarnames_7(*args,**kwds)
  def __generateconnames_7(self,subi,fmt,dims,sp,namedaxisidxs,names):
    num = len(subi) if subi is not None else 0
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_182 = (ctypes.c_char_p*len(names))()
      for __tmp_184,__tmp_183 in enumerate(names):
        __tmp_182[__tmp_184] = __tmp_183.encode("utf-8")
    else:
      __tmp_182 = None
    _res_generateconnames = __library__.MSK_generateconnames(self.__nativep,num,_tmparray_subi_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_182)
    if _res_generateconnames != 0:
      _,_msg_generateconnames = self.__getlasterror(_res_generateconnames)
      raise Error(rescode(_res_generateconnames),_msg_generateconnames)
  def generateconnames(self,*args,**kwds):
    """
    Generates systematic names for constraints.
  
    generateconnames(subi,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The constraint name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [subi : array(int32)]  Indexes of the constraints.  
    """
    return self.__generateconnames_7(*args,**kwds)
  def __generateconenames_7(self,subk,fmt,dims,sp,namedaxisidxs,names):
    num = len(subk) if subk is not None else 0
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_188 = (ctypes.c_char_p*len(names))()
      for __tmp_190,__tmp_189 in enumerate(names):
        __tmp_188[__tmp_190] = __tmp_189.encode("utf-8")
    else:
      __tmp_188 = None
    _res_generateconenames = __library__.MSK_generateconenames(self.__nativep,num,_tmparray_subk_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_188)
    if _res_generateconenames != 0:
      _,_msg_generateconenames = self.__getlasterror(_res_generateconenames)
      raise Error(rescode(_res_generateconenames),_msg_generateconenames)
  def generateconenames(self,*args,**kwds):
    """
    Generates systematic names for cone.
  
    generateconenames(subk,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The cone name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [subk : array(int32)]  Indexes of the cone.  
    """
    return self.__generateconenames_7(*args,**kwds)
  def __generateaccnames_7(self,sub,fmt,dims,sp,namedaxisidxs,names):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_194 = (ctypes.c_char_p*len(names))()
      for __tmp_196,__tmp_195 in enumerate(names):
        __tmp_194[__tmp_196] = __tmp_195.encode("utf-8")
    else:
      __tmp_194 = None
    _res_generateaccnames = __library__.MSK_generateaccnames(self.__nativep,num,_tmparray_sub_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_194)
    if _res_generateaccnames != 0:
      _,_msg_generateaccnames = self.__getlasterror(_res_generateaccnames)
      raise Error(rescode(_res_generateaccnames),_msg_generateaccnames)
  def generateaccnames(self,*args,**kwds):
    """
    Generates systematic names for affine conic constraints.
  
    generateaccnames(sub,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The variable name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [sub : array(int64)]  Indexes of the affine conic constraints.  
    """
    return self.__generateaccnames_7(*args,**kwds)
  def __generatedjcnames_7(self,sub,fmt,dims,sp,namedaxisidxs,names):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    ndims = len(dims) if dims is not None else 0
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_sp = False
    if sp is None:
      sp_ = None
      _tmparray_sp_ = None
    else:
      if len(sp) < int(num):
        raise ValueError("argument sp is too short")
      _tmparray_sp_ = (ctypes.c_int64*len(sp))(*sp)
    numnamedaxis = len(namedaxisidxs) if namedaxisidxs is not None else 0
    copyback_namedaxisidxs = False
    if namedaxisidxs is None:
      namedaxisidxs_ = None
      _tmparray_namedaxisidxs_ = None
    else:
      _tmparray_namedaxisidxs_ = (ctypes.c_int32*len(namedaxisidxs))(*namedaxisidxs)
    numnames = len(names) if names is not None else 0
    if names is not None:
      __tmp_200 = (ctypes.c_char_p*len(names))()
      for __tmp_202,__tmp_201 in enumerate(names):
        __tmp_200[__tmp_202] = __tmp_201.encode("utf-8")
    else:
      __tmp_200 = None
    _res_generatedjcnames = __library__.MSK_generatedjcnames(self.__nativep,num,_tmparray_sub_,fmt.encode("UTF-8"),ndims,_tmparray_dims_,_tmparray_sp_,numnamedaxis,_tmparray_namedaxisidxs_,numnames,__tmp_200)
    if _res_generatedjcnames != 0:
      _,_msg_generatedjcnames = self.__getlasterror(_res_generatedjcnames)
      raise Error(rescode(_res_generatedjcnames),_msg_generatedjcnames)
  def generatedjcnames(self,*args,**kwds):
    """
    Generates systematic names for affine conic constraints.
  
    generatedjcnames(sub,fmt,dims,sp,namedaxisidxs,names)
      [dims : array(int32)]  Dimensions in the shape.  
      [fmt : str]  The variable name formatting string.  
      [namedaxisidxs : array(int32)]  List if named index axes  
      [names : array(str)]  All axis names.  
      [sp : array(int64)]  Items that should be named.  
      [sub : array(int64)]  Indexes of the disjunctive constraints.  
    """
    return self.__generatedjcnames_7(*args,**kwds)
  def __putconname_3(self,i,name):
    _res_putconname = __library__.MSK_putconname(self.__nativep,i,name.encode("UTF-8"))
    if _res_putconname != 0:
      _,_msg_putconname = self.__getlasterror(_res_putconname)
      raise Error(rescode(_res_putconname),_msg_putconname)
  def putconname(self,*args,**kwds):
    """
    Sets the name of a constraint.
  
    putconname(i,name)
      [i : int32]  Index of the constraint.  
      [name : str]  The name of the constraint.  
    """
    return self.__putconname_3(*args,**kwds)
  def __putvarname_3(self,j,name):
    _res_putvarname = __library__.MSK_putvarname(self.__nativep,j,name.encode("UTF-8"))
    if _res_putvarname != 0:
      _,_msg_putvarname = self.__getlasterror(_res_putvarname)
      raise Error(rescode(_res_putvarname),_msg_putvarname)
  def putvarname(self,*args,**kwds):
    """
    Sets the name of a variable.
  
    putvarname(j,name)
      [j : int32]  Index of the variable.  
      [name : str]  The variable name.  
    """
    return self.__putvarname_3(*args,**kwds)
  def __putconename_3(self,j,name):
    _res_putconename = __library__.MSK_putconename(self.__nativep,j,name.encode("UTF-8"))
    if _res_putconename != 0:
      _,_msg_putconename = self.__getlasterror(_res_putconename)
      raise Error(rescode(_res_putconename),_msg_putconename)
  def putconename(self,*args,**kwds):
    """
    Sets the name of a cone.
  
    putconename(j,name)
      [j : int32]  Index of the cone.  
      [name : str]  The name of the cone.  
    """
    return self.__putconename_3(*args,**kwds)
  def __putbarvarname_3(self,j,name):
    _res_putbarvarname = __library__.MSK_putbarvarname(self.__nativep,j,name.encode("UTF-8"))
    if _res_putbarvarname != 0:
      _,_msg_putbarvarname = self.__getlasterror(_res_putbarvarname)
      raise Error(rescode(_res_putbarvarname),_msg_putbarvarname)
  def putbarvarname(self,*args,**kwds):
    """
    Sets the name of a semidefinite variable.
  
    putbarvarname(j,name)
      [j : int32]  Index of the variable.  
      [name : str]  The variable name.  
    """
    return self.__putbarvarname_3(*args,**kwds)
  def __putdomainname_3(self,domidx,name):
    _res_putdomainname = __library__.MSK_putdomainname(self.__nativep,domidx,name.encode("UTF-8"))
    if _res_putdomainname != 0:
      _,_msg_putdomainname = self.__getlasterror(_res_putdomainname)
      raise Error(rescode(_res_putdomainname),_msg_putdomainname)
  def putdomainname(self,*args,**kwds):
    """
    Sets the name of a domain.
  
    putdomainname(domidx,name)
      [domidx : int64]  Index of the domain.  
      [name : str]  The name of the domain.  
    """
    return self.__putdomainname_3(*args,**kwds)
  def __putdjcname_3(self,djcidx,name):
    _res_putdjcname = __library__.MSK_putdjcname(self.__nativep,djcidx,name.encode("UTF-8"))
    if _res_putdjcname != 0:
      _,_msg_putdjcname = self.__getlasterror(_res_putdjcname)
      raise Error(rescode(_res_putdjcname),_msg_putdjcname)
  def putdjcname(self,*args,**kwds):
    """
    Sets the name of a disjunctive constraint.
  
    putdjcname(djcidx,name)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [name : str]  The name of the disjunctive constraint.  
    """
    return self.__putdjcname_3(*args,**kwds)
  def __putaccname_3(self,accidx,name):
    _res_putaccname = __library__.MSK_putaccname(self.__nativep,accidx,name.encode("UTF-8"))
    if _res_putaccname != 0:
      _,_msg_putaccname = self.__getlasterror(_res_putaccname)
      raise Error(rescode(_res_putaccname),_msg_putaccname)
  def putaccname(self,*args,**kwds):
    """
    Sets the name of an affine conic constraint.
  
    putaccname(accidx,name)
      [accidx : int64]  Index of the affine conic constraint.  
      [name : str]  The name of the affine conic constraint.  
    """
    return self.__putaccname_3(*args,**kwds)
  def __getvarnamelen_2(self,i):
    len_ = ctypes.c_int32()
    _res_getvarnamelen = __library__.MSK_getvarnamelen(self.__nativep,i,ctypes.byref(len_))
    if _res_getvarnamelen != 0:
      _,_msg_getvarnamelen = self.__getlasterror(_res_getvarnamelen)
      raise Error(rescode(_res_getvarnamelen),_msg_getvarnamelen)
    len = len_.value
    return (len_.value)
  def getvarnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a variable.
  
    getvarnamelen(i) -> (len)
      [i : int32]  Index of a variable.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getvarnamelen_2(*args,**kwds)
  def __getvarname_2(self,j):
    __tmp_206 = ctypes.c_int32()
    _res_getvarnamelen = __library__.MSK_getvarnamelen(self.__nativep,j,ctypes.byref(__tmp_206))
    if _res_getvarnamelen != 0:
      _,_msg_getvarnamelen = self.__getlasterror(_res_getvarnamelen)
      raise Error(rescode(_res_getvarnamelen),_msg_getvarnamelen)
    sizename = (1 + __tmp_206.value);
    name = (ctypes.c_char*sizename)()
    _res_getvarname = __library__.MSK_getvarname(self.__nativep,j,sizename,name)
    if _res_getvarname != 0:
      _,_msg_getvarname = self.__getlasterror(_res_getvarname)
      raise Error(rescode(_res_getvarname),_msg_getvarname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getvarname(self,*args,**kwds):
    """
    Obtains the name of a variable.
  
    getvarname(j) -> (name)
      [j : int32]  Index of a variable.  
      [name : str]  Returns the required name.  
    """
    return self.__getvarname_2(*args,**kwds)
  def __getconnamelen_2(self,i):
    len_ = ctypes.c_int32()
    _res_getconnamelen = __library__.MSK_getconnamelen(self.__nativep,i,ctypes.byref(len_))
    if _res_getconnamelen != 0:
      _,_msg_getconnamelen = self.__getlasterror(_res_getconnamelen)
      raise Error(rescode(_res_getconnamelen),_msg_getconnamelen)
    len = len_.value
    return (len_.value)
  def getconnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a constraint.
  
    getconnamelen(i) -> (len)
      [i : int32]  Index of the constraint.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getconnamelen_2(*args,**kwds)
  def __getconname_2(self,i):
    __tmp_210 = ctypes.c_int32()
    _res_getconnamelen = __library__.MSK_getconnamelen(self.__nativep,i,ctypes.byref(__tmp_210))
    if _res_getconnamelen != 0:
      _,_msg_getconnamelen = self.__getlasterror(_res_getconnamelen)
      raise Error(rescode(_res_getconnamelen),_msg_getconnamelen)
    sizename = (1 + __tmp_210.value);
    name = (ctypes.c_char*sizename)()
    _res_getconname = __library__.MSK_getconname(self.__nativep,i,sizename,name)
    if _res_getconname != 0:
      _,_msg_getconname = self.__getlasterror(_res_getconname)
      raise Error(rescode(_res_getconname),_msg_getconname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getconname(self,*args,**kwds):
    """
    Obtains the name of a constraint.
  
    getconname(i) -> (name)
      [i : int32]  Index of the constraint.  
      [name : str]  The required name.  
    """
    return self.__getconname_2(*args,**kwds)
  def __getconnameindex_2(self,somename):
    asgn_ = ctypes.c_int32()
    index_ = ctypes.c_int32()
    _res_getconnameindex = __library__.MSK_getconnameindex(self.__nativep,somename.encode("UTF-8"),ctypes.byref(asgn_),ctypes.byref(index_))
    if _res_getconnameindex != 0:
      _,_msg_getconnameindex = self.__getlasterror(_res_getconnameindex)
      raise Error(rescode(_res_getconnameindex),_msg_getconnameindex)
    asgn = asgn_.value
    index = index_.value
    return (asgn_.value,index_.value)
  def getconnameindex(self,*args,**kwds):
    """
    Checks whether the name has been assigned to any constraint.
  
    getconnameindex(somename) -> (asgn,index)
      [asgn : int32]  Is non-zero if the name somename is assigned to some constraint.  
      [index : int32]  If the name somename is assigned to a constraint, then return the index of the constraint.  
      [somename : str]  The name which should be checked.  
    """
    return self.__getconnameindex_2(*args,**kwds)
  def __getvarnameindex_2(self,somename):
    asgn_ = ctypes.c_int32()
    index_ = ctypes.c_int32()
    _res_getvarnameindex = __library__.MSK_getvarnameindex(self.__nativep,somename.encode("UTF-8"),ctypes.byref(asgn_),ctypes.byref(index_))
    if _res_getvarnameindex != 0:
      _,_msg_getvarnameindex = self.__getlasterror(_res_getvarnameindex)
      raise Error(rescode(_res_getvarnameindex),_msg_getvarnameindex)
    asgn = asgn_.value
    index = index_.value
    return (asgn_.value,index_.value)
  def getvarnameindex(self,*args,**kwds):
    """
    Checks whether the name has been assigned to any variable.
  
    getvarnameindex(somename) -> (asgn,index)
      [asgn : int32]  Is non-zero if the name somename is assigned to a variable.  
      [index : int32]  If the name somename is assigned to a variable, then return the index of the variable.  
      [somename : str]  The name which should be checked.  
    """
    return self.__getvarnameindex_2(*args,**kwds)
  def __getconenamelen_2(self,i):
    len_ = ctypes.c_int32()
    _res_getconenamelen = __library__.MSK_getconenamelen(self.__nativep,i,ctypes.byref(len_))
    if _res_getconenamelen != 0:
      _,_msg_getconenamelen = self.__getlasterror(_res_getconenamelen)
      raise Error(rescode(_res_getconenamelen),_msg_getconenamelen)
    len = len_.value
    return (len_.value)
  def getconenamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a cone.
  
    getconenamelen(i) -> (len)
      [i : int32]  Index of the cone.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getconenamelen_2(*args,**kwds)
  def __getconename_2(self,i):
    __tmp_214 = ctypes.c_int32()
    _res_getconenamelen = __library__.MSK_getconenamelen(self.__nativep,i,ctypes.byref(__tmp_214))
    if _res_getconenamelen != 0:
      _,_msg_getconenamelen = self.__getlasterror(_res_getconenamelen)
      raise Error(rescode(_res_getconenamelen),_msg_getconenamelen)
    sizename = (1 + __tmp_214.value);
    name = (ctypes.c_char*sizename)()
    _res_getconename = __library__.MSK_getconename(self.__nativep,i,sizename,name)
    if _res_getconename != 0:
      _,_msg_getconename = self.__getlasterror(_res_getconename)
      raise Error(rescode(_res_getconename),_msg_getconename)
    return (name.value.decode("utf-8",errors="ignore"))
  def getconename(self,*args,**kwds):
    """
    Obtains the name of a cone.
  
    getconename(i) -> (name)
      [i : int32]  Index of the cone.  
      [name : str]  The required name.  
    """
    return self.__getconename_2(*args,**kwds)
  def __getconenameindex_2(self,somename):
    asgn_ = ctypes.c_int32()
    index_ = ctypes.c_int32()
    _res_getconenameindex = __library__.MSK_getconenameindex(self.__nativep,somename.encode("UTF-8"),ctypes.byref(asgn_),ctypes.byref(index_))
    if _res_getconenameindex != 0:
      _,_msg_getconenameindex = self.__getlasterror(_res_getconenameindex)
      raise Error(rescode(_res_getconenameindex),_msg_getconenameindex)
    asgn = asgn_.value
    index = index_.value
    return (asgn_.value,index_.value)
  def getconenameindex(self,*args,**kwds):
    """
    Checks whether the name has been assigned to any cone.
  
    getconenameindex(somename) -> (asgn,index)
      [asgn : int32]  Is non-zero if the name somename is assigned to some cone.  
      [index : int32]  If the name somename is assigned to some cone, this is the index of the cone.  
      [somename : str]  The name which should be checked.  
    """
    return self.__getconenameindex_2(*args,**kwds)
  def __getdomainnamelen_2(self,domidx):
    len_ = ctypes.c_int32()
    _res_getdomainnamelen = __library__.MSK_getdomainnamelen(self.__nativep,domidx,ctypes.byref(len_))
    if _res_getdomainnamelen != 0:
      _,_msg_getdomainnamelen = self.__getlasterror(_res_getdomainnamelen)
      raise Error(rescode(_res_getdomainnamelen),_msg_getdomainnamelen)
    len = len_.value
    return (len_.value)
  def getdomainnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a domain.
  
    getdomainnamelen(domidx) -> (len)
      [domidx : int64]  Index of a domain.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getdomainnamelen_2(*args,**kwds)
  def __getdomainname_2(self,domidx):
    __tmp_218 = ctypes.c_int32()
    _res_getdomainnamelen = __library__.MSK_getdomainnamelen(self.__nativep,domidx,ctypes.byref(__tmp_218))
    if _res_getdomainnamelen != 0:
      _,_msg_getdomainnamelen = self.__getlasterror(_res_getdomainnamelen)
      raise Error(rescode(_res_getdomainnamelen),_msg_getdomainnamelen)
    sizename = (1 + __tmp_218.value);
    name = (ctypes.c_char*sizename)()
    _res_getdomainname = __library__.MSK_getdomainname(self.__nativep,domidx,sizename,name)
    if _res_getdomainname != 0:
      _,_msg_getdomainname = self.__getlasterror(_res_getdomainname)
      raise Error(rescode(_res_getdomainname),_msg_getdomainname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getdomainname(self,*args,**kwds):
    """
    Obtains the name of a domain.
  
    getdomainname(domidx) -> (name)
      [domidx : int64]  Index of a domain.  
      [name : str]  Returns the required name.  
    """
    return self.__getdomainname_2(*args,**kwds)
  def __getdjcnamelen_2(self,djcidx):
    len_ = ctypes.c_int32()
    _res_getdjcnamelen = __library__.MSK_getdjcnamelen(self.__nativep,djcidx,ctypes.byref(len_))
    if _res_getdjcnamelen != 0:
      _,_msg_getdjcnamelen = self.__getlasterror(_res_getdjcnamelen)
      raise Error(rescode(_res_getdjcnamelen),_msg_getdjcnamelen)
    len = len_.value
    return (len_.value)
  def getdjcnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of a disjunctive constraint.
  
    getdjcnamelen(djcidx) -> (len)
      [djcidx : int64]  Index of a disjunctive constraint.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getdjcnamelen_2(*args,**kwds)
  def __getdjcname_2(self,djcidx):
    __tmp_222 = ctypes.c_int32()
    _res_getdjcnamelen = __library__.MSK_getdjcnamelen(self.__nativep,djcidx,ctypes.byref(__tmp_222))
    if _res_getdjcnamelen != 0:
      _,_msg_getdjcnamelen = self.__getlasterror(_res_getdjcnamelen)
      raise Error(rescode(_res_getdjcnamelen),_msg_getdjcnamelen)
    sizename = (1 + __tmp_222.value);
    name = (ctypes.c_char*sizename)()
    _res_getdjcname = __library__.MSK_getdjcname(self.__nativep,djcidx,sizename,name)
    if _res_getdjcname != 0:
      _,_msg_getdjcname = self.__getlasterror(_res_getdjcname)
      raise Error(rescode(_res_getdjcname),_msg_getdjcname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getdjcname(self,*args,**kwds):
    """
    Obtains the name of a disjunctive constraint.
  
    getdjcname(djcidx) -> (name)
      [djcidx : int64]  Index of a disjunctive constraint.  
      [name : str]  Returns the required name.  
    """
    return self.__getdjcname_2(*args,**kwds)
  def __getaccnamelen_2(self,accidx):
    len_ = ctypes.c_int32()
    _res_getaccnamelen = __library__.MSK_getaccnamelen(self.__nativep,accidx,ctypes.byref(len_))
    if _res_getaccnamelen != 0:
      _,_msg_getaccnamelen = self.__getlasterror(_res_getaccnamelen)
      raise Error(rescode(_res_getaccnamelen),_msg_getaccnamelen)
    len = len_.value
    return (len_.value)
  def getaccnamelen(self,*args,**kwds):
    """
    Obtains the length of the name of an affine conic constraint.
  
    getaccnamelen(accidx) -> (len)
      [accidx : int64]  Index of an affine conic constraint.  
      [len : int32]  Returns the length of the indicated name.  
    """
    return self.__getaccnamelen_2(*args,**kwds)
  def __getaccname_2(self,accidx):
    __tmp_226 = ctypes.c_int32()
    _res_getaccnamelen = __library__.MSK_getaccnamelen(self.__nativep,accidx,ctypes.byref(__tmp_226))
    if _res_getaccnamelen != 0:
      _,_msg_getaccnamelen = self.__getlasterror(_res_getaccnamelen)
      raise Error(rescode(_res_getaccnamelen),_msg_getaccnamelen)
    sizename = (1 + __tmp_226.value);
    name = (ctypes.c_char*sizename)()
    _res_getaccname = __library__.MSK_getaccname(self.__nativep,accidx,sizename,name)
    if _res_getaccname != 0:
      _,_msg_getaccname = self.__getlasterror(_res_getaccname)
      raise Error(rescode(_res_getaccname),_msg_getaccname)
    return (name.value.decode("utf-8",errors="ignore"))
  def getaccname(self,*args,**kwds):
    """
    Obtains the name of an affine conic constraint.
  
    getaccname(accidx) -> (name)
      [accidx : int64]  Index of an affine conic constraint.  
      [name : str]  Returns the required name.  
    """
    return self.__getaccname_2(*args,**kwds)
  def __getnumanz_1(self):
    numanz_ = ctypes.c_int32()
    _res_getnumanz = __library__.MSK_getnumanz(self.__nativep,ctypes.byref(numanz_))
    if _res_getnumanz != 0:
      _,_msg_getnumanz = self.__getlasterror(_res_getnumanz)
      raise Error(rescode(_res_getnumanz),_msg_getnumanz)
    numanz = numanz_.value
    return (numanz_.value)
  def getnumanz(self,*args,**kwds):
    """
    Obtains the number of non-zeros in the coefficient matrix.
  
    getnumanz() -> (numanz)
      [numanz : int32]  Number of non-zero elements in the linear constraint matrix.  
    """
    return self.__getnumanz_1(*args,**kwds)
  def __getnumanz64_1(self):
    numanz_ = ctypes.c_int64()
    _res_getnumanz64 = __library__.MSK_getnumanz64(self.__nativep,ctypes.byref(numanz_))
    if _res_getnumanz64 != 0:
      _,_msg_getnumanz64 = self.__getlasterror(_res_getnumanz64)
      raise Error(rescode(_res_getnumanz64),_msg_getnumanz64)
    numanz = numanz_.value
    return (numanz_.value)
  def getnumanz64(self,*args,**kwds):
    """
    Obtains the number of non-zeros in the coefficient matrix.
  
    getnumanz64() -> (numanz)
      [numanz : int64]  Number of non-zero elements in the linear constraint matrix.  
    """
    return self.__getnumanz64_1(*args,**kwds)
  def __getnumcon_1(self):
    numcon_ = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(numcon_))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    numcon = numcon_.value
    return (numcon_.value)
  def getnumcon(self,*args,**kwds):
    """
    Obtains the number of constraints.
  
    getnumcon() -> (numcon)
      [numcon : int32]  Number of constraints.  
    """
    return self.__getnumcon_1(*args,**kwds)
  def __getnumcone_1(self):
    numcone_ = ctypes.c_int32()
    _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(numcone_))
    if _res_getnumcone != 0:
      _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
      raise Error(rescode(_res_getnumcone),_msg_getnumcone)
    numcone = numcone_.value
    return (numcone_.value)
  def getnumcone(self,*args,**kwds):
    """
    Obtains the number of cones.
  
    getnumcone() -> (numcone)
      [numcone : int32]  Number of conic constraints.  
    """
    return self.__getnumcone_1(*args,**kwds)
  def __getnumconemem_2(self,k):
    nummem_ = ctypes.c_int32()
    _res_getnumconemem = __library__.MSK_getnumconemem(self.__nativep,k,ctypes.byref(nummem_))
    if _res_getnumconemem != 0:
      _,_msg_getnumconemem = self.__getlasterror(_res_getnumconemem)
      raise Error(rescode(_res_getnumconemem),_msg_getnumconemem)
    nummem = nummem_.value
    return (nummem_.value)
  def getnumconemem(self,*args,**kwds):
    """
    Obtains the number of members in a cone.
  
    getnumconemem(k) -> (nummem)
      [k : int32]  Index of the cone.  
      [nummem : int32]  Number of member variables in the cone.  
    """
    return self.__getnumconemem_2(*args,**kwds)
  def __getnumintvar_1(self):
    numintvar_ = ctypes.c_int32()
    _res_getnumintvar = __library__.MSK_getnumintvar(self.__nativep,ctypes.byref(numintvar_))
    if _res_getnumintvar != 0:
      _,_msg_getnumintvar = self.__getlasterror(_res_getnumintvar)
      raise Error(rescode(_res_getnumintvar),_msg_getnumintvar)
    numintvar = numintvar_.value
    return (numintvar_.value)
  def getnumintvar(self,*args,**kwds):
    """
    Obtains the number of integer-constrained variables.
  
    getnumintvar() -> (numintvar)
      [numintvar : int32]  Number of integer variables.  
    """
    return self.__getnumintvar_1(*args,**kwds)
  def __getnumparam_2(self,partype : parametertype):
    numparam_ = ctypes.c_int32()
    _res_getnumparam = __library__.MSK_getnumparam(self.__nativep,partype,ctypes.byref(numparam_))
    if _res_getnumparam != 0:
      _,_msg_getnumparam = self.__getlasterror(_res_getnumparam)
      raise Error(rescode(_res_getnumparam),_msg_getnumparam)
    numparam = numparam_.value
    return (numparam_.value)
  def getnumparam(self,*args,**kwds):
    """
    Obtains the number of parameters of a given type.
  
    getnumparam() -> (numparam)
      [numparam : int32]  Returns the number of parameters of the requested type.  
    """
    return self.__getnumparam_2(*args,**kwds)
  def __getnumqconknz64_2(self,k):
    numqcnz_ = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(numqcnz_))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    numqcnz = numqcnz_.value
    return (numqcnz_.value)
  def getnumqconknz(self,*args,**kwds):
    """
    Obtains the number of non-zero quadratic terms in a constraint.
  
    getnumqconknz(k) -> (numqcnz)
      [k : int32]  Index of the constraint for which the number quadratic terms should be obtained.  
      [numqcnz : int64]  Number of quadratic terms.  
    """
    return self.__getnumqconknz64_2(*args,**kwds)
  def __getnumqobjnz64_1(self):
    numqonz_ = ctypes.c_int64()
    _res_getnumqobjnz64 = __library__.MSK_getnumqobjnz64(self.__nativep,ctypes.byref(numqonz_))
    if _res_getnumqobjnz64 != 0:
      _,_msg_getnumqobjnz64 = self.__getlasterror(_res_getnumqobjnz64)
      raise Error(rescode(_res_getnumqobjnz64),_msg_getnumqobjnz64)
    numqonz = numqonz_.value
    return (numqonz_.value)
  def getnumqobjnz(self,*args,**kwds):
    """
    Obtains the number of non-zero quadratic terms in the objective.
  
    getnumqobjnz() -> (numqonz)
      [numqonz : int64]  Number of non-zero elements in the quadratic objective terms.  
    """
    return self.__getnumqobjnz64_1(*args,**kwds)
  def __getnumvar_1(self):
    numvar_ = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(numvar_))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    numvar = numvar_.value
    return (numvar_.value)
  def getnumvar(self,*args,**kwds):
    """
    Obtains the number of variables.
  
    getnumvar() -> (numvar)
      [numvar : int32]  Number of variables.  
    """
    return self.__getnumvar_1(*args,**kwds)
  def __getnumbarvar_1(self):
    numbarvar_ = ctypes.c_int32()
    _res_getnumbarvar = __library__.MSK_getnumbarvar(self.__nativep,ctypes.byref(numbarvar_))
    if _res_getnumbarvar != 0:
      _,_msg_getnumbarvar = self.__getlasterror(_res_getnumbarvar)
      raise Error(rescode(_res_getnumbarvar),_msg_getnumbarvar)
    numbarvar = numbarvar_.value
    return (numbarvar_.value)
  def getnumbarvar(self,*args,**kwds):
    """
    Obtains the number of semidefinite variables.
  
    getnumbarvar() -> (numbarvar)
      [numbarvar : int32]  Number of semidefinite variables in the problem.  
    """
    return self.__getnumbarvar_1(*args,**kwds)
  def __getmaxnumbarvar_1(self):
    maxnumbarvar_ = ctypes.c_int32()
    _res_getmaxnumbarvar = __library__.MSK_getmaxnumbarvar(self.__nativep,ctypes.byref(maxnumbarvar_))
    if _res_getmaxnumbarvar != 0:
      _,_msg_getmaxnumbarvar = self.__getlasterror(_res_getmaxnumbarvar)
      raise Error(rescode(_res_getmaxnumbarvar),_msg_getmaxnumbarvar)
    maxnumbarvar = maxnumbarvar_.value
    return (maxnumbarvar_.value)
  def getmaxnumbarvar(self,*args,**kwds):
    """
    Obtains maximum number of symmetric matrix variables for which space is currently preallocated.
  
    getmaxnumbarvar() -> (maxnumbarvar)
      [maxnumbarvar : int32]  Maximum number of symmetric matrix variables for which space is currently preallocated.  
    """
    return self.__getmaxnumbarvar_1(*args,**kwds)
  def __getdimbarvarj_2(self,j):
    dimbarvarj_ = ctypes.c_int32()
    _res_getdimbarvarj = __library__.MSK_getdimbarvarj(self.__nativep,j,ctypes.byref(dimbarvarj_))
    if _res_getdimbarvarj != 0:
      _,_msg_getdimbarvarj = self.__getlasterror(_res_getdimbarvarj)
      raise Error(rescode(_res_getdimbarvarj),_msg_getdimbarvarj)
    dimbarvarj = dimbarvarj_.value
    return (dimbarvarj_.value)
  def getdimbarvarj(self,*args,**kwds):
    """
    Obtains the dimension of a symmetric matrix variable.
  
    getdimbarvarj(j) -> (dimbarvarj)
      [dimbarvarj : int32]  The dimension of the j'th semidefinite variable.  
      [j : int32]  Index of the semidefinite variable whose dimension is requested.  
    """
    return self.__getdimbarvarj_2(*args,**kwds)
  def __getlenbarvarj_2(self,j):
    lenbarvarj_ = ctypes.c_int64()
    _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(lenbarvarj_))
    if _res_getlenbarvarj != 0:
      _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
      raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
    lenbarvarj = lenbarvarj_.value
    return (lenbarvarj_.value)
  def getlenbarvarj(self,*args,**kwds):
    """
    Obtains the length of one semidefinite variable.
  
    getlenbarvarj(j) -> (lenbarvarj)
      [j : int32]  Index of the semidefinite variable whose length if requested.  
      [lenbarvarj : int64]  Number of scalar elements in the lower triangular part of the semidefinite variable.  
    """
    return self.__getlenbarvarj_2(*args,**kwds)
  def __getobjname_1(self):
    __tmp_230 = ctypes.c_int32()
    _res_getobjnamelen = __library__.MSK_getobjnamelen(self.__nativep,ctypes.byref(__tmp_230))
    if _res_getobjnamelen != 0:
      _,_msg_getobjnamelen = self.__getlasterror(_res_getobjnamelen)
      raise Error(rescode(_res_getobjnamelen),_msg_getobjnamelen)
    sizeobjname = (1 + __tmp_230.value);
    objname = (ctypes.c_char*sizeobjname)()
    _res_getobjname = __library__.MSK_getobjname(self.__nativep,sizeobjname,objname)
    if _res_getobjname != 0:
      _,_msg_getobjname = self.__getlasterror(_res_getobjname)
      raise Error(rescode(_res_getobjname),_msg_getobjname)
    return (objname.value.decode("utf-8",errors="ignore"))
  def getobjname(self,*args,**kwds):
    """
    Obtains the name assigned to the objective function.
  
    getobjname() -> (objname)
      [objname : str]  Assigned the objective name.  
    """
    return self.__getobjname_1(*args,**kwds)
  def __getobjnamelen_1(self):
    len_ = ctypes.c_int32()
    _res_getobjnamelen = __library__.MSK_getobjnamelen(self.__nativep,ctypes.byref(len_))
    if _res_getobjnamelen != 0:
      _,_msg_getobjnamelen = self.__getlasterror(_res_getobjnamelen)
      raise Error(rescode(_res_getobjnamelen),_msg_getobjnamelen)
    len = len_.value
    return (len_.value)
  def getobjnamelen(self,*args,**kwds):
    """
    Obtains the length of the name assigned to the objective function.
  
    getobjnamelen() -> (len)
      [len : int32]  Assigned the length of the objective name.  
    """
    return self.__getobjnamelen_1(*args,**kwds)
  def __getprimalobj_2(self,whichsol : soltype):
    primalobj_ = ctypes.c_double()
    _res_getprimalobj = __library__.MSK_getprimalobj(self.__nativep,whichsol,ctypes.byref(primalobj_))
    if _res_getprimalobj != 0:
      _,_msg_getprimalobj = self.__getlasterror(_res_getprimalobj)
      raise Error(rescode(_res_getprimalobj),_msg_getprimalobj)
    primalobj = primalobj_.value
    return (primalobj_.value)
  def getprimalobj(self,*args,**kwds):
    """
    Computes the primal objective value for the desired solution.
  
    getprimalobj() -> (primalobj)
      [primalobj : float64]  Objective value corresponding to the primal solution.  
    """
    return self.__getprimalobj_2(*args,**kwds)
  def __getprobtype_1(self):
    probtype = ctypes.c_int()
    _res_getprobtype = __library__.MSK_getprobtype(self.__nativep,ctypes.byref(probtype))
    if _res_getprobtype != 0:
      _,_msg_getprobtype = self.__getlasterror(_res_getprobtype)
      raise Error(rescode(_res_getprobtype),_msg_getprobtype)
    return (problemtype(probtype.value))
  def getprobtype(self,*args,**kwds):
    """
    Obtains the problem type.
  
    getprobtype() -> (probtype)
      [probtype : mosek.problemtype]  The problem type.  
    """
    return self.__getprobtype_1(*args,**kwds)
  def __getqconk64_5(self,k,qcsubi,qcsubj,qcval):
    __tmp_234 = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_234))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    maxnumqcnz = __tmp_234.value;
    numqcnz_ = ctypes.c_int64()
    copyback_qcsubi = False
    if qcsubi is None:
      qcsubi_ = None
      _tmparray_qcsubi_ = None
    else:
      __tmp_236 = ctypes.c_int64()
      _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_236))
      if _res_getnumqconknz64 != 0:
        _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
        raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
      if len(qcsubi) < int(__tmp_236.value):
        raise ValueError("argument qcsubi is too short")
      _tmparray_qcsubi_ = (ctypes.c_int32*len(qcsubi))(*qcsubi)
    copyback_qcsubj = False
    if qcsubj is None:
      qcsubj_ = None
      _tmparray_qcsubj_ = None
    else:
      __tmp_240 = ctypes.c_int64()
      _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_240))
      if _res_getnumqconknz64 != 0:
        _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
        raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
      if len(qcsubj) < int(__tmp_240.value):
        raise ValueError("argument qcsubj is too short")
      _tmparray_qcsubj_ = (ctypes.c_int32*len(qcsubj))(*qcsubj)
    copyback_qcval = False
    if qcval is None:
      qcval_ = None
      _tmparray_qcval_ = None
    else:
      __tmp_244 = ctypes.c_int64()
      _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_244))
      if _res_getnumqconknz64 != 0:
        _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
        raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
      if len(qcval) < int(__tmp_244.value):
        raise ValueError("argument qcval is too short")
      _tmparray_qcval_ = (ctypes.c_double*len(qcval))(*qcval)
    _res_getqconk64 = __library__.MSK_getqconk64(self.__nativep,k,maxnumqcnz,ctypes.byref(numqcnz_),_tmparray_qcsubi_,_tmparray_qcsubj_,_tmparray_qcval_)
    if _res_getqconk64 != 0:
      _,_msg_getqconk64 = self.__getlasterror(_res_getqconk64)
      raise Error(rescode(_res_getqconk64),_msg_getqconk64)
    numqcnz = numqcnz_.value
    if qcsubi is not None:
      for __tmp_238,__tmp_239 in enumerate(_tmparray_qcsubi_):
        qcsubi[__tmp_238] = __tmp_239
    if qcsubj is not None:
      for __tmp_242,__tmp_243 in enumerate(_tmparray_qcsubj_):
        qcsubj[__tmp_242] = __tmp_243
    if qcval is not None:
      for __tmp_246,__tmp_247 in enumerate(_tmparray_qcval_):
        qcval[__tmp_246] = __tmp_247
    return (numqcnz_.value)
  def __getqconk64_2(self,k):
    __tmp_248 = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_248))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    maxnumqcnz = __tmp_248.value;
    numqcnz_ = ctypes.c_int64()
    __tmp_250 = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_250))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    qcsubi = numpy.zeros(__tmp_250.value,numpy.int32)
    __tmp_253 = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_253))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    qcsubj = numpy.zeros(__tmp_253.value,numpy.int32)
    __tmp_256 = ctypes.c_int64()
    _res_getnumqconknz64 = __library__.MSK_getnumqconknz64(self.__nativep,k,ctypes.byref(__tmp_256))
    if _res_getnumqconknz64 != 0:
      _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
      raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
    qcval = numpy.zeros(__tmp_256.value,numpy.float64)
    _res_getqconk64 = __library__.MSK_getqconk64(self.__nativep,k,maxnumqcnz,ctypes.byref(numqcnz_),ctypes.cast(qcsubi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(qcsubj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(qcval.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getqconk64 != 0:
      _,_msg_getqconk64 = self.__getlasterror(_res_getqconk64)
      raise Error(rescode(_res_getqconk64),_msg_getqconk64)
    numqcnz = numqcnz_.value
    return (numqcnz_.value,qcsubi,qcsubj,qcval)
  def getqconk(self,*args,**kwds):
    """
    Obtains all the quadratic terms in a constraint.
  
    getqconk(k,qcsubi,qcsubj,qcval) -> (numqcnz)
    getqconk(k) -> (numqcnz,qcsubi,qcsubj,qcval)
      [k : int32]  Which constraint.  
      [numqcnz : int64]  Number of quadratic terms.  
      [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
      [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
      [qcval : array(float64)]  Quadratic constraint coefficient values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getqconk64_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getqconk64_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getqobj64_4(self,qosubi,qosubj,qoval):
    __tmp_259 = ctypes.c_int64()
    _res_getnumqobjnz64 = __library__.MSK_getnumqobjnz64(self.__nativep,ctypes.byref(__tmp_259))
    if _res_getnumqobjnz64 != 0:
      _,_msg_getnumqobjnz64 = self.__getlasterror(_res_getnumqobjnz64)
      raise Error(rescode(_res_getnumqobjnz64),_msg_getnumqobjnz64)
    maxnumqonz = __tmp_259.value;
    numqonz_ = ctypes.c_int64()
    copyback_qosubi = False
    if qosubi is None:
      qosubi_ = None
      _tmparray_qosubi_ = None
    else:
      if len(qosubi) < int(maxnumqonz):
        raise ValueError("argument qosubi is too short")
      _tmparray_qosubi_ = (ctypes.c_int32*len(qosubi))(*qosubi)
    copyback_qosubj = False
    if qosubj is None:
      qosubj_ = None
      _tmparray_qosubj_ = None
    else:
      if len(qosubj) < int(maxnumqonz):
        raise ValueError("argument qosubj is too short")
      _tmparray_qosubj_ = (ctypes.c_int32*len(qosubj))(*qosubj)
    copyback_qoval = False
    if qoval is None:
      qoval_ = None
      _tmparray_qoval_ = None
    else:
      if len(qoval) < int(maxnumqonz):
        raise ValueError("argument qoval is too short")
      _tmparray_qoval_ = (ctypes.c_double*len(qoval))(*qoval)
    _res_getqobj64 = __library__.MSK_getqobj64(self.__nativep,maxnumqonz,ctypes.byref(numqonz_),_tmparray_qosubi_,_tmparray_qosubj_,_tmparray_qoval_)
    if _res_getqobj64 != 0:
      _,_msg_getqobj64 = self.__getlasterror(_res_getqobj64)
      raise Error(rescode(_res_getqobj64),_msg_getqobj64)
    numqonz = numqonz_.value
    if qosubi is not None:
      for __tmp_261,__tmp_262 in enumerate(_tmparray_qosubi_):
        qosubi[__tmp_261] = __tmp_262
    if qosubj is not None:
      for __tmp_263,__tmp_264 in enumerate(_tmparray_qosubj_):
        qosubj[__tmp_263] = __tmp_264
    if qoval is not None:
      for __tmp_265,__tmp_266 in enumerate(_tmparray_qoval_):
        qoval[__tmp_265] = __tmp_266
    return (numqonz_.value)
  def __getqobj64_1(self):
    __tmp_267 = ctypes.c_int64()
    _res_getnumqobjnz64 = __library__.MSK_getnumqobjnz64(self.__nativep,ctypes.byref(__tmp_267))
    if _res_getnumqobjnz64 != 0:
      _,_msg_getnumqobjnz64 = self.__getlasterror(_res_getnumqobjnz64)
      raise Error(rescode(_res_getnumqobjnz64),_msg_getnumqobjnz64)
    maxnumqonz = __tmp_267.value;
    numqonz_ = ctypes.c_int64()
    qosubi = numpy.zeros(maxnumqonz,numpy.int32)
    qosubj = numpy.zeros(maxnumqonz,numpy.int32)
    qoval = numpy.zeros(maxnumqonz,numpy.float64)
    _res_getqobj64 = __library__.MSK_getqobj64(self.__nativep,maxnumqonz,ctypes.byref(numqonz_),ctypes.cast(qosubi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(qosubj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(qoval.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getqobj64 != 0:
      _,_msg_getqobj64 = self.__getlasterror(_res_getqobj64)
      raise Error(rescode(_res_getqobj64),_msg_getqobj64)
    numqonz = numqonz_.value
    return (numqonz_.value,qosubi,qosubj,qoval)
  def getqobj(self,*args,**kwds):
    """
    Obtains all the quadratic terms in the objective.
  
    getqobj(qosubi,qosubj,qoval) -> (numqonz)
    getqobj() -> (numqonz,qosubi,qosubj,qoval)
      [numqonz : int64]  Number of non-zero elements in the quadratic objective terms.  
      [qosubi : array(int32)]  Row subscripts for quadratic objective coefficients.  
      [qosubj : array(int32)]  Column subscripts for quadratic objective coefficients.  
      [qoval : array(float64)]  Quadratic objective coefficient values.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getqobj64_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getqobj64_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getqobjij_3(self,i,j):
    qoij_ = ctypes.c_double()
    _res_getqobjij = __library__.MSK_getqobjij(self.__nativep,i,j,ctypes.byref(qoij_))
    if _res_getqobjij != 0:
      _,_msg_getqobjij = self.__getlasterror(_res_getqobjij)
      raise Error(rescode(_res_getqobjij),_msg_getqobjij)
    qoij = qoij_.value
    return (qoij_.value)
  def getqobjij(self,*args,**kwds):
    """
    Obtains one coefficient from the quadratic term of the objective
  
    getqobjij(i,j) -> (qoij)
      [i : int32]  Row index of the coefficient.  
      [j : int32]  Column index of coefficient.  
      [qoij : float64]  The required coefficient.  
    """
    return self.__getqobjij_3(*args,**kwds)
  def __getsolution_13(self,whichsol : soltype,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx):
    problemsta = ctypes.c_int()
    solutionsta = ctypes.c_int()
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_272 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_272))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(skc) < __tmp_272.value:
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))()
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_276 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_276))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(skx) < __tmp_276.value:
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))()
    if skn is None:
      _tmparray_skn_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_280 = ctypes.c_int32()
      _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_280))
      if _res_getnumcone != 0:
        _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
        raise Error(rescode(_res_getnumcone),_msg_getnumcone)
      if len(skn) < __tmp_280.value:
        raise ValueError("argument skn is too short")
      _tmparray_skn_ = (ctypes.c_int32*len(skn))()
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      __tmp_284 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_284))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(xc) < int(__tmp_284.value):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      __tmp_288 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_288))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(xx) < int(__tmp_288.value):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      __tmp_292 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_292))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(y) < int(__tmp_292.value):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      __tmp_296 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_296))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(slc) < int(__tmp_296.value):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      __tmp_300 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_300))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(suc) < int(__tmp_300.value):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      __tmp_304 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_304))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(slx) < int(__tmp_304.value):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      __tmp_308 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_308))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(sux) < int(__tmp_308.value):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      __tmp_312 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_312))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(snx) < int(__tmp_312.value):
        raise ValueError("argument snx is too short")
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    _res_getsolution = __library__.MSK_getsolution(self.__nativep,whichsol,ctypes.byref(problemsta),ctypes.byref(solutionsta),_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,_tmparray_xc_,_tmparray_xx_,_tmparray_y_,_tmparray_slc_,_tmparray_suc_,_tmparray_slx_,_tmparray_sux_,_tmparray_snx_)
    if _res_getsolution != 0:
      _,_msg_getsolution = self.__getlasterror(_res_getsolution)
      raise Error(rescode(_res_getsolution),_msg_getsolution)
    if skc is not None:
      for __tmp_274,__tmp_275 in enumerate(_tmparray_skc_):
        skc[__tmp_274] = stakey(__tmp_275)
    if skx is not None:
      for __tmp_278,__tmp_279 in enumerate(_tmparray_skx_):
        skx[__tmp_278] = stakey(__tmp_279)
    if skn is not None:
      for __tmp_282,__tmp_283 in enumerate(_tmparray_skn_):
        skn[__tmp_282] = stakey(__tmp_283)
    if xc is not None:
      for __tmp_286,__tmp_287 in enumerate(_tmparray_xc_):
        xc[__tmp_286] = __tmp_287
    if xx is not None:
      for __tmp_290,__tmp_291 in enumerate(_tmparray_xx_):
        xx[__tmp_290] = __tmp_291
    if y is not None:
      for __tmp_294,__tmp_295 in enumerate(_tmparray_y_):
        y[__tmp_294] = __tmp_295
    if slc is not None:
      for __tmp_298,__tmp_299 in enumerate(_tmparray_slc_):
        slc[__tmp_298] = __tmp_299
    if suc is not None:
      for __tmp_302,__tmp_303 in enumerate(_tmparray_suc_):
        suc[__tmp_302] = __tmp_303
    if slx is not None:
      for __tmp_306,__tmp_307 in enumerate(_tmparray_slx_):
        slx[__tmp_306] = __tmp_307
    if sux is not None:
      for __tmp_310,__tmp_311 in enumerate(_tmparray_sux_):
        sux[__tmp_310] = __tmp_311
    if snx is not None:
      for __tmp_314,__tmp_315 in enumerate(_tmparray_snx_):
        snx[__tmp_314] = __tmp_315
    return (prosta(problemsta.value),solsta(solutionsta.value))
  def __getsolution_2(self,whichsol : soltype):
    problemsta = ctypes.c_int()
    solutionsta = ctypes.c_int()
    __tmp_316 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_316))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    _tmparray_skc_ = (ctypes.c_int32*__tmp_316.value)()
    __tmp_318 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_318))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    _tmparray_skx_ = (ctypes.c_int32*__tmp_318.value)()
    __tmp_320 = ctypes.c_int32()
    _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_320))
    if _res_getnumcone != 0:
      _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
      raise Error(rescode(_res_getnumcone),_msg_getnumcone)
    _tmparray_skn_ = (ctypes.c_int32*__tmp_320.value)()
    __tmp_322 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_322))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    xc = numpy.zeros(__tmp_322.value,numpy.float64)
    __tmp_325 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_325))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    xx = numpy.zeros(__tmp_325.value,numpy.float64)
    __tmp_328 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_328))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    y = numpy.zeros(__tmp_328.value,numpy.float64)
    __tmp_331 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_331))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    slc = numpy.zeros(__tmp_331.value,numpy.float64)
    __tmp_334 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_334))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    suc = numpy.zeros(__tmp_334.value,numpy.float64)
    __tmp_337 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_337))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    slx = numpy.zeros(__tmp_337.value,numpy.float64)
    __tmp_340 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_340))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    sux = numpy.zeros(__tmp_340.value,numpy.float64)
    __tmp_343 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_343))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    snx = numpy.zeros(__tmp_343.value,numpy.float64)
    _res_getsolution = __library__.MSK_getsolution(self.__nativep,whichsol,ctypes.byref(problemsta),ctypes.byref(solutionsta),_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,ctypes.cast(xc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(xx.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(y.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(slc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(suc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(slx.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(sux.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(snx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsolution != 0:
      _,_msg_getsolution = self.__getlasterror(_res_getsolution)
      raise Error(rescode(_res_getsolution),_msg_getsolution)
    skc = list(map(lambda _i: stakey(_i),_tmparray_skc_))
    skx = list(map(lambda _i: stakey(_i),_tmparray_skx_))
    skn = list(map(lambda _i: stakey(_i),_tmparray_skn_))
    return (prosta(problemsta.value),solsta(solutionsta.value),skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx)
  def getsolution(self,*args,**kwds):
    """
    Obtains the complete solution.
  
    getsolution(skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx) -> (problemsta,solutionsta)
    getsolution() -> 
               (problemsta,
                solutionsta,
                skc,
                skx,
                skn,
                xc,
                xx,
                y,
                slc,
                suc,
                slx,
                sux,
                snx)
      [problemsta : mosek.prosta]  Problem status.  
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
      [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
      [solutionsta : mosek.solsta]  Solution status.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
      [xc : array(float64)]  Primal constraint solution.  
      [xx : array(float64)]  Primal variable solution.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 13: return self.__getsolution_13(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsolution_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsolutionnew_14(self,whichsol : soltype,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty):
    problemsta = ctypes.c_int()
    solutionsta = ctypes.c_int()
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_346 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_346))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(skc) < __tmp_346.value:
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))()
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_350 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_350))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(skx) < __tmp_350.value:
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))()
    if skn is None:
      _tmparray_skn_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_354 = ctypes.c_int32()
      _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_354))
      if _res_getnumcone != 0:
        _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
        raise Error(rescode(_res_getnumcone),_msg_getnumcone)
      if len(skn) < __tmp_354.value:
        raise ValueError("argument skn is too short")
      _tmparray_skn_ = (ctypes.c_int32*len(skn))()
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      __tmp_358 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_358))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(xc) < int(__tmp_358.value):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      __tmp_362 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_362))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(xx) < int(__tmp_362.value):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      __tmp_366 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_366))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(y) < int(__tmp_366.value):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      __tmp_370 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_370))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(slc) < int(__tmp_370.value):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      __tmp_374 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_374))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(suc) < int(__tmp_374.value):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      __tmp_378 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_378))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(slx) < int(__tmp_378.value):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      __tmp_382 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_382))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(sux) < int(__tmp_382.value):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      __tmp_386 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_386))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(snx) < int(__tmp_386.value):
        raise ValueError("argument snx is too short")
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    copyback_doty = False
    if doty is None:
      doty_ = None
      _tmparray_doty_ = None
    else:
      __tmp_390 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_390))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(doty) < int(__tmp_390.value):
        raise ValueError("argument doty is too short")
      _tmparray_doty_ = (ctypes.c_double*len(doty))(*doty)
    _res_getsolutionnew = __library__.MSK_getsolutionnew(self.__nativep,whichsol,ctypes.byref(problemsta),ctypes.byref(solutionsta),_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,_tmparray_xc_,_tmparray_xx_,_tmparray_y_,_tmparray_slc_,_tmparray_suc_,_tmparray_slx_,_tmparray_sux_,_tmparray_snx_,_tmparray_doty_)
    if _res_getsolutionnew != 0:
      _,_msg_getsolutionnew = self.__getlasterror(_res_getsolutionnew)
      raise Error(rescode(_res_getsolutionnew),_msg_getsolutionnew)
    if skc is not None:
      for __tmp_348,__tmp_349 in enumerate(_tmparray_skc_):
        skc[__tmp_348] = stakey(__tmp_349)
    if skx is not None:
      for __tmp_352,__tmp_353 in enumerate(_tmparray_skx_):
        skx[__tmp_352] = stakey(__tmp_353)
    if skn is not None:
      for __tmp_356,__tmp_357 in enumerate(_tmparray_skn_):
        skn[__tmp_356] = stakey(__tmp_357)
    if xc is not None:
      for __tmp_360,__tmp_361 in enumerate(_tmparray_xc_):
        xc[__tmp_360] = __tmp_361
    if xx is not None:
      for __tmp_364,__tmp_365 in enumerate(_tmparray_xx_):
        xx[__tmp_364] = __tmp_365
    if y is not None:
      for __tmp_368,__tmp_369 in enumerate(_tmparray_y_):
        y[__tmp_368] = __tmp_369
    if slc is not None:
      for __tmp_372,__tmp_373 in enumerate(_tmparray_slc_):
        slc[__tmp_372] = __tmp_373
    if suc is not None:
      for __tmp_376,__tmp_377 in enumerate(_tmparray_suc_):
        suc[__tmp_376] = __tmp_377
    if slx is not None:
      for __tmp_380,__tmp_381 in enumerate(_tmparray_slx_):
        slx[__tmp_380] = __tmp_381
    if sux is not None:
      for __tmp_384,__tmp_385 in enumerate(_tmparray_sux_):
        sux[__tmp_384] = __tmp_385
    if snx is not None:
      for __tmp_388,__tmp_389 in enumerate(_tmparray_snx_):
        snx[__tmp_388] = __tmp_389
    if doty is not None:
      for __tmp_392,__tmp_393 in enumerate(_tmparray_doty_):
        doty[__tmp_392] = __tmp_393
    return (prosta(problemsta.value),solsta(solutionsta.value))
  def __getsolutionnew_2(self,whichsol : soltype):
    problemsta = ctypes.c_int()
    solutionsta = ctypes.c_int()
    __tmp_394 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_394))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    _tmparray_skc_ = (ctypes.c_int32*__tmp_394.value)()
    __tmp_396 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_396))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    _tmparray_skx_ = (ctypes.c_int32*__tmp_396.value)()
    __tmp_398 = ctypes.c_int32()
    _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_398))
    if _res_getnumcone != 0:
      _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
      raise Error(rescode(_res_getnumcone),_msg_getnumcone)
    _tmparray_skn_ = (ctypes.c_int32*__tmp_398.value)()
    __tmp_400 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_400))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    xc = numpy.zeros(__tmp_400.value,numpy.float64)
    __tmp_403 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_403))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    xx = numpy.zeros(__tmp_403.value,numpy.float64)
    __tmp_406 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_406))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    y = numpy.zeros(__tmp_406.value,numpy.float64)
    __tmp_409 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_409))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    slc = numpy.zeros(__tmp_409.value,numpy.float64)
    __tmp_412 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_412))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    suc = numpy.zeros(__tmp_412.value,numpy.float64)
    __tmp_415 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_415))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    slx = numpy.zeros(__tmp_415.value,numpy.float64)
    __tmp_418 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_418))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    sux = numpy.zeros(__tmp_418.value,numpy.float64)
    __tmp_421 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_421))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    snx = numpy.zeros(__tmp_421.value,numpy.float64)
    __tmp_424 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_424))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    doty = numpy.zeros(__tmp_424.value,numpy.float64)
    _res_getsolutionnew = __library__.MSK_getsolutionnew(self.__nativep,whichsol,ctypes.byref(problemsta),ctypes.byref(solutionsta),_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,ctypes.cast(xc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(xx.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(y.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(slc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(suc.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(slx.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(sux.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(snx.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(doty.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsolutionnew != 0:
      _,_msg_getsolutionnew = self.__getlasterror(_res_getsolutionnew)
      raise Error(rescode(_res_getsolutionnew),_msg_getsolutionnew)
    skc = list(map(lambda _i: stakey(_i),_tmparray_skc_))
    skx = list(map(lambda _i: stakey(_i),_tmparray_skx_))
    skn = list(map(lambda _i: stakey(_i),_tmparray_skn_))
    return (prosta(problemsta.value),solsta(solutionsta.value),skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty)
  def getsolutionnew(self,*args,**kwds):
    """
    Obtains the complete solution.
  
    getsolutionnew(skc,
                   skx,
                   skn,
                   xc,
                   xx,
                   y,
                   slc,
                   suc,
                   slx,
                   sux,
                   snx,
                   doty) -> (problemsta,solutionsta)
    getsolutionnew() -> 
                  (problemsta,
                   solutionsta,
                   skc,
                   skx,
                   skn,
                   xc,
                   xx,
                   y,
                   slc,
                   suc,
                   slx,
                   sux,
                   snx,
                   doty)
      [doty : array(float64)]  Dual variables corresponding to affine conic constraints.  
      [problemsta : mosek.prosta]  Problem status.  
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
      [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
      [solutionsta : mosek.solsta]  Solution status.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
      [xc : array(float64)]  Primal constraint solution.  
      [xx : array(float64)]  Primal variable solution.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 14: return self.__getsolutionnew_14(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsolutionnew_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsolsta_2(self,whichsol : soltype):
    solutionsta = ctypes.c_int()
    _res_getsolsta = __library__.MSK_getsolsta(self.__nativep,whichsol,ctypes.byref(solutionsta))
    if _res_getsolsta != 0:
      _,_msg_getsolsta = self.__getlasterror(_res_getsolsta)
      raise Error(rescode(_res_getsolsta),_msg_getsolsta)
    return (solsta(solutionsta.value))
  def getsolsta(self,*args,**kwds):
    """
    Obtains the solution status.
  
    getsolsta() -> (solutionsta)
      [solutionsta : mosek.solsta]  Solution status.  
    """
    return self.__getsolsta_2(*args,**kwds)
  def __getprosta_2(self,whichsol : soltype):
    problemsta = ctypes.c_int()
    _res_getprosta = __library__.MSK_getprosta(self.__nativep,whichsol,ctypes.byref(problemsta))
    if _res_getprosta != 0:
      _,_msg_getprosta = self.__getlasterror(_res_getprosta)
      raise Error(rescode(_res_getprosta),_msg_getprosta)
    return (prosta(problemsta.value))
  def getprosta(self,*args,**kwds):
    """
    Obtains the problem status.
  
    getprosta() -> (problemsta)
      [problemsta : mosek.prosta]  Problem status.  
    """
    return self.__getprosta_2(*args,**kwds)
  def __getskc_3(self,whichsol : soltype,skc):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_427 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_427))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(skc) < __tmp_427.value:
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))()
    _res_getskc = __library__.MSK_getskc(self.__nativep,whichsol,_tmparray_skc_)
    if _res_getskc != 0:
      _,_msg_getskc = self.__getlasterror(_res_getskc)
      raise Error(rescode(_res_getskc),_msg_getskc)
    if skc is not None:
      for __tmp_429,__tmp_430 in enumerate(_tmparray_skc_):
        skc[__tmp_429] = stakey(__tmp_430)
  def __getskc_2(self,whichsol : soltype):
    __tmp_431 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_431))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    _tmparray_skc_ = (ctypes.c_int32*__tmp_431.value)()
    _res_getskc = __library__.MSK_getskc(self.__nativep,whichsol,_tmparray_skc_)
    if _res_getskc != 0:
      _,_msg_getskc = self.__getlasterror(_res_getskc)
      raise Error(rescode(_res_getskc),_msg_getskc)
    skc = list(map(lambda _i: stakey(_i),_tmparray_skc_))
    return (skc)
  def getskc(self,*args,**kwds):
    """
    Obtains the status keys for the constraints.
  
    getskc(skc)
    getskc() -> (skc)
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getskc_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getskc_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getskx_3(self,whichsol : soltype,skx):
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_433 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_433))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(skx) < __tmp_433.value:
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))()
    _res_getskx = __library__.MSK_getskx(self.__nativep,whichsol,_tmparray_skx_)
    if _res_getskx != 0:
      _,_msg_getskx = self.__getlasterror(_res_getskx)
      raise Error(rescode(_res_getskx),_msg_getskx)
    if skx is not None:
      for __tmp_435,__tmp_436 in enumerate(_tmparray_skx_):
        skx[__tmp_435] = stakey(__tmp_436)
  def __getskx_2(self,whichsol : soltype):
    __tmp_437 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_437))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    _tmparray_skx_ = (ctypes.c_int32*__tmp_437.value)()
    _res_getskx = __library__.MSK_getskx(self.__nativep,whichsol,_tmparray_skx_)
    if _res_getskx != 0:
      _,_msg_getskx = self.__getlasterror(_res_getskx)
      raise Error(rescode(_res_getskx),_msg_getskx)
    skx = list(map(lambda _i: stakey(_i),_tmparray_skx_))
    return (skx)
  def getskx(self,*args,**kwds):
    """
    Obtains the status keys for the scalar variables.
  
    getskx(skx)
    getskx() -> (skx)
      [skx : array(mosek.stakey)]  Status keys for the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getskx_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getskx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getskn_3(self,whichsol : soltype,skn):
    if skn is None:
      _tmparray_skn_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_439 = ctypes.c_int32()
      _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_439))
      if _res_getnumcone != 0:
        _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
        raise Error(rescode(_res_getnumcone),_msg_getnumcone)
      if len(skn) < __tmp_439.value:
        raise ValueError("argument skn is too short")
      _tmparray_skn_ = (ctypes.c_int32*len(skn))()
    _res_getskn = __library__.MSK_getskn(self.__nativep,whichsol,_tmparray_skn_)
    if _res_getskn != 0:
      _,_msg_getskn = self.__getlasterror(_res_getskn)
      raise Error(rescode(_res_getskn),_msg_getskn)
    if skn is not None:
      for __tmp_441,__tmp_442 in enumerate(_tmparray_skn_):
        skn[__tmp_441] = stakey(__tmp_442)
  def __getskn_2(self,whichsol : soltype):
    __tmp_443 = ctypes.c_int32()
    _res_getnumcone = __library__.MSK_getnumcone(self.__nativep,ctypes.byref(__tmp_443))
    if _res_getnumcone != 0:
      _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
      raise Error(rescode(_res_getnumcone),_msg_getnumcone)
    _tmparray_skn_ = (ctypes.c_int32*__tmp_443.value)()
    _res_getskn = __library__.MSK_getskn(self.__nativep,whichsol,_tmparray_skn_)
    if _res_getskn != 0:
      _,_msg_getskn = self.__getlasterror(_res_getskn)
      raise Error(rescode(_res_getskn),_msg_getskn)
    skn = list(map(lambda _i: stakey(_i),_tmparray_skn_))
    return (skn)
  def getskn(self,*args,**kwds):
    """
    Obtains the status keys for the conic constraints.
  
    getskn(skn)
    getskn() -> (skn)
      [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getskn_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getskn_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getxc_3(self,whichsol : soltype,xc):
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      __tmp_445 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_445))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(xc) < int(__tmp_445.value):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    _res_getxc = __library__.MSK_getxc(self.__nativep,whichsol,_tmparray_xc_)
    if _res_getxc != 0:
      _,_msg_getxc = self.__getlasterror(_res_getxc)
      raise Error(rescode(_res_getxc),_msg_getxc)
    if xc is not None:
      for __tmp_447,__tmp_448 in enumerate(_tmparray_xc_):
        xc[__tmp_447] = __tmp_448
  def __getxc_2(self,whichsol : soltype):
    __tmp_449 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_449))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    xc = numpy.zeros(__tmp_449.value,numpy.float64)
    _res_getxc = __library__.MSK_getxc(self.__nativep,whichsol,ctypes.cast(xc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getxc != 0:
      _,_msg_getxc = self.__getlasterror(_res_getxc)
      raise Error(rescode(_res_getxc),_msg_getxc)
    return (xc)
  def getxc(self,*args,**kwds):
    """
    Obtains the xc vector for a solution.
  
    getxc(xc)
    getxc() -> (xc)
      [xc : array(float64)]  Primal constraint solution.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getxc_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getxc_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getxx_3(self,whichsol : soltype,xx):
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      __tmp_452 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_452))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(xx) < int(__tmp_452.value):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    _res_getxx = __library__.MSK_getxx(self.__nativep,whichsol,_tmparray_xx_)
    if _res_getxx != 0:
      _,_msg_getxx = self.__getlasterror(_res_getxx)
      raise Error(rescode(_res_getxx),_msg_getxx)
    if xx is not None:
      for __tmp_454,__tmp_455 in enumerate(_tmparray_xx_):
        xx[__tmp_454] = __tmp_455
  def __getxx_2(self,whichsol : soltype):
    __tmp_456 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_456))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    xx = numpy.zeros(__tmp_456.value,numpy.float64)
    _res_getxx = __library__.MSK_getxx(self.__nativep,whichsol,ctypes.cast(xx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getxx != 0:
      _,_msg_getxx = self.__getlasterror(_res_getxx)
      raise Error(rescode(_res_getxx),_msg_getxx)
    return (xx)
  def getxx(self,*args,**kwds):
    """
    Obtains the xx vector for a solution.
  
    getxx(xx)
    getxx() -> (xx)
      [xx : array(float64)]  Primal variable solution.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getxx_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getxx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __gety_3(self,whichsol : soltype,y):
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      __tmp_459 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_459))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(y) < int(__tmp_459.value):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_gety = __library__.MSK_gety(self.__nativep,whichsol,_tmparray_y_)
    if _res_gety != 0:
      _,_msg_gety = self.__getlasterror(_res_gety)
      raise Error(rescode(_res_gety),_msg_gety)
    if y is not None:
      for __tmp_461,__tmp_462 in enumerate(_tmparray_y_):
        y[__tmp_461] = __tmp_462
  def __gety_2(self,whichsol : soltype):
    __tmp_463 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_463))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    y = numpy.zeros(__tmp_463.value,numpy.float64)
    _res_gety = __library__.MSK_gety(self.__nativep,whichsol,ctypes.cast(y.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_gety != 0:
      _,_msg_gety = self.__getlasterror(_res_gety)
      raise Error(rescode(_res_gety),_msg_gety)
    return (y)
  def gety(self,*args,**kwds):
    """
    Obtains the y vector for a solution.
  
    gety(y)
    gety() -> (y)
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__gety_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__gety_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getslc_3(self,whichsol : soltype,slc):
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      __tmp_466 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_466))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(slc) < int(__tmp_466.value):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    _res_getslc = __library__.MSK_getslc(self.__nativep,whichsol,_tmparray_slc_)
    if _res_getslc != 0:
      _,_msg_getslc = self.__getlasterror(_res_getslc)
      raise Error(rescode(_res_getslc),_msg_getslc)
    if slc is not None:
      for __tmp_468,__tmp_469 in enumerate(_tmparray_slc_):
        slc[__tmp_468] = __tmp_469
  def __getslc_2(self,whichsol : soltype):
    __tmp_470 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_470))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    slc = numpy.zeros(__tmp_470.value,numpy.float64)
    _res_getslc = __library__.MSK_getslc(self.__nativep,whichsol,ctypes.cast(slc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getslc != 0:
      _,_msg_getslc = self.__getlasterror(_res_getslc)
      raise Error(rescode(_res_getslc),_msg_getslc)
    return (slc)
  def getslc(self,*args,**kwds):
    """
    Obtains the slc vector for a solution.
  
    getslc(slc)
    getslc() -> (slc)
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getslc_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getslc_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccdoty_4(self,whichsol : soltype,accidx,doty):
    copyback_doty = False
    if doty is None:
      doty_ = None
      _tmparray_doty_ = None
    else:
      __tmp_473 = ctypes.c_int64()
      _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_473))
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      if len(doty) < int(__tmp_473.value):
        raise ValueError("argument doty is too short")
      _tmparray_doty_ = (ctypes.c_double*len(doty))(*doty)
    _res_getaccdoty = __library__.MSK_getaccdoty(self.__nativep,whichsol,accidx,_tmparray_doty_)
    if _res_getaccdoty != 0:
      _,_msg_getaccdoty = self.__getlasterror(_res_getaccdoty)
      raise Error(rescode(_res_getaccdoty),_msg_getaccdoty)
    if doty is not None:
      for __tmp_475,__tmp_476 in enumerate(_tmparray_doty_):
        doty[__tmp_475] = __tmp_476
  def __getaccdoty_3(self,whichsol : soltype,accidx):
    __tmp_477 = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_477))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    doty = numpy.zeros(__tmp_477.value,numpy.float64)
    _res_getaccdoty = __library__.MSK_getaccdoty(self.__nativep,whichsol,accidx,ctypes.cast(doty.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccdoty != 0:
      _,_msg_getaccdoty = self.__getlasterror(_res_getaccdoty)
      raise Error(rescode(_res_getaccdoty),_msg_getaccdoty)
    return (doty)
  def getaccdoty(self,*args,**kwds):
    """
    Obtains the doty vector for an affine conic constraint.
  
    getaccdoty(accidx,doty)
    getaccdoty(accidx) -> (doty)
      [accidx : int64]  The index of the affine conic constraint.  
      [doty : array(float64)]  The dual values for this affine conic constraint. The array should have length equal to the dimension of the constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getaccdoty_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getaccdoty_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccdotys_3(self,whichsol : soltype,doty):
    copyback_doty = False
    if doty is None:
      doty_ = None
      _tmparray_doty_ = None
    else:
      __tmp_480 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_480))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(doty) < int(__tmp_480.value):
        raise ValueError("argument doty is too short")
      _tmparray_doty_ = (ctypes.c_double*len(doty))(*doty)
    _res_getaccdotys = __library__.MSK_getaccdotys(self.__nativep,whichsol,_tmparray_doty_)
    if _res_getaccdotys != 0:
      _,_msg_getaccdotys = self.__getlasterror(_res_getaccdotys)
      raise Error(rescode(_res_getaccdotys),_msg_getaccdotys)
    if doty is not None:
      for __tmp_482,__tmp_483 in enumerate(_tmparray_doty_):
        doty[__tmp_482] = __tmp_483
  def __getaccdotys_2(self,whichsol : soltype):
    __tmp_484 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_484))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    doty = numpy.zeros(__tmp_484.value,numpy.float64)
    _res_getaccdotys = __library__.MSK_getaccdotys(self.__nativep,whichsol,ctypes.cast(doty.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccdotys != 0:
      _,_msg_getaccdotys = self.__getlasterror(_res_getaccdotys)
      raise Error(rescode(_res_getaccdotys),_msg_getaccdotys)
    return (doty)
  def getaccdotys(self,*args,**kwds):
    """
    Obtains the doty vector for a solution.
  
    getaccdotys(doty)
    getaccdotys() -> (doty)
      [doty : array(float64)]  The dual values of affine conic constraints. The array should have length equal to the sum of dimensions of all affine conic constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getaccdotys_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getaccdotys_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __evaluateacc_4(self,whichsol : soltype,accidx,activity):
    copyback_activity = False
    if activity is None:
      activity_ = None
      _tmparray_activity_ = None
    else:
      __tmp_487 = ctypes.c_int64()
      _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_487))
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      if len(activity) < int(__tmp_487.value):
        raise ValueError("argument activity is too short")
      _tmparray_activity_ = (ctypes.c_double*len(activity))(*activity)
    _res_evaluateacc = __library__.MSK_evaluateacc(self.__nativep,whichsol,accidx,_tmparray_activity_)
    if _res_evaluateacc != 0:
      _,_msg_evaluateacc = self.__getlasterror(_res_evaluateacc)
      raise Error(rescode(_res_evaluateacc),_msg_evaluateacc)
    if activity is not None:
      for __tmp_489,__tmp_490 in enumerate(_tmparray_activity_):
        activity[__tmp_489] = __tmp_490
  def __evaluateacc_3(self,whichsol : soltype,accidx):
    __tmp_491 = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_491))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    activity = numpy.zeros(__tmp_491.value,numpy.float64)
    _res_evaluateacc = __library__.MSK_evaluateacc(self.__nativep,whichsol,accidx,ctypes.cast(activity.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_evaluateacc != 0:
      _,_msg_evaluateacc = self.__getlasterror(_res_evaluateacc)
      raise Error(rescode(_res_evaluateacc),_msg_evaluateacc)
    return (activity)
  def evaluateacc(self,*args,**kwds):
    """
    Evaluates the activity of an affine conic constraint.
  
    evaluateacc(accidx,activity)
    evaluateacc(accidx) -> (activity)
      [accidx : int64]  The index of the affine conic constraint.  
      [activity : array(float64)]  The activity of the affine conic constraint. The array should have length equal to the dimension of the constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__evaluateacc_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__evaluateacc_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __evaluateaccs_3(self,whichsol : soltype,activity):
    copyback_activity = False
    if activity is None:
      activity_ = None
      _tmparray_activity_ = None
    else:
      __tmp_494 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_494))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(activity) < int(__tmp_494.value):
        raise ValueError("argument activity is too short")
      _tmparray_activity_ = (ctypes.c_double*len(activity))(*activity)
    _res_evaluateaccs = __library__.MSK_evaluateaccs(self.__nativep,whichsol,_tmparray_activity_)
    if _res_evaluateaccs != 0:
      _,_msg_evaluateaccs = self.__getlasterror(_res_evaluateaccs)
      raise Error(rescode(_res_evaluateaccs),_msg_evaluateaccs)
    if activity is not None:
      for __tmp_496,__tmp_497 in enumerate(_tmparray_activity_):
        activity[__tmp_496] = __tmp_497
  def __evaluateaccs_2(self,whichsol : soltype):
    __tmp_498 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_498))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    activity = numpy.zeros(__tmp_498.value,numpy.float64)
    _res_evaluateaccs = __library__.MSK_evaluateaccs(self.__nativep,whichsol,ctypes.cast(activity.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_evaluateaccs != 0:
      _,_msg_evaluateaccs = self.__getlasterror(_res_evaluateaccs)
      raise Error(rescode(_res_evaluateaccs),_msg_evaluateaccs)
    return (activity)
  def evaluateaccs(self,*args,**kwds):
    """
    Evaluates the activities of all affine conic constraints.
  
    evaluateaccs(activity)
    evaluateaccs() -> (activity)
      [activity : array(float64)]  The activity of affine conic constraints. The array should have length equal to the sum of dimensions of all affine conic constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__evaluateaccs_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__evaluateaccs_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsuc_3(self,whichsol : soltype,suc):
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      __tmp_501 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_501))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(suc) < int(__tmp_501.value):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    _res_getsuc = __library__.MSK_getsuc(self.__nativep,whichsol,_tmparray_suc_)
    if _res_getsuc != 0:
      _,_msg_getsuc = self.__getlasterror(_res_getsuc)
      raise Error(rescode(_res_getsuc),_msg_getsuc)
    if suc is not None:
      for __tmp_503,__tmp_504 in enumerate(_tmparray_suc_):
        suc[__tmp_503] = __tmp_504
  def __getsuc_2(self,whichsol : soltype):
    __tmp_505 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_505))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    suc = numpy.zeros(__tmp_505.value,numpy.float64)
    _res_getsuc = __library__.MSK_getsuc(self.__nativep,whichsol,ctypes.cast(suc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsuc != 0:
      _,_msg_getsuc = self.__getlasterror(_res_getsuc)
      raise Error(rescode(_res_getsuc),_msg_getsuc)
    return (suc)
  def getsuc(self,*args,**kwds):
    """
    Obtains the suc vector for a solution.
  
    getsuc(suc)
    getsuc() -> (suc)
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getsuc_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsuc_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getslx_3(self,whichsol : soltype,slx):
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      __tmp_508 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_508))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(slx) < int(__tmp_508.value):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    _res_getslx = __library__.MSK_getslx(self.__nativep,whichsol,_tmparray_slx_)
    if _res_getslx != 0:
      _,_msg_getslx = self.__getlasterror(_res_getslx)
      raise Error(rescode(_res_getslx),_msg_getslx)
    if slx is not None:
      for __tmp_510,__tmp_511 in enumerate(_tmparray_slx_):
        slx[__tmp_510] = __tmp_511
  def __getslx_2(self,whichsol : soltype):
    __tmp_512 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_512))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    slx = numpy.zeros(__tmp_512.value,numpy.float64)
    _res_getslx = __library__.MSK_getslx(self.__nativep,whichsol,ctypes.cast(slx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getslx != 0:
      _,_msg_getslx = self.__getlasterror(_res_getslx)
      raise Error(rescode(_res_getslx),_msg_getslx)
    return (slx)
  def getslx(self,*args,**kwds):
    """
    Obtains the slx vector for a solution.
  
    getslx(slx)
    getslx() -> (slx)
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getslx_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getslx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsux_3(self,whichsol : soltype,sux):
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      __tmp_515 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_515))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(sux) < int(__tmp_515.value):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    _res_getsux = __library__.MSK_getsux(self.__nativep,whichsol,_tmparray_sux_)
    if _res_getsux != 0:
      _,_msg_getsux = self.__getlasterror(_res_getsux)
      raise Error(rescode(_res_getsux),_msg_getsux)
    if sux is not None:
      for __tmp_517,__tmp_518 in enumerate(_tmparray_sux_):
        sux[__tmp_517] = __tmp_518
  def __getsux_2(self,whichsol : soltype):
    __tmp_519 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_519))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    sux = numpy.zeros(__tmp_519.value,numpy.float64)
    _res_getsux = __library__.MSK_getsux(self.__nativep,whichsol,ctypes.cast(sux.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsux != 0:
      _,_msg_getsux = self.__getlasterror(_res_getsux)
      raise Error(rescode(_res_getsux),_msg_getsux)
    return (sux)
  def getsux(self,*args,**kwds):
    """
    Obtains the sux vector for a solution.
  
    getsux(sux)
    getsux() -> (sux)
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getsux_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsux_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsnx_3(self,whichsol : soltype,snx):
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      __tmp_522 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_522))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(snx) < int(__tmp_522.value):
        raise ValueError("argument snx is too short")
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    _res_getsnx = __library__.MSK_getsnx(self.__nativep,whichsol,_tmparray_snx_)
    if _res_getsnx != 0:
      _,_msg_getsnx = self.__getlasterror(_res_getsnx)
      raise Error(rescode(_res_getsnx),_msg_getsnx)
    if snx is not None:
      for __tmp_524,__tmp_525 in enumerate(_tmparray_snx_):
        snx[__tmp_524] = __tmp_525
  def __getsnx_2(self,whichsol : soltype):
    __tmp_526 = ctypes.c_int32()
    _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_526))
    if _res_getnumvar != 0:
      _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
      raise Error(rescode(_res_getnumvar),_msg_getnumvar)
    snx = numpy.zeros(__tmp_526.value,numpy.float64)
    _res_getsnx = __library__.MSK_getsnx(self.__nativep,whichsol,ctypes.cast(snx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsnx != 0:
      _,_msg_getsnx = self.__getlasterror(_res_getsnx)
      raise Error(rescode(_res_getsnx),_msg_getsnx)
    return (snx)
  def getsnx(self,*args,**kwds):
    """
    Obtains the snx vector for a solution.
  
    getsnx(snx)
    getsnx() -> (snx)
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getsnx_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsnx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getskcslice_5(self,whichsol : soltype,first,last,skc):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(skc) < (last - first):
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))()
    _res_getskcslice = __library__.MSK_getskcslice(self.__nativep,whichsol,first,last,_tmparray_skc_)
    if _res_getskcslice != 0:
      _,_msg_getskcslice = self.__getlasterror(_res_getskcslice)
      raise Error(rescode(_res_getskcslice),_msg_getskcslice)
    if skc is not None:
      for __tmp_529,__tmp_530 in enumerate(_tmparray_skc_):
        skc[__tmp_529] = stakey(__tmp_530)
  def __getskcslice_4(self,whichsol : soltype,first,last):
    _tmparray_skc_ = (ctypes.c_int32*(last - first))()
    _res_getskcslice = __library__.MSK_getskcslice(self.__nativep,whichsol,first,last,_tmparray_skc_)
    if _res_getskcslice != 0:
      _,_msg_getskcslice = self.__getlasterror(_res_getskcslice)
      raise Error(rescode(_res_getskcslice),_msg_getskcslice)
    skc = list(map(lambda _i: stakey(_i),_tmparray_skc_))
    return (skc)
  def getskcslice(self,*args,**kwds):
    """
    Obtains the status keys for a slice of the constraints.
  
    getskcslice(first,last,skc)
    getskcslice(first,last) -> (skc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getskcslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getskcslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getskxslice_5(self,whichsol : soltype,first,last,skx):
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(skx) < (last - first):
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))()
    _res_getskxslice = __library__.MSK_getskxslice(self.__nativep,whichsol,first,last,_tmparray_skx_)
    if _res_getskxslice != 0:
      _,_msg_getskxslice = self.__getlasterror(_res_getskxslice)
      raise Error(rescode(_res_getskxslice),_msg_getskxslice)
    if skx is not None:
      for __tmp_531,__tmp_532 in enumerate(_tmparray_skx_):
        skx[__tmp_531] = stakey(__tmp_532)
  def __getskxslice_4(self,whichsol : soltype,first,last):
    _tmparray_skx_ = (ctypes.c_int32*(last - first))()
    _res_getskxslice = __library__.MSK_getskxslice(self.__nativep,whichsol,first,last,_tmparray_skx_)
    if _res_getskxslice != 0:
      _,_msg_getskxslice = self.__getlasterror(_res_getskxslice)
      raise Error(rescode(_res_getskxslice),_msg_getskxslice)
    skx = list(map(lambda _i: stakey(_i),_tmparray_skx_))
    return (skx)
  def getskxslice(self,*args,**kwds):
    """
    Obtains the status keys for a slice of the scalar variables.
  
    getskxslice(first,last,skx)
    getskxslice(first,last) -> (skx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getskxslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getskxslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getxcslice_5(self,whichsol : soltype,first,last,xc):
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      if len(xc) < int((last - first)):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    _res_getxcslice = __library__.MSK_getxcslice(self.__nativep,whichsol,first,last,_tmparray_xc_)
    if _res_getxcslice != 0:
      _,_msg_getxcslice = self.__getlasterror(_res_getxcslice)
      raise Error(rescode(_res_getxcslice),_msg_getxcslice)
    if xc is not None:
      for __tmp_533,__tmp_534 in enumerate(_tmparray_xc_):
        xc[__tmp_533] = __tmp_534
  def __getxcslice_4(self,whichsol : soltype,first,last):
    xc = numpy.zeros((last - first),numpy.float64)
    _res_getxcslice = __library__.MSK_getxcslice(self.__nativep,whichsol,first,last,ctypes.cast(xc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getxcslice != 0:
      _,_msg_getxcslice = self.__getlasterror(_res_getxcslice)
      raise Error(rescode(_res_getxcslice),_msg_getxcslice)
    return (xc)
  def getxcslice(self,*args,**kwds):
    """
    Obtains a slice of the xc vector for a solution.
  
    getxcslice(first,last,xc)
    getxcslice(first,last) -> (xc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [xc : array(float64)]  Primal constraint solution.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getxcslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getxcslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getxxslice_5(self,whichsol : soltype,first,last,xx):
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      if len(xx) < int((last - first)):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    _res_getxxslice = __library__.MSK_getxxslice(self.__nativep,whichsol,first,last,_tmparray_xx_)
    if _res_getxxslice != 0:
      _,_msg_getxxslice = self.__getlasterror(_res_getxxslice)
      raise Error(rescode(_res_getxxslice),_msg_getxxslice)
    if xx is not None:
      for __tmp_536,__tmp_537 in enumerate(_tmparray_xx_):
        xx[__tmp_536] = __tmp_537
  def __getxxslice_4(self,whichsol : soltype,first,last):
    xx = numpy.zeros((last - first),numpy.float64)
    _res_getxxslice = __library__.MSK_getxxslice(self.__nativep,whichsol,first,last,ctypes.cast(xx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getxxslice != 0:
      _,_msg_getxxslice = self.__getlasterror(_res_getxxslice)
      raise Error(rescode(_res_getxxslice),_msg_getxxslice)
    return (xx)
  def getxxslice(self,*args,**kwds):
    """
    Obtains a slice of the xx vector for a solution.
  
    getxxslice(first,last,xx)
    getxxslice(first,last) -> (xx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [xx : array(float64)]  Primal variable solution.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getxxslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getxxslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getyslice_5(self,whichsol : soltype,first,last,y):
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      if len(y) < int((last - first)):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_getyslice = __library__.MSK_getyslice(self.__nativep,whichsol,first,last,_tmparray_y_)
    if _res_getyslice != 0:
      _,_msg_getyslice = self.__getlasterror(_res_getyslice)
      raise Error(rescode(_res_getyslice),_msg_getyslice)
    if y is not None:
      for __tmp_539,__tmp_540 in enumerate(_tmparray_y_):
        y[__tmp_539] = __tmp_540
  def __getyslice_4(self,whichsol : soltype,first,last):
    y = numpy.zeros((last - first),numpy.float64)
    _res_getyslice = __library__.MSK_getyslice(self.__nativep,whichsol,first,last,ctypes.cast(y.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getyslice != 0:
      _,_msg_getyslice = self.__getlasterror(_res_getyslice)
      raise Error(rescode(_res_getyslice),_msg_getyslice)
    return (y)
  def getyslice(self,*args,**kwds):
    """
    Obtains a slice of the y vector for a solution.
  
    getyslice(first,last,y)
    getyslice(first,last) -> (y)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getyslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getyslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getslcslice_5(self,whichsol : soltype,first,last,slc):
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      if len(slc) < int((last - first)):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    _res_getslcslice = __library__.MSK_getslcslice(self.__nativep,whichsol,first,last,_tmparray_slc_)
    if _res_getslcslice != 0:
      _,_msg_getslcslice = self.__getlasterror(_res_getslcslice)
      raise Error(rescode(_res_getslcslice),_msg_getslcslice)
    if slc is not None:
      for __tmp_542,__tmp_543 in enumerate(_tmparray_slc_):
        slc[__tmp_542] = __tmp_543
  def __getslcslice_4(self,whichsol : soltype,first,last):
    slc = numpy.zeros((last - first),numpy.float64)
    _res_getslcslice = __library__.MSK_getslcslice(self.__nativep,whichsol,first,last,ctypes.cast(slc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getslcslice != 0:
      _,_msg_getslcslice = self.__getlasterror(_res_getslcslice)
      raise Error(rescode(_res_getslcslice),_msg_getslcslice)
    return (slc)
  def getslcslice(self,*args,**kwds):
    """
    Obtains a slice of the slc vector for a solution.
  
    getslcslice(first,last,slc)
    getslcslice(first,last) -> (slc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getslcslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getslcslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsucslice_5(self,whichsol : soltype,first,last,suc):
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      if len(suc) < int((last - first)):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    _res_getsucslice = __library__.MSK_getsucslice(self.__nativep,whichsol,first,last,_tmparray_suc_)
    if _res_getsucslice != 0:
      _,_msg_getsucslice = self.__getlasterror(_res_getsucslice)
      raise Error(rescode(_res_getsucslice),_msg_getsucslice)
    if suc is not None:
      for __tmp_545,__tmp_546 in enumerate(_tmparray_suc_):
        suc[__tmp_545] = __tmp_546
  def __getsucslice_4(self,whichsol : soltype,first,last):
    suc = numpy.zeros((last - first),numpy.float64)
    _res_getsucslice = __library__.MSK_getsucslice(self.__nativep,whichsol,first,last,ctypes.cast(suc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsucslice != 0:
      _,_msg_getsucslice = self.__getlasterror(_res_getsucslice)
      raise Error(rescode(_res_getsucslice),_msg_getsucslice)
    return (suc)
  def getsucslice(self,*args,**kwds):
    """
    Obtains a slice of the suc vector for a solution.
  
    getsucslice(first,last,suc)
    getsucslice(first,last) -> (suc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getsucslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getsucslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getslxslice_5(self,whichsol : soltype,first,last,slx):
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      if len(slx) < int((last - first)):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    _res_getslxslice = __library__.MSK_getslxslice(self.__nativep,whichsol,first,last,_tmparray_slx_)
    if _res_getslxslice != 0:
      _,_msg_getslxslice = self.__getlasterror(_res_getslxslice)
      raise Error(rescode(_res_getslxslice),_msg_getslxslice)
    if slx is not None:
      for __tmp_548,__tmp_549 in enumerate(_tmparray_slx_):
        slx[__tmp_548] = __tmp_549
  def __getslxslice_4(self,whichsol : soltype,first,last):
    slx = numpy.zeros((last - first),numpy.float64)
    _res_getslxslice = __library__.MSK_getslxslice(self.__nativep,whichsol,first,last,ctypes.cast(slx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getslxslice != 0:
      _,_msg_getslxslice = self.__getlasterror(_res_getslxslice)
      raise Error(rescode(_res_getslxslice),_msg_getslxslice)
    return (slx)
  def getslxslice(self,*args,**kwds):
    """
    Obtains a slice of the slx vector for a solution.
  
    getslxslice(first,last,slx)
    getslxslice(first,last) -> (slx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getslxslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getslxslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsuxslice_5(self,whichsol : soltype,first,last,sux):
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      if len(sux) < int((last - first)):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    _res_getsuxslice = __library__.MSK_getsuxslice(self.__nativep,whichsol,first,last,_tmparray_sux_)
    if _res_getsuxslice != 0:
      _,_msg_getsuxslice = self.__getlasterror(_res_getsuxslice)
      raise Error(rescode(_res_getsuxslice),_msg_getsuxslice)
    if sux is not None:
      for __tmp_551,__tmp_552 in enumerate(_tmparray_sux_):
        sux[__tmp_551] = __tmp_552
  def __getsuxslice_4(self,whichsol : soltype,first,last):
    sux = numpy.zeros((last - first),numpy.float64)
    _res_getsuxslice = __library__.MSK_getsuxslice(self.__nativep,whichsol,first,last,ctypes.cast(sux.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsuxslice != 0:
      _,_msg_getsuxslice = self.__getlasterror(_res_getsuxslice)
      raise Error(rescode(_res_getsuxslice),_msg_getsuxslice)
    return (sux)
  def getsuxslice(self,*args,**kwds):
    """
    Obtains a slice of the sux vector for a solution.
  
    getsuxslice(first,last,sux)
    getsuxslice(first,last) -> (sux)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getsuxslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getsuxslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsnxslice_5(self,whichsol : soltype,first,last,snx):
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      if len(snx) < int((last - first)):
        raise ValueError("argument snx is too short")
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    _res_getsnxslice = __library__.MSK_getsnxslice(self.__nativep,whichsol,first,last,_tmparray_snx_)
    if _res_getsnxslice != 0:
      _,_msg_getsnxslice = self.__getlasterror(_res_getsnxslice)
      raise Error(rescode(_res_getsnxslice),_msg_getsnxslice)
    if snx is not None:
      for __tmp_554,__tmp_555 in enumerate(_tmparray_snx_):
        snx[__tmp_554] = __tmp_555
  def __getsnxslice_4(self,whichsol : soltype,first,last):
    snx = numpy.zeros((last - first),numpy.float64)
    _res_getsnxslice = __library__.MSK_getsnxslice(self.__nativep,whichsol,first,last,ctypes.cast(snx.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsnxslice != 0:
      _,_msg_getsnxslice = self.__getlasterror(_res_getsnxslice)
      raise Error(rescode(_res_getsnxslice),_msg_getsnxslice)
    return (snx)
  def getsnxslice(self,*args,**kwds):
    """
    Obtains a slice of the snx vector for a solution.
  
    getsnxslice(first,last,snx)
    getsnxslice(first,last) -> (snx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getsnxslice_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getsnxslice_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarxj_4(self,whichsol : soltype,j,barxj):
    copyback_barxj = False
    if barxj is None:
      barxj_ = None
      _tmparray_barxj_ = None
    else:
      __tmp_557 = ctypes.c_int64()
      _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_557))
      if _res_getlenbarvarj != 0:
        _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
        raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
      if len(barxj) < int(__tmp_557.value):
        raise ValueError("argument barxj is too short")
      _tmparray_barxj_ = (ctypes.c_double*len(barxj))(*barxj)
    _res_getbarxj = __library__.MSK_getbarxj(self.__nativep,whichsol,j,_tmparray_barxj_)
    if _res_getbarxj != 0:
      _,_msg_getbarxj = self.__getlasterror(_res_getbarxj)
      raise Error(rescode(_res_getbarxj),_msg_getbarxj)
    if barxj is not None:
      for __tmp_559,__tmp_560 in enumerate(_tmparray_barxj_):
        barxj[__tmp_559] = __tmp_560
  def __getbarxj_3(self,whichsol : soltype,j):
    __tmp_561 = ctypes.c_int64()
    _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_561))
    if _res_getlenbarvarj != 0:
      _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
      raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
    barxj = numpy.zeros(__tmp_561.value,numpy.float64)
    _res_getbarxj = __library__.MSK_getbarxj(self.__nativep,whichsol,j,ctypes.cast(barxj.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarxj != 0:
      _,_msg_getbarxj = self.__getlasterror(_res_getbarxj)
      raise Error(rescode(_res_getbarxj),_msg_getbarxj)
    return (barxj)
  def getbarxj(self,*args,**kwds):
    """
    Obtains the primal solution for a semidefinite variable.
  
    getbarxj(j,barxj)
    getbarxj(j) -> (barxj)
      [barxj : array(float64)]  Value of the j'th variable of barx.  
      [j : int32]  Index of the semidefinite variable.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getbarxj_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getbarxj_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarxslice_6(self,whichsol : soltype,first,last,slicesize,barxslice):
    copyback_barxslice = False
    if barxslice is None:
      barxslice_ = None
      _tmparray_barxslice_ = None
    else:
      if len(barxslice) < int(slicesize):
        raise ValueError("argument barxslice is too short")
      _tmparray_barxslice_ = (ctypes.c_double*len(barxslice))(*barxslice)
    _res_getbarxslice = __library__.MSK_getbarxslice(self.__nativep,whichsol,first,last,slicesize,_tmparray_barxslice_)
    if _res_getbarxslice != 0:
      _,_msg_getbarxslice = self.__getlasterror(_res_getbarxslice)
      raise Error(rescode(_res_getbarxslice),_msg_getbarxslice)
    if barxslice is not None:
      for __tmp_564,__tmp_565 in enumerate(_tmparray_barxslice_):
        barxslice[__tmp_564] = __tmp_565
  def __getbarxslice_5(self,whichsol : soltype,first,last,slicesize):
    barxslice = numpy.zeros(slicesize,numpy.float64)
    _res_getbarxslice = __library__.MSK_getbarxslice(self.__nativep,whichsol,first,last,slicesize,ctypes.cast(barxslice.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarxslice != 0:
      _,_msg_getbarxslice = self.__getlasterror(_res_getbarxslice)
      raise Error(rescode(_res_getbarxslice),_msg_getbarxslice)
    return (barxslice)
  def getbarxslice(self,*args,**kwds):
    """
    Obtains the primal solution for a sequence of semidefinite variables.
  
    getbarxslice(first,last,slicesize,barxslice)
    getbarxslice(first,last,slicesize) -> (barxslice)
      [barxslice : array(float64)]  Solution values of symmetric matrix variables in the slice, stored sequentially.  
      [first : int32]  Index of the first semidefinite variable in the slice.  
      [last : int32]  Index of the last semidefinite variable in the slice plus one.  
      [slicesize : int64]  Denotes the length of the array barxslice.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getbarxslice_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 5: return self.__getbarxslice_5(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarsj_4(self,whichsol : soltype,j,barsj):
    copyback_barsj = False
    if barsj is None:
      barsj_ = None
      _tmparray_barsj_ = None
    else:
      __tmp_567 = ctypes.c_int64()
      _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_567))
      if _res_getlenbarvarj != 0:
        _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
        raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
      if len(barsj) < int(__tmp_567.value):
        raise ValueError("argument barsj is too short")
      _tmparray_barsj_ = (ctypes.c_double*len(barsj))(*barsj)
    _res_getbarsj = __library__.MSK_getbarsj(self.__nativep,whichsol,j,_tmparray_barsj_)
    if _res_getbarsj != 0:
      _,_msg_getbarsj = self.__getlasterror(_res_getbarsj)
      raise Error(rescode(_res_getbarsj),_msg_getbarsj)
    if barsj is not None:
      for __tmp_569,__tmp_570 in enumerate(_tmparray_barsj_):
        barsj[__tmp_569] = __tmp_570
  def __getbarsj_3(self,whichsol : soltype,j):
    __tmp_571 = ctypes.c_int64()
    _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_571))
    if _res_getlenbarvarj != 0:
      _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
      raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
    barsj = numpy.zeros(__tmp_571.value,numpy.float64)
    _res_getbarsj = __library__.MSK_getbarsj(self.__nativep,whichsol,j,ctypes.cast(barsj.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarsj != 0:
      _,_msg_getbarsj = self.__getlasterror(_res_getbarsj)
      raise Error(rescode(_res_getbarsj),_msg_getbarsj)
    return (barsj)
  def getbarsj(self,*args,**kwds):
    """
    Obtains the dual solution for a semidefinite variable.
  
    getbarsj(j,barsj)
    getbarsj(j) -> (barsj)
      [barsj : array(float64)]  Value of the j'th dual variable of barx.  
      [j : int32]  Index of the semidefinite variable.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getbarsj_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getbarsj_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarsslice_6(self,whichsol : soltype,first,last,slicesize,barsslice):
    copyback_barsslice = False
    if barsslice is None:
      barsslice_ = None
      _tmparray_barsslice_ = None
    else:
      if len(barsslice) < int(slicesize):
        raise ValueError("argument barsslice is too short")
      _tmparray_barsslice_ = (ctypes.c_double*len(barsslice))(*barsslice)
    _res_getbarsslice = __library__.MSK_getbarsslice(self.__nativep,whichsol,first,last,slicesize,_tmparray_barsslice_)
    if _res_getbarsslice != 0:
      _,_msg_getbarsslice = self.__getlasterror(_res_getbarsslice)
      raise Error(rescode(_res_getbarsslice),_msg_getbarsslice)
    if barsslice is not None:
      for __tmp_574,__tmp_575 in enumerate(_tmparray_barsslice_):
        barsslice[__tmp_574] = __tmp_575
  def __getbarsslice_5(self,whichsol : soltype,first,last,slicesize):
    barsslice = numpy.zeros(slicesize,numpy.float64)
    _res_getbarsslice = __library__.MSK_getbarsslice(self.__nativep,whichsol,first,last,slicesize,ctypes.cast(barsslice.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarsslice != 0:
      _,_msg_getbarsslice = self.__getlasterror(_res_getbarsslice)
      raise Error(rescode(_res_getbarsslice),_msg_getbarsslice)
    return (barsslice)
  def getbarsslice(self,*args,**kwds):
    """
    Obtains the dual solution for a sequence of semidefinite variables.
  
    getbarsslice(first,last,slicesize,barsslice)
    getbarsslice(first,last,slicesize) -> (barsslice)
      [barsslice : array(float64)]  Dual solution values of symmetric matrix variables in the slice, stored sequentially.  
      [first : int32]  Index of the first semidefinite variable in the slice.  
      [last : int32]  Index of the last semidefinite variable in the slice plus one.  
      [slicesize : int64]  Denotes the length of the array barsslice.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getbarsslice_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 5: return self.__getbarsslice_5(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putskc_3(self,whichsol : soltype,skc):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_577 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_577))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(skc) < __tmp_577.value:
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))(*skc)
    _res_putskc = __library__.MSK_putskc(self.__nativep,whichsol,_tmparray_skc_)
    if _res_putskc != 0:
      _,_msg_putskc = self.__getlasterror(_res_putskc)
      raise Error(rescode(_res_putskc),_msg_putskc)
  def putskc(self,*args,**kwds):
    """
    Sets the status keys for the constraints.
  
    putskc(skc)
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
    """
    return self.__putskc_3(*args,**kwds)
  def __putskx_3(self,whichsol : soltype,skx):
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      __tmp_585 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_585))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(skx) < __tmp_585.value:
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))(*skx)
    _res_putskx = __library__.MSK_putskx(self.__nativep,whichsol,_tmparray_skx_)
    if _res_putskx != 0:
      _,_msg_putskx = self.__getlasterror(_res_putskx)
      raise Error(rescode(_res_putskx),_msg_putskx)
  def putskx(self,*args,**kwds):
    """
    Sets the status keys for the scalar variables.
  
    putskx(skx)
      [skx : array(mosek.stakey)]  Status keys for the variables.  
    """
    return self.__putskx_3(*args,**kwds)
  def __putxc_3(self,whichsol : soltype,xc):
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      __tmp_593 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_593))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(xc) < int(__tmp_593.value):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    _res_putxc = __library__.MSK_putxc(self.__nativep,whichsol,_tmparray_xc_)
    if _res_putxc != 0:
      _,_msg_putxc = self.__getlasterror(_res_putxc)
      raise Error(rescode(_res_putxc),_msg_putxc)
    if xc is not None:
      for __tmp_595,__tmp_596 in enumerate(_tmparray_xc_):
        xc[__tmp_595] = __tmp_596
  def __putxc_2(self,whichsol : soltype):
    __tmp_597 = ctypes.c_int32()
    _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_597))
    if _res_getnumcon != 0:
      _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
      raise Error(rescode(_res_getnumcon),_msg_getnumcon)
    xc = numpy.zeros(__tmp_597.value,numpy.float64)
    _res_putxc = __library__.MSK_putxc(self.__nativep,whichsol,ctypes.cast(xc.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_putxc != 0:
      _,_msg_putxc = self.__getlasterror(_res_putxc)
      raise Error(rescode(_res_putxc),_msg_putxc)
    return (xc)
  def putxc(self,*args,**kwds):
    """
    Sets the xc vector for a solution.
  
    putxc(xc)
    putxc() -> (xc)
      [xc : array(float64)]  Primal constraint solution.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__putxc_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__putxc_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putxx_3(self,whichsol : soltype,xx):
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      __tmp_600 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_600))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(xx) < int(__tmp_600.value):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    _res_putxx = __library__.MSK_putxx(self.__nativep,whichsol,_tmparray_xx_)
    if _res_putxx != 0:
      _,_msg_putxx = self.__getlasterror(_res_putxx)
      raise Error(rescode(_res_putxx),_msg_putxx)
  def putxx(self,*args,**kwds):
    """
    Sets the xx vector for a solution.
  
    putxx(xx)
      [xx : array(float64)]  Primal variable solution.  
    """
    return self.__putxx_3(*args,**kwds)
  def __puty_3(self,whichsol : soltype,y):
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      __tmp_604 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_604))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(y) < int(__tmp_604.value):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_puty = __library__.MSK_puty(self.__nativep,whichsol,_tmparray_y_)
    if _res_puty != 0:
      _,_msg_puty = self.__getlasterror(_res_puty)
      raise Error(rescode(_res_puty),_msg_puty)
  def puty(self,*args,**kwds):
    """
    Sets the y vector for a solution.
  
    puty(y)
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    return self.__puty_3(*args,**kwds)
  def __putslc_3(self,whichsol : soltype,slc):
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      __tmp_608 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_608))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(slc) < int(__tmp_608.value):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    _res_putslc = __library__.MSK_putslc(self.__nativep,whichsol,_tmparray_slc_)
    if _res_putslc != 0:
      _,_msg_putslc = self.__getlasterror(_res_putslc)
      raise Error(rescode(_res_putslc),_msg_putslc)
  def putslc(self,*args,**kwds):
    """
    Sets the slc vector for a solution.
  
    putslc(slc)
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
    """
    return self.__putslc_3(*args,**kwds)
  def __putsuc_3(self,whichsol : soltype,suc):
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      __tmp_612 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_612))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(suc) < int(__tmp_612.value):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    _res_putsuc = __library__.MSK_putsuc(self.__nativep,whichsol,_tmparray_suc_)
    if _res_putsuc != 0:
      _,_msg_putsuc = self.__getlasterror(_res_putsuc)
      raise Error(rescode(_res_putsuc),_msg_putsuc)
  def putsuc(self,*args,**kwds):
    """
    Sets the suc vector for a solution.
  
    putsuc(suc)
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
    """
    return self.__putsuc_3(*args,**kwds)
  def __putslx_3(self,whichsol : soltype,slx):
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      __tmp_616 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_616))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(slx) < int(__tmp_616.value):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    _res_putslx = __library__.MSK_putslx(self.__nativep,whichsol,_tmparray_slx_)
    if _res_putslx != 0:
      _,_msg_putslx = self.__getlasterror(_res_putslx)
      raise Error(rescode(_res_putslx),_msg_putslx)
  def putslx(self,*args,**kwds):
    """
    Sets the slx vector for a solution.
  
    putslx(slx)
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
    """
    return self.__putslx_3(*args,**kwds)
  def __putsux_3(self,whichsol : soltype,sux):
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      __tmp_620 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_620))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(sux) < int(__tmp_620.value):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    _res_putsux = __library__.MSK_putsux(self.__nativep,whichsol,_tmparray_sux_)
    if _res_putsux != 0:
      _,_msg_putsux = self.__getlasterror(_res_putsux)
      raise Error(rescode(_res_putsux),_msg_putsux)
  def putsux(self,*args,**kwds):
    """
    Sets the sux vector for a solution.
  
    putsux(sux)
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
    """
    return self.__putsux_3(*args,**kwds)
  def __putsnx_3(self,whichsol : soltype,sux):
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      __tmp_624 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_624))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(sux) < int(__tmp_624.value):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    _res_putsnx = __library__.MSK_putsnx(self.__nativep,whichsol,_tmparray_sux_)
    if _res_putsnx != 0:
      _,_msg_putsnx = self.__getlasterror(_res_putsnx)
      raise Error(rescode(_res_putsnx),_msg_putsnx)
  def putsnx(self,*args,**kwds):
    """
    Sets the snx vector for a solution.
  
    putsnx(sux)
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
    """
    return self.__putsnx_3(*args,**kwds)
  def __putaccdoty_4(self,whichsol : soltype,accidx,doty):
    copyback_doty = False
    if doty is None:
      doty_ = None
      _tmparray_doty_ = None
    else:
      __tmp_628 = ctypes.c_int64()
      _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_628))
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      if len(doty) < int(__tmp_628.value):
        raise ValueError("argument doty is too short")
      _tmparray_doty_ = (ctypes.c_double*len(doty))(*doty)
    _res_putaccdoty = __library__.MSK_putaccdoty(self.__nativep,whichsol,accidx,_tmparray_doty_)
    if _res_putaccdoty != 0:
      _,_msg_putaccdoty = self.__getlasterror(_res_putaccdoty)
      raise Error(rescode(_res_putaccdoty),_msg_putaccdoty)
    if doty is not None:
      for __tmp_630,__tmp_631 in enumerate(_tmparray_doty_):
        doty[__tmp_630] = __tmp_631
  def __putaccdoty_3(self,whichsol : soltype,accidx):
    __tmp_632 = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_632))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    doty = numpy.zeros(__tmp_632.value,numpy.float64)
    _res_putaccdoty = __library__.MSK_putaccdoty(self.__nativep,whichsol,accidx,ctypes.cast(doty.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_putaccdoty != 0:
      _,_msg_putaccdoty = self.__getlasterror(_res_putaccdoty)
      raise Error(rescode(_res_putaccdoty),_msg_putaccdoty)
    return (doty)
  def putaccdoty(self,*args,**kwds):
    """
    Puts the doty vector for a solution.
  
    putaccdoty(accidx,doty)
    putaccdoty(accidx) -> (doty)
      [accidx : int64]  The index of the affine conic constraint.  
      [doty : array(float64)]  The dual values for this affine conic constraint. The array should have length equal to the dimension of the constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__putaccdoty_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__putaccdoty_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putskcslice_5(self,whichsol : soltype,first,last,skc):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(skc) < (last - first):
        raise ValueError("argument skc is too short")
      _tmparray_skc_ = (ctypes.c_int32*len(skc))(*skc)
    _res_putskcslice = __library__.MSK_putskcslice(self.__nativep,whichsol,first,last,_tmparray_skc_)
    if _res_putskcslice != 0:
      _,_msg_putskcslice = self.__getlasterror(_res_putskcslice)
      raise Error(rescode(_res_putskcslice),_msg_putskcslice)
  def putskcslice(self,*args,**kwds):
    """
    Sets the status keys for a slice of the constraints.
  
    putskcslice(first,last,skc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
    """
    return self.__putskcslice_5(*args,**kwds)
  def __putskxslice_5(self,whichsol : soltype,first,last,skx):
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(skx) < (last - first):
        raise ValueError("argument skx is too short")
      _tmparray_skx_ = (ctypes.c_int32*len(skx))(*skx)
    _res_putskxslice = __library__.MSK_putskxslice(self.__nativep,whichsol,first,last,_tmparray_skx_)
    if _res_putskxslice != 0:
      _,_msg_putskxslice = self.__getlasterror(_res_putskxslice)
      raise Error(rescode(_res_putskxslice),_msg_putskxslice)
  def putskxslice(self,*args,**kwds):
    """
    Sets the status keys for a slice of the variables.
  
    putskxslice(first,last,skx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
    """
    return self.__putskxslice_5(*args,**kwds)
  def __putxcslice_5(self,whichsol : soltype,first,last,xc):
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      if len(xc) < int((last - first)):
        raise ValueError("argument xc is too short")
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    _res_putxcslice = __library__.MSK_putxcslice(self.__nativep,whichsol,first,last,_tmparray_xc_)
    if _res_putxcslice != 0:
      _,_msg_putxcslice = self.__getlasterror(_res_putxcslice)
      raise Error(rescode(_res_putxcslice),_msg_putxcslice)
  def putxcslice(self,*args,**kwds):
    """
    Sets a slice of the xc vector for a solution.
  
    putxcslice(first,last,xc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [xc : array(float64)]  Primal constraint solution.  
    """
    return self.__putxcslice_5(*args,**kwds)
  def __putxxslice_5(self,whichsol : soltype,first,last,xx):
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      if len(xx) < int((last - first)):
        raise ValueError("argument xx is too short")
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    _res_putxxslice = __library__.MSK_putxxslice(self.__nativep,whichsol,first,last,_tmparray_xx_)
    if _res_putxxslice != 0:
      _,_msg_putxxslice = self.__getlasterror(_res_putxxslice)
      raise Error(rescode(_res_putxxslice),_msg_putxxslice)
  def putxxslice(self,*args,**kwds):
    """
    Sets a slice of the xx vector for a solution.
  
    putxxslice(first,last,xx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [xx : array(float64)]  Primal variable solution.  
    """
    return self.__putxxslice_5(*args,**kwds)
  def __putyslice_5(self,whichsol : soltype,first,last,y):
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      if len(y) < int((last - first)):
        raise ValueError("argument y is too short")
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    _res_putyslice = __library__.MSK_putyslice(self.__nativep,whichsol,first,last,_tmparray_y_)
    if _res_putyslice != 0:
      _,_msg_putyslice = self.__getlasterror(_res_putyslice)
      raise Error(rescode(_res_putyslice),_msg_putyslice)
  def putyslice(self,*args,**kwds):
    """
    Sets a slice of the y vector for a solution.
  
    putyslice(first,last,y)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    return self.__putyslice_5(*args,**kwds)
  def __putslcslice_5(self,whichsol : soltype,first,last,slc):
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      if len(slc) < int((last - first)):
        raise ValueError("argument slc is too short")
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    _res_putslcslice = __library__.MSK_putslcslice(self.__nativep,whichsol,first,last,_tmparray_slc_)
    if _res_putslcslice != 0:
      _,_msg_putslcslice = self.__getlasterror(_res_putslcslice)
      raise Error(rescode(_res_putslcslice),_msg_putslcslice)
  def putslcslice(self,*args,**kwds):
    """
    Sets a slice of the slc vector for a solution.
  
    putslcslice(first,last,slc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
    """
    return self.__putslcslice_5(*args,**kwds)
  def __putsucslice_5(self,whichsol : soltype,first,last,suc):
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      if len(suc) < int((last - first)):
        raise ValueError("argument suc is too short")
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    _res_putsucslice = __library__.MSK_putsucslice(self.__nativep,whichsol,first,last,_tmparray_suc_)
    if _res_putsucslice != 0:
      _,_msg_putsucslice = self.__getlasterror(_res_putsucslice)
      raise Error(rescode(_res_putsucslice),_msg_putsucslice)
  def putsucslice(self,*args,**kwds):
    """
    Sets a slice of the suc vector for a solution.
  
    putsucslice(first,last,suc)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
    """
    return self.__putsucslice_5(*args,**kwds)
  def __putslxslice_5(self,whichsol : soltype,first,last,slx):
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      if len(slx) < int((last - first)):
        raise ValueError("argument slx is too short")
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    _res_putslxslice = __library__.MSK_putslxslice(self.__nativep,whichsol,first,last,_tmparray_slx_)
    if _res_putslxslice != 0:
      _,_msg_putslxslice = self.__getlasterror(_res_putslxslice)
      raise Error(rescode(_res_putslxslice),_msg_putslxslice)
  def putslxslice(self,*args,**kwds):
    """
    Sets a slice of the slx vector for a solution.
  
    putslxslice(first,last,slx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
    """
    return self.__putslxslice_5(*args,**kwds)
  def __putsuxslice_5(self,whichsol : soltype,first,last,sux):
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      if len(sux) < int((last - first)):
        raise ValueError("argument sux is too short")
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    _res_putsuxslice = __library__.MSK_putsuxslice(self.__nativep,whichsol,first,last,_tmparray_sux_)
    if _res_putsuxslice != 0:
      _,_msg_putsuxslice = self.__getlasterror(_res_putsuxslice)
      raise Error(rescode(_res_putsuxslice),_msg_putsuxslice)
  def putsuxslice(self,*args,**kwds):
    """
    Sets a slice of the sux vector for a solution.
  
    putsuxslice(first,last,sux)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
    """
    return self.__putsuxslice_5(*args,**kwds)
  def __putsnxslice_5(self,whichsol : soltype,first,last,snx):
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      if len(snx) < int((last - first)):
        raise ValueError("argument snx is too short")
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    _res_putsnxslice = __library__.MSK_putsnxslice(self.__nativep,whichsol,first,last,_tmparray_snx_)
    if _res_putsnxslice != 0:
      _,_msg_putsnxslice = self.__getlasterror(_res_putsnxslice)
      raise Error(rescode(_res_putsnxslice),_msg_putsnxslice)
  def putsnxslice(self,*args,**kwds):
    """
    Sets a slice of the snx vector for a solution.
  
    putsnxslice(first,last,snx)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
    """
    return self.__putsnxslice_5(*args,**kwds)
  def __putbarxj_4(self,whichsol : soltype,j,barxj):
    copyback_barxj = False
    if barxj is None:
      barxj_ = None
      _tmparray_barxj_ = None
    else:
      __tmp_643 = ctypes.c_int64()
      _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_643))
      if _res_getlenbarvarj != 0:
        _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
        raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
      if len(barxj) < int(__tmp_643.value):
        raise ValueError("argument barxj is too short")
      _tmparray_barxj_ = (ctypes.c_double*len(barxj))(*barxj)
    _res_putbarxj = __library__.MSK_putbarxj(self.__nativep,whichsol,j,_tmparray_barxj_)
    if _res_putbarxj != 0:
      _,_msg_putbarxj = self.__getlasterror(_res_putbarxj)
      raise Error(rescode(_res_putbarxj),_msg_putbarxj)
  def putbarxj(self,*args,**kwds):
    """
    Sets the primal solution for a semidefinite variable.
  
    putbarxj(j,barxj)
      [barxj : array(float64)]  Value of the j'th variable of barx.  
      [j : int32]  Index of the semidefinite variable.  
    """
    return self.__putbarxj_4(*args,**kwds)
  def __putbarsj_4(self,whichsol : soltype,j,barsj):
    copyback_barsj = False
    if barsj is None:
      barsj_ = None
      _tmparray_barsj_ = None
    else:
      __tmp_647 = ctypes.c_int64()
      _res_getlenbarvarj = __library__.MSK_getlenbarvarj(self.__nativep,j,ctypes.byref(__tmp_647))
      if _res_getlenbarvarj != 0:
        _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
        raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
      if len(barsj) < int(__tmp_647.value):
        raise ValueError("argument barsj is too short")
      _tmparray_barsj_ = (ctypes.c_double*len(barsj))(*barsj)
    _res_putbarsj = __library__.MSK_putbarsj(self.__nativep,whichsol,j,_tmparray_barsj_)
    if _res_putbarsj != 0:
      _,_msg_putbarsj = self.__getlasterror(_res_putbarsj)
      raise Error(rescode(_res_putbarsj),_msg_putbarsj)
  def putbarsj(self,*args,**kwds):
    """
    Sets the dual solution for a semidefinite variable.
  
    putbarsj(j,barsj)
      [barsj : array(float64)]  Value of the j'th variable of barx.  
      [j : int32]  Index of the semidefinite variable.  
    """
    return self.__putbarsj_4(*args,**kwds)
  def __getpviolcon_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpviolcon = __library__.MSK_getpviolcon(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getpviolcon != 0:
      _,_msg_getpviolcon = self.__getlasterror(_res_getpviolcon)
      raise Error(rescode(_res_getpviolcon),_msg_getpviolcon)
    if viol is not None:
      for __tmp_651,__tmp_652 in enumerate(_tmparray_viol_):
        viol[__tmp_651] = __tmp_652
  def __getpviolcon_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getpviolcon = __library__.MSK_getpviolcon(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpviolcon != 0:
      _,_msg_getpviolcon = self.__getlasterror(_res_getpviolcon)
      raise Error(rescode(_res_getpviolcon),_msg_getpviolcon)
    return (viol)
  def getpviolcon(self,*args,**kwds):
    """
    Computes the violation of a primal solution associated to a constraint.
  
    getpviolcon(sub,viol)
    getpviolcon(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpviolcon_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpviolcon_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getpviolvar_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpviolvar = __library__.MSK_getpviolvar(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getpviolvar != 0:
      _,_msg_getpviolvar = self.__getlasterror(_res_getpviolvar)
      raise Error(rescode(_res_getpviolvar),_msg_getpviolvar)
    if viol is not None:
      for __tmp_654,__tmp_655 in enumerate(_tmparray_viol_):
        viol[__tmp_654] = __tmp_655
  def __getpviolvar_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getpviolvar = __library__.MSK_getpviolvar(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpviolvar != 0:
      _,_msg_getpviolvar = self.__getlasterror(_res_getpviolvar)
      raise Error(rescode(_res_getpviolvar),_msg_getpviolvar)
    return (viol)
  def getpviolvar(self,*args,**kwds):
    """
    Computes the violation of a primal solution for a list of scalar variables.
  
    getpviolvar(sub,viol)
    getpviolvar(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of x variables.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpviolvar_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpviolvar_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getpviolbarvar_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpviolbarvar = __library__.MSK_getpviolbarvar(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getpviolbarvar != 0:
      _,_msg_getpviolbarvar = self.__getlasterror(_res_getpviolbarvar)
      raise Error(rescode(_res_getpviolbarvar),_msg_getpviolbarvar)
    if viol is not None:
      for __tmp_657,__tmp_658 in enumerate(_tmparray_viol_):
        viol[__tmp_657] = __tmp_658
  def __getpviolbarvar_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getpviolbarvar = __library__.MSK_getpviolbarvar(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpviolbarvar != 0:
      _,_msg_getpviolbarvar = self.__getlasterror(_res_getpviolbarvar)
      raise Error(rescode(_res_getpviolbarvar),_msg_getpviolbarvar)
    return (viol)
  def getpviolbarvar(self,*args,**kwds):
    """
    Computes the violation of a primal solution for a list of semidefinite variables.
  
    getpviolbarvar(sub,viol)
    getpviolbarvar(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of barX variables.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpviolbarvar_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpviolbarvar_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getpviolcones_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpviolcones = __library__.MSK_getpviolcones(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getpviolcones != 0:
      _,_msg_getpviolcones = self.__getlasterror(_res_getpviolcones)
      raise Error(rescode(_res_getpviolcones),_msg_getpviolcones)
    if viol is not None:
      for __tmp_660,__tmp_661 in enumerate(_tmparray_viol_):
        viol[__tmp_660] = __tmp_661
  def __getpviolcones_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getpviolcones = __library__.MSK_getpviolcones(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpviolcones != 0:
      _,_msg_getpviolcones = self.__getlasterror(_res_getpviolcones)
      raise Error(rescode(_res_getpviolcones),_msg_getpviolcones)
    return (viol)
  def getpviolcones(self,*args,**kwds):
    """
    Computes the violation of a solution for set of conic constraints.
  
    getpviolcones(sub,viol)
    getpviolcones(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of conic constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpviolcones_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpviolcones_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getpviolacc_4(self,whichsol : soltype,accidxlist,viol):
    numaccidx = len(accidxlist) if accidxlist is not None else 0
    copyback_accidxlist = False
    if accidxlist is None:
      accidxlist_ = None
      _tmparray_accidxlist_ = None
    else:
      _tmparray_accidxlist_ = (ctypes.c_int64*len(accidxlist))(*accidxlist)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(numaccidx):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpviolacc = __library__.MSK_getpviolacc(self.__nativep,whichsol,numaccidx,_tmparray_accidxlist_,_tmparray_viol_)
    if _res_getpviolacc != 0:
      _,_msg_getpviolacc = self.__getlasterror(_res_getpviolacc)
      raise Error(rescode(_res_getpviolacc),_msg_getpviolacc)
    if viol is not None:
      for __tmp_663,__tmp_664 in enumerate(_tmparray_viol_):
        viol[__tmp_663] = __tmp_664
  def __getpviolacc_3(self,whichsol : soltype,accidxlist):
    numaccidx = len(accidxlist) if accidxlist is not None else 0
    copyback_accidxlist = False
    if accidxlist is None:
      accidxlist_ = None
      _tmparray_accidxlist_ = None
    else:
      _tmparray_accidxlist_ = (ctypes.c_int64*len(accidxlist))(*accidxlist)
    viol = numpy.zeros(numaccidx,numpy.float64)
    _res_getpviolacc = __library__.MSK_getpviolacc(self.__nativep,whichsol,numaccidx,_tmparray_accidxlist_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpviolacc != 0:
      _,_msg_getpviolacc = self.__getlasterror(_res_getpviolacc)
      raise Error(rescode(_res_getpviolacc),_msg_getpviolacc)
    return (viol)
  def getpviolacc(self,*args,**kwds):
    """
    Computes the violation of a solution for set of affine conic constraints.
  
    getpviolacc(accidxlist,viol)
    getpviolacc(accidxlist) -> (viol)
      [accidxlist : array(int64)]  An array of indexes of conic constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpviolacc_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpviolacc_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getpvioldjc_4(self,whichsol : soltype,djcidxlist,viol):
    numdjcidx = len(djcidxlist) if djcidxlist is not None else 0
    copyback_djcidxlist = False
    if djcidxlist is None:
      djcidxlist_ = None
      _tmparray_djcidxlist_ = None
    else:
      _tmparray_djcidxlist_ = (ctypes.c_int64*len(djcidxlist))(*djcidxlist)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(numdjcidx):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getpvioldjc = __library__.MSK_getpvioldjc(self.__nativep,whichsol,numdjcidx,_tmparray_djcidxlist_,_tmparray_viol_)
    if _res_getpvioldjc != 0:
      _,_msg_getpvioldjc = self.__getlasterror(_res_getpvioldjc)
      raise Error(rescode(_res_getpvioldjc),_msg_getpvioldjc)
    if viol is not None:
      for __tmp_666,__tmp_667 in enumerate(_tmparray_viol_):
        viol[__tmp_666] = __tmp_667
  def __getpvioldjc_3(self,whichsol : soltype,djcidxlist):
    numdjcidx = len(djcidxlist) if djcidxlist is not None else 0
    copyback_djcidxlist = False
    if djcidxlist is None:
      djcidxlist_ = None
      _tmparray_djcidxlist_ = None
    else:
      _tmparray_djcidxlist_ = (ctypes.c_int64*len(djcidxlist))(*djcidxlist)
    viol = numpy.zeros(numdjcidx,numpy.float64)
    _res_getpvioldjc = __library__.MSK_getpvioldjc(self.__nativep,whichsol,numdjcidx,_tmparray_djcidxlist_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpvioldjc != 0:
      _,_msg_getpvioldjc = self.__getlasterror(_res_getpvioldjc)
      raise Error(rescode(_res_getpvioldjc),_msg_getpvioldjc)
    return (viol)
  def getpvioldjc(self,*args,**kwds):
    """
    Computes the violation of a solution for set of disjunctive constraints.
  
    getpvioldjc(djcidxlist,viol)
    getpvioldjc(djcidxlist) -> (viol)
      [djcidxlist : array(int64)]  An array of indexes of disjunctive constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getpvioldjc_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getpvioldjc_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdviolcon_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getdviolcon = __library__.MSK_getdviolcon(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getdviolcon != 0:
      _,_msg_getdviolcon = self.__getlasterror(_res_getdviolcon)
      raise Error(rescode(_res_getdviolcon),_msg_getdviolcon)
    if viol is not None:
      for __tmp_669,__tmp_670 in enumerate(_tmparray_viol_):
        viol[__tmp_669] = __tmp_670
  def __getdviolcon_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getdviolcon = __library__.MSK_getdviolcon(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdviolcon != 0:
      _,_msg_getdviolcon = self.__getlasterror(_res_getdviolcon)
      raise Error(rescode(_res_getdviolcon),_msg_getdviolcon)
    return (viol)
  def getdviolcon(self,*args,**kwds):
    """
    Computes the violation of a dual solution associated with a set of constraints.
  
    getdviolcon(sub,viol)
    getdviolcon(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getdviolcon_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getdviolcon_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdviolvar_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getdviolvar = __library__.MSK_getdviolvar(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getdviolvar != 0:
      _,_msg_getdviolvar = self.__getlasterror(_res_getdviolvar)
      raise Error(rescode(_res_getdviolvar),_msg_getdviolvar)
    if viol is not None:
      for __tmp_672,__tmp_673 in enumerate(_tmparray_viol_):
        viol[__tmp_672] = __tmp_673
  def __getdviolvar_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getdviolvar = __library__.MSK_getdviolvar(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdviolvar != 0:
      _,_msg_getdviolvar = self.__getlasterror(_res_getdviolvar)
      raise Error(rescode(_res_getdviolvar),_msg_getdviolvar)
    return (viol)
  def getdviolvar(self,*args,**kwds):
    """
    Computes the violation of a dual solution associated with a set of scalar variables.
  
    getdviolvar(sub,viol)
    getdviolvar(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of x variables.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getdviolvar_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getdviolvar_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdviolbarvar_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getdviolbarvar = __library__.MSK_getdviolbarvar(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getdviolbarvar != 0:
      _,_msg_getdviolbarvar = self.__getlasterror(_res_getdviolbarvar)
      raise Error(rescode(_res_getdviolbarvar),_msg_getdviolbarvar)
    if viol is not None:
      for __tmp_675,__tmp_676 in enumerate(_tmparray_viol_):
        viol[__tmp_675] = __tmp_676
  def __getdviolbarvar_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getdviolbarvar = __library__.MSK_getdviolbarvar(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdviolbarvar != 0:
      _,_msg_getdviolbarvar = self.__getlasterror(_res_getdviolbarvar)
      raise Error(rescode(_res_getdviolbarvar),_msg_getdviolbarvar)
    return (viol)
  def getdviolbarvar(self,*args,**kwds):
    """
    Computes the violation of dual solution for a set of semidefinite variables.
  
    getdviolbarvar(sub,viol)
    getdviolbarvar(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of barx variables.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getdviolbarvar_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getdviolbarvar_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdviolcones_4(self,whichsol : soltype,sub,viol):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(num):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getdviolcones = __library__.MSK_getdviolcones(self.__nativep,whichsol,num,_tmparray_sub_,_tmparray_viol_)
    if _res_getdviolcones != 0:
      _,_msg_getdviolcones = self.__getlasterror(_res_getdviolcones)
      raise Error(rescode(_res_getdviolcones),_msg_getdviolcones)
    if viol is not None:
      for __tmp_678,__tmp_679 in enumerate(_tmparray_viol_):
        viol[__tmp_678] = __tmp_679
  def __getdviolcones_3(self,whichsol : soltype,sub):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    viol = numpy.zeros(num,numpy.float64)
    _res_getdviolcones = __library__.MSK_getdviolcones(self.__nativep,whichsol,num,_tmparray_sub_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdviolcones != 0:
      _,_msg_getdviolcones = self.__getlasterror(_res_getdviolcones)
      raise Error(rescode(_res_getdviolcones),_msg_getdviolcones)
    return (viol)
  def getdviolcones(self,*args,**kwds):
    """
    Computes the violation of a solution for set of dual conic constraints.
  
    getdviolcones(sub,viol)
    getdviolcones(sub) -> (viol)
      [sub : array(int32)]  An array of indexes of conic constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getdviolcones_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getdviolcones_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdviolacc_4(self,whichsol : soltype,accidxlist,viol):
    numaccidx = len(accidxlist) if accidxlist is not None else 0
    copyback_accidxlist = False
    if accidxlist is None:
      accidxlist_ = None
      _tmparray_accidxlist_ = None
    else:
      _tmparray_accidxlist_ = (ctypes.c_int64*len(accidxlist))(*accidxlist)
    copyback_viol = False
    if viol is None:
      viol_ = None
      _tmparray_viol_ = None
    else:
      if len(viol) < int(numaccidx):
        raise ValueError("argument viol is too short")
      _tmparray_viol_ = (ctypes.c_double*len(viol))(*viol)
    _res_getdviolacc = __library__.MSK_getdviolacc(self.__nativep,whichsol,numaccidx,_tmparray_accidxlist_,_tmparray_viol_)
    if _res_getdviolacc != 0:
      _,_msg_getdviolacc = self.__getlasterror(_res_getdviolacc)
      raise Error(rescode(_res_getdviolacc),_msg_getdviolacc)
    if viol is not None:
      for __tmp_681,__tmp_682 in enumerate(_tmparray_viol_):
        viol[__tmp_681] = __tmp_682
  def __getdviolacc_3(self,whichsol : soltype,accidxlist):
    numaccidx = len(accidxlist) if accidxlist is not None else 0
    copyback_accidxlist = False
    if accidxlist is None:
      accidxlist_ = None
      _tmparray_accidxlist_ = None
    else:
      _tmparray_accidxlist_ = (ctypes.c_int64*len(accidxlist))(*accidxlist)
    viol = numpy.zeros(numaccidx,numpy.float64)
    _res_getdviolacc = __library__.MSK_getdviolacc(self.__nativep,whichsol,numaccidx,_tmparray_accidxlist_,ctypes.cast(viol.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdviolacc != 0:
      _,_msg_getdviolacc = self.__getlasterror(_res_getdviolacc)
      raise Error(rescode(_res_getdviolacc),_msg_getdviolacc)
    return (viol)
  def getdviolacc(self,*args,**kwds):
    """
    Computes the violation of the dual solution for set of affine conic constraints.
  
    getdviolacc(accidxlist,viol)
    getdviolacc(accidxlist) -> (viol)
      [accidxlist : array(int64)]  An array of indexes of conic constraints.  
      [viol : array(float64)]  List of violations corresponding to sub.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getdviolacc_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getdviolacc_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsolutioninfo_2(self,whichsol : soltype):
    pobj_ = ctypes.c_double()
    pviolcon_ = ctypes.c_double()
    pviolvar_ = ctypes.c_double()
    pviolbarvar_ = ctypes.c_double()
    pviolcone_ = ctypes.c_double()
    pviolitg_ = ctypes.c_double()
    dobj_ = ctypes.c_double()
    dviolcon_ = ctypes.c_double()
    dviolvar_ = ctypes.c_double()
    dviolbarvar_ = ctypes.c_double()
    dviolcone_ = ctypes.c_double()
    _res_getsolutioninfo = __library__.MSK_getsolutioninfo(self.__nativep,whichsol,ctypes.byref(pobj_),ctypes.byref(pviolcon_),ctypes.byref(pviolvar_),ctypes.byref(pviolbarvar_),ctypes.byref(pviolcone_),ctypes.byref(pviolitg_),ctypes.byref(dobj_),ctypes.byref(dviolcon_),ctypes.byref(dviolvar_),ctypes.byref(dviolbarvar_),ctypes.byref(dviolcone_))
    if _res_getsolutioninfo != 0:
      _,_msg_getsolutioninfo = self.__getlasterror(_res_getsolutioninfo)
      raise Error(rescode(_res_getsolutioninfo),_msg_getsolutioninfo)
    pobj = pobj_.value
    pviolcon = pviolcon_.value
    pviolvar = pviolvar_.value
    pviolbarvar = pviolbarvar_.value
    pviolcone = pviolcone_.value
    pviolitg = pviolitg_.value
    dobj = dobj_.value
    dviolcon = dviolcon_.value
    dviolvar = dviolvar_.value
    dviolbarvar = dviolbarvar_.value
    dviolcone = dviolcone_.value
    return (pobj_.value,pviolcon_.value,pviolvar_.value,pviolbarvar_.value,pviolcone_.value,pviolitg_.value,dobj_.value,dviolcon_.value,dviolvar_.value,dviolbarvar_.value,dviolcone_.value)
  def getsolutioninfo(self,*args,**kwds):
    """
    Obtains information about of a solution.
  
    getsolutioninfo() -> 
                   (pobj,
                    pviolcon,
                    pviolvar,
                    pviolbarvar,
                    pviolcone,
                    pviolitg,
                    dobj,
                    dviolcon,
                    dviolvar,
                    dviolbarvar,
                    dviolcone)
      [dobj : float64]  Dual objective value.  
      [dviolbarvar : float64]  Maximal dual bound violation for a bars variable.  
      [dviolcon : float64]  Maximal dual bound violation for a xc variable.  
      [dviolcone : float64]  Maximum violation of the dual solution in the dual conic constraints.  
      [dviolvar : float64]  Maximal dual bound violation for a xx variable.  
      [pobj : float64]  The primal objective value.  
      [pviolbarvar : float64]  Maximal primal bound violation for a barx variable.  
      [pviolcon : float64]  Maximal primal bound violation for a xc variable.  
      [pviolcone : float64]  Maximal primal violation of the solution with respect to the conic constraints.  
      [pviolitg : float64]  Maximal violation in the integer constraints.  
      [pviolvar : float64]  Maximal primal bound violation for a xx variable.  
    """
    return self.__getsolutioninfo_2(*args,**kwds)
  def __getsolutioninfonew_2(self,whichsol : soltype):
    pobj_ = ctypes.c_double()
    pviolcon_ = ctypes.c_double()
    pviolvar_ = ctypes.c_double()
    pviolbarvar_ = ctypes.c_double()
    pviolcone_ = ctypes.c_double()
    pviolacc_ = ctypes.c_double()
    pvioldjc_ = ctypes.c_double()
    pviolitg_ = ctypes.c_double()
    dobj_ = ctypes.c_double()
    dviolcon_ = ctypes.c_double()
    dviolvar_ = ctypes.c_double()
    dviolbarvar_ = ctypes.c_double()
    dviolcone_ = ctypes.c_double()
    dviolacc_ = ctypes.c_double()
    _res_getsolutioninfonew = __library__.MSK_getsolutioninfonew(self.__nativep,whichsol,ctypes.byref(pobj_),ctypes.byref(pviolcon_),ctypes.byref(pviolvar_),ctypes.byref(pviolbarvar_),ctypes.byref(pviolcone_),ctypes.byref(pviolacc_),ctypes.byref(pvioldjc_),ctypes.byref(pviolitg_),ctypes.byref(dobj_),ctypes.byref(dviolcon_),ctypes.byref(dviolvar_),ctypes.byref(dviolbarvar_),ctypes.byref(dviolcone_),ctypes.byref(dviolacc_))
    if _res_getsolutioninfonew != 0:
      _,_msg_getsolutioninfonew = self.__getlasterror(_res_getsolutioninfonew)
      raise Error(rescode(_res_getsolutioninfonew),_msg_getsolutioninfonew)
    pobj = pobj_.value
    pviolcon = pviolcon_.value
    pviolvar = pviolvar_.value
    pviolbarvar = pviolbarvar_.value
    pviolcone = pviolcone_.value
    pviolacc = pviolacc_.value
    pvioldjc = pvioldjc_.value
    pviolitg = pviolitg_.value
    dobj = dobj_.value
    dviolcon = dviolcon_.value
    dviolvar = dviolvar_.value
    dviolbarvar = dviolbarvar_.value
    dviolcone = dviolcone_.value
    dviolacc = dviolacc_.value
    return (pobj_.value,pviolcon_.value,pviolvar_.value,pviolbarvar_.value,pviolcone_.value,pviolacc_.value,pvioldjc_.value,pviolitg_.value,dobj_.value,dviolcon_.value,dviolvar_.value,dviolbarvar_.value,dviolcone_.value,dviolacc_.value)
  def getsolutioninfonew(self,*args,**kwds):
    """
    Obtains information about of a solution.
  
    getsolutioninfonew() -> 
                      (pobj,
                       pviolcon,
                       pviolvar,
                       pviolbarvar,
                       pviolcone,
                       pviolacc,
                       pvioldjc,
                       pviolitg,
                       dobj,
                       dviolcon,
                       dviolvar,
                       dviolbarvar,
                       dviolcone,
                       dviolacc)
      [dobj : float64]  Dual objective value.  
      [dviolacc : float64]  Maximum violation of the dual solution in the dual affine conic constraints.  
      [dviolbarvar : float64]  Maximal dual bound violation for a bars variable.  
      [dviolcon : float64]  Maximal dual bound violation for a xc variable.  
      [dviolcone : float64]  Maximum violation of the dual solution in the dual conic constraints.  
      [dviolvar : float64]  Maximal dual bound violation for a xx variable.  
      [pobj : float64]  The primal objective value.  
      [pviolacc : float64]  Maximal primal violation of the solution with respect to the affine conic constraints.  
      [pviolbarvar : float64]  Maximal primal bound violation for a barx variable.  
      [pviolcon : float64]  Maximal primal bound violation for a xc variable.  
      [pviolcone : float64]  Maximal primal violation of the solution with respect to the conic constraints.  
      [pvioldjc : float64]  Maximal primal violation of the solution with respect to the disjunctive constraints.  
      [pviolitg : float64]  Maximal violation in the integer constraints.  
      [pviolvar : float64]  Maximal primal bound violation for a xx variable.  
    """
    return self.__getsolutioninfonew_2(*args,**kwds)
  def __getdualsolutionnorms_2(self,whichsol : soltype):
    nrmy_ = ctypes.c_double()
    nrmslc_ = ctypes.c_double()
    nrmsuc_ = ctypes.c_double()
    nrmslx_ = ctypes.c_double()
    nrmsux_ = ctypes.c_double()
    nrmsnx_ = ctypes.c_double()
    nrmbars_ = ctypes.c_double()
    _res_getdualsolutionnorms = __library__.MSK_getdualsolutionnorms(self.__nativep,whichsol,ctypes.byref(nrmy_),ctypes.byref(nrmslc_),ctypes.byref(nrmsuc_),ctypes.byref(nrmslx_),ctypes.byref(nrmsux_),ctypes.byref(nrmsnx_),ctypes.byref(nrmbars_))
    if _res_getdualsolutionnorms != 0:
      _,_msg_getdualsolutionnorms = self.__getlasterror(_res_getdualsolutionnorms)
      raise Error(rescode(_res_getdualsolutionnorms),_msg_getdualsolutionnorms)
    nrmy = nrmy_.value
    nrmslc = nrmslc_.value
    nrmsuc = nrmsuc_.value
    nrmslx = nrmslx_.value
    nrmsux = nrmsux_.value
    nrmsnx = nrmsnx_.value
    nrmbars = nrmbars_.value
    return (nrmy_.value,nrmslc_.value,nrmsuc_.value,nrmslx_.value,nrmsux_.value,nrmsnx_.value,nrmbars_.value)
  def getdualsolutionnorms(self,*args,**kwds):
    """
    Compute norms of the dual solution.
  
    getdualsolutionnorms() -> 
                        (nrmy,
                         nrmslc,
                         nrmsuc,
                         nrmslx,
                         nrmsux,
                         nrmsnx,
                         nrmbars)
      [nrmbars : float64]  The norm of the bars vector.  
      [nrmslc : float64]  The norm of the slc vector.  
      [nrmslx : float64]  The norm of the slx vector.  
      [nrmsnx : float64]  The norm of the snx vector.  
      [nrmsuc : float64]  The norm of the suc vector.  
      [nrmsux : float64]  The norm of the sux vector.  
      [nrmy : float64]  The norm of the y vector.  
    """
    return self.__getdualsolutionnorms_2(*args,**kwds)
  def __getprimalsolutionnorms_2(self,whichsol : soltype):
    nrmxc_ = ctypes.c_double()
    nrmxx_ = ctypes.c_double()
    nrmbarx_ = ctypes.c_double()
    _res_getprimalsolutionnorms = __library__.MSK_getprimalsolutionnorms(self.__nativep,whichsol,ctypes.byref(nrmxc_),ctypes.byref(nrmxx_),ctypes.byref(nrmbarx_))
    if _res_getprimalsolutionnorms != 0:
      _,_msg_getprimalsolutionnorms = self.__getlasterror(_res_getprimalsolutionnorms)
      raise Error(rescode(_res_getprimalsolutionnorms),_msg_getprimalsolutionnorms)
    nrmxc = nrmxc_.value
    nrmxx = nrmxx_.value
    nrmbarx = nrmbarx_.value
    return (nrmxc_.value,nrmxx_.value,nrmbarx_.value)
  def getprimalsolutionnorms(self,*args,**kwds):
    """
    Compute norms of the primal solution.
  
    getprimalsolutionnorms() -> (nrmxc,nrmxx,nrmbarx)
      [nrmbarx : float64]  The norm of the barX vector.  
      [nrmxc : float64]  The norm of the xc vector.  
      [nrmxx : float64]  The norm of the xx vector.  
    """
    return self.__getprimalsolutionnorms_2(*args,**kwds)
  def __getsolutionslice_6(self,whichsol : soltype,solitem : solitem,first,last,values):
    copyback_values = False
    if values is None:
      values_ = None
      _tmparray_values_ = None
    else:
      if len(values) < int((last - first)):
        raise ValueError("argument values is too short")
      _tmparray_values_ = (ctypes.c_double*len(values))(*values)
    _res_getsolutionslice = __library__.MSK_getsolutionslice(self.__nativep,whichsol,solitem,first,last,_tmparray_values_)
    if _res_getsolutionslice != 0:
      _,_msg_getsolutionslice = self.__getlasterror(_res_getsolutionslice)
      raise Error(rescode(_res_getsolutionslice),_msg_getsolutionslice)
    if values is not None:
      for __tmp_684,__tmp_685 in enumerate(_tmparray_values_):
        values[__tmp_684] = __tmp_685
  def __getsolutionslice_5(self,whichsol : soltype,solitem : solitem,first,last):
    values = numpy.zeros((last - first),numpy.float64)
    _res_getsolutionslice = __library__.MSK_getsolutionslice(self.__nativep,whichsol,solitem,first,last,ctypes.cast(values.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsolutionslice != 0:
      _,_msg_getsolutionslice = self.__getlasterror(_res_getsolutionslice)
      raise Error(rescode(_res_getsolutionslice),_msg_getsolutionslice)
    return (values)
  def getsolutionslice(self,*args,**kwds):
    """
    Obtains a slice of the solution.
  
    getsolutionslice(first,last,values)
    getsolutionslice(first,last) -> (values)
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
      [values : array(float64)]  The values of the requested solution elements.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getsolutionslice_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 5: return self.__getsolutionslice_5(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getreducedcosts_5(self,whichsol : soltype,first,last,redcosts):
    copyback_redcosts = False
    if redcosts is None:
      redcosts_ = None
      _tmparray_redcosts_ = None
    else:
      if len(redcosts) < int((last - first)):
        raise ValueError("argument redcosts is too short")
      _tmparray_redcosts_ = (ctypes.c_double*len(redcosts))(*redcosts)
    _res_getreducedcosts = __library__.MSK_getreducedcosts(self.__nativep,whichsol,first,last,_tmparray_redcosts_)
    if _res_getreducedcosts != 0:
      _,_msg_getreducedcosts = self.__getlasterror(_res_getreducedcosts)
      raise Error(rescode(_res_getreducedcosts),_msg_getreducedcosts)
    if redcosts is not None:
      for __tmp_687,__tmp_688 in enumerate(_tmparray_redcosts_):
        redcosts[__tmp_687] = __tmp_688
  def __getreducedcosts_4(self,whichsol : soltype,first,last):
    redcosts = numpy.zeros((last - first),numpy.float64)
    _res_getreducedcosts = __library__.MSK_getreducedcosts(self.__nativep,whichsol,first,last,ctypes.cast(redcosts.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getreducedcosts != 0:
      _,_msg_getreducedcosts = self.__getlasterror(_res_getreducedcosts)
      raise Error(rescode(_res_getreducedcosts),_msg_getreducedcosts)
    return (redcosts)
  def getreducedcosts(self,*args,**kwds):
    """
    Obtains the reduced costs for a sequence of variables.
  
    getreducedcosts(first,last,redcosts)
    getreducedcosts(first,last) -> (redcosts)
      [first : int32]  The index of the first variable in the sequence.  
      [last : int32]  The index of the last variable in the sequence plus 1.  
      [redcosts : array(float64)]  Returns the requested reduced costs.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getreducedcosts_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 4: return self.__getreducedcosts_4(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getstrparam_2(self,param : sparam):
    __tmp_690 = ctypes.c_int32()
    _res_getstrparamlen = __library__.MSK_getstrparamlen(self.__nativep,param,ctypes.byref(__tmp_690))
    if _res_getstrparamlen != 0:
      _,_msg_getstrparamlen = self.__getlasterror(_res_getstrparamlen)
      raise Error(rescode(_res_getstrparamlen),_msg_getstrparamlen)
    maxlen = (1 + __tmp_690.value);
    len_ = ctypes.c_int32()
    parvalue = (ctypes.c_char*maxlen)()
    _res_getstrparam = __library__.MSK_getstrparam(self.__nativep,param,maxlen,ctypes.byref(len_),parvalue)
    if _res_getstrparam != 0:
      _,_msg_getstrparam = self.__getlasterror(_res_getstrparam)
      raise Error(rescode(_res_getstrparam),_msg_getstrparam)
    len = len_.value
    return (len_.value,parvalue.value.decode("utf-8",errors="ignore"))
  def getstrparam(self,*args,**kwds):
    """
    Obtains the value of a string parameter.
  
    getstrparam() -> (len,parvalue)
      [len : int32]  The length of the parameter value.  
      [parvalue : str]  If this is not a null pointer, the parameter value is stored here.  
    """
    return self.__getstrparam_2(*args,**kwds)
  def __getstrparamlen_2(self,param : sparam):
    len_ = ctypes.c_int32()
    _res_getstrparamlen = __library__.MSK_getstrparamlen(self.__nativep,param,ctypes.byref(len_))
    if _res_getstrparamlen != 0:
      _,_msg_getstrparamlen = self.__getlasterror(_res_getstrparamlen)
      raise Error(rescode(_res_getstrparamlen),_msg_getstrparamlen)
    len = len_.value
    return (len_.value)
  def getstrparamlen(self,*args,**kwds):
    """
    Obtains the length of a string parameter.
  
    getstrparamlen() -> (len)
      [len : int32]  The length of the parameter value.  
    """
    return self.__getstrparamlen_2(*args,**kwds)
  def __gettasknamelen_1(self):
    len_ = ctypes.c_int32()
    _res_gettasknamelen = __library__.MSK_gettasknamelen(self.__nativep,ctypes.byref(len_))
    if _res_gettasknamelen != 0:
      _,_msg_gettasknamelen = self.__getlasterror(_res_gettasknamelen)
      raise Error(rescode(_res_gettasknamelen),_msg_gettasknamelen)
    len = len_.value
    return (len_.value)
  def gettasknamelen(self,*args,**kwds):
    """
    Obtains the length the task name.
  
    gettasknamelen() -> (len)
      [len : int32]  Returns the length of the task name.  
    """
    return self.__gettasknamelen_1(*args,**kwds)
  def __gettaskname_1(self):
    __tmp_694 = ctypes.c_int32()
    _res_gettasknamelen = __library__.MSK_gettasknamelen(self.__nativep,ctypes.byref(__tmp_694))
    if _res_gettasknamelen != 0:
      _,_msg_gettasknamelen = self.__getlasterror(_res_gettasknamelen)
      raise Error(rescode(_res_gettasknamelen),_msg_gettasknamelen)
    sizetaskname = (1 + __tmp_694.value);
    taskname = (ctypes.c_char*sizetaskname)()
    _res_gettaskname = __library__.MSK_gettaskname(self.__nativep,sizetaskname,taskname)
    if _res_gettaskname != 0:
      _,_msg_gettaskname = self.__getlasterror(_res_gettaskname)
      raise Error(rescode(_res_gettaskname),_msg_gettaskname)
    return (taskname.value.decode("utf-8",errors="ignore"))
  def gettaskname(self,*args,**kwds):
    """
    Obtains the task name.
  
    gettaskname() -> (taskname)
      [taskname : str]  Returns the task name.  
    """
    return self.__gettaskname_1(*args,**kwds)
  def __getvartype_2(self,j):
    vartype = ctypes.c_int()
    _res_getvartype = __library__.MSK_getvartype(self.__nativep,j,ctypes.byref(vartype))
    if _res_getvartype != 0:
      _,_msg_getvartype = self.__getlasterror(_res_getvartype)
      raise Error(rescode(_res_getvartype),_msg_getvartype)
    return (variabletype(vartype.value))
  def getvartype(self,*args,**kwds):
    """
    Gets the variable type of one variable.
  
    getvartype(j) -> (vartype)
      [j : int32]  Index of the variable.  
      [vartype : mosek.variabletype]  Variable type of variable index j.  
    """
    return self.__getvartype_2(*args,**kwds)
  def __getvartypelist_3(self,subj,vartype):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    if vartype is None:
      _tmparray_vartype_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(vartype) < num:
        raise ValueError("argument vartype is too short")
      _tmparray_vartype_ = (ctypes.c_int32*len(vartype))()
    _res_getvartypelist = __library__.MSK_getvartypelist(self.__nativep,num,_tmparray_subj_,_tmparray_vartype_)
    if _res_getvartypelist != 0:
      _,_msg_getvartypelist = self.__getlasterror(_res_getvartypelist)
      raise Error(rescode(_res_getvartypelist),_msg_getvartypelist)
    if vartype is not None:
      for __tmp_698,__tmp_699 in enumerate(_tmparray_vartype_):
        vartype[__tmp_698] = variabletype(__tmp_699)
  def __getvartypelist_2(self,subj):
    num = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    _tmparray_vartype_ = (ctypes.c_int32*num)()
    _res_getvartypelist = __library__.MSK_getvartypelist(self.__nativep,num,_tmparray_subj_,_tmparray_vartype_)
    if _res_getvartypelist != 0:
      _,_msg_getvartypelist = self.__getlasterror(_res_getvartypelist)
      raise Error(rescode(_res_getvartypelist),_msg_getvartypelist)
    vartype = list(map(lambda _i: variabletype(_i),_tmparray_vartype_))
    return (vartype)
  def getvartypelist(self,*args,**kwds):
    """
    Obtains the variable type for one or more variables.
  
    getvartypelist(subj,vartype)
    getvartypelist(subj) -> (vartype)
      [subj : array(int32)]  A list of variable indexes.  
      [vartype : array(mosek.variabletype)]  Returns the variables types corresponding the variable indexes requested.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getvartypelist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getvartypelist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __inputdata64_15(self,maxnumcon,maxnumvar,c,cfix,aptrb,aptre,asub,aval,bkc,blc,buc,bkx,blx,bux):
    numcon = min(len(buc) if buc is not None else 0,len(blc) if blc is not None else 0,len(bkc) if bkc is not None else 0)
    numvar = min(len(c) if c is not None else 0,len(bux) if bux is not None else 0,len(blx) if blx is not None else 0,len(bkx) if bkx is not None else 0,len(aptrb) if aptrb is not None else 0,len(aptre) if aptre is not None else 0)
    copyback_c = False
    if c is None:
      c_ = None
      _tmparray_c_ = None
    else:
      _tmparray_c_ = (ctypes.c_double*len(c))(*c)
    copyback_aptrb = False
    if aptrb is None:
      aptrb_ = None
      _tmparray_aptrb_ = None
    else:
      _tmparray_aptrb_ = (ctypes.c_int64*len(aptrb))(*aptrb)
    copyback_aptre = False
    if aptre is None:
      aptre_ = None
      _tmparray_aptre_ = None
    else:
      _tmparray_aptre_ = (ctypes.c_int64*len(aptre))(*aptre)
    copyback_asub = False
    if asub is None:
      asub_ = None
      _tmparray_asub_ = None
    else:
      _tmparray_asub_ = (ctypes.c_int32*len(asub))(*asub)
    copyback_aval = False
    if aval is None:
      aval_ = None
      _tmparray_aval_ = None
    else:
      _tmparray_aval_ = (ctypes.c_double*len(aval))(*aval)
    if bkc is None:
      _tmparray_bkc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_bkc_ = (ctypes.c_int32*len(bkc))(*bkc)
    copyback_blc = False
    if blc is None:
      blc_ = None
      _tmparray_blc_ = None
    else:
      _tmparray_blc_ = (ctypes.c_double*len(blc))(*blc)
    copyback_buc = False
    if buc is None:
      buc_ = None
      _tmparray_buc_ = None
    else:
      _tmparray_buc_ = (ctypes.c_double*len(buc))(*buc)
    if bkx is None:
      _tmparray_bkx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_bkx_ = (ctypes.c_int32*len(bkx))(*bkx)
    copyback_blx = False
    if blx is None:
      blx_ = None
      _tmparray_blx_ = None
    else:
      _tmparray_blx_ = (ctypes.c_double*len(blx))(*blx)
    copyback_bux = False
    if bux is None:
      bux_ = None
      _tmparray_bux_ = None
    else:
      _tmparray_bux_ = (ctypes.c_double*len(bux))(*bux)
    _res_inputdata64 = __library__.MSK_inputdata64(self.__nativep,maxnumcon,maxnumvar,numcon,numvar,_tmparray_c_,cfix,_tmparray_aptrb_,_tmparray_aptre_,_tmparray_asub_,_tmparray_aval_,_tmparray_bkc_,_tmparray_blc_,_tmparray_buc_,_tmparray_bkx_,_tmparray_blx_,_tmparray_bux_)
    if _res_inputdata64 != 0:
      _,_msg_inputdata64 = self.__getlasterror(_res_inputdata64)
      raise Error(rescode(_res_inputdata64),_msg_inputdata64)
  def inputdata(self,*args,**kwds):
    """
    Input the linear part of an optimization task in one function call.
  
    inputdata(maxnumcon,
              maxnumvar,
              c,
              cfix,
              aptrb,
              aptre,
              asub,
              aval,
              bkc,
              blc,
              buc,
              bkx,
              blx,
              bux)
      [aptrb : array(int64)]  Row or column start pointers.  
      [aptre : array(int64)]  Row or column end pointers.  
      [asub : array(int32)]  Coefficient subscripts.  
      [aval : array(float64)]  Coefficient values.  
      [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
      [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
      [blc : array(float64)]  Lower bounds for the constraints.  
      [blx : array(float64)]  Lower bounds for the variables.  
      [buc : array(float64)]  Upper bounds for the constraints.  
      [bux : array(float64)]  Upper bounds for the variables.  
      [c : array(float64)]  Linear terms of the objective as a dense vector. The length is the number of variables.  
      [cfix : float64]  Fixed term in the objective.  
      [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
      [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
    """
    return self.__inputdata64_15(*args,**kwds)
  def __isdouparname_2(self,parname):
    param = ctypes.c_int()
    _res_isdouparname = __library__.MSK_isdouparname(self.__nativep,parname.encode("UTF-8"),ctypes.byref(param))
    if _res_isdouparname != 0:
      _,_msg_isdouparname = self.__getlasterror(_res_isdouparname)
      raise Error(rescode(_res_isdouparname),_msg_isdouparname)
    return (dparam(param.value))
  def isdouparname(self,*args,**kwds):
    """
    Checks a double parameter name.
  
    isdouparname(parname) -> (param)
      [param : mosek.dparam]  Returns the parameter corresponding to the name, if one exists.  
      [parname : str]  Parameter name.  
    """
    return self.__isdouparname_2(*args,**kwds)
  def __isintparname_2(self,parname):
    param = ctypes.c_int()
    _res_isintparname = __library__.MSK_isintparname(self.__nativep,parname.encode("UTF-8"),ctypes.byref(param))
    if _res_isintparname != 0:
      _,_msg_isintparname = self.__getlasterror(_res_isintparname)
      raise Error(rescode(_res_isintparname),_msg_isintparname)
    return (iparam(param.value))
  def isintparname(self,*args,**kwds):
    """
    Checks an integer parameter name.
  
    isintparname(parname) -> (param)
      [param : mosek.iparam]  Returns the parameter corresponding to the name, if one exists.  
      [parname : str]  Parameter name.  
    """
    return self.__isintparname_2(*args,**kwds)
  def __isstrparname_2(self,parname):
    param = ctypes.c_int()
    _res_isstrparname = __library__.MSK_isstrparname(self.__nativep,parname.encode("UTF-8"),ctypes.byref(param))
    if _res_isstrparname != 0:
      _,_msg_isstrparname = self.__getlasterror(_res_isstrparname)
      raise Error(rescode(_res_isstrparname),_msg_isstrparname)
    return (sparam(param.value))
  def isstrparname(self,*args,**kwds):
    """
    Checks a string parameter name.
  
    isstrparname(parname) -> (param)
      [param : mosek.sparam]  Returns the parameter corresponding to the name, if one exists.  
      [parname : str]  Parameter name.  
    """
    return self.__isstrparname_2(*args,**kwds)
  def __linkfiletotaskstream_4(self,whichstream : streamtype,filename,append):
    _res_linkfiletotaskstream = __library__.MSK_linkfiletotaskstream(self.__nativep,whichstream,filename.encode("UTF-8"),append)
    if _res_linkfiletotaskstream != 0:
      _,_msg_linkfiletotaskstream = self.__getlasterror(_res_linkfiletotaskstream)
      raise Error(rescode(_res_linkfiletotaskstream),_msg_linkfiletotaskstream)
  def linkfiletostream(self,*args,**kwds):
    """
    Directs all output from a task stream to a file.
  
    linkfiletostream(filename,append)
      [append : int32]  If this argument is 0 the output file will be overwritten, otherwise it will be appended to.  
      [filename : str]  A valid file name.  
    """
    return self.__linkfiletotaskstream_4(*args,**kwds)
  def __primalrepair_5(self,wlc,wuc,wlx,wux):
    copyback_wlc = False
    if wlc is None:
      wlc_ = None
      _tmparray_wlc_ = None
    else:
      __tmp_708 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_708))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(wlc) < int(__tmp_708.value):
        raise ValueError("argument wlc is too short")
      _tmparray_wlc_ = (ctypes.c_double*len(wlc))(*wlc)
    copyback_wuc = False
    if wuc is None:
      wuc_ = None
      _tmparray_wuc_ = None
    else:
      __tmp_710 = ctypes.c_int32()
      _res_getnumcon = __library__.MSK_getnumcon(self.__nativep,ctypes.byref(__tmp_710))
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      if len(wuc) < int(__tmp_710.value):
        raise ValueError("argument wuc is too short")
      _tmparray_wuc_ = (ctypes.c_double*len(wuc))(*wuc)
    copyback_wlx = False
    if wlx is None:
      wlx_ = None
      _tmparray_wlx_ = None
    else:
      __tmp_712 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_712))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(wlx) < int(__tmp_712.value):
        raise ValueError("argument wlx is too short")
      _tmparray_wlx_ = (ctypes.c_double*len(wlx))(*wlx)
    copyback_wux = False
    if wux is None:
      wux_ = None
      _tmparray_wux_ = None
    else:
      __tmp_714 = ctypes.c_int32()
      _res_getnumvar = __library__.MSK_getnumvar(self.__nativep,ctypes.byref(__tmp_714))
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      if len(wux) < int(__tmp_714.value):
        raise ValueError("argument wux is too short")
      _tmparray_wux_ = (ctypes.c_double*len(wux))(*wux)
    _res_primalrepair = __library__.MSK_primalrepair(self.__nativep,_tmparray_wlc_,_tmparray_wuc_,_tmparray_wlx_,_tmparray_wux_)
    if _res_primalrepair != 0:
      _,_msg_primalrepair = self.__getlasterror(_res_primalrepair)
      raise Error(rescode(_res_primalrepair),_msg_primalrepair)
  def primalrepair(self,*args,**kwds):
    """
    Repairs a primal infeasible optimization problem by adjusting the bounds on the constraints and variables.
  
    primalrepair(wlc,wuc,wlx,wux)
      [wlc : array(float64)]  Weights associated with relaxing lower bounds on the constraints.  
      [wlx : array(float64)]  Weights associated with relaxing the lower bounds of the variables.  
      [wuc : array(float64)]  Weights associated with relaxing the upper bound on the constraints.  
      [wux : array(float64)]  Weights associated with relaxing the upper bounds of variables.  
    """
    return self.__primalrepair_5(*args,**kwds)
  def __infeasibilityreport_3(self,whichstream : streamtype,whichsol : soltype):
    _res_infeasibilityreport = __library__.MSK_infeasibilityreport(self.__nativep,whichstream,whichsol)
    if _res_infeasibilityreport != 0:
      _,_msg_infeasibilityreport = self.__getlasterror(_res_infeasibilityreport)
      raise Error(rescode(_res_infeasibilityreport),_msg_infeasibilityreport)
  def infeasibilityreport(self,*args,**kwds):
    """
    Prints the infeasibility report to an output stream.
  
    infeasibilityreport()
    """
    return self.__infeasibilityreport_3(*args,**kwds)
  def __toconic_1(self):
    _res_toconic = __library__.MSK_toconic(self.__nativep)
    if _res_toconic != 0:
      _,_msg_toconic = self.__getlasterror(_res_toconic)
      raise Error(rescode(_res_toconic),_msg_toconic)
  def toconic(self,*args,**kwds):
    """
    In-place reformulation of a QCQO to a conic quadratic problem.
  
    toconic()
    """
    return self.__toconic_1(*args,**kwds)
  def __optimizetrm_1(self):
    trmcode = ctypes.c_int()
    _res_optimizetrm = __library__.MSK_optimizetrm(self.__nativep,ctypes.byref(trmcode))
    if _res_optimizetrm != 0:
      _,_msg_optimizetrm = self.__getlasterror(_res_optimizetrm)
      raise Error(rescode(_res_optimizetrm),_msg_optimizetrm)
    return (rescode(trmcode.value))
  def optimize(self,*args,**kwds):
    """
    Optimizes the problem.
  
    optimize() -> (trmcode)
      [trmcode : mosek.rescode]  Is either OK or a termination response code.  
    """
    return self.__optimizetrm_1(*args,**kwds)
  def __commitchanges_1(self):
    _res_commitchanges = __library__.MSK_commitchanges(self.__nativep)
    if _res_commitchanges != 0:
      _,_msg_commitchanges = self.__getlasterror(_res_commitchanges)
      raise Error(rescode(_res_commitchanges),_msg_commitchanges)
  def commitchanges(self,*args,**kwds):
    """
    Commits all cached problem changes.
  
    commitchanges()
    """
    return self.__commitchanges_1(*args,**kwds)
  def __getatruncatetol_2(self,tolzero):
    copyback_tolzero = False
    if tolzero is None:
      tolzero_ = None
      _tmparray_tolzero_ = None
    else:
      if len(tolzero) < int(1):
        raise ValueError("argument tolzero is too short")
      _tmparray_tolzero_ = (ctypes.c_double*len(tolzero))(*tolzero)
    _res_getatruncatetol = __library__.MSK_getatruncatetol(self.__nativep,_tmparray_tolzero_)
    if _res_getatruncatetol != 0:
      _,_msg_getatruncatetol = self.__getlasterror(_res_getatruncatetol)
      raise Error(rescode(_res_getatruncatetol),_msg_getatruncatetol)
    if tolzero is not None:
      for __tmp_724,__tmp_725 in enumerate(_tmparray_tolzero_):
        tolzero[__tmp_724] = __tmp_725
  def __getatruncatetol_1(self):
    tolzero = numpy.zeros(1,numpy.float64)
    _res_getatruncatetol = __library__.MSK_getatruncatetol(self.__nativep,ctypes.cast(tolzero.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getatruncatetol != 0:
      _,_msg_getatruncatetol = self.__getlasterror(_res_getatruncatetol)
      raise Error(rescode(_res_getatruncatetol),_msg_getatruncatetol)
    return (tolzero)
  def getatruncatetol(self,*args,**kwds):
    """
    Gets the current A matrix truncation threshold.
  
    getatruncatetol(tolzero)
    getatruncatetol() -> (tolzero)
      [tolzero : array(float64)]  Truncation tolerance.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__getatruncatetol_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getatruncatetol_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putatruncatetol_2(self,tolzero):
    _res_putatruncatetol = __library__.MSK_putatruncatetol(self.__nativep,tolzero)
    if _res_putatruncatetol != 0:
      _,_msg_putatruncatetol = self.__getlasterror(_res_putatruncatetol)
      raise Error(rescode(_res_putatruncatetol),_msg_putatruncatetol)
  def putatruncatetol(self,*args,**kwds):
    """
    Truncates all elements in A below a certain tolerance to zero.
  
    putatruncatetol(tolzero)
      [tolzero : float64]  Truncation tolerance.  
    """
    return self.__putatruncatetol_2(*args,**kwds)
  def __putaij_4(self,i,j,aij):
    _res_putaij = __library__.MSK_putaij(self.__nativep,i,j,aij)
    if _res_putaij != 0:
      _,_msg_putaij = self.__getlasterror(_res_putaij)
      raise Error(rescode(_res_putaij),_msg_putaij)
  def putaij(self,*args,**kwds):
    """
    Changes a single value in the linear coefficient matrix.
  
    putaij(i,j,aij)
      [aij : float64]  New coefficient.  
      [i : int32]  Constraint (row) index.  
      [j : int32]  Variable (column) index.  
    """
    return self.__putaij_4(*args,**kwds)
  def __putaijlist64_4(self,subi,subj,valij):
    num = min(len(subi) if subi is not None else 0,len(subj) if subj is not None else 0,len(valij) if valij is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valij = False
    if valij is None:
      valij_ = None
      _tmparray_valij_ = None
    else:
      _tmparray_valij_ = (ctypes.c_double*len(valij))(*valij)
    _res_putaijlist64 = __library__.MSK_putaijlist64(self.__nativep,num,_tmparray_subi_,_tmparray_subj_,_tmparray_valij_)
    if _res_putaijlist64 != 0:
      _,_msg_putaijlist64 = self.__getlasterror(_res_putaijlist64)
      raise Error(rescode(_res_putaijlist64),_msg_putaijlist64)
  def putaijlist(self,*args,**kwds):
    """
    Changes one or more coefficients in the linear constraint matrix.
  
    putaijlist(subi,subj,valij)
      [subi : array(int32)]  Constraint (row) indices.  
      [subj : array(int32)]  Variable (column) indices.  
      [valij : array(float64)]  New coefficient values.  
    """
    return self.__putaijlist64_4(*args,**kwds)
  def __putacol_4(self,j,subj,valj):
    nzj = min(len(subj) if subj is not None else 0,len(valj) if valj is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valj = False
    if valj is None:
      valj_ = None
      _tmparray_valj_ = None
    else:
      _tmparray_valj_ = (ctypes.c_double*len(valj))(*valj)
    _res_putacol = __library__.MSK_putacol(self.__nativep,j,nzj,_tmparray_subj_,_tmparray_valj_)
    if _res_putacol != 0:
      _,_msg_putacol = self.__getlasterror(_res_putacol)
      raise Error(rescode(_res_putacol),_msg_putacol)
  def putacol(self,*args,**kwds):
    """
    Replaces all elements in one column of the linear constraint matrix.
  
    putacol(j,subj,valj)
      [j : int32]  Column index.  
      [subj : array(int32)]  Row indexes of non-zero values in column.  
      [valj : array(float64)]  New non-zero values of column.  
    """
    return self.__putacol_4(*args,**kwds)
  def __putarow_4(self,i,subi,vali):
    nzi = min(len(subi) if subi is not None else 0,len(vali) if vali is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_vali = False
    if vali is None:
      vali_ = None
      _tmparray_vali_ = None
    else:
      _tmparray_vali_ = (ctypes.c_double*len(vali))(*vali)
    _res_putarow = __library__.MSK_putarow(self.__nativep,i,nzi,_tmparray_subi_,_tmparray_vali_)
    if _res_putarow != 0:
      _,_msg_putarow = self.__getlasterror(_res_putarow)
      raise Error(rescode(_res_putarow),_msg_putarow)
  def putarow(self,*args,**kwds):
    """
    Replaces all elements in one row of the linear constraint matrix.
  
    putarow(i,subi,vali)
      [i : int32]  Row index.  
      [subi : array(int32)]  Column indexes of non-zero values in row.  
      [vali : array(float64)]  New non-zero values of row.  
    """
    return self.__putarow_4(*args,**kwds)
  def __putarowslice64_7(self,first,last,ptrb,ptre,asub,aval):
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      if len(ptrb) < int((last - first)):
        raise ValueError("argument ptrb is too short")
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      if len(ptre) < int((last - first)):
        raise ValueError("argument ptre is too short")
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_asub = False
    if asub is None:
      asub_ = None
      _tmparray_asub_ = None
    else:
      _tmparray_asub_ = (ctypes.c_int32*len(asub))(*asub)
    copyback_aval = False
    if aval is None:
      aval_ = None
      _tmparray_aval_ = None
    else:
      _tmparray_aval_ = (ctypes.c_double*len(aval))(*aval)
    _res_putarowslice64 = __library__.MSK_putarowslice64(self.__nativep,first,last,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_asub_,_tmparray_aval_)
    if _res_putarowslice64 != 0:
      _,_msg_putarowslice64 = self.__getlasterror(_res_putarowslice64)
      raise Error(rescode(_res_putarowslice64),_msg_putarowslice64)
  def putarowslice(self,*args,**kwds):
    """
    Replaces all elements in several rows the linear constraint matrix.
  
    putarowslice(first,last,ptrb,ptre,asub,aval)
      [asub : array(int32)]  Column indexes of new elements.  
      [aval : array(float64)]  Coefficient values.  
      [first : int32]  First row in the slice.  
      [last : int32]  Last row plus one in the slice.  
      [ptrb : array(int64)]  Array of pointers to the first element in the rows.  
      [ptre : array(int64)]  Array of pointers to the last element plus one in the rows.  
    """
    return self.__putarowslice64_7(*args,**kwds)
  def __putarowlist64_6(self,sub,ptrb,ptre,asub,aval):
    num = min(len(sub) if sub is not None else 0,len(ptrb) if ptrb is not None else 0,len(ptre) if ptre is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_asub = False
    if asub is None:
      asub_ = None
      _tmparray_asub_ = None
    else:
      _tmparray_asub_ = (ctypes.c_int32*len(asub))(*asub)
    copyback_aval = False
    if aval is None:
      aval_ = None
      _tmparray_aval_ = None
    else:
      _tmparray_aval_ = (ctypes.c_double*len(aval))(*aval)
    _res_putarowlist64 = __library__.MSK_putarowlist64(self.__nativep,num,_tmparray_sub_,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_asub_,_tmparray_aval_)
    if _res_putarowlist64 != 0:
      _,_msg_putarowlist64 = self.__getlasterror(_res_putarowlist64)
      raise Error(rescode(_res_putarowlist64),_msg_putarowlist64)
  def putarowlist(self,*args,**kwds):
    """
    Replaces all elements in several rows of the linear constraint matrix.
  
    putarowlist(sub,ptrb,ptre,asub,aval)
      [asub : array(int32)]  Variable indexes.  
      [aval : array(float64)]  Coefficient values.  
      [ptrb : array(int64)]  Array of pointers to the first element in the rows.  
      [ptre : array(int64)]  Array of pointers to the last element plus one in the rows.  
      [sub : array(int32)]  Indexes of rows or columns that should be replaced.  
    """
    return self.__putarowlist64_6(*args,**kwds)
  def __putacolslice64_7(self,first,last,ptrb,ptre,asub,aval):
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_asub = False
    if asub is None:
      asub_ = None
      _tmparray_asub_ = None
    else:
      _tmparray_asub_ = (ctypes.c_int32*len(asub))(*asub)
    copyback_aval = False
    if aval is None:
      aval_ = None
      _tmparray_aval_ = None
    else:
      _tmparray_aval_ = (ctypes.c_double*len(aval))(*aval)
    _res_putacolslice64 = __library__.MSK_putacolslice64(self.__nativep,first,last,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_asub_,_tmparray_aval_)
    if _res_putacolslice64 != 0:
      _,_msg_putacolslice64 = self.__getlasterror(_res_putacolslice64)
      raise Error(rescode(_res_putacolslice64),_msg_putacolslice64)
  def putacolslice(self,*args,**kwds):
    """
    Replaces all elements in a sequence of columns the linear constraint matrix.
  
    putacolslice(first,last,ptrb,ptre,asub,aval)
      [asub : array(int32)]  Row indexes  
      [aval : array(float64)]  Coefficient values.  
      [first : int32]  First column in the slice.  
      [last : int32]  Last column plus one in the slice.  
      [ptrb : array(int64)]  Array of pointers to the first element in the columns.  
      [ptre : array(int64)]  Array of pointers to the last element plus one in the columns.  
    """
    return self.__putacolslice64_7(*args,**kwds)
  def __putacollist64_6(self,sub,ptrb,ptre,asub,aval):
    num = min(len(sub) if sub is not None else 0,len(ptrb) if ptrb is not None else 0,len(ptre) if ptre is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_asub = False
    if asub is None:
      asub_ = None
      _tmparray_asub_ = None
    else:
      _tmparray_asub_ = (ctypes.c_int32*len(asub))(*asub)
    copyback_aval = False
    if aval is None:
      aval_ = None
      _tmparray_aval_ = None
    else:
      _tmparray_aval_ = (ctypes.c_double*len(aval))(*aval)
    _res_putacollist64 = __library__.MSK_putacollist64(self.__nativep,num,_tmparray_sub_,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_asub_,_tmparray_aval_)
    if _res_putacollist64 != 0:
      _,_msg_putacollist64 = self.__getlasterror(_res_putacollist64)
      raise Error(rescode(_res_putacollist64),_msg_putacollist64)
  def putacollist(self,*args,**kwds):
    """
    Replaces all elements in several columns the linear constraint matrix.
  
    putacollist(sub,ptrb,ptre,asub,aval)
      [asub : array(int32)]  Row indexes  
      [aval : array(float64)]  Coefficient values.  
      [ptrb : array(int64)]  Array of pointers to the first element in the columns.  
      [ptre : array(int64)]  Array of pointers to the last element plus one in the columns.  
      [sub : array(int32)]  Indexes of columns that should be replaced.  
    """
    return self.__putacollist64_6(*args,**kwds)
  def __putbaraij_5(self,i,j,sub,weights):
    num = min(len(sub) if sub is not None else 0,len(weights) if weights is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_putbaraij = __library__.MSK_putbaraij(self.__nativep,i,j,num,_tmparray_sub_,_tmparray_weights_)
    if _res_putbaraij != 0:
      _,_msg_putbaraij = self.__getlasterror(_res_putbaraij)
      raise Error(rescode(_res_putbaraij),_msg_putbaraij)
  def putbaraij(self,*args,**kwds):
    """
    Inputs an element of barA.
  
    putbaraij(i,j,sub,weights)
      [i : int32]  Row index of barA.  
      [j : int32]  Column index of barA.  
      [sub : array(int64)]  Element indexes in matrix storage.  
      [weights : array(float64)]  Weights in the weighted sum.  
    """
    return self.__putbaraij_5(*args,**kwds)
  def __putbaraijlist_7(self,subi,subj,alphaptrb,alphaptre,matidx,weights):
    num = min(len(subi) if subi is not None else 0,len(subj) if subj is not None else 0,len(alphaptrb) if alphaptrb is not None else 0,len(alphaptre) if alphaptre is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_alphaptrb = False
    if alphaptrb is None:
      alphaptrb_ = None
      _tmparray_alphaptrb_ = None
    else:
      _tmparray_alphaptrb_ = (ctypes.c_int64*len(alphaptrb))(*alphaptrb)
    copyback_alphaptre = False
    if alphaptre is None:
      alphaptre_ = None
      _tmparray_alphaptre_ = None
    else:
      _tmparray_alphaptre_ = (ctypes.c_int64*len(alphaptre))(*alphaptre)
    copyback_matidx = False
    if matidx is None:
      matidx_ = None
      _tmparray_matidx_ = None
    else:
      _tmparray_matidx_ = (ctypes.c_int64*len(matidx))(*matidx)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_putbaraijlist = __library__.MSK_putbaraijlist(self.__nativep,num,_tmparray_subi_,_tmparray_subj_,_tmparray_alphaptrb_,_tmparray_alphaptre_,_tmparray_matidx_,_tmparray_weights_)
    if _res_putbaraijlist != 0:
      _,_msg_putbaraijlist = self.__getlasterror(_res_putbaraijlist)
      raise Error(rescode(_res_putbaraijlist),_msg_putbaraijlist)
  def putbaraijlist(self,*args,**kwds):
    """
    Inputs list of elements of barA.
  
    putbaraijlist(subi,
                  subj,
                  alphaptrb,
                  alphaptre,
                  matidx,
                  weights)
      [alphaptrb : array(int64)]  Start entries for terms in the weighted sum.  
      [alphaptre : array(int64)]  End entries for terms in the weighted sum.  
      [matidx : array(int64)]  Element indexes in matrix storage.  
      [subi : array(int32)]  Row index of barA.  
      [subj : array(int32)]  Column index of barA.  
      [weights : array(float64)]  Weights in the weighted sum.  
    """
    return self.__putbaraijlist_7(*args,**kwds)
  def __putbararowlist_8(self,subi,ptrb,ptre,subj,nummat,matidx,weights):
    num = min(len(subi) if subi is not None else 0,len(ptrb) if ptrb is not None else 0,len(ptre) if ptre is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_ptrb = False
    if ptrb is None:
      ptrb_ = None
      _tmparray_ptrb_ = None
    else:
      _tmparray_ptrb_ = (ctypes.c_int64*len(ptrb))(*ptrb)
    copyback_ptre = False
    if ptre is None:
      ptre_ = None
      _tmparray_ptre_ = None
    else:
      _tmparray_ptre_ = (ctypes.c_int64*len(ptre))(*ptre)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_nummat = False
    if nummat is None:
      nummat_ = None
      _tmparray_nummat_ = None
    else:
      if len(nummat) < int(len(subj)):
        raise ValueError("argument nummat is too short")
      _tmparray_nummat_ = (ctypes.c_int64*len(nummat))(*nummat)
    copyback_matidx = False
    if matidx is None:
      matidx_ = None
      _tmparray_matidx_ = None
    else:
      __tmp_727 = sum(nummat)
      if len(matidx) < int(__tmp_727):
        raise ValueError("argument matidx is too short")
      _tmparray_matidx_ = (ctypes.c_int64*len(matidx))(*matidx)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      __tmp_728 = sum(nummat)
      if len(weights) < int(__tmp_728):
        raise ValueError("argument weights is too short")
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_putbararowlist = __library__.MSK_putbararowlist(self.__nativep,num,_tmparray_subi_,_tmparray_ptrb_,_tmparray_ptre_,_tmparray_subj_,_tmparray_nummat_,_tmparray_matidx_,_tmparray_weights_)
    if _res_putbararowlist != 0:
      _,_msg_putbararowlist = self.__getlasterror(_res_putbararowlist)
      raise Error(rescode(_res_putbararowlist),_msg_putbararowlist)
  def putbararowlist(self,*args,**kwds):
    """
    Replace a set of rows of barA
  
    putbararowlist(subi,
                   ptrb,
                   ptre,
                   subj,
                   nummat,
                   matidx,
                   weights)
      [matidx : array(int64)]  Matrix indexes for weighted sum of matrixes.  
      [nummat : array(int64)]  Number of entries in weighted sum of matrixes.  
      [ptrb : array(int64)]  Start of rows in barA.  
      [ptre : array(int64)]  End of rows in barA.  
      [subi : array(int32)]  Row indexes of barA.  
      [subj : array(int32)]  Column index of barA.  
      [weights : array(float64)]  Weights for weighted sum of matrixes.  
    """
    return self.__putbararowlist_8(*args,**kwds)
  def __getnumbarcnz_1(self):
    nz_ = ctypes.c_int64()
    _res_getnumbarcnz = __library__.MSK_getnumbarcnz(self.__nativep,ctypes.byref(nz_))
    if _res_getnumbarcnz != 0:
      _,_msg_getnumbarcnz = self.__getlasterror(_res_getnumbarcnz)
      raise Error(rescode(_res_getnumbarcnz),_msg_getnumbarcnz)
    nz = nz_.value
    return (nz_.value)
  def getnumbarcnz(self,*args,**kwds):
    """
    Obtains the number of nonzero elements in barc.
  
    getnumbarcnz() -> (nz)
      [nz : int64]  The number of nonzero elements in barc.  
    """
    return self.__getnumbarcnz_1(*args,**kwds)
  def __getnumbaranz_1(self):
    nz_ = ctypes.c_int64()
    _res_getnumbaranz = __library__.MSK_getnumbaranz(self.__nativep,ctypes.byref(nz_))
    if _res_getnumbaranz != 0:
      _,_msg_getnumbaranz = self.__getlasterror(_res_getnumbaranz)
      raise Error(rescode(_res_getnumbaranz),_msg_getnumbaranz)
    nz = nz_.value
    return (nz_.value)
  def getnumbaranz(self,*args,**kwds):
    """
    Get the number of nonzero elements in barA.
  
    getnumbaranz() -> (nz)
      [nz : int64]  The number of nonzero block elements in barA.  
    """
    return self.__getnumbaranz_1(*args,**kwds)
  def __getbarcsparsity_2(self,idxj):
    __tmp_731 = ctypes.c_int64()
    _res_getnumbarcnz = __library__.MSK_getnumbarcnz(self.__nativep,ctypes.byref(__tmp_731))
    if _res_getnumbarcnz != 0:
      _,_msg_getnumbarcnz = self.__getlasterror(_res_getnumbarcnz)
      raise Error(rescode(_res_getnumbarcnz),_msg_getnumbarcnz)
    maxnumnz = __tmp_731.value;
    numnz_ = ctypes.c_int64()
    copyback_idxj = False
    if idxj is None:
      idxj_ = None
      _tmparray_idxj_ = None
    else:
      if len(idxj) < int(maxnumnz):
        raise ValueError("argument idxj is too short")
      _tmparray_idxj_ = (ctypes.c_int64*len(idxj))(*idxj)
    _res_getbarcsparsity = __library__.MSK_getbarcsparsity(self.__nativep,maxnumnz,ctypes.byref(numnz_),_tmparray_idxj_)
    if _res_getbarcsparsity != 0:
      _,_msg_getbarcsparsity = self.__getlasterror(_res_getbarcsparsity)
      raise Error(rescode(_res_getbarcsparsity),_msg_getbarcsparsity)
    numnz = numnz_.value
    if idxj is not None:
      for __tmp_733,__tmp_734 in enumerate(_tmparray_idxj_):
        idxj[__tmp_733] = __tmp_734
    return (numnz_.value)
  def __getbarcsparsity_1(self):
    __tmp_735 = ctypes.c_int64()
    _res_getnumbarcnz = __library__.MSK_getnumbarcnz(self.__nativep,ctypes.byref(__tmp_735))
    if _res_getnumbarcnz != 0:
      _,_msg_getnumbarcnz = self.__getlasterror(_res_getnumbarcnz)
      raise Error(rescode(_res_getnumbarcnz),_msg_getnumbarcnz)
    maxnumnz = __tmp_735.value;
    numnz_ = ctypes.c_int64()
    idxj = numpy.zeros(maxnumnz,numpy.int64)
    _res_getbarcsparsity = __library__.MSK_getbarcsparsity(self.__nativep,maxnumnz,ctypes.byref(numnz_),ctypes.cast(idxj.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getbarcsparsity != 0:
      _,_msg_getbarcsparsity = self.__getlasterror(_res_getbarcsparsity)
      raise Error(rescode(_res_getbarcsparsity),_msg_getbarcsparsity)
    numnz = numnz_.value
    return (numnz_.value,idxj)
  def getbarcsparsity(self,*args,**kwds):
    """
    Get the positions of the nonzero elements in barc.
  
    getbarcsparsity(idxj) -> (numnz)
    getbarcsparsity() -> (numnz,idxj)
      [idxj : array(int64)]  Internal positions of the nonzeros elements in barc.  
      [numnz : int64]  Number of nonzero elements in barc.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__getbarcsparsity_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getbarcsparsity_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarasparsity_2(self,idxij):
    __tmp_738 = ctypes.c_int64()
    _res_getnumbaranz = __library__.MSK_getnumbaranz(self.__nativep,ctypes.byref(__tmp_738))
    if _res_getnumbaranz != 0:
      _,_msg_getnumbaranz = self.__getlasterror(_res_getnumbaranz)
      raise Error(rescode(_res_getnumbaranz),_msg_getnumbaranz)
    maxnumnz = __tmp_738.value;
    numnz_ = ctypes.c_int64()
    copyback_idxij = False
    if idxij is None:
      idxij_ = None
      _tmparray_idxij_ = None
    else:
      if len(idxij) < int(maxnumnz):
        raise ValueError("argument idxij is too short")
      _tmparray_idxij_ = (ctypes.c_int64*len(idxij))(*idxij)
    _res_getbarasparsity = __library__.MSK_getbarasparsity(self.__nativep,maxnumnz,ctypes.byref(numnz_),_tmparray_idxij_)
    if _res_getbarasparsity != 0:
      _,_msg_getbarasparsity = self.__getlasterror(_res_getbarasparsity)
      raise Error(rescode(_res_getbarasparsity),_msg_getbarasparsity)
    numnz = numnz_.value
    if idxij is not None:
      for __tmp_740,__tmp_741 in enumerate(_tmparray_idxij_):
        idxij[__tmp_740] = __tmp_741
    return (numnz_.value)
  def __getbarasparsity_1(self):
    __tmp_742 = ctypes.c_int64()
    _res_getnumbaranz = __library__.MSK_getnumbaranz(self.__nativep,ctypes.byref(__tmp_742))
    if _res_getnumbaranz != 0:
      _,_msg_getnumbaranz = self.__getlasterror(_res_getnumbaranz)
      raise Error(rescode(_res_getnumbaranz),_msg_getnumbaranz)
    maxnumnz = __tmp_742.value;
    numnz_ = ctypes.c_int64()
    idxij = numpy.zeros(maxnumnz,numpy.int64)
    _res_getbarasparsity = __library__.MSK_getbarasparsity(self.__nativep,maxnumnz,ctypes.byref(numnz_),ctypes.cast(idxij.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getbarasparsity != 0:
      _,_msg_getbarasparsity = self.__getlasterror(_res_getbarasparsity)
      raise Error(rescode(_res_getbarasparsity),_msg_getbarasparsity)
    numnz = numnz_.value
    return (numnz_.value,idxij)
  def getbarasparsity(self,*args,**kwds):
    """
    Obtains the sparsity pattern of the barA matrix.
  
    getbarasparsity(idxij) -> (numnz)
    getbarasparsity() -> (numnz,idxij)
      [idxij : array(int64)]  Position of each nonzero element in the vector representation of barA.  
      [numnz : int64]  Number of nonzero elements in barA.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__getbarasparsity_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getbarasparsity_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbarcidxinfo_2(self,idx):
    num_ = ctypes.c_int64()
    _res_getbarcidxinfo = __library__.MSK_getbarcidxinfo(self.__nativep,idx,ctypes.byref(num_))
    if _res_getbarcidxinfo != 0:
      _,_msg_getbarcidxinfo = self.__getlasterror(_res_getbarcidxinfo)
      raise Error(rescode(_res_getbarcidxinfo),_msg_getbarcidxinfo)
    num = num_.value
    return (num_.value)
  def getbarcidxinfo(self,*args,**kwds):
    """
    Obtains information about an element in barc.
  
    getbarcidxinfo(idx) -> (num)
      [idx : int64]  Index of the element for which information should be obtained. The value is an index of a symmetric sparse variable.  
      [num : int64]  Number of terms that appear in the weighted sum that forms the requested element.  
    """
    return self.__getbarcidxinfo_2(*args,**kwds)
  def __getbarcidxj_2(self,idx):
    j_ = ctypes.c_int32()
    _res_getbarcidxj = __library__.MSK_getbarcidxj(self.__nativep,idx,ctypes.byref(j_))
    if _res_getbarcidxj != 0:
      _,_msg_getbarcidxj = self.__getlasterror(_res_getbarcidxj)
      raise Error(rescode(_res_getbarcidxj),_msg_getbarcidxj)
    j = j_.value
    return (j_.value)
  def getbarcidxj(self,*args,**kwds):
    """
    Obtains the row index of an element in barc.
  
    getbarcidxj(idx) -> (j)
      [idx : int64]  Index of the element for which information should be obtained.  
      [j : int32]  Row index in barc.  
    """
    return self.__getbarcidxj_2(*args,**kwds)
  def __getbarcidx_4(self,idx,sub,weights):
    __tmp_745 = ctypes.c_int64()
    _res_getbarcidxinfo = __library__.MSK_getbarcidxinfo(self.__nativep,idx,ctypes.byref(__tmp_745))
    if _res_getbarcidxinfo != 0:
      _,_msg_getbarcidxinfo = self.__getlasterror(_res_getbarcidxinfo)
      raise Error(rescode(_res_getbarcidxinfo),_msg_getbarcidxinfo)
    maxnum = __tmp_745.value;
    j_ = ctypes.c_int32()
    num_ = ctypes.c_int64()
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      if len(sub) < int(maxnum):
        raise ValueError("argument sub is too short")
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      if len(weights) < int(maxnum):
        raise ValueError("argument weights is too short")
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_getbarcidx = __library__.MSK_getbarcidx(self.__nativep,idx,maxnum,ctypes.byref(j_),ctypes.byref(num_),_tmparray_sub_,_tmparray_weights_)
    if _res_getbarcidx != 0:
      _,_msg_getbarcidx = self.__getlasterror(_res_getbarcidx)
      raise Error(rescode(_res_getbarcidx),_msg_getbarcidx)
    j = j_.value
    num = num_.value
    if sub is not None:
      for __tmp_747,__tmp_748 in enumerate(_tmparray_sub_):
        sub[__tmp_747] = __tmp_748
    if weights is not None:
      for __tmp_749,__tmp_750 in enumerate(_tmparray_weights_):
        weights[__tmp_749] = __tmp_750
    return (j_.value,num_.value)
  def __getbarcidx_2(self,idx):
    __tmp_751 = ctypes.c_int64()
    _res_getbarcidxinfo = __library__.MSK_getbarcidxinfo(self.__nativep,idx,ctypes.byref(__tmp_751))
    if _res_getbarcidxinfo != 0:
      _,_msg_getbarcidxinfo = self.__getlasterror(_res_getbarcidxinfo)
      raise Error(rescode(_res_getbarcidxinfo),_msg_getbarcidxinfo)
    maxnum = __tmp_751.value;
    j_ = ctypes.c_int32()
    num_ = ctypes.c_int64()
    sub = numpy.zeros(maxnum,numpy.int64)
    weights = numpy.zeros(maxnum,numpy.float64)
    _res_getbarcidx = __library__.MSK_getbarcidx(self.__nativep,idx,maxnum,ctypes.byref(j_),ctypes.byref(num_),ctypes.cast(sub.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(weights.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarcidx != 0:
      _,_msg_getbarcidx = self.__getlasterror(_res_getbarcidx)
      raise Error(rescode(_res_getbarcidx),_msg_getbarcidx)
    j = j_.value
    num = num_.value
    return (j_.value,num_.value,sub,weights)
  def getbarcidx(self,*args,**kwds):
    """
    Obtains information about an element in barc.
  
    getbarcidx(idx,sub,weights) -> (j,num)
    getbarcidx(idx) -> (j,num,sub,weights)
      [idx : int64]  Index of the element for which information should be obtained.  
      [j : int32]  Row index in barc.  
      [num : int64]  Number of terms in the weighted sum.  
      [sub : array(int64)]  Elements appearing the weighted sum.  
      [weights : array(float64)]  Weights of terms in the weighted sum.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getbarcidx_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getbarcidx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getbaraidxinfo_2(self,idx):
    num_ = ctypes.c_int64()
    _res_getbaraidxinfo = __library__.MSK_getbaraidxinfo(self.__nativep,idx,ctypes.byref(num_))
    if _res_getbaraidxinfo != 0:
      _,_msg_getbaraidxinfo = self.__getlasterror(_res_getbaraidxinfo)
      raise Error(rescode(_res_getbaraidxinfo),_msg_getbaraidxinfo)
    num = num_.value
    return (num_.value)
  def getbaraidxinfo(self,*args,**kwds):
    """
    Obtains the number of terms in the weighted sum that form a particular element in barA.
  
    getbaraidxinfo(idx) -> (num)
      [idx : int64]  The internal position of the element for which information should be obtained.  
      [num : int64]  Number of terms in the weighted sum that form the specified element in barA.  
    """
    return self.__getbaraidxinfo_2(*args,**kwds)
  def __getbaraidxij_2(self,idx):
    i_ = ctypes.c_int32()
    j_ = ctypes.c_int32()
    _res_getbaraidxij = __library__.MSK_getbaraidxij(self.__nativep,idx,ctypes.byref(i_),ctypes.byref(j_))
    if _res_getbaraidxij != 0:
      _,_msg_getbaraidxij = self.__getlasterror(_res_getbaraidxij)
      raise Error(rescode(_res_getbaraidxij),_msg_getbaraidxij)
    i = i_.value
    j = j_.value
    return (i_.value,j_.value)
  def getbaraidxij(self,*args,**kwds):
    """
    Obtains information about an element in barA.
  
    getbaraidxij(idx) -> (i,j)
      [i : int32]  Row index of the element at position idx.  
      [idx : int64]  Position of the element in the vectorized form.  
      [j : int32]  Column index of the element at position idx.  
    """
    return self.__getbaraidxij_2(*args,**kwds)
  def __getbaraidx_4(self,idx,sub,weights):
    __tmp_755 = ctypes.c_int64()
    _res_getbaraidxinfo = __library__.MSK_getbaraidxinfo(self.__nativep,idx,ctypes.byref(__tmp_755))
    if _res_getbaraidxinfo != 0:
      _,_msg_getbaraidxinfo = self.__getlasterror(_res_getbaraidxinfo)
      raise Error(rescode(_res_getbaraidxinfo),_msg_getbaraidxinfo)
    maxnum = __tmp_755.value;
    i_ = ctypes.c_int32()
    j_ = ctypes.c_int32()
    num_ = ctypes.c_int64()
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      if len(sub) < int(maxnum):
        raise ValueError("argument sub is too short")
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      if len(weights) < int(maxnum):
        raise ValueError("argument weights is too short")
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_getbaraidx = __library__.MSK_getbaraidx(self.__nativep,idx,maxnum,ctypes.byref(i_),ctypes.byref(j_),ctypes.byref(num_),_tmparray_sub_,_tmparray_weights_)
    if _res_getbaraidx != 0:
      _,_msg_getbaraidx = self.__getlasterror(_res_getbaraidx)
      raise Error(rescode(_res_getbaraidx),_msg_getbaraidx)
    i = i_.value
    j = j_.value
    num = num_.value
    if sub is not None:
      for __tmp_757,__tmp_758 in enumerate(_tmparray_sub_):
        sub[__tmp_757] = __tmp_758
    if weights is not None:
      for __tmp_759,__tmp_760 in enumerate(_tmparray_weights_):
        weights[__tmp_759] = __tmp_760
    return (i_.value,j_.value,num_.value)
  def __getbaraidx_2(self,idx):
    __tmp_761 = ctypes.c_int64()
    _res_getbaraidxinfo = __library__.MSK_getbaraidxinfo(self.__nativep,idx,ctypes.byref(__tmp_761))
    if _res_getbaraidxinfo != 0:
      _,_msg_getbaraidxinfo = self.__getlasterror(_res_getbaraidxinfo)
      raise Error(rescode(_res_getbaraidxinfo),_msg_getbaraidxinfo)
    maxnum = __tmp_761.value;
    i_ = ctypes.c_int32()
    j_ = ctypes.c_int32()
    num_ = ctypes.c_int64()
    sub = numpy.zeros(maxnum,numpy.int64)
    weights = numpy.zeros(maxnum,numpy.float64)
    _res_getbaraidx = __library__.MSK_getbaraidx(self.__nativep,idx,maxnum,ctypes.byref(i_),ctypes.byref(j_),ctypes.byref(num_),ctypes.cast(sub.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(weights.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbaraidx != 0:
      _,_msg_getbaraidx = self.__getlasterror(_res_getbaraidx)
      raise Error(rescode(_res_getbaraidx),_msg_getbaraidx)
    i = i_.value
    j = j_.value
    num = num_.value
    return (i_.value,j_.value,num_.value,sub,weights)
  def getbaraidx(self,*args,**kwds):
    """
    Obtains information about an element in barA.
  
    getbaraidx(idx,sub,weights) -> (i,j,num)
    getbaraidx(idx) -> (i,j,num,sub,weights)
      [i : int32]  Row index of the element at position idx.  
      [idx : int64]  Position of the element in the vectorized form.  
      [j : int32]  Column index of the element at position idx.  
      [num : int64]  Number of terms in weighted sum that forms the element.  
      [sub : array(int64)]  A list indexes of the elements from symmetric matrix storage that appear in the weighted sum.  
      [weights : array(float64)]  The weights associated with each term in the weighted sum.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getbaraidx_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getbaraidx_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getnumbarcblocktriplets_1(self):
    num_ = ctypes.c_int64()
    _res_getnumbarcblocktriplets = __library__.MSK_getnumbarcblocktriplets(self.__nativep,ctypes.byref(num_))
    if _res_getnumbarcblocktriplets != 0:
      _,_msg_getnumbarcblocktriplets = self.__getlasterror(_res_getnumbarcblocktriplets)
      raise Error(rescode(_res_getnumbarcblocktriplets),_msg_getnumbarcblocktriplets)
    num = num_.value
    return (num_.value)
  def getnumbarcblocktriplets(self,*args,**kwds):
    """
    Obtains an upper bound on the number of elements in the block triplet form of barc.
  
    getnumbarcblocktriplets() -> (num)
      [num : int64]  An upper bound on the number of elements in the block triplet form of barc.  
    """
    return self.__getnumbarcblocktriplets_1(*args,**kwds)
  def __putbarcblocktriplet_5(self,subj,subk,subl,valjkl):
    num = min(len(subj) if subj is not None else 0,len(subk) if subk is not None else 0,len(subl) if subl is not None else 0,len(valjkl) if valjkl is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(num):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(num):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(num):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valjkl = False
    if valjkl is None:
      valjkl_ = None
      _tmparray_valjkl_ = None
    else:
      if len(valjkl) < int(num):
        raise ValueError("argument valjkl is too short")
      _tmparray_valjkl_ = (ctypes.c_double*len(valjkl))(*valjkl)
    _res_putbarcblocktriplet = __library__.MSK_putbarcblocktriplet(self.__nativep,num,_tmparray_subj_,_tmparray_subk_,_tmparray_subl_,_tmparray_valjkl_)
    if _res_putbarcblocktriplet != 0:
      _,_msg_putbarcblocktriplet = self.__getlasterror(_res_putbarcblocktriplet)
      raise Error(rescode(_res_putbarcblocktriplet),_msg_putbarcblocktriplet)
  def putbarcblocktriplet(self,*args,**kwds):
    """
    Inputs barC in block triplet form.
  
    putbarcblocktriplet(subj,subk,subl,valjkl)
      [subj : array(int32)]  Symmetric matrix variable index.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valjkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    return self.__putbarcblocktriplet_5(*args,**kwds)
  def __getbarcblocktriplet_5(self,subj,subk,subl,valjkl):
    __tmp_765 = ctypes.c_int64()
    _res_getnumbarcblocktriplets = __library__.MSK_getnumbarcblocktriplets(self.__nativep,ctypes.byref(__tmp_765))
    if _res_getnumbarcblocktriplets != 0:
      _,_msg_getnumbarcblocktriplets = self.__getlasterror(_res_getnumbarcblocktriplets)
      raise Error(rescode(_res_getnumbarcblocktriplets),_msg_getnumbarcblocktriplets)
    maxnum = __tmp_765.value;
    num_ = ctypes.c_int64()
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxnum):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(maxnum):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(maxnum):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valjkl = False
    if valjkl is None:
      valjkl_ = None
      _tmparray_valjkl_ = None
    else:
      if len(valjkl) < int(maxnum):
        raise ValueError("argument valjkl is too short")
      _tmparray_valjkl_ = (ctypes.c_double*len(valjkl))(*valjkl)
    _res_getbarcblocktriplet = __library__.MSK_getbarcblocktriplet(self.__nativep,maxnum,ctypes.byref(num_),_tmparray_subj_,_tmparray_subk_,_tmparray_subl_,_tmparray_valjkl_)
    if _res_getbarcblocktriplet != 0:
      _,_msg_getbarcblocktriplet = self.__getlasterror(_res_getbarcblocktriplet)
      raise Error(rescode(_res_getbarcblocktriplet),_msg_getbarcblocktriplet)
    num = num_.value
    if subj is not None:
      for __tmp_767,__tmp_768 in enumerate(_tmparray_subj_):
        subj[__tmp_767] = __tmp_768
    if subk is not None:
      for __tmp_769,__tmp_770 in enumerate(_tmparray_subk_):
        subk[__tmp_769] = __tmp_770
    if subl is not None:
      for __tmp_771,__tmp_772 in enumerate(_tmparray_subl_):
        subl[__tmp_771] = __tmp_772
    if valjkl is not None:
      for __tmp_773,__tmp_774 in enumerate(_tmparray_valjkl_):
        valjkl[__tmp_773] = __tmp_774
    return (num_.value)
  def __getbarcblocktriplet_1(self):
    __tmp_775 = ctypes.c_int64()
    _res_getnumbarcblocktriplets = __library__.MSK_getnumbarcblocktriplets(self.__nativep,ctypes.byref(__tmp_775))
    if _res_getnumbarcblocktriplets != 0:
      _,_msg_getnumbarcblocktriplets = self.__getlasterror(_res_getnumbarcblocktriplets)
      raise Error(rescode(_res_getnumbarcblocktriplets),_msg_getnumbarcblocktriplets)
    maxnum = __tmp_775.value;
    num_ = ctypes.c_int64()
    subj = numpy.zeros(maxnum,numpy.int32)
    subk = numpy.zeros(maxnum,numpy.int32)
    subl = numpy.zeros(maxnum,numpy.int32)
    valjkl = numpy.zeros(maxnum,numpy.float64)
    _res_getbarcblocktriplet = __library__.MSK_getbarcblocktriplet(self.__nativep,maxnum,ctypes.byref(num_),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subk.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subl.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(valjkl.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarcblocktriplet != 0:
      _,_msg_getbarcblocktriplet = self.__getlasterror(_res_getbarcblocktriplet)
      raise Error(rescode(_res_getbarcblocktriplet),_msg_getbarcblocktriplet)
    num = num_.value
    return (num_.value,subj,subk,subl,valjkl)
  def getbarcblocktriplet(self,*args,**kwds):
    """
    Obtains barC in block triplet form.
  
    getbarcblocktriplet(subj,subk,subl,valjkl) -> (num)
    getbarcblocktriplet() -> (num,subj,subk,subl,valjkl)
      [num : int64]  Number of elements in the block triplet form.  
      [subj : array(int32)]  Symmetric matrix variable index.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valjkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getbarcblocktriplet_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getbarcblocktriplet_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putbarablocktriplet_6(self,subi,subj,subk,subl,valijkl):
    num = min(len(subj) if subj is not None else 0,len(subk) if subk is not None else 0,len(subl) if subl is not None else 0,len(valijkl) if valijkl is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(num):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(num):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(num):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(num):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valijkl = False
    if valijkl is None:
      valijkl_ = None
      _tmparray_valijkl_ = None
    else:
      if len(valijkl) < int(num):
        raise ValueError("argument valijkl is too short")
      _tmparray_valijkl_ = (ctypes.c_double*len(valijkl))(*valijkl)
    _res_putbarablocktriplet = __library__.MSK_putbarablocktriplet(self.__nativep,num,_tmparray_subi_,_tmparray_subj_,_tmparray_subk_,_tmparray_subl_,_tmparray_valijkl_)
    if _res_putbarablocktriplet != 0:
      _,_msg_putbarablocktriplet = self.__getlasterror(_res_putbarablocktriplet)
      raise Error(rescode(_res_putbarablocktriplet),_msg_putbarablocktriplet)
  def putbarablocktriplet(self,*args,**kwds):
    """
    Inputs barA in block triplet form.
  
    putbarablocktriplet(subi,subj,subk,subl,valijkl)
      [subi : array(int32)]  Constraint index.  
      [subj : array(int32)]  Symmetric matrix variable index.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valijkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    return self.__putbarablocktriplet_6(*args,**kwds)
  def __getnumbarablocktriplets_1(self):
    num_ = ctypes.c_int64()
    _res_getnumbarablocktriplets = __library__.MSK_getnumbarablocktriplets(self.__nativep,ctypes.byref(num_))
    if _res_getnumbarablocktriplets != 0:
      _,_msg_getnumbarablocktriplets = self.__getlasterror(_res_getnumbarablocktriplets)
      raise Error(rescode(_res_getnumbarablocktriplets),_msg_getnumbarablocktriplets)
    num = num_.value
    return (num_.value)
  def getnumbarablocktriplets(self,*args,**kwds):
    """
    Obtains an upper bound on the number of scalar elements in the block triplet form of bara.
  
    getnumbarablocktriplets() -> (num)
      [num : int64]  An upper bound on the number of elements in the block triplet form of bara.  
    """
    return self.__getnumbarablocktriplets_1(*args,**kwds)
  def __getbarablocktriplet_6(self,subi,subj,subk,subl,valijkl):
    __tmp_781 = ctypes.c_int64()
    _res_getnumbarablocktriplets = __library__.MSK_getnumbarablocktriplets(self.__nativep,ctypes.byref(__tmp_781))
    if _res_getnumbarablocktriplets != 0:
      _,_msg_getnumbarablocktriplets = self.__getlasterror(_res_getnumbarablocktriplets)
      raise Error(rescode(_res_getnumbarablocktriplets),_msg_getnumbarablocktriplets)
    maxnum = __tmp_781.value;
    num_ = ctypes.c_int64()
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(maxnum):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxnum):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(maxnum):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(maxnum):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valijkl = False
    if valijkl is None:
      valijkl_ = None
      _tmparray_valijkl_ = None
    else:
      if len(valijkl) < int(maxnum):
        raise ValueError("argument valijkl is too short")
      _tmparray_valijkl_ = (ctypes.c_double*len(valijkl))(*valijkl)
    _res_getbarablocktriplet = __library__.MSK_getbarablocktriplet(self.__nativep,maxnum,ctypes.byref(num_),_tmparray_subi_,_tmparray_subj_,_tmparray_subk_,_tmparray_subl_,_tmparray_valijkl_)
    if _res_getbarablocktriplet != 0:
      _,_msg_getbarablocktriplet = self.__getlasterror(_res_getbarablocktriplet)
      raise Error(rescode(_res_getbarablocktriplet),_msg_getbarablocktriplet)
    num = num_.value
    if subi is not None:
      for __tmp_783,__tmp_784 in enumerate(_tmparray_subi_):
        subi[__tmp_783] = __tmp_784
    if subj is not None:
      for __tmp_785,__tmp_786 in enumerate(_tmparray_subj_):
        subj[__tmp_785] = __tmp_786
    if subk is not None:
      for __tmp_787,__tmp_788 in enumerate(_tmparray_subk_):
        subk[__tmp_787] = __tmp_788
    if subl is not None:
      for __tmp_789,__tmp_790 in enumerate(_tmparray_subl_):
        subl[__tmp_789] = __tmp_790
    if valijkl is not None:
      for __tmp_791,__tmp_792 in enumerate(_tmparray_valijkl_):
        valijkl[__tmp_791] = __tmp_792
    return (num_.value)
  def __getbarablocktriplet_1(self):
    __tmp_793 = ctypes.c_int64()
    _res_getnumbarablocktriplets = __library__.MSK_getnumbarablocktriplets(self.__nativep,ctypes.byref(__tmp_793))
    if _res_getnumbarablocktriplets != 0:
      _,_msg_getnumbarablocktriplets = self.__getlasterror(_res_getnumbarablocktriplets)
      raise Error(rescode(_res_getnumbarablocktriplets),_msg_getnumbarablocktriplets)
    maxnum = __tmp_793.value;
    num_ = ctypes.c_int64()
    subi = numpy.zeros(maxnum,numpy.int32)
    subj = numpy.zeros(maxnum,numpy.int32)
    subk = numpy.zeros(maxnum,numpy.int32)
    subl = numpy.zeros(maxnum,numpy.int32)
    valijkl = numpy.zeros(maxnum,numpy.float64)
    _res_getbarablocktriplet = __library__.MSK_getbarablocktriplet(self.__nativep,maxnum,ctypes.byref(num_),ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subk.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subl.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(valijkl.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getbarablocktriplet != 0:
      _,_msg_getbarablocktriplet = self.__getlasterror(_res_getbarablocktriplet)
      raise Error(rescode(_res_getbarablocktriplet),_msg_getbarablocktriplet)
    num = num_.value
    return (num_.value,subi,subj,subk,subl,valijkl)
  def getbarablocktriplet(self,*args,**kwds):
    """
    Obtains barA in block triplet form.
  
    getbarablocktriplet(subi,subj,subk,subl,valijkl) -> (num)
    getbarablocktriplet() -> (num,subi,subj,subk,subl,valijkl)
      [num : int64]  Number of elements in the block triplet form.  
      [subi : array(int32)]  Constraint index.  
      [subj : array(int32)]  Symmetric matrix variable index.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valijkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getbarablocktriplet_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getbarablocktriplet_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putmaxnumafe_2(self,maxnumafe):
    _res_putmaxnumafe = __library__.MSK_putmaxnumafe(self.__nativep,maxnumafe)
    if _res_putmaxnumafe != 0:
      _,_msg_putmaxnumafe = self.__getlasterror(_res_putmaxnumafe)
      raise Error(rescode(_res_putmaxnumafe),_msg_putmaxnumafe)
  def putmaxnumafe(self,*args,**kwds):
    """
    Sets the number of preallocated affine expressions in the optimization task.
  
    putmaxnumafe(maxnumafe)
      [maxnumafe : int64]  Number of preallocated affine expressions.  
    """
    return self.__putmaxnumafe_2(*args,**kwds)
  def __getnumafe_1(self):
    numafe_ = ctypes.c_int64()
    _res_getnumafe = __library__.MSK_getnumafe(self.__nativep,ctypes.byref(numafe_))
    if _res_getnumafe != 0:
      _,_msg_getnumafe = self.__getlasterror(_res_getnumafe)
      raise Error(rescode(_res_getnumafe),_msg_getnumafe)
    numafe = numafe_.value
    return (numafe_.value)
  def getnumafe(self,*args,**kwds):
    """
    Obtains the number of affine expressions.
  
    getnumafe() -> (numafe)
      [numafe : int64]  Number of affine expressions.  
    """
    return self.__getnumafe_1(*args,**kwds)
  def __appendafes_2(self,num):
    _res_appendafes = __library__.MSK_appendafes(self.__nativep,num)
    if _res_appendafes != 0:
      _,_msg_appendafes = self.__getlasterror(_res_appendafes)
      raise Error(rescode(_res_appendafes),_msg_appendafes)
  def appendafes(self,*args,**kwds):
    """
    Appends a number of empty affine expressions to the optimization task.
  
    appendafes(num)
      [num : int64]  Number of empty affine expressions which should be appended.  
    """
    return self.__appendafes_2(*args,**kwds)
  def __putafefentry_4(self,afeidx,varidx,value):
    _res_putafefentry = __library__.MSK_putafefentry(self.__nativep,afeidx,varidx,value)
    if _res_putafefentry != 0:
      _,_msg_putafefentry = self.__getlasterror(_res_putafefentry)
      raise Error(rescode(_res_putafefentry),_msg_putafefentry)
  def putafefentry(self,*args,**kwds):
    """
    Replaces one entry in F.
  
    putafefentry(afeidx,varidx,value)
      [afeidx : int64]  Row index in F.  
      [value : float64]  Value of the entry.  
      [varidx : int32]  Column index in F.  
    """
    return self.__putafefentry_4(*args,**kwds)
  def __putafefentrylist_4(self,afeidx,varidx,val):
    numentr = min(len(afeidx) if afeidx is not None else 0,len(varidx) if varidx is not None else 0,len(val) if val is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_putafefentrylist = __library__.MSK_putafefentrylist(self.__nativep,numentr,_tmparray_afeidx_,_tmparray_varidx_,_tmparray_val_)
    if _res_putafefentrylist != 0:
      _,_msg_putafefentrylist = self.__getlasterror(_res_putafefentrylist)
      raise Error(rescode(_res_putafefentrylist),_msg_putafefentrylist)
  def putafefentrylist(self,*args,**kwds):
    """
    Replaces a list of entries in F.
  
    putafefentrylist(afeidx,varidx,val)
      [afeidx : array(int64)]  Row indices in F.  
      [val : array(float64)]  Values of the entries in F.  
      [varidx : array(int32)]  Column indices in F.  
    """
    return self.__putafefentrylist_4(*args,**kwds)
  def __emptyafefrow_2(self,afeidx):
    _res_emptyafefrow = __library__.MSK_emptyafefrow(self.__nativep,afeidx)
    if _res_emptyafefrow != 0:
      _,_msg_emptyafefrow = self.__getlasterror(_res_emptyafefrow)
      raise Error(rescode(_res_emptyafefrow),_msg_emptyafefrow)
  def emptyafefrow(self,*args,**kwds):
    """
    Clears a row in F.
  
    emptyafefrow(afeidx)
      [afeidx : int64]  Row index.  
    """
    return self.__emptyafefrow_2(*args,**kwds)
  def __emptyafefcol_2(self,varidx):
    _res_emptyafefcol = __library__.MSK_emptyafefcol(self.__nativep,varidx)
    if _res_emptyafefcol != 0:
      _,_msg_emptyafefcol = self.__getlasterror(_res_emptyafefcol)
      raise Error(rescode(_res_emptyafefcol),_msg_emptyafefcol)
  def emptyafefcol(self,*args,**kwds):
    """
    Clears a column in F.
  
    emptyafefcol(varidx)
      [varidx : int32]  Variable index.  
    """
    return self.__emptyafefcol_2(*args,**kwds)
  def __emptyafefrowlist_2(self,afeidx):
    numafeidx = len(afeidx) if afeidx is not None else 0
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    _res_emptyafefrowlist = __library__.MSK_emptyafefrowlist(self.__nativep,numafeidx,_tmparray_afeidx_)
    if _res_emptyafefrowlist != 0:
      _,_msg_emptyafefrowlist = self.__getlasterror(_res_emptyafefrowlist)
      raise Error(rescode(_res_emptyafefrowlist),_msg_emptyafefrowlist)
  def emptyafefrowlist(self,*args,**kwds):
    """
    Clears rows in F.
  
    emptyafefrowlist(afeidx)
      [afeidx : array(int64)]  Indices of rows in F to clear.  
    """
    return self.__emptyafefrowlist_2(*args,**kwds)
  def __emptyafefcollist_2(self,varidx):
    numvaridx = len(varidx) if varidx is not None else 0
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    _res_emptyafefcollist = __library__.MSK_emptyafefcollist(self.__nativep,numvaridx,_tmparray_varidx_)
    if _res_emptyafefcollist != 0:
      _,_msg_emptyafefcollist = self.__getlasterror(_res_emptyafefcollist)
      raise Error(rescode(_res_emptyafefcollist),_msg_emptyafefcollist)
  def emptyafefcollist(self,*args,**kwds):
    """
    Clears columns in F.
  
    emptyafefcollist(varidx)
      [varidx : array(int32)]  Indices of variables in F to clear.  
    """
    return self.__emptyafefcollist_2(*args,**kwds)
  def __putafefrow_4(self,afeidx,varidx,val):
    numnz = min(len(varidx) if varidx is not None else 0,len(val) if val is not None else 0)
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_putafefrow = __library__.MSK_putafefrow(self.__nativep,afeidx,numnz,_tmparray_varidx_,_tmparray_val_)
    if _res_putafefrow != 0:
      _,_msg_putafefrow = self.__getlasterror(_res_putafefrow)
      raise Error(rescode(_res_putafefrow),_msg_putafefrow)
  def putafefrow(self,*args,**kwds):
    """
    Replaces all elements in one row of the F matrix in the affine expressions.
  
    putafefrow(afeidx,varidx,val)
      [afeidx : int64]  Row index.  
      [val : array(float64)]  New non-zero values in the row.  
      [varidx : array(int32)]  Column indexes of non-zero values in the row.  
    """
    return self.__putafefrow_4(*args,**kwds)
  def __putafefrowlist_6(self,afeidx,numnzrow,ptrrow,varidx,val):
    numafeidx = min(len(afeidx) if afeidx is not None else 0,len(numnzrow) if numnzrow is not None else 0,len(ptrrow) if ptrrow is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_numnzrow = False
    if numnzrow is None:
      numnzrow_ = None
      _tmparray_numnzrow_ = None
    else:
      _tmparray_numnzrow_ = (ctypes.c_int32*len(numnzrow))(*numnzrow)
    copyback_ptrrow = False
    if ptrrow is None:
      ptrrow_ = None
      _tmparray_ptrrow_ = None
    else:
      _tmparray_ptrrow_ = (ctypes.c_int64*len(ptrrow))(*ptrrow)
    lenidxval = min(len(varidx) if varidx is not None else 0,len(val) if val is not None else 0)
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_putafefrowlist = __library__.MSK_putafefrowlist(self.__nativep,numafeidx,_tmparray_afeidx_,_tmparray_numnzrow_,_tmparray_ptrrow_,lenidxval,_tmparray_varidx_,_tmparray_val_)
    if _res_putafefrowlist != 0:
      _,_msg_putafefrowlist = self.__getlasterror(_res_putafefrowlist)
      raise Error(rescode(_res_putafefrowlist),_msg_putafefrowlist)
  def putafefrowlist(self,*args,**kwds):
    """
    Replaces all elements in a number of rows of the F matrix in the affine expressions.
  
    putafefrowlist(afeidx,numnzrow,ptrrow,varidx,val)
      [afeidx : array(int64)]  Row indices.  
      [numnzrow : array(int32)]  Number of non-zeros in each row.  
      [ptrrow : array(int64)]  Pointer to the first nonzero in each row.  
      [val : array(float64)]  New non-zero values in the rows.  
      [varidx : array(int32)]  Column indexes of non-zero values.  
    """
    return self.__putafefrowlist_6(*args,**kwds)
  def __putafefcol_4(self,varidx,afeidx,val):
    numnz = min(len(afeidx) if afeidx is not None else 0,len(val) if val is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_putafefcol = __library__.MSK_putafefcol(self.__nativep,varidx,numnz,_tmparray_afeidx_,_tmparray_val_)
    if _res_putafefcol != 0:
      _,_msg_putafefcol = self.__getlasterror(_res_putafefcol)
      raise Error(rescode(_res_putafefcol),_msg_putafefcol)
  def putafefcol(self,*args,**kwds):
    """
    Replaces all elements in one column of the F matrix in the affine expressions.
  
    putafefcol(varidx,afeidx,val)
      [afeidx : array(int64)]  Row indexes of non-zero values in the column.  
      [val : array(float64)]  New non-zero values in the column.  
      [varidx : int32]  Column index.  
    """
    return self.__putafefcol_4(*args,**kwds)
  def __getafefrownumnz_2(self,afeidx):
    numnz_ = ctypes.c_int32()
    _res_getafefrownumnz = __library__.MSK_getafefrownumnz(self.__nativep,afeidx,ctypes.byref(numnz_))
    if _res_getafefrownumnz != 0:
      _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
      raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
    numnz = numnz_.value
    return (numnz_.value)
  def getafefrownumnz(self,*args,**kwds):
    """
    Obtains the number of nonzeros in a row of F.
  
    getafefrownumnz(afeidx) -> (numnz)
      [afeidx : int64]  Row index.  
      [numnz : int32]  Number of non-zeros in the row.  
    """
    return self.__getafefrownumnz_2(*args,**kwds)
  def __getafefnumnz_1(self):
    numnz_ = ctypes.c_int64()
    _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(numnz_))
    if _res_getafefnumnz != 0:
      _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
      raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
    numnz = numnz_.value
    return (numnz_.value)
  def getafefnumnz(self,*args,**kwds):
    """
    Obtains the total number of nonzeros in F.
  
    getafefnumnz() -> (numnz)
      [numnz : int64]  Number of nonzeros in F.  
    """
    return self.__getafefnumnz_1(*args,**kwds)
  def __getafefrow_4(self,afeidx,varidx,val):
    numnz_ = ctypes.c_int32()
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      __tmp_800 = ctypes.c_int32()
      _res_getafefrownumnz = __library__.MSK_getafefrownumnz(self.__nativep,afeidx,ctypes.byref(__tmp_800))
      if _res_getafefrownumnz != 0:
        _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
        raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
      if len(varidx) < int(__tmp_800.value):
        raise ValueError("argument varidx is too short")
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      __tmp_804 = ctypes.c_int32()
      _res_getafefrownumnz = __library__.MSK_getafefrownumnz(self.__nativep,afeidx,ctypes.byref(__tmp_804))
      if _res_getafefrownumnz != 0:
        _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
        raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
      if len(val) < int(__tmp_804.value):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getafefrow = __library__.MSK_getafefrow(self.__nativep,afeidx,ctypes.byref(numnz_),_tmparray_varidx_,_tmparray_val_)
    if _res_getafefrow != 0:
      _,_msg_getafefrow = self.__getlasterror(_res_getafefrow)
      raise Error(rescode(_res_getafefrow),_msg_getafefrow)
    numnz = numnz_.value
    if varidx is not None:
      for __tmp_802,__tmp_803 in enumerate(_tmparray_varidx_):
        varidx[__tmp_802] = __tmp_803
    if val is not None:
      for __tmp_806,__tmp_807 in enumerate(_tmparray_val_):
        val[__tmp_806] = __tmp_807
    return (numnz_.value)
  def __getafefrow_2(self,afeidx):
    numnz_ = ctypes.c_int32()
    __tmp_808 = ctypes.c_int32()
    _res_getafefrownumnz = __library__.MSK_getafefrownumnz(self.__nativep,afeidx,ctypes.byref(__tmp_808))
    if _res_getafefrownumnz != 0:
      _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
      raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
    varidx = numpy.zeros(__tmp_808.value,numpy.int32)
    __tmp_811 = ctypes.c_int32()
    _res_getafefrownumnz = __library__.MSK_getafefrownumnz(self.__nativep,afeidx,ctypes.byref(__tmp_811))
    if _res_getafefrownumnz != 0:
      _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
      raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
    val = numpy.zeros(__tmp_811.value,numpy.float64)
    _res_getafefrow = __library__.MSK_getafefrow(self.__nativep,afeidx,ctypes.byref(numnz_),ctypes.cast(varidx.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getafefrow != 0:
      _,_msg_getafefrow = self.__getlasterror(_res_getafefrow)
      raise Error(rescode(_res_getafefrow),_msg_getafefrow)
    numnz = numnz_.value
    return (numnz_.value,varidx,val)
  def getafefrow(self,*args,**kwds):
    """
    Obtains one row of F in sparse format.
  
    getafefrow(afeidx,varidx,val) -> (numnz)
    getafefrow(afeidx) -> (numnz,varidx,val)
      [afeidx : int64]  Row index.  
      [numnz : int32]  Number of non-zeros in the row obtained.  
      [val : array(float64)]  Values of the non-zeros in the row obtained.  
      [varidx : array(int32)]  Column indices of the non-zeros in the row obtained.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getafefrow_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getafefrow_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getafeftrip_4(self,afeidx,varidx,val):
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      __tmp_814 = ctypes.c_int64()
      _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_814))
      if _res_getafefnumnz != 0:
        _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
        raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
      if len(afeidx) < int(__tmp_814.value):
        raise ValueError("argument afeidx is too short")
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_varidx = False
    if varidx is None:
      varidx_ = None
      _tmparray_varidx_ = None
    else:
      __tmp_818 = ctypes.c_int64()
      _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_818))
      if _res_getafefnumnz != 0:
        _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
        raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
      if len(varidx) < int(__tmp_818.value):
        raise ValueError("argument varidx is too short")
      _tmparray_varidx_ = (ctypes.c_int32*len(varidx))(*varidx)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      __tmp_822 = ctypes.c_int64()
      _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_822))
      if _res_getafefnumnz != 0:
        _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
        raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
      if len(val) < int(__tmp_822.value):
        raise ValueError("argument val is too short")
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_getafeftrip = __library__.MSK_getafeftrip(self.__nativep,_tmparray_afeidx_,_tmparray_varidx_,_tmparray_val_)
    if _res_getafeftrip != 0:
      _,_msg_getafeftrip = self.__getlasterror(_res_getafeftrip)
      raise Error(rescode(_res_getafeftrip),_msg_getafeftrip)
    if afeidx is not None:
      for __tmp_816,__tmp_817 in enumerate(_tmparray_afeidx_):
        afeidx[__tmp_816] = __tmp_817
    if varidx is not None:
      for __tmp_820,__tmp_821 in enumerate(_tmparray_varidx_):
        varidx[__tmp_820] = __tmp_821
    if val is not None:
      for __tmp_824,__tmp_825 in enumerate(_tmparray_val_):
        val[__tmp_824] = __tmp_825
  def __getafeftrip_1(self):
    __tmp_826 = ctypes.c_int64()
    _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_826))
    if _res_getafefnumnz != 0:
      _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
      raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
    afeidx = numpy.zeros(__tmp_826.value,numpy.int64)
    __tmp_829 = ctypes.c_int64()
    _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_829))
    if _res_getafefnumnz != 0:
      _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
      raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
    varidx = numpy.zeros(__tmp_829.value,numpy.int32)
    __tmp_832 = ctypes.c_int64()
    _res_getafefnumnz = __library__.MSK_getafefnumnz(self.__nativep,ctypes.byref(__tmp_832))
    if _res_getafefnumnz != 0:
      _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
      raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
    val = numpy.zeros(__tmp_832.value,numpy.float64)
    _res_getafeftrip = __library__.MSK_getafeftrip(self.__nativep,ctypes.cast(afeidx.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(varidx.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getafeftrip != 0:
      _,_msg_getafeftrip = self.__getlasterror(_res_getafeftrip)
      raise Error(rescode(_res_getafeftrip),_msg_getafeftrip)
    return (afeidx,varidx,val)
  def getafeftrip(self,*args,**kwds):
    """
    Obtains the F matrix in triplet format.
  
    getafeftrip(afeidx,varidx,val)
    getafeftrip() -> (afeidx,varidx,val)
      [afeidx : array(int64)]  Row indices of nonzeros.  
      [val : array(float64)]  Values of nonzero entries.  
      [varidx : array(int32)]  Column indices of nonzeros.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getafeftrip_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getafeftrip_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putafebarfentry_5(self,afeidx,barvaridx,termidx,termweight):
    numterm = min(len(termidx) if termidx is not None else 0,len(termweight) if termweight is not None else 0)
    copyback_termidx = False
    if termidx is None:
      termidx_ = None
      _tmparray_termidx_ = None
    else:
      _tmparray_termidx_ = (ctypes.c_int64*len(termidx))(*termidx)
    copyback_termweight = False
    if termweight is None:
      termweight_ = None
      _tmparray_termweight_ = None
    else:
      _tmparray_termweight_ = (ctypes.c_double*len(termweight))(*termweight)
    _res_putafebarfentry = __library__.MSK_putafebarfentry(self.__nativep,afeidx,barvaridx,numterm,_tmparray_termidx_,_tmparray_termweight_)
    if _res_putafebarfentry != 0:
      _,_msg_putafebarfentry = self.__getlasterror(_res_putafebarfentry)
      raise Error(rescode(_res_putafebarfentry),_msg_putafebarfentry)
  def putafebarfentry(self,*args,**kwds):
    """
    Inputs one entry in barF.
  
    putafebarfentry(afeidx,barvaridx,termidx,termweight)
      [afeidx : int64]  Row index of barF.  
      [barvaridx : int32]  Semidefinite variable index.  
      [termidx : array(int64)]  Element indices in matrix storage.  
      [termweight : array(float64)]  Weights in the weighted sum.  
    """
    return self.__putafebarfentry_5(*args,**kwds)
  def __putafebarfentrylist_7(self,afeidx,barvaridx,numterm,ptrterm,termidx,termweight):
    numafeidx = min(len(afeidx) if afeidx is not None else 0,len(barvaridx) if barvaridx is not None else 0,len(numterm) if numterm is not None else 0,len(ptrterm) if ptrterm is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_barvaridx = False
    if barvaridx is None:
      barvaridx_ = None
      _tmparray_barvaridx_ = None
    else:
      _tmparray_barvaridx_ = (ctypes.c_int32*len(barvaridx))(*barvaridx)
    copyback_numterm = False
    if numterm is None:
      numterm_ = None
      _tmparray_numterm_ = None
    else:
      _tmparray_numterm_ = (ctypes.c_int64*len(numterm))(*numterm)
    copyback_ptrterm = False
    if ptrterm is None:
      ptrterm_ = None
      _tmparray_ptrterm_ = None
    else:
      _tmparray_ptrterm_ = (ctypes.c_int64*len(ptrterm))(*ptrterm)
    lenterm = min(len(termidx) if termidx is not None else 0,len(termweight) if termweight is not None else 0)
    copyback_termidx = False
    if termidx is None:
      termidx_ = None
      _tmparray_termidx_ = None
    else:
      _tmparray_termidx_ = (ctypes.c_int64*len(termidx))(*termidx)
    copyback_termweight = False
    if termweight is None:
      termweight_ = None
      _tmparray_termweight_ = None
    else:
      _tmparray_termweight_ = (ctypes.c_double*len(termweight))(*termweight)
    _res_putafebarfentrylist = __library__.MSK_putafebarfentrylist(self.__nativep,numafeidx,_tmparray_afeidx_,_tmparray_barvaridx_,_tmparray_numterm_,_tmparray_ptrterm_,lenterm,_tmparray_termidx_,_tmparray_termweight_)
    if _res_putafebarfentrylist != 0:
      _,_msg_putafebarfentrylist = self.__getlasterror(_res_putafebarfentrylist)
      raise Error(rescode(_res_putafebarfentrylist),_msg_putafebarfentrylist)
  def putafebarfentrylist(self,*args,**kwds):
    """
    Inputs a list of entries in barF.
  
    putafebarfentrylist(afeidx,
                        barvaridx,
                        numterm,
                        ptrterm,
                        termidx,
                        termweight)
      [afeidx : array(int64)]  Row indexes of barF.  
      [barvaridx : array(int32)]  Semidefinite variable indexes.  
      [numterm : array(int64)]  Number of terms in the weighted sums.  
      [ptrterm : array(int64)]  Pointer to the terms forming each entry.  
      [termidx : array(int64)]  Concatenated element indexes in matrix storage.  
      [termweight : array(float64)]  Concatenated weights in the weighted sum.  
    """
    return self.__putafebarfentrylist_7(*args,**kwds)
  def __putafebarfrow_7(self,afeidx,barvaridx,numterm,ptrterm,termidx,termweight):
    numentr = min(len(barvaridx) if barvaridx is not None else 0,len(numterm) if numterm is not None else 0,len(ptrterm) if ptrterm is not None else 0)
    copyback_barvaridx = False
    if barvaridx is None:
      barvaridx_ = None
      _tmparray_barvaridx_ = None
    else:
      _tmparray_barvaridx_ = (ctypes.c_int32*len(barvaridx))(*barvaridx)
    copyback_numterm = False
    if numterm is None:
      numterm_ = None
      _tmparray_numterm_ = None
    else:
      _tmparray_numterm_ = (ctypes.c_int64*len(numterm))(*numterm)
    copyback_ptrterm = False
    if ptrterm is None:
      ptrterm_ = None
      _tmparray_ptrterm_ = None
    else:
      _tmparray_ptrterm_ = (ctypes.c_int64*len(ptrterm))(*ptrterm)
    lenterm = min(len(termidx) if termidx is not None else 0,len(termweight) if termweight is not None else 0)
    copyback_termidx = False
    if termidx is None:
      termidx_ = None
      _tmparray_termidx_ = None
    else:
      _tmparray_termidx_ = (ctypes.c_int64*len(termidx))(*termidx)
    copyback_termweight = False
    if termweight is None:
      termweight_ = None
      _tmparray_termweight_ = None
    else:
      _tmparray_termweight_ = (ctypes.c_double*len(termweight))(*termweight)
    _res_putafebarfrow = __library__.MSK_putafebarfrow(self.__nativep,afeidx,numentr,_tmparray_barvaridx_,_tmparray_numterm_,_tmparray_ptrterm_,lenterm,_tmparray_termidx_,_tmparray_termweight_)
    if _res_putafebarfrow != 0:
      _,_msg_putafebarfrow = self.__getlasterror(_res_putafebarfrow)
      raise Error(rescode(_res_putafebarfrow),_msg_putafebarfrow)
  def putafebarfrow(self,*args,**kwds):
    """
    Inputs a row of barF.
  
    putafebarfrow(afeidx,
                  barvaridx,
                  numterm,
                  ptrterm,
                  termidx,
                  termweight)
      [afeidx : int64]  Row index of barF.  
      [barvaridx : array(int32)]  Semidefinite variable indexes.  
      [numterm : array(int64)]  Number of terms in the weighted sums.  
      [ptrterm : array(int64)]  Pointer to the terms forming each entry.  
      [termidx : array(int64)]  Concatenated element indexes in matrix storage.  
      [termweight : array(float64)]  Concatenated weights in the weighted sum.  
    """
    return self.__putafebarfrow_7(*args,**kwds)
  def __emptyafebarfrow_2(self,afeidx):
    _res_emptyafebarfrow = __library__.MSK_emptyafebarfrow(self.__nativep,afeidx)
    if _res_emptyafebarfrow != 0:
      _,_msg_emptyafebarfrow = self.__getlasterror(_res_emptyafebarfrow)
      raise Error(rescode(_res_emptyafebarfrow),_msg_emptyafebarfrow)
  def emptyafebarfrow(self,*args,**kwds):
    """
    Clears a row in barF
  
    emptyafebarfrow(afeidx)
      [afeidx : int64]  Row index of barF.  
    """
    return self.__emptyafebarfrow_2(*args,**kwds)
  def __emptyafebarfrowlist_2(self,afeidxlist):
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    _res_emptyafebarfrowlist = __library__.MSK_emptyafebarfrowlist(self.__nativep,numafeidx,_tmparray_afeidxlist_)
    if _res_emptyafebarfrowlist != 0:
      _,_msg_emptyafebarfrowlist = self.__getlasterror(_res_emptyafebarfrowlist)
      raise Error(rescode(_res_emptyafebarfrowlist),_msg_emptyafebarfrowlist)
  def emptyafebarfrowlist(self,*args,**kwds):
    """
    Clears rows in barF.
  
    emptyafebarfrowlist(afeidxlist)
      [afeidxlist : array(int64)]  Indices of rows in barF to clear.  
    """
    return self.__emptyafebarfrowlist_2(*args,**kwds)
  def __putafebarfblocktriplet_6(self,afeidx,barvaridx,subk,subl,valkl):
    numtrip = min(len(afeidx) if afeidx is not None else 0,len(barvaridx) if barvaridx is not None else 0,len(subk) if subk is not None else 0,len(subl) if subl is not None else 0,len(valkl) if valkl is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      if len(afeidx) < int(numtrip):
        raise ValueError("argument afeidx is too short")
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_barvaridx = False
    if barvaridx is None:
      barvaridx_ = None
      _tmparray_barvaridx_ = None
    else:
      if len(barvaridx) < int(numtrip):
        raise ValueError("argument barvaridx is too short")
      _tmparray_barvaridx_ = (ctypes.c_int32*len(barvaridx))(*barvaridx)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(numtrip):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(numtrip):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valkl = False
    if valkl is None:
      valkl_ = None
      _tmparray_valkl_ = None
    else:
      if len(valkl) < int(numtrip):
        raise ValueError("argument valkl is too short")
      _tmparray_valkl_ = (ctypes.c_double*len(valkl))(*valkl)
    _res_putafebarfblocktriplet = __library__.MSK_putafebarfblocktriplet(self.__nativep,numtrip,_tmparray_afeidx_,_tmparray_barvaridx_,_tmparray_subk_,_tmparray_subl_,_tmparray_valkl_)
    if _res_putafebarfblocktriplet != 0:
      _,_msg_putafebarfblocktriplet = self.__getlasterror(_res_putafebarfblocktriplet)
      raise Error(rescode(_res_putafebarfblocktriplet),_msg_putafebarfblocktriplet)
  def putafebarfblocktriplet(self,*args,**kwds):
    """
    Inputs barF in block triplet form.
  
    putafebarfblocktriplet(afeidx,barvaridx,subk,subl,valkl)
      [afeidx : array(int64)]  Constraint index.  
      [barvaridx : array(int32)]  Symmetric matrix variable index.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    return self.__putafebarfblocktriplet_6(*args,**kwds)
  def __getafebarfnumblocktriplets_1(self):
    numtrip_ = ctypes.c_int64()
    _res_getafebarfnumblocktriplets = __library__.MSK_getafebarfnumblocktriplets(self.__nativep,ctypes.byref(numtrip_))
    if _res_getafebarfnumblocktriplets != 0:
      _,_msg_getafebarfnumblocktriplets = self.__getlasterror(_res_getafebarfnumblocktriplets)
      raise Error(rescode(_res_getafebarfnumblocktriplets),_msg_getafebarfnumblocktriplets)
    numtrip = numtrip_.value
    return (numtrip_.value)
  def getafebarfnumblocktriplets(self,*args,**kwds):
    """
    Obtains an upper bound on the number of elements in the block triplet form of barf.
  
    getafebarfnumblocktriplets() -> (numtrip)
      [numtrip : int64]  An upper bound on the number of elements in the block triplet form of barf.  
    """
    return self.__getafebarfnumblocktriplets_1(*args,**kwds)
  def __getafebarfblocktriplet_6(self,afeidx,barvaridx,subk,subl,valkl):
    __tmp_835 = ctypes.c_int64()
    _res_getafebarfnumblocktriplets = __library__.MSK_getafebarfnumblocktriplets(self.__nativep,ctypes.byref(__tmp_835))
    if _res_getafebarfnumblocktriplets != 0:
      _,_msg_getafebarfnumblocktriplets = self.__getlasterror(_res_getafebarfnumblocktriplets)
      raise Error(rescode(_res_getafebarfnumblocktriplets),_msg_getafebarfnumblocktriplets)
    maxnumtrip = __tmp_835.value;
    numtrip_ = ctypes.c_int64()
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      if len(afeidx) < int(maxnumtrip):
        raise ValueError("argument afeidx is too short")
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_barvaridx = False
    if barvaridx is None:
      barvaridx_ = None
      _tmparray_barvaridx_ = None
    else:
      if len(barvaridx) < int(maxnumtrip):
        raise ValueError("argument barvaridx is too short")
      _tmparray_barvaridx_ = (ctypes.c_int32*len(barvaridx))(*barvaridx)
    copyback_subk = False
    if subk is None:
      subk_ = None
      _tmparray_subk_ = None
    else:
      if len(subk) < int(maxnumtrip):
        raise ValueError("argument subk is too short")
      _tmparray_subk_ = (ctypes.c_int32*len(subk))(*subk)
    copyback_subl = False
    if subl is None:
      subl_ = None
      _tmparray_subl_ = None
    else:
      if len(subl) < int(maxnumtrip):
        raise ValueError("argument subl is too short")
      _tmparray_subl_ = (ctypes.c_int32*len(subl))(*subl)
    copyback_valkl = False
    if valkl is None:
      valkl_ = None
      _tmparray_valkl_ = None
    else:
      if len(valkl) < int(maxnumtrip):
        raise ValueError("argument valkl is too short")
      _tmparray_valkl_ = (ctypes.c_double*len(valkl))(*valkl)
    _res_getafebarfblocktriplet = __library__.MSK_getafebarfblocktriplet(self.__nativep,maxnumtrip,ctypes.byref(numtrip_),_tmparray_afeidx_,_tmparray_barvaridx_,_tmparray_subk_,_tmparray_subl_,_tmparray_valkl_)
    if _res_getafebarfblocktriplet != 0:
      _,_msg_getafebarfblocktriplet = self.__getlasterror(_res_getafebarfblocktriplet)
      raise Error(rescode(_res_getafebarfblocktriplet),_msg_getafebarfblocktriplet)
    numtrip = numtrip_.value
    if afeidx is not None:
      for __tmp_837,__tmp_838 in enumerate(_tmparray_afeidx_):
        afeidx[__tmp_837] = __tmp_838
    if barvaridx is not None:
      for __tmp_839,__tmp_840 in enumerate(_tmparray_barvaridx_):
        barvaridx[__tmp_839] = __tmp_840
    if subk is not None:
      for __tmp_841,__tmp_842 in enumerate(_tmparray_subk_):
        subk[__tmp_841] = __tmp_842
    if subl is not None:
      for __tmp_843,__tmp_844 in enumerate(_tmparray_subl_):
        subl[__tmp_843] = __tmp_844
    if valkl is not None:
      for __tmp_845,__tmp_846 in enumerate(_tmparray_valkl_):
        valkl[__tmp_845] = __tmp_846
    return (numtrip_.value)
  def __getafebarfblocktriplet_1(self):
    __tmp_847 = ctypes.c_int64()
    _res_getafebarfnumblocktriplets = __library__.MSK_getafebarfnumblocktriplets(self.__nativep,ctypes.byref(__tmp_847))
    if _res_getafebarfnumblocktriplets != 0:
      _,_msg_getafebarfnumblocktriplets = self.__getlasterror(_res_getafebarfnumblocktriplets)
      raise Error(rescode(_res_getafebarfnumblocktriplets),_msg_getafebarfnumblocktriplets)
    maxnumtrip = __tmp_847.value;
    numtrip_ = ctypes.c_int64()
    afeidx = numpy.zeros(maxnumtrip,numpy.int64)
    barvaridx = numpy.zeros(maxnumtrip,numpy.int32)
    subk = numpy.zeros(maxnumtrip,numpy.int32)
    subl = numpy.zeros(maxnumtrip,numpy.int32)
    valkl = numpy.zeros(maxnumtrip,numpy.float64)
    _res_getafebarfblocktriplet = __library__.MSK_getafebarfblocktriplet(self.__nativep,maxnumtrip,ctypes.byref(numtrip_),ctypes.cast(afeidx.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(barvaridx.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subk.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subl.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(valkl.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getafebarfblocktriplet != 0:
      _,_msg_getafebarfblocktriplet = self.__getlasterror(_res_getafebarfblocktriplet)
      raise Error(rescode(_res_getafebarfblocktriplet),_msg_getafebarfblocktriplet)
    numtrip = numtrip_.value
    return (numtrip_.value,afeidx,barvaridx,subk,subl,valkl)
  def getafebarfblocktriplet(self,*args,**kwds):
    """
    Obtains barF in block triplet form.
  
    getafebarfblocktriplet(afeidx,barvaridx,subk,subl,valkl) -> (numtrip)
    getafebarfblocktriplet() -> 
                          (numtrip,
                           afeidx,
                           barvaridx,
                           subk,
                           subl,
                           valkl)
      [afeidx : array(int64)]  Constraint index.  
      [barvaridx : array(int32)]  Symmetric matrix variable index.  
      [numtrip : int64]  Number of elements in the block triplet form.  
      [subk : array(int32)]  Block row index.  
      [subl : array(int32)]  Block column index.  
      [valkl : array(float64)]  The numerical value associated with each block triplet.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getafebarfblocktriplet_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getafebarfblocktriplet_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getafebarfnumrowentries_2(self,afeidx):
    numentr_ = ctypes.c_int32()
    _res_getafebarfnumrowentries = __library__.MSK_getafebarfnumrowentries(self.__nativep,afeidx,ctypes.byref(numentr_))
    if _res_getafebarfnumrowentries != 0:
      _,_msg_getafebarfnumrowentries = self.__getlasterror(_res_getafebarfnumrowentries)
      raise Error(rescode(_res_getafebarfnumrowentries),_msg_getafebarfnumrowentries)
    numentr = numentr_.value
    return (numentr_.value)
  def getafebarfnumrowentries(self,*args,**kwds):
    """
    Obtains the number of nonzero entries in a row of barF.
  
    getafebarfnumrowentries(afeidx) -> (numentr)
      [afeidx : int64]  Row index of barF.  
      [numentr : int32]  Number of nonzero entries in a row of barF.  
    """
    return self.__getafebarfnumrowentries_2(*args,**kwds)
  def __getafebarfrowinfo_2(self,afeidx):
    numentr_ = ctypes.c_int32()
    numterm_ = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(numentr_),ctypes.byref(numterm_))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    numentr = numentr_.value
    numterm = numterm_.value
    return (numentr_.value,numterm_.value)
  def getafebarfrowinfo(self,*args,**kwds):
    """
    Obtains information about one row of barF.
  
    getafebarfrowinfo(afeidx) -> (numentr,numterm)
      [afeidx : int64]  Row index of barF.  
      [numentr : int32]  Number of nonzero entries in a row of barF.  
      [numterm : int64]  Number of terms in the weighted sums representation of the row of barF.  
    """
    return self.__getafebarfrowinfo_2(*args,**kwds)
  def __getafebarfrow_7(self,afeidx,barvaridx,ptrterm,numterm,termidx,termweight):
    copyback_barvaridx = False
    if barvaridx is None:
      barvaridx_ = None
      _tmparray_barvaridx_ = None
    else:
      __tmp_854 = ctypes.c_int32()
      __tmp_855 = ctypes.c_int64()
      _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_854),ctypes.byref(__tmp_855))
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      if len(barvaridx) < int(__tmp_854.value):
        raise ValueError("argument barvaridx is too short")
      _tmparray_barvaridx_ = (ctypes.c_int32*len(barvaridx))(*barvaridx)
    copyback_ptrterm = False
    if ptrterm is None:
      ptrterm_ = None
      _tmparray_ptrterm_ = None
    else:
      __tmp_859 = ctypes.c_int32()
      __tmp_860 = ctypes.c_int64()
      _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_859),ctypes.byref(__tmp_860))
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      if len(ptrterm) < int(__tmp_859.value):
        raise ValueError("argument ptrterm is too short")
      _tmparray_ptrterm_ = (ctypes.c_int64*len(ptrterm))(*ptrterm)
    copyback_numterm = False
    if numterm is None:
      numterm_ = None
      _tmparray_numterm_ = None
    else:
      __tmp_864 = ctypes.c_int32()
      __tmp_865 = ctypes.c_int64()
      _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_864),ctypes.byref(__tmp_865))
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      if len(numterm) < int(__tmp_864.value):
        raise ValueError("argument numterm is too short")
      _tmparray_numterm_ = (ctypes.c_int64*len(numterm))(*numterm)
    copyback_termidx = False
    if termidx is None:
      termidx_ = None
      _tmparray_termidx_ = None
    else:
      __tmp_869 = ctypes.c_int32()
      __tmp_870 = ctypes.c_int64()
      _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_869),ctypes.byref(__tmp_870))
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      if len(termidx) < int(__tmp_870.value):
        raise ValueError("argument termidx is too short")
      _tmparray_termidx_ = (ctypes.c_int64*len(termidx))(*termidx)
    copyback_termweight = False
    if termweight is None:
      termweight_ = None
      _tmparray_termweight_ = None
    else:
      __tmp_874 = ctypes.c_int32()
      __tmp_875 = ctypes.c_int64()
      _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_874),ctypes.byref(__tmp_875))
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      if len(termweight) < int(__tmp_875.value):
        raise ValueError("argument termweight is too short")
      _tmparray_termweight_ = (ctypes.c_double*len(termweight))(*termweight)
    _res_getafebarfrow = __library__.MSK_getafebarfrow(self.__nativep,afeidx,_tmparray_barvaridx_,_tmparray_ptrterm_,_tmparray_numterm_,_tmparray_termidx_,_tmparray_termweight_)
    if _res_getafebarfrow != 0:
      _,_msg_getafebarfrow = self.__getlasterror(_res_getafebarfrow)
      raise Error(rescode(_res_getafebarfrow),_msg_getafebarfrow)
    if barvaridx is not None:
      for __tmp_857,__tmp_858 in enumerate(_tmparray_barvaridx_):
        barvaridx[__tmp_857] = __tmp_858
    if ptrterm is not None:
      for __tmp_862,__tmp_863 in enumerate(_tmparray_ptrterm_):
        ptrterm[__tmp_862] = __tmp_863
    if numterm is not None:
      for __tmp_867,__tmp_868 in enumerate(_tmparray_numterm_):
        numterm[__tmp_867] = __tmp_868
    if termidx is not None:
      for __tmp_872,__tmp_873 in enumerate(_tmparray_termidx_):
        termidx[__tmp_872] = __tmp_873
    if termweight is not None:
      for __tmp_877,__tmp_878 in enumerate(_tmparray_termweight_):
        termweight[__tmp_877] = __tmp_878
  def __getafebarfrow_2(self,afeidx):
    __tmp_879 = ctypes.c_int32()
    __tmp_880 = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_879),ctypes.byref(__tmp_880))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    barvaridx = numpy.zeros(__tmp_879.value,numpy.int32)
    __tmp_883 = ctypes.c_int32()
    __tmp_884 = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_883),ctypes.byref(__tmp_884))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    ptrterm = numpy.zeros(__tmp_883.value,numpy.int64)
    __tmp_887 = ctypes.c_int32()
    __tmp_888 = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_887),ctypes.byref(__tmp_888))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    numterm = numpy.zeros(__tmp_887.value,numpy.int64)
    __tmp_891 = ctypes.c_int32()
    __tmp_892 = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_891),ctypes.byref(__tmp_892))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    termidx = numpy.zeros(__tmp_892.value,numpy.int64)
    __tmp_895 = ctypes.c_int32()
    __tmp_896 = ctypes.c_int64()
    _res_getafebarfrowinfo = __library__.MSK_getafebarfrowinfo(self.__nativep,afeidx,ctypes.byref(__tmp_895),ctypes.byref(__tmp_896))
    if _res_getafebarfrowinfo != 0:
      _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
      raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
    termweight = numpy.zeros(__tmp_896.value,numpy.float64)
    _res_getafebarfrow = __library__.MSK_getafebarfrow(self.__nativep,afeidx,ctypes.cast(barvaridx.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(ptrterm.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(numterm.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(termidx.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(termweight.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getafebarfrow != 0:
      _,_msg_getafebarfrow = self.__getlasterror(_res_getafebarfrow)
      raise Error(rescode(_res_getafebarfrow),_msg_getafebarfrow)
    return (barvaridx,ptrterm,numterm,termidx,termweight)
  def getafebarfrow(self,*args,**kwds):
    """
    Obtains nonzero entries in one row of barF.
  
    getafebarfrow(afeidx,
                  barvaridx,
                  ptrterm,
                  numterm,
                  termidx,
                  termweight)
    getafebarfrow(afeidx) -> 
                 (barvaridx,
                  ptrterm,
                  numterm,
                  termidx,
                  termweight)
      [afeidx : int64]  Row index of barF.  
      [barvaridx : array(int32)]  Semidefinite variable indices.  
      [numterm : array(int64)]  Number of terms in each entry.  
      [ptrterm : array(int64)]  Pointers to the description of entries.  
      [termidx : array(int64)]  Indices of semidefinite matrices from E.  
      [termweight : array(float64)]  Weights appearing in the weighted sum representation.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 7: return self.__getafebarfrow_7(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getafebarfrow_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putafeg_3(self,afeidx,g):
    _res_putafeg = __library__.MSK_putafeg(self.__nativep,afeidx,g)
    if _res_putafeg != 0:
      _,_msg_putafeg = self.__getlasterror(_res_putafeg)
      raise Error(rescode(_res_putafeg),_msg_putafeg)
  def putafeg(self,*args,**kwds):
    """
    Replaces one element in the g vector in the affine expressions.
  
    putafeg(afeidx,g)
      [afeidx : int64]  Row index.  
      [g : float64]  New value for the element of g.  
    """
    return self.__putafeg_3(*args,**kwds)
  def __putafeglist_3(self,afeidx,g):
    numafeidx = min(len(afeidx) if afeidx is not None else 0,len(g) if g is not None else 0)
    copyback_afeidx = False
    if afeidx is None:
      afeidx_ = None
      _tmparray_afeidx_ = None
    else:
      _tmparray_afeidx_ = (ctypes.c_int64*len(afeidx))(*afeidx)
    copyback_g = False
    if g is None:
      g_ = None
      _tmparray_g_ = None
    else:
      _tmparray_g_ = (ctypes.c_double*len(g))(*g)
    _res_putafeglist = __library__.MSK_putafeglist(self.__nativep,numafeidx,_tmparray_afeidx_,_tmparray_g_)
    if _res_putafeglist != 0:
      _,_msg_putafeglist = self.__getlasterror(_res_putafeglist)
      raise Error(rescode(_res_putafeglist),_msg_putafeglist)
  def putafeglist(self,*args,**kwds):
    """
    Replaces a list of elements in the g vector in the affine expressions.
  
    putafeglist(afeidx,g)
      [afeidx : array(int64)]  Indices of entries in g.  
      [g : array(float64)]  New values for the elements of g.  
    """
    return self.__putafeglist_3(*args,**kwds)
  def __getafeg_2(self,afeidx):
    g_ = ctypes.c_double()
    _res_getafeg = __library__.MSK_getafeg(self.__nativep,afeidx,ctypes.byref(g_))
    if _res_getafeg != 0:
      _,_msg_getafeg = self.__getlasterror(_res_getafeg)
      raise Error(rescode(_res_getafeg),_msg_getafeg)
    g = g_.value
    return (g_.value)
  def getafeg(self,*args,**kwds):
    """
    Obtains a single coefficient in g.
  
    getafeg(afeidx) -> (g)
      [afeidx : int64]  Element index.  
      [g : float64]  The entry in g.  
    """
    return self.__getafeg_2(*args,**kwds)
  def __getafegslice_4(self,first,last,g):
    copyback_g = False
    if g is None:
      g_ = None
      _tmparray_g_ = None
    else:
      if len(g) < int((last - first)):
        raise ValueError("argument g is too short")
      _tmparray_g_ = (ctypes.c_double*len(g))(*g)
    _res_getafegslice = __library__.MSK_getafegslice(self.__nativep,first,last,_tmparray_g_)
    if _res_getafegslice != 0:
      _,_msg_getafegslice = self.__getlasterror(_res_getafegslice)
      raise Error(rescode(_res_getafegslice),_msg_getafegslice)
    if g is not None:
      for __tmp_899,__tmp_900 in enumerate(_tmparray_g_):
        g[__tmp_899] = __tmp_900
  def __getafegslice_3(self,first,last):
    g = numpy.zeros((last - first),numpy.float64)
    _res_getafegslice = __library__.MSK_getafegslice(self.__nativep,first,last,ctypes.cast(g.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getafegslice != 0:
      _,_msg_getafegslice = self.__getlasterror(_res_getafegslice)
      raise Error(rescode(_res_getafegslice),_msg_getafegslice)
    return (g)
  def getafegslice(self,*args,**kwds):
    """
    Obtains a sequence of coefficients from the vector g.
  
    getafegslice(first,last,g)
    getafegslice(first,last) -> (g)
      [first : int64]  First index in the sequence.  
      [g : array(float64)]  The slice of g as a dense vector.  
      [last : int64]  Last index plus 1 in the sequence.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getafegslice_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 3: return self.__getafegslice_3(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putafegslice_4(self,first,last,slice):
    copyback_slice = False
    if slice is None:
      slice_ = None
      _tmparray_slice_ = None
    else:
      if len(slice) < int((last - first)):
        raise ValueError("argument slice is too short")
      _tmparray_slice_ = (ctypes.c_double*len(slice))(*slice)
    _res_putafegslice = __library__.MSK_putafegslice(self.__nativep,first,last,_tmparray_slice_)
    if _res_putafegslice != 0:
      _,_msg_putafegslice = self.__getlasterror(_res_putafegslice)
      raise Error(rescode(_res_putafegslice),_msg_putafegslice)
  def putafegslice(self,*args,**kwds):
    """
    Modifies a slice of the vector g.
  
    putafegslice(first,last,slice)
      [first : int64]  First index in the sequence.  
      [last : int64]  Last index plus 1 in the sequence.  
      [slice : array(float64)]  The slice of g as a dense vector.  
    """
    return self.__putafegslice_4(*args,**kwds)
  def __putmaxnumdjc_2(self,maxnumdjc):
    _res_putmaxnumdjc = __library__.MSK_putmaxnumdjc(self.__nativep,maxnumdjc)
    if _res_putmaxnumdjc != 0:
      _,_msg_putmaxnumdjc = self.__getlasterror(_res_putmaxnumdjc)
      raise Error(rescode(_res_putmaxnumdjc),_msg_putmaxnumdjc)
  def putmaxnumdjc(self,*args,**kwds):
    """
    Sets the number of preallocated disjunctive constraints.
  
    putmaxnumdjc(maxnumdjc)
      [maxnumdjc : int64]  Number of preallocated disjunctive constraints in the task.  
    """
    return self.__putmaxnumdjc_2(*args,**kwds)
  def __getnumdjc_1(self):
    num_ = ctypes.c_int64()
    _res_getnumdjc = __library__.MSK_getnumdjc(self.__nativep,ctypes.byref(num_))
    if _res_getnumdjc != 0:
      _,_msg_getnumdjc = self.__getlasterror(_res_getnumdjc)
      raise Error(rescode(_res_getnumdjc),_msg_getnumdjc)
    num = num_.value
    return (num_.value)
  def getnumdjc(self,*args,**kwds):
    """
    Obtains the number of disjunctive constraints.
  
    getnumdjc() -> (num)
      [num : int64]  The number of disjunctive constraints.  
    """
    return self.__getnumdjc_1(*args,**kwds)
  def __getdjcnumdomain_2(self,djcidx):
    numdomain_ = ctypes.c_int64()
    _res_getdjcnumdomain = __library__.MSK_getdjcnumdomain(self.__nativep,djcidx,ctypes.byref(numdomain_))
    if _res_getdjcnumdomain != 0:
      _,_msg_getdjcnumdomain = self.__getlasterror(_res_getdjcnumdomain)
      raise Error(rescode(_res_getdjcnumdomain),_msg_getdjcnumdomain)
    numdomain = numdomain_.value
    return (numdomain_.value)
  def getdjcnumdomain(self,*args,**kwds):
    """
    Obtains the number of domains in the disjunctive constraint.
  
    getdjcnumdomain(djcidx) -> (numdomain)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [numdomain : int64]  Number of domains in the disjunctive constraint.  
    """
    return self.__getdjcnumdomain_2(*args,**kwds)
  def __getdjcnumdomaintot_1(self):
    numdomaintot_ = ctypes.c_int64()
    _res_getdjcnumdomaintot = __library__.MSK_getdjcnumdomaintot(self.__nativep,ctypes.byref(numdomaintot_))
    if _res_getdjcnumdomaintot != 0:
      _,_msg_getdjcnumdomaintot = self.__getlasterror(_res_getdjcnumdomaintot)
      raise Error(rescode(_res_getdjcnumdomaintot),_msg_getdjcnumdomaintot)
    numdomaintot = numdomaintot_.value
    return (numdomaintot_.value)
  def getdjcnumdomaintot(self,*args,**kwds):
    """
    Obtains the number of domains in all disjunctive constraints.
  
    getdjcnumdomaintot() -> (numdomaintot)
      [numdomaintot : int64]  Number of domains in all disjunctive constraints.  
    """
    return self.__getdjcnumdomaintot_1(*args,**kwds)
  def __getdjcnumafe_2(self,djcidx):
    numafe_ = ctypes.c_int64()
    _res_getdjcnumafe = __library__.MSK_getdjcnumafe(self.__nativep,djcidx,ctypes.byref(numafe_))
    if _res_getdjcnumafe != 0:
      _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
      raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
    numafe = numafe_.value
    return (numafe_.value)
  def getdjcnumafe(self,*args,**kwds):
    """
    Obtains the number of affine expressions in the disjunctive constraint.
  
    getdjcnumafe(djcidx) -> (numafe)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [numafe : int64]  Number of affine expressions in the disjunctive constraint.  
    """
    return self.__getdjcnumafe_2(*args,**kwds)
  def __getdjcnumafetot_1(self):
    numafetot_ = ctypes.c_int64()
    _res_getdjcnumafetot = __library__.MSK_getdjcnumafetot(self.__nativep,ctypes.byref(numafetot_))
    if _res_getdjcnumafetot != 0:
      _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
      raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
    numafetot = numafetot_.value
    return (numafetot_.value)
  def getdjcnumafetot(self,*args,**kwds):
    """
    Obtains the number of affine expressions in all disjunctive constraints.
  
    getdjcnumafetot() -> (numafetot)
      [numafetot : int64]  Number of affine expressions in all disjunctive constraints.  
    """
    return self.__getdjcnumafetot_1(*args,**kwds)
  def __getdjcnumterm_2(self,djcidx):
    numterm_ = ctypes.c_int64()
    _res_getdjcnumterm = __library__.MSK_getdjcnumterm(self.__nativep,djcidx,ctypes.byref(numterm_))
    if _res_getdjcnumterm != 0:
      _,_msg_getdjcnumterm = self.__getlasterror(_res_getdjcnumterm)
      raise Error(rescode(_res_getdjcnumterm),_msg_getdjcnumterm)
    numterm = numterm_.value
    return (numterm_.value)
  def getdjcnumterm(self,*args,**kwds):
    """
    Obtains the number terms in the disjunctive constraint.
  
    getdjcnumterm(djcidx) -> (numterm)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [numterm : int64]  Number of terms in the disjunctive constraint.  
    """
    return self.__getdjcnumterm_2(*args,**kwds)
  def __getdjcnumtermtot_1(self):
    numtermtot_ = ctypes.c_int64()
    _res_getdjcnumtermtot = __library__.MSK_getdjcnumtermtot(self.__nativep,ctypes.byref(numtermtot_))
    if _res_getdjcnumtermtot != 0:
      _,_msg_getdjcnumtermtot = self.__getlasterror(_res_getdjcnumtermtot)
      raise Error(rescode(_res_getdjcnumtermtot),_msg_getdjcnumtermtot)
    numtermtot = numtermtot_.value
    return (numtermtot_.value)
  def getdjcnumtermtot(self,*args,**kwds):
    """
    Obtains the number of terms in all disjunctive constraints.
  
    getdjcnumtermtot() -> (numtermtot)
      [numtermtot : int64]  Total number of terms in all disjunctive constraints.  
    """
    return self.__getdjcnumtermtot_1(*args,**kwds)
  def __putmaxnumacc_2(self,maxnumacc):
    _res_putmaxnumacc = __library__.MSK_putmaxnumacc(self.__nativep,maxnumacc)
    if _res_putmaxnumacc != 0:
      _,_msg_putmaxnumacc = self.__getlasterror(_res_putmaxnumacc)
      raise Error(rescode(_res_putmaxnumacc),_msg_putmaxnumacc)
  def putmaxnumacc(self,*args,**kwds):
    """
    Sets the number of preallocated affine conic constraints.
  
    putmaxnumacc(maxnumacc)
      [maxnumacc : int64]  Number of preallocated affine conic constraints.  
    """
    return self.__putmaxnumacc_2(*args,**kwds)
  def __getnumacc_1(self):
    num_ = ctypes.c_int64()
    _res_getnumacc = __library__.MSK_getnumacc(self.__nativep,ctypes.byref(num_))
    if _res_getnumacc != 0:
      _,_msg_getnumacc = self.__getlasterror(_res_getnumacc)
      raise Error(rescode(_res_getnumacc),_msg_getnumacc)
    num = num_.value
    return (num_.value)
  def getnumacc(self,*args,**kwds):
    """
    Obtains the number of affine conic constraints.
  
    getnumacc() -> (num)
      [num : int64]  The number of affine conic constraints.  
    """
    return self.__getnumacc_1(*args,**kwds)
  def __appendacc_4(self,domidx,afeidxlist,b):
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_appendacc = __library__.MSK_appendacc(self.__nativep,domidx,numafeidx,_tmparray_afeidxlist_,_tmparray_b_)
    if _res_appendacc != 0:
      _,_msg_appendacc = self.__getlasterror(_res_appendacc)
      raise Error(rescode(_res_appendacc),_msg_appendacc)
  def appendacc(self,*args,**kwds):
    """
    Appends an affine conic constraint to the task.
  
    appendacc(domidx,afeidxlist,b)
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidx : int64]  Domain index.  
    """
    return self.__appendacc_4(*args,**kwds)
  def __appendaccs_4(self,domidxs,afeidxlist,b):
    numaccs = len(domidxs) if domidxs is not None else 0
    copyback_domidxs = False
    if domidxs is None:
      domidxs_ = None
      _tmparray_domidxs_ = None
    else:
      _tmparray_domidxs_ = (ctypes.c_int64*len(domidxs))(*domidxs)
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_appendaccs = __library__.MSK_appendaccs(self.__nativep,numaccs,_tmparray_domidxs_,numafeidx,_tmparray_afeidxlist_,_tmparray_b_)
    if _res_appendaccs != 0:
      _,_msg_appendaccs = self.__getlasterror(_res_appendaccs)
      raise Error(rescode(_res_appendaccs),_msg_appendaccs)
  def appendaccs(self,*args,**kwds):
    """
    Appends a number of affine conic constraint to the task.
  
    appendaccs(domidxs,afeidxlist,b)
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidxs : array(int64)]  Domain indices.  
    """
    return self.__appendaccs_4(*args,**kwds)
  def __appendaccseq_4(self,domidx,afeidxfirst,b):
    __tmp_902 = ctypes.c_int64()
    _res_getdomainn = __library__.MSK_getdomainn(self.__nativep,domidx,ctypes.byref(__tmp_902))
    if _res_getdomainn != 0:
      _,_msg_getdomainn = self.__getlasterror(_res_getdomainn)
      raise Error(rescode(_res_getdomainn),_msg_getdomainn)
    numafeidx = __tmp_902.value;
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_appendaccseq = __library__.MSK_appendaccseq(self.__nativep,domidx,numafeidx,afeidxfirst,_tmparray_b_)
    if _res_appendaccseq != 0:
      _,_msg_appendaccseq = self.__getlasterror(_res_appendaccseq)
      raise Error(rescode(_res_appendaccseq),_msg_appendaccseq)
  def appendaccseq(self,*args,**kwds):
    """
    Appends an affine conic constraint to the task.
  
    appendaccseq(domidx,afeidxfirst,b)
      [afeidxfirst : int64]  Index of the first affine expression.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidx : int64]  Domain index.  
    """
    return self.__appendaccseq_4(*args,**kwds)
  def __appendaccsseq_5(self,domidxs,numafeidx,afeidxfirst,b):
    numaccs = len(domidxs) if domidxs is not None else 0
    copyback_domidxs = False
    if domidxs is None:
      domidxs_ = None
      _tmparray_domidxs_ = None
    else:
      _tmparray_domidxs_ = (ctypes.c_int64*len(domidxs))(*domidxs)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_appendaccsseq = __library__.MSK_appendaccsseq(self.__nativep,numaccs,_tmparray_domidxs_,numafeidx,afeidxfirst,_tmparray_b_)
    if _res_appendaccsseq != 0:
      _,_msg_appendaccsseq = self.__getlasterror(_res_appendaccsseq)
      raise Error(rescode(_res_appendaccsseq),_msg_appendaccsseq)
  def appendaccsseq(self,*args,**kwds):
    """
    Appends a number of affine conic constraint to the task.
  
    appendaccsseq(domidxs,numafeidx,afeidxfirst,b)
      [afeidxfirst : int64]  Index of the first affine expression.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidxs : array(int64)]  Domain indices.  
      [numafeidx : int64]  Number of affine expressions in the affine expression list (must equal the sum of dimensions of the domains).  
    """
    return self.__appendaccsseq_5(*args,**kwds)
  def __putacc_5(self,accidx,domidx,afeidxlist,b):
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_putacc = __library__.MSK_putacc(self.__nativep,accidx,domidx,numafeidx,_tmparray_afeidxlist_,_tmparray_b_)
    if _res_putacc != 0:
      _,_msg_putacc = self.__getlasterror(_res_putacc)
      raise Error(rescode(_res_putacc),_msg_putacc)
  def putacc(self,*args,**kwds):
    """
    Puts an affine conic constraint.
  
    putacc(accidx,domidx,afeidxlist,b)
      [accidx : int64]  Affine conic constraint index.  
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidx : int64]  Domain index.  
    """
    return self.__putacc_5(*args,**kwds)
  def __putacclist_5(self,accidxs,domidxs,afeidxlist,b):
    numaccs = min(len(domidxs) if domidxs is not None else 0,len(accidxs) if accidxs is not None else 0)
    copyback_accidxs = False
    if accidxs is None:
      accidxs_ = None
      _tmparray_accidxs_ = None
    else:
      _tmparray_accidxs_ = (ctypes.c_int64*len(accidxs))(*accidxs)
    copyback_domidxs = False
    if domidxs is None:
      domidxs_ = None
      _tmparray_domidxs_ = None
    else:
      _tmparray_domidxs_ = (ctypes.c_int64*len(domidxs))(*domidxs)
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_putacclist = __library__.MSK_putacclist(self.__nativep,numaccs,_tmparray_accidxs_,_tmparray_domidxs_,numafeidx,_tmparray_afeidxlist_,_tmparray_b_)
    if _res_putacclist != 0:
      _,_msg_putacclist = self.__getlasterror(_res_putacclist)
      raise Error(rescode(_res_putacclist),_msg_putacclist)
  def putacclist(self,*args,**kwds):
    """
    Puts a number of affine conic constraints.
  
    putacclist(accidxs,domidxs,afeidxlist,b)
      [accidxs : array(int64)]  Affine conic constraint indices.  
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      [domidxs : array(int64)]  Domain indices.  
    """
    return self.__putacclist_5(*args,**kwds)
  def __putaccb_3(self,accidx,b):
    lengthb = len(b) if b is not None else 0
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_putaccb = __library__.MSK_putaccb(self.__nativep,accidx,lengthb,_tmparray_b_)
    if _res_putaccb != 0:
      _,_msg_putaccb = self.__getlasterror(_res_putaccb)
      raise Error(rescode(_res_putaccb),_msg_putaccb)
  def putaccb(self,*args,**kwds):
    """
    Puts the constant vector b in an affine conic constraint.
  
    putaccb(accidx,b)
      [accidx : int64]  Affine conic constraint index.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
    """
    return self.__putaccb_3(*args,**kwds)
  def __putaccbj_4(self,accidx,j,bj):
    _res_putaccbj = __library__.MSK_putaccbj(self.__nativep,accidx,j,bj)
    if _res_putaccbj != 0:
      _,_msg_putaccbj = self.__getlasterror(_res_putaccbj)
      raise Error(rescode(_res_putaccbj),_msg_putaccbj)
  def putaccbj(self,*args,**kwds):
    """
    Sets one element in the b vector of an affine conic constraint.
  
    putaccbj(accidx,j,bj)
      [accidx : int64]  Affine conic constraint index.  
      [bj : float64]  The new value of b[j].  
      [j : int64]  The index of an element in b to change.  
    """
    return self.__putaccbj_4(*args,**kwds)
  def __getaccdomain_2(self,accidx):
    domidx_ = ctypes.c_int64()
    _res_getaccdomain = __library__.MSK_getaccdomain(self.__nativep,accidx,ctypes.byref(domidx_))
    if _res_getaccdomain != 0:
      _,_msg_getaccdomain = self.__getlasterror(_res_getaccdomain)
      raise Error(rescode(_res_getaccdomain),_msg_getaccdomain)
    domidx = domidx_.value
    return (domidx_.value)
  def getaccdomain(self,*args,**kwds):
    """
    Obtains the domain appearing in the affine conic constraint.
  
    getaccdomain(accidx) -> (domidx)
      [accidx : int64]  The index of the affine conic constraint.  
      [domidx : int64]  The index of domain in the affine conic constraint.  
    """
    return self.__getaccdomain_2(*args,**kwds)
  def __getaccn_2(self,accidx):
    n_ = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(n_))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    n = n_.value
    return (n_.value)
  def getaccn(self,*args,**kwds):
    """
    Obtains the dimension of the affine conic constraint.
  
    getaccn(accidx) -> (n)
      [accidx : int64]  The index of the affine conic constraint.  
      [n : int64]  The dimension of the affine conic constraint (equal to the dimension of its domain).  
    """
    return self.__getaccn_2(*args,**kwds)
  def __getaccntot_1(self):
    n_ = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(n_))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    n = n_.value
    return (n_.value)
  def getaccntot(self,*args,**kwds):
    """
    Obtains the total dimension of all affine conic constraints.
  
    getaccntot() -> (n)
      [n : int64]  The total dimension of all affine conic constraints.  
    """
    return self.__getaccntot_1(*args,**kwds)
  def __getaccafeidxlist_3(self,accidx,afeidxlist):
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      __tmp_906 = ctypes.c_int64()
      _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_906))
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      if len(afeidxlist) < int(__tmp_906.value):
        raise ValueError("argument afeidxlist is too short")
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    _res_getaccafeidxlist = __library__.MSK_getaccafeidxlist(self.__nativep,accidx,_tmparray_afeidxlist_)
    if _res_getaccafeidxlist != 0:
      _,_msg_getaccafeidxlist = self.__getlasterror(_res_getaccafeidxlist)
      raise Error(rescode(_res_getaccafeidxlist),_msg_getaccafeidxlist)
    if afeidxlist is not None:
      for __tmp_908,__tmp_909 in enumerate(_tmparray_afeidxlist_):
        afeidxlist[__tmp_908] = __tmp_909
  def __getaccafeidxlist_2(self,accidx):
    __tmp_910 = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_910))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    afeidxlist = numpy.zeros(__tmp_910.value,numpy.int64)
    _res_getaccafeidxlist = __library__.MSK_getaccafeidxlist(self.__nativep,accidx,ctypes.cast(afeidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getaccafeidxlist != 0:
      _,_msg_getaccafeidxlist = self.__getlasterror(_res_getaccafeidxlist)
      raise Error(rescode(_res_getaccafeidxlist),_msg_getaccafeidxlist)
    return (afeidxlist)
  def getaccafeidxlist(self,*args,**kwds):
    """
    Obtains the list of affine expressions appearing in the affine conic constraint.
  
    getaccafeidxlist(accidx,afeidxlist)
    getaccafeidxlist(accidx) -> (afeidxlist)
      [accidx : int64]  Index of the affine conic constraint.  
      [afeidxlist : array(int64)]  List of indexes of affine expressions appearing in the constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getaccafeidxlist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getaccafeidxlist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccb_3(self,accidx,b):
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      __tmp_913 = ctypes.c_int64()
      _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_913))
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      if len(b) < int(__tmp_913.value):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_getaccb = __library__.MSK_getaccb(self.__nativep,accidx,_tmparray_b_)
    if _res_getaccb != 0:
      _,_msg_getaccb = self.__getlasterror(_res_getaccb)
      raise Error(rescode(_res_getaccb),_msg_getaccb)
    if b is not None:
      for __tmp_915,__tmp_916 in enumerate(_tmparray_b_):
        b[__tmp_915] = __tmp_916
  def __getaccb_2(self,accidx):
    __tmp_917 = ctypes.c_int64()
    _res_getaccn = __library__.MSK_getaccn(self.__nativep,accidx,ctypes.byref(__tmp_917))
    if _res_getaccn != 0:
      _,_msg_getaccn = self.__getlasterror(_res_getaccn)
      raise Error(rescode(_res_getaccn),_msg_getaccn)
    b = numpy.zeros(__tmp_917.value,numpy.float64)
    _res_getaccb = __library__.MSK_getaccb(self.__nativep,accidx,ctypes.cast(b.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccb != 0:
      _,_msg_getaccb = self.__getlasterror(_res_getaccb)
      raise Error(rescode(_res_getaccb),_msg_getaccb)
    return (b)
  def getaccb(self,*args,**kwds):
    """
    Obtains the additional constant term vector appearing in the affine conic constraint.
  
    getaccb(accidx,b)
    getaccb(accidx) -> (b)
      [accidx : int64]  Index of the affine conic constraint.  
      [b : array(float64)]  The vector b appearing in the constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getaccb_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getaccb_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccs_4(self,domidxlist,afeidxlist,b):
    copyback_domidxlist = False
    if domidxlist is None:
      domidxlist_ = None
      _tmparray_domidxlist_ = None
    else:
      __tmp_920 = ctypes.c_int64()
      _res_getnumacc = __library__.MSK_getnumacc(self.__nativep,ctypes.byref(__tmp_920))
      if _res_getnumacc != 0:
        _,_msg_getnumacc = self.__getlasterror(_res_getnumacc)
        raise Error(rescode(_res_getnumacc),_msg_getnumacc)
      if len(domidxlist) < int(__tmp_920.value):
        raise ValueError("argument domidxlist is too short")
      _tmparray_domidxlist_ = (ctypes.c_int64*len(domidxlist))(*domidxlist)
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      __tmp_924 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_924))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(afeidxlist) < int(__tmp_924.value):
        raise ValueError("argument afeidxlist is too short")
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      __tmp_928 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_928))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(b) < int(__tmp_928.value):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_getaccs = __library__.MSK_getaccs(self.__nativep,_tmparray_domidxlist_,_tmparray_afeidxlist_,_tmparray_b_)
    if _res_getaccs != 0:
      _,_msg_getaccs = self.__getlasterror(_res_getaccs)
      raise Error(rescode(_res_getaccs),_msg_getaccs)
    if domidxlist is not None:
      for __tmp_922,__tmp_923 in enumerate(_tmparray_domidxlist_):
        domidxlist[__tmp_922] = __tmp_923
    if afeidxlist is not None:
      for __tmp_926,__tmp_927 in enumerate(_tmparray_afeidxlist_):
        afeidxlist[__tmp_926] = __tmp_927
    if b is not None:
      for __tmp_930,__tmp_931 in enumerate(_tmparray_b_):
        b[__tmp_930] = __tmp_931
  def __getaccs_1(self):
    __tmp_932 = ctypes.c_int64()
    _res_getnumacc = __library__.MSK_getnumacc(self.__nativep,ctypes.byref(__tmp_932))
    if _res_getnumacc != 0:
      _,_msg_getnumacc = self.__getlasterror(_res_getnumacc)
      raise Error(rescode(_res_getnumacc),_msg_getnumacc)
    domidxlist = numpy.zeros(__tmp_932.value,numpy.int64)
    __tmp_935 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_935))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    afeidxlist = numpy.zeros(__tmp_935.value,numpy.int64)
    __tmp_938 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_938))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    b = numpy.zeros(__tmp_938.value,numpy.float64)
    _res_getaccs = __library__.MSK_getaccs(self.__nativep,ctypes.cast(domidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(afeidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(b.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccs != 0:
      _,_msg_getaccs = self.__getlasterror(_res_getaccs)
      raise Error(rescode(_res_getaccs),_msg_getaccs)
    return (domidxlist,afeidxlist,b)
  def getaccs(self,*args,**kwds):
    """
    Obtains full data of all affine conic constraints.
  
    getaccs(domidxlist,afeidxlist,b)
    getaccs() -> (domidxlist,afeidxlist,b)
      [afeidxlist : array(int64)]  The concatenation of index lists of affine expressions appearing in all affine conic constraints.  
      [b : array(float64)]  The concatenation of vectors b appearing in all affine conic constraints.  
      [domidxlist : array(int64)]  The list of domains appearing in all affine conic constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getaccs_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getaccs_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccfnumnz_1(self):
    accfnnz_ = ctypes.c_int64()
    _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(accfnnz_))
    if _res_getaccfnumnz != 0:
      _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
      raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
    accfnnz = accfnnz_.value
    return (accfnnz_.value)
  def getaccfnumnz(self,*args,**kwds):
    """
    Obtains the total number of nonzeros in the ACC implied F matrix.
  
    getaccfnumnz() -> (accfnnz)
      [accfnnz : int64]  Number of nonzeros in the F matrix implied by ACCs.  
    """
    return self.__getaccfnumnz_1(*args,**kwds)
  def __getaccftrip_4(self,frow,fcol,fval):
    copyback_frow = False
    if frow is None:
      frow_ = None
      _tmparray_frow_ = None
    else:
      __tmp_941 = ctypes.c_int64()
      _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_941))
      if _res_getaccfnumnz != 0:
        _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
        raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
      if len(frow) < int(__tmp_941.value):
        raise ValueError("argument frow is too short")
      _tmparray_frow_ = (ctypes.c_int64*len(frow))(*frow)
    copyback_fcol = False
    if fcol is None:
      fcol_ = None
      _tmparray_fcol_ = None
    else:
      __tmp_945 = ctypes.c_int64()
      _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_945))
      if _res_getaccfnumnz != 0:
        _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
        raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
      if len(fcol) < int(__tmp_945.value):
        raise ValueError("argument fcol is too short")
      _tmparray_fcol_ = (ctypes.c_int32*len(fcol))(*fcol)
    copyback_fval = False
    if fval is None:
      fval_ = None
      _tmparray_fval_ = None
    else:
      __tmp_949 = ctypes.c_int64()
      _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_949))
      if _res_getaccfnumnz != 0:
        _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
        raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
      if len(fval) < int(__tmp_949.value):
        raise ValueError("argument fval is too short")
      _tmparray_fval_ = (ctypes.c_double*len(fval))(*fval)
    _res_getaccftrip = __library__.MSK_getaccftrip(self.__nativep,_tmparray_frow_,_tmparray_fcol_,_tmparray_fval_)
    if _res_getaccftrip != 0:
      _,_msg_getaccftrip = self.__getlasterror(_res_getaccftrip)
      raise Error(rescode(_res_getaccftrip),_msg_getaccftrip)
    if frow is not None:
      for __tmp_943,__tmp_944 in enumerate(_tmparray_frow_):
        frow[__tmp_943] = __tmp_944
    if fcol is not None:
      for __tmp_947,__tmp_948 in enumerate(_tmparray_fcol_):
        fcol[__tmp_947] = __tmp_948
    if fval is not None:
      for __tmp_951,__tmp_952 in enumerate(_tmparray_fval_):
        fval[__tmp_951] = __tmp_952
  def __getaccftrip_1(self):
    __tmp_953 = ctypes.c_int64()
    _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_953))
    if _res_getaccfnumnz != 0:
      _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
      raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
    frow = numpy.zeros(__tmp_953.value,numpy.int64)
    __tmp_956 = ctypes.c_int64()
    _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_956))
    if _res_getaccfnumnz != 0:
      _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
      raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
    fcol = numpy.zeros(__tmp_956.value,numpy.int32)
    __tmp_959 = ctypes.c_int64()
    _res_getaccfnumnz = __library__.MSK_getaccfnumnz(self.__nativep,ctypes.byref(__tmp_959))
    if _res_getaccfnumnz != 0:
      _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
      raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
    fval = numpy.zeros(__tmp_959.value,numpy.float64)
    _res_getaccftrip = __library__.MSK_getaccftrip(self.__nativep,ctypes.cast(frow.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(fcol.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(fval.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccftrip != 0:
      _,_msg_getaccftrip = self.__getlasterror(_res_getaccftrip)
      raise Error(rescode(_res_getaccftrip),_msg_getaccftrip)
    return (frow,fcol,fval)
  def getaccftrip(self,*args,**kwds):
    """
    Obtains the F matrix (implied by the AFE ordering within the ACCs) in triplet format.
  
    getaccftrip(frow,fcol,fval)
    getaccftrip() -> (frow,fcol,fval)
      [fcol : array(int32)]  Column indices of nonzeros in the implied F matrix.  
      [frow : array(int64)]  Row indices of nonzeros in the implied F matrix.  
      [fval : array(float64)]  Values of nonzero entries in the implied F matrix.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 4: return self.__getaccftrip_4(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getaccftrip_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccgvector_2(self,g):
    copyback_g = False
    if g is None:
      g_ = None
      _tmparray_g_ = None
    else:
      __tmp_962 = ctypes.c_int64()
      _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_962))
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      if len(g) < int(__tmp_962.value):
        raise ValueError("argument g is too short")
      _tmparray_g_ = (ctypes.c_double*len(g))(*g)
    _res_getaccgvector = __library__.MSK_getaccgvector(self.__nativep,_tmparray_g_)
    if _res_getaccgvector != 0:
      _,_msg_getaccgvector = self.__getlasterror(_res_getaccgvector)
      raise Error(rescode(_res_getaccgvector),_msg_getaccgvector)
    if g is not None:
      for __tmp_964,__tmp_965 in enumerate(_tmparray_g_):
        g[__tmp_964] = __tmp_965
  def __getaccgvector_1(self):
    __tmp_966 = ctypes.c_int64()
    _res_getaccntot = __library__.MSK_getaccntot(self.__nativep,ctypes.byref(__tmp_966))
    if _res_getaccntot != 0:
      _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
      raise Error(rescode(_res_getaccntot),_msg_getaccntot)
    g = numpy.zeros(__tmp_966.value,numpy.float64)
    _res_getaccgvector = __library__.MSK_getaccgvector(self.__nativep,ctypes.cast(g.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccgvector != 0:
      _,_msg_getaccgvector = self.__getlasterror(_res_getaccgvector)
      raise Error(rescode(_res_getaccgvector),_msg_getaccgvector)
    return (g)
  def getaccgvector(self,*args,**kwds):
    """
    The g vector as used within the ACCs.
  
    getaccgvector(g)
    getaccgvector() -> (g)
      [g : array(float64)]  The g vector as used within the ACCs.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 2: return self.__getaccgvector_2(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getaccgvector_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getaccbarfnumblocktriplets_1(self):
    numtrip_ = ctypes.c_int64()
    _res_getaccbarfnumblocktriplets = __library__.MSK_getaccbarfnumblocktriplets(self.__nativep,ctypes.byref(numtrip_))
    if _res_getaccbarfnumblocktriplets != 0:
      _,_msg_getaccbarfnumblocktriplets = self.__getlasterror(_res_getaccbarfnumblocktriplets)
      raise Error(rescode(_res_getaccbarfnumblocktriplets),_msg_getaccbarfnumblocktriplets)
    numtrip = numtrip_.value
    return (numtrip_.value)
  def getaccbarfnumblocktriplets(self,*args,**kwds):
    """
    Obtains an upper bound on the number of elements in the block triplet form of barf, as used within the ACCs.
  
    getaccbarfnumblocktriplets() -> (numtrip)
      [numtrip : int64]  An upper bound on the number of elements in the block triplet form of barf, as used within the ACCs.  
    """
    return self.__getaccbarfnumblocktriplets_1(*args,**kwds)
  def __getaccbarfblocktriplet_6(self,acc_afe,bar_var,blk_row,blk_col,blk_val):
    __tmp_969 = ctypes.c_int64()
    _res_getaccbarfnumblocktriplets = __library__.MSK_getaccbarfnumblocktriplets(self.__nativep,ctypes.byref(__tmp_969))
    if _res_getaccbarfnumblocktriplets != 0:
      _,_msg_getaccbarfnumblocktriplets = self.__getlasterror(_res_getaccbarfnumblocktriplets)
      raise Error(rescode(_res_getaccbarfnumblocktriplets),_msg_getaccbarfnumblocktriplets)
    maxnumtrip = __tmp_969.value;
    numtrip_ = ctypes.c_int64()
    copyback_acc_afe = False
    if acc_afe is None:
      acc_afe_ = None
      _tmparray_acc_afe_ = None
    else:
      if len(acc_afe) < int(maxnumtrip):
        raise ValueError("argument acc_afe is too short")
      _tmparray_acc_afe_ = (ctypes.c_int64*len(acc_afe))(*acc_afe)
    copyback_bar_var = False
    if bar_var is None:
      bar_var_ = None
      _tmparray_bar_var_ = None
    else:
      if len(bar_var) < int(maxnumtrip):
        raise ValueError("argument bar_var is too short")
      _tmparray_bar_var_ = (ctypes.c_int32*len(bar_var))(*bar_var)
    copyback_blk_row = False
    if blk_row is None:
      blk_row_ = None
      _tmparray_blk_row_ = None
    else:
      if len(blk_row) < int(maxnumtrip):
        raise ValueError("argument blk_row is too short")
      _tmparray_blk_row_ = (ctypes.c_int32*len(blk_row))(*blk_row)
    copyback_blk_col = False
    if blk_col is None:
      blk_col_ = None
      _tmparray_blk_col_ = None
    else:
      if len(blk_col) < int(maxnumtrip):
        raise ValueError("argument blk_col is too short")
      _tmparray_blk_col_ = (ctypes.c_int32*len(blk_col))(*blk_col)
    copyback_blk_val = False
    if blk_val is None:
      blk_val_ = None
      _tmparray_blk_val_ = None
    else:
      if len(blk_val) < int(maxnumtrip):
        raise ValueError("argument blk_val is too short")
      _tmparray_blk_val_ = (ctypes.c_double*len(blk_val))(*blk_val)
    _res_getaccbarfblocktriplet = __library__.MSK_getaccbarfblocktriplet(self.__nativep,maxnumtrip,ctypes.byref(numtrip_),_tmparray_acc_afe_,_tmparray_bar_var_,_tmparray_blk_row_,_tmparray_blk_col_,_tmparray_blk_val_)
    if _res_getaccbarfblocktriplet != 0:
      _,_msg_getaccbarfblocktriplet = self.__getlasterror(_res_getaccbarfblocktriplet)
      raise Error(rescode(_res_getaccbarfblocktriplet),_msg_getaccbarfblocktriplet)
    numtrip = numtrip_.value
    if acc_afe is not None:
      for __tmp_971,__tmp_972 in enumerate(_tmparray_acc_afe_):
        acc_afe[__tmp_971] = __tmp_972
    if bar_var is not None:
      for __tmp_973,__tmp_974 in enumerate(_tmparray_bar_var_):
        bar_var[__tmp_973] = __tmp_974
    if blk_row is not None:
      for __tmp_975,__tmp_976 in enumerate(_tmparray_blk_row_):
        blk_row[__tmp_975] = __tmp_976
    if blk_col is not None:
      for __tmp_977,__tmp_978 in enumerate(_tmparray_blk_col_):
        blk_col[__tmp_977] = __tmp_978
    if blk_val is not None:
      for __tmp_979,__tmp_980 in enumerate(_tmparray_blk_val_):
        blk_val[__tmp_979] = __tmp_980
    return (numtrip_.value)
  def __getaccbarfblocktriplet_1(self):
    __tmp_981 = ctypes.c_int64()
    _res_getaccbarfnumblocktriplets = __library__.MSK_getaccbarfnumblocktriplets(self.__nativep,ctypes.byref(__tmp_981))
    if _res_getaccbarfnumblocktriplets != 0:
      _,_msg_getaccbarfnumblocktriplets = self.__getlasterror(_res_getaccbarfnumblocktriplets)
      raise Error(rescode(_res_getaccbarfnumblocktriplets),_msg_getaccbarfnumblocktriplets)
    maxnumtrip = __tmp_981.value;
    numtrip_ = ctypes.c_int64()
    acc_afe = numpy.zeros(maxnumtrip,numpy.int64)
    bar_var = numpy.zeros(maxnumtrip,numpy.int32)
    blk_row = numpy.zeros(maxnumtrip,numpy.int32)
    blk_col = numpy.zeros(maxnumtrip,numpy.int32)
    blk_val = numpy.zeros(maxnumtrip,numpy.float64)
    _res_getaccbarfblocktriplet = __library__.MSK_getaccbarfblocktriplet(self.__nativep,maxnumtrip,ctypes.byref(numtrip_),ctypes.cast(acc_afe.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(bar_var.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(blk_row.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(blk_col.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(blk_val.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getaccbarfblocktriplet != 0:
      _,_msg_getaccbarfblocktriplet = self.__getlasterror(_res_getaccbarfblocktriplet)
      raise Error(rescode(_res_getaccbarfblocktriplet),_msg_getaccbarfblocktriplet)
    numtrip = numtrip_.value
    return (numtrip_.value,acc_afe,bar_var,blk_row,blk_col,blk_val)
  def getaccbarfblocktriplet(self,*args,**kwds):
    """
    Obtains barF, implied by the ACCs, in block triplet form.
  
    getaccbarfblocktriplet(acc_afe,bar_var,blk_row,blk_col,blk_val) -> (numtrip)
    getaccbarfblocktriplet() -> 
                          (numtrip,
                           acc_afe,
                           bar_var,
                           blk_row,
                           blk_col,
                           blk_val)
      [acc_afe : array(int64)]  Index of the AFE within the concatenated list of AFEs in ACCs.  
      [bar_var : array(int32)]  Symmetric matrix variable index.  
      [blk_col : array(int32)]  Block column index.  
      [blk_row : array(int32)]  Block row index.  
      [blk_val : array(float64)]  The numerical value associated with each block triplet.  
      [numtrip : int64]  Number of elements in the block triplet form.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getaccbarfblocktriplet_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getaccbarfblocktriplet_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __appenddjcs_2(self,num):
    _res_appenddjcs = __library__.MSK_appenddjcs(self.__nativep,num)
    if _res_appenddjcs != 0:
      _,_msg_appenddjcs = self.__getlasterror(_res_appenddjcs)
      raise Error(rescode(_res_appenddjcs),_msg_appenddjcs)
  def appenddjcs(self,*args,**kwds):
    """
    Appends a number of empty disjunctive constraints to the task.
  
    appenddjcs(num)
      [num : int64]  Number of empty disjunctive constraints which should be appended.  
    """
    return self.__appenddjcs_2(*args,**kwds)
  def __putdjc_6(self,djcidx,domidxlist,afeidxlist,b,termsizelist):
    numdomidx = len(domidxlist) if domidxlist is not None else 0
    copyback_domidxlist = False
    if domidxlist is None:
      domidxlist_ = None
      _tmparray_domidxlist_ = None
    else:
      _tmparray_domidxlist_ = (ctypes.c_int64*len(domidxlist))(*domidxlist)
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    numterms = len(termsizelist) if termsizelist is not None else 0
    copyback_termsizelist = False
    if termsizelist is None:
      termsizelist_ = None
      _tmparray_termsizelist_ = None
    else:
      _tmparray_termsizelist_ = (ctypes.c_int64*len(termsizelist))(*termsizelist)
    _res_putdjc = __library__.MSK_putdjc(self.__nativep,djcidx,numdomidx,_tmparray_domidxlist_,numafeidx,_tmparray_afeidxlist_,_tmparray_b_,numterms,_tmparray_termsizelist_)
    if _res_putdjc != 0:
      _,_msg_putdjc = self.__getlasterror(_res_putdjc)
      raise Error(rescode(_res_putdjc),_msg_putdjc)
  def putdjc(self,*args,**kwds):
    """
    Inputs a disjunctive constraint.
  
    putdjc(djcidx,
           domidxlist,
           afeidxlist,
           b,
           termsizelist)
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions.  
      [djcidx : int64]  Index of the disjunctive constraint.  
      [domidxlist : array(int64)]  List of domain indexes.  
      [termsizelist : array(int64)]  List of term sizes.  
    """
    return self.__putdjc_6(*args,**kwds)
  def __putdjcslice_8(self,idxfirst,idxlast,domidxlist,afeidxlist,b,termsizelist,termsindjc):
    numdomidx = len(domidxlist) if domidxlist is not None else 0
    copyback_domidxlist = False
    if domidxlist is None:
      domidxlist_ = None
      _tmparray_domidxlist_ = None
    else:
      _tmparray_domidxlist_ = (ctypes.c_int64*len(domidxlist))(*domidxlist)
    numafeidx = len(afeidxlist) if afeidxlist is not None else 0
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      if len(b) < int(numafeidx):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    numterms = len(termsizelist) if termsizelist is not None else 0
    copyback_termsizelist = False
    if termsizelist is None:
      termsizelist_ = None
      _tmparray_termsizelist_ = None
    else:
      _tmparray_termsizelist_ = (ctypes.c_int64*len(termsizelist))(*termsizelist)
    copyback_termsindjc = False
    if termsindjc is None:
      termsindjc_ = None
      _tmparray_termsindjc_ = None
    else:
      if len(termsindjc) < int((idxlast - idxfirst)):
        raise ValueError("argument termsindjc is too short")
      _tmparray_termsindjc_ = (ctypes.c_int64*len(termsindjc))(*termsindjc)
    _res_putdjcslice = __library__.MSK_putdjcslice(self.__nativep,idxfirst,idxlast,numdomidx,_tmparray_domidxlist_,numafeidx,_tmparray_afeidxlist_,_tmparray_b_,numterms,_tmparray_termsizelist_,_tmparray_termsindjc_)
    if _res_putdjcslice != 0:
      _,_msg_putdjcslice = self.__getlasterror(_res_putdjcslice)
      raise Error(rescode(_res_putdjcslice),_msg_putdjcslice)
  def putdjcslice(self,*args,**kwds):
    """
    Inputs a slice of disjunctive constraints.
  
    putdjcslice(idxfirst,
                idxlast,
                domidxlist,
                afeidxlist,
                b,
                termsizelist,
                termsindjc)
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, may be NULL.  
      [domidxlist : array(int64)]  List of domain indexes.  
      [idxfirst : int64]  Index of the first disjunctive constraint in the slice.  
      [idxlast : int64]  Index of the last disjunctive constraint in the slice plus 1.  
      [termsindjc : array(int64)]  Number of terms in each of the disjunctive constraints in the slice.  
      [termsizelist : array(int64)]  List of term sizes.  
    """
    return self.__putdjcslice_8(*args,**kwds)
  def __getdjcdomainidxlist_3(self,djcidx,domidxlist):
    copyback_domidxlist = False
    if domidxlist is None:
      domidxlist_ = None
      _tmparray_domidxlist_ = None
    else:
      __tmp_988 = ctypes.c_int64()
      _res_getdjcnumdomain = __library__.MSK_getdjcnumdomain(self.__nativep,djcidx,ctypes.byref(__tmp_988))
      if _res_getdjcnumdomain != 0:
        _,_msg_getdjcnumdomain = self.__getlasterror(_res_getdjcnumdomain)
        raise Error(rescode(_res_getdjcnumdomain),_msg_getdjcnumdomain)
      if len(domidxlist) < int(__tmp_988.value):
        raise ValueError("argument domidxlist is too short")
      _tmparray_domidxlist_ = (ctypes.c_int64*len(domidxlist))(*domidxlist)
    _res_getdjcdomainidxlist = __library__.MSK_getdjcdomainidxlist(self.__nativep,djcidx,_tmparray_domidxlist_)
    if _res_getdjcdomainidxlist != 0:
      _,_msg_getdjcdomainidxlist = self.__getlasterror(_res_getdjcdomainidxlist)
      raise Error(rescode(_res_getdjcdomainidxlist),_msg_getdjcdomainidxlist)
    if domidxlist is not None:
      for __tmp_990,__tmp_991 in enumerate(_tmparray_domidxlist_):
        domidxlist[__tmp_990] = __tmp_991
  def __getdjcdomainidxlist_2(self,djcidx):
    __tmp_992 = ctypes.c_int64()
    _res_getdjcnumdomain = __library__.MSK_getdjcnumdomain(self.__nativep,djcidx,ctypes.byref(__tmp_992))
    if _res_getdjcnumdomain != 0:
      _,_msg_getdjcnumdomain = self.__getlasterror(_res_getdjcnumdomain)
      raise Error(rescode(_res_getdjcnumdomain),_msg_getdjcnumdomain)
    domidxlist = numpy.zeros(__tmp_992.value,numpy.int64)
    _res_getdjcdomainidxlist = __library__.MSK_getdjcdomainidxlist(self.__nativep,djcidx,ctypes.cast(domidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getdjcdomainidxlist != 0:
      _,_msg_getdjcdomainidxlist = self.__getlasterror(_res_getdjcdomainidxlist)
      raise Error(rescode(_res_getdjcdomainidxlist),_msg_getdjcdomainidxlist)
    return (domidxlist)
  def getdjcdomainidxlist(self,*args,**kwds):
    """
    Obtains the list of domain indexes in a disjunctive constraint.
  
    getdjcdomainidxlist(djcidx,domidxlist)
    getdjcdomainidxlist(djcidx) -> (domidxlist)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [domidxlist : array(int64)]  List of term sizes.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getdjcdomainidxlist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getdjcdomainidxlist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdjcafeidxlist_3(self,djcidx,afeidxlist):
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      __tmp_995 = ctypes.c_int64()
      _res_getdjcnumafe = __library__.MSK_getdjcnumafe(self.__nativep,djcidx,ctypes.byref(__tmp_995))
      if _res_getdjcnumafe != 0:
        _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
        raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
      if len(afeidxlist) < int(__tmp_995.value):
        raise ValueError("argument afeidxlist is too short")
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    _res_getdjcafeidxlist = __library__.MSK_getdjcafeidxlist(self.__nativep,djcidx,_tmparray_afeidxlist_)
    if _res_getdjcafeidxlist != 0:
      _,_msg_getdjcafeidxlist = self.__getlasterror(_res_getdjcafeidxlist)
      raise Error(rescode(_res_getdjcafeidxlist),_msg_getdjcafeidxlist)
    if afeidxlist is not None:
      for __tmp_997,__tmp_998 in enumerate(_tmparray_afeidxlist_):
        afeidxlist[__tmp_997] = __tmp_998
  def __getdjcafeidxlist_2(self,djcidx):
    __tmp_999 = ctypes.c_int64()
    _res_getdjcnumafe = __library__.MSK_getdjcnumafe(self.__nativep,djcidx,ctypes.byref(__tmp_999))
    if _res_getdjcnumafe != 0:
      _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
      raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
    afeidxlist = numpy.zeros(__tmp_999.value,numpy.int64)
    _res_getdjcafeidxlist = __library__.MSK_getdjcafeidxlist(self.__nativep,djcidx,ctypes.cast(afeidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getdjcafeidxlist != 0:
      _,_msg_getdjcafeidxlist = self.__getlasterror(_res_getdjcafeidxlist)
      raise Error(rescode(_res_getdjcafeidxlist),_msg_getdjcafeidxlist)
    return (afeidxlist)
  def getdjcafeidxlist(self,*args,**kwds):
    """
    Obtains the list of affine expression indexes in a disjunctive constraint.
  
    getdjcafeidxlist(djcidx,afeidxlist)
    getdjcafeidxlist(djcidx) -> (afeidxlist)
      [afeidxlist : array(int64)]  List of affine expression indexes.  
      [djcidx : int64]  Index of the disjunctive constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getdjcafeidxlist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getdjcafeidxlist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdjcb_3(self,djcidx,b):
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      __tmp_1002 = ctypes.c_int64()
      _res_getdjcnumafe = __library__.MSK_getdjcnumafe(self.__nativep,djcidx,ctypes.byref(__tmp_1002))
      if _res_getdjcnumafe != 0:
        _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
        raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
      if len(b) < int(__tmp_1002.value):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    _res_getdjcb = __library__.MSK_getdjcb(self.__nativep,djcidx,_tmparray_b_)
    if _res_getdjcb != 0:
      _,_msg_getdjcb = self.__getlasterror(_res_getdjcb)
      raise Error(rescode(_res_getdjcb),_msg_getdjcb)
    if b is not None:
      for __tmp_1004,__tmp_1005 in enumerate(_tmparray_b_):
        b[__tmp_1004] = __tmp_1005
  def __getdjcb_2(self,djcidx):
    __tmp_1006 = ctypes.c_int64()
    _res_getdjcnumafe = __library__.MSK_getdjcnumafe(self.__nativep,djcidx,ctypes.byref(__tmp_1006))
    if _res_getdjcnumafe != 0:
      _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
      raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
    b = numpy.zeros(__tmp_1006.value,numpy.float64)
    _res_getdjcb = __library__.MSK_getdjcb(self.__nativep,djcidx,ctypes.cast(b.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getdjcb != 0:
      _,_msg_getdjcb = self.__getlasterror(_res_getdjcb)
      raise Error(rescode(_res_getdjcb),_msg_getdjcb)
    return (b)
  def getdjcb(self,*args,**kwds):
    """
    Obtains the optional constant term vector of a disjunctive constraint.
  
    getdjcb(djcidx,b)
    getdjcb(djcidx) -> (b)
      [b : array(float64)]  The vector b.  
      [djcidx : int64]  Index of the disjunctive constraint.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getdjcb_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getdjcb_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdjctermsizelist_3(self,djcidx,termsizelist):
    copyback_termsizelist = False
    if termsizelist is None:
      termsizelist_ = None
      _tmparray_termsizelist_ = None
    else:
      __tmp_1009 = ctypes.c_int64()
      _res_getdjcnumterm = __library__.MSK_getdjcnumterm(self.__nativep,djcidx,ctypes.byref(__tmp_1009))
      if _res_getdjcnumterm != 0:
        _,_msg_getdjcnumterm = self.__getlasterror(_res_getdjcnumterm)
        raise Error(rescode(_res_getdjcnumterm),_msg_getdjcnumterm)
      if len(termsizelist) < int(__tmp_1009.value):
        raise ValueError("argument termsizelist is too short")
      _tmparray_termsizelist_ = (ctypes.c_int64*len(termsizelist))(*termsizelist)
    _res_getdjctermsizelist = __library__.MSK_getdjctermsizelist(self.__nativep,djcidx,_tmparray_termsizelist_)
    if _res_getdjctermsizelist != 0:
      _,_msg_getdjctermsizelist = self.__getlasterror(_res_getdjctermsizelist)
      raise Error(rescode(_res_getdjctermsizelist),_msg_getdjctermsizelist)
    if termsizelist is not None:
      for __tmp_1011,__tmp_1012 in enumerate(_tmparray_termsizelist_):
        termsizelist[__tmp_1011] = __tmp_1012
  def __getdjctermsizelist_2(self,djcidx):
    __tmp_1013 = ctypes.c_int64()
    _res_getdjcnumterm = __library__.MSK_getdjcnumterm(self.__nativep,djcidx,ctypes.byref(__tmp_1013))
    if _res_getdjcnumterm != 0:
      _,_msg_getdjcnumterm = self.__getlasterror(_res_getdjcnumterm)
      raise Error(rescode(_res_getdjcnumterm),_msg_getdjcnumterm)
    termsizelist = numpy.zeros(__tmp_1013.value,numpy.int64)
    _res_getdjctermsizelist = __library__.MSK_getdjctermsizelist(self.__nativep,djcidx,ctypes.cast(termsizelist.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getdjctermsizelist != 0:
      _,_msg_getdjctermsizelist = self.__getlasterror(_res_getdjctermsizelist)
      raise Error(rescode(_res_getdjctermsizelist),_msg_getdjctermsizelist)
    return (termsizelist)
  def getdjctermsizelist(self,*args,**kwds):
    """
    Obtains the list of term sizes in a disjunctive constraint.
  
    getdjctermsizelist(djcidx,termsizelist)
    getdjctermsizelist(djcidx) -> (termsizelist)
      [djcidx : int64]  Index of the disjunctive constraint.  
      [termsizelist : array(int64)]  List of term sizes.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getdjctermsizelist_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getdjctermsizelist_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getdjcs_6(self,domidxlist,afeidxlist,b,termsizelist,numterms):
    copyback_domidxlist = False
    if domidxlist is None:
      domidxlist_ = None
      _tmparray_domidxlist_ = None
    else:
      __tmp_1016 = ctypes.c_int64()
      _res_getdjcnumdomaintot = __library__.MSK_getdjcnumdomaintot(self.__nativep,ctypes.byref(__tmp_1016))
      if _res_getdjcnumdomaintot != 0:
        _,_msg_getdjcnumdomaintot = self.__getlasterror(_res_getdjcnumdomaintot)
        raise Error(rescode(_res_getdjcnumdomaintot),_msg_getdjcnumdomaintot)
      if len(domidxlist) < int(__tmp_1016.value):
        raise ValueError("argument domidxlist is too short")
      _tmparray_domidxlist_ = (ctypes.c_int64*len(domidxlist))(*domidxlist)
    copyback_afeidxlist = False
    if afeidxlist is None:
      afeidxlist_ = None
      _tmparray_afeidxlist_ = None
    else:
      __tmp_1020 = ctypes.c_int64()
      _res_getdjcnumafetot = __library__.MSK_getdjcnumafetot(self.__nativep,ctypes.byref(__tmp_1020))
      if _res_getdjcnumafetot != 0:
        _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
        raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
      if len(afeidxlist) < int(__tmp_1020.value):
        raise ValueError("argument afeidxlist is too short")
      _tmparray_afeidxlist_ = (ctypes.c_int64*len(afeidxlist))(*afeidxlist)
    copyback_b = False
    if b is None:
      b_ = None
      _tmparray_b_ = None
    else:
      __tmp_1024 = ctypes.c_int64()
      _res_getdjcnumafetot = __library__.MSK_getdjcnumafetot(self.__nativep,ctypes.byref(__tmp_1024))
      if _res_getdjcnumafetot != 0:
        _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
        raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
      if len(b) < int(__tmp_1024.value):
        raise ValueError("argument b is too short")
      _tmparray_b_ = (ctypes.c_double*len(b))(*b)
    copyback_termsizelist = False
    if termsizelist is None:
      termsizelist_ = None
      _tmparray_termsizelist_ = None
    else:
      __tmp_1028 = ctypes.c_int64()
      _res_getdjcnumtermtot = __library__.MSK_getdjcnumtermtot(self.__nativep,ctypes.byref(__tmp_1028))
      if _res_getdjcnumtermtot != 0:
        _,_msg_getdjcnumtermtot = self.__getlasterror(_res_getdjcnumtermtot)
        raise Error(rescode(_res_getdjcnumtermtot),_msg_getdjcnumtermtot)
      if len(termsizelist) < int(__tmp_1028.value):
        raise ValueError("argument termsizelist is too short")
      _tmparray_termsizelist_ = (ctypes.c_int64*len(termsizelist))(*termsizelist)
    copyback_numterms = False
    if numterms is None:
      numterms_ = None
      _tmparray_numterms_ = None
    else:
      __tmp_1032 = ctypes.c_int64()
      _res_getnumdjc = __library__.MSK_getnumdjc(self.__nativep,ctypes.byref(__tmp_1032))
      if _res_getnumdjc != 0:
        _,_msg_getnumdjc = self.__getlasterror(_res_getnumdjc)
        raise Error(rescode(_res_getnumdjc),_msg_getnumdjc)
      if len(numterms) < int(__tmp_1032.value):
        raise ValueError("argument numterms is too short")
      _tmparray_numterms_ = (ctypes.c_int64*len(numterms))(*numterms)
    _res_getdjcs = __library__.MSK_getdjcs(self.__nativep,_tmparray_domidxlist_,_tmparray_afeidxlist_,_tmparray_b_,_tmparray_termsizelist_,_tmparray_numterms_)
    if _res_getdjcs != 0:
      _,_msg_getdjcs = self.__getlasterror(_res_getdjcs)
      raise Error(rescode(_res_getdjcs),_msg_getdjcs)
    if domidxlist is not None:
      for __tmp_1018,__tmp_1019 in enumerate(_tmparray_domidxlist_):
        domidxlist[__tmp_1018] = __tmp_1019
    if afeidxlist is not None:
      for __tmp_1022,__tmp_1023 in enumerate(_tmparray_afeidxlist_):
        afeidxlist[__tmp_1022] = __tmp_1023
    if b is not None:
      for __tmp_1026,__tmp_1027 in enumerate(_tmparray_b_):
        b[__tmp_1026] = __tmp_1027
    if termsizelist is not None:
      for __tmp_1030,__tmp_1031 in enumerate(_tmparray_termsizelist_):
        termsizelist[__tmp_1030] = __tmp_1031
    if numterms is not None:
      for __tmp_1034,__tmp_1035 in enumerate(_tmparray_numterms_):
        numterms[__tmp_1034] = __tmp_1035
  def __getdjcs_1(self):
    __tmp_1036 = ctypes.c_int64()
    _res_getdjcnumdomaintot = __library__.MSK_getdjcnumdomaintot(self.__nativep,ctypes.byref(__tmp_1036))
    if _res_getdjcnumdomaintot != 0:
      _,_msg_getdjcnumdomaintot = self.__getlasterror(_res_getdjcnumdomaintot)
      raise Error(rescode(_res_getdjcnumdomaintot),_msg_getdjcnumdomaintot)
    domidxlist = numpy.zeros(__tmp_1036.value,numpy.int64)
    __tmp_1039 = ctypes.c_int64()
    _res_getdjcnumafetot = __library__.MSK_getdjcnumafetot(self.__nativep,ctypes.byref(__tmp_1039))
    if _res_getdjcnumafetot != 0:
      _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
      raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
    afeidxlist = numpy.zeros(__tmp_1039.value,numpy.int64)
    __tmp_1042 = ctypes.c_int64()
    _res_getdjcnumafetot = __library__.MSK_getdjcnumafetot(self.__nativep,ctypes.byref(__tmp_1042))
    if _res_getdjcnumafetot != 0:
      _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
      raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
    b = numpy.zeros(__tmp_1042.value,numpy.float64)
    __tmp_1045 = ctypes.c_int64()
    _res_getdjcnumtermtot = __library__.MSK_getdjcnumtermtot(self.__nativep,ctypes.byref(__tmp_1045))
    if _res_getdjcnumtermtot != 0:
      _,_msg_getdjcnumtermtot = self.__getlasterror(_res_getdjcnumtermtot)
      raise Error(rescode(_res_getdjcnumtermtot),_msg_getdjcnumtermtot)
    termsizelist = numpy.zeros(__tmp_1045.value,numpy.int64)
    __tmp_1048 = ctypes.c_int64()
    _res_getnumdjc = __library__.MSK_getnumdjc(self.__nativep,ctypes.byref(__tmp_1048))
    if _res_getnumdjc != 0:
      _,_msg_getnumdjc = self.__getlasterror(_res_getnumdjc)
      raise Error(rescode(_res_getnumdjc),_msg_getnumdjc)
    numterms = numpy.zeros(__tmp_1048.value,numpy.int64)
    _res_getdjcs = __library__.MSK_getdjcs(self.__nativep,ctypes.cast(domidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(afeidxlist.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(b.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(termsizelist.ctypes,ctypes.POINTER(ctypes.c_int64)),ctypes.cast(numterms.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_getdjcs != 0:
      _,_msg_getdjcs = self.__getlasterror(_res_getdjcs)
      raise Error(rescode(_res_getdjcs),_msg_getdjcs)
    return (domidxlist,afeidxlist,b,termsizelist,numterms)
  def getdjcs(self,*args,**kwds):
    """
    Obtains full data of all disjunctive constraints.
  
    getdjcs(domidxlist,
            afeidxlist,
            b,
            termsizelist,
            numterms)
    getdjcs() -> 
           (domidxlist,
            afeidxlist,
            b,
            termsizelist,
            numterms)
      [afeidxlist : array(int64)]  The concatenation of index lists of affine expressions appearing in all disjunctive constraints.  
      [b : array(float64)]  The concatenation of vectors b appearing in all disjunctive constraints.  
      [domidxlist : array(int64)]  The concatenation of index lists of domains appearing in all disjunctive constraints.  
      [numterms : array(int64)]  The number of terms in each of the disjunctive constraints.  
      [termsizelist : array(int64)]  The concatenation of lists of term sizes appearing in all disjunctive constraints.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__getdjcs_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 1: return self.__getdjcs_1(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putconbound_5(self,i,bkc : boundkey,blc,buc):
    _res_putconbound = __library__.MSK_putconbound(self.__nativep,i,bkc,blc,buc)
    if _res_putconbound != 0:
      _,_msg_putconbound = self.__getlasterror(_res_putconbound)
      raise Error(rescode(_res_putconbound),_msg_putconbound)
  def putconbound(self,*args,**kwds):
    """
    Changes the bound for one constraint.
  
    putconbound(i,blc,buc)
      [blc : float64]  New lower bound.  
      [buc : float64]  New upper bound.  
      [i : int32]  Index of the constraint.  
    """
    return self.__putconbound_5(*args,**kwds)
  def __putconboundlist_5(self,sub,bkc,blc,buc):
    num = min(len(sub) if sub is not None else 0,len(bkc) if bkc is not None else 0,len(blc) if blc is not None else 0,len(buc) if buc is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    if bkc is None:
      _tmparray_bkc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_bkc_ = (ctypes.c_int32*len(bkc))(*bkc)
    copyback_blc = False
    if blc is None:
      blc_ = None
      _tmparray_blc_ = None
    else:
      _tmparray_blc_ = (ctypes.c_double*len(blc))(*blc)
    copyback_buc = False
    if buc is None:
      buc_ = None
      _tmparray_buc_ = None
    else:
      _tmparray_buc_ = (ctypes.c_double*len(buc))(*buc)
    _res_putconboundlist = __library__.MSK_putconboundlist(self.__nativep,num,_tmparray_sub_,_tmparray_bkc_,_tmparray_blc_,_tmparray_buc_)
    if _res_putconboundlist != 0:
      _,_msg_putconboundlist = self.__getlasterror(_res_putconboundlist)
      raise Error(rescode(_res_putconboundlist),_msg_putconboundlist)
  def putconboundlist(self,*args,**kwds):
    """
    Changes the bounds of a list of constraints.
  
    putconboundlist(sub,bkc,blc,buc)
      [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
      [blc : array(float64)]  Lower bounds for the constraints.  
      [buc : array(float64)]  Upper bounds for the constraints.  
      [sub : array(int32)]  List of constraint indexes.  
    """
    return self.__putconboundlist_5(*args,**kwds)
  def __putconboundlistconst_5(self,sub,bkc : boundkey,blc,buc):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    _res_putconboundlistconst = __library__.MSK_putconboundlistconst(self.__nativep,num,_tmparray_sub_,bkc,blc,buc)
    if _res_putconboundlistconst != 0:
      _,_msg_putconboundlistconst = self.__getlasterror(_res_putconboundlistconst)
      raise Error(rescode(_res_putconboundlistconst),_msg_putconboundlistconst)
  def putconboundlistconst(self,*args,**kwds):
    """
    Changes the bounds of a list of constraints.
  
    putconboundlistconst(sub,blc,buc)
      [blc : float64]  New lower bound for all constraints in the list.  
      [buc : float64]  New upper bound for all constraints in the list.  
      [sub : array(int32)]  List of constraint indexes.  
    """
    return self.__putconboundlistconst_5(*args,**kwds)
  def __putconboundslice_6(self,first,last,bkc,blc,buc):
    if bkc is None:
      _tmparray_bkc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(bkc) < (last - first):
        raise ValueError("argument bkc is too short")
      _tmparray_bkc_ = (ctypes.c_int32*len(bkc))(*bkc)
    copyback_blc = False
    if blc is None:
      blc_ = None
      _tmparray_blc_ = None
    else:
      if len(blc) < int((last - first)):
        raise ValueError("argument blc is too short")
      _tmparray_blc_ = (ctypes.c_double*len(blc))(*blc)
    copyback_buc = False
    if buc is None:
      buc_ = None
      _tmparray_buc_ = None
    else:
      if len(buc) < int((last - first)):
        raise ValueError("argument buc is too short")
      _tmparray_buc_ = (ctypes.c_double*len(buc))(*buc)
    _res_putconboundslice = __library__.MSK_putconboundslice(self.__nativep,first,last,_tmparray_bkc_,_tmparray_blc_,_tmparray_buc_)
    if _res_putconboundslice != 0:
      _,_msg_putconboundslice = self.__getlasterror(_res_putconboundslice)
      raise Error(rescode(_res_putconboundslice),_msg_putconboundslice)
  def putconboundslice(self,*args,**kwds):
    """
    Changes the bounds for a slice of the constraints.
  
    putconboundslice(first,last,bkc,blc,buc)
      [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
      [blc : array(float64)]  Lower bounds for the constraints.  
      [buc : array(float64)]  Upper bounds for the constraints.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    return self.__putconboundslice_6(*args,**kwds)
  def __putconboundsliceconst_6(self,first,last,bkc : boundkey,blc,buc):
    _res_putconboundsliceconst = __library__.MSK_putconboundsliceconst(self.__nativep,first,last,bkc,blc,buc)
    if _res_putconboundsliceconst != 0:
      _,_msg_putconboundsliceconst = self.__getlasterror(_res_putconboundsliceconst)
      raise Error(rescode(_res_putconboundsliceconst),_msg_putconboundsliceconst)
  def putconboundsliceconst(self,*args,**kwds):
    """
    Changes the bounds for a slice of the constraints.
  
    putconboundsliceconst(first,last,blc,buc)
      [blc : float64]  New lower bound for all constraints in the slice.  
      [buc : float64]  New upper bound for all constraints in the slice.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    return self.__putconboundsliceconst_6(*args,**kwds)
  def __putvarbound_5(self,j,bkx : boundkey,blx,bux):
    _res_putvarbound = __library__.MSK_putvarbound(self.__nativep,j,bkx,blx,bux)
    if _res_putvarbound != 0:
      _,_msg_putvarbound = self.__getlasterror(_res_putvarbound)
      raise Error(rescode(_res_putvarbound),_msg_putvarbound)
  def putvarbound(self,*args,**kwds):
    """
    Changes the bounds for one variable.
  
    putvarbound(j,blx,bux)
      [blx : float64]  New lower bound.  
      [bux : float64]  New upper bound.  
      [j : int32]  Index of the variable.  
    """
    return self.__putvarbound_5(*args,**kwds)
  def __putvarboundlist_5(self,sub,bkx,blx,bux):
    num = min(len(sub) if sub is not None else 0,len(bkx) if bkx is not None else 0,len(blx) if blx is not None else 0,len(bux) if bux is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    if bkx is None:
      _tmparray_bkx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_bkx_ = (ctypes.c_int32*len(bkx))(*bkx)
    copyback_blx = False
    if blx is None:
      blx_ = None
      _tmparray_blx_ = None
    else:
      _tmparray_blx_ = (ctypes.c_double*len(blx))(*blx)
    copyback_bux = False
    if bux is None:
      bux_ = None
      _tmparray_bux_ = None
    else:
      _tmparray_bux_ = (ctypes.c_double*len(bux))(*bux)
    _res_putvarboundlist = __library__.MSK_putvarboundlist(self.__nativep,num,_tmparray_sub_,_tmparray_bkx_,_tmparray_blx_,_tmparray_bux_)
    if _res_putvarboundlist != 0:
      _,_msg_putvarboundlist = self.__getlasterror(_res_putvarboundlist)
      raise Error(rescode(_res_putvarboundlist),_msg_putvarboundlist)
  def putvarboundlist(self,*args,**kwds):
    """
    Changes the bounds of a list of variables.
  
    putvarboundlist(sub,bkx,blx,bux)
      [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
      [blx : array(float64)]  Lower bounds for the variables.  
      [bux : array(float64)]  Upper bounds for the variables.  
      [sub : array(int32)]  List of variable indexes.  
    """
    return self.__putvarboundlist_5(*args,**kwds)
  def __putvarboundlistconst_5(self,sub,bkx : boundkey,blx,bux):
    num = len(sub) if sub is not None else 0
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int32*len(sub))(*sub)
    _res_putvarboundlistconst = __library__.MSK_putvarboundlistconst(self.__nativep,num,_tmparray_sub_,bkx,blx,bux)
    if _res_putvarboundlistconst != 0:
      _,_msg_putvarboundlistconst = self.__getlasterror(_res_putvarboundlistconst)
      raise Error(rescode(_res_putvarboundlistconst),_msg_putvarboundlistconst)
  def putvarboundlistconst(self,*args,**kwds):
    """
    Changes the bounds of a list of variables.
  
    putvarboundlistconst(sub,blx,bux)
      [blx : float64]  New lower bound for all variables in the list.  
      [bux : float64]  New upper bound for all variables in the list.  
      [sub : array(int32)]  List of variable indexes.  
    """
    return self.__putvarboundlistconst_5(*args,**kwds)
  def __putvarboundslice_6(self,first,last,bkx,blx,bux):
    if bkx is None:
      _tmparray_bkx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      if len(bkx) < (last - first):
        raise ValueError("argument bkx is too short")
      _tmparray_bkx_ = (ctypes.c_int32*len(bkx))(*bkx)
    copyback_blx = False
    if blx is None:
      blx_ = None
      _tmparray_blx_ = None
    else:
      if len(blx) < int((last - first)):
        raise ValueError("argument blx is too short")
      _tmparray_blx_ = (ctypes.c_double*len(blx))(*blx)
    copyback_bux = False
    if bux is None:
      bux_ = None
      _tmparray_bux_ = None
    else:
      if len(bux) < int((last - first)):
        raise ValueError("argument bux is too short")
      _tmparray_bux_ = (ctypes.c_double*len(bux))(*bux)
    _res_putvarboundslice = __library__.MSK_putvarboundslice(self.__nativep,first,last,_tmparray_bkx_,_tmparray_blx_,_tmparray_bux_)
    if _res_putvarboundslice != 0:
      _,_msg_putvarboundslice = self.__getlasterror(_res_putvarboundslice)
      raise Error(rescode(_res_putvarboundslice),_msg_putvarboundslice)
  def putvarboundslice(self,*args,**kwds):
    """
    Changes the bounds for a slice of the variables.
  
    putvarboundslice(first,last,bkx,blx,bux)
      [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
      [blx : array(float64)]  Lower bounds for the variables.  
      [bux : array(float64)]  Upper bounds for the variables.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    return self.__putvarboundslice_6(*args,**kwds)
  def __putvarboundsliceconst_6(self,first,last,bkx : boundkey,blx,bux):
    _res_putvarboundsliceconst = __library__.MSK_putvarboundsliceconst(self.__nativep,first,last,bkx,blx,bux)
    if _res_putvarboundsliceconst != 0:
      _,_msg_putvarboundsliceconst = self.__getlasterror(_res_putvarboundsliceconst)
      raise Error(rescode(_res_putvarboundsliceconst),_msg_putvarboundsliceconst)
  def putvarboundsliceconst(self,*args,**kwds):
    """
    Changes the bounds for a slice of the variables.
  
    putvarboundsliceconst(first,last,blx,bux)
      [blx : float64]  New lower bound for all variables in the slice.  
      [bux : float64]  New upper bound for all variables in the slice.  
      [first : int32]  First index in the sequence.  
      [last : int32]  Last index plus 1 in the sequence.  
    """
    return self.__putvarboundsliceconst_6(*args,**kwds)
  def __putcfix_2(self,cfix):
    _res_putcfix = __library__.MSK_putcfix(self.__nativep,cfix)
    if _res_putcfix != 0:
      _,_msg_putcfix = self.__getlasterror(_res_putcfix)
      raise Error(rescode(_res_putcfix),_msg_putcfix)
  def putcfix(self,*args,**kwds):
    """
    Replaces the fixed term in the objective.
  
    putcfix(cfix)
      [cfix : float64]  Fixed term in the objective.  
    """
    return self.__putcfix_2(*args,**kwds)
  def __putcj_3(self,j,cj):
    _res_putcj = __library__.MSK_putcj(self.__nativep,j,cj)
    if _res_putcj != 0:
      _,_msg_putcj = self.__getlasterror(_res_putcj)
      raise Error(rescode(_res_putcj),_msg_putcj)
  def putcj(self,*args,**kwds):
    """
    Modifies one linear coefficient in the objective.
  
    putcj(j,cj)
      [cj : float64]  New coefficient value.  
      [j : int32]  Index of the variable whose objective coefficient should be changed.  
    """
    return self.__putcj_3(*args,**kwds)
  def __putobjsense_2(self,sense : objsense):
    _res_putobjsense = __library__.MSK_putobjsense(self.__nativep,sense)
    if _res_putobjsense != 0:
      _,_msg_putobjsense = self.__getlasterror(_res_putobjsense)
      raise Error(rescode(_res_putobjsense),_msg_putobjsense)
  def putobjsense(self,*args,**kwds):
    """
    Sets the objective sense.
  
    putobjsense()
    """
    return self.__putobjsense_2(*args,**kwds)
  def __getobjsense_1(self):
    sense = ctypes.c_int()
    _res_getobjsense = __library__.MSK_getobjsense(self.__nativep,ctypes.byref(sense))
    if _res_getobjsense != 0:
      _,_msg_getobjsense = self.__getlasterror(_res_getobjsense)
      raise Error(rescode(_res_getobjsense),_msg_getobjsense)
    return (objsense(sense.value))
  def getobjsense(self,*args,**kwds):
    """
    Gets the objective sense.
  
    getobjsense() -> (sense)
      [sense : mosek.objsense]  The returned objective sense.  
    """
    return self.__getobjsense_1(*args,**kwds)
  def __putclist_3(self,subj,val):
    num = min(len(subj) if subj is not None else 0,len(val) if val is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_val = False
    if val is None:
      val_ = None
      _tmparray_val_ = None
    else:
      _tmparray_val_ = (ctypes.c_double*len(val))(*val)
    _res_putclist = __library__.MSK_putclist(self.__nativep,num,_tmparray_subj_,_tmparray_val_)
    if _res_putclist != 0:
      _,_msg_putclist = self.__getlasterror(_res_putclist)
      raise Error(rescode(_res_putclist),_msg_putclist)
  def putclist(self,*args,**kwds):
    """
    Modifies a part of the linear objective coefficients.
  
    putclist(subj,val)
      [subj : array(int32)]  Indices of variables for which objective coefficients should be changed.  
      [val : array(float64)]  New numerical values for the objective coefficients that should be modified.  
    """
    return self.__putclist_3(*args,**kwds)
  def __putcslice_4(self,first,last,slice):
    copyback_slice = False
    if slice is None:
      slice_ = None
      _tmparray_slice_ = None
    else:
      if len(slice) < int((last - first)):
        raise ValueError("argument slice is too short")
      _tmparray_slice_ = (ctypes.c_double*len(slice))(*slice)
    _res_putcslice = __library__.MSK_putcslice(self.__nativep,first,last,_tmparray_slice_)
    if _res_putcslice != 0:
      _,_msg_putcslice = self.__getlasterror(_res_putcslice)
      raise Error(rescode(_res_putcslice),_msg_putcslice)
  def putcslice(self,*args,**kwds):
    """
    Modifies a slice of the linear objective coefficients.
  
    putcslice(first,last,slice)
      [first : int32]  First element in the slice of c.  
      [last : int32]  Last element plus 1 of the slice in c to be changed.  
      [slice : array(float64)]  New numerical values for the objective coefficients that should be modified.  
    """
    return self.__putcslice_4(*args,**kwds)
  def __putbarcj_4(self,j,sub,weights):
    num = min(len(sub) if sub is not None else 0,len(weights) if weights is not None else 0)
    copyback_sub = False
    if sub is None:
      sub_ = None
      _tmparray_sub_ = None
    else:
      _tmparray_sub_ = (ctypes.c_int64*len(sub))(*sub)
    copyback_weights = False
    if weights is None:
      weights_ = None
      _tmparray_weights_ = None
    else:
      _tmparray_weights_ = (ctypes.c_double*len(weights))(*weights)
    _res_putbarcj = __library__.MSK_putbarcj(self.__nativep,j,num,_tmparray_sub_,_tmparray_weights_)
    if _res_putbarcj != 0:
      _,_msg_putbarcj = self.__getlasterror(_res_putbarcj)
      raise Error(rescode(_res_putbarcj),_msg_putbarcj)
  def putbarcj(self,*args,**kwds):
    """
    Changes one element in barc.
  
    putbarcj(j,sub,weights)
      [j : int32]  Index of the element in barc` that should be changed.  
      [sub : array(int64)]  sub is list of indexes of those symmetric matrices appearing in sum.  
      [weights : array(float64)]  The weights of the terms in the weighted sum.  
    """
    return self.__putbarcj_4(*args,**kwds)
  def __putcone_5(self,k,ct : conetype,conepar,submem):
    nummem = len(submem) if submem is not None else 0
    copyback_submem = False
    if submem is None:
      submem_ = None
      _tmparray_submem_ = None
    else:
      _tmparray_submem_ = (ctypes.c_int32*len(submem))(*submem)
    _res_putcone = __library__.MSK_putcone(self.__nativep,k,ct,conepar,nummem,_tmparray_submem_)
    if _res_putcone != 0:
      _,_msg_putcone = self.__getlasterror(_res_putcone)
      raise Error(rescode(_res_putcone),_msg_putcone)
  def putcone(self,*args,**kwds):
    """
    Replaces a conic constraint.
  
    putcone(k,conepar,submem)
      [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
      [k : int32]  Index of the cone.  
      [submem : array(int32)]  Variable subscripts of the members in the cone.  
    """
    return self.__putcone_5(*args,**kwds)
  def __putmaxnumdomain_2(self,maxnumdomain):
    _res_putmaxnumdomain = __library__.MSK_putmaxnumdomain(self.__nativep,maxnumdomain)
    if _res_putmaxnumdomain != 0:
      _,_msg_putmaxnumdomain = self.__getlasterror(_res_putmaxnumdomain)
      raise Error(rescode(_res_putmaxnumdomain),_msg_putmaxnumdomain)
  def putmaxnumdomain(self,*args,**kwds):
    """
    Sets the number of preallocated domains in the optimization task.
  
    putmaxnumdomain(maxnumdomain)
      [maxnumdomain : int64]  Number of preallocated domains.  
    """
    return self.__putmaxnumdomain_2(*args,**kwds)
  def __getnumdomain_1(self):
    numdomain_ = ctypes.c_int64()
    _res_getnumdomain = __library__.MSK_getnumdomain(self.__nativep,ctypes.byref(numdomain_))
    if _res_getnumdomain != 0:
      _,_msg_getnumdomain = self.__getlasterror(_res_getnumdomain)
      raise Error(rescode(_res_getnumdomain),_msg_getnumdomain)
    numdomain = numdomain_.value
    return (numdomain_.value)
  def getnumdomain(self,*args,**kwds):
    """
    Obtain the number of domains defined.
  
    getnumdomain() -> (numdomain)
      [numdomain : int64]  Number of domains in the task.  
    """
    return self.__getnumdomain_1(*args,**kwds)
  def __appendrplusdomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendrplusdomain = __library__.MSK_appendrplusdomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendrplusdomain != 0:
      _,_msg_appendrplusdomain = self.__getlasterror(_res_appendrplusdomain)
      raise Error(rescode(_res_appendrplusdomain),_msg_appendrplusdomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendrplusdomain(self,*args,**kwds):
    """
    Appends the n dimensional positive orthant to the list of domains.
  
    appendrplusdomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendrplusdomain_2(*args,**kwds)
  def __appendrminusdomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendrminusdomain = __library__.MSK_appendrminusdomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendrminusdomain != 0:
      _,_msg_appendrminusdomain = self.__getlasterror(_res_appendrminusdomain)
      raise Error(rescode(_res_appendrminusdomain),_msg_appendrminusdomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendrminusdomain(self,*args,**kwds):
    """
    Appends the n dimensional negative orthant to the list of domains.
  
    appendrminusdomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendrminusdomain_2(*args,**kwds)
  def __appendrdomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendrdomain = __library__.MSK_appendrdomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendrdomain != 0:
      _,_msg_appendrdomain = self.__getlasterror(_res_appendrdomain)
      raise Error(rescode(_res_appendrdomain),_msg_appendrdomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendrdomain(self,*args,**kwds):
    """
    Appends the n dimensional real number domain.
  
    appendrdomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendrdomain_2(*args,**kwds)
  def __appendrzerodomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendrzerodomain = __library__.MSK_appendrzerodomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendrzerodomain != 0:
      _,_msg_appendrzerodomain = self.__getlasterror(_res_appendrzerodomain)
      raise Error(rescode(_res_appendrzerodomain),_msg_appendrzerodomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendrzerodomain(self,*args,**kwds):
    """
    Appends the n dimensional 0 domain.
  
    appendrzerodomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendrzerodomain_2(*args,**kwds)
  def __appendquadraticconedomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendquadraticconedomain = __library__.MSK_appendquadraticconedomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendquadraticconedomain != 0:
      _,_msg_appendquadraticconedomain = self.__getlasterror(_res_appendquadraticconedomain)
      raise Error(rescode(_res_appendquadraticconedomain),_msg_appendquadraticconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendquadraticconedomain(self,*args,**kwds):
    """
    Appends the n dimensional quadratic cone domain.
  
    appendquadraticconedomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendquadraticconedomain_2(*args,**kwds)
  def __appendrquadraticconedomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendrquadraticconedomain = __library__.MSK_appendrquadraticconedomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendrquadraticconedomain != 0:
      _,_msg_appendrquadraticconedomain = self.__getlasterror(_res_appendrquadraticconedomain)
      raise Error(rescode(_res_appendrquadraticconedomain),_msg_appendrquadraticconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendrquadraticconedomain(self,*args,**kwds):
    """
    Appends the n dimensional rotated quadratic cone domain.
  
    appendrquadraticconedomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendrquadraticconedomain_2(*args,**kwds)
  def __appendprimalexpconedomain_1(self):
    domidx_ = ctypes.c_int64()
    _res_appendprimalexpconedomain = __library__.MSK_appendprimalexpconedomain(self.__nativep,ctypes.byref(domidx_))
    if _res_appendprimalexpconedomain != 0:
      _,_msg_appendprimalexpconedomain = self.__getlasterror(_res_appendprimalexpconedomain)
      raise Error(rescode(_res_appendprimalexpconedomain),_msg_appendprimalexpconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendprimalexpconedomain(self,*args,**kwds):
    """
    Appends the primal exponential cone domain.
  
    appendprimalexpconedomain() -> (domidx)
      [domidx : int64]  Index of the domain.  
    """
    return self.__appendprimalexpconedomain_1(*args,**kwds)
  def __appenddualexpconedomain_1(self):
    domidx_ = ctypes.c_int64()
    _res_appenddualexpconedomain = __library__.MSK_appenddualexpconedomain(self.__nativep,ctypes.byref(domidx_))
    if _res_appenddualexpconedomain != 0:
      _,_msg_appenddualexpconedomain = self.__getlasterror(_res_appenddualexpconedomain)
      raise Error(rescode(_res_appenddualexpconedomain),_msg_appenddualexpconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appenddualexpconedomain(self,*args,**kwds):
    """
    Appends the dual exponential cone domain.
  
    appenddualexpconedomain() -> (domidx)
      [domidx : int64]  Index of the domain.  
    """
    return self.__appenddualexpconedomain_1(*args,**kwds)
  def __appendprimalgeomeanconedomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendprimalgeomeanconedomain = __library__.MSK_appendprimalgeomeanconedomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendprimalgeomeanconedomain != 0:
      _,_msg_appendprimalgeomeanconedomain = self.__getlasterror(_res_appendprimalgeomeanconedomain)
      raise Error(rescode(_res_appendprimalgeomeanconedomain),_msg_appendprimalgeomeanconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendprimalgeomeanconedomain(self,*args,**kwds):
    """
    Appends the primal geometric mean cone domain.
  
    appendprimalgeomeanconedomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appendprimalgeomeanconedomain_2(*args,**kwds)
  def __appenddualgeomeanconedomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appenddualgeomeanconedomain = __library__.MSK_appenddualgeomeanconedomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appenddualgeomeanconedomain != 0:
      _,_msg_appenddualgeomeanconedomain = self.__getlasterror(_res_appenddualgeomeanconedomain)
      raise Error(rescode(_res_appenddualgeomeanconedomain),_msg_appenddualgeomeanconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appenddualgeomeanconedomain(self,*args,**kwds):
    """
    Appends the dual geometric mean cone domain.
  
    appenddualgeomeanconedomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimmension of the domain.  
    """
    return self.__appenddualgeomeanconedomain_2(*args,**kwds)
  def __appendprimalpowerconedomain_3(self,n,alpha):
    nleft = len(alpha) if alpha is not None else 0
    copyback_alpha = False
    if alpha is None:
      alpha_ = None
      _tmparray_alpha_ = None
    else:
      _tmparray_alpha_ = (ctypes.c_double*len(alpha))(*alpha)
    domidx_ = ctypes.c_int64()
    _res_appendprimalpowerconedomain = __library__.MSK_appendprimalpowerconedomain(self.__nativep,n,nleft,_tmparray_alpha_,ctypes.byref(domidx_))
    if _res_appendprimalpowerconedomain != 0:
      _,_msg_appendprimalpowerconedomain = self.__getlasterror(_res_appendprimalpowerconedomain)
      raise Error(rescode(_res_appendprimalpowerconedomain),_msg_appendprimalpowerconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendprimalpowerconedomain(self,*args,**kwds):
    """
    Appends the primal power cone domain.
  
    appendprimalpowerconedomain(n,alpha) -> (domidx)
      [alpha : array(float64)]  The sequence proportional to exponents. Must be positive.  
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimension of the domain.  
    """
    return self.__appendprimalpowerconedomain_3(*args,**kwds)
  def __appenddualpowerconedomain_3(self,n,alpha):
    nleft = len(alpha) if alpha is not None else 0
    copyback_alpha = False
    if alpha is None:
      alpha_ = None
      _tmparray_alpha_ = None
    else:
      _tmparray_alpha_ = (ctypes.c_double*len(alpha))(*alpha)
    domidx_ = ctypes.c_int64()
    _res_appenddualpowerconedomain = __library__.MSK_appenddualpowerconedomain(self.__nativep,n,nleft,_tmparray_alpha_,ctypes.byref(domidx_))
    if _res_appenddualpowerconedomain != 0:
      _,_msg_appenddualpowerconedomain = self.__getlasterror(_res_appenddualpowerconedomain)
      raise Error(rescode(_res_appenddualpowerconedomain),_msg_appenddualpowerconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appenddualpowerconedomain(self,*args,**kwds):
    """
    Appends the dual power cone domain.
  
    appenddualpowerconedomain(n,alpha) -> (domidx)
      [alpha : array(float64)]  The sequence proportional to exponents. Must be positive.  
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimension of the domain.  
    """
    return self.__appenddualpowerconedomain_3(*args,**kwds)
  def __appendsvecpsdconedomain_2(self,n):
    domidx_ = ctypes.c_int64()
    _res_appendsvecpsdconedomain = __library__.MSK_appendsvecpsdconedomain(self.__nativep,n,ctypes.byref(domidx_))
    if _res_appendsvecpsdconedomain != 0:
      _,_msg_appendsvecpsdconedomain = self.__getlasterror(_res_appendsvecpsdconedomain)
      raise Error(rescode(_res_appendsvecpsdconedomain),_msg_appendsvecpsdconedomain)
    domidx = domidx_.value
    return (domidx_.value)
  def appendsvecpsdconedomain(self,*args,**kwds):
    """
    Appends the vectorized SVEC PSD cone domain.
  
    appendsvecpsdconedomain(n) -> (domidx)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimension of the domain.  
    """
    return self.__appendsvecpsdconedomain_2(*args,**kwds)
  def __getdomaintype_2(self,domidx):
    domtype = ctypes.c_int()
    _res_getdomaintype = __library__.MSK_getdomaintype(self.__nativep,domidx,ctypes.byref(domtype))
    if _res_getdomaintype != 0:
      _,_msg_getdomaintype = self.__getlasterror(_res_getdomaintype)
      raise Error(rescode(_res_getdomaintype),_msg_getdomaintype)
    return (domaintype(domtype.value))
  def getdomaintype(self,*args,**kwds):
    """
    Returns the type of the domain.
  
    getdomaintype(domidx) -> (domtype)
      [domidx : int64]  Index of the domain.  
      [domtype : mosek.domaintype]  The type of the domain.  
    """
    return self.__getdomaintype_2(*args,**kwds)
  def __getdomainn_2(self,domidx):
    n_ = ctypes.c_int64()
    _res_getdomainn = __library__.MSK_getdomainn(self.__nativep,domidx,ctypes.byref(n_))
    if _res_getdomainn != 0:
      _,_msg_getdomainn = self.__getlasterror(_res_getdomainn)
      raise Error(rescode(_res_getdomainn),_msg_getdomainn)
    n = n_.value
    return (n_.value)
  def getdomainn(self,*args,**kwds):
    """
    Obtains the dimension of the domain.
  
    getdomainn(domidx) -> (n)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimension of the domain.  
    """
    return self.__getdomainn_2(*args,**kwds)
  def __getpowerdomaininfo_2(self,domidx):
    n_ = ctypes.c_int64()
    nleft_ = ctypes.c_int64()
    _res_getpowerdomaininfo = __library__.MSK_getpowerdomaininfo(self.__nativep,domidx,ctypes.byref(n_),ctypes.byref(nleft_))
    if _res_getpowerdomaininfo != 0:
      _,_msg_getpowerdomaininfo = self.__getlasterror(_res_getpowerdomaininfo)
      raise Error(rescode(_res_getpowerdomaininfo),_msg_getpowerdomaininfo)
    n = n_.value
    nleft = nleft_.value
    return (n_.value,nleft_.value)
  def getpowerdomaininfo(self,*args,**kwds):
    """
    Obtains structural information about a power domain.
  
    getpowerdomaininfo(domidx) -> (n,nleft)
      [domidx : int64]  Index of the domain.  
      [n : int64]  Dimension of the domain.  
      [nleft : int64]  Number of variables on the left hand side.  
    """
    return self.__getpowerdomaininfo_2(*args,**kwds)
  def __getpowerdomainalpha_3(self,domidx,alpha):
    copyback_alpha = False
    if alpha is None:
      alpha_ = None
      _tmparray_alpha_ = None
    else:
      __tmp_1067 = ctypes.c_int64()
      __tmp_1068 = ctypes.c_int64()
      _res_getpowerdomaininfo = __library__.MSK_getpowerdomaininfo(self.__nativep,domidx,ctypes.byref(__tmp_1067),ctypes.byref(__tmp_1068))
      if _res_getpowerdomaininfo != 0:
        _,_msg_getpowerdomaininfo = self.__getlasterror(_res_getpowerdomaininfo)
        raise Error(rescode(_res_getpowerdomaininfo),_msg_getpowerdomaininfo)
      if len(alpha) < int(__tmp_1068.value):
        raise ValueError("argument alpha is too short")
      _tmparray_alpha_ = (ctypes.c_double*len(alpha))(*alpha)
    _res_getpowerdomainalpha = __library__.MSK_getpowerdomainalpha(self.__nativep,domidx,_tmparray_alpha_)
    if _res_getpowerdomainalpha != 0:
      _,_msg_getpowerdomainalpha = self.__getlasterror(_res_getpowerdomainalpha)
      raise Error(rescode(_res_getpowerdomainalpha),_msg_getpowerdomainalpha)
    if alpha is not None:
      for __tmp_1070,__tmp_1071 in enumerate(_tmparray_alpha_):
        alpha[__tmp_1070] = __tmp_1071
  def __getpowerdomainalpha_2(self,domidx):
    __tmp_1072 = ctypes.c_int64()
    __tmp_1073 = ctypes.c_int64()
    _res_getpowerdomaininfo = __library__.MSK_getpowerdomaininfo(self.__nativep,domidx,ctypes.byref(__tmp_1072),ctypes.byref(__tmp_1073))
    if _res_getpowerdomaininfo != 0:
      _,_msg_getpowerdomaininfo = self.__getlasterror(_res_getpowerdomaininfo)
      raise Error(rescode(_res_getpowerdomaininfo),_msg_getpowerdomaininfo)
    alpha = numpy.zeros(__tmp_1073.value,numpy.float64)
    _res_getpowerdomainalpha = __library__.MSK_getpowerdomainalpha(self.__nativep,domidx,ctypes.cast(alpha.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getpowerdomainalpha != 0:
      _,_msg_getpowerdomainalpha = self.__getlasterror(_res_getpowerdomainalpha)
      raise Error(rescode(_res_getpowerdomainalpha),_msg_getpowerdomainalpha)
    return (alpha)
  def getpowerdomainalpha(self,*args,**kwds):
    """
    Obtains the exponent vector of a power domain.
  
    getpowerdomainalpha(domidx,alpha)
    getpowerdomainalpha(domidx) -> (alpha)
      [alpha : array(float64)]  The exponent vector of the domain.  
      [domidx : int64]  Index of the domain.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 3: return self.__getpowerdomainalpha_3(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getpowerdomainalpha_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __appendsparsesymmat_5(self,dim,subi,subj,valij):
    nz = min(len(subi) if subi is not None else 0,len(subj) if subj is not None else 0,len(valij) if valij is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valij = False
    if valij is None:
      valij_ = None
      _tmparray_valij_ = None
    else:
      _tmparray_valij_ = (ctypes.c_double*len(valij))(*valij)
    idx_ = ctypes.c_int64()
    _res_appendsparsesymmat = __library__.MSK_appendsparsesymmat(self.__nativep,dim,nz,_tmparray_subi_,_tmparray_subj_,_tmparray_valij_,ctypes.byref(idx_))
    if _res_appendsparsesymmat != 0:
      _,_msg_appendsparsesymmat = self.__getlasterror(_res_appendsparsesymmat)
      raise Error(rescode(_res_appendsparsesymmat),_msg_appendsparsesymmat)
    idx = idx_.value
    return (idx_.value)
  def appendsparsesymmat(self,*args,**kwds):
    """
    Appends a general sparse symmetric matrix to the storage of symmetric matrices.
  
    appendsparsesymmat(dim,subi,subj,valij) -> (idx)
      [dim : int32]  Dimension of the symmetric matrix that is appended.  
      [idx : int64]  Unique index assigned to the inputted matrix.  
      [subi : array(int32)]  Row subscript in the triplets.  
      [subj : array(int32)]  Column subscripts in the triplets.  
      [valij : array(float64)]  Values of each triplet.  
    """
    return self.__appendsparsesymmat_5(*args,**kwds)
  def __appendsparsesymmatlist_7(self,dims,nz,subi,subj,valij,idx):
    num = min(len(dims) if dims is not None else 0,len(nz) if nz is not None else 0)
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_nz = False
    if nz is None:
      nz_ = None
      _tmparray_nz_ = None
    else:
      _tmparray_nz_ = (ctypes.c_int64*len(nz))(*nz)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      __tmp_1076 = sum(nz)
      if len(subi) < int(__tmp_1076):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      __tmp_1077 = sum(nz)
      if len(subj) < int(__tmp_1077):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valij = False
    if valij is None:
      valij_ = None
      _tmparray_valij_ = None
    else:
      __tmp_1078 = sum(nz)
      if len(valij) < int(__tmp_1078):
        raise ValueError("argument valij is too short")
      _tmparray_valij_ = (ctypes.c_double*len(valij))(*valij)
    copyback_idx = False
    if idx is None:
      idx_ = None
      _tmparray_idx_ = None
    else:
      if len(idx) < int(num):
        raise ValueError("argument idx is too short")
      _tmparray_idx_ = (ctypes.c_int64*len(idx))(*idx)
    _res_appendsparsesymmatlist = __library__.MSK_appendsparsesymmatlist(self.__nativep,num,_tmparray_dims_,_tmparray_nz_,_tmparray_subi_,_tmparray_subj_,_tmparray_valij_,_tmparray_idx_)
    if _res_appendsparsesymmatlist != 0:
      _,_msg_appendsparsesymmatlist = self.__getlasterror(_res_appendsparsesymmatlist)
      raise Error(rescode(_res_appendsparsesymmatlist),_msg_appendsparsesymmatlist)
    if idx is not None:
      for __tmp_1079,__tmp_1080 in enumerate(_tmparray_idx_):
        idx[__tmp_1079] = __tmp_1080
  def __appendsparsesymmatlist_6(self,dims,nz,subi,subj,valij):
    num = min(len(dims) if dims is not None else 0,len(nz) if nz is not None else 0)
    copyback_dims = False
    if dims is None:
      dims_ = None
      _tmparray_dims_ = None
    else:
      _tmparray_dims_ = (ctypes.c_int32*len(dims))(*dims)
    copyback_nz = False
    if nz is None:
      nz_ = None
      _tmparray_nz_ = None
    else:
      _tmparray_nz_ = (ctypes.c_int64*len(nz))(*nz)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      __tmp_1081 = sum(nz)
      if len(subi) < int(__tmp_1081):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      __tmp_1082 = sum(nz)
      if len(subj) < int(__tmp_1082):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valij = False
    if valij is None:
      valij_ = None
      _tmparray_valij_ = None
    else:
      __tmp_1083 = sum(nz)
      if len(valij) < int(__tmp_1083):
        raise ValueError("argument valij is too short")
      _tmparray_valij_ = (ctypes.c_double*len(valij))(*valij)
    idx = numpy.zeros(num,numpy.int64)
    _res_appendsparsesymmatlist = __library__.MSK_appendsparsesymmatlist(self.__nativep,num,_tmparray_dims_,_tmparray_nz_,_tmparray_subi_,_tmparray_subj_,_tmparray_valij_,ctypes.cast(idx.ctypes,ctypes.POINTER(ctypes.c_int64)))
    if _res_appendsparsesymmatlist != 0:
      _,_msg_appendsparsesymmatlist = self.__getlasterror(_res_appendsparsesymmatlist)
      raise Error(rescode(_res_appendsparsesymmatlist),_msg_appendsparsesymmatlist)
    return (idx)
  def appendsparsesymmatlist(self,*args,**kwds):
    """
    Appends a general sparse symmetric matrix to the storage of symmetric matrices.
  
    appendsparsesymmatlist(dims,nz,subi,subj,valij,idx)
    appendsparsesymmatlist(dims,nz,subi,subj,valij) -> (idx)
      [dims : array(int32)]  Dimensions of the symmetric matrixes.  
      [idx : array(int64)]  Unique index assigned to the inputted matrix.  
      [nz : array(int64)]  Number of nonzeros for each matrix.  
      [subi : array(int32)]  Row subscript in the triplets.  
      [subj : array(int32)]  Column subscripts in the triplets.  
      [valij : array(float64)]  Values of each triplet.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 7: return self.__appendsparsesymmatlist_7(*args,**kwds)
    elif len(args)+len(kwds)+1 == 6: return self.__appendsparsesymmatlist_6(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __getsymmatinfo_2(self,idx):
    dim_ = ctypes.c_int32()
    nz_ = ctypes.c_int64()
    mattype = ctypes.c_int()
    _res_getsymmatinfo = __library__.MSK_getsymmatinfo(self.__nativep,idx,ctypes.byref(dim_),ctypes.byref(nz_),ctypes.byref(mattype))
    if _res_getsymmatinfo != 0:
      _,_msg_getsymmatinfo = self.__getlasterror(_res_getsymmatinfo)
      raise Error(rescode(_res_getsymmatinfo),_msg_getsymmatinfo)
    dim = dim_.value
    nz = nz_.value
    return (dim_.value,nz_.value,symmattype(mattype.value))
  def getsymmatinfo(self,*args,**kwds):
    """
    Obtains information about a matrix from the symmetric matrix storage.
  
    getsymmatinfo(idx) -> (dim,nz,mattype)
      [dim : int32]  Returns the dimension of the requested matrix.  
      [idx : int64]  Index of the matrix for which information is requested.  
      [mattype : mosek.symmattype]  Returns the type of the requested matrix.  
      [nz : int64]  Returns the number of non-zeros in the requested matrix.  
    """
    return self.__getsymmatinfo_2(*args,**kwds)
  def __getnumsymmat_1(self):
    num_ = ctypes.c_int64()
    _res_getnumsymmat = __library__.MSK_getnumsymmat(self.__nativep,ctypes.byref(num_))
    if _res_getnumsymmat != 0:
      _,_msg_getnumsymmat = self.__getlasterror(_res_getnumsymmat)
      raise Error(rescode(_res_getnumsymmat),_msg_getnumsymmat)
    num = num_.value
    return (num_.value)
  def getnumsymmat(self,*args,**kwds):
    """
    Obtains the number of symmetric matrices stored.
  
    getnumsymmat() -> (num)
      [num : int64]  The number of symmetric sparse matrices.  
    """
    return self.__getnumsymmat_1(*args,**kwds)
  def __getsparsesymmat_5(self,idx,subi,subj,valij):
    __tmp_1085 = ctypes.c_int32()
    __tmp_1086 = ctypes.c_int64()
    __tmp_1087 = ctypes.c_int32()
    _res_getsymmatinfo = __library__.MSK_getsymmatinfo(self.__nativep,idx,ctypes.byref(__tmp_1085),ctypes.byref(__tmp_1086),ctypes.byref(__tmp_1087))
    if _res_getsymmatinfo != 0:
      _,_msg_getsymmatinfo = self.__getlasterror(_res_getsymmatinfo)
      raise Error(rescode(_res_getsymmatinfo),_msg_getsymmatinfo)
    maxlen = __tmp_1086.value;
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      if len(subi) < int(maxlen):
        raise ValueError("argument subi is too short")
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      if len(subj) < int(maxlen):
        raise ValueError("argument subj is too short")
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_valij = False
    if valij is None:
      valij_ = None
      _tmparray_valij_ = None
    else:
      if len(valij) < int(maxlen):
        raise ValueError("argument valij is too short")
      _tmparray_valij_ = (ctypes.c_double*len(valij))(*valij)
    _res_getsparsesymmat = __library__.MSK_getsparsesymmat(self.__nativep,idx,maxlen,_tmparray_subi_,_tmparray_subj_,_tmparray_valij_)
    if _res_getsparsesymmat != 0:
      _,_msg_getsparsesymmat = self.__getlasterror(_res_getsparsesymmat)
      raise Error(rescode(_res_getsparsesymmat),_msg_getsparsesymmat)
    if subi is not None:
      for __tmp_1089,__tmp_1090 in enumerate(_tmparray_subi_):
        subi[__tmp_1089] = __tmp_1090
    if subj is not None:
      for __tmp_1091,__tmp_1092 in enumerate(_tmparray_subj_):
        subj[__tmp_1091] = __tmp_1092
    if valij is not None:
      for __tmp_1093,__tmp_1094 in enumerate(_tmparray_valij_):
        valij[__tmp_1093] = __tmp_1094
  def __getsparsesymmat_2(self,idx):
    __tmp_1095 = ctypes.c_int32()
    __tmp_1096 = ctypes.c_int64()
    __tmp_1097 = ctypes.c_int32()
    _res_getsymmatinfo = __library__.MSK_getsymmatinfo(self.__nativep,idx,ctypes.byref(__tmp_1095),ctypes.byref(__tmp_1096),ctypes.byref(__tmp_1097))
    if _res_getsymmatinfo != 0:
      _,_msg_getsymmatinfo = self.__getlasterror(_res_getsymmatinfo)
      raise Error(rescode(_res_getsymmatinfo),_msg_getsymmatinfo)
    maxlen = __tmp_1096.value;
    subi = numpy.zeros(maxlen,numpy.int32)
    subj = numpy.zeros(maxlen,numpy.int32)
    valij = numpy.zeros(maxlen,numpy.float64)
    _res_getsparsesymmat = __library__.MSK_getsparsesymmat(self.__nativep,idx,maxlen,ctypes.cast(subi.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(subj.ctypes,ctypes.POINTER(ctypes.c_int32)),ctypes.cast(valij.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_getsparsesymmat != 0:
      _,_msg_getsparsesymmat = self.__getlasterror(_res_getsparsesymmat)
      raise Error(rescode(_res_getsparsesymmat),_msg_getsparsesymmat)
    return (subi,subj,valij)
  def getsparsesymmat(self,*args,**kwds):
    """
    Gets a single symmetric matrix from the matrix store.
  
    getsparsesymmat(idx,subi,subj,valij)
    getsparsesymmat(idx) -> (subi,subj,valij)
      [idx : int64]  Index of the matrix to retrieve.  
      [subi : array(int32)]  Row subscripts of the matrix non-zero elements.  
      [subj : array(int32)]  Column subscripts of the matrix non-zero elements.  
      [valij : array(float64)]  Coefficients of the matrix non-zero elements.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 5: return self.__getsparsesymmat_5(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__getsparsesymmat_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __putdouparam_3(self,param : dparam,parvalue):
    _res_putdouparam = __library__.MSK_putdouparam(self.__nativep,param,parvalue)
    if _res_putdouparam != 0:
      _,_msg_putdouparam = self.__getlasterror(_res_putdouparam)
      raise Error(rescode(_res_putdouparam),_msg_putdouparam)
  def putdouparam(self,*args,**kwds):
    """
    Sets a double parameter.
  
    putdouparam(parvalue)
      [parvalue : float64]  Parameter value.  
    """
    return self.__putdouparam_3(*args,**kwds)
  def __putintparam_3(self,param : iparam,parvalue):
    _res_putintparam = __library__.MSK_putintparam(self.__nativep,param,parvalue)
    if _res_putintparam != 0:
      _,_msg_putintparam = self.__getlasterror(_res_putintparam)
      raise Error(rescode(_res_putintparam),_msg_putintparam)
  def putintparam(self,*args,**kwds):
    """
    Sets an integer parameter.
  
    putintparam(parvalue)
      [parvalue : int32]  Parameter value.  
    """
    return self.__putintparam_3(*args,**kwds)
  def __putmaxnumcon_2(self,maxnumcon):
    _res_putmaxnumcon = __library__.MSK_putmaxnumcon(self.__nativep,maxnumcon)
    if _res_putmaxnumcon != 0:
      _,_msg_putmaxnumcon = self.__getlasterror(_res_putmaxnumcon)
      raise Error(rescode(_res_putmaxnumcon),_msg_putmaxnumcon)
  def putmaxnumcon(self,*args,**kwds):
    """
    Sets the number of preallocated constraints in the optimization task.
  
    putmaxnumcon(maxnumcon)
      [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
    """
    return self.__putmaxnumcon_2(*args,**kwds)
  def __putmaxnumcone_2(self,maxnumcone):
    _res_putmaxnumcone = __library__.MSK_putmaxnumcone(self.__nativep,maxnumcone)
    if _res_putmaxnumcone != 0:
      _,_msg_putmaxnumcone = self.__getlasterror(_res_putmaxnumcone)
      raise Error(rescode(_res_putmaxnumcone),_msg_putmaxnumcone)
  def putmaxnumcone(self,*args,**kwds):
    """
    Sets the number of preallocated conic constraints in the optimization task.
  
    putmaxnumcone(maxnumcone)
      [maxnumcone : int32]  Number of preallocated conic constraints in the optimization task.  
    """
    return self.__putmaxnumcone_2(*args,**kwds)
  def __getmaxnumcone_1(self):
    maxnumcone_ = ctypes.c_int32()
    _res_getmaxnumcone = __library__.MSK_getmaxnumcone(self.__nativep,ctypes.byref(maxnumcone_))
    if _res_getmaxnumcone != 0:
      _,_msg_getmaxnumcone = self.__getlasterror(_res_getmaxnumcone)
      raise Error(rescode(_res_getmaxnumcone),_msg_getmaxnumcone)
    maxnumcone = maxnumcone_.value
    return (maxnumcone_.value)
  def getmaxnumcone(self,*args,**kwds):
    """
    Obtains the number of preallocated cones in the optimization task.
  
    getmaxnumcone() -> (maxnumcone)
      [maxnumcone : int32]  Number of preallocated conic constraints in the optimization task.  
    """
    return self.__getmaxnumcone_1(*args,**kwds)
  def __putmaxnumvar_2(self,maxnumvar):
    _res_putmaxnumvar = __library__.MSK_putmaxnumvar(self.__nativep,maxnumvar)
    if _res_putmaxnumvar != 0:
      _,_msg_putmaxnumvar = self.__getlasterror(_res_putmaxnumvar)
      raise Error(rescode(_res_putmaxnumvar),_msg_putmaxnumvar)
  def putmaxnumvar(self,*args,**kwds):
    """
    Sets the number of preallocated variables in the optimization task.
  
    putmaxnumvar(maxnumvar)
      [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
    """
    return self.__putmaxnumvar_2(*args,**kwds)
  def __putmaxnumbarvar_2(self,maxnumbarvar):
    _res_putmaxnumbarvar = __library__.MSK_putmaxnumbarvar(self.__nativep,maxnumbarvar)
    if _res_putmaxnumbarvar != 0:
      _,_msg_putmaxnumbarvar = self.__getlasterror(_res_putmaxnumbarvar)
      raise Error(rescode(_res_putmaxnumbarvar),_msg_putmaxnumbarvar)
  def putmaxnumbarvar(self,*args,**kwds):
    """
    Sets the number of preallocated symmetric matrix variables.
  
    putmaxnumbarvar(maxnumbarvar)
      [maxnumbarvar : int32]  Number of preallocated symmetric matrix variables.  
    """
    return self.__putmaxnumbarvar_2(*args,**kwds)
  def __putmaxnumanz_2(self,maxnumanz):
    _res_putmaxnumanz = __library__.MSK_putmaxnumanz(self.__nativep,maxnumanz)
    if _res_putmaxnumanz != 0:
      _,_msg_putmaxnumanz = self.__getlasterror(_res_putmaxnumanz)
      raise Error(rescode(_res_putmaxnumanz),_msg_putmaxnumanz)
  def putmaxnumanz(self,*args,**kwds):
    """
    Sets the number of preallocated non-zero entries in the linear coefficient matrix.
  
    putmaxnumanz(maxnumanz)
      [maxnumanz : int64]  New size of the storage reserved for storing the linear coefficient matrix.  
    """
    return self.__putmaxnumanz_2(*args,**kwds)
  def __putmaxnumqnz_2(self,maxnumqnz):
    _res_putmaxnumqnz = __library__.MSK_putmaxnumqnz(self.__nativep,maxnumqnz)
    if _res_putmaxnumqnz != 0:
      _,_msg_putmaxnumqnz = self.__getlasterror(_res_putmaxnumqnz)
      raise Error(rescode(_res_putmaxnumqnz),_msg_putmaxnumqnz)
  def putmaxnumqnz(self,*args,**kwds):
    """
    Sets the number of preallocated non-zero entries in quadratic terms.
  
    putmaxnumqnz(maxnumqnz)
      [maxnumqnz : int64]  Number of non-zero elements preallocated in quadratic coefficient matrices.  
    """
    return self.__putmaxnumqnz_2(*args,**kwds)
  def __getmaxnumqnz64_1(self):
    maxnumqnz_ = ctypes.c_int64()
    _res_getmaxnumqnz64 = __library__.MSK_getmaxnumqnz64(self.__nativep,ctypes.byref(maxnumqnz_))
    if _res_getmaxnumqnz64 != 0:
      _,_msg_getmaxnumqnz64 = self.__getlasterror(_res_getmaxnumqnz64)
      raise Error(rescode(_res_getmaxnumqnz64),_msg_getmaxnumqnz64)
    maxnumqnz = maxnumqnz_.value
    return (maxnumqnz_.value)
  def getmaxnumqnz(self,*args,**kwds):
    """
    Obtains the number of preallocated non-zeros for all quadratic terms in objective and constraints.
  
    getmaxnumqnz() -> (maxnumqnz)
      [maxnumqnz : int64]  Number of non-zero elements preallocated in quadratic coefficient matrices.  
    """
    return self.__getmaxnumqnz64_1(*args,**kwds)
  def __putnadouparam_3(self,paramname,parvalue):
    _res_putnadouparam = __library__.MSK_putnadouparam(self.__nativep,paramname.encode("UTF-8"),parvalue)
    if _res_putnadouparam != 0:
      _,_msg_putnadouparam = self.__getlasterror(_res_putnadouparam)
      raise Error(rescode(_res_putnadouparam),_msg_putnadouparam)
  def putnadouparam(self,*args,**kwds):
    """
    Sets a double parameter.
  
    putnadouparam(paramname,parvalue)
      [paramname : str]  Name of a parameter.  
      [parvalue : float64]  Parameter value.  
    """
    return self.__putnadouparam_3(*args,**kwds)
  def __putnaintparam_3(self,paramname,parvalue):
    _res_putnaintparam = __library__.MSK_putnaintparam(self.__nativep,paramname.encode("UTF-8"),parvalue)
    if _res_putnaintparam != 0:
      _,_msg_putnaintparam = self.__getlasterror(_res_putnaintparam)
      raise Error(rescode(_res_putnaintparam),_msg_putnaintparam)
  def putnaintparam(self,*args,**kwds):
    """
    Sets an integer parameter.
  
    putnaintparam(paramname,parvalue)
      [paramname : str]  Name of a parameter.  
      [parvalue : int32]  Parameter value.  
    """
    return self.__putnaintparam_3(*args,**kwds)
  def __putnastrparam_3(self,paramname,parvalue):
    _res_putnastrparam = __library__.MSK_putnastrparam(self.__nativep,paramname.encode("UTF-8"),parvalue.encode("UTF-8"))
    if _res_putnastrparam != 0:
      _,_msg_putnastrparam = self.__getlasterror(_res_putnastrparam)
      raise Error(rescode(_res_putnastrparam),_msg_putnastrparam)
  def putnastrparam(self,*args,**kwds):
    """
    Sets a string parameter.
  
    putnastrparam(paramname,parvalue)
      [paramname : str]  Name of a parameter.  
      [parvalue : str]  Parameter value.  
    """
    return self.__putnastrparam_3(*args,**kwds)
  def __putobjname_2(self,objname):
    _res_putobjname = __library__.MSK_putobjname(self.__nativep,objname.encode("UTF-8"))
    if _res_putobjname != 0:
      _,_msg_putobjname = self.__getlasterror(_res_putobjname)
      raise Error(rescode(_res_putobjname),_msg_putobjname)
  def putobjname(self,*args,**kwds):
    """
    Assigns a new name to the objective.
  
    putobjname(objname)
      [objname : str]  Name of the objective.  
    """
    return self.__putobjname_2(*args,**kwds)
  def __putparam_3(self,parname,parvalue):
    _res_putparam = __library__.MSK_putparam(self.__nativep,parname.encode("UTF-8"),parvalue.encode("UTF-8"))
    if _res_putparam != 0:
      _,_msg_putparam = self.__getlasterror(_res_putparam)
      raise Error(rescode(_res_putparam),_msg_putparam)
  def putparam(self,*args,**kwds):
    """
    Modifies the value of parameter.
  
    putparam(parname,parvalue)
      [parname : str]  Parameter name.  
      [parvalue : str]  Parameter value.  
    """
    return self.__putparam_3(*args,**kwds)
  def __putqcon_5(self,qcsubk,qcsubi,qcsubj,qcval):
    numqcnz = min(len(qcsubi) if qcsubi is not None else 0,len(qcsubj) if qcsubj is not None else 0,len(qcval) if qcval is not None else 0)
    copyback_qcsubk = False
    if qcsubk is None:
      qcsubk_ = None
      _tmparray_qcsubk_ = None
    else:
      _tmparray_qcsubk_ = (ctypes.c_int32*len(qcsubk))(*qcsubk)
    copyback_qcsubi = False
    if qcsubi is None:
      qcsubi_ = None
      _tmparray_qcsubi_ = None
    else:
      _tmparray_qcsubi_ = (ctypes.c_int32*len(qcsubi))(*qcsubi)
    copyback_qcsubj = False
    if qcsubj is None:
      qcsubj_ = None
      _tmparray_qcsubj_ = None
    else:
      _tmparray_qcsubj_ = (ctypes.c_int32*len(qcsubj))(*qcsubj)
    copyback_qcval = False
    if qcval is None:
      qcval_ = None
      _tmparray_qcval_ = None
    else:
      _tmparray_qcval_ = (ctypes.c_double*len(qcval))(*qcval)
    _res_putqcon = __library__.MSK_putqcon(self.__nativep,numqcnz,_tmparray_qcsubk_,_tmparray_qcsubi_,_tmparray_qcsubj_,_tmparray_qcval_)
    if _res_putqcon != 0:
      _,_msg_putqcon = self.__getlasterror(_res_putqcon)
      raise Error(rescode(_res_putqcon),_msg_putqcon)
  def putqcon(self,*args,**kwds):
    """
    Replaces all quadratic terms in constraints.
  
    putqcon(qcsubk,qcsubi,qcsubj,qcval)
      [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
      [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
      [qcsubk : array(int32)]  Constraint subscripts for quadratic coefficients.  
      [qcval : array(float64)]  Quadratic constraint coefficient values.  
    """
    return self.__putqcon_5(*args,**kwds)
  def __putqconk_5(self,k,qcsubi,qcsubj,qcval):
    numqcnz = min(len(qcsubi) if qcsubi is not None else 0,len(qcsubj) if qcsubj is not None else 0,len(qcval) if qcval is not None else 0)
    copyback_qcsubi = False
    if qcsubi is None:
      qcsubi_ = None
      _tmparray_qcsubi_ = None
    else:
      _tmparray_qcsubi_ = (ctypes.c_int32*len(qcsubi))(*qcsubi)
    copyback_qcsubj = False
    if qcsubj is None:
      qcsubj_ = None
      _tmparray_qcsubj_ = None
    else:
      _tmparray_qcsubj_ = (ctypes.c_int32*len(qcsubj))(*qcsubj)
    copyback_qcval = False
    if qcval is None:
      qcval_ = None
      _tmparray_qcval_ = None
    else:
      _tmparray_qcval_ = (ctypes.c_double*len(qcval))(*qcval)
    _res_putqconk = __library__.MSK_putqconk(self.__nativep,k,numqcnz,_tmparray_qcsubi_,_tmparray_qcsubj_,_tmparray_qcval_)
    if _res_putqconk != 0:
      _,_msg_putqconk = self.__getlasterror(_res_putqconk)
      raise Error(rescode(_res_putqconk),_msg_putqconk)
  def putqconk(self,*args,**kwds):
    """
    Replaces all quadratic terms in a single constraint.
  
    putqconk(k,qcsubi,qcsubj,qcval)
      [k : int32]  The constraint in which the new quadratic elements are inserted.  
      [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
      [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
      [qcval : array(float64)]  Quadratic constraint coefficient values.  
    """
    return self.__putqconk_5(*args,**kwds)
  def __putqobj_4(self,qosubi,qosubj,qoval):
    numqonz = min(len(qosubi) if qosubi is not None else 0,len(qosubj) if qosubj is not None else 0,len(qoval) if qoval is not None else 0)
    copyback_qosubi = False
    if qosubi is None:
      qosubi_ = None
      _tmparray_qosubi_ = None
    else:
      _tmparray_qosubi_ = (ctypes.c_int32*len(qosubi))(*qosubi)
    copyback_qosubj = False
    if qosubj is None:
      qosubj_ = None
      _tmparray_qosubj_ = None
    else:
      _tmparray_qosubj_ = (ctypes.c_int32*len(qosubj))(*qosubj)
    copyback_qoval = False
    if qoval is None:
      qoval_ = None
      _tmparray_qoval_ = None
    else:
      _tmparray_qoval_ = (ctypes.c_double*len(qoval))(*qoval)
    _res_putqobj = __library__.MSK_putqobj(self.__nativep,numqonz,_tmparray_qosubi_,_tmparray_qosubj_,_tmparray_qoval_)
    if _res_putqobj != 0:
      _,_msg_putqobj = self.__getlasterror(_res_putqobj)
      raise Error(rescode(_res_putqobj),_msg_putqobj)
  def putqobj(self,*args,**kwds):
    """
    Replaces all quadratic terms in the objective.
  
    putqobj(qosubi,qosubj,qoval)
      [qosubi : array(int32)]  Row subscripts for quadratic objective coefficients.  
      [qosubj : array(int32)]  Column subscripts for quadratic objective coefficients.  
      [qoval : array(float64)]  Quadratic objective coefficient values.  
    """
    return self.__putqobj_4(*args,**kwds)
  def __putqobjij_4(self,i,j,qoij):
    _res_putqobjij = __library__.MSK_putqobjij(self.__nativep,i,j,qoij)
    if _res_putqobjij != 0:
      _,_msg_putqobjij = self.__getlasterror(_res_putqobjij)
      raise Error(rescode(_res_putqobjij),_msg_putqobjij)
  def putqobjij(self,*args,**kwds):
    """
    Replaces one coefficient in the quadratic term in the objective.
  
    putqobjij(i,j,qoij)
      [i : int32]  Row index for the coefficient to be replaced.  
      [j : int32]  Column index for the coefficient to be replaced.  
      [qoij : float64]  The new coefficient value.  
    """
    return self.__putqobjij_4(*args,**kwds)
  def __putsolution_13(self,whichsol : soltype,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skc_ = (ctypes.c_int32*len(skc))(*skc)
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skx_ = (ctypes.c_int32*len(skx))(*skx)
    if skn is None:
      _tmparray_skn_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skn_ = (ctypes.c_int32*len(skn))(*skn)
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    _res_putsolution = __library__.MSK_putsolution(self.__nativep,whichsol,_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,_tmparray_xc_,_tmparray_xx_,_tmparray_y_,_tmparray_slc_,_tmparray_suc_,_tmparray_slx_,_tmparray_sux_,_tmparray_snx_)
    if _res_putsolution != 0:
      _,_msg_putsolution = self.__getlasterror(_res_putsolution)
      raise Error(rescode(_res_putsolution),_msg_putsolution)
  def putsolution(self,*args,**kwds):
    """
    Inserts a solution.
  
    putsolution(skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx)
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
      [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
      [xc : array(float64)]  Primal constraint solution.  
      [xx : array(float64)]  Primal variable solution.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    return self.__putsolution_13(*args,**kwds)
  def __putsolutionnew_14(self,whichsol : soltype,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty):
    if skc is None:
      _tmparray_skc_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skc_ = (ctypes.c_int32*len(skc))(*skc)
    if skx is None:
      _tmparray_skx_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skx_ = (ctypes.c_int32*len(skx))(*skx)
    if skn is None:
      _tmparray_skn_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_skn_ = (ctypes.c_int32*len(skn))(*skn)
    copyback_xc = False
    if xc is None:
      xc_ = None
      _tmparray_xc_ = None
    else:
      _tmparray_xc_ = (ctypes.c_double*len(xc))(*xc)
    copyback_xx = False
    if xx is None:
      xx_ = None
      _tmparray_xx_ = None
    else:
      _tmparray_xx_ = (ctypes.c_double*len(xx))(*xx)
    copyback_y = False
    if y is None:
      y_ = None
      _tmparray_y_ = None
    else:
      _tmparray_y_ = (ctypes.c_double*len(y))(*y)
    copyback_slc = False
    if slc is None:
      slc_ = None
      _tmparray_slc_ = None
    else:
      _tmparray_slc_ = (ctypes.c_double*len(slc))(*slc)
    copyback_suc = False
    if suc is None:
      suc_ = None
      _tmparray_suc_ = None
    else:
      _tmparray_suc_ = (ctypes.c_double*len(suc))(*suc)
    copyback_slx = False
    if slx is None:
      slx_ = None
      _tmparray_slx_ = None
    else:
      _tmparray_slx_ = (ctypes.c_double*len(slx))(*slx)
    copyback_sux = False
    if sux is None:
      sux_ = None
      _tmparray_sux_ = None
    else:
      _tmparray_sux_ = (ctypes.c_double*len(sux))(*sux)
    copyback_snx = False
    if snx is None:
      snx_ = None
      _tmparray_snx_ = None
    else:
      _tmparray_snx_ = (ctypes.c_double*len(snx))(*snx)
    copyback_doty = False
    if doty is None:
      doty_ = None
      _tmparray_doty_ = None
    else:
      _tmparray_doty_ = (ctypes.c_double*len(doty))(*doty)
    _res_putsolutionnew = __library__.MSK_putsolutionnew(self.__nativep,whichsol,_tmparray_skc_,_tmparray_skx_,_tmparray_skn_,_tmparray_xc_,_tmparray_xx_,_tmparray_y_,_tmparray_slc_,_tmparray_suc_,_tmparray_slx_,_tmparray_sux_,_tmparray_snx_,_tmparray_doty_)
    if _res_putsolutionnew != 0:
      _,_msg_putsolutionnew = self.__getlasterror(_res_putsolutionnew)
      raise Error(rescode(_res_putsolutionnew),_msg_putsolutionnew)
  def putsolutionnew(self,*args,**kwds):
    """
    Inserts a solution.
  
    putsolutionnew(skc,
                   skx,
                   skn,
                   xc,
                   xx,
                   y,
                   slc,
                   suc,
                   slx,
                   sux,
                   snx,
                   doty)
      [doty : array(float64)]  Dual variables corresponding to affine conic constraints.  
      [skc : array(mosek.stakey)]  Status keys for the constraints.  
      [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
      [skx : array(mosek.stakey)]  Status keys for the variables.  
      [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
      [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
      [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
      [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
      [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
      [xc : array(float64)]  Primal constraint solution.  
      [xx : array(float64)]  Primal variable solution.  
      [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
    """
    return self.__putsolutionnew_14(*args,**kwds)
  def __putconsolutioni_7(self,i,whichsol : soltype,sk : stakey,x,sl,su):
    _res_putconsolutioni = __library__.MSK_putconsolutioni(self.__nativep,i,whichsol,sk,x,sl,su)
    if _res_putconsolutioni != 0:
      _,_msg_putconsolutioni = self.__getlasterror(_res_putconsolutioni)
      raise Error(rescode(_res_putconsolutioni),_msg_putconsolutioni)
  def putconsolutioni(self,*args,**kwds):
    """
    Sets the primal and dual solution information for a single constraint.
  
    putconsolutioni(i,x,sl,su)
      [i : int32]  Index of the constraint.  
      [sl : float64]  Solution value of the dual variable associated with the lower bound.  
      [su : float64]  Solution value of the dual variable associated with the upper bound.  
      [x : float64]  Primal solution value of the constraint.  
    """
    return self.__putconsolutioni_7(*args,**kwds)
  def __putvarsolutionj_8(self,j,whichsol : soltype,sk : stakey,x,sl,su,sn):
    _res_putvarsolutionj = __library__.MSK_putvarsolutionj(self.__nativep,j,whichsol,sk,x,sl,su,sn)
    if _res_putvarsolutionj != 0:
      _,_msg_putvarsolutionj = self.__getlasterror(_res_putvarsolutionj)
      raise Error(rescode(_res_putvarsolutionj),_msg_putvarsolutionj)
  def putvarsolutionj(self,*args,**kwds):
    """
    Sets the primal and dual solution information for a single variable.
  
    putvarsolutionj(j,x,sl,su,sn)
      [j : int32]  Index of the variable.  
      [sl : float64]  Solution value of the dual variable associated with the lower bound.  
      [sn : float64]  Solution value of the dual variable associated with the conic constraint.  
      [su : float64]  Solution value of the dual variable associated with the upper bound.  
      [x : float64]  Primal solution value of the variable.  
    """
    return self.__putvarsolutionj_8(*args,**kwds)
  def __putsolutionyi_4(self,i,whichsol : soltype,y):
    _res_putsolutionyi = __library__.MSK_putsolutionyi(self.__nativep,i,whichsol,y)
    if _res_putsolutionyi != 0:
      _,_msg_putsolutionyi = self.__getlasterror(_res_putsolutionyi)
      raise Error(rescode(_res_putsolutionyi),_msg_putsolutionyi)
  def putsolutionyi(self,*args,**kwds):
    """
    Inputs the dual variable of a solution.
  
    putsolutionyi(i,y)
      [i : int32]  Index of the dual variable.  
      [y : float64]  Solution value of the dual variable.  
    """
    return self.__putsolutionyi_4(*args,**kwds)
  def __putstrparam_3(self,param : sparam,parvalue):
    _res_putstrparam = __library__.MSK_putstrparam(self.__nativep,param,parvalue.encode("UTF-8"))
    if _res_putstrparam != 0:
      _,_msg_putstrparam = self.__getlasterror(_res_putstrparam)
      raise Error(rescode(_res_putstrparam),_msg_putstrparam)
  def putstrparam(self,*args,**kwds):
    """
    Sets a string parameter.
  
    putstrparam(parvalue)
      [parvalue : str]  Parameter value.  
    """
    return self.__putstrparam_3(*args,**kwds)
  def __puttaskname_2(self,taskname):
    _res_puttaskname = __library__.MSK_puttaskname(self.__nativep,taskname.encode("UTF-8"))
    if _res_puttaskname != 0:
      _,_msg_puttaskname = self.__getlasterror(_res_puttaskname)
      raise Error(rescode(_res_puttaskname),_msg_puttaskname)
  def puttaskname(self,*args,**kwds):
    """
    Assigns a new name to the task.
  
    puttaskname(taskname)
      [taskname : str]  Name assigned to the task.  
    """
    return self.__puttaskname_2(*args,**kwds)
  def __putvartype_3(self,j,vartype : variabletype):
    _res_putvartype = __library__.MSK_putvartype(self.__nativep,j,vartype)
    if _res_putvartype != 0:
      _,_msg_putvartype = self.__getlasterror(_res_putvartype)
      raise Error(rescode(_res_putvartype),_msg_putvartype)
  def putvartype(self,*args,**kwds):
    """
    Sets the variable type of one variable.
  
    putvartype(j)
      [j : int32]  Index of the variable.  
    """
    return self.__putvartype_3(*args,**kwds)
  def __putvartypelist_3(self,subj,vartype):
    num = min(len(subj) if subj is not None else 0,len(vartype) if vartype is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    if vartype is None:
      _tmparray_vartype_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_vartype_ = (ctypes.c_int32*len(vartype))(*vartype)
    _res_putvartypelist = __library__.MSK_putvartypelist(self.__nativep,num,_tmparray_subj_,_tmparray_vartype_)
    if _res_putvartypelist != 0:
      _,_msg_putvartypelist = self.__getlasterror(_res_putvartypelist)
      raise Error(rescode(_res_putvartypelist),_msg_putvartypelist)
  def putvartypelist(self,*args,**kwds):
    """
    Sets the variable type for one or more variables.
  
    putvartypelist(subj,vartype)
      [subj : array(int32)]  A list of variable indexes for which the variable type should be changed.  
      [vartype : array(mosek.variabletype)]  A list of variable types.  
    """
    return self.__putvartypelist_3(*args,**kwds)
  def __readdataformat_4(self,filename,format : dataformat,compress : compresstype):
    _res_readdataformat = __library__.MSK_readdataformat(self.__nativep,filename.encode("UTF-8"),format,compress)
    if _res_readdataformat != 0:
      _,_msg_readdataformat = self.__getlasterror(_res_readdataformat)
      raise Error(rescode(_res_readdataformat),_msg_readdataformat)
  def readdataformat(self,*args,**kwds):
    """
    Reads problem data from a file.
  
    readdataformat(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readdataformat_4(*args,**kwds)
  def __readdataautoformat_2(self,filename):
    _res_readdataautoformat = __library__.MSK_readdataautoformat(self.__nativep,filename.encode("UTF-8"))
    if _res_readdataautoformat != 0:
      _,_msg_readdataautoformat = self.__getlasterror(_res_readdataautoformat)
      raise Error(rescode(_res_readdataautoformat),_msg_readdataautoformat)
  def readdata(self,*args,**kwds):
    """
    Reads problem data from a file.
  
    readdata(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readdataautoformat_2(*args,**kwds)
  def __readparamfile_2(self,filename):
    _res_readparamfile = __library__.MSK_readparamfile(self.__nativep,filename.encode("UTF-8"))
    if _res_readparamfile != 0:
      _,_msg_readparamfile = self.__getlasterror(_res_readparamfile)
      raise Error(rescode(_res_readparamfile),_msg_readparamfile)
  def readparamfile(self,*args,**kwds):
    """
    Reads a parameter file.
  
    readparamfile(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readparamfile_2(*args,**kwds)
  def __readsolution_3(self,whichsol : soltype,filename):
    _res_readsolution = __library__.MSK_readsolution(self.__nativep,whichsol,filename.encode("UTF-8"))
    if _res_readsolution != 0:
      _,_msg_readsolution = self.__getlasterror(_res_readsolution)
      raise Error(rescode(_res_readsolution),_msg_readsolution)
  def readsolution(self,*args,**kwds):
    """
    Reads a solution from a file.
  
    readsolution(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readsolution_3(*args,**kwds)
  def __readjsonsol_2(self,filename):
    _res_readjsonsol = __library__.MSK_readjsonsol(self.__nativep,filename.encode("UTF-8"))
    if _res_readjsonsol != 0:
      _,_msg_readjsonsol = self.__getlasterror(_res_readjsonsol)
      raise Error(rescode(_res_readjsonsol),_msg_readjsonsol)
  def readjsonsol(self,*args,**kwds):
    """
    Reads a solution from a JSOL file.
  
    readjsonsol(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readjsonsol_2(*args,**kwds)
  def __readsummary_2(self,whichstream : streamtype):
    _res_readsummary = __library__.MSK_readsummary(self.__nativep,whichstream)
    if _res_readsummary != 0:
      _,_msg_readsummary = self.__getlasterror(_res_readsummary)
      raise Error(rescode(_res_readsummary),_msg_readsummary)
  def readsummary(self,*args,**kwds):
    """
    Prints information about last file read.
  
    readsummary()
    """
    return self.__readsummary_2(*args,**kwds)
  def __resizetask_6(self,maxnumcon,maxnumvar,maxnumcone,maxnumanz,maxnumqnz):
    _res_resizetask = __library__.MSK_resizetask(self.__nativep,maxnumcon,maxnumvar,maxnumcone,maxnumanz,maxnumqnz)
    if _res_resizetask != 0:
      _,_msg_resizetask = self.__getlasterror(_res_resizetask)
      raise Error(rescode(_res_resizetask),_msg_resizetask)
  def resizetask(self,*args,**kwds):
    """
    Resizes an optimization task.
  
    resizetask(maxnumcon,
               maxnumvar,
               maxnumcone,
               maxnumanz,
               maxnumqnz)
      [maxnumanz : int64]  New maximum number of linear non-zero elements.  
      [maxnumcon : int32]  New maximum number of constraints.  
      [maxnumcone : int32]  New maximum number of cones.  
      [maxnumqnz : int64]  New maximum number of quadratic non-zeros elements.  
      [maxnumvar : int32]  New maximum number of variables.  
    """
    return self.__resizetask_6(*args,**kwds)
  def __checkmemtask_3(self,file,line):
    _res_checkmemtask = __library__.MSK_checkmemtask(self.__nativep,file.encode("UTF-8"),line)
    if _res_checkmemtask != 0:
      _,_msg_checkmemtask = self.__getlasterror(_res_checkmemtask)
      raise Error(rescode(_res_checkmemtask),_msg_checkmemtask)
  def checkmem(self,*args,**kwds):
    """
    Checks the memory allocated by the task.
  
    checkmem(file,line)
      [file : str]  File from which the function is called.  
      [line : int32]  Line in the file from which the function is called.  
    """
    return self.__checkmemtask_3(*args,**kwds)
  def __getmemusagetask_1(self):
    meminuse_ = ctypes.c_int64()
    maxmemuse_ = ctypes.c_int64()
    _res_getmemusagetask = __library__.MSK_getmemusagetask(self.__nativep,ctypes.byref(meminuse_),ctypes.byref(maxmemuse_))
    if _res_getmemusagetask != 0:
      _,_msg_getmemusagetask = self.__getlasterror(_res_getmemusagetask)
      raise Error(rescode(_res_getmemusagetask),_msg_getmemusagetask)
    meminuse = meminuse_.value
    maxmemuse = maxmemuse_.value
    return (meminuse_.value,maxmemuse_.value)
  def getmemusage(self,*args,**kwds):
    """
    Obtains information about the amount of memory used by a task.
  
    getmemusage() -> (meminuse,maxmemuse)
      [maxmemuse : int64]  Maximum amount of memory used by the task until now.  
      [meminuse : int64]  Amount of memory currently used by the task.  
    """
    return self.__getmemusagetask_1(*args,**kwds)
  def __setdefaults_1(self):
    _res_setdefaults = __library__.MSK_setdefaults(self.__nativep)
    if _res_setdefaults != 0:
      _,_msg_setdefaults = self.__getlasterror(_res_setdefaults)
      raise Error(rescode(_res_setdefaults),_msg_setdefaults)
  def setdefaults(self,*args,**kwds):
    """
    Resets all parameter values.
  
    setdefaults()
    """
    return self.__setdefaults_1(*args,**kwds)
  def __solutiondef_2(self,whichsol : soltype):
    isdef_ = ctypes.c_int32()
    _res_solutiondef = __library__.MSK_solutiondef(self.__nativep,whichsol,ctypes.byref(isdef_))
    if _res_solutiondef != 0:
      _,_msg_solutiondef = self.__getlasterror(_res_solutiondef)
      raise Error(rescode(_res_solutiondef),_msg_solutiondef)
    isdef = isdef_.value
    return (isdef_.value)
  def solutiondef(self,*args,**kwds):
    """
    Checks whether a solution is defined.
  
    solutiondef() -> (isdef)
      [isdef : bool]  Is non-zero if the requested solution is defined.  
    """
    return self.__solutiondef_2(*args,**kwds)
  def __deletesolution_2(self,whichsol : soltype):
    _res_deletesolution = __library__.MSK_deletesolution(self.__nativep,whichsol)
    if _res_deletesolution != 0:
      _,_msg_deletesolution = self.__getlasterror(_res_deletesolution)
      raise Error(rescode(_res_deletesolution),_msg_deletesolution)
  def deletesolution(self,*args,**kwds):
    """
    Undefine a solution and free the memory it uses.
  
    deletesolution()
    """
    return self.__deletesolution_2(*args,**kwds)
  def __onesolutionsummary_3(self,whichstream : streamtype,whichsol : soltype):
    _res_onesolutionsummary = __library__.MSK_onesolutionsummary(self.__nativep,whichstream,whichsol)
    if _res_onesolutionsummary != 0:
      _,_msg_onesolutionsummary = self.__getlasterror(_res_onesolutionsummary)
      raise Error(rescode(_res_onesolutionsummary),_msg_onesolutionsummary)
  def onesolutionsummary(self,*args,**kwds):
    """
    Prints a short summary of a specified solution.
  
    onesolutionsummary()
    """
    return self.__onesolutionsummary_3(*args,**kwds)
  def __solutionsummary_2(self,whichstream : streamtype):
    _res_solutionsummary = __library__.MSK_solutionsummary(self.__nativep,whichstream)
    if _res_solutionsummary != 0:
      _,_msg_solutionsummary = self.__getlasterror(_res_solutionsummary)
      raise Error(rescode(_res_solutionsummary),_msg_solutionsummary)
  def solutionsummary(self,*args,**kwds):
    """
    Prints a short summary of the current solutions.
  
    solutionsummary()
    """
    return self.__solutionsummary_2(*args,**kwds)
  def __updatesolutioninfo_2(self,whichsol : soltype):
    _res_updatesolutioninfo = __library__.MSK_updatesolutioninfo(self.__nativep,whichsol)
    if _res_updatesolutioninfo != 0:
      _,_msg_updatesolutioninfo = self.__getlasterror(_res_updatesolutioninfo)
      raise Error(rescode(_res_updatesolutioninfo),_msg_updatesolutioninfo)
  def updatesolutioninfo(self,*args,**kwds):
    """
    Update the information items related to the solution.
  
    updatesolutioninfo()
    """
    return self.__updatesolutioninfo_2(*args,**kwds)
  def __optimizersummary_2(self,whichstream : streamtype):
    _res_optimizersummary = __library__.MSK_optimizersummary(self.__nativep,whichstream)
    if _res_optimizersummary != 0:
      _,_msg_optimizersummary = self.__getlasterror(_res_optimizersummary)
      raise Error(rescode(_res_optimizersummary),_msg_optimizersummary)
  def optimizersummary(self,*args,**kwds):
    """
    Prints a short summary with optimizer statistics from last optimization.
  
    optimizersummary()
    """
    return self.__optimizersummary_2(*args,**kwds)
  def __strtoconetype_2(self,str):
    conetype = ctypes.c_int()
    _res_strtoconetype = __library__.MSK_strtoconetype(self.__nativep,str.encode("UTF-8"),ctypes.byref(conetype))
    if _res_strtoconetype != 0:
      _,_msg_strtoconetype = self.__getlasterror(_res_strtoconetype)
      raise Error(rescode(_res_strtoconetype),_msg_strtoconetype)
    return (conetype(conetype.value))
  def strtoconetype(self,*args,**kwds):
    """
    Obtains a cone type code.
  
    strtoconetype(str) -> (conetype)
      [conetype : mosek.conetype]  The cone type corresponding to str.  
      [str : str]  String corresponding to the cone type code.  
    """
    return self.__strtoconetype_2(*args,**kwds)
  def __strtosk_2(self,str):
    sk = ctypes.c_int()
    _res_strtosk = __library__.MSK_strtosk(self.__nativep,str.encode("UTF-8"),ctypes.byref(sk))
    if _res_strtosk != 0:
      _,_msg_strtosk = self.__getlasterror(_res_strtosk)
      raise Error(rescode(_res_strtosk),_msg_strtosk)
    return (stakey(sk.value))
  def strtosk(self,*args,**kwds):
    """
    Obtains a status key.
  
    strtosk(str) -> (sk)
      [sk : mosek.stakey]  Status key corresponding to the string.  
      [str : str]  A status key abbreviation string.  
    """
    return self.__strtosk_2(*args,**kwds)
  def __writedata_2(self,filename):
    _res_writedata = __library__.MSK_writedata(self.__nativep,filename.encode("UTF-8"))
    if _res_writedata != 0:
      _,_msg_writedata = self.__getlasterror(_res_writedata)
      raise Error(rescode(_res_writedata),_msg_writedata)
  def writedata(self,*args,**kwds):
    """
    Writes problem data to a file.
  
    writedata(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writedata_2(*args,**kwds)
  def __writetask_2(self,filename):
    _res_writetask = __library__.MSK_writetask(self.__nativep,filename.encode("UTF-8"))
    if _res_writetask != 0:
      _,_msg_writetask = self.__getlasterror(_res_writetask)
      raise Error(rescode(_res_writetask),_msg_writetask)
  def writetask(self,*args,**kwds):
    """
    Write a complete binary dump of the task data.
  
    writetask(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writetask_2(*args,**kwds)
  def __writebsolution_3(self,filename,compress : compresstype):
    _res_writebsolution = __library__.MSK_writebsolution(self.__nativep,filename.encode("UTF-8"),compress)
    if _res_writebsolution != 0:
      _,_msg_writebsolution = self.__getlasterror(_res_writebsolution)
      raise Error(rescode(_res_writebsolution),_msg_writebsolution)
  def writebsolution(self,*args,**kwds):
    """
    Write a binary dump of the task solution and information items.
  
    writebsolution(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writebsolution_3(*args,**kwds)
  def __readbsolution_3(self,filename,compress : compresstype):
    _res_readbsolution = __library__.MSK_readbsolution(self.__nativep,filename.encode("UTF-8"),compress)
    if _res_readbsolution != 0:
      _,_msg_readbsolution = self.__getlasterror(_res_readbsolution)
      raise Error(rescode(_res_readbsolution),_msg_readbsolution)
  def readbsolution(self,*args,**kwds):
    """
    Read a binary dump of the task solution and information items.
  
    readbsolution(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readbsolution_3(*args,**kwds)
  def __writesolutionfile_2(self,filename):
    _res_writesolutionfile = __library__.MSK_writesolutionfile(self.__nativep,filename.encode("UTF-8"))
    if _res_writesolutionfile != 0:
      _,_msg_writesolutionfile = self.__getlasterror(_res_writesolutionfile)
      raise Error(rescode(_res_writesolutionfile),_msg_writesolutionfile)
  def writesolutionfile(self,*args,**kwds):
    """
    Write solution file in format determined by the filename
  
    writesolutionfile(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writesolutionfile_2(*args,**kwds)
  def __readsolutionfile_2(self,filename):
    _res_readsolutionfile = __library__.MSK_readsolutionfile(self.__nativep,filename.encode("UTF-8"))
    if _res_readsolutionfile != 0:
      _,_msg_readsolutionfile = self.__getlasterror(_res_readsolutionfile)
      raise Error(rescode(_res_readsolutionfile),_msg_readsolutionfile)
  def readsolutionfile(self,*args,**kwds):
    """
    Read solution file in format determined by the filename
  
    readsolutionfile(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readsolutionfile_2(*args,**kwds)
  def __readtask_2(self,filename):
    _res_readtask = __library__.MSK_readtask(self.__nativep,filename.encode("UTF-8"))
    if _res_readtask != 0:
      _,_msg_readtask = self.__getlasterror(_res_readtask)
      raise Error(rescode(_res_readtask),_msg_readtask)
  def readtask(self,*args,**kwds):
    """
    Load task data from a file.
  
    readtask(filename)
      [filename : str]  A valid file name.  
    """
    return self.__readtask_2(*args,**kwds)
  def __readopfstring_2(self,data):
    _res_readopfstring = __library__.MSK_readopfstring(self.__nativep,data.encode("UTF-8"))
    if _res_readopfstring != 0:
      _,_msg_readopfstring = self.__getlasterror(_res_readopfstring)
      raise Error(rescode(_res_readopfstring),_msg_readopfstring)
  def readopfstring(self,*args,**kwds):
    """
    Load task data from a string in OPF format.
  
    readopfstring(data)
      [data : str]  Problem data in text format.  
    """
    return self.__readopfstring_2(*args,**kwds)
  def __readlpstring_2(self,data):
    _res_readlpstring = __library__.MSK_readlpstring(self.__nativep,data.encode("UTF-8"))
    if _res_readlpstring != 0:
      _,_msg_readlpstring = self.__getlasterror(_res_readlpstring)
      raise Error(rescode(_res_readlpstring),_msg_readlpstring)
  def readlpstring(self,*args,**kwds):
    """
    Load task data from a string in LP format.
  
    readlpstring(data)
      [data : str]  Problem data in text format.  
    """
    return self.__readlpstring_2(*args,**kwds)
  def __readjsonstring_2(self,data):
    _res_readjsonstring = __library__.MSK_readjsonstring(self.__nativep,data.encode("UTF-8"))
    if _res_readjsonstring != 0:
      _,_msg_readjsonstring = self.__getlasterror(_res_readjsonstring)
      raise Error(rescode(_res_readjsonstring),_msg_readjsonstring)
  def readjsonstring(self,*args,**kwds):
    """
    Load task data from a string in JSON format.
  
    readjsonstring(data)
      [data : str]  Problem data in text format.  
    """
    return self.__readjsonstring_2(*args,**kwds)
  def __readptfstring_2(self,data):
    _res_readptfstring = __library__.MSK_readptfstring(self.__nativep,data.encode("UTF-8"))
    if _res_readptfstring != 0:
      _,_msg_readptfstring = self.__getlasterror(_res_readptfstring)
      raise Error(rescode(_res_readptfstring),_msg_readptfstring)
  def readptfstring(self,*args,**kwds):
    """
    Load task data from a string in PTF format.
  
    readptfstring(data)
      [data : str]  Problem data in text format.  
    """
    return self.__readptfstring_2(*args,**kwds)
  def __writeparamfile_2(self,filename):
    _res_writeparamfile = __library__.MSK_writeparamfile(self.__nativep,filename.encode("UTF-8"))
    if _res_writeparamfile != 0:
      _,_msg_writeparamfile = self.__getlasterror(_res_writeparamfile)
      raise Error(rescode(_res_writeparamfile),_msg_writeparamfile)
  def writeparamfile(self,*args,**kwds):
    """
    Writes all the parameters to a parameter file.
  
    writeparamfile(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writeparamfile_2(*args,**kwds)
  def __getinfeasiblesubproblem_2(self,whichsol : soltype):
    inftask = ctypes.c_voidp()
    _res_getinfeasiblesubproblem = __library__.MSK_getinfeasiblesubproblem(self.__nativep,whichsol,ctypes.byref(inftask))
    if _res_getinfeasiblesubproblem != 0:
      _,_msg_getinfeasiblesubproblem = self.__getlasterror(_res_getinfeasiblesubproblem)
      raise Error(rescode(_res_getinfeasiblesubproblem),_msg_getinfeasiblesubproblem)
    return (Task(nativep = inftask))
  def getinfeasiblesubproblem(self,*args,**kwds):
    """
    Obtains an infeasible subproblem.
  
    getinfeasiblesubproblem() -> (inftask)
      [inftask : mosek.Task]  A new task containing the infeasible subproblem.  
    """
    return self.__getinfeasiblesubproblem_2(*args,**kwds)
  def __writesolution_3(self,whichsol : soltype,filename):
    _res_writesolution = __library__.MSK_writesolution(self.__nativep,whichsol,filename.encode("UTF-8"))
    if _res_writesolution != 0:
      _,_msg_writesolution = self.__getlasterror(_res_writesolution)
      raise Error(rescode(_res_writesolution),_msg_writesolution)
  def writesolution(self,*args,**kwds):
    """
    Write a solution to a file.
  
    writesolution(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writesolution_3(*args,**kwds)
  def __writejsonsol_2(self,filename):
    _res_writejsonsol = __library__.MSK_writejsonsol(self.__nativep,filename.encode("UTF-8"))
    if _res_writejsonsol != 0:
      _,_msg_writejsonsol = self.__getlasterror(_res_writejsonsol)
      raise Error(rescode(_res_writejsonsol),_msg_writejsonsol)
  def writejsonsol(self,*args,**kwds):
    """
    Writes a solution to a JSON file.
  
    writejsonsol(filename)
      [filename : str]  A valid file name.  
    """
    return self.__writejsonsol_2(*args,**kwds)
  def __primalsensitivity_13(self,subi,marki,subj,markj,leftpricei,rightpricei,leftrangei,rightrangei,leftpricej,rightpricej,leftrangej,rightrangej):
    numi = min(len(subi) if subi is not None else 0,len(marki) if marki is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    if marki is None:
      _tmparray_marki_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_marki_ = (ctypes.c_int32*len(marki))(*marki)
    numj = min(len(subj) if subj is not None else 0,len(markj) if markj is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    if markj is None:
      _tmparray_markj_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_markj_ = (ctypes.c_int32*len(markj))(*markj)
    copyback_leftpricei = False
    if leftpricei is None:
      leftpricei_ = None
      _tmparray_leftpricei_ = None
    else:
      if len(leftpricei) < int(numi):
        raise ValueError("argument leftpricei is too short")
      _tmparray_leftpricei_ = (ctypes.c_double*len(leftpricei))(*leftpricei)
    copyback_rightpricei = False
    if rightpricei is None:
      rightpricei_ = None
      _tmparray_rightpricei_ = None
    else:
      if len(rightpricei) < int(numi):
        raise ValueError("argument rightpricei is too short")
      _tmparray_rightpricei_ = (ctypes.c_double*len(rightpricei))(*rightpricei)
    copyback_leftrangei = False
    if leftrangei is None:
      leftrangei_ = None
      _tmparray_leftrangei_ = None
    else:
      if len(leftrangei) < int(numi):
        raise ValueError("argument leftrangei is too short")
      _tmparray_leftrangei_ = (ctypes.c_double*len(leftrangei))(*leftrangei)
    copyback_rightrangei = False
    if rightrangei is None:
      rightrangei_ = None
      _tmparray_rightrangei_ = None
    else:
      if len(rightrangei) < int(numi):
        raise ValueError("argument rightrangei is too short")
      _tmparray_rightrangei_ = (ctypes.c_double*len(rightrangei))(*rightrangei)
    copyback_leftpricej = False
    if leftpricej is None:
      leftpricej_ = None
      _tmparray_leftpricej_ = None
    else:
      if len(leftpricej) < int(numj):
        raise ValueError("argument leftpricej is too short")
      _tmparray_leftpricej_ = (ctypes.c_double*len(leftpricej))(*leftpricej)
    copyback_rightpricej = False
    if rightpricej is None:
      rightpricej_ = None
      _tmparray_rightpricej_ = None
    else:
      if len(rightpricej) < int(numj):
        raise ValueError("argument rightpricej is too short")
      _tmparray_rightpricej_ = (ctypes.c_double*len(rightpricej))(*rightpricej)
    copyback_leftrangej = False
    if leftrangej is None:
      leftrangej_ = None
      _tmparray_leftrangej_ = None
    else:
      if len(leftrangej) < int(numj):
        raise ValueError("argument leftrangej is too short")
      _tmparray_leftrangej_ = (ctypes.c_double*len(leftrangej))(*leftrangej)
    copyback_rightrangej = False
    if rightrangej is None:
      rightrangej_ = None
      _tmparray_rightrangej_ = None
    else:
      if len(rightrangej) < int(numj):
        raise ValueError("argument rightrangej is too short")
      _tmparray_rightrangej_ = (ctypes.c_double*len(rightrangej))(*rightrangej)
    _res_primalsensitivity = __library__.MSK_primalsensitivity(self.__nativep,numi,_tmparray_subi_,_tmparray_marki_,numj,_tmparray_subj_,_tmparray_markj_,_tmparray_leftpricei_,_tmparray_rightpricei_,_tmparray_leftrangei_,_tmparray_rightrangei_,_tmparray_leftpricej_,_tmparray_rightpricej_,_tmparray_leftrangej_,_tmparray_rightrangej_)
    if _res_primalsensitivity != 0:
      _,_msg_primalsensitivity = self.__getlasterror(_res_primalsensitivity)
      raise Error(rescode(_res_primalsensitivity),_msg_primalsensitivity)
    if leftpricei is not None:
      for __tmp_1134,__tmp_1135 in enumerate(_tmparray_leftpricei_):
        leftpricei[__tmp_1134] = __tmp_1135
    if rightpricei is not None:
      for __tmp_1136,__tmp_1137 in enumerate(_tmparray_rightpricei_):
        rightpricei[__tmp_1136] = __tmp_1137
    if leftrangei is not None:
      for __tmp_1138,__tmp_1139 in enumerate(_tmparray_leftrangei_):
        leftrangei[__tmp_1138] = __tmp_1139
    if rightrangei is not None:
      for __tmp_1140,__tmp_1141 in enumerate(_tmparray_rightrangei_):
        rightrangei[__tmp_1140] = __tmp_1141
    if leftpricej is not None:
      for __tmp_1142,__tmp_1143 in enumerate(_tmparray_leftpricej_):
        leftpricej[__tmp_1142] = __tmp_1143
    if rightpricej is not None:
      for __tmp_1144,__tmp_1145 in enumerate(_tmparray_rightpricej_):
        rightpricej[__tmp_1144] = __tmp_1145
    if leftrangej is not None:
      for __tmp_1146,__tmp_1147 in enumerate(_tmparray_leftrangej_):
        leftrangej[__tmp_1146] = __tmp_1147
    if rightrangej is not None:
      for __tmp_1148,__tmp_1149 in enumerate(_tmparray_rightrangej_):
        rightrangej[__tmp_1148] = __tmp_1149
  def __primalsensitivity_5(self,subi,marki,subj,markj):
    numi = min(len(subi) if subi is not None else 0,len(marki) if marki is not None else 0)
    copyback_subi = False
    if subi is None:
      subi_ = None
      _tmparray_subi_ = None
    else:
      _tmparray_subi_ = (ctypes.c_int32*len(subi))(*subi)
    if marki is None:
      _tmparray_marki_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_marki_ = (ctypes.c_int32*len(marki))(*marki)
    numj = min(len(subj) if subj is not None else 0,len(markj) if markj is not None else 0)
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    if markj is None:
      _tmparray_markj_ = ctypes.POINTER(ctypes.c_int32)()
    else:
      _tmparray_markj_ = (ctypes.c_int32*len(markj))(*markj)
    leftpricei = numpy.zeros(numi,numpy.float64)
    rightpricei = numpy.zeros(numi,numpy.float64)
    leftrangei = numpy.zeros(numi,numpy.float64)
    rightrangei = numpy.zeros(numi,numpy.float64)
    leftpricej = numpy.zeros(numj,numpy.float64)
    rightpricej = numpy.zeros(numj,numpy.float64)
    leftrangej = numpy.zeros(numj,numpy.float64)
    rightrangej = numpy.zeros(numj,numpy.float64)
    _res_primalsensitivity = __library__.MSK_primalsensitivity(self.__nativep,numi,_tmparray_subi_,_tmparray_marki_,numj,_tmparray_subj_,_tmparray_markj_,ctypes.cast(leftpricei.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightpricei.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(leftrangei.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightrangei.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(leftpricej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightpricej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(leftrangej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightrangej.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_primalsensitivity != 0:
      _,_msg_primalsensitivity = self.__getlasterror(_res_primalsensitivity)
      raise Error(rescode(_res_primalsensitivity),_msg_primalsensitivity)
    return (leftpricei,rightpricei,leftrangei,rightrangei,leftpricej,rightpricej,leftrangej,rightrangej)
  def primalsensitivity(self,*args,**kwds):
    """
    Perform sensitivity analysis on bounds.
  
    primalsensitivity(subi,
                      marki,
                      subj,
                      markj,
                      leftpricei,
                      rightpricei,
                      leftrangei,
                      rightrangei,
                      leftpricej,
                      rightpricej,
                      leftrangej,
                      rightrangej)
    primalsensitivity(subi,marki,subj,markj) -> 
                     (leftpricei,
                      rightpricei,
                      leftrangei,
                      rightrangei,
                      leftpricej,
                      rightpricej,
                      leftrangej,
                      rightrangej)
      [leftpricei : array(float64)]  Left shadow price for constraints.  
      [leftpricej : array(float64)]  Left shadow price for variables.  
      [leftrangei : array(float64)]  Left range for constraints.  
      [leftrangej : array(float64)]  Left range for variables.  
      [marki : array(mosek.mark)]  Mark which constraint bounds to analyze.  
      [markj : array(mosek.mark)]  Mark which variable bounds to analyze.  
      [rightpricei : array(float64)]  Right shadow price for constraints.  
      [rightpricej : array(float64)]  Right shadow price for variables.  
      [rightrangei : array(float64)]  Right range for constraints.  
      [rightrangej : array(float64)]  Right range for variables.  
      [subi : array(int32)]  Indexes of constraints to analyze.  
      [subj : array(int32)]  Indexes of variables to analyze.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 13: return self.__primalsensitivity_13(*args,**kwds)
    elif len(args)+len(kwds)+1 == 5: return self.__primalsensitivity_5(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __sensitivityreport_2(self,whichstream : streamtype):
    _res_sensitivityreport = __library__.MSK_sensitivityreport(self.__nativep,whichstream)
    if _res_sensitivityreport != 0:
      _,_msg_sensitivityreport = self.__getlasterror(_res_sensitivityreport)
      raise Error(rescode(_res_sensitivityreport),_msg_sensitivityreport)
  def sensitivityreport(self,*args,**kwds):
    """
    Creates a sensitivity report.
  
    sensitivityreport()
    """
    return self.__sensitivityreport_2(*args,**kwds)
  def __dualsensitivity_6(self,subj,leftpricej,rightpricej,leftrangej,rightrangej):
    numj = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    copyback_leftpricej = False
    if leftpricej is None:
      leftpricej_ = None
      _tmparray_leftpricej_ = None
    else:
      if len(leftpricej) < int(numj):
        raise ValueError("argument leftpricej is too short")
      _tmparray_leftpricej_ = (ctypes.c_double*len(leftpricej))(*leftpricej)
    copyback_rightpricej = False
    if rightpricej is None:
      rightpricej_ = None
      _tmparray_rightpricej_ = None
    else:
      if len(rightpricej) < int(numj):
        raise ValueError("argument rightpricej is too short")
      _tmparray_rightpricej_ = (ctypes.c_double*len(rightpricej))(*rightpricej)
    copyback_leftrangej = False
    if leftrangej is None:
      leftrangej_ = None
      _tmparray_leftrangej_ = None
    else:
      if len(leftrangej) < int(numj):
        raise ValueError("argument leftrangej is too short")
      _tmparray_leftrangej_ = (ctypes.c_double*len(leftrangej))(*leftrangej)
    copyback_rightrangej = False
    if rightrangej is None:
      rightrangej_ = None
      _tmparray_rightrangej_ = None
    else:
      if len(rightrangej) < int(numj):
        raise ValueError("argument rightrangej is too short")
      _tmparray_rightrangej_ = (ctypes.c_double*len(rightrangej))(*rightrangej)
    _res_dualsensitivity = __library__.MSK_dualsensitivity(self.__nativep,numj,_tmparray_subj_,_tmparray_leftpricej_,_tmparray_rightpricej_,_tmparray_leftrangej_,_tmparray_rightrangej_)
    if _res_dualsensitivity != 0:
      _,_msg_dualsensitivity = self.__getlasterror(_res_dualsensitivity)
      raise Error(rescode(_res_dualsensitivity),_msg_dualsensitivity)
    if leftpricej is not None:
      for __tmp_1162,__tmp_1163 in enumerate(_tmparray_leftpricej_):
        leftpricej[__tmp_1162] = __tmp_1163
    if rightpricej is not None:
      for __tmp_1164,__tmp_1165 in enumerate(_tmparray_rightpricej_):
        rightpricej[__tmp_1164] = __tmp_1165
    if leftrangej is not None:
      for __tmp_1166,__tmp_1167 in enumerate(_tmparray_leftrangej_):
        leftrangej[__tmp_1166] = __tmp_1167
    if rightrangej is not None:
      for __tmp_1168,__tmp_1169 in enumerate(_tmparray_rightrangej_):
        rightrangej[__tmp_1168] = __tmp_1169
  def __dualsensitivity_2(self,subj):
    numj = len(subj) if subj is not None else 0
    copyback_subj = False
    if subj is None:
      subj_ = None
      _tmparray_subj_ = None
    else:
      _tmparray_subj_ = (ctypes.c_int32*len(subj))(*subj)
    leftpricej = numpy.zeros(numj,numpy.float64)
    rightpricej = numpy.zeros(numj,numpy.float64)
    leftrangej = numpy.zeros(numj,numpy.float64)
    rightrangej = numpy.zeros(numj,numpy.float64)
    _res_dualsensitivity = __library__.MSK_dualsensitivity(self.__nativep,numj,_tmparray_subj_,ctypes.cast(leftpricej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightpricej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(leftrangej.ctypes,ctypes.POINTER(ctypes.c_double)),ctypes.cast(rightrangej.ctypes,ctypes.POINTER(ctypes.c_double)))
    if _res_dualsensitivity != 0:
      _,_msg_dualsensitivity = self.__getlasterror(_res_dualsensitivity)
      raise Error(rescode(_res_dualsensitivity),_msg_dualsensitivity)
    return (leftpricej,rightpricej,leftrangej,rightrangej)
  def dualsensitivity(self,*args,**kwds):
    """
    Performs sensitivity analysis on objective coefficients.
  
    dualsensitivity(subj,
                    leftpricej,
                    rightpricej,
                    leftrangej,
                    rightrangej)
    dualsensitivity(subj) -> 
                   (leftpricej,
                    rightpricej,
                    leftrangej,
                    rightrangej)
      [leftpricej : array(float64)]  Left shadow prices for requested coefficients.  
      [leftrangej : array(float64)]  Left range for requested coefficients.  
      [rightpricej : array(float64)]  Right shadow prices for requested coefficients.  
      [rightrangej : array(float64)]  Right range for requested coefficients.  
      [subj : array(int32)]  Indexes of objective coefficients to analyze.  
    """
    if False: pass
    elif len(args)+len(kwds)+1 == 6: return self.__dualsensitivity_6(*args,**kwds)
    elif len(args)+len(kwds)+1 == 2: return self.__dualsensitivity_2(*args,**kwds)
    else: raise TypeError("Missing positional arguments")
  def __optimizermt_3(self,address,accesstoken):
    trmcode = ctypes.c_int()
    _res_optimizermt = __library__.MSK_optimizermt(self.__nativep,address.encode("UTF-8"),accesstoken.encode("UTF-8"),ctypes.byref(trmcode))
    if _res_optimizermt != 0:
      _,_msg_optimizermt = self.__getlasterror(_res_optimizermt)
      raise Error(rescode(_res_optimizermt),_msg_optimizermt)
    return (rescode(trmcode.value))
  def optimizermt(self,*args,**kwds):
    """
    Offload the optimization task to a solver server and wait for the solution.
  
    optimizermt(address,accesstoken) -> (trmcode)
      [accesstoken : str]  Access token.  
      [address : str]  Address of the OptServer.  
      [trmcode : mosek.rescode]  Is either OK or a termination response code.  
    """
    return self.__optimizermt_3(*args,**kwds)
  def __asyncoptimize_3(self,address,accesstoken):
    token = (ctypes.c_char*33)()
    _res_asyncoptimize = __library__.MSK_asyncoptimize(self.__nativep,address.encode("UTF-8"),accesstoken.encode("UTF-8"),token)
    if _res_asyncoptimize != 0:
      _,_msg_asyncoptimize = self.__getlasterror(_res_asyncoptimize)
      raise Error(rescode(_res_asyncoptimize),_msg_asyncoptimize)
    return (token.value.decode("utf-8",errors="ignore"))
  def asyncoptimize(self,*args,**kwds):
    """
    Offload the optimization task to a solver server in asynchronous mode.
  
    asyncoptimize(address,accesstoken) -> (token)
      [accesstoken : str]  Access token.  
      [address : str]  Address of the OptServer.  
      [token : str]  Returns the task token.  
    """
    return self.__asyncoptimize_3(*args,**kwds)
  def __asyncstop_4(self,address,accesstoken,token):
    _res_asyncstop = __library__.MSK_asyncstop(self.__nativep,address.encode("UTF-8"),accesstoken.encode("UTF-8"),token.encode("UTF-8"))
    if _res_asyncstop != 0:
      _,_msg_asyncstop = self.__getlasterror(_res_asyncstop)
      raise Error(rescode(_res_asyncstop),_msg_asyncstop)
  def asyncstop(self,*args,**kwds):
    """
    Request that the job identified by the token is terminated.
  
    asyncstop(address,accesstoken,token)
      [accesstoken : str]  Access token.  
      [address : str]  Address of the OptServer.  
      [token : str]  The task token.  
    """
    return self.__asyncstop_4(*args,**kwds)
  def __asyncpoll_4(self,address,accesstoken,token):
    respavailable_ = ctypes.c_int32()
    resp = ctypes.c_int()
    trm = ctypes.c_int()
    _res_asyncpoll = __library__.MSK_asyncpoll(self.__nativep,address.encode("UTF-8"),accesstoken.encode("UTF-8"),token.encode("UTF-8"),ctypes.byref(respavailable_),ctypes.byref(resp),ctypes.byref(trm))
    if _res_asyncpoll != 0:
      _,_msg_asyncpoll = self.__getlasterror(_res_asyncpoll)
      raise Error(rescode(_res_asyncpoll),_msg_asyncpoll)
    respavailable = respavailable_.value
    return (respavailable_.value,rescode(resp.value),rescode(trm.value))
  def asyncpoll(self,*args,**kwds):
    """
    Requests information about the status of the remote job.
  
    asyncpoll(address,accesstoken,token) -> (respavailable,resp,trm)
      [accesstoken : str]  Access token.  
      [address : str]  Address of the OptServer.  
      [resp : mosek.rescode]  Is the response code from the remote solver.  
      [respavailable : bool]  Indicates if a remote response is available.  
      [token : str]  The task token.  
      [trm : mosek.rescode]  Is either OK or a termination response code.  
    """
    return self.__asyncpoll_4(*args,**kwds)
  def __asyncgetresult_4(self,address,accesstoken,token):
    respavailable_ = ctypes.c_int32()
    resp = ctypes.c_int()
    trm = ctypes.c_int()
    _res_asyncgetresult = __library__.MSK_asyncgetresult(self.__nativep,address.encode("UTF-8"),accesstoken.encode("UTF-8"),token.encode("UTF-8"),ctypes.byref(respavailable_),ctypes.byref(resp),ctypes.byref(trm))
    if _res_asyncgetresult != 0:
      _,_msg_asyncgetresult = self.__getlasterror(_res_asyncgetresult)
      raise Error(rescode(_res_asyncgetresult),_msg_asyncgetresult)
    respavailable = respavailable_.value
    return (respavailable_.value,rescode(resp.value),rescode(trm.value))
  def asyncgetresult(self,*args,**kwds):
    """
    Request a solution from a remote job.
  
    asyncgetresult(address,accesstoken,token) -> (respavailable,resp,trm)
      [accesstoken : str]  Access token.  
      [address : str]  Address of the OptServer.  
      [resp : mosek.rescode]  Is the response code from the remote solver.  
      [respavailable : bool]  Indicates if a remote response is available.  
      [token : str]  The task token.  
      [trm : mosek.rescode]  Is either OK or a termination response code.  
    """
    return self.__asyncgetresult_4(*args,**kwds)
  def __putoptserverhost_2(self,host):
    _res_putoptserverhost = __library__.MSK_putoptserverhost(self.__nativep,host.encode("UTF-8"))
    if _res_putoptserverhost != 0:
      _,_msg_putoptserverhost = self.__getlasterror(_res_putoptserverhost)
      raise Error(rescode(_res_putoptserverhost),_msg_putoptserverhost)
  def putoptserverhost(self,*args,**kwds):
    """
    Specify an OptServer for remote calls.
  
    putoptserverhost(host)
      [host : str]  A URL specifying the optimization server to be used.  
    """
    return self.__putoptserverhost_2(*args,**kwds)



class LinAlg:
  __env = Env()
  
  axpy = __env.axpy
  dot  = __env.dot
  gemv = __env.gemv
  gemm = __env.gemm
  syrk = __env.syrk
  syeig = __env.syeig
  syevd = __env.syevd
  potrf = __env.potrf

if __name__ == '__main__':
    env = Env()
