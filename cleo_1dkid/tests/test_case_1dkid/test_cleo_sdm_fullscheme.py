"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: test_cleo_sdm.py
Project: test_case_1dkid
Created Date: Friday 27th June 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Tuesday 1st July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
1-D kid test case for CLEO SDM with full scheme, i.e. with condensation/evaporation,
collision-coalescence and precipitation enabled
"""

import pytest
import numpy as np
from pathlib import Path
from PyMPDATA_examples.Shipway_and_Hill_2012 import si


@pytest.fixture(scope="module")
def figpath(pytestconfig):
    return pytestconfig.getoption("figpath")


@pytest.fixture(scope="module")
def path2cleopythonbindings(pytestconfig):
    return pytestconfig.getoption("cleo_path2cleopythonbindings")


@pytest.fixture(scope="module")
def config_filename(pytestconfig):
    return pytestconfig.getoption("cleo_test_1dkid_fullscheme_config_filename")


def test_cleo_sdm_1dkid_fullscheme(figpath, path2cleopythonbindings, config_filename):
    """runs test of 1-D KiD rainshaft model using CLEO SDM for the
    microphysics scheme with full warm-rain microphysics enabled: condensation/evaporation,
    collision-coalescence and precipitation (i.e. condensates have terminal velocity).

     NOTE: test assumes CLEO's initial condition binary files already exist
    (i.e. 'dimlessGBxboundaries.dat' and 'dimlessSDsinit.dat' files, whose
    locations are given in CLEO's config file ('config_filename')

    This function sets up initial conditions and parameters for running a 1-D KiD rainshaft
    test case using the CLEO SDM microphysics scheme (via a wrapper).
    It then runs the test case as specified.
    """
    import os

    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    from libs.test_case_1dkid.perform_1dkid_test_case import perform_1dkid_test_case
    from libs.thermo.thermodynamics import Thermodynamics
    from libs.cleo_sdm.microphysics_scheme_wrapper import MicrophysicsSchemeWrapper

    ### label for test case to name data/plots with
    run_name = "cleo_sdm_1dkid_fullscheme"

    ### path to directory to save data/plots in after model run
    Path(figpath).mkdir(parents=False, exist_ok=True)

    ### time and grid parameters
    # NOTE: these must be consistent with CLEO initial condition binary files(!)
    z_min = -25 * si.m  # (!) must be consistent with CLEO
    z_max = 3200 * si.m  # (!) must be consistent with CLEO
    z_delta = 25 * si.m  # (!) must be consistent with CLEO
    timestep = 1.25 * si.s
    time_end = 15 * si.minutes

    ### initial thermodynamic conditions
    assert (
        z_max - z_min
    ) % z_delta == 0, "z limit is not a multiple of the grid spacing."
    ngbxs = int((z_max - z_min) / z_delta)
    zeros = np.zeros(ngbxs)
    zeros2 = np.tile(zeros, 2)
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
        zeros2,
        zeros2,
        zeros2,
    )

    ### microphysics scheme to use (within a wrapper)
    is_motion = True
    microphys_scheme = MicrophysicsSchemeWrapper(
        config_filename,
        is_motion,
        0.0,
        timestep,
        thermo_init.press,
        thermo_init.temp,
        thermo_init.massmix_ratios["qvap"],
        thermo_init.massmix_ratios["qcond"],
        thermo_init.wvel,
        thermo_init.uvel,
        thermo_init.vvel,
    )

    ### Perform test of 1-D KiD rainshaft model using chosen setup
    advect_hydrometeors = False
    perform_1dkid_test_case(
        z_min,
        z_delta,
        z_max,
        time_end,
        timestep,
        thermo_init,
        microphys_scheme,
        advect_hydrometeors,
        figpath,
        run_name,
    )
