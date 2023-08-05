#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pybuilder',
          version = '0.10.20',
          description = '''An extensible, easy to use continuous build tool for Python''',
          long_description = '''PyBuilder is a continuous build tool for multiple languages.

PyBuilder primarily targets Python projects but due to its extensible
nature it can be used for other languages as well.

PyBuilder features a powerful yet easy to use plugin mechanism which
allows programmers to extend the tool in an unlimited way.
''',
          author = "Alexander Metzner, Maximilien Riehl, Michael Gruber, Udo Juettner",
          author_email = "alexander.metzner@gmail.com, max@riehl.io, aelgru@gmail.com, udo.juettner@gmail.com",
          license = 'Apache License',
          url = 'http://pybuilder.github.io',
          scripts = ['pyb'],
          packages = ['pybuilder', 'pybuilder.pluginhelper', 'pybuilder.plugins', 'pybuilder.plugins.python'],
          py_modules = [],
          classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: Implementation :: CPython', 'Programming Language :: Python :: Implementation :: PyPy', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Topic :: Software Development :: Build Tools', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
             #  data files
             # package data
          
          
          zip_safe=True
    )
