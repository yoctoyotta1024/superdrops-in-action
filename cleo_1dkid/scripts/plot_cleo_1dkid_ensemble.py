"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: plot_cleo_1dkid_ensemble.py
Project: scripts
Created Date: Monday 14th July 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Plots ensemble of runs of the 1-D kid test case datasets from CLEO SDM.

NOTE: script assumes setup .txt files and .zarr datasets for ensemble are
        all in the same directory and all files in that directory are desired
"""

# %%
import argparse
import glob
import os
import sys
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--binpath",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/bin/fullscheme/",
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
    default="/home/m/m300950/superdrops-in-action/plots/fullscheme",
    help="path to save figures in",
)
parser.add_argument(
    "--path2cleo",
    type=Path,
    default="/home/m/m300950/CLEO/",
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


# %%
assert args.binpath.is_dir()
setupfiles = glob.glob(os.path.join(args.binpath, "*.txt"))
datasets = glob.glob(os.path.join(args.binpath, "*.zarr"))
assert setupfiles and datasets, "no setupfiles or datasets found"
print(f"Setup and datasets found in\n{args.binpath}:")
print(", ".join([Path(s).name for s in setupfiles]))
print(", ".join([Path(s).name for s in datasets]))
# %%
config = pysetuptxt.get_config(setupfiles[0], nattrs=3, isprint=False)
consts = pysetuptxt.get_consts(setupfiles[0], isprint=False)
gbxs = pygbxsdat.get_gridboxes(args.grid_filename, consts["COORD0"], isprint=False)
time = pyzarr.get_time(datasets[0])
# %%
ds = xr.open_mfdataset(datasets, engine="zarr", combine="nested", concat_dim="ensemble")
ensemble_coord = dict(ensemble=("ensemble", [str(Path(d).stem) for d in datasets]))
ds = ds.assign_coords(ensemble_coord)

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

ds


# %%
def rho(press, temp, qvap):
    p = press * 100  # [Pa]
    qv = qvap / 1000  # [kg/kg]
    Rd = 287.0027
    Rv = 461.52998157941937
    Rq = (Rv * qv + Rd) / (1 + qv)
    return p / Rq / temp


# %%
def plot_vertical_profiles_timeslice(ds, time2plot):
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
    axs = axs.flatten()
    data = {}
    for v, var in enumerate(["press", "temp", "qvap", "wvel", "qcond"]):
        mean, err1, err2 = mean_stddev(ds[var], dim="ensemble")
        m2plt = mean.sel(time=time2plot, method="nearest")
        plot_vertical_error_shading(
            axs[v],
            ds.height,
            m2plt,
            err1.sel(time=time2plot, method="nearest"),
            err2.sel(time=time2plot, method="nearest"),
            plot_mean=False,
        )
        m2plt.plot(ax=axs[v], y="height", color="k")
        axs[v].set_xlabel(f"{ds[var].name} / {ds[var].units}")
        axs[v].set_ylabel(f"{ds.height.name} / {ds.height.units}")
        data[var] = m2plt

    rho2plt = rho(data["press"], data["temp"], data["qvap"])
    rho2plt.plot(ax=axs[-1], y="height", color="k")
    axs[-1].set_xlabel("rho / kg m$^{-3}$")
    axs[-1].set_ylabel(f"{ds.height.name} / {ds.height.units}")

    fig.tight_layout()


time2plot = 0  # [s]
plot_vertical_profiles_timeslice(ds, time2plot)
plt.show()


# %%
def plot_qvap_qcond(ds, times4xsection):
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))

    for v, var in enumerate(["qvap", "qcond"]):
        mean, err1, err2 = mean_stddev(ds[var], dim="ensemble")
        mean.T.plot(ax=axs[v, 0], cmap="Blues")
        axs[v, 0].set_xlim([0, 1500])
        axs[v, 0].set_ylabel("height / m")
        axs[v, 0].set_xlabel("time / s")

        for t, c in times4xsection.items():
            m2plt = mean.sel(time=t, method="nearest")
            e1, e2 = (
                err1.sel(time=t, method="nearest"),
                err2.sel(time=t, method="nearest"),
            )
            plot_vertical_error_shading(
                axs[v, 1],
                ds.height,
                m2plt,
                e1,
                e2,
                plot_mean=True,
                shading_kwargs={"color": c, "alpha": 0.3},
                mean_kwargs={"color": c, "label": f"time={t}s"},
            )
            axs[v, 0].vlines(
                t, ds.height.min(), ds.height.max(), linestyle=(0, (5, 6)), color=c
            )

        axs[v, 1].set_xlabel(f"{var} / {ds[var].units}")
        axs[v, 1].set_ylabel("height / m")
        axs[v, 1].set_ylim(0, 2000)
        axs[v, 1].set_title("")
        axs[v, 1].legend()

    fig.tight_layout()


times4xsection = {  # s: color
    180: "black",
    300: "blue",
    420: "purple",
    540: "red",
    660: "darkred",
}
plot_qvap_qcond(ds, times4xsection)
plt.show()


# %%
def plot_hill_figure2(ds):
    fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(5, 10), sharey=True)

    nc0 = ds.numconc.sel(time=0, method="nearest").mean().values
    fig.suptitle("Fig. 2, N$_a$ = {:.0f} ".format(nc0) + "cm$^{-3}$")

    lwc_10mins = ds.lwc.sel(time=600, method="nearest")
    mean, err1, err2 = mean_stddev(lwc_10mins, dim="ensemble")
    plot_vertical_error_shading(
        axs[0],
        ds.height,
        mean,
        err1,
        err2,
        plot_mean=True,
        shading_kwargs={"color": "blue", "alpha": 0.3},
        mean_kwargs={
            "color": "blue",
            "label": "time={:.0f}mins".format(lwc_10mins.time.values / 60),
        },
    )
    axs[0].legend()
    axs[0].set_xlabel("LWC / g m$^{-3}$")

    axs[0].set_ylim([0, 3000])
    for ax in axs:
        ax.set_ylabel("height / m")

    fig.tight_layout()


plot_hill_figure2(ds)
plt.show()


# %%
def plot_lwc_max_height(ds):
    fig, axs = plt.subplots(nrows=2, ncols=1)

    maxlwc = ds.lwc.max(dim="height")
    height_maxlwc = ds.lwc.idxmax(dim="height")

    ds.lwc.sel(ensemble="sol_0").T.plot(ax=axs[0])
    height_maxlwc.sel(ensemble="sol_0").plot(ax=axs[0], color="grey")

    ds.lwc.sel(height=height_maxlwc).sel(ensemble="sol_0").plot(ax=axs[1])
    maxlwc.sel(ensemble="sol_0").plot(linestyle="--", ax=axs[1], color="grey")

    fig.tight_layout()


plot_lwc_max_height(ds)
plt.show


# %%
def plot_hill_figure2(ds):
    fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(5, 10), sharex=True)

    nc0 = ds.numconc.sel(time=0, method="nearest").mean().values
    fig.suptitle("Fig. 4, N$_a$ = {:.0f} ".format(nc0) + "cm$^{-3}$")

    mean, err1, err2 = mean_stddev(ds.lwp, dim="ensemble")
    plot_horizontal_error_shading(
        axs[0],
        ds.time,
        mean,
        err1,
        err2,
        shading_kwargs={"alpha": 0.3, "color": "pink"},
        mean_kwargs={"color": "pink"},
        plot_mean=True,
    )
    axs[0].set_ylabel("LWP / kg m$^{-2}$")
    axs[0].set_ylim(bottom=0)

    # height_maxlwc = ds.lwc.idxmax(dim="height")

    axs[0].set_xlim([60, 3600])
    axs[-1].set_xlabel("time / s")

    fig.tight_layout()


plot_hill_figure2(ds)
plt.show()
