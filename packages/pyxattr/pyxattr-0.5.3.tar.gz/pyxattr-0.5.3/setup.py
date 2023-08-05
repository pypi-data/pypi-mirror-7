#!/usr/bin/python

import distutils
try:
  from setuptools import setup, Extension
except ImportError:
  from distutils.core import setup, Extension

long_desc = """This is a C extension module for Python which
implements extended attributes manipulation. It is a wrapper on top
of the attr C library - see attr(5)."""
version = "0.5.3"
author = "Iustin Pop"
author_email = "iusty@k1024.org"
macros = [
    ("_XATTR_VERSION", '"%s"' % version),
    ("_XATTR_AUTHOR", '"%s"' % author),
    ("_XATTR_EMAIL", '"%s"' % author_email),
    ]
setup(name = "pyxattr",
      version = version,
      description = "Filesystem extended attributes for python",
      long_description = long_desc,
      author = author,
      author_email = author_email,
      url = "http://pyxattr.k1024.org/",
      download_url = "http://pyxattr.k1024.org/downloads/",
      license = "LGPL",
      ext_modules = [Extension("xattr", ["xattr.c"],
                               libraries=["attr"],
                               define_macros=macros,
                               extra_compile_args=["-Wall", "-Werror"],
                               )],
      test_suite = "test",
      platforms = ["Linux"],
      )
