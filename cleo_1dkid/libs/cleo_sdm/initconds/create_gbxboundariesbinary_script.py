"""
----- CLEO -----
File: create_gbxboundariesbinary_script.py
Project: scripts
Created Date: Tuesday 24th October 2023
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Monday 17th June 2024
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
Copyright (c) 2023 MPI-M, Clara Bayley
-----
File Description:
uses cleopy module to create gridbox boundaries binary file for input to CLEO SDM
"""

import argparse
import numpy as np
from pathlib import Path
import yaml

### ----------------------- INPUT PARAMETERS ----------------------- ###
parser = argparse.ArgumentParser()
parser.add_argument(
    "--config_filename",
    type=Path,
    help="path to configuration yaml for test run",
)
parser.add_argument(
    "--isfigures",
    type=str,
    choices=["TRUE", "FALSE"],
    default="FALSE",
    help="=='TRUE', plot and save figures of initial conditions",
)
parser.add_argument(
    "--figpath",
    type=Path,
    help="path to save figures in",
)
parser.add_argument(
    "--figlabel",
    type=str,
    default="",
    help="label for saving figures with",
)
args = parser.parse_args()

if args.isfigures == "TRUE":
    isfigures = [True, True]
else:
    isfigures = [False, False]

from cleopy import geninitconds

### essential paths and filenames
config_filename = args.config_filename
figpath = args.figpath
cnfg = yaml.safe_load(open(config_filename))
constants_filename = cnfg["inputfiles"]["constants_filename"]
grid_filename = cnfg["inputfiles"]["grid_filename"]
assert config_filename.exists()
assert Path(constants_filename).exists()
assert Path(grid_filename).parent.is_dir()
if isfigures[1]:
    figpath.is_dir()

### input parameters for zcoords of gridbox boundaries
zmin = -25  # minimum z coord [m]
zmax = 3200  # maximum z coord [m]
zdelta = 25  # even spacing
zgrid = [zmin, zmax, zdelta]
# zgrid = np.arange(zmin, zmax+zdelta, zdelta)

### input parameters for x coords of gridbox boundaries
xgrid = np.asarray([0, 1])

### input parameters for y coords of gridbox boundaries
ygrid = np.asarray([0, 1])
### ---------------------------------------------------------------- ###


### -------------------- BINARY FILE GENERATION--------------------- ###
geninitconds.generate_gridbox_boundaries(
    grid_filename,
    zgrid,
    xgrid,
    ygrid,
    constants_filename,
    isprintinfo=isfigures[0],
    isfigures=isfigures,
    savefigpath=figpath,
    savelabel=args.figlabel,
)
### ---------------------------------------------------------------- ###
