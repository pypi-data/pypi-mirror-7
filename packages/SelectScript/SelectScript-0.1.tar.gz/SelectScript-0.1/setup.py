import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "SelectScript",
    version = "0.1",
    author = "Andr"+unichr(233)+" Dietrich",
    author_email = "dietrich@ivs.cs.uni-magdeburg.de",
    description = ("Implementation of the query-language SelectScript for Python."),
    license = "BSD",
    keywords = "query, language",
    url = "https://pypi.python.org/pypi/SelectScript/0.1",
    packages=['SelectScript'],
    long_description=read('README'),
    install_requires=['antlr_python_runtime'],
    #dependency_links = [],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
