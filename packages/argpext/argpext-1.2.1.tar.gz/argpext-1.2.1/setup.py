

from distutils.core import setup

setup(
    name='argpext'
    , version='1.2.1'
    , description = 'Argpext: hierarchical extension of sub-commands in argparse.'
    , author='Alexander Shirokov'
    , author_email='alexander.shirokov@gmail.com'
    , packages=['argpext']
    #, scripts = ['argpext.py']
    , py_modules=['argpext']
    , license='OSI Approved'
    , long_description="""Argpext is a module dedicated to improving the command line
interface with Python module internals.  It allows one to
quickly expose any selected Python functions to the command
line within DOS or Linux-like shells. Help messages are
automatically produced.

Argpext provides hierarchical extension to the
"Sub-commands" utility of the standard argparse
module. It allows one to group any Python functions into a
hierarchical tree-like structure, e.g.  according to their
logic. Every such function then corresponds to a certain
sequence of sub-commands, and can be executed directly from
the command line by simply passing the sequence as command
line arguments to the top level script. The rest of the
command line arguments to the script are used to set up the
values of function arguments, at which level the standard
argparse interface applies.

Argpext provides a special type to support command line
arguments that take predetermined set of values. Information
about available choices is automatically propagated into the usage help
message.

"""
    , classifiers = [
        'Development Status :: 4 - Beta'
        ,'Environment :: Console'
        ,'Intended Audience :: Developers'
        ,'Intended Audience :: Information Technology'
        ,'Intended Audience :: Science/Research'
        ,'Intended Audience :: End Users/Desktop'
        ,'Operating System :: MacOS :: MacOS X'
        ,'Operating System :: Microsoft :: Windows'
        ,'Operating System :: POSIX'
        ,'Programming Language :: Python :: 3'
        ,'Programming Language :: Python :: 2'

        ,'Topic :: Software Development :: User Interfaces'
        ,'Topic :: Software Development :: Interpreters'        
        ,'Topic :: Utilities'
    ]
)

