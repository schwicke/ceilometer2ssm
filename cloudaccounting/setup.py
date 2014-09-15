import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ceilossm",
    version = "0.0.1",
    author = "Sajeesh Cimson Sasi, Nirbhay Chandorkar, Ulrich Schwickerath",
    description = ("Tools for WLCG cloud accounting "),
    license = "ASL2",
    keywords = "ceilometer2ssm",
    url = "https://github.com/schwicke/ceilometer2ssm",
    packages=['cloudaccounting','caapi','caapi/app','caapi/app/scripts'],
    scripts=['ceilometer2ssm','ceilodatastore','ceilodatapoll','ceilodata2ssm','ceilodata2acct','standalone/cloudaccounting'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: Apache2 License",
    ],
)
