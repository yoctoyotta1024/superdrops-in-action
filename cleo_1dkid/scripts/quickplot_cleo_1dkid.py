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
    default="/home/m/m300950/superdrops-in-action/build/bin/condevap_only",
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
    default="/home/m/m300950/superdrops-in-action/build/bin/condevap_only",
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
