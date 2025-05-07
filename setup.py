#!/usr/bin/env python3

"""Python setup."""
import os
import re
from setuptools import setup, find_packages

def read(file_name):
    """Return the contents of a file as a string."""
    with open(os.path.join(os.path.dirname(__file__), file_name), 'r') as file:
        filestring = file.read()
    return filestring


def get_version():
    """Return the version of this module."""
    raw_init_file = read("pyproject.toml")
    rx_compiled = re.compile(r"\s*version\s*=\s*\"(\S+)\"")
    ver = rx_compiled.search(raw_init_file).group(1)
    return ver

setup(name="aya",
      version=get_version(),
      author="DullnessOutfield",
      description="Collection of utilities to assist with Kismet analysis",
      url="https://github.com/DullnessOutfield/aya",
      download_url="https://github.com/DullnessOutfield/aya",
      packages=find_packages(),
      install_requires=["kismet_rest", "requests >= 2.20"],
      setup_requires=["kismet_rest", "requests >= 2.20"],
      classifiers=['Development Status :: 3 - Alpha',
          "Intended Audience :: Developers",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "Topic :: Security",
      ],
    python_requires='>=3.9',  )