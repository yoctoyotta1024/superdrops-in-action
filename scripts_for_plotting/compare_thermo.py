"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: compare_thermo.py
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
import matplotlib.pyplot as plt
from pathlib import Path

from src import load_ensemble_datasets as led

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

# is_precip = False
is_precip = True
precip_rolling_window = 100  # [number of timesteps, 1 timestep~1.25s]

# %% Check directories containing datasets exist
assert args.cleo_path2build.is_dir(), f"cleo_path2build: {args.cleo_path2build}"
assert args.pysdm_path2build.is_dir(), f"pysdm_path2build: {args.pysdm_path2build}"
assert args.path4figs.is_dir(), f"path4figs: {args.path4figs}"

# %% Load CLEO ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50, False): ([256], [0.5]),
    (50, True): ([256], [0.5]),
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
    print(key)
print("-------------------------------- ")

# %% Load PySDM ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50.0, True): ([256], [0.5]),
}

pysdm_datasets = led.fetch_pysdm_datasets(
    args.pysdm_path2build, setups, is_precip, precip_rolling_window
)

print(f"---- {len(pysdm_datasets)} ensembles of pysdm data ---- ")
for key, value in pysdm_datasets.items():
    print(key)
print("-------------------------------- ")
# %% print available ensemble names
print(f"---- {len(pysdm_datasets)} ensembles of pysdm data ---- ")
for key, value in pysdm_datasets.items():
    print(key)
print("-------------------------------- ")
print(f"---- {len(cleo_datasets)} ensembles of cleo data ---- ")
for key, value in cleo_datasets.items():
    print(key)
print("-------------------------------- ")

# %%
fig, axs = plt.subplots(nrows=10, ncols=1, figsize=(8, 20))
# cds = cleo_datasets["is_precipFalse_numconc50p000_nsupers256_alpha0p500_fixedeffFalse"]
# pds = pysdm_datasets["is_precipFalse_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
# cds = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse"]
cds = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
pds = pysdm_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]

fig.suptitle("CLEO - PySDM")


def diff(v1, v2):
    return v1.mean(dim="ensemble") - v2.mean(dim="ensemble")


diff(cds.temp, pds.T).plot(ax=axs[0], y="height", cmap="bwr")
axs[0].set_title("temp /K")

diff(cds.press, pds.p).plot(ax=axs[1], y="height", cmap="bwr")
axs[1].set_title("press / hPa")

diff(cds.qvap, pds.water_vapour_mixing_ratio).plot(ax=axs[2], y="height", cmap="bwr")
axs[2].set_title("qvap /g/kg")

diff(cds.relh, pds.RH).plot(ax=axs[3], y="height", cmap="bwr")
axs[3].set_title("relh /%")

diff(cds.qcond, pds.water_liquid_mixing_ratio).plot(ax=axs[4], y="height", cmap="bwr")
axs[4].set_title("qcond /g/kg")

diff(cds.lwc, pds.lwc).plot(ax=axs[5], y="height", cmap="bwr")
axs[5].set_title("LWC /g/m$^{-3}$")

times2plot = [0.0, 500, 1500]
colors = ["C1", "C2", "C3"]
for t, c in zip(times2plot, colors):
    cds.qvap.mean(dim="ensemble").sel(time=t, method="nearest").plot(
        ax=axs[6], y="height", c=c, label=t
    )
    pds.water_vapour_mixing_ratio.mean(dim="ensemble").sel(
        time=t, method="nearest"
    ).plot(ax=axs[6], y="height", linestyle="--", c=c, label=t)
axs[6].legend(loc="upper left")
axs[6].set_xlim([10, 15.25])
axs[6].set_ylim([0.0, 3000])
axs[6].set_title(f"qvap at {times2plot}s /g/kg")

