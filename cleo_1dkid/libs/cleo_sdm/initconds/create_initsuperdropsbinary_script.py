"""
----- CLEO -----
File: create_initsuperdropsbinary_script.py
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
uses cleopy module to create binary file for initial superdroplet conditions to read into CLEO SDM
"""

import argparse
from pathlib import Path
import yaml

import alphasampling
from PySDM.initialisation import spectra

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
    default="False",
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
    gbxs2plt = [0]  # indexes of GBx index of SDs to plot (nb. "all" can be very slow)
else:
    isfigures = [False, False]
    gbxs2plt = None

from cleopy import geninitconds
from cleopy.initsuperdropsbinary_src import dryrgens, attrsgen, crdgens

### essential paths and filenames
config_filename = args.config_filename
figpath = args.figpath
cnfg = yaml.safe_load(open(config_filename))
constants_filename = cnfg["inputfiles"]["constants_filename"]
grid_filename = cnfg["inputfiles"]["grid_filename"]
initsupers_filename = cnfg["initsupers"]["initsupers_filename"]
assert Path(config_filename).exists()
assert Path(constants_filename).exists()
assert Path(grid_filename).parent.is_dir()
if isfigures[1]:
    figpath.is_dir()
### ------------------------------------------- ###

### --- Choice of Droplet Radius Probability Distribution and Radii Generator --- ###
geomean = 0.04e-6
geosig = 1.4
numconc = 50 * 1e6
spectrum = spectra.Lognormal(norm_factor=1.0, m_mode=geomean, s_geom=geosig)

### --- Choice of Superdroplet  --- ###
nsupers = 256  # Number of Superdroplets per Gridbox
alpha = 0.0  # sampling param: 0 -> const xi, 1 -> xi follows spectrum
default_cdf_range = (0.00001, 0.99999)
rspan = spectrum.percentiles(
    default_cdf_range
)  # min and max range of radii to sample [m]
radiigen, xiprobdist = alphasampling.AlphaSamplingWrapper(spectrum, alpha, rspan)
numconc_tolerance = (
    0.001  # 0.1% tolerance on resultant numconc not being equal to input numconc
)
### --------------------------------------------------------- ###

### --- Choice of Superdroplet Dry Radii Generator --- ###
dryr_sf = 1.0  # scale factor for dry radii [m]
dryradiigen = dryrgens.ScaledRadiiGen(dryr_sf)  # dryradii are 1/sf of radii [m]
### ---------------------------------------------- ###

### --- Choice of Superdroplet Coords Generator --- ###
coord3gen = crdgens.SampleCoordGen(True)  # sample coord3 range randomly or not
coord1gen = None  # do not generate superdroplet coord1s
coord2gen = None  # do not generate superdroplet coord2s
### ----------------------------------------------- ###

### -------------------- BINARY FILE GENERATION--------------------- ###
initattrsgen = attrsgen.AttrsGenerator(
    radiigen, dryradiigen, xiprobdist, coord3gen, coord1gen, coord2gen
)
geninitconds.generate_initial_superdroplet_conditions(
    initattrsgen,
    initsupers_filename,
    config_filename,
    constants_filename,
    grid_filename,
    nsupers,
    numconc,
    numconc_tolerance=numconc_tolerance,
    isprintinfo=isfigures[0],
    isfigures=isfigures,
    savefigpath=figpath,
    gbxs2plt=gbxs2plt,
    savelabel=args.figlabel,
)
### ---------------------------------------------------------------- ###
