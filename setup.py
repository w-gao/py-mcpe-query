"""Query an mcpe server easily

setup.py

Copyright (c) 2017 w-gao
"""

from setuptools import setup

setup(name='py_mcpe_query',
      version='0.1',
      description='Query an mcpe server easily',
      long_description='a Python software that uses the query protocol to ping an mcpe server for basic information',
      url='https://github.com/w-gao/py-mcpe-query',
      author='w-gao',
      author_email='w-gao@users.noreply.github.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'
      ],
      keywords='mcpe minecraft mcpeserver',
      packages=['py_mcpe_query']
      )
