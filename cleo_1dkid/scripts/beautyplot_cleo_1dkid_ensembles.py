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

import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--binpath",
    type=Path,
    default="/work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build/bin",
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
from pySD.sdmout_src import pysetuptxt, pygbxsdat  # from plotssrc import pltsds


# %%
def mean_iqr_ensemble(arr):
    """return mean, lq and uq, over ensemble dimension of array"""
    mean = arr.mean(dim="ensemble")
    arr = arr.chunk(dict(ensemble=-1))
    lq = arr.quantile(0.25, dim="ensemble", skipna=False)
    uq = arr.quantile(0.75, dim="ensemble", skipna=False)
    return mean, lq, uq


def plot_vertical_shading(
    ax,
    y,
    mean,
    lower,
    upper,
    plot_mean=False,
    shading_kwargs={"alpha": 0.3, "color": "pink"},
    mean_kwargs={"color": "black"},
):
    ax.fill_betweenx(y, lower, upper, **shading_kwargs)
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
def get_configuration_data(setupfile):
    config = pysetuptxt.get_config(setupfiles[0], nattrs=3, isprint=False)
    consts = pysetuptxt.get_consts(setupfiles[0], isprint=False)
    gbxs = pygbxsdat.get_gridboxes(args.grid_filename, consts["COORD0"], isprint=False)
    return config, consts, gbxs


# %%
assert args.binpath.is_dir()
ensembles = {}
for ensemb in ["condevap_only", "fullscheme"]:
    path2ensemb = args.binpath / ensemb
    print(f"Searching for ensemble {ensemb} in:\n{path2ensemb}")
    setupfiles = glob.glob(os.path.join(path2ensemb, "*.txt"))
    datasets = glob.glob(os.path.join(path2ensemb, "*.zarr"))
    assert setupfiles and datasets, "no setupfiles or datasets found"
    print(f"Setup and datasets found in\n{path2ensemb}:")
    print(", ".join([Path(s).name for s in setupfiles]))
    print(", ".join([Path(s).name for s in datasets]))

    config, consts, gbxs = get_configuration_data(
        setupfiles[0]
    )  # use first setup found

    ds = xr.open_mfdataset(
        datasets, engine="zarr", combine="nested", concat_dim="ensemble"
    )
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

    ensembles[ensemb] = ds

for ensemb, ds in ensembles.items():
    print(ensemb)
    print(ds)


# %%
def plot_qcond(axs, ds, times4xsection, showlegend=True, xsection_ylims=(0, 1750)):
    var = "qcond"
    label = "q$_l$ / g kg$^{-1}$"
    cmap = "Greys"
    norm = colors.LogNorm(vmin=1e-2, vmax=20)

    mean, lq, uq = mean_iqr_ensemble(ds[var])
    timemin = ds.time.values / 60
    contf = axs[0].pcolormesh(
        timemin,
        ds.height.values,
        mean.T,
        cmap=cmap,
        norm=norm,
    )
    plt.colorbar(contf, ax=axs[0], label=label)
    axs[0].set_xlim(0, 60)
    axs[0].set_ylim(0, 3000)
    axs[0].set_ylabel("height / m")
    axs[0].set_xlabel("time / min")

    for t, c in times4xsection.items():
        tmin = ds.time.sel(time=t, method="nearest") / 60
        m2plt = mean.sel(time=t, method="nearest")
        e1, e2 = (
            lq.sel(time=t, method="nearest"),
            uq.sel(time=t, method="nearest"),
        )
        plot_vertical_shading(
            axs[1],
            ds.height,
            m2plt,
            e1,
            e2,
            plot_mean=True,
            shading_kwargs={"color": c, "alpha": 0.3},
            mean_kwargs={
                "color": c,
                "label": "time={:.0f}min".format(tmin),
                "linewidth": 1.0,
            },
        )
        axs[0].vlines(
            tmin,
            xsection_ylims[0],
            xsection_ylims[1],
            linestyle=(0, (7, 7)),
            color=c,
            linewidth=1.0,
        )
    axs[1].set_xlabel(label)
    axs[1].set_ylabel("height / m")
    axs[1].set_ylim(xsection_ylims)
    axs[1].set_xlim(0, 10)
    axs[1].set_title("")
    if showlegend:
        axs[1].legend(loc=(0.6, 0.475))


# %%
fig, axs = plt.subplots(nrows=len(ensembles), ncols=2, figsize=(9, 5.2))
times4xsection = {  # time[s]: color
    120: "black",
    300: "darkblue",
    420: "purple",
    540: "crimson",
    3600: "darkred",
}
e = 0
showlegend = True
for ensemb, ds in ensembles.items():
    print(f"{ensemb} ensemble size: {ds.ensemble.size}")
    plot_qcond(axs[e, :], ds, times4xsection, showlegend=showlegend)
    e += 1
    showlegend = False  # only show legend on first ensemble plot
for ax in axs.flatten():
    ax.spines[["right", "top"]].set_visible(False)
for ax in axs[:, 0]:
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.set_yticks([0, 1000, 2000, 3000])
for ax in axs[:, 1]:
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([0, 500, 1000, 1500])
fig.tight_layout()


if args.figpath.is_dir():
    savename = args.figpath / "liquid_water_mass_mixing_ratios.png"
    fig.savefig(savename, dpi=800, bbox_inches="tight", facecolor="w")
else:
    print("not saving figure, no existing directory provided")

plt.show()
