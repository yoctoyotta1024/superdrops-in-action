"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: compare_with_cleo.py
Project: scripts
Created Date: Tuesday 9th December 2025
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
import glob
import os

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

from pathlib import Path

from cleopy.sdmout_src import pyzarr, pysetuptxt, pygbxsdat
from PySDM.physics import si

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

assert args.path4figs.is_dir(), f"path4figs: {args.path4figs}"


# %% Generic Functions
def get_label(is_precip, fixed_coaleff, numconc, nsupers, alpha):
    precip = "False"
    if is_precip:
        precip = "True"

    fixedeff = "False"
    if fixed_coaleff:
        fixedeff = "True"

    numconc = f"{numconc:.3f}".replace(".", "p")
    alpha = f"{alpha:.3f}".replace(".", "p")

    return f"is_precip{precip}_numconc{numconc}_nsupers{nsupers}_alpha{alpha}_fixedeff{fixedeff}"


# %% CLEO functions
def get_cleo_ensemble_of_runs(
    path2build, is_precip, fixed_coaleff, numconc, nsupers, alpha
):
    label = f"n{nsupers}_a{alpha}_r".replace(".", "p")
    binpath = path2build / f"bin_{numconc}cm3"
    if fixed_coaleff:
        binpath = Path(str(binpath) + "_fixed_coaleff")
    if is_precip:
        binpath = binpath / "fullscheme"
    else:
        binpath = binpath / "condevap_only"

    assert binpath.is_dir(), f"binpath: {binpath}"
    setupfiles = glob.glob(os.path.join(binpath, f"setup_{label}*.txt"))
    datasets = glob.glob(os.path.join(binpath, f"sol_{label}*.zarr"))
    print(os.path.join(binpath, f"sol_{label}*.zarr"))
    assert setupfiles and datasets, "no CLEO setupfiles or datasets found"
    print(f"CLEO Setup and datasets found in\n{binpath}:")
    print(", ".join([Path(s).name for s in setupfiles]))
    print(", ".join([Path(s).name for s in datasets]))

    return setupfiles, datasets


def get_cleo_consts_gbxs_time(
    path2build,
    grid_filename,
    is_precip=True,
    numconc=50,
    nsupers=256,
    alpha=1.0,
    runn=0,
):
    label = f"n{nsupers}_a{alpha}_r{runn}".replace(".", "p")
    if is_precip:
        binpath = path2build / f"bin_{numconc}cm3" / "fullscheme"
    else:
        binpath = path2build / f"bin_{numconc}cm3" / "condevap_only"

    setup = binpath / f"setup_{label}.txt"
    dataset = binpath / f"sol_{label}.zarr"

    config = pysetuptxt.get_config(setup, nattrs=3, isprint=False)
    consts = pysetuptxt.get_consts(setup, isprint=False)
    gbxs = pygbxsdat.get_gridboxes(grid_filename, consts["COORD0"], isprint=False)
    time = pyzarr.get_time(dataset)

    return config, consts, gbxs, time


def get_cleo_ensemble_dataset(config, gbxs, datasets):
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

    return ds


def cleo_lwc_fixed(press, temp, qvap, qcond):
    def rho(press, temp, qvap):
        p = press * 100  # [Pa]
        qv = qvap / 1000  # [kg/kg]
        Rd = 287.0027
        Rv = 461.52998157941937
        Rq = (Rv * qv + Rd) / (1 + qv)
        return p / Rq / temp

    rho_dry = rho(press, temp, qvap) / (1 + qvap / 1000)
    return qcond * rho_dry


# %% PySDM functions
def get_pysdm_ensemble_of_runs(path2build, is_precip, numconc, nsupers, alpha):
    precip = "False"
    if is_precip:
        precip = "True"
    label = f"naero{numconc}_precip{precip}_a{alpha}_r".replace(".", "p")
    binpath = path2build / f"bin_nsupers{nsupers}"

    assert binpath.is_dir()
    datasets = glob.glob(os.path.join(binpath, f"{label}*/"))
    print(os.path.join(binpath, f"{label}*/"))
    print(datasets)
    assert datasets, "no PySDM datasets found"
    print(f"PySDM Datasets found in\n{binpath}:")
    print(", ".join([Path(s).name for s in datasets]))

    return datasets


