#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(  name='auxdata',
        version='0.0.2',
        description='Module for loading and processing of auxdata (peripheral signals, triggers, videos from triggered cameras), using VIs from the Bonhoeffer-lab',
        url='https://github.com/pgoltstein/auxdata',
        author='Pieter Goltstein',
        author_email='xpieter@mac.com',
        license='GNU GENERAL PUBLIC LICENSE Version 3',
        packages=['auxrecorder','videorecorder'],
        install_requires=['numpy','tqdm'],
        zip_safe=False
        )
