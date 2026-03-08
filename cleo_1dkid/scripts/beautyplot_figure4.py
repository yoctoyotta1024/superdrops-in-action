"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: beautyplot_cleo_1dkid_ensembles.py
Project: scripts
Created Date: Monday 28th July 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Plots for CLEO paper 2 for multiple ensembles of runs of the
1-D kid test case datasets from CLEO SDM.

NOTE: script assumes setup .txt files and .zarr datasets for each ensemble are
        all in the same directory and all files in that directory are desired
"""

# %%
import argparse
import glob
import os
import sys
import awkward as ak
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.gridspec import GridSpec

parser = argparse.ArgumentParser()
parser.add_argument(
    "--binpath",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/bin/fullscheme",
    help="path to CLEO output .zarr and .txt datasets of ensemble",
)
parser.add_argument(
    "--grid_filename",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/share/dimlessGBxboundaries.dat",
    help="path to gridbox boundaries binary file",
)
parser.add_argument(
    "--figpath",
    type=Path,
    default="/home/m/m300950/superdrops-in-action/plots",
    help="path to save figures in",
)
parser.add_argument(
    "--path2cleo",
    type=Path,
    default="/home/m/m300950/CLEO",
    help="path to pySD python module",
)
args = parser.parse_args()
# %%
sys.path.append(str(args.path2cleo))  # imports from pySD
sys.path.append(
    str(args.path2cleo / "examples" / "exampleplotting")
)  # imports from example plots package
from pySD.sdmout_src import pyzarr, pysetuptxt, pygbxsdat  # from plotssrc import pltsds


# %%
def unflatten_superdrops(rawdata, raggedcount, nsupers):
    sdarr = ak.unflatten(rawdata, raggedcount)
    sdarr = ak.to_regular(ak.unflatten(sdarr, ak.flatten(nsupers), axis=1), axis=1)
    return sdarr


def superdrops_variable_ensemble(ensemble_ds, var):
    sources = [xr.open_dataset(s, engine="zarr") for s in ensemble_ds.sources.values]
    data = {
        e: unflatten_superdrops(
            ds[var].values,
            ds.raggedcount.values,
            ds.nsupers.values,
        )
        for e, ds in zip(ensemble_ds.ensemble.values, sources)
    }
    return data


def incloud_numconc(ds, xi, radius, assign_to_dataset=False):
    numconc_d = {}
    for e in ds.ensemble.values:
        mask_incloud_lwc = (ds.sel(ensemble=e).lwc / 1000 > 1e-5).values
        v = ak.where(mask_incloud_lwc[:, :, None], xi[e], np.nan)
        xi_incloud = ak.where(radius[e] > 1, v, np.nan)

        sum_xi_incloud = ak.to_numpy(ak.sum(xi_incloud, axis=2), allow_missing=False)
        numconc_d[e] = sum_xi_incloud / ds.volume.values[None, :] / 1e6

    numconc_d = xr.DataArray(
        list(numconc_d.values()),
        name="numconc_d",
        dims=["ensemble", "time", "height"],
        attrs={"units": "cm^-3"},
    )

    if assign_to_dataset:
        ds = ds.assign(**{numconc_d.name: numconc_d})

    return ds, numconc_d


def mass_water(radius, msol, RHO_L, RHO_SOL):
    msol_kg = msol / 1000  # convert msol from grams to Kg
    radius_m = radius / 1e6  # convert microns to m

    v_sol = msol_kg / RHO_SOL
    v_w = 4 / 3.0 * np.pi * (radius_m**3) - v_sol

    m_water = RHO_L * v_w
    m_water_corrected = np.where(m_water <= 0.0, 0.0, m_water)

    return m_water_corrected  # [kg]


def volume_diameter(xi, m_water, RHO_L):
    """xi and m_water here are single member of ensemble not entire dictionary"""
    weighted_water = ak.to_numpy(
        ak.sum((m_water) ** (4 / 3) * xi, axis=2), allow_missing=False
    )
    sum_water = ak.to_numpy(ak.sum(m_water * xi, axis=2), allow_missing=False)

    dvol = (6.0 / np.pi / RHO_L) ** (1 / 3) * weighted_water / sum_water

    return dvol


def mass_weighted_mean_volume_diameter(ds, xi, m_water, RHO_L, assign_to_dataset=False):
    dvol = {}
    for e in ds.ensemble.values:
        dvol[e] = volume_diameter(xi[e], m_water[e], RHO_L) * 1e6  # [microns]

    dvol = xr.DataArray(
        list(dvol.values()),
        name="dvol",
        dims=["ensemble", "time", "height"],
        attrs={"units": "micro-m", "long_name": "mass weighted mean volume diameter"},
    )

    if assign_to_dataset:
        ds = ds.assign(**{dvol.name: dvol})

    return ds, dvol


def volume_diameter_stddev(xi, m_water, dvol, RHO_L):
    """xi and m_water here are single member of ensemble not entire dictionary"""

    sumxi = ak.to_numpy(ak.sum(xi, axis=2), allow_missing=False)
    di = (6.0 / np.pi / RHO_L * m_water) ** (1 / 3)
    diffssqrd = xi * (di - dvol.values[:, :, None]) ** 2
    sumdiffssqrd = ak.to_numpy(ak.sum(diffssqrd, axis=2), allow_missing=False)

    sigma = (1 / (sumxi - 1) * sumdiffssqrd) ** (1 / 2)

    return sigma


def mass_weighted_volume_diameter_stddev(
    ds, xi, m_water, RHO_L, assign_to_dataset=False
):
    sigma = {}
    for e in ds.ensemble.values:
        dvol_m = ds.sel(ensemble=e).dvol / 1e6
        sigma[e] = (
            volume_diameter_stddev(xi[e], m_water[e], dvol_m, RHO_L) * 1e6
        )  # [microns]

    sigma = xr.DataArray(
        list(sigma.values()),
        name="dvol_sigma",
        dims=["ensemble", "time", "height"],
        attrs={
            "units": "micro-m",
            "long_name": "standard deviation of mass weighted volume diameter",
        },
    )

    if assign_to_dataset:
        ds = ds.assign(**{sigma.name: sigma})

    return ds, sigma


def variable_at_lwcmax(ds, array):
    height_lwcmax = ds.lwc.idxmax(dim="height")
    atmax = array.sel(height=height_lwcmax)
    return atmax


# %%
def rho(press, temp, qvap):
    p = press * 100  # [Pa]
    qv = qvap / 1000  # [kg/kg]
    Rd = 287.0027
    Rv = 461.52998157941937
    Rq = (Rv * qv + Rd) / (1 + qv)
    return p / Rq / temp


def mean_stddev(arr, dim="ensemble"):
    """return mean +- stddev over dimension of array (default over ensemble)"""
    mean = arr.mean(dim=dim)
    stddev = arr.std(dim=dim) / (arr[dim].size ** (0.5))
    return mean, -stddev, +stddev


def plot_vertical_error_shading(
    ax,
    y,
    mean,
    lower_error,
    upper_error,
    plot_mean=False,
    shading_kwargs={"alpha": 0.3, "color": "pink"},
    mean_kwargs={"color": "black"},
):
    ax.fill_betweenx(y, mean + lower_error, mean + upper_error, **shading_kwargs)
    if plot_mean:
        ax.plot(mean, y, **mean_kwargs)


def plot_horizontal_error_shading(
    ax,
    x,
    mean,
    lower_error,
    upper_error,
    plot_mean=False,
    shading_kwargs={"alpha": 0.3, "color": "pink"},
    mean_kwargs={"color": "black"},
):
    ax.fill_between(x, mean + lower_error, mean + upper_error, **shading_kwargs)
    if plot_mean:
        ax.plot(x, mean, **mean_kwargs)


def save_figure(fig, savename):
    if savename.parent.is_dir():
        fig.savefig(savename, dpi=800, bbox_inches="tight", facecolor="w")
    else:
        print("not saving figure, no existing directory provided")


# %%
assert args.binpath.is_dir()
setupfiles = glob.glob(os.path.join(args.binpath, "*.txt"))
datasets = glob.glob(os.path.join(args.binpath, "*.zarr"))
print(setupfiles)
print(datasets)
assert setupfiles and datasets, "no setupfiles or datasets found"
print(f"Setup and datasets found in\n{args.binpath}:")
print(", ".join([Path(s).name for s in setupfiles]))
print(", ".join([Path(s).name for s in datasets]))
# %%
config = pysetuptxt.get_config(setupfiles[0], nattrs=3, isprint=False)
consts = pysetuptxt.get_consts(setupfiles[0], isprint=False)
gbxs = pygbxsdat.get_gridboxes(args.grid_filename, consts["COORD0"], isprint=False)
time = pyzarr.get_time(datasets[0])

precip_rolling_window = 100  # [number of timesteps, 1 timestep~1.25s]


# %%
def drop_superdroplets(ds):
    superdroplets = [
        "sdId",
        "sdgbxindex",
        "coord3",
        "coord1",
        "coord2",
        "msol",
        "radius",
        "xi",
    ]
    return ds.drop_vars(superdroplets)


ds = xr.open_mfdataset(
    datasets,
    engine="zarr",
    combine="nested",
    concat_dim="ensemble",
    preprocess=drop_superdroplets,
)
ensemble_coord = dict(ensemble=("ensemble", [str(Path(d).stem) for d in datasets]))
ds = ds.assign_coords(ensemble_coord)

arr = xr.DataArray(
    datasets,
    name="sources",
    dims=["ensemble"],
    attrs={"long_name": "path to dataset of each ensemble member"},
)
ds = ds.assign(**{arr.name: arr})

ds = ds.rename_dims({"gbxindex": "height"})
ds = ds.drop_vars("gbxindex")
ds = ds.assign_coords(height=("height", gbxs["zfull"]))
ds["height"].attrs["units"] = "m"

arr = xr.DataArray(
    gbxs["gbxvols"][0, 0, :], name="volume", dims="height", attrs={"units": "m^3"}
)
ds = ds.assign(**{arr.name: arr})

arr = xr.DataArray(
    ds.massmom0 / ds.volume / 1e6,
    name="numconc",
    dims=["ensemble", "time", "height"],
    attrs={"units": "cm^-3"},
)
ds = ds.assign(**{arr.name: arr})

arr = xr.DataArray(
    ds.massmom1 / ds.volume,
    name="lwc",
    dims=["ensemble", "time", "height"],
    attrs={"units": "g m^-3"},
)
ds = ds.assign(**{arr.name: arr})

arr = xr.DataArray(
    ds.lwc.integrate(coord="height") / 1000,
    name="lwp",
    dims=["ensemble", "time"],
    attrs={"units": "Kg m^-2"},
)
ds = ds.assign(**{arr.name: arr})

surface = ds.height.sel(height=0.0, method="nearest")
arr = xr.DataArray(
    ds.precip.sel(height=surface, method="nearest")
    * 1000
    / (config["OBSTSTEP"] / 3600),
    name="surfprecip_rate",
    dims=["ensemble", "time"],
    attrs={
        "units": "mm hr^-1",
        "long_name": "surface precipitation rate",
    },
)
ds = ds.assign(**{arr.name: arr})

arr = xr.DataArray(
    ds.surfprecip_rate.rolling(time=precip_rolling_window, center=True).mean(),
    name="surfprecip_rolling",
    dims=["ensemble", "time"],
    attrs={
        "units": "mm hr^-1",
        "long_name": "rolling mean of surface precipitation rate",
    },
)
ds = ds.assign(**{arr.name: arr})


ds

# %%
print(f"surface precipitation identified at {surface.values}m")
# %% (slow) superdroplet variables across ensemble
xi = superdrops_variable_ensemble(ds, "xi")
radius = superdrops_variable_ensemble(ds, "radius")
msol = superdrops_variable_ensemble(ds, "msol")
m_water = {
    e: mass_water(radius[e], msol[e], consts["RHO_L"], consts["RHO_SOL"])
    for e in ds.ensemble.values
}
ds = incloud_numconc(ds, xi, radius, assign_to_dataset=True)[0]
ds = mass_weighted_mean_volume_diameter(
    ds, xi, m_water, consts["RHO_L"], assign_to_dataset=True
)[0]
ds = mass_weighted_volume_diameter_stddev(
    ds, xi, m_water, consts["RHO_L"], assign_to_dataset=True
)[0]
ds


# %%
def plot_hill_figure4(ds):
    fig = plt.figure(figsize=(10, 5))
    gs = GridSpec(
        2,
        6,
        figure=fig,
        hspace=0.3,
        wspace=0.9,
    )

    axs = [
        fig.add_subplot(gs[0, 0:2]),
        fig.add_subplot(gs[0, 2:4]),
        fig.add_subplot(gs[0, 4:6]),
        fig.add_subplot(gs[1, 1:3]),
        fig.add_subplot(gs[1, 3:5]),
    ]

    cloudbase = 700  # height of cloud base [m]

    # nc0 = ds.numconc.sel(time=0, method="nearest").mean().values
    # fig.suptitle("Fig. 4, N$_a$ = {:.0f} ".format(nc0) + "cm$^{-3}$")

    mean, err1, err2 = mean_stddev(ds.lwp, dim="ensemble")
    plot_horizontal_error_shading(
        axs[0],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "blue"},
        mean_kwargs={"color": "blue"},
        plot_mean=True,
    )
    axs[0].set_ylabel("LWP / kg m$^{-2}$")
    axs[0].set_ylim(bottom=0)

    # height_maxlwc = ds.lwc.idxmax(dim="height")
    mean, err1, err2 = mean_stddev(ds.surfprecip_rate, dim="ensemble")
    plot_horizontal_error_shading(
        axs[1],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "blue"},
        mean_kwargs={"color": "blue", "linewidth": 0.3},
        plot_mean=True,
    )
    axs[1].set_ylabel(f"surface precip / mm hr$^{-1}$")
    axs[1].set_ylim(bottom=0, top=6.5)

    mean_numconc_d = ds.numconc_d.mean(dim="height")
    mean, err1, err2 = mean_stddev(mean_numconc_d, dim="ensemble")
    plot_horizontal_error_shading(
        axs[2],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "blue"},
        mean_kwargs={"color": "blue"},
        plot_mean=True,
    )
    axs[2].set_ylabel("mean N$_d$ / cm$^{-3}$")
    axs[2].set_ylim(bottom=0)

    dvol_atcloudbase = ds.dvol.sel(height=cloudbase, method="nearest")
    mean, err1, err2 = mean_stddev(dvol_atcloudbase, dim="ensemble")
    plot_horizontal_error_shading(
        axs[3],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "blue"},
        mean_kwargs={"color": "blue"},
        plot_mean=True,
    )
    axs[3].set_ylabel("D$_{vol}$ / \u03BCm")
    axs[3].set_yscale("log")
    axs[3].set_ylim(bottom=10)  # [10, 1175]

    sigma_atcloudbase = ds.dvol_sigma.sel(height=cloudbase, method="nearest")
    mean, err1, err2 = mean_stddev(sigma_atcloudbase, dim="ensemble")
    plot_horizontal_error_shading(
        axs[4],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "blue"},
        mean_kwargs={"color": "blue"},
        plot_mean=True,
    )
    axs[4].set_ylabel("\u03C3 / \u03BCm")
    axs[4].set_yscale("log")
    axs[4].set_ylim(bottom=1)  # [1, 1100]

    axs[0].set_xlim([60, 3600])
    axs[-1].set_xlabel("time / s")

    for ax in axs:
        ax.spines[["top", "right"]].set_visible(False)

    return fig


fig = plot_hill_figure4(ds)

if args.figpath.is_dir():
    savename = args.figpath / "hill_figure4_ensembles.pdf"
    fig.savefig(savename, dpi=800, bbox_inches="tight", facecolor="w")
else:
    print("not saving figure, no existing directory provided")

plt.show()
