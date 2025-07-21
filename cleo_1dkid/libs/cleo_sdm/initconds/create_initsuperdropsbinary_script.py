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
uses pySD module to create binary file
for  initial superdroplet conditions
to read into CLEO SDM
"""

import sys
from pathlib import Path

import alphasampling
from PySDM.initialisation import spectra

sys.path.append(sys.argv[1])  # path to pySD (same as to CLEO)
from pySD import geninitconds
from pySD.initsuperdropsbinary_src import dryrgens, attrsgen, crdgens

### ----------------------- INPUT PARAMETERS ----------------------- ###
### --- absolute or relative paths for --- ###
### ---   build and CLEO directories --- ###
path2CLEO = Path(sys.argv[1])
path2build = Path(sys.argv[2])
config_filename = Path(sys.argv[3])

# booleans for [making, saving] initialisation figures
isfigures = [True, True]
gbxs2plt = [0, 10]  # indexes of GBx index of SDs to plot (nb. "all" can be very slow)

### essential paths and filenames
constants_filename = path2CLEO / "libs" / "cleoconstants.hpp"
binariespath = path2build / "share"
savefigpath = path2build / "bin"

grid_filename = (
    binariespath / "dimlessGBxboundaries.dat"
)  # note this should match config.yaml
initsupers_filename = (
    binariespath / "dimlessSDsinit.dat"
)  # note this should match config.yaml

### --- Number of Superdroplets per Gridbox --- ###
nsupers = 128
### ------------------------------------------- ###


### --- Choice of Superdroplet Dry Radii Generator --- ###
dryr_sf = 1.0  # scale factor for dry radii [m]
dryradiigen = dryrgens.ScaledRadiiGen(dryr_sf)  # dryradii are 1/sf of radii [m]
### ---------------------------------------------- ###

### --- Choice of Droplet Radius Probability Distribution and Radii Generator --- ###
geomean = 0.04e-6
geosig = 1.4
numconc = 50 * 1e6
spectrum = spectra.Lognormal(norm_factor=1.0, m_mode=geomean, s_geom=geosig)

### --- Choice of Superdroplet  --- ###
alpha = 0.75
default_cdf_range = (0.00001, 0.99999)
rspan = spectrum.percentiles(
    default_cdf_range
)  # min and max range of radii to sample [m]
radiigen, xiprobdist = alphasampling.AlphaSamplingWrapper(spectrum, alpha, rspan)
numconc_tolerance = (
    0.001  # 0.1% tolerance on resultant numconc not being equal to input numconc
)
### --------------------------------------------------------- ###

### --- Choice of Superdroplet Coords Generator --- ###
coord3gen = crdgens.SampleCoordGen(True)  # sample coord3 range randomly or not
coord1gen = None  # do not generate superdroplet coord1s
coord2gen = None  # do not generate superdroplet coord2s
### ----------------------------------------------- ###

### -------------------- BINARY FILE GENERATION--------------------- ###
### ensure build, share and bin directories exist
if path2CLEO == path2build:
    raise ValueError("build directory cannot be CLEO")
else:
    path2build.mkdir(exist_ok=True)
    binariespath.mkdir(exist_ok=True)
    if isfigures[1]:
        savefigpath.mkdir(exist_ok=True)


### write initial superdrops binary
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
    isprintinfo=True,
    isfigures=isfigures,
    savefigpath=savefigpath,
    gbxs2plt=gbxs2plt,
)
### ---------------------------------------------------------------- ###
