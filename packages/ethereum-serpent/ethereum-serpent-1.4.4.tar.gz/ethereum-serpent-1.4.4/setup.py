#!/usr/bin/env python

import os
from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build
from subprocess import call


class build_me(build):
    def run(self):
        build.run(self)
        # if os.uname()[0] == 'Linux' and os.geteuid() == 0:
        #     call(['sudo', 'apt-get', 'install', 'cmake'])
        #     call(['sudo', 'apt-get', 'install', 'libboost-dev'])
        call(['mkdir', 'build'])
        os.chdir('build')
        call(['cmake', '..', '-DLANGUAGES=1'])
        call(['make'])
        os.chdir('..')


class install_me(install):
    def run(self):
        install.run(self)
        os.chdir('build')
        call(['make', 'install'])
        os.chdir('..')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='ethereum-serpent',
    version='1.4.4',
    description='Serpent compiler',
    maintainer='Vitalik Buterin',
    maintainer_email='v@buterin.com',
    license='WTFPL',
    url='http://www.ethereum.org/',
    long_description=read('README.md'),
    cmdclass={
        'build': build_me,
        'install': install_me,
    }
)
