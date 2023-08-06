from setuptools import setup, find_packages
from os import path

import responsys

project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.md')) as f:
    long_description = f.read()

install_requires = (
    'suds-jurko'
)
tests_require = (
    'coverage',
    'mock',
    'nose',
    'pinocchio',
)

setup(
    name=responsys.__name__,
    keywords=responsys.__keywords__,
    version=responsys.__version__,
    author='Jared Lang',
    author_email='kaptainlange@gmail.com',
    description='Python client library for the Responsys Interact API',
    long_description=long_description,
    packages=find_packages(),
    license='LICENSE',
    install_requires=install_requires,
    setup_requires=tests_require,
    tests_require=tests_require,
    test_suite='nose.collector',
)
