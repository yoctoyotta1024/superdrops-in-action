"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: quickplot_cleo_1dkid.py
Project: scripts
Created Date: Monday 14th July 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Monday 14th July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Quickplots of 1-D kid test case dataset from CLEO SDM.

NOTE: script assumes setup .txt file and .zarr dataset are in same directory
"""

# %%
import argparse
import awkward as ak
import random
import sys
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--binpath",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/bin/fullscheme",
    help="path to CLEO run output files",
)
parser.add_argument(
    "--grid_filename",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/share/dimlessGBxboundaries.dat",
    help="path to gridbox boundaries binary file",
)
parser.add_argument(
    "--figpath",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/build/bin/fullscheme",
    help="path to save figures in",
)
parser.add_argument(
    "--run_name",
    type=str,
    default="cleo_condevap_only",
    help="label for test case",
)
parser.add_argument(
    "--path2cleo",
    type=Path,
    default="/home/m/m300950/CLEO/",
    help="path to pySD python module",
)
args = parser.parse_args()

dataset = args.binpath / "sol.zarr"
setupfile = args.binpath / "setup.txt"
# %%
sys.path.append(str(args.path2cleo))  # imports from pySD
sys.path.append(
    str(args.path2cleo) + "/examples" "/exampleplotting"
)  # imports from example plots package
from pySD.sdmout_src import pyzarr, pysetuptxt, pygbxsdat  # from plotssrc import pltsds

# %%
config = pysetuptxt.get_config(setupfile, nattrs=3, isprint=True)
consts = pysetuptxt.get_consts(setupfile, isprint=True)
gbxs = pygbxsdat.get_gridboxes(args.grid_filename, consts["COORD0"], isprint=True)

time = pyzarr.get_time(dataset)
config["ntime"] = len(time.secs)
superdrops = pyzarr.get_supers(dataset, consts)
totnsupers = pyzarr.get_totnsupers(dataset)

ntime = time.secs.shape[0]
massmoms = pyzarr.get_massmoms(dataset, ntime, gbxs["ndims"])
rainmassmoms = pyzarr.get_rainmassmoms(dataset, ntime, gbxs["ndims"])


def reshape_superdrops_pergbx(data, nsupers_values):
    data_pergbx = ak.unflatten(data, ak.flatten(nsupers_values), axis=1)
    return data_pergbx


# %%
numconc = massmoms.mom0 / gbxs["gbxvols"][None, :, :, :] / 1e6  # [cm^-3]
lwcontent = massmoms.mom1 / gbxs["gbxvols"][None, :, :, :]  # [g m^-3]
lwpath = lwcontent * (gbxs["zhalf"][-1] - gbxs["zhalf"][0]) / 1000  # [kg m^-2]

incloudmask = lwcontent[:, 0, 0, :] > 1e-5 * 1000
lwpmax_idxs = np.argmax(lwpath, axis=-1, keepdims=True)
t10_idx = np.argmin(abs(time.mins - 10))
rhol = consts["RHO_L"]  # kg/m^3
print(f"time closest to 10mins: {time.mins[t10_idx]}mins")

# %%
ds = xr.open_dataset(dataset, engine="zarr")
ds = ds.rename_dims({"gbxindex": "height"})
ds = ds.drop_vars("gbxindex")
ds = ds.assign_coords(height=("height", gbxs["zfull"]))
ds["height"].attrs["units"] = "m"
ds

# %%
fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
time2plot = 0  # [s]

ds.press.sel(time=time2plot, method="nearest").T.plot(ax=axs[0, 0], y="height")
ds.temp.sel(time=time2plot, method="nearest").T.plot(ax=axs[0, 1], y="height")
ds.wvel.sel(time=time2plot, method="nearest").T.plot(ax=axs[0, 2], y="height")
ds.qvap.sel(time=time2plot, method="nearest").T.plot(ax=axs[1, 0], y="height")
ds.qcond.sel(time=time2plot, method="nearest").T.plot(ax=axs[1, 1], y="height")

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
xtlim = 15 * 60  # [s]

ds.wvel.T.plot(ax=axs[0])
axs[0].set_xlim([0, xtlim])

axs[1].plot(time.secs, ds.wvel)
axs[1].set_xlabel("time /s")
axs[1].set_ylabel(ds.wvel.name + " / " + ds.wvel.units)
axs[1].set_xlim([0, xtlim])

times = [3, 6, 9, 12]  # [min]
for t in times:
    wsel = ds.wvel.sel(time=t * 60, method="nearest")
    print(
        f"time={wsel.time.values/60}min, (max,min) wvel =({wsel.max().values, wsel.min().values})"
    )
    wsel.plot(ax=axs[2], label=f"time={t}min", y="height")
axs[2].legend()
axs[2].set_title("")

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

ds.press.T.plot(ax=axs[0, 0])
ds.temp.T.plot(ax=axs[0, 1])
ds.totnsupers.plot(ax=axs[0, 2])
ds.qvap.T.plot(ax=axs[1, 0])
ds.qcond.T.plot(ax=axs[1, 1])

fig.tight_layout()
plt.show()

# %%
nsample = 50
superdrops.attach_time(time.mins, "min", do_reshape=True, var4reshape="sdId")

sample_population = list(np.unique(ak.flatten(superdrops.sdId())))
ids2plot = random.sample(sample_population, nsample)
attrs = ["time", "radius", "xi", "msol", "coord3"]
sample = superdrops.sample("sdId", sample_values=ids2plot, variables2sample=attrs)


# %%
def plot_randomsample_superdrops(sample):
    import warnings

    fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(12, 8))
    fig.suptitle("Time Evolution of a Random Sample of Superdroplets")

    sample_time = sample.time()

    for a, attr in enumerate(["radius", "xi", "msol", "coord3"]):
        data = sample[attr]
        if len(ak.flatten(data)) == 0:
            warnings.warn(f"no data for {attr} found. Not plotting {attr}")
            continue
        for i in range(len(data)):
            t = sample_time[i]
            d = data[i]
            axs[0, a].plot(
                t, d, linewidth=0.8, markersize=0.2
            )  # plot each SD seperately

    axs[0, 0].set_yscale("log")
    axs[0, 0].set_ylabel("radius, r /\u03BCm")
    axs[0, 1].set_ylabel("multiplicity, \u03BE")
    axs[0, 2].set_ylabel("solute mass, msol /g")
    axs[0, 3].set_ylabel("zcoord /km")
    for ax in axs[0, :]:
        ax.set_xlabel("time /min")
        ax.set_xlim([0, 1])

    for i in range(len(sample["radius"])):
        r = sample["radius"][i]
        crd3 = sample["coord3"][i]
        axs[1, 0].plot(
            r, crd3, linewidth=0.8, markersize=0.2
        )  # plot each SD seperately
    axs[1, 0].set_xscale("log")
    axs[1, 0].set_ylabel("zcoord /km")
    axs[1, 0].set_xlabel("radius, r /\u03BCm")

    fig.tight_layout()

    return fig, axs, sample


fig, axs, sample = plot_randomsample_superdrops(sample)
plt.show()

# %%
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))

ds.qvap.T.plot(ax=axs[0, 0])
ds.qcond.T.plot(ax=axs[1, 0])

times = [3, 6, 9, 12]  # [min]
for t in times:
    qvsel = ds.qvap.sel(time=t * 60, method="nearest")
    print(
        f"time={qvsel.time.values/60}min, (max,min) qvap =({qvsel.max().values, qvsel.min().values})"
    )
    qvsel.plot(ax=axs[0, 1], label=f"time={t}min", y="height")

    qcsel = ds.qcond.sel(time=t * 60, method="nearest")
    print(
        f"time={qcsel.time.values/60}min, (max,min) qcond =({qcsel.max().values, qcsel.min().values})"
    )
    qcsel.plot(ax=axs[1, 1], label=f"time={t}min", y="height")
axs[0, 1].legend()
axs[0, 1].set_title("")
axs[1, 1].legend()
axs[1, 1].set_title("")

fig.tight_layout()
plt.show()
# %%
plt.title("in-cloud mask")
plt.contourf(ds.time, ds.height, incloudmask.T)
plt.xlabel("time /s")
plt.ylabel("height /m")
plt.show()
# %%
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

axs[0].set_title("LWP")
contf = axs[0].contourf(ds.time, ds.height, lwpath[:, 0, 0, :].T)
plt.colorbar(contf, ax=axs[0])

lwpmax1 = np.amax(lwpath, axis=-1)[:, 0, 0]
lwpmax2 = np.take_along_axis(lwpath, lwpmax_idxs, axis=-1)[:, 0, 0, 0]
axs[1].set_title("max LWP")
axs[1].plot(time.secs, lwpath[:, 0, 0, :], linewidth=0.8)
axs[1].plot(time.secs, lwpmax1, color="k")
axs[1].plot(time.secs, lwpmax2, color="lightgray", linestyle=":")
axs[1].set_ylabel("LWP / kg m$^{-2}$")
axs[1].set_xlabel("time / s")

lwpmax_height = ds.height.values[lwpmax_idxs[:, 0, 0, 0]]
axs[2].set_title("height of maximum LWP")
axs[2].plot(time.secs, lwpmax_height, linewidth=0.8)
axs[2].set_ylabel("height / m")
axs[2].set_xlabel("time / s")

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(12, 8))

_xi = reshape_superdrops_pergbx(superdrops["xi"], ds.nsupers.values)
xi_incloud = ak.where(incloudmask[:, :, None], _xi, np.nan)
_sumxi_incloud = ak.to_numpy(ak.sum(xi_incloud, axis=2), allow_missing=False)
numconc_d = _sumxi_incloud / gbxs["gbxvols"][None, 0, 0, :] / 1e6
contf = axs[0, 0].contourf(ds.time, ds.height, numconc_d.T)
plt.colorbar(contf, ax=axs[0, 0], label="in-cloud numconc / cm$^{-3}$")

_m_water = superdrops.m_water(superdrops.radius(), superdrops.msol()) / 1000  # [kg]
_m_water = reshape_superdrops_pergbx(_m_water, ds.nsupers.values)
_m_water_corrected = np.where(_m_water <= 0.0, np.nan, _m_water)
_dvol_mean = ak.to_numpy(
    ak.mean(_m_water_corrected, weight=_xi, axis=2), allow_missing=False
)
_dvol = (6.0 / np.pi / rhol * _dvol_mean) ** (1 / 3)
contf = axs[1, 0].contourf(ds.time, ds.height, _dvol.T * 1e6)
plt.colorbar(contf, ax=axs[1, 0], label="unweighted D$_{vol}$ / \u03BCm")

_weighted_water_corrected = ak.to_numpy(
    ak.sum((_m_water_corrected) ** (4 / 3) * _xi, axis=2), allow_missing=False
)
_summ_water_corrected = ak.to_numpy(
    ak.sum(_m_water_corrected * _xi, axis=2), allow_missing=False
)
_wghtd_dvol = (
    (6.0 / np.pi / rhol) ** (1 / 3) * _weighted_water_corrected / _summ_water_corrected
)
contf = axs[1, 1].contourf(ds.time, ds.height, _wghtd_dvol.T * 1e6)
plt.colorbar(contf, ax=axs[1, 1], label="D$_{vol}$ / \u03BCm")

_sumxi = ak.to_numpy(ak.sum(_xi, axis=2), allow_missing=False)
_di = (6.0 / np.pi / rhol * _m_water_corrected) ** (1 / 3)
_diffssqrd = _xi * (_di - _wghtd_dvol) ** 2
_sumdiffssqrd = ak.to_numpy(ak.sum(_diffssqrd, axis=2), allow_missing=False)
_wghtd_sigma = (1 / (_sumxi - 1) * _sumdiffssqrd) ** (1 / 2)
contf = axs[0, 1].contourf(ds.time, ds.height, _wghtd_sigma.T * 1e6)
plt.colorbar(contf, ax=axs[0, 1], label="\u03C3 / \u03BCm")

# axs[0,0].set_xscale("log")
axs[0, 0].set_xlim([60, ds.time[-1]])
axs[1, 0].set_xlabel("time / s")
axs[1, 1].set_xlabel("time / s")
axs[0, 0].set_ylabel("height / m")
axs[1, 0].set_ylabel("height / m")

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=3, ncols=2, sharex=True)
_xi = reshape_superdrops_pergbx(superdrops["xi"], ds.nsupers.values)
_msol = reshape_superdrops_pergbx(superdrops["msol"], ds.nsupers.values) / 1000  # [kg]
_m_water = superdrops.m_water(superdrops.radius(), superdrops.msol()) / 1000  # [kg]
_m_water = reshape_superdrops_pergbx(_m_water, ds.nsupers.values)
_mass = superdrops.mass(superdrops.radius(), superdrops.msol()) / 1000  # [kg]
_mass = reshape_superdrops_pergbx(_mass, ds.nsupers.values)

_summ_water = ak.to_numpy(ak.sum(_m_water * _xi, axis=2), allow_missing=False)
_summass = ak.to_numpy(ak.sum(_mass * _xi, axis=2), allow_missing=False)
_summsol = ak.to_numpy(ak.sum(_msol * _xi, axis=2), allow_missing=False)

axs[0, 0].set_title("totmass - msol - m_water")
contf = axs[0, 0].contourf(((_summass - (_summ_water + _summsol)) / _summass).T)
plt.colorbar(contf, ax=axs[0, 0])

axs[1, 0].set_title("totmass - massmom1")
contf = axs[1, 0].contourf(((_summass - massmoms.mom1[:, 0, 0, :] * 1000) / _summass).T)
plt.colorbar(contf, ax=axs[1, 0])

axs[2, 0].set_title("totxi - massmom0")
_sumxi = ak.to_numpy(ak.sum(_xi, axis=2), allow_missing=False)
contf = axs[2, 0].contourf(((_sumxi - massmoms.mom0[:, 0, 0, :]) / _summass).T)
plt.colorbar(contf, ax=axs[2, 0])

axs[0, 1].set_title("m_water_corrected - m_water")
_m_water_corrected = np.where(_m_water <= 0.0, np.nan, _m_water)
_summ_water_corrected = ak.to_numpy(
    ak.sum(_m_water_corrected * _xi, axis=2), allow_missing=False
)
contf = axs[0, 1].contourf((_summ_water_corrected - _summ_water).T)
plt.colorbar(contf, ax=axs[0, 1])

axs[1, 1].set_title("dvol - dvol1 (unweighted)")
_dvol_mean = ak.to_numpy(
    ak.mean(_m_water_corrected, weight=_xi, axis=2), allow_missing=False
)
_dvol = (6.0 / np.pi / rhol * _dvol_mean) ** (1 / 3)
dvol1 = (6.0 / np.pi / rhol * _summ_water_corrected / _sumxi) ** (1 / 3)
contf = axs[1, 1].contourf((_dvol - dvol1).T)
plt.colorbar(contf, ax=axs[1, 1])

axs[2, 1].set_title("dvol - dmean (unweighted)")
_radius = (
    reshape_superdrops_pergbx(superdrops["radius"], ds.nsupers.values) * 1e-6
)  # [m]
# dry_diam =  (6.0 / np.pi /  consts["RHO_SOL"]* _msol/1000 / _sumxi)**(1/3)
dvol2 = 2 * ak.to_numpy(ak.sum(_radius * _xi, axis=2), allow_missing=False) / _sumxi
contf = axs[2, 1].contourf((_dvol - dvol2).T)
plt.colorbar(contf, ax=axs[2, 1])

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(5, 10), sharex=True)

fig.suptitle("Fig. 4, N$_a$ = {:.0f} ".format(numconc[0, 0, 0, 0]) + "cm$^{-3}$")
islogx = False

lwpmax = np.take_along_axis(lwpath, lwpmax_idxs, axis=-1)[:, 0, 0, 0]
axs[0].set_title("(a)", loc="left")
axs[0].plot(time.secs, lwpmax, color="b")
axs[0].set_ylabel("LWP / kg m$^{-2}$")
axs[0].set_ylim(bottom=0)

_xi = reshape_superdrops_pergbx(superdrops["xi"], ds.nsupers.values)
xi_incloud = ak.where(incloudmask[:, :, None], _xi, np.nan)
sumxi_incloud = ak.to_numpy(ak.sum(xi_incloud, axis=2), allow_missing=False)
numconc_d = sumxi_incloud / gbxs["gbxvols"][None, 0, 0, :] / 1e6
mean_numconc_d = np.nan_to_num(np.nanmean(numconc_d, axis=1))
# axs[1].plot(time.secs, numconc_d, linewidth=0.8, alpha=0.3)
axs[1].plot(time.secs, mean_numconc_d, color="b")
axs[1].set_title("(d)", loc="left")
axs[1].set_ylabel("mean N$_d$ / cm$^{-3}$")
axs[1].set_ylim(bottom=0)

m_water = superdrops.m_water(superdrops.radius(), superdrops.msol()) / 1000  # [kg]
m_water = reshape_superdrops_pergbx(m_water, ds.nsupers.values)
m_water_corrected = np.where(m_water <= 0.0, np.nan, m_water)
dvol_mean = ak.to_numpy(
    ak.mean(m_water_corrected, weight=_xi, axis=2), allow_missing=False
)
dvol = (6.0 / np.pi / rhol * dvol_mean) ** (1 / 3)

weighted_water_corrected = ak.to_numpy(
    ak.sum((m_water_corrected) ** (4 / 3) * _xi, axis=2), allow_missing=False
)
summ_water_corrected = ak.to_numpy(
    ak.sum(m_water_corrected * _xi, axis=2), allow_missing=False
)
wghtd_dvol = (
    (6.0 / np.pi / rhol) ** (1 / 3) * weighted_water_corrected / summ_water_corrected
)

dvolmax = np.take_along_axis(dvol, lwpmax_idxs[:, 0, 0, :], axis=-1)[:, 0]
wghtd_dvolmax = np.take_along_axis(wghtd_dvol, lwpmax_idxs[:, 0, 0, :], axis=-1)[:, 0]
axs[2].plot(time.secs, dvolmax * 1e6, color="purple", linestyle="--")
axs[2].plot(time.secs, wghtd_dvolmax * 1e6, color="b", linestyle="--")
axs[2].set_title("(g)", loc="left")
axs[2].set_ylabel("D$_{vol}$ / \u03BCm")


sumxi = ak.to_numpy(ak.sum(_xi, axis=2), allow_missing=False)
di = (6.0 / np.pi / rhol * m_water_corrected) ** (1 / 3)
diffssqrd = _xi * (di - wghtd_dvol) ** 2
sumdiffssqrd = ak.to_numpy(ak.sum(diffssqrd, axis=2), allow_missing=False)
wghtd_sigma = (1 / (sumxi - 1) * sumdiffssqrd) ** (1 / 2)
wghtd_sigmamax = np.take_along_axis(wghtd_sigma, lwpmax_idxs[:, 0, 0, :], axis=-1)[:, 0]
axs[3].plot(time.secs, wghtd_sigmamax * 1e6, color="b")
axs[3].set_title("(j)", loc="left")
axs[3].set_yscale("log")
axs[3].set_ylabel("\u03C3 / \u03BCm")

if islogx:
    axs[0].set_xscale("log")
    axs[2].set_ylim([10, 70])
    axs[3].set_ylim([0.1, 50])
else:
    axs[2].set_yscale("log")
    axs[2].set_ylim([10, 1150])
    axs[3].set_ylim([1, 1050])
axs[0].set_xlim([60, 3600])
axs[-1].set_xlabel("time / s")

fig.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(5, 10), sharey=True)

fig.suptitle("Fig. 2, N$_a$ = {:.0f} ".format(numconc[0, 0, 0, 0]) + "cm$^{-3}$")

lwc_10mins = lwcontent[t10_idx, 0, 0]
axs[0].step(lwc_10mins, gbxs["zfull"], where="mid", color="b")
axs[0].set_title("(a)", loc="left")
axs[0].set_xlabel("LWC / g m$^{-3}$")

numconc_d_10mins = np.nan_to_num(numconc_d[t10_idx])
axs[1].step(numconc_d_10mins, gbxs["zfull"], where="mid", color="b")
axs[1].set_title("(d)", loc="left")
axs[1].set_xlabel("mean N$_d$ / cm$^{-3}$")

dvol_10mins = dvol[t10_idx, :]
wghtd_dvol_10mins = wghtd_dvol[t10_idx, :]
axs[2].step(
    dvol_10mins * 1e6, gbxs["zfull"], where="mid", linestyle="--", color="purple"
)
axs[2].step(
    wghtd_dvol_10mins * 1e6, gbxs["zfull"], where="mid", linestyle="--", color="b"
)
axs[1].set_title("(g)", loc="left")
axs[2].set_xlabel("D$_{vol}$ / \u03BCm")
axs[2].set_xscale("log")
axs[2].set_xlim([10, 100])

wghtd_sigma_10mins = wghtd_sigma[t10_idx, :]
plt.step(wghtd_sigma_10mins * 1e6, gbxs["zfull"], where="mid", color="b")
axs[1].set_title("(j)", loc="left")
plt.xlabel("\u03C3 / \u03BCm")
plt.xscale("log")
plt.xlim([0.1, 100])

axs[0].set_ylim([0, 3000])
for ax in axs:
    ax.set_ylabel("height / m")

fig.tight_layout()
plt.show()
# %%
