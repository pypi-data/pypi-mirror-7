#!/usr/bin/env python
from setuptools import setup

long_description = open('README.rst').read()

# very convoluted way of reading version from the module without importing it
version = (
    [l for l in open('flask_injector.py') if '__version__' in l][0]
    .split('=')[-1]
    .strip().strip('\'')
)

if __name__ == '__main__':
    setup(
        name='Flask-Injector',
        version=version,
        url='https://github.com/alecthomas/flask_injector',
        license='BSD',
        author='Alec Thomas',
        author_email='alec@swapoff.org',
        description=
            'Adds Injector, a Dependency Injection framework, support to Flask.',
        long_description=long_description,
        py_modules=['flask_injector'],
        zip_safe=True,
        platforms='any',
        install_requires=['Flask', 'injector>=0.7.4'],
        keywords=['Dependency Injection', 'Flask'],
    )