def convert_numpy_arrays_to_dataset(dataset):
    def get_dims(key, len_time, len_height, array):
        if array.shape == (len_time,):
            return ("time",)
        elif array.shape == (len_height,):
            return ("height",)
        elif array.shape == (len_height, len_time):
            return ("height", "time")
        elif (
            array.ndim == 3
            and array.shape[0] == len_height
            and array.shape[2] == len_time
        ):
            return ("height", "spectralbin", "time")
        else:
            raise ValueError(f"{key} array has unsupported dimensions")

    datafiles = glob.glob(os.path.join(dataset, "*.npy"))

    ### remove unwanted variables
    for d in datafiles:
        assert Path(d).parent == Path(datafiles[0]).parent
    datafiles.remove(f"{Path(d).parent}/activating.npy")
    datafiles.remove(f"{Path(d).parent}/deactivating.npy")
    datafiles.remove(f"{Path(d).parent}/coalescence_rate.npy")
    datafiles.remove(f"{Path(d).parent}/collision_deficit.npy")
    datafiles.remove(f"{Path(d).parent}/dry_spectrum.npy")
    datafiles.remove(f"{Path(d).parent}/wet_spectrum.npy")
    datafiles.remove(f"{Path(d).parent}/peak_saturation.npy")
    datafiles.remove(f"{Path(d).parent}/rain_averaged_terminal_velocity.npy")
    datafiles.remove(f"{Path(d).parent}/ripening.npy")

    rawdata = {Path(file).stem: np.load(file) for file in datafiles}

    lt = rawdata["t"].shape[0]
    lh = rawdata["z"].shape[0]
    data = {
        key: {"dims": get_dims(key, lt, lh, value), "data": value}
        for key, value in rawdata.items()
    }

    ### rename variables to match CLEO naming conventions
    data["time"] = data.pop("t")
    data["height"] = data.pop("z")
    data["lwc"] = data.pop("LWC")

    ds = xr.Dataset.from_dict(data)

    return ds


def get_pysdm_ensemble_dataset(datasets):
    ddss = []
    for dataset in datasets:
        ddss.append(convert_numpy_arrays_to_dataset(dataset))

    ds = xr.concat(ddss, dim="ensemble")
    ensemble_coord = dict(ensemble=("ensemble", [str(Path(d).stem) for d in datasets]))
    ds = ds.assign_coords(ensemble_coord)

    arr = xr.DataArray(
        datasets,
        name="sources",
        dims=["ensemble"],
        attrs={"long_name": "path to dataset of each ensemble member"},
    )
    ds = ds.assign(**{arr.name: arr})

    arr = xr.DataArray(
        ds.lwc.integrate(coord="height"),
        name="lwp",
        dims=["ensemble", "time"],
        attrs={"units": "Kg m^-2"},
    )
    ds = ds.assign(**{arr.name: arr})

    arr = xr.DataArray(
        ds.surface_precipitation * si.hour / si.mm,
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

    return ds


# %% Load CLEO ensembles
cleo_config, cleo_consts, cleo_gbxs, cleo_time = get_cleo_consts_gbxs_time(
    args.cleo_path2build, args.cleo_grid_filename
)

setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50, False): ([256], [0, 0.5, 1.0]),
    (50, True): ([256], [0, 0.5, 1.0]),
    (150, False): ([256], [0, 0.5, 1.0]),
    (150, True): ([256], [0, 0.5, 1.0]),
    (300, False): ([256], [0, 0.5, 1.0]),
    (300, True): ([256], [0, 0.5, 1.0]),
}

