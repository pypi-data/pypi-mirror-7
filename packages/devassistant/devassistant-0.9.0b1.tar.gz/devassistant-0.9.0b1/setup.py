#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import subprocess

import devassistant

try:
    from setuptools import setup, Command
except:
    from distutils.core import setup, Command

class PyTest(Command):
    user_options = [('test-runner=',
                     't',
                     'test runner to use; by default, multiple py.test runners are tried')]
    command_consumes_arguments = True

    def initialize_options(self):
        self.test_runner = None
        self.args = []

    def finalize_options(self):
        pass

    def runner_exists(self, runner):
        syspaths = os.getenv('PATH').split(os.pathsep)
        for p in syspaths:
            if os.path.exists(os.path.join(p, runner)):
                return True

        return False

    def run(self):
        # only one test runner => just run the tests
        runners = ['py.test-2.7', 'py.test-3.3']
        if self.test_runner:
            runners = [self.test_runner]

        have_runner = False
        for runner in runners:
            if self.runner_exists(runner):
                have_runner = True

        if not have_runner:
            if self.runner_exists('py.test'):
                runners = ['py.test']
            else:
                print('No py.test runners found, can\'t run tests.')
                print('Tried: {0}.'.format(', '.join(runners + ['py.test'])))
                raise SystemExit(100)

        for runner in runners:
            if len(runners) > 1:
                print('\n' * 2)
            print('Running tests using "{0}":'.format(runner))

            retcode = 0
            cmd = [runner]
            for a in self.args:
                cmd.append(a)
            cmd.append('test')
            t = subprocess.Popen(cmd)
            rc = t.wait()
            retcode = t.returncode or retcode

        raise SystemExit(retcode)


description = ''.join(open('README.rst').readlines())

setup(
    name = 'devassistant',
    version = devassistant.__version__,
    description = 'DevAssistant helps you kickstart your projects with ease.',
    long_description = description,
    keywords = 'develop,kickstart,easy,quick',
    author = 'Bohuslav "Slavek" Kabrda',
    author_email = 'bkabrda@redhat.com',
    url = 'https://github.com/bkabrda/devassistant',
    license = 'GPLv2+',
    packages = ['devassistant', 'devassistant.cli', 'devassistant.gui'],
    include_package_data = True,
    entry_points = {'console_scripts':['da=devassistant.cli.cli_runner:CliRunner.run',
                                       'da-gui=devassistant.gui:run_gui',
                                       'devassistant=devassistant.cli.cli_runner:CliRunner.run',
                                       'devassistant-gui=devassistant.gui:run_gui']},
    # PyGithub is in fact optional, but let's keep it here
    install_requires=['PyYaml', 'PyGithub>=1.14.2', 'jinja2', 'progress', 'six'],
    setup_requires = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                  ],
    cmdclass = {'test': PyTest}
)
