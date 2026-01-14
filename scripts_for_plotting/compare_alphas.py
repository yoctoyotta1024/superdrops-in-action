"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: compare_alphas.py
Project: scripts
Created Date: Thursday 11th December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Plot results of 1-D kid test case for CLEO and PySDM with only condensation/evaporation enabled
or with precipitation enabled.
"""

# %%
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src import load_ensemble_datasets as led
from src import calcs

# %%
parser = argparse.ArgumentParser()
parser.add_argument(
    "--cleo_path2build",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/",
    help="path to CLEO bin directories containing .zarr and .txt datasets of ensembles",
)
parser.add_argument(
    "--pysdm_path2build",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/pysdm_1dkid/build/",
    help="path to PySDM bin directories containing .npy files for data in ensembles",
)
parser.add_argument(
    "--cleo_grid_filename",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/share/dimlessGBxboundaries.dat",
    help="path to gridbox boundaries binary file",
)
parser.add_argument(
    "--path4figs",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/plots",
    help="path to save figures in",
)
args = parser.parse_known_args()[0]

is_precip = True
precip_rolling_window = 100  # [number of timesteps, 1 timestep~1.25s]

# %% Check directories containing datasets exist
assert args.cleo_path2build.is_dir(), f"cleo_path2build: {args.cleo_path2build}"
assert args.pysdm_path2build.is_dir(), f"pysdm_path2build: {args.pysdm_path2build}"
assert args.path4figs.is_dir(), f"path4figs: {args.path4figs}"

# %% font sizes for beautifying plots
SMALL_SIZE = 15
MEDIUM_SIZE = 16
BIG_SIZE = 18.5

plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=BIG_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=BIG_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=BIG_SIZE)  # legend fontsize
plt.rc("figure", titlesize=BIG_SIZE)  # fontsize of the figure title

# %% Load CLEO ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50, False): ([256], [0.0, 0.5, 1.0]),  # [0, 0.5, 1.0]),
    (50, True): ([256], [0.0, 0.5, 1.0]),
    (150, False): ([256], [0.0, 0.5, 1.0]),
    (150, True): ([256], [0.0, 0.5, 1.0]),
    (300, False): ([256], [0.0, 0.5, 1.0]),
    (300, True): ([256], [0.0, 0.5, 1.0]),
}

cleo_datasets = led.fetch_cleo_datasets(
    args.cleo_path2build,
    args.cleo_grid_filename,
    setups,
    is_precip,
    precip_rolling_window,
)

print(f"---- {len(cleo_datasets)} ensembles of cleo data ---- ")
for key, value in cleo_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")


# %% Load PySDM ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50.0, True): ([256], [0.0, 0.5, 1.0]),
    (150.0, True): ([256], [0.0, 0.5, 1.0]),
    (300.0, True): ([256], [0.0, 0.5, 1.0]),
}

pysdm_datasets = led.fetch_pysdm_datasets(
    args.pysdm_path2build, setups, is_precip, precip_rolling_window
)

print(f"---- {len(pysdm_datasets)} ensembles of pysdm data ---- ")
for key, value in pysdm_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")
# %% print available ensemble names
print(f"---- {len(pysdm_datasets)} ensembles of pysdm data ---- ")
for key, value in pysdm_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")
print(f"---- {len(cleo_datasets)} ensembles of cleo data ---- ")
for key, value in cleo_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")
# %% Plot Hill figure 4 (top 2 rows only)
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(21, 5), width_ratios=[5, 5, 5, 4])
gs = axes[0, -1].get_gridspec()
for ax in axes[:, -1]:
    ax.remove()
axes = axes[:, :-1]
legax = fig.add_subplot(gs[:, -1])
legax.spines[["right", "top", "left", "bottom"]].set_visible(False)
legax.set_xticks([])
legax.set_yticks([])


def get_style(model, fixed_coaleff, alpha):
    if model == "pysdm" and fixed_coaleff:
        c = "red"
    elif model == "pysdm" and not fixed_coaleff:
        c = "orange"
    elif model == "cleo" and fixed_coaleff:
        c = "blue"
    elif model == "cleo" and not fixed_coaleff:
        c = "purple"

    if alpha == 0.0:
        line = "solid"
    elif alpha == 0.5:
        line = "dashed"
    elif alpha == 1.0:
        line = "dotted"

    if model == "pysdm":
        mdl = "PySDM"
    elif model == "cleo":
        mdl = "CLEO"
    if not fixed_coaleff:
        lbl = f"{mdl}" + " with $E_{coll}$, " + f"\u03B1={alpha}"
    else:
        lbl = f"{mdl}, \u03B1={alpha}"

    return {"color": c, "linestyle": line, "label": lbl}


axes_setups = {
    0: {
        "numconc": 50,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
    1: {
        "numconc": 150,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
    2: {
        "numconc": 300,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
}

handles, labels = [], []
for a in range(len(axes_setups)):
    ax = axes[:, a]  # axes for given numconc
    numconc = axes_setups[a]["numconc"]
    nsupers = axes_setups[a]["nsupers"]

    for alpha in axes_setups[a]["alpha"]:
        for fixed_coaleff in axes_setups[a]["fixed_coaleff"]:
            label = led.get_label(is_precip, fixed_coaleff, numconc, nsupers, alpha)
            if label not in pysdm_datasets.keys():
                print(f"skipping PySDM {label}")
            else:
                # print(f"{label} found for PySDM")
                ds = pysdm_datasets[label]
                style = get_style("pysdm", fixed_coaleff, alpha)
                ax[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **style)
                ax[1].plot(ds.time, ds.surfprecip_rolling.mean(dim="ensemble"), **style)

                style["label"] = None
                style["alpha"] = 0.15
                lower, upper = calcs.mean_pm_stddev(ds.lwp, dim="ensemble")
                ax[0].fill_between(ds.time, lower, upper, **style)
                lower, upper = calcs.mean_pm_stddev_surfprecip_rolling(
                    ds, precip_rolling_window, dim="ensemble"
                )
                ax[1].fill_between(ds.time, lower, upper, **style)

            if label not in cleo_datasets.keys():
                print(f"skipping CLEO {label}")
            else:
                # print(f"{label} found for CLEO")
                ds = cleo_datasets[label]
                style = get_style("cleo", fixed_coaleff, alpha)
                ax[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **style)
                ax[1].plot(ds.time, ds.surfprecip_rolling.mean(dim="ensemble"), **style)

                style["label"] = None
                style["alpha"] = 0.15
                lower, upper = calcs.mean_pm_stddev(ds.lwp, dim="ensemble")
                ax[0].fill_between(ds.time, lower, upper, **style)
                lower, upper = calcs.mean_pm_stddev_surfprecip_rolling(
                    ds, precip_rolling_window, dim="ensemble"
                )
                ax[1].fill_between(ds.time, lower, upper, **style)

    hands, labs = ax[0].get_legend_handles_labels()
    for lab in labs:
        if lab not in labels:
            labels.append(lab)
            handles.append(hands[labs.index(lab)])

legax.legend(handles, labels)

for ax in axes.flatten():
    ax.spines[["right", "top"]].set_visible(False)
    ax.set_xlim([0, 3000])

for ax in axes[1, :]:
    ax.set_xlabel("time [s]")

axes[0, 0].set_ylabel("LWP / kg m$^{-2}$")
ylims1 = [0.0, 1.75]
yticks1 = np.arange(ylims1[0], ylims1[1] + 0.5, 0.5)
for ax in axes[0, :]:
    ax.set_ylim(ylims1)
    ax.set_yticks(yticks1)

axes[1, 0].set_ylabel("P / mm $h^{-1}$")
ylims2 = [0.0, 4.0]
yticks2 = np.arange(ylims2[0], ylims2[1] + 1.0, 1.0)
for ax in axes[1, :]:
    ax.set_ylim(ylims2)
    ax.set_yticks(yticks2)

plt.savefig(args.path4figs / "fig4_alphas.pdf", format="pdf", bbox_inches="tight")
plt.show()

# %% Plot different version of Hill figure 4 (top 2 rows only)
fig, axes = plt.subplots(
    nrows=5, ncols=2, figsize=(10, 10), height_ratios=[5, 5, 1, 5, 5]
)
gs = axes[2, 1].get_gridspec()
axes[2, 0].remove()  # padding axes
for ax in axes[2:, -1]:
    ax.remove()  # legend axes
axes = [[axes[0, 0], axes[1, 0]], [axes[0, 1], axes[1, 1]], [axes[3, 0], axes[4, 0]]]
legax = fig.add_subplot(gs[2:, -1])
legax.spines[["right", "top", "left", "bottom"]].set_visible(False)
legax.set_xticks([])
legax.set_yticks([])

axes_setups = {
    0: {
        "numconc": 50,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
    1: {
        "numconc": 150,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
    2: {
        "numconc": 300,
        "nsupers": 256,
        "alpha": [0.0, 0.5, 1.0],
        "fixed_coaleff": [True, False],
    },
}

handles, labels = [], []
for a in range(len(axes_setups)):
    axs = axes[a]  # axes for given numconc
    numconc = axes_setups[a]["numconc"]
    nsupers = axes_setups[a]["nsupers"]

    for alpha in axes_setups[a]["alpha"]:
        for fixed_coaleff in axes_setups[a]["fixed_coaleff"]:
            label = led.get_label(is_precip, fixed_coaleff, numconc, nsupers, alpha)
            if label not in pysdm_datasets.keys():
                print(f"skipping PySDM {label}")
            else:
                # print(f"{label} found for PySDM")
                ds = pysdm_datasets[label]
                style = get_style("pysdm", fixed_coaleff, alpha)
                axs[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **style)
                axs[1].plot(
                    ds.time, ds.surfprecip_rolling.mean(dim="ensemble"), **style
                )

                style["label"] = None
                style["alpha"] = 0.15
                lower, upper = calcs.mean_pm_stddev(ds.lwp, dim="ensemble")
                axs[0].fill_between(ds.time, lower, upper, **style)
                lower, upper = calcs.mean_pm_stddev_surfprecip_rolling(
                    ds, precip_rolling_window, dim="ensemble"
                )
                axs[1].fill_between(ds.time, lower, upper, **style)

            if label not in cleo_datasets.keys():
                print(f"skipping CLEO {label}")
            else:
                # print(f"{label} found for CLEO")
                ds = cleo_datasets[label]
                style = get_style("cleo", fixed_coaleff, alpha)
                axs[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **style)
                axs[1].plot(
                    ds.time, ds.surfprecip_rolling.mean(dim="ensemble"), **style
                )

                style["label"] = None
                style["alpha"] = 0.15
                lower, upper = calcs.mean_pm_stddev(ds.lwp, dim="ensemble")
                axs[0].fill_between(ds.time, lower, upper, **style)
                lower, upper = calcs.mean_pm_stddev_surfprecip_rolling(
                    ds, precip_rolling_window, dim="ensemble"
                )
                axs[1].fill_between(ds.time, lower, upper, **style)

    hands, labs = axs[0].get_legend_handles_labels()
    for lab in labs:
        if lab not in labels:
            labels.append(lab)
            handles.append(hands[labs.index(lab)])

legax.legend(handles, labels, loc="lower center")

for axs in axes:
    for ax in axs:
        ax.spines[["right", "top"]].set_visible(False)
        ax.set_xlim([0, 3000])

for ax in [axes[0][1], axes[1][1], axes[2][1]]:
    ax.set_xlabel("time [s]")

ylims1 = [0.0, 1.6]
yticks1 = np.arange(ylims1[0], ylims1[1] + 0.5, 0.5)
for ax in [axes[0][0], axes[1][0], axes[2][0]]:
    ax.set_ylabel("LWP / kg m$^{-2}$")
    ax.set_yticks(yticks1)
    ax.set_ylim(ylims1)

ylims2 = [0.0, 3.25]
yticks2 = np.arange(ylims2[0], ylims2[1] + 1.0, 1.0)
for ax in [axes[0][1], axes[1][1], axes[2][1]]:
    ax.set_ylabel("P / mm $h^{-1}$")
    ax.set_yticks(yticks2)
    ax.set_ylim(ylims2)

panels = ["a)", "b)", "c)"]
for a in range(len(axes_setups)):
    numconc = axes_setups[a]["numconc"]
    axes[a][0].set_title(f"{panels[a]}" + "  N$_c$ = " + f"{numconc}" + " cm$^{{-3}}$")

fig.tight_layout()
plt.subplots_adjust(hspace=0.5)

plt.savefig(args.path4figs / "fig4_alphas_v2.pdf", format="pdf", bbox_inches="tight")
plt.show()


# %%
