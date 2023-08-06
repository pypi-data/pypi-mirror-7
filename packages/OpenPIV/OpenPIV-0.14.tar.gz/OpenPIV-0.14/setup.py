from distutils.core import setup, Extension
from Cython.Distutils import build_ext

import glob
import numpy

# Build extensions 
module1 = Extension(    name         = "openpiv.process",
                        sources      = ["openpiv/src/process.pyx"],
                        include_dirs = [numpy.get_include()],
                    )
                    
module2 = Extension(    name         = "openpiv.lib",
                        sources      = ["openpiv/src/lib.pyx"],
                        include_dirs = [numpy.get_include()],
                    )

# a list of the extension modules that we want to distribute
ext_modules = [module1, module2]


# Package data are those filed 'strictly' needed by the program
# to function correctly.  Images, default configuration files, et cetera.
package_data =  [ 'data/defaults-processing-parameters.cfg', 
                  'data/ui_resources.qrc',
                  'data/images/*.png',
                  'data/icons/*.png',
                ]


# data files are other files which are not required by the program but 
# we want to ditribute as well, for example documentation.
data_files = [ ('openpiv/tutorial/', glob.glob('openpiv/tutorial/*') ),
               ('openpiv/tutorial-part1/', glob.glob('openpiv/tutorial-part1/*') ),
               ('openpiv/masking_tutorial/', glob.glob('openpiv/masking_tutorial/*') ),
               ('openpiv/docs/openpiv/examples/example1', glob.glob('openpiv/docs/examples/example1/*') ),
               ('openpiv/docs/openpiv/examples/gurney-flap', glob.glob('openpiv/docs/examples/gurney-flap/*') ),
               ('openpiv/docs/openpiv', ['README.rst'] ),
               ('openpiv/data/ui', glob.glob('openpiv/data/ui/*.ui') ),
             ]


# packages that we want to distribute. THis is how
# we have divided the openpiv package.
packages = ['openpiv', 'openpiv.ui']


# script are executable files that will be run to load the gui or something else.
scripts = ['tutorial/tutorial-part1.py', 'masking_tutorial/masking_tutorial.py']



setup(  name = "OpenPIV",
        version = "0.14",
        author = "The OpenPIV contributors",
        author_email = "openpiv@openpiv.net",
        description = "A software for PIV data analysis",
        license = "GPL v3",
        url = "www.openpiv.net",
        long_description =  """OpenPIV is an initiative of scientists to
                            develop a software, algorithms and methods
                            for the state-of-the-art experimental tool
                            of Particle Image Velocimetry (PIV) which 
                            are free, open source, and easy to operate.""",
                            
        ext_modules = ext_modules, 
        packages = packages,
        cmdclass = {'build_ext': build_ext},
        scripts = scripts,
        package_data = {'': package_data},
        data_files = data_files
        )

