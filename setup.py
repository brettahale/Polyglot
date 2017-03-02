""" Controls how Polyglot should be built by Python """

from setuptools import setup, find_packages
from Cython.Build import cythonize
import polyglot.version

PACKAGES = ['polyglot', 'polyglot.element_manager',
            'polyglot.element_manager.http', 'polyglot.element_manager.isy']

# run setup
setup(
    name="Polyglot",
    version=polyglot.version.PGVERSION,
    author="Universal Devices Inc",
    author_email="support@universal-devices.com",
    description="Polyglot for ISY994i",
    url="http://ud-polyglot.readthedocs.io/",
    include_package_data=True,
    platforms="any",
    #ext_modules=cythonize('polyglot/*.pyx'),
    packages=PACKAGES
)
