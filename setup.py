#!/usr/bin/env python
import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

VERSION = '0.0.11'
PATH = os.path.dirname(os.path.abspath(__file__))
try:
    LONG_DESC = '\n===='+open(os.path.join(PATH, 'README.rst'), 'r').read().split('====', 1)[-1]
except IOError: #happens when using tox
    LONG_DESC = ''

setup(name='django-dockitcms',
      version=VERSION,
      description="CMS written using django-dockit",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='django CMS',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://github.com/webcube/django-dockitcms',
      license='New BSD License',
      packages=find_packages(exclude=['test_environment', 'tests']),
      test_suite='tests.setuptest.runtests',
      tests_require=(
        'pep8==1.3.1',
        'coverage',
        'django',
        'nose',
        'django-nose',
      ),
      include_package_data = True,
      )
