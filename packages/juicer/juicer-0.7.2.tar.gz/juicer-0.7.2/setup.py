import os
import sys

from distutils.core import setup

setup(name='juicer',
      version='0.7.2',
      description='Administer Pulp and Release Carts',
      maintainer='Tim Bielawa',
      maintainer_email='tbielawa@redhat.com',
      url='https://github.com/juicer/juicer',
      license='GPLv3+',
      package_dir={ 'juicer': 'juicer' },
      packages=[
         'juicer',
         'juicer.juicer',
         'juicer.admin',
         'juicer.common',
         'juicer.utils',
      ],
      scripts=[
         'bin/juicer',
         'bin/juicer-admin'
      ]
)
