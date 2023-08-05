from distutils.core import setup, Extension
from glob import glob
from platform import system
from numpy import get_include
from numpy.distutils.system_info import get_info, BlasNotFoundError 

### if you're having errors linking blas/lapack, set this to false:
USE_LAPACK = True

rootDir = ''

lib = ['m']
if system() == 'Linux':
    lib += ['rt']

sources = ['scsmodule.c', ] + glob(rootDir + 'src/*.c')
define_macros = [('PYTHON', None), ('DLONG', None)] # add ('BLAS64', None) for 64 bit blas libs
include_dirs = [rootDir + 'include', get_include()]
libraries = lib
extra_link_args = []
extra_compile_args = []

blas_info = get_info('blas_opt')
lapack_info = get_info('lapack_opt')
if blas_info and lapack_info and USE_LAPACK:
    include_dirs += blas_info.pop('include_dirs', []) + lapack_info.pop('include_dirs', [])
    define_macros += [('LAPACK_LIB_FOUND', None)] + blas_info.pop('define_macros', []) + lapack_info.pop('define_macros', [])
    libraries += blas_info.pop('libraries', []) + lapack_info.pop('libraries', [])
    extra_link_args += blas_info.pop('extra_link_args', []) + lapack_info.pop('extra_link_args', [])
    extra_compile_args += blas_info.pop('extra_compile_args', []) + lapack_info.pop('extra_compile_args', [])

_scs_direct = Extension(
                    name='_scs_direct',
                    sources=sources + glob(rootDir + 'linsys/direct/*.c') + glob(rootDir + 'linsys/direct/external/*.c'),
                    define_macros=define_macros,
                    include_dirs=include_dirs + [rootDir + 'linsys/direct/', rootDir + 'linsys/direct/external/'],
                    libraries=libraries,
                    extra_link_args=extra_link_args,
                    extra_compile_args=extra_compile_args
                    )

_scs_indirect = Extension(
                    name='_scs_indirect',
                    sources=sources + glob(rootDir + 'linsys/indirect/*.c'),
                    define_macros=define_macros + [('INDIRECT', None)],
                    include_dirs=include_dirs + [rootDir + 'linsys/indirect/'],
                    libraries=libraries,
                    extra_link_args=extra_link_args,
                    extra_compile_args=extra_compile_args
                     )
setup(name='scs',
        version='1.0.2',
        author = 'Brendan O\'Donoghue',
        author_email = 'bodonoghue85@gmail.com',
        url = 'http://github.com/cvxgrp/scs',
        description='scs: splittling cone solver',
        py_modules=['scs'],
        ext_modules=[_scs_direct, _scs_indirect],
        requires=["numpy (>= 1.7)","scipy (>= 1.2)"],
        license = "GPLv3",
        long_description="Solves convex cone programs via operator splitting. Can solve: linear programs (LPs) second-order cone programs (SOCPs), semidefinite programs (SDPs), and exponential cone programs (EXPs). See http://github.com/cvxgrp/scs for more details."
        )