times2plot = [400, 1500]
colors = ["C0", "C3"]
for t, c in zip(times2plot, colors):
    cds.qcond.mean(dim="ensemble").sel(time=t, method="nearest").plot(
        ax=axs[7], y="height", c=c, label=t
    )
    pds.water_liquid_mixing_ratio.mean(dim="ensemble").sel(
        time=t, method="nearest"
    ).plot(ax=axs[7], y="height", linestyle="--", c=c, label=t)
axs[7].legend(loc="upper left")
axs[7].set_xlim([0.4, 1.4])
axs[7].set_ylim([0.0, 3000])
axs[7].set_title(f"qcond at {times2plot}s /g/kg")

times2plot = [400, 1500]
colors = ["C0", "C3"]
for t, c in zip(times2plot, colors):
    cds.lwc.mean(dim="ensemble").sel(time=t, method="nearest").plot(
        ax=axs[8], y="height", c=c, label=t
    )
    pds.lwc.mean(dim="ensemble").sel(time=t, method="nearest").plot(
        ax=axs[8], y="height", linestyle="--", c=c, label=t
    )
axs[8].legend(loc="upper left")
axs[8].set_xlim([0.4, 1.6])
axs[8].set_ylim([0.0, 3000])
axs[8].set_title(f"lwc {times2plot}s /g/m$^3$")


cds.lwp.mean(dim="ensemble").plot(ax=axs[9], x="time", c="green")
pds.lwp.mean(dim="ensemble").plot(ax=axs[9], x="time", c="darkgreen", linestyle="--")
axs[9].set_xlim([0.0, 3600])
axs[9].set_ylim([0.0, 1.6])
axs[9].set_title("lwp /kg/m$^3$")
axs[9].spines[["right", "top"]].set_visible(False)

fig.tight_layout()
plt.show()
# %%
fig, axs = plt.subplots(nrows=6, ncols=2, figsize=(8, 16))
cds1 = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse"]
cds2 = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
pds = pysdm_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]

fig.suptitle("Reference is CLEO with fixed CoalEff, Ec=1")


def diff(v1, v2):
    return v1.mean(dim="ensemble") - v2.mean(dim="ensemble")


diff(cds2.temp, cds1.temp).plot(ax=axs[0, 0], y="height", cmap="bwr")
diff(cds2.temp, pds.T).plot(ax=axs[0, 1], y="height", cmap="bwr")
axs[0, 0].set_title("CLEO Ec=1 - CLEO with Ec\ntemp /K")
axs[0, 1].set_title("CLEO Ec=1 - PySDM\ntemp /K")

diff(cds2.press, cds1.press).plot(ax=axs[1, 0], y="height", cmap="bwr")
diff(cds2.press, pds.p).plot(ax=axs[1, 1], y="height", cmap="bwr")
axs[1, 0].set_title("press /hPa")

diff(cds2.qvap, cds1.qvap).plot(ax=axs[2, 0], y="height", cmap="bwr")
diff(cds2.qvap, pds.water_vapour_mixing_ratio).plot(
    ax=axs[2, 1], y="height", cmap="bwr"
)
axs[2, 0].set_title("qvap /g/kg")

diff(cds2.relh, cds1.relh).plot(ax=axs[3, 0], y="height", cmap="bwr")
diff(cds2.relh, pds.RH).plot(ax=axs[3, 1], y="height", cmap="bwr")
axs[3, 0].set_title("relh /%")

diff(cds2.qcond, cds1.qcond).plot(ax=axs[4, 0], y="height", cmap="bwr")
diff(cds2.qcond, pds.water_liquid_mixing_ratio).plot(
    ax=axs[4, 1], y="height", cmap="bwr"
)
axs[4, 0].set_title("qcond /g/kg")

diff(cds2.surfprecip_rate, cds1.surfprecip_rate).plot(ax=axs[5, 0])
diff(cds2.surfprecip_rate, pds.surfprecip_rate).plot(ax=axs[5, 1])
axs[5, 0].set_title("precip /mm h$^-1$")

fig.tight_layout()
plt.show()

# %%
