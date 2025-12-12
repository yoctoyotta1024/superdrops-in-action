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
from PySDM.physics import convert_to, si

import matplotlib.pyplot as plt
from open_atmos_jupyter_utils import show_plot

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

alphas = [0.5]
n_sd_per_gridbox = int(cnfg["superdroplet_initialization"]["n_sd_per_gridbox"])
aerosol_conc = float(cnfg["superdroplet_initialization"]["numconc"]) / si.m**3
geomean = float(cnfg["superdroplet_initialization"]["geomean"])
geosig = float(cnfg["superdroplet_initialization"]["geosig"])

is_precip = bool(cnfg["sdm_settings"]["is_precip"])
n_iters = int(cnfg["sdm_settings"]["n_iters"])

binpath = Path(cnfg["outputfiles"]["binpath"])
figspath = Path(cnfg["outputfiles"]["figspath"])
assert binpath.exists(), f"Output path {binpath} does not exist!"
assert figspath.exists(), f"Plots path {figspath} does not exist!"
# %%
output = {}
settings = {}
simulation = {}

# %%
for alph in alphas:
    print(f"Running {n_iters} simulations with alpha={alph} ...")
    for i in range(n_iters):
        key = f"naero{aerosol_conc/1e6}_precip{is_precip}_a{alph}_r{i}".replace(
            ".", "p"
        )
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


# %%
def plot_with_iterations(
    var,
    qlabel,
    fname,
    output,
    n_iters,
    na,
    precip,
    vmin=None,
    vmax=None,
    cmin=None,
    cmax=None,
    line=None,
    colors=None,
):
    line = line or {15: ":", 20: "--", 25: "-", 30: "-."}
    colors = colors or {15: "k", 20: "tab:blue", 25: "tab:orange", 30: "tab:green"}

    # Aggregate data across iterations
    var_iters = []
    for i in range(n_iters):
        key = f"naero{aerosol_conc/1e6}_precip{is_precip}_a{alph}_r{i}".replace(
            ".", "p"
        )
        var_iters.append(output[key][var])

    # Compute mean and standard deviation
    var_mean = np.mean(var_iters, axis=0)
    var_std = np.std(var_iters, axis=0)

    dt = output[key]["t"][1] - output[key]["t"][0]
    dz = output[key]["z"][1] - output[key]["z"][0]
    tgrid = np.concatenate(((output[key]["t"][0] - dt / 2,), output[key]["t"] + dt / 2))
    zgrid = np.concatenate(((output[key]["z"][0] - dz / 2,), output[key]["z"] + dz / 2))
    convert_to(zgrid, si.km)

    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(25, 5)
    ax1 = fig.add_subplot(gs[:-1, 0:4])
    if cmin is not None and cmax is not None:
        mesh = ax1.pcolormesh(tgrid, zgrid, var_mean, cmap="BuPu", vmin=cmin, vmax=cmax)
    else:
        mesh = ax1.pcolormesh(tgrid, zgrid, var_mean, cmap="BuPu")

    ax1.set_xlabel("time [s]")
    ax1.set_ylabel("z [km]")
    ax1.set_ylim(0, None)

    cbar = fig.colorbar(mesh, fraction=0.05, location="top")
    cbar.set_label(qlabel)

    ax2 = fig.add_subplot(gs[:-1, 4:], sharey=ax1)
    ax2.set_xlabel(qlabel)

    last_t = 0
    for i, t in enumerate(output[key]["t"]):
        x_mean, z = var_mean[:, i], output[key]["z"].copy()
        x_std = var_std[:, i]
        convert_to(z, si.km)
        params = {"color": "black"}
        for line_t, line_s in line.items():
            if last_t < line_t * si.min <= t:
                params["ls"] = line_s
                # Plot mean line
                ax2.plot(x_mean, z, color=colors[line_t])
                # Add shaded region for standard deviation
                ax2.fill_betweenx(
                    z, x_mean - x_std, x_mean + x_std, color=colors[line_t], alpha=0.2
                )
                if vmin is not None and vmax is not None:
                    ax1.axvline(t, ymin=vmin, ymax=vmax, color=colors[line_t])
                else:
                    ax1.axvline(t, color=colors[line_t])
        last_t = t

    show_plot(filename=fname, inline_format="png")


# %%
ensembles = {}
for alph in alphas:
    print(f"Now loading data for {n_iters} simulations with alpha={alph} ...")
    for i in range(n_iters):
        key = f"naero{aerosol_conc/1e6}_precip{is_precip}_a{alph}_r{i}".replace(
            ".", "p"
        )
        print(f"loading n_iter={i}, key: {key}")
        output_folder = binpath / key

        dataset = {}
        dataset["cloud_water_mixing_ratio"] = np.load(
            output_folder / "cloud_water_mixing_ratio.npy"
        )
        dataset["rain_water_mixing_ratio"] = np.load(
            output_folder / "rain_water_mixing_ratio.npy"
        )
        dataset["q_cond"] = (
            dataset["cloud_water_mixing_ratio"] + dataset["rain_water_mixing_ratio"]
        )
        dataset["t"] = np.load(output_folder / "t.npy")
        dataset["z"] = np.load(output_folder / "z.npy")

        ensembles[key] = dataset

for alph in alphas:
    print(f"Now plotting {n_iters} simulations with alpha={alph} ...")
    for i in range(n_iters):
        key = f"naero{aerosol_conc/1e6}_precip{is_precip}_a{alph}_r{i}".replace(
            ".", "p"
        )
        print(f"plotting n_iter={i}, key: {key}")

        condline = {5: ":", 7: "--", 9: "-", 11: "-.", 60: ":"}
        condcolors = {5: "grey", 7: "black", 9: "darkblue", 11: "violet", 60: "darkred"}
        precipline = {7: ":", 9: "--", 20: "-", 30: "-.", 60: ":"}
        precipcolors = {
            7: "black",
            9: "darkblue",
            20: "mediumorchid",
            30: "crimson",
            60: "darkred",
        }

        if is_precip:
            line = precipline
            color = precipcolors
        else:
            line = condline
            color = condcolors

        figs_folder = figspath / key
        Path.mkdir(figs_folder, exist_ok=True)
        plot_with_iterations(
            var="q_cond",
            qlabel="q_cond",
            fname=f"{figs_folder / key}.pdf",
            output=ensembles,
            n_iters=n_iters,
            na=aerosol_conc / 1e6,
            precip=is_precip,
            line=line,
            colors=color,
        )
# %%
