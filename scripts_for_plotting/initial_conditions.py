"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: initial_conditions.py
Project: scripts
Created Date: Sunday 21st December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Plot initial conditions of 1-D kid test case from CLEO and PySDM output.
"""

# %%
import argparse
import matplotlib.pyplot as plt
from pathlib import Path

from src import load_ensemble_datasets as led
from src import distribs

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

# %% Load CLEO dataset to plot
cleo_dataset = (
    args.cleo_path2build / "bin_50cm3_real" / "condevap_only" / "sol_n256_a0p5_r0.zarr"
)
cleo_setup = (
    args.cleo_path2build / "bin_50cm3_real" / "condevap_only" / "setup_n256_a0p5_r0.txt"
)
cds, csds, csds_time = led.get_single_cleo_dataset(
    cleo_dataset,
    cleo_setup,
    args.cleo_grid_filename,
    precip_rolling_window,
)
cds

# %% Load PySDM dataset to plot
pysdm_dataset = (
    args.pysdm_path2build / "bin_nsupers256" / "naero50p0_precipFalse_a0p5_r0"
)
pds = led.get_single_pysdm_dataset(pysdm_dataset, precip_rolling_window)
pds

# %% full thermodynamics sanity check
fig, axes = plt.subplots(nrows=10, ncols=3, figsize=(8, 16))

times_colors = {
    0: "blue",
    1800: "darkgreen",
    3600: "grey",
}

cds_height = cds.height
pds_height = pds.height


def at_time(ds, var, time2plot):
    return ds[var].sel(time=time2plot, method="nearest")


def plot_row(axs, cds_var, pds_var, color):
    axs[0].plot(cds_var, cds_height, linestyle="-", color=color, alpha=0.5)
    axs[1].plot(pds_var, pds_height, linestyle="-", color=color, alpha=0.5)

    pds_on_cds_grid = pds_var.interp(height=cds_height)
    axs[2].plot(
        cds_var - pds_on_cds_grid, cds_height, linestyle="--", color=color, alpha=0.5
    )


for t, c in times_colors.items():
    axes[0, 0].set_title("CLEO\ntheta")
    axes[0, 1].set_title("PySDM\n")
    axes[0, 2].set_title("CLEO - PySDM\n")
    axes[0, 0].set_title("theta")
    plot_row(axes[0, :], at_time(cds, "theta", t), at_time(pds, "theta", t), color=c)

    axes[1, 0].set_title("theta_virtual")
    plot_row(
        axes[1, :],
        at_time(cds, "theta_virtual", t),
        at_time(pds, "theta_virtual", t),
        color=c,
    )

    axes[2, 0].set_title("qvap")
    plot_row(axes[2, :], at_time(cds, "qvap", t), at_time(pds, "qvap", t), color=c)

    axes[3, 0].set_title("press")
    plot_row(axes[3, :], at_time(cds, "press", t), at_time(pds, "press", t), color=c)

    axes[4, 0].set_title("press_dry")
    plot_row(
        axes[4, :], at_time(cds, "press_dry", t), at_time(pds, "press_dry", t), color=c
    )

    axes[5, 0].set_title("press_vapour")
    plot_row(
        axes[5, :],
        at_time(cds, "press_vapour", t),
        at_time(pds, "press_vapour", t),
        color=c,
    )

    axes[6, 0].set_title("rho")
    plot_row(axes[6, :], at_time(cds, "rho", t), at_time(pds, "rho", t), color=c)

    axes[7, 0].set_title("rho_dry")
    plot_row(
        axes[7, :], at_time(cds, "rho_dry", t), at_time(pds, "rho_dry", t), color=c
    )

    axes[8, 0].set_title("temp")
    plot_row(axes[8, :], at_time(cds, "temp", t), at_time(pds, "temp", t), color=c)

    axes[9, 0].set_title("relh")
    plot_row(axes[9, :], at_time(cds, "relh", t), at_time(pds, "relh", t), color=c)


for ax in axes.flatten():
    ax.set_ylim([-25, 3200])

fig.tight_layout()
plt.show()


# %% nice plot of intitial conditions
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8.5, 5.5))


def at_time(ds, var, time2plot):
    return ds[var].sel(time=time2plot, method="nearest")


for t in [0]:
    axes[0, 0].plot(at_time(cds, "theta", t), cds.height, color="C0", label="\u03F4")
    axes[0, 0].plot(
        at_time(cds, "theta_virtual", t), cds.height, color="C3", label="\u03F4$_{v}$"
    )
    axes[0, 0].legend()
    axes[0, 0].set_xlabel("\u03F4 / K")

    axes[0, 1].plot(at_time(cds, "qvap", t), cds.height)
    axes[0, 1].set_xlabel("q$_{v}$ / g kg$^{-1}$")

    axes[1, 0].plot(at_time(cds, "press", t), cds.height, color="C0", label="P")
    axes[1, 0].plot(
        at_time(cds, "press_dry", t), cds.height, color="C3", label="P$_{d}$"
    )
    # ax2 = axes[1, 0].twiny()
    # ax2.plot(at_time(cds, "press_vapour", t), cds.height, color="C4", label="P$_{v}$")
    # ax2.spines[["right",]].set_visible(False)
    # ax2.set_xlabel("P$_{v}$ / hPa", color="C4")
    axes[1, 0].legend()
    axes[1, 0].set_xlabel("P / hPa")

    axes[1, 2].plot(at_time(cds, "temp", t), cds.height)
    axes[1, 2].set_xlabel("T / K")

    axes[1, 1].plot(at_time(cds, "rho", t), cds.height, color="C0", label="\u03C1")
    axes[1, 1].plot(
        at_time(cds, "rho_dry", t), cds.height, color="C3", label="\u03C1$_{d}$"
    )
    axes[1, 1].legend()
    axes[1, 1].set_xlabel("\u03C1 / kg m$^{-3}$")

linestyles_h = {3000: ":", 1500: "--", 0: "-"}
for h in [3000, 1500, 0]:
    wvel = cds.wvel.sel(height=h, method="nearest")
    axes[0, 2].plot(
        cds.time, wvel, label=f"{h} m", color="k", linestyle=linestyles_h[h]
    )
axes[0, 2].set_xlabel("time / s")
axes[0, 2].set_xlim([0.0, 1000])
axes[0, 2].legend()
axes[0, 2].set_ylabel("$w$ / m s$^{-1}$")

axes[0, 0].set_ylabel("height / m")
axes[1, 0].set_ylabel("height / m")

for ax in axes.flatten():
    ax.spines[["right", "top"]].set_visible(False)

fig.tight_layout()

plt.savefig(
    args.path4figs / "thermo_inital_conditions.pdf", format="pdf", bbox_inches="tight"
)
plt.show()

# %% get colleciton of difefrent alpha superdrops
### assumes same cleo_setup and csds_time
data_path = args.cleo_path2build / "bin_50cm3_real" / "fullscheme"
alpha_csds = {
    0.0: data_path / "sol_n256_a0p0_r0.zarr",
    0.5: data_path / "sol_n256_a0p5_r0.zarr",
    1.0: data_path / "sol_n256_a1p0_r0.zarr",
}
for alpha, dataset in alpha_csds.items():
    alpha_csds[alpha] = led.get_single_cleo_dataset(
        dataset, cleo_setup, args.cleo_grid_filename, precip_rolling_window
    )[1]
alpha_csds
# %% plot different initial aerosol and alpha sampling from alpha_csds
from importlib import reload

reload(distribs)

fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(9, 5), sharex=True)

t2plts = [0.0]
nbins = 40
ylog = False
# rspan = [ak.min(csds["radius"]) * 0.9, ak.max(csds["radius"]) * 1.1]
rspan = [9.5e-3, 1.7e-1]  # microns
coord3_range = [0.0, 25.0]
volume = (
    (coord3_range[1] - coord3_range[0])
    * (cds.volume.sel(height=cds.height[1]) / (cds.height[2] - cds.height[1]))
).values

alpha_color = {
    0.0: "orange",
    0.5: "violet",
    1.0: "turquoise",
}
for alpha, csds in alpha_csds.items():
    plot_kwargs = {"c": alpha_color[alpha], "label": f"\u03B1 = {alpha}"}
    distribs.plot_numconc(
        fig,
        axs[0],
        csds,
        csds_time,
        coord3_range,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        ylog=True,
    )

    distribs.plot_nsupers(
        fig,
        axs[1],
        csds,
        csds_time,
        coord3_range,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        ylog=True,
    )

    plot_kwargs["marker"] = "."
    distribs.plot_xi(
        fig,
        axs[2],
        csds,
        csds_time,
        coord3_range,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        ylog=True,
    )
# fig.suptitle(f"distribution between {coord3_range[0]} < z < {coord3_range[1]}")

for ax in axs:
    ax.spines[["right", "top"]].set_visible(False)
axs[1].legend(loc="upper right")

fig.tight_layout()

plt.savefig(
    args.path4figs / "alpha_sampling_inital_conditions.pdf",
    format="pdf",
    bbox_inches="tight",
)
plt.show()
# %%
