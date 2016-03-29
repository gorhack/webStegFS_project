#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='covertFS',
    version='0.9.3b',
    entry_points={'console_scripts': ['covertFS = covertFS.__main__:main']},
    description='It\'s covert and stuff',
    long_description=readme,
    author='Kyle Gorak, David Hart, Adam Sjoholm, and Ryne Flores',
    author_email='kyle.gorak@usma.edu',
    url='https://github.com/gorhack/covertFS',
    license='USMA',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: File System',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
    ],
    keywords='covert file system steganography',
    packages=find_packages(exclude=['docs', 'dist', 'design', 'paper', 'covertFS.egg-info', '__pycache__', '.idea']),
    package_data={
        'README': ['README.rst'],
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "fs",
        "lxml",
        "Pillow",
        "fusepy",
    ]
)
