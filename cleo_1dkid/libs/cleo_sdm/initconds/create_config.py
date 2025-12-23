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
import shutil
from pathlib import Path
import yaml

parser = argparse.ArgumentParser()
parser.add_argument(
    "src_config_filename", type=Path, help="Absolute path to original config"
)
parser.add_argument(
    "dest_config_filename", type=Path, help="Absolute path to destination config"
)
parser.add_argument(
    "--cleoconstants_filepath",
    type=Path,
    help="path to cleoconstants.hpp file",
)
parser.add_argument(
    "--grid_filename",
    type=Path,
    help="path to gridbox binary file",
)
parser.add_argument(
    "--initsupers_filename",
    type=Path,
    help="path to initial superdroplets binary file",
)
parser.add_argument(
    "--setup_filename",
    type=Path,
    help="path to output .txt file",
)
parser.add_argument(
    "--zarrbasedir",
    type=Path,
    help="path to output .zarr directory",
)
parser.add_argument(
    "--nsupers_pergbx",
    type=int,
    help="number of superdroplets per gridbox",
)
parser.add_argument(
    "--alpha",
    type=float,
    help="alpha value for superdroplet initial conditions",
)
parser.add_argument(
    "--numconc",
    type=float,
    help="number concentration /cm^3 for superdroplet initial conditions",
)
args = parser.parse_args()

from cleopy import editconfigfile

### ----- create temporary config file for simulation(s) ----- ###
cleoconstants_filepath = args.cleoconstants_filepath
grid_filename = args.grid_filename
initsupers_filename = args.initsupers_filename
setup_filename = args.setup_filename
zarrbasedir = args.zarrbasedir
nsupers_pergbx = args.nsupers_pergbx
alpha = args.alpha
numconc_perm3 = float(args.numconc) * 1e6  # [m^-3]

cnfg = yaml.safe_load(open(args.src_config_filename))
initnsupers = int(cnfg["domain"]["ngbxs"]) * nsupers_pergbx
newnsupers = nsupers_pergbx
maxnsupers = initnsupers * 2

# check directories meet requirements
assert cleoconstants_filepath.parent.is_dir()
assert grid_filename.parent.is_dir()
assert initsupers_filename.parent.is_dir()
assert setup_filename.parent.is_dir()
assert zarrbasedir.parent.is_dir()
assert setup_filename.suffix == ".txt"
assert zarrbasedir.suffix == ".zarr"

# copy src_config to dest_config and then edit parameters in this dictionary
params = {
    "constants_filename": str(cleoconstants_filepath / "cleoconstants.hpp"),
    "grid_filename": str(grid_filename),
    "initsupers_filename": str(initsupers_filename),
    "setup_filename": str(setup_filename),
    "zarrbasedir": str(zarrbasedir),
    "nsupers_pergbx": int(nsupers_pergbx),
    "alpha": float(alpha),
    "maxnsupers": int(maxnsupers),
    "initnsupers": int(initnsupers),
    "newnsupers": int(newnsupers),
    "numconc": int(numconc_perm3),
    "NUMCONC_a": int(numconc_perm3),
}

print("--- create_config configuration arguments ---")
print(args.src_config_filename, args.dest_config_filename)
for k, v in params.items():
    print(k, v)
print("---------------------------------------------")
shutil.copy(args.src_config_filename, args.dest_config_filename)
editconfigfile.edit_config_params(args.dest_config_filename, params)
