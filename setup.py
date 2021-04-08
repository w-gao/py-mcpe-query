"""
Copyright (c) 2017-2021 w-gao
"""

from setuptools import setup

setup(name='py_mcpe_query',
      version='0.2.1',
      description='Query a Minecraft: bedrock edition server easily',
      long_description='a Python software that uses the query protocol to ping a Minecraft: Bedrock edition server '
                       'for basic information',
      url='https://github.com/w-gao/py-mcpe-query',
      author='w-gao',
      author_email='dev@wlgao.com',
      license='MIT',
      packages=['mcpe_query'],
      python_requires=">=3.6",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'
      ],
      keywords='mcpe minecraft mcpeserver')
