"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: thermodynamics.py
Project: thermo
Created Date: Wednesday 28th February 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Monday 11th November 2024
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
"""

import numpy as np
from copy import deepcopy


class Thermodynamics:
    """
    Class stores the thermodynamic variables required to run microphysics schemes in this project.

    Thermodynamic variables include pressure, temperature, moist air density and the specific
    content (mass mixing ratio) of vapour and condensates.

    Parameters:
      temp (np.ndarray):
        Temperature (K).
      rho (np.ndarray):
        Density of moist air (kg/m3).
      press (np.ndarray):
        Pressure (Pa).
      qvap (np.ndarray):
        Specific water vapor content (kg/kg).
      qcond (np.ndarray):
        Specific cloud water content (kg/kg).
      qice (np.ndarray):
        Specific cloud ice content (kg/kg).
      qrain (np.ndarray):
        Specific rain content (kg/kg).
      qsnow (np.ndarray):
        Specific snow content kg/kg).
      qgrau (np.ndarray):
        Specific graupel content (kg/kg).

    Attributes:
      temp (np.ndarray):
        Temperature (K).
      rho (np.ndarray):
        Density of moist air (kg/m3).
      press (np.ndarray):
        Pressure (Pa).
      massmix_ratios (dict):
        Specific content of vapour and condensates (see below).

      massmax_ratios consists of the following:
              massmix_ratios["qvap"] = qvap (np.ndarray): Specific water vapor content (kg/kg)\n
              massmix_ratios["qcond"] = qcond (np.ndarray): Specific cloud water content (kg/kg)\n
              massmix_ratios["qice"] = qice (np.ndarray): Specific cloud ice content (kg/kg)\n
              massmix_ratios["qrain"] = qrain (np.ndarray): Specific rain content (kg/kg)\n
              massmix_ratios["qsnow"] = qsnow (np.ndarray): Specific snow content kg/kg)\n
              massmix_ratios["qgrau"] = qgrau (np.ndarray): Specific graupel content (kg/kg).

    """

    def __init__(
        self,
        temp: np.ndarray,
        rho: np.ndarray,
        press: np.ndarray,
        qvap: np.ndarray,
        qcond: np.ndarray,
        qice: np.ndarray,
        qrain: np.ndarray,
        qsnow: np.ndarray,
        qgrau: np.ndarray,
        wvel: np.ndarray,
        uvel: np.ndarray,
        vvel: np.ndarray,
    ):
        """Initialize a thermodynamics object with the given variables

        Parameters:
            press (np.ndarray): Pressure (Pa).
            temp (np.ndarray): Temperature (K).
            rho (np.ndarray): Density of moist air (kg/m3)
            qvap (np.ndarray): Specific water vapor content (kg/kg)
            qcond (np.ndarray): Specific cloud water content (kg/kg)
            qice (np.ndarray): Specific cloud ice content (kg/kg)
            qrain (np.ndarray): Specific rain content (kg/kg)
            qsnow (np.ndarray): Specific snow content kg/kg)
            qgrau (np.ndarray): Specific graupel content (kg/kg)
            wvel (np.ndarray): vertical wind velocity, 'z', (m/s)
            uvel (np.ndarray): zonal wind velocity, 'x', (m/s)
            vvel (np.ndarray): meridional wind velocity, 'y', (m/s)
        """
        self.temp = deepcopy(temp)
        self.rho = deepcopy(rho)
        self.press = deepcopy(press)
        self.massmix_ratios = {
            "qvap": deepcopy(qvap),
            "qcond": deepcopy(qcond),
            "qice": deepcopy(qice),
            "qrain": deepcopy(qrain),
            "qsnow": deepcopy(qsnow),
            "qgrau": deepcopy(qgrau),
        }
        self.wvel = deepcopy(wvel)
        self.uvel = deepcopy(uvel)
        self.vvel = deepcopy(vvel)

    def print_state(self):
        print(self.temp)
        print(self.rho)
        print(self.press)
        print(self.massmix_ratios)

    def unpack_massmix_ratios(self):
        """returns list of references to massmix_ratio arrays"""
        return list(
            self.massmix_ratios.values()
        )  # qvap, qcond, qice, qrain, qsnow, qgrau

    def copy_massmix_ratios(self, qvap, qcond, qice, qrain, qsnow, qgrau):
        """copies values for each variable into respective array in massmix_ratios dictionary"""
        self.massmix_ratios["qvap"][:] = qvap
        self.massmix_ratios["qcond"][:] = qcond
        self.massmix_ratios["qice"][:] = qice
        self.massmix_ratios["qrain"][:] = qrain
        self.massmix_ratios["qsnow"][:] = qsnow
        self.massmix_ratios["qgrau"][:] = qgrau
