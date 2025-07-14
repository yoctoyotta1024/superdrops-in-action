"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: test_bulkkid.py
Project: test_case_1dkid
Created Date: Monday 2nd September 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Wednesday 4th June 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
"""

import pytest
import numpy as np
from pathlib import Path
from PyMPDATA_examples.Shipway_and_Hill_2012 import si

from libs.test_case_1dkid.perform_1dkid_test_case import perform_1dkid_test_case
from libs.thermo.thermodynamics import Thermodynamics
from libs.pympdata_bulk.bulk_scheme_condensation import (
    MicrophysicsSchemeWrapper,
)


@pytest.fixture(scope="module")
def binpath(pytestconfig):
    return pytestconfig.getoption("binpath")


def test_pympdata_bulk_scheme_1dkid(binpath):
    """runs test of 1-D KiD rainshaft model using bulk scheme for condensation
    extracted from pyMPDATA for the microphysics scheme.

    This function sets up initial conditions and parameters for running a 1-D KiD rainshaft
    test case using the bulk microphysics scheme for condensation from the Shipway and Hill 2012
    pyMPDATA-examples example (via a wrapper). It then runs the test case as specified.
    """
    ### label for test case to name data/plots with
    run_name = "pympdata_bulkmicrophys_1dkid"

    ### path to directory to save data/plots in after model run
    Path(binpath).mkdir(parents=False, exist_ok=True)

    ### time and grid parameters
    z_delta = 25 * si.m
    z_max = 3200 * si.m
    timestep = 1.25 * si.s
    time_end = 15 * si.minutes

    ### initial thermodynamic conditions
    assert z_max % z_delta == 0, "z limit is not a multiple of the grid spacing."
    zeros = np.zeros(int(z_max / z_delta))
    null = np.array([])  # this microphysics test doesn't need winds
    thermo_init = Thermodynamics(
        zeros,
        zeros,
        zeros,
        zeros,
        zeros,
        zeros,
        zeros,
        zeros,
        zeros,
        null,
        null,
        null,
    )

    ### microphysics scheme to use (within a wrapper)
    microphys_scheme = MicrophysicsSchemeWrapper()

    ### Perform test of 1-D KiD rainshaft model using chosen setup
    advect_hydrometeors = True
    perform_1dkid_test_case(
        z_delta,
        z_max,
        time_end,
        timestep,
        thermo_init,
        microphys_scheme,
        advect_hydrometeors,
        binpath,
        run_name,
    )