cleo_datasets = {
    get_label(
        is_precip, fixed_coaleff, numconc, nsupers, alpha
    ): get_cleo_ensemble_dataset(
        cleo_config,
        cleo_gbxs,
        get_cleo_ensemble_of_runs(
            args.cleo_path2build,
            is_precip,
            fixed_coaleff,
            numconc,
            nsupers,
            alpha,
        )[1],
    )
    for numconc, fixed_coaleff in setups.keys()
    for nsupers in setups[(numconc, fixed_coaleff)][0]
    for alpha in setups[(numconc, fixed_coaleff)][1]
}

print("---- ensembles of cleo data ---- ")
for key, value in cleo_datasets.items():
    print(key)
print("-------------------------------- ")


# %% Load PySDM ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50.0, True): ([8, 256], [0.0, 0.5, 1.0]),
    (150.0, True): ([256], [0.0, 0.5, 1.0]),
    (300.0, True): ([256], [0.0, 0.5, 1.0]),
}

pysdm_datasets = {
    get_label(
        is_precip, fixed_coaleff, numconc, nsupers, alpha
    ): get_pysdm_ensemble_dataset(
        get_pysdm_ensemble_of_runs(
            args.pysdm_path2build, is_precip, numconc, nsupers, alpha
        )
    )
    for numconc, fixed_coaleff in setups.keys()
    for nsupers in setups[(numconc, fixed_coaleff)][0]
    for alpha in setups[(numconc, fixed_coaleff)][1]
}

print("---- ensembles of pysdm data ---- ")
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
# %% Plot Hill Figure 4 (top 2 rows only)
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(16, 5), width_ratios=[5, 5, 5, 4])
gs = axes[0, 3].get_gridspec()
for ax in axes[:, -1]:
    ax.remove()
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
    lbl = f"{mdl}, \u03B1={alpha}"
    if not fixed_coaleff:
        lbl += ", with $E_{coal}$"

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
for a in range(3):
    ax = axes[:, a]  # axes for given numconc
    numconc = axes_setups[a]["numconc"]
    nsupers = axes_setups[a]["nsupers"]

    for alpha in axes_setups[a]["alpha"]:
        for fixed_coaleff in axes_setups[a]["fixed_coaleff"]:
            label = get_label(is_precip, fixed_coaleff, numconc, nsupers, alpha)
            if label in pysdm_datasets.keys():
                # print(f"{label} found for PySDM")
                ds = pysdm_datasets[label]
                style = get_style("pysdm", fixed_coaleff, alpha)
                ax[0].plot(ds.lwp.mean(dim="ensemble"), **style)
                ax[1].plot(ds.surfprecip_rolling.mean(dim="ensemble"), **style)
            else:
                print(f"skipping PySDM {label}")

            if label in cleo_datasets.keys():
                # print(f"{label} found for CLEO")
                ds = cleo_datasets[label]
                style = get_style("cleo", fixed_coaleff, alpha)
                ax[0].plot(ds.lwp.mean(dim="ensemble"), **style)
                ax[1].plot(ds.surfprecip_rolling.mean(dim="ensemble"), **style)

                fstyle = get_style("cleo", fixed_coaleff, alpha)
                fstyle["label"] += "\n -- LWP fix"
                fstyle["color"] = "medium" + fstyle["color"]
                lwpfix = (
                    cleo_lwc_fixed(ds.press, ds.temp, ds.qvap, ds.qcond).integrate(
                        coord="height"
                    )
                    / 1000
                )
                ax[0].plot(lwpfix.mean(dim="ensemble"), **fstyle)

            else:
                print(f"skipping CLEO {label}")

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
# yticks1 = np.arange(ylims1[0], ylims1[1]+0.5, 0.5)
for ax in axes[0, :]:
    ax.set_ylim(ylims1)
    # ax.set_yticks(yticks1)

axes[1, 0].set_ylabel("P / mm h^{-1}$")
ylims2 = [0.0, 4.0]
# yticks2 = np.arange(ylims2[0], ylims2[1]+1.0, 1.0)
for ax in axes[1, :]:
    ax.set_ylim(ylims2)
    # ax.set_yticks(yticks2)

plt.savefig(
    args.path4figs / "fig4_pysdm_cleo_comparison.pdf", format="pdf", bbox_inches="tight"
)
plt.show()

# %%
