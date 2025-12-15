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
import numpy as np
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

is_precip = False
# is_precip = True
precip_rolling_window = 100  # [number of timesteps, 1 timestep~1.25s]

# %% Check directories containing datasets exist
assert args.cleo_path2build.is_dir(), f"cleo_path2build: {args.cleo_path2build}"
assert args.pysdm_path2build.is_dir(), f"pysdm_path2build: {args.pysdm_path2build}"
assert args.path4figs.is_dir(), f"path4figs: {args.path4figs}"

# %% Load CLEO ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    # (50, False): ([256], [0.5]),
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
    print(key, f"members={value.ensemble.size}")
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

# %%
fig, axs = plt.subplots(nrows=10, ncols=1, figsize=(8, 20))
cds = cleo_datasets["is_precipFalse_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
pds = pysdm_datasets["is_precipFalse_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
# cds = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse"]
# cds = cleo_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]
# pds = pysdm_datasets["is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue"]

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

# %% relative humidity from CLEO thermo
from metpy import calc
from metpy.units import units

cds_temp = cds.temp.mean(dim="ensemble") * units.K
cds_press = cds.press.mean(dim="ensemble") * units.hPa
cds_qvap = cds.qvap.mean(dim="ensemble") / 1000

cds_relh = calc.relative_humidity_from_mixing_ratio(cds_press, cds_temp, cds_qvap)
cds_relh.plot(y="height")
# %% relative humidity from PySDM thermo
pds_temp = pds.T.mean(dim="ensemble") * units.K
pds_press = pds.p.mean(dim="ensemble") * units.hPa
pds_qvap = pds.water_vapour_mixing_ratio.mean(dim="ensemble") / 1000

pds_relh = calc.relative_humidity_from_mixing_ratio(pds_press, pds_temp, pds_qvap)
pds_relh.plot(y="height")
# %% sanity check, calculated relh similar to model output
fig, ax = plt.subplots(nrows=2, ncols=3)
cds.relh.mean(dim="ensemble").plot(ax=ax[0, 0], y="height")
cds_relh.plot(ax=ax[0, 1], y="height")
(cds.relh.mean(dim="ensemble") / 100 - cds_relh).plot(ax=ax[0, 2], y="height")
pds.RH.mean(dim="ensemble").plot(ax=ax[1, 0], y="height")
pds_relh.plot(ax=ax[1, 1], y="height")
(pds.RH.mean(dim="ensemble") / 100 - pds_relh).plot(ax=ax[1, 2], y="height")
fig.tight_layout()
# %% temp difference -> cds colder by O(0.1K)
(cds_temp - pds_temp).plot(y="height")
# %% whereas press different (looks like relh difference!)
(cds_press - pds_press).plot(y="height")
# %% relh difference could be due to pressure (and consequently qvap) difference?
fig, ax = plt.subplots(nrows=1, ncols=2)
((cds_qvap - pds_qvap) * 1000).plot(y="height", ax=ax[0])
(cds_relh - pds_relh).plot(y="height", ax=ax[1])
fig.tight_layout()
# %% CLEO 'press' is total pressure at start and remain constant ignoring changing qvap
# however PySDM 'press' is total pressure at the start and changes with changing qvap
RGAS_UNIV = 8.314462618
MR_WATER = 0.01801528
MR_DRY = 0.028966216
RGAS_DRY = RGAS_UNIV / MR_DRY
RGAS_V = RGAS_UNIV / MR_WATER
EPS = RGAS_DRY / RGAS_V

cds_pvap_t0 = (cds_press * (1 + cds_qvap / EPS) - cds_press).sel(
    time=0.0, method="nearest"
)

cds_press_tot = (cds_press - cds_pvap_t0) * (1 + cds_qvap / EPS)
cds_pvap = cds_press_tot - cds_press
cds_pvap.plot(y="height", cmap="bwr")
# %% temperature different remains constant throughout simulation
(cds_temp - pds_temp).sel(time=0.0).plot(y="height")
(cds_temp - pds_temp).sel(time=100, method="nearest").plot(y="height")
(cds_temp - pds_temp).sel(time=500).plot(y="height")
# %% whereas pressure difference increases due to condensation chaning vapour pressure in PySDM
(cds_press - pds_press).sel(time=0.0).plot(y="height")
(cds_press - pds_press).sel(time=100, method="nearest").plot(y="height")
(cds_press - pds_press).sel(time=500).plot(y="height")
# %% not accoutning for change in vapour is screwing up CLEO vs. PySDM!
(cds_press_tot - pds_press).sel(time=0.0).plot(y="height")
(cds_press_tot - pds_press).sel(time=100, method="nearest").plot(y="height")
(cds_press_tot - pds_press).sel(time=500).plot(y="height")
# %% further confirmation
for time in [0, 100, 500]:
    pt0 = pds_qvap.sel(time=0.0, method="nearest")
    pt = pds_qvap.sel(time=time, method="nearest")
    (pt0 - pt).plot(y="height")
plt.show()
for time in [0, 100, 500]:
    pt0 = pds_press.sel(time=0.0, method="nearest")
    pt = pds_press.sel(time=time, method="nearest")
    (pt0 - pt).plot(y="height")
plt.show()
pds_pvap = calc.vapor_pressure(pds_press, pds_qvap)
for time in [0, 100, 500]:
    pt0 = pds_pvap.sel(time=0.0, method="nearest")
    pt = pds_pvap.sel(time=time, method="nearest")
    (pt0 - pt).plot(y="height")
plt.show()
pds_pdry = pds_press - pds_pvap
for time in [0, 100, 500]:
    pt0 = pds_pdry.sel(time=0.0, method="nearest")
    pt = pds_pdry.sel(time=time, method="nearest")
    (pt0 - pt).plot(y="height")
# %% further confirmation
((cds_press - cds_pvap_t0) - pds_pdry).sel(time=0.0).plot(y="height")
((cds_press - cds_pvap_t0) - pds_pdry).sel(time=100, method="nearest").plot(y="height")
((cds_press - cds_pvap_t0) - pds_pdry).sel(time=500).plot(y="height")
# %% swapping in PySDM temperature to relH
pds_temp_on_cdsgrid = pds_temp.interp(height=cds.height)
pds_temp_on_cdsgrid = pds_temp_on_cdsgrid.interp(time=cds.time)
pds_temp_on_cdsgrid = pds_temp_on_cdsgrid.T * units.K

cds_relh_with_pds_temp = calc.relative_humidity_from_mixing_ratio(
    cds_press, pds_temp_on_cdsgrid, cds_qvap
)
(cds_relh_with_pds_temp - pds_relh).plot(y="height")
# %% swapping in PySDM pressure to relH
pds_press_on_cdsgrid = pds_press.interp(height=cds.height)
pds_press_on_cdsgrid = pds_press_on_cdsgrid.interp(time=cds.time)
pds_press_on_cdsgrid = pds_press_on_cdsgrid.T * units.hPa

cds_relh_with_pds_press = calc.relative_humidity_from_mixing_ratio(
    pds_press_on_cdsgrid, cds_temp, cds_qvap
)
(cds_relh_with_pds_press - pds_relh).plot(y="height")
# %% swapping in PySDM vapour to relH
pds_qvap_on_cdsgrid = pds_qvap.interp(height=cds.height)
pds_qvap_on_cdsgrid = pds_qvap_on_cdsgrid.interp(time=cds.time)
pds_qvap_on_cdsgrid = pds_qvap_on_cdsgrid.T

cds_relh_with_pds_qvap = calc.relative_humidity_from_mixing_ratio(
    cds_press, cds_temp, pds_qvap_on_cdsgrid
)
(cds_relh_with_pds_qvap - pds_relh).plot(y="height")
# %% swapping in PySDM vapour and pressure to relH
cds_relh_with_pds_pressqvap = calc.relative_humidity_from_mixing_ratio(
    pds_press_on_cdsgrid, cds_temp, pds_qvap_on_cdsgrid
)
(cds_relh_with_pds_pressqvap - pds_relh).plot(y="height")

# %% Now qvap/qcond seems to be the problem -> collisions start earlier in CLEO
cds_qcond = cds.qcond.mean(dim="ensemble")
pds_qcond = pds.water_liquid_mixing_ratio.mean(dim="ensemble")
for time in [0, 100, 500]:
    fig, ax = plt.subplots(nrows=1, ncols=2)
    ((cds_qvap - pds_qvap) * 1000).sel(time=time, method="nearest").plot(
        y="height", ax=ax[0]
    )
    (cds_qcond).sel(time=time, method="nearest").plot(y="height", ax=ax[1])
    (pds_qcond).sel(time=time, method="nearest").plot(
        y="height", linestyle="--", ax=ax[1]
    )
    ax[0].set_ylim(bottom=-10)
    ax[1].set_ylim(bottom=-10)
    fig.tight_layout()
    plt.show()
# %% check total water content
cds_tot = cds_qcond / 1000 + cds_qvap
pds_tot = pds_qcond / 1000 + pds_qvap
for time in [0, 100, 500]:
    fig, ax = plt.subplots(nrows=1, ncols=2)
    (cds_tot - pds_tot).sel(time=time, method="nearest").plot(y="height", ax=ax[0])
    (cds_tot).sel(time=time, method="nearest").plot(y="height", ax=ax[1])
    (pds_tot).sel(time=time, method="nearest").plot(
        y="height", linestyle="--", ax=ax[1]
    )
    ax[0].set_ylim(bottom=-10)
    ax[1].set_ylim(bottom=-10)
    fig.tight_layout()
    plt.show()

# %% check number of superdroplets per grid-box
cds_nsupers = cds.nsupers.mean(dim="ensemble")
cds_nsupers.plot(y="height", vmin=0, vmax=800)
plt.ylim(0, 3000)
plt.show()

pds_nsupers = pds.super_droplet_count_per_gridbox.mean(dim="ensemble")
pds_nsupers.plot(y="height", vmin=0, vmax=800)
plt.ylim(0, 3000)
plt.show()

# %% attempt to look at effective radius
import xarray as xr
import awkward as ak

rawds = xr.open_dataset(cds.sources.values[0], engine="zarr")


# %%
def unflatten_superdrops(rawdata, raggedcount, nsupers):
    sdarr = ak.unflatten(rawdata, raggedcount)
    sdarr = ak.to_regular(ak.unflatten(sdarr, ak.flatten(nsupers), axis=1), axis=1)
    return sdarr


radius = unflatten_superdrops(
    rawds.radius.values, rawds.raggedcount.values, rawds.nsupers.values
)
radius = radius / 1e6  # [m]
xi = unflatten_superdrops(
    rawds.xi.values, rawds.raggedcount.values, rawds.nsupers.values
)
# %%
r3 = ak.sum((radius**3) * xi, axis=-1)
r2 = ak.sum((radius**2) * xi, axis=-1)
cds_reff = xr.DataArray(
    np.asarray(ak.to_numpy(r3 / r2)),
    name="effective_radius",
    dims=["time", "height"],
    attrs={"units": "m"},
)
# %%
pds_reff = pds.effective_radius.mean(dim="ensemble")
pds_reff.plot(vmin=1e-5, vmax=5e-5)
plt.show()

cds_reff.plot(y="height", vmin=1e-5, vmax=5e-5)

# %% looking at activated droplets
pds_aerosol = (pds.na / 1e6).mean(dim="ensemble")
pds_cloud = (pds.nc / 1e6).mean(dim="ensemble")
pds_rain = (pds.nr / 1e6).mean(dim="ensemble")

pds_numconc = pds_aerosol + pds_cloud + pds_rain
pds_numconc.plot(vmin=0.0, vmax=60)
plt.ylim(bottom=0.0)
plt.show()

cds_numconc = cds.numconc.mean(dim="ensemble")
cds_numconc.plot(y="height", vmin=0.0, vmax=60)
plt.show()
# %% calculate number concentration of categories in CLEO
ntot = ak.sum(xi, axis=-1) / cds.volume.values[None, :] / 1e6  # [cm^-3]
na = (
    ak.sum(ak.where(radius < 1e-6, xi, 0.0), axis=-1) / cds.volume.values[None, :] / 1e6
)  # [cm^-3]
nr = (
    ak.sum(ak.where(radius > 50e-6, xi, 0.0), axis=-1)
    / cds.volume.values[None, :]
    / 1e6
)  # [cm^-3]
nc = ntot - nr - na

cds_aerosol = xr.DataArray(
    np.asarray(ak.to_numpy(na)),
    name="number conc aerosol droplets",
    dims=["time", "height"],
    attrs={"units": "cm^-3"},
)
cds_aerosol = cds_aerosol.assign_coords(height=cds.height)
cds_aerosol = cds_aerosol.assign_coords(time=cds.time)

cds_cloud = xr.DataArray(
    np.asarray(ak.to_numpy(nc)),
    name="number conc cloud droplets",
    dims=["time", "height"],
    attrs={"units": "cm^-3"},
)
cds_cloud = cds_cloud.assign_coords(height=cds.height)
cds_cloud = cds_cloud.assign_coords(time=cds.time)

cds_rain = xr.DataArray(
    np.asarray(ak.to_numpy(nr)),
    name="number conc rain droplets",
    dims=["time", "height"],
    attrs={"units": "cm^-3"},
)
cds_rain = cds_rain.assign_coords(height=cds.height)
cds_rain = cds_rain.assign_coords(time=cds.time)

# %% sanity check numconc
(cds_numconc - ak.to_numpy(ntot)).plot(y="height")
# %%
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
cds_aerosol.plot(vmin=0.0, vmax=60, ax=axs[0], y="height")
pds_aerosol.plot(vmin=0.0, vmax=60, ax=axs[1], y="height")
axs[0].set_title("CLEO")
axs[1].set_title("PySDM")
plt.ylim(bottom=0.0)
plt.tight_layout()
plt.show()

fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
cds_cloud.plot(vmin=0.0, vmax=60, ax=axs[0], y="height")
pds_cloud.plot(vmin=0.0, vmax=60, ax=axs[1], y="height")
plt.ylim(bottom=0.0)
plt.tight_layout()
plt.show()

fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
cds_rain.plot(vmin=0.0, vmax=0.3, ax=axs[0], y="height")
pds_rain.plot(vmin=0.0, vmax=0.3, ax=axs[1], y="height")
plt.ylim(bottom=0.0)
plt.tight_layout()
plt.show()
# %% aerosol
for time in [0, 100, 500]:
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
    (cds_aerosol - pds_aerosol).sel(time=time, method="nearest").plot(
        ax=axs[0], y="height"
    )
    cds_aerosol.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    pds_aerosol.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    axs[0].set_title("CLEO - PySDM")
    axs[1].set_title("CLEO and PySDM")
    plt.ylim(bottom=0.0)
    plt.tight_layout()
    plt.show()

# %% cloud
for time in [0, 100, 500]:
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
    (cds_cloud - pds_cloud).sel(time=time, method="nearest").plot(ax=axs[0], y="height")
    cds_cloud.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    pds_cloud.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    axs[0].set_title("CLEO - PySDM")
    axs[1].set_title("CLEO and PySDM")
    plt.ylim(bottom=0.0)
    plt.tight_layout()
    plt.show()
# %% rain
for time in [700, 1000, 1500]:
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 5))
    (cds_rain - pds_rain).sel(time=time, method="nearest").plot(ax=axs[0], y="height")
    cds_rain.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    pds_rain.sel(time=time, method="nearest").plot(ax=axs[1], y="height")
    axs[0].set_title("CLEO - PySDM")
    axs[1].set_title("CLEO and PySDM")
    plt.ylim(bottom=0.0)
    plt.tight_layout()
    plt.show()
# %%
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(5, 8))
(cds_aerosol - pds_aerosol).plot(ax=axs[0], y="height")
axs[0].set_title("CLEO - PySDM")
plt.ylim(bottom=0.0)

(cds_cloud - pds_cloud).plot(ax=axs[1], y="height")
(cds_rain - pds_rain).plot(ax=axs[2], y="height")

plt.ylim(bottom=0.0)
plt.tight_layout()
plt.show()
# %%
