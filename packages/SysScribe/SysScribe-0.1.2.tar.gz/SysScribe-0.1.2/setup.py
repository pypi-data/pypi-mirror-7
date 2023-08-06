from setuptools import setup, find_packages
import os
import re

version = re.compile(r'VERSION\s*=\s*\((.*?)\)')

def get_package_version():
    "returns package version without importing it"
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "sysscribe/__init__.py")) as initf:
        for line in initf:
            m = version.match(line.strip())
            if not m:
                continue
            return ".".join(m.groups()[0].split(", "))

classes = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: BSD License
    Topic :: System :: Logging
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.2
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: POSIX :: Linux
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


setup(
    name='SysScribe',
    version=get_package_version(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    author='Zenotech',
    author_email='admin@zenotech.com',
    license='BSD',
    url='https://github.com/zenotech/SysScribe',
    classifiers=classifiers,
    description='Records system setup as a python dictionary',
    long_description=open('README.md').read(),
    include_package_data=True,
    package_data = {
        '': ['*.md',]
    },
)