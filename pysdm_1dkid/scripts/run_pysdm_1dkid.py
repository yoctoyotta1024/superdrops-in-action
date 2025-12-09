"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: run_pysdm_1dkid.py
Project: scripts
Created Date: Tuesday 9th December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Run 1-D kid test case for PySDM with only condensation/evaporation enabled
or with precipitation enabled.
"""

# %%
import argparse
import yaml
import numpy as np
from pathlib import Path

from PySDM_examples.Shipway_and_Hill_2012 import Settings, Simulation
from PySDM.physics import si

# %%
parser = argparse.ArgumentParser()
parser.add_argument(
    "--config_filename",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/pysdm_1dkid/share/config.yaml",
    help="path to configuration yaml for test run",
)
args = parser.parse_known_args()[0]
cnfg = yaml.safe_load(open(args.config_filename))

common_params = {
    "dt": 1.25 * si.s,
    "dz": 25 * si.m,
    "p0": 1000 * si.hPa,
    "kappa": 0.9,
    "rho_times_w_1": 3 * si.kg / si.m**3,
    "save_spec_and_attr_times": np.linspace(0, 3600, 2881),
    "cloud_water_radius_range": (2 * si.um, 50 * si.um),
    "rain_water_radius_range": (50 * si.um, np.inf),
    "ignore_moisture_profile_in_density_calc": False,
    # 'collision_kernel': Hydrodynamic(),
}

alphas = [0.0, 0.5, 1.0]
n_sd_per_gridbox = int(cnfg["superdroplet_initialization"]["n_sd_per_gridbox"])
aerosol_conc = float(cnfg["superdroplet_initialization"]["numconc"]) / si.m**3
geomean = float(cnfg["superdroplet_initialization"]["geomean"])
geosig = float(cnfg["superdroplet_initialization"]["geosig"])

is_precip = bool(cnfg["sdm_settings"]["is_precip"])
n_iters = int(cnfg["sdm_settings"]["n_iters"])

binpath = Path(cnfg["outputfiles"]["output_path"])
assert binpath.exists(), f"Output path {binpath} does not exist!"
# %%
output = {}
settings = {}
simulation = {}

# %%
for alph in alphas:
    print(f"Running {n_iters} simulations with alpha={alph} ...")
    for i in range(n_iters):
        key = f"naero{aerosol_conc/1e6}_precip{is_precip}_a{alph}_r{i}".replace(".", "p")
        print(f"running n_iter={i}, key: {key}")
        settings[key] = Settings(
            **common_params,
            n_sd_per_gridbox=n_sd_per_gridbox,
            particles_per_volume_STP=aerosol_conc,
            precip=is_precip,
            geomean=geomean,
            geosig=geosig,
            alpha=alph,
        )
        settings[key].formulae.seed = i
        simulation[key] = Simulation(settings[key])
        output[key] = simulation[key].run().products

        output_folder = binpath / key
        Path.mkdir(output_folder, exist_ok=True)
        for variable, values in output[key].items():
            assert type(values) == np.ndarray
            file = output_folder / f"{variable}.npy".replace(" ", "_")
            np.save(file, values)
