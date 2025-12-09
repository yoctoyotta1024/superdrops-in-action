"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: initial_pressure_profile.py
Project: initconds
Created Date: Tuesday 18th November 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Method to get dictionary of {gbxindex: pressure} to set initial pressure profile when superdroplet
xi (number concentration) initialisation requires it (see create_initsuperdropsbinary_script.py)
"""

import sys
import numpy as np
from pathlib import Path
from cleopy.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from PyMPDATA_examples.Shipway_and_Hill_2012 import si

sys.path.append(
    str(Path(__file__).parent.parent.parent)
)  # superdrops-in-action/cleo_1dkid/libs/
from test_case_1dkid.settings import Settings


def get_initial_pressure_profile(
    grid_filename,
    is_exner_novapour,
    is_exner_novapour_uniformrho,
    p_surf,
    z_min,
    z_max,
    z_delta,
):
    ### (!) dummy settings to get presure profile, must match settings in KiDDynamics (!)
    settings = Settings(
        dt=0.0,
        dz=z_delta * si.m,
        wmax_const=0.0,
        tscale_const=0.0,
        t_max=0.0,
        z_min=z_min * si.m,
        z_max=z_max * si.m,
        p_surf=p_surf * si.hPa,
        is_exner_novapour=is_exner_novapour,
        is_exner_novapour_uniformrho=is_exner_novapour_uniformrho,
        is_approx_drhod_dz=False,
    )
    zfull = np.arange(z_min + z_delta / 2, z_max + z_delta / 2, z_delta)
    press_prof = settings.press(zfull)

    gbxbounds = rgrid.read_dimless_gbxboundaries_binary(grid_filename, isprint=False)

    assert len(press_prof) == len(
        gbxbounds.keys()
    ), "number of gbxindexes and number of pressure values are not equal"

    return dict(zip(gbxbounds.keys(), press_prof)), press_prof[0]
