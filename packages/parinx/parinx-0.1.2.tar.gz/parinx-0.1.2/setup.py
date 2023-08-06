# -*- coding:utf-8 -*-
import os
import sys

from setuptools import setup, find_packages
from setuptools import Command
from setuptools.command.install import install
from subprocess import call
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin

TEST_PATHS = ['tests', ]

SUPPORTED_VERSIONS = ['2.5', '2.6', '2.7', 'PyPy', ]

if sys.version_info <= (2, 4):
    version = '.'.join([str(x) for x in sys.version_info[:3]])
    print('Version ' + version + ' is not supported. Supported versions are ' +
          ', '.join(SUPPORTED_VERSIONS))
    sys.exit(1)


class TestCommand(Command):
    description = "run test suite"
    user_options = []

    def initialize_options(self):
        THIS_DIR = os.path.abspath(os.path.split(__file__)[0])
        sys.path.insert(0, THIS_DIR)
        for test_path in TEST_PATHS:
            sys.path.insert(0, pjoin(THIS_DIR, test_path))
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        status = self._run_tests()
        sys.exit(status)

    def _run_tests(self):
        pre_python26 = (sys.version_info[0] == 2
                        and sys.version_info[1] < 6)
        if pre_python26:
            missing = []
            # test for dependencies
            try:
                import simplejson
                simplejson              # silence pyflakes
            except ImportError:
                missing.append("simplejson")

            try:
                import ssl
                ssl                     # silence pyflakes
            except ImportError:
                missing.append("ssl")

            if missing:
                print("Missing dependencies: " + ", ".join(missing))
                sys.exit(1)

        testfiles = []
        for test_path in TEST_PATHS:
            for t in glob(pjoin(self._dir, test_path, 'test_*.py')):
                testfiles.append('.'.join(
                    [test_path.replace('/', '.'), splitext(basename(t))[0]]))

        tests = TestLoader().loadTestsFromNames(testfiles)

        #        for test_module in DOC_TEST_MODULES:
        #            tests.addTests(doctest.DocTestSuite(test_module))

        t = TextTestRunner(verbosity=2)
        res = t.run(tests)
        return not res.wasSuccessful()


class Pep8Command(Command):
    description = "run pep8 script"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import pep8

            pep8
        except ImportError:
            print ('Missing "pep8" library. You can install it using pip: '
                   'pip install pep8')
            sys.exit(1)

        cwd = os.getcwd()
        retcode = call(('pep8 %s/parinx/ %s/tests/' %
                        (cwd, cwd)).split(' '))
        sys.exit(retcode)

setup(
    name='parinx',
    version='0.1.2',
    packages=find_packages(),
    package_dir={'parinx': 'parinx'},
    url='https://github.com/rahulrrixe/parinx',
    license='Apache License (2.0)',
    author='Rahul Ranjan',
    author_email='rahul.rrixe@gmail.com',
    description='Parinx implements a basic Sphinx docstring parser language   \
                 which providesa interface to extract the relavant parameter. \
                 You might find it most useful for tasks involving automated  \
                 data extraction from sphinx docs.',
    entry_points='''
            [console_scripts]
            ''',
    cmdclass={
        'pep8': Pep8Command,
        'test': TestCommand,
        'install': install,
    },
    keywords=['sphinx', 'docstring', 'parser'],
    tests_require=['unittest2']
)
