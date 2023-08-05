#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

from setuptools import setup, find_packages
from setuptools.extension import Extension
from setuptools.command.install import install

import os, sys
from subprocess import Popen, PIPE

class orthpolxx_install(install):
    
    def run(self):

        print "Installation of ORTHPOLxx"
                
        os.chdir("./ORTHPOLxx")

        error = os.system("chmod u+x configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        
        currpath = os.getcwd()
        error = os.system("CFLAGS=-fPIC FFLAGS=-fPIC CPPFLAGS=-fPIC ./configure")
        
        if error: raise Exception("Compile error of ORTHPOLxx")
        error = os.system("make")
        if error: raise Exception("Compile error of ORTHPOLxx")
                
        os.chdir("../")
        
        print "Installation of PyORTHPOL"

        install.run(self)


if __name__ == "__main__":
        
    oxx_inc = ['./ORTHPOLxx/build/include/liborthpol-1.0']
    # oxx_ld = "-L/ORTHPOLxx/build/lib/liborthpol-1.0.a"
    oxx_ld = ['ORTHPOLxx/src/cheb.o', 
              'ORTHPOLxx/src/chri.o',
              'ORTHPOLxx/src/d1mach.o',
              'ORTHPOLxx/src/dcheb.o',
              'ORTHPOLxx/src/dchri.o',
              'ORTHPOLxx/src/dgauss.o',
              'ORTHPOLxx/src/dgchri.o',
              'ORTHPOLxx/src/dkern.o',
              'ORTHPOLxx/src/dknum.o',
              'ORTHPOLxx/src/dlancz.o',
              'ORTHPOLxx/src/dlob.o',
              'ORTHPOLxx/src/dmcdis.o',
              'ORTHPOLxx/src/dmcheb.o',
              'ORTHPOLxx/src/dqgp.o',
              'ORTHPOLxx/src/dradau.o',
              'ORTHPOLxx/src/drecur.o',
              'ORTHPOLxx/src/dsti.o',
              'ORTHPOLxx/src/gauss.o',
              'ORTHPOLxx/src/gchri.o',
              'ORTHPOLxx/src/i1mach.o',
              'ORTHPOLxx/src/kern.o',
              'ORTHPOLxx/src/knum.o',
              'ORTHPOLxx/src/lancz.o',
              'ORTHPOLxx/src/lob.o',
              'ORTHPOLxx/src/mccheb.o',
              'ORTHPOLxx/src/mcdis.o',
              'ORTHPOLxx/src/nu0her.o',
              'ORTHPOLxx/src/nu0jac.o',
              'ORTHPOLxx/src/nu0lag.o',
              'ORTHPOLxx/src/qgp.o',
              'ORTHPOLxx/src/r1mach.o',
              'ORTHPOLxx/src/radau.o',
              'ORTHPOLxx/src/recur.o',
              'ORTHPOLxx/src/sti.o',
              'ORTHPOLxx/src/ORTHPOLPP.o']
    
    ext_modules = [ Extension('orthpol', 
                              ['src/PyORTHPOL.cpp'],
                              include_dirs = oxx_inc,
                              extra_compile_args = ['-lgfortran', '-g', '-O0'],
                              extra_link_args = oxx_ld + ['-lgfortran', '-g', '-O0'])
                    ]
    
    setup(
        name='orthpol',
        version = "0.1.4",
        license = "COPYING.LESSER",
        description = "Python wrapper for the ORTHPOL package",
        url="http://www2.compute.dtu.dk/~dabi/index.php?slab=dtu-uq",
        author = "Daniele Bigoni",
        author_email = "dabi@dtu.dk",
        ext_modules = ext_modules,
        cmdclass={'install': orthpolxx_install})
        # configuration=configuration)

