# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="pysimpledmx",
    version=open("VERSION").read(),
    description="simple dmx control for the Enttec DMX USB Pro",
    license="GPLV3",
    author="c0z3n, sabjorn",
    url="https://github.com/c0z3n/pySimpleDMX, https://github.com/limbicmedia/pySimpleDMX",
    packages=find_packages(),
    install_requires=[
        "pyserial"
    ],
    long_description=open("README.md").read(),
    classifiers=[
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        "Intended Audience :: Other Audience",
        "Topic :: Artistic Software",
    ]
)
