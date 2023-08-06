#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
        name='prompt_toolkit',
        author='Jonathan Slenders',
        version='0.2',
        license='LICENSE.txt',
        url='https://github.com/jonathanslenders/python-prompt-toolkit',

        description='',
        long_description='',
        packages=['prompt_toolkit'],
        install_requires = [ 'pygments', 'docopt', 'six' ],
        #install_requires = [  'wcwidth', ], # TODO: add wcwidth when released on pypi
        extra_requires=[
            # Required for the Python repl
            'jedi'
        ],
        scripts = [
            'bin/ptpython',
        ]
)
