"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: arakawa_c.py
Project: test_case_1dkid
Created Date: Wednesday 2nd July 2025
Author: PyMPATA Authors (PyMPDATA)
Additional Contributors: Clara Bayley (CB)
-----
Last Modified: Wednesday 2nd July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
File is adaptation from PyMPDATA Shipway and Hill 2012 example, copied from:
https://github.com/open-atmos/PyMPDATA/blob/main/examples/PyMPDATA_examples/Shipway_and_Hill_2012/arakawa_c.py
between v1.6.1 and v1.6.2
"""

import numpy as np


class arakawa_c:
    @staticmethod
    def z_scalar_coord(grid):
        zZ = np.linspace(1 / 2, grid[0] - 1 / 2, grid[0])
        return zZ

    @staticmethod
    def z_vector_coord(grid):
        zZ = np.linspace(0, grid[0], grid[0] + 1)
        return zZ
