"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: __init__.py
Project: cleo_sdm
Created Date: Monday 23rd June 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
"""


import argparse
import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))  # scripts directory
import shared_script_variables as ssv

parser = argparse.ArgumentParser()
parser.add_argument("path2CLEO", type=Path, help="Absolute path to CLEO (for pySD)")
parser.add_argument("path2builds", type=Path, help="Absolute path to builds")
parser.add_argument(
    "buildtype",
    type=str,
    choices=["serial", "openmp", "cuda", "threads"],
    help="Type of build: serial, openmp, cuda or threads",
)
parser.add_argument(
    "--gen_initconds",
    type=str,
    choices=["TRUE", "FALSE"],
    default="TRUE",
    help="=='TRUE', else don't generate initial condition binary files",
)
args = parser.parse_args()

path2src = Path(__file__).resolve().parent.parent.parent / "src"
path2CLEO = args.path2CLEO
path2builds = args.path2builds
buildtype = args.buildtype
if args.gen_initconds == "TRUE":
    gen_initconds = True
else:
    gen_initconds = False

sys.path.append(str(path2CLEO))  # for imports for editing a config file
sys.path.append(str(path2src))  # for imports for input files generation
from collisions0d import initconds_colls0d as initconds
from pySD import editconfigfile

### ----- create temporary config file for simulation(s) ----- ###
src_config_filename = path2src / "collisions0d" / "config_colls0d.yaml"

ngbxs_nsupers_runs = ssv.get_ngbxs_nsupers_runs()
ngbxs_nsupers_nthreads = ssv.get_ngbxs_nsupers_nthreads(
    buildtype, ngbxs_nsupers_runs=ngbxs_nsupers_runs
)

savefigpath = path2builds / "bin" / "colls0d"
sharepath = path2builds / "share" / "colls0d"
binpath = path2builds / buildtype / "bin" / "colls0d"
tmppath = path2builds / buildtype / "tmp" / "colls0d"
constants_filepath = path2builds / buildtype / "_deps" / "cleo-src" / "libs"
params = {
    "constants_filename": str(constants_filepath / "cleoconstants.hpp"),
    "sharepath": str(sharepath),
    "savefigpath": str(savefigpath),
}


def get_grid_filename(sharepath: Path, ngbxs: int):
    return str(sharepath / f"dimlessGBxboundaries_{ngbxs}.dat")


def get_initsupers_filename(sharepath: Path, ngbxs: int, nsupers: int, nrun: int):
    return sharepath / f"dimlessSDsinit_{ngbxs}_{nsupers}_{nrun}.dat"


### --- ensure build, share and bin directories exist --- ###
if path2CLEO == path2builds:
    raise ValueError("build directory cannot be CLEO")
else:
    savefigpath.mkdir(exist_ok=True, parents=True)
    sharepath.mkdir(exist_ok=True, parents=True)
    binpath.mkdir(exist_ok=True, parents=True)
    tmppath.mkdir(exist_ok=True, parents=True)

for ngbxs, nsupers in ngbxs_nsupers_runs.keys():
    ### ----- Copy config to temporary file and edit specific parameters ----- ###
    for nrun in range(ngbxs_nsupers_runs[(ngbxs, nsupers)]):
        for nthreads in ngbxs_nsupers_nthreads[(ngbxs, nsupers)]:
            config_filename = ssv.get_config_filename(
                tmppath, ngbxs, nsupers, nrun, nthreads=nthreads
            )
            binpath_run = ssv.get_run_binpath(
                binpath, ngbxs, nsupers, nrun, nthreads=nthreads
            )

            params["num_threads"] = nthreads

            params["ngbxs"] = ngbxs
            params["grid_filename"] = str(get_grid_filename(sharepath, ngbxs))
            if ngbxs < 64:
                ndim_x = ndim_y = 1
            else:
                ndim_x = ndim_y = 8
                assert ngbxs % 64 == 0, "ngbxs > 64 must also be a multiple of 64"
            ndim_z = ngbxs / ndim_x / ndim_y
            assert (
                ndim_x * ndim_z * ndim_y == ngbxs
            ), "product of ndims must equal ngbxs"
            params["zgrid"] = [0, 10000, 10000 / ndim_z]
            params["xgrid"] = [0, 10000, 10000 / ndim_x]
            params["ygrid"] = [0, 10000, 10000 / ndim_y]

            params["maxnsupers"] = nsupers * ngbxs
            params["initsupers_filename"] = str(
                get_initsupers_filename(sharepath, ngbxs, nsupers, nrun)
            )

            params["setup_filename"] = str(binpath_run / "setup.txt")
            params["zarrbasedir"] = str(binpath_run / "sol.zarr")

            shutil.copy(Path(src_config_filename), config_filename)
            editconfigfile.edit_config_params(config_filename, params)

if gen_initconds:
    for ngbxs, nsupers in ngbxs_nsupers_runs.keys():
        isfigures = [True, True]
        nthreads_dummy = ngbxs_nsupers_nthreads[(ngbxs, nsupers)][
            0
        ]  # all nthreads use same initial conditions
        ### ----- write initial gridbox boundaries binary file ----- ###
        nrun_dummy = 0  # all runs use same init gbxs
        config_filename = ssv.get_config_filename(
            tmppath, ngbxs, nsupers, nrun=nrun_dummy, nthreads=nthreads_dummy
        )
        shutil.rmtree(get_grid_filename(sharepath, ngbxs), ignore_errors=True)
        initconds.gridbox_boundaries(path2CLEO, config_filename, isfigures=isfigures)

        ### ----- write initial superdroplets binary files ----- ###
        for nrun in range(ngbxs_nsupers_runs[(ngbxs, nsupers)]):
            config_filename = ssv.get_config_filename(
                tmppath, ngbxs, nsupers, nrun, nthreads=nthreads_dummy
            )
            shutil.rmtree(
                get_initsupers_filename(sharepath, ngbxs, nsupers, nrun),
                ignore_errors=True,
            )
            initconds.initial_superdroplet_conditions(
                path2CLEO, config_filename, isfigures=isfigures
            )
            isfigures = [False, False]  # only plot SD figures once
