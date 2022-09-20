"""Setup file"""
from setuptools import setup, find_packages
from distutils.util import convert_path
import os

main_ns = {}
ver_path = convert_path('ecrops/ecrops_version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='ecrops',
      version=main_ns['__version__'],
      description='Engine for Crop Parallelizable Simulations',
      url='',
      author='Davide Fumagalli, Marian Bratu - JRC',
      author_email='',
      long_description=read('Readme.md'),
      license='EUPL',
      use_2to3=False,
      packages=find_packages(),
      install_requires=['numpy>=1.6.0'],
      zip_safe=False,
      package_data={
          # If any package contains *.txt or *.rst files, include them:
          "": ["*.html"]
      }
      )
