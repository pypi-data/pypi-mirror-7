from setuptools import setup

import imp
_version = imp.load_source("structpack._version", "structpack/_version.py")

setup(
    name        = 'structpack',
    version     = _version.__version__,
    url         = 'https://github.com/Knio/structpack',
    author      = 'Tom Flanagan',
    author_email= 'tom@zkpq.ca',
    description = '''A Python library for serializing and deserializing object trees to JSON-compatable values (dicts, lists, strings, ints, floats, bools).''',
    long_description = open('README.md').read(),
    license = 'MIT',
    packages=['structpack'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
