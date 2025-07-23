"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: run_cleo_1dkid_condevap_only.py
Project: scripts
Created Date: Monday 14th July 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Run 1-D kid test case for CLEO SDM with only condensation/evaporation enabled.

NOTE: script assumes CLEO's initial condition binary files already exist
(i.e. 'dimlessGBxboundaries.dat' and 'dimlessSDsinit.dat' files, whose
locations are given in CLEO's config file ('config_filename')
"""

import argparse
import numpy as np
import os
import sys
from pathlib import Path
from PyMPDATA_examples.Shipway_and_Hill_2012 import si

parser = argparse.ArgumentParser()
parser.add_argument(
    "--run_name",
    type=str,
    default="cleo_condevap_only",
    help="label for test run",
)
parser.add_argument(
    "--config_filename",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/cleo_1dkid/share/cleo_initial_conditions/1dkid/condevap_only/config.yaml",
    help="path to configuration yaml for test run",
)
parser.add_argument(
    "--binpath",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/bin/condevap_only",
    help="path to CLEO run output files",
)
parser.add_argument(
    "--figpath",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/bin/condevap_only",
    help="path to save figures in",
)
parser.add_argument(
    "--path2pycleo",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/pycleo",
    help="path to pycleo python module",
)
args = parser.parse_args()

os.environ["PYCLEO_DIR"] = str(args.path2pycleo)
sys.path.append("/home/m/m300950/superdrops-in-action/cleo_1dkid/")
from libs.test_case_1dkid.perform_1dkid_test_case import perform_1dkid_test_case
from libs.thermo.thermodynamics import Thermodynamics
from libs.cleo_sdm.microphysics_scheme_wrapper import MicrophysicsSchemeWrapper

### label for test case to name data/plots with
run_name = args.run_name
config_filename = args.config_filename
binpath = args.binpath
figpath = args.figpath

### path to directory to save data/plots in after model run
Path(figpath).mkdir(parents=False, exist_ok=True)

### time and grid parameters
# NOTE: these must be consistent with CLEO initial condition binary files(!)
z_delta = 25 * si.m  # (!) must be consistent with CLEO
z_max = 3200 * si.m  # (!) must be consistent with CLEO
timestep = 1.25 * si.s
time_end = 60 * si.minutes

### initial thermodynamic conditions
assert z_max % z_delta == 0, "z limit is not a multiple of the grid spacing."
ngbxs = int(z_max / z_delta)
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
out = perform_1dkid_test_case(
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
