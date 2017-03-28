#!/usr/bin/env python
import sys
from distutils.core import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='evesde',
    version='0.1',
    description='Simple EVE Static Data Export SQLite database wrapper',
    author='Sairon Istyar',
    author_email='saironiq@gmail.com',
    url='https://github.com/saironiq/evesde',
    requires=['json', 'sqlite3'],
    license='GPLv2',
    keywords=('eve-online', 'sde'),
    platforms='any',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
        'Intended Audience :: Developers',
    ),
    zip_safe=True,
    py_modules=['evesde',],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
