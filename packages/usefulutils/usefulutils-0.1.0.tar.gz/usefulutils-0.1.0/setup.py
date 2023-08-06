"""
Useful Utils
==============

"""

from setuptools import setup, find_packages

setup(
    name='usefulutils',
    version='0.1.0',
    author='Halfmoon Labs',
    author_email='hello@halfmoonlabs.com',
    description='Generally useful tools.',
    keywords='dict dictionary scrub to_dict todict json',
    url='https://github.com/onenameio/useful-utils',
    license='MIT',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False, 
)
