#!/usr/bin/env python

from setuptools import setup, find_packages
from typing import List


def install_requires() -> List[str]:
    with open("./requirements.txt", "r") as f:
        return f.read().split("\n")


setup(name="line4py",
      version="1.0.0",
      license="MIT",
      description="LINE's library for Python",
      author="R4zL",
      url="https://github.com/7rs/line4py",
      install_requires=install_requires(),
      packages=find_packages(exclude=('example')))
