"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: load_ensemble_datasets.py
Project: scripts
Created Date: Wednesday 10th December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Load results of 1-D kid test case for CLEO and PySDM into xarray datasets
"""

# %%
import glob
import os
import numpy as np
import xarray as xr
from pathlib import Path

from cleopy.sdmout_src import pyzarr, pysetuptxt, pygbxsdat
from PySDM.physics import si
from metpy import calc as mtpy_calc
from metpy.units import units as mtpy_units

from . import calcs


# %% Generic functions
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
    if is_precip:
        binpath = binpath / "fullscheme"
        if fixed_coaleff:
            binpath = Path(str(binpath) + "_fixed_coaleff")
    else:
        binpath = binpath / "condevap_only"

    assert binpath.is_dir(), f"binpath: {binpath}"
    setupfiles = glob.glob(os.path.join(binpath, f"setup_{label}*.txt"))
    datasets = glob.glob(os.path.join(binpath, f"sol_{label}*.zarr"))
    print(os.path.join(binpath, f"sol_{label}*.zarr"))
    assert (
        setupfiles and datasets
    ), f"no CLEO setupfiles or datasets for sol_{label}*.zarr found in\n{binpath}"
    print(f"CLEO Setup and datasets for sol_{label}*.zarr found in\n{binpath}:")
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
    binpath = path2build / f"bin_{numconc}cm3" / "condevap_only"
    if not binpath.is_dir():
        binpath = path2build / f"bin_{numconc}cm3" / "fullscheme_fixed_coaleff"
    if not binpath.is_dir():
        binpath = path2build / f"bin_{numconc}cm3" / "fullscheme"
    if not binpath.is_dir():
        raise FileNotFoundError(
            f"{binpath} doesn't exist for get_cleo_consts_gbxs_time"
        )
    print(f"using {binpath} for get_cleo_consts_gbxs_time")

    setup = binpath / f"setup_{label}.txt"
    dataset = binpath / f"sol_{label}.zarr"

    config = pysetuptxt.get_config(setup, nattrs=3, isprint=False)
    consts = pysetuptxt.get_consts(setup, isprint=False)
    gbxs = pygbxsdat.get_gridboxes(grid_filename, consts["COORD0"], isprint=False)
    time = pyzarr.get_time(dataset)

    return config, consts, gbxs, time


def get_cleo_ensemble_dataset(config, gbxs, datasets, precip_rolling_window):
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
        consolidated=False,
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
        calcs.mean_rolling_window(ds.surfprecip_rate, precip_rolling_window),
        name="surfprecip_rolling",
        dims=["ensemble", "time"],
        attrs={
            "units": "mm hr^-1",
            "long_name": "rolling mean of surface precipitation rate",
        },
    )
    ds = ds.assign(**{arr.name: arr})

    arr = xr.DataArray(
        mtpy_calc.relative_humidity_from_mixing_ratio(
            ds.press * mtpy_units.hPa,
            ds.temp * mtpy_units.kelvin,
            ds.qvap / 1000,
        )
        * 100,
        name="relh",
        dims=["ensemble", "time", "height"],
        attrs={
            "units": "%",
        },
    )
    ds = ds.assign(**{arr.name: arr})

    return ds


def fetch_cleo_datasets(
    cleo_path2build, cleo_grid_filename, setups, is_precip, precip_rolling_window
):
    cleo_config, cleo_consts, cleo_gbxs, cleo_time = get_cleo_consts_gbxs_time(
        cleo_path2build,
        cleo_grid_filename,
        is_precip=is_precip,
        numconc=50,
        nsupers=256,
        alpha=0.5,
        runn=0,
    )

    cleo_datasets = {
        get_label(
            is_precip, fixed_coaleff, numconc, nsupers, alpha
        ): get_cleo_ensemble_dataset(
            cleo_config,
            cleo_gbxs,
            get_cleo_ensemble_of_runs(
                cleo_path2build,
                is_precip,
                fixed_coaleff,
                numconc,
                nsupers,
                alpha,
            )[1],
            precip_rolling_window,
        )
        for numconc, fixed_coaleff in setups.keys()
        for nsupers in setups[(numconc, fixed_coaleff)][0]
        for alpha in setups[(numconc, fixed_coaleff)][1]
    }

    return cleo_datasets


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
    assert datasets, f"no PySDM datasets for {label}*/ found in\n{binpath}"
    print(f"PySDM Datasets found for {label}*/ in\n{binpath}:")
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
    datafiles.remove(f"{Path(d).parent}/dry_spectrum.npy")
    datafiles.remove(f"{Path(d).parent}/wet_spectrum.npy")
    datafiles.remove(f"{Path(d).parent}/peak_saturation.npy")
    datafiles.remove(f"{Path(d).parent}/rain_averaged_terminal_velocity.npy")
    datafiles.remove(f"{Path(d).parent}/ripening.npy")
    try:
        datafiles.remove(f"{Path(d).parent}/coalescence_rate.npy")
    except ValueError:
        print("no coalescence_rate in dataset")
    try:
        datafiles.remove(f"{Path(d).parent}/collision_deficit.npy")
    except ValueError:
        print("no collision_deficit in dataset")

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


def get_pysdm_ensemble_dataset(datasets, precip_rolling_window):
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

    ds["p"] = ds["p"] / 100
    ds["p"].attrs["unit"] = "hPa"

    ds["lwc"] = ds["lwc"] * 1000
    ds["lwc"].attrs["unit"] = "g m^-3"

    ds["water_vapour_mixing_ratio"] = ds["water_vapour_mixing_ratio"] * 1000
    ds["water_vapour_mixing_ratio"].attrs["unit"] = "g/kg"

    arr = xr.DataArray(
        ds.rain_water_mixing_ratio + ds.cloud_water_mixing_ratio,
        name="water_liquid_mixing_ratio",
        dims=["ensemble", "height", "time"],
        attrs={"units": "g/kg"},
    )
    ds = ds.assign(**{arr.name: arr})

    arr = xr.DataArray(
        ds.lwc.integrate(coord="height") / 1000,
        name="lwp",
        dims=["ensemble", "time"],
        attrs={"units": "Kg m^-2"},
    )
    ds = ds.assign(**{arr.name: arr})

    try:
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
    except AttributeError:
        print("no precipitation in dataset")

    try:
        arr = xr.DataArray(
            calcs.mean_rolling_window(ds.surfprecip_rate, precip_rolling_window),
            name="surfprecip_rolling",
            dims=["ensemble", "time"],
            attrs={
                "units": "mm hr^-1",
                "long_name": "rolling mean of surface precipitation rate",
            },
        )
        ds = ds.assign(**{arr.name: arr})
    except AttributeError:
        print("no precipitation in dataset")

    return ds


def fetch_pysdm_datasets(pysdm_path2build, setups, is_precip, precip_rolling_window):
    pysdm_datasets = {
        get_label(
            is_precip, fixed_coaleff, numconc, nsupers, alpha
        ): get_pysdm_ensemble_dataset(
            get_pysdm_ensemble_of_runs(
                pysdm_path2build, is_precip, numconc, nsupers, alpha
            ),
            precip_rolling_window,
        )
        for numconc, fixed_coaleff in setups.keys()
        for nsupers in setups[(numconc, fixed_coaleff)][0]
        for alpha in setups[(numconc, fixed_coaleff)][1]
    }

    return pysdm_datasets
