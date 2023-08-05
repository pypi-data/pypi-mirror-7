#!/usr/bin/env python

from setuptools import setup, find_packages
import os

pkg_root = os.path.dirname(__file__)

# Error-handling here is to allow package to be built w/o README included
try: readme = open(os.path.join(pkg_root, 'README.txt')).read()
except IOError: readme = ''

setup(

	name = 'layered-yaml-attrdict-config',
	version = '14.05.0',
	author = 'Mike Kazantsev',
	author_email = 'mk.fraggod@gmail.com',
	license = 'WTFPL',
	keywords = 'yaml configuration conf serialization inheritance merge update',
	url = 'https://github.com/mk-fg/layered-yaml-attrdict-config',

	description = 'YAML-based configuration module',
	long_description = readme,

	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Software Development',
		'Topic :: Software Development :: Libraries :: Python Modules' ],

	install_requires = ['PyYAML'],
	packages = find_packages(),
	package_data = {'': ['README.txt']},
	exclude_package_data = {'': ['README.*']} )
