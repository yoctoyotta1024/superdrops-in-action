"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: setup.py
Project: superdrops-in-action
Created Date: Monday 14th July 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
"""

from setuptools import setup, find_packages

setup(
    name="superdrops-in-action",
    version="X.Y.Z",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "sphinx",
    ],
)
