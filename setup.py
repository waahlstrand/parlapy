# -*- coding: UTF-8 -*
from setuptools import setup

setup(name='parlapy',
      version='0.1',
      description='A Python wrapper for the public API of the Swedish Parliament data',
      url='http://github.com/waahlstrand/parlapy',
      author='Victor Wåhlstrand Skärström',
      license='MIT',
      packages=['parlapy'],
      zip_safe=False,
      install_requires=['requests',
                        'tqdm'])