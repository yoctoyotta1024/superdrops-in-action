"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: bulk_scheme_condensation.py
Project: pympdata_bulk
Created Date: Monday 2nd September 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Wednesday 4th September 2024
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Simple bulk microphysics scheme extracted from pyMPDATA
Shipway and Hill 2012 example for 1-D KiD rainshaft model
"""

import numpy as np
from ..thermo.thermodynamics import Thermodynamics
from PyMPDATA_examples import Shipway_and_Hill_2012 as kid

from copy import deepcopy


def bulk_scheme_condensation(temp, press, qvap, qcond):
    """
    Enacts saturation adjustment on qvap and qcond for a very simple bulk
    scheme to ensure relative humidity <= 100%. Extracted from pyMPDATA
    Bulk (nr=1) Microphysics Scheme for condensation in
    Shipway and Hill 2012 example for a 1-D KiD rainshaft model.

    See https://github.com/open-atmos/PyMPDATA/tree/main/examples/PyMPDATA_examples/Shipway_and_Hill_2012)
    for the original source code.

    Parameters:
    temp (float): Temperature in Kelvin.
    press (float): Pressure in Pascals.
    qvap (float): Specific humidity of water vapor (kg/kg).
    qcond (float): Specific humidity of condensed water (kg/kg).

    Returns:
    tuple: Adjusted specific humidities of water vapor and condensed water (qvap, qcond).
    """
    pvs = kid.formulae.pvs_Celsius(temp - kid.const.T0)
    relh = kid.formulae.pv(press, qvap) / pvs

    dqcond = np.maximum(0, qvap * (1 - 1 / relh))

    qvap -= dqcond
    qcond += dqcond

    return qvap, qcond


class MicrophysicsSchemeWrapper:
    def __init__(self):
        """Initialize the WrappedKiDBulkMicrophysics object."""
        self.microphys = "pyMPDATA KiD Bulk Microphysics Scheme for Condensation"
        self.name = "Wrapper around " + self.microphys

    def initialize(self) -> int:
        """Initialise the microphysics scheme.

        This method calls the microphysics initialisation

        Returns:
            int: 0 upon successful initialisation
        """
        return 0

    def finalize(self) -> int:
        """Finalise the microphysics scheme.

        This method calls the microphysics finalisation.

        Returns:
            int: 0 upon successful finalisation.
        """
        return 0

    def run(self, timestep: float, thermo: Thermodynamics) -> Thermodynamics:
        """Run the microphysics computations.

        This method is a wrapper of the MicrophysicsScheme object's run function to call the
        microphysics computations in a way that's compatible with the test and scripts in this project.

        Args:
            timestep (float): Time-step for integration of microphysics (s).
            thermo (Thermodynamics): Thermodynamic properties.

        Returns:
            Thermodynamics: Updated thermodynamic properties after microphysics computations.
        """

        cp_thermo = deepcopy(thermo)
        temp = cp_thermo.temp
        press = cp_thermo.press
        qvap = cp_thermo.massmix_ratios["qvap"]
        qcond = cp_thermo.massmix_ratios["qcond"]

        qvap, qcond = bulk_scheme_condensation(temp, press, qvap, qcond)

        cp_thermo.massmix_ratios["qvap"][:] = qvap
        cp_thermo.massmix_ratios["qcond"][:] = qcond

        return cp_thermo
