"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: compare_profiles.py
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
from src import calcs

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

precip_rolling_window = 100  # [number of timesteps, 1 timestep~1.25s]

numconc = 50  # [cm^-3]
nsupers = 256
alpha = 0.5
# %% Check directories containing datasets exist
assert args.cleo_path2build.is_dir(), f"cleo_path2build: {args.cleo_path2build}"
assert args.path4figs.is_dir(), f"path4figs: {args.path4figs}"


# %%
cleo_config, cleo_consts, cleo_gbxs, cleo_time = led.get_cleo_consts_gbxs_time(
    args.cleo_path2build,
    args.cleo_grid_filename,
    is_precip=True,
    numconc=numconc,
    nsupers=nsupers,
    alpha=alpha,
    runn=0,
)


# %%
def retrieve_different_profile_datasets(profiles_datasets, simtype):
    for key in profiles_datasets.keys():
        if key == "hydrostatic":
            binpath = args.cleo_path2build / f"bin_{numconc}cm3_real" / simtype
        else:
            binpath = (
                args.cleo_path2build
                / f"bin_{numconc}cm3_real"
                / "other_profiles"
                / key
                / simtype
            )
        assert binpath.is_dir(), f"binpath: {binpath}"
        profiles_datasets[key] = led.get_cleo_ensemble_dataset(
            cleo_config,
            cleo_gbxs,
            led.search_for_ensemble_of_cleo_runs(binpath, nsupers, alpha)[1],
            precip_rolling_window,
        )

    print(f"---- {len(profiles_datasets)} ensembles of {simtype} data ---- ")
    for key, value in profiles_datasets.items():
        print(key, f"members={value.ensemble.size}")
    print("-------------------------------- ")

    return profiles_datasets


# %%
condevap_only_datasets = {
    "hydrostatic": None,
    "approx_drhod_dz": None,
    "exner_novapour": None,
    "exner_novapour_constrho": None,
}
condevap_only_datasets = retrieve_different_profile_datasets(
    condevap_only_datasets, "condevap_only"
)
# %%
fullscheme_datasets = {
    "hydrostatic": None,
    "approx_drhod_dz": None,
    "exner_novapour": None,
    "exner_novapour_constrho": None,
}

fullscheme_datasets = retrieve_different_profile_datasets(
    fullscheme_datasets, "fullscheme"
)
# %% Plot Hill figure 4 (top 2 rows only)
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(9, 5), width_ratios=[3, 2])
gs = axes[0, -1].get_gridspec()
axes[0, -1].remove()
stdax = axes[1, -1]
axes = axes[:, :-1]
legax = fig.add_subplot(gs[0, -1])
legax.spines[["right", "top", "left", "bottom"]].set_visible(False)
legax.set_xticks([])
legax.set_yticks([])


def get_style(profile, simtype):
    if simtype == "condevap_only":
        line = "dotted"
    elif simtype == "fullscheme_fixed_coaleff":
        line = "dashed"
    elif simtype == "fullscheme":
        line = "solid"

    if profile == "hydrostatic":
        c = "C0"
    if profile == "approx_drhod_dz":
        c = "C4"
    elif profile == "exner_novapour":
        c = "C1"
    elif profile == "exner_novapour_constrho":
        c = "C3"

    return {"color": c, "linestyle": line}


axes_setups = {
    0: {
        "numconc": 50,
        "nsupers": 256,
        "alpha": 0.5,
    },
}

simtypes = {  # simtype: datasets for profiles
    "condevap_only": condevap_only_datasets,
    "fullscheme": fullscheme_datasets,
}

label_for_simtype = {  # simtype: label for legend
    "condevap_only": "no precip",
    "fullscheme": "with $E_{coal}$",
}

label_for_profile = {  # profile: label for legend
    "hydrostatic": "H",
    "approx_drhod_dz": "H$_{no-vapour}$",
    "exner_novapour": "$\u03A0$",
    "exner_novapour_constrho": "$\u03A0_{constant-density}$",
}


profile_as_value = {  # (for stdax) profile: value on x axis
    "hydrostatic": 0,
    "approx_drhod_dz": 1,
    "exner_novapour": 2,
    "exner_novapour_constrho": 3,
}

fmt_for_simtype = {  # (for stdax) simtype: markerstyle
    # excluding condevap_only
    "fullscheme": "x",
}

handles, labels = [], []
for a in range(len(axes_setups)):
    ax = axes[:, a]  # axes for given numconc
    numconc = axes_setups[a]["numconc"]
    nsupers = axes_setups[a]["nsupers"]
    alpha = axes_setups[a]["alpha"]

    for simtype, datasets in simtypes.items():
        for profile, ds in datasets.items():
            style = get_style(profile, simtype)

            if profile == list(datasets.keys())[0]:
                # get black lines with simtype label for legend
                lstyle = {**style}
                lstyle["color"] = "k"
                lines = ax[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **lstyle)
                handles.append(lines[0])
                labels.append(label_for_simtype[simtype])

            lines = ax[0].plot(ds.time, ds.lwp.mean(dim="ensemble"), **style)
            ax[1].plot(ds.time, ds.surfprecip_rolling.mean(dim="ensemble"), **style)
            if simtype == "fullscheme":
                handles.append(lines[0])
                labels.append(label_for_profile[profile])

            style["label"] = None
            style["alpha"] = 0.15
            lower, upper = calcs.mean_pm_stddev(ds.lwp, dim="ensemble")
            ax[0].fill_between(ds.time, lower, upper, **style)
            lower, upper = calcs.mean_pm_stddev_surfprecip_rolling(
                ds, precip_rolling_window, dim="ensemble"
            )
            ax[1].fill_between(ds.time, lower, upper, **style)

            if simtype != "condevap_only":
                mean = np.mean(ds.surfprecip_rolling.mean(dim="ensemble"))
                # yerr = [[mean-np.mean(lower)], [np.mean(upper)-mean]]
                yerr = np.mean((upper - lower) / 2.0)
                stdax.errorbar(
                    profile_as_value[profile],
                    mean,
                    yerr=yerr,
                    fmt=fmt_for_simtype[simtype],
                    color=style["color"],
                )
legax.legend(handles, labels)

for ax in axes.flatten():
    ax.spines[["right", "top"]].set_visible(False)
    ax.set_xlim([0, 3000])

for ax in axes[1, :]:
    ax.set_xlabel("time [s]")

axes[0, 0].set_ylabel("LWP / kg m$^{-2}$")
ylims1 = [0.0, 3.5]
yticks1 = np.arange(ylims1[0], ylims1[1] + 0.5, 1.0)
for ax in axes[0, :]:
    ax.set_ylim(ylims1)
    ax.set_yticks(yticks1)

axes[1, 0].set_ylabel("P / mm h$^{-1}$")
ylims2 = [0.0, 25]
yticks2 = np.arange(ylims2[0], ylims2[1] + 5, 5)
for ax in axes[1, :]:
    ax.set_ylim(ylims2)
    ax.set_yticks(yticks2)


stdax.set_ylabel("<P> / mm h$^{-1}$")
stdax.spines[["right", "top"]].set_visible(False)
stdax.set_ylim(bottom=0.0)
stdax.set_xticks(list(profile_as_value.values()))
labels = [label_for_profile[k] for k in profile_as_value.keys()]
stdax.set_xticklabels(labels)
stdax.set_xlabel("")

plt.savefig(args.path4figs / "fig4_profiles.pdf", format="pdf", bbox_inches="tight")
plt.show()


# %% Load more CLEO ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50, False): ([256], [0.0, 0.5, 1.0]),  # [0, 0.5, 1.0]),
    (50, True): ([256], [0.0, 0.5, 1.0]),
}

cleo_datasets = led.fetch_cleo_datasets(
    args.cleo_path2build,
    args.cleo_grid_filename,
    setups,
    True,
    precip_rolling_window,
)

# %% Load more CLEO ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50, False): ([8, 32, 64, 128, 256, 1024, 4096], [0.5]),
}

nsupers_datasets = led.fetch_cleo_datasets(
    args.cleo_path2build,
    args.cleo_grid_filename,
    setups,
    True,
    precip_rolling_window,
)
# %% Load more PySDM ensembles
setups = {  # (numconc, fixed_coaleffs) : (nsupers_per_gbxs, alphas)
    (50.0, True): ([256], [0.0, 0.5, 1.0]),
}

pysdm_datasets = led.fetch_pysdm_datasets(
    args.pysdm_path2build, setups, True, precip_rolling_window
)
# %% print available datasets
print(f"---- {len(fullscheme_datasets)} ensembles of cleo data ---- ")
for key, value in fullscheme_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")

print(f"---- {len(cleo_datasets)} ensembles of cleo data ---- ")
for key, value in cleo_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")

print(f"---- {len(pysdm_datasets)} ensembles of pysdm data ---- ")
for key, value in pysdm_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")

print(f"---- {len(nsupers_datasets)} ensembles of cleo data ---- ")
for key, value in nsupers_datasets.items():
    print(key, f"members={value.ensemble.size}")
print("-------------------------------- ")


# %% plot accumulated precip of many datasets
def add_surfprecip_cumulative_to_plot(
    axs, ds, plot_kwargs={"fmt": "x", "color": "k"}, nsupers=None, note=None
):
    fmt = plot_kwargs.pop("fmt")

    mean = ds.surfprecip_cumulative.mean(dim="ensemble")
    lower, upper = calcs.mean_pm_stddev(ds.surfprecip_cumulative, dim="ensemble")
    yerr = np.mean((upper - lower) / 2.0)

    axs[0].plot(ds.time, mean, **plot_kwargs)

    x, y = 0.0, mean[-1]
    if nsupers is not None:
        x = np.log2(nsupers)
    axs[1].errorbar(x, y, yerr=yerr, **plot_kwargs, fmt=fmt)
    if note is not None:
        axs[1].annotate(note, (x + 1, y), va="center", color=plot_kwargs["color"])

    plot_kwargs["label"] = None
    plot_kwargs["alpha"] = 0.15
    axs[0].fill_between(ds.time, lower, upper, **plot_kwargs)


fullscheme_plot_kwargs = {  # fullscheme_datasets : plot_kwargs
    "hydrostatic": {"color": "black", "linestyle": "-", "fmt": "+"},
    "approx_drhod_dz": {"color": "black", "linestyle": ":", "fmt": "+"},
    "exner_novapour": {"color": "black", "linestyle": "--", "fmt": "+"},
    "exner_novapour_constrho": {"color": "black", "linestyle": "-.", "fmt": "+"},
}

cleo_datasets_plot_kwargs = {
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffFalse": {
        "color": "purple",
        "linestyle": "-",
        "fmt": "1",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse": {
        "color": "purple",
        "linestyle": "-",
        "fmt": "+",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffFalse": {
        "color": "purple",
        "linestyle": "-",
        "fmt": "x",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffTrue": {
        "color": "blue",
        "linestyle": "-",
        "fmt": "1",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue": {
        "color": "blue",
        "linestyle": "-",
        "fmt": "+",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffTrue": {
        "color": "blue",
        "linestyle": "-",
        "fmt": "x",
    },
}

pysdm_datasets_plot_kwargs = {
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffTrue": {
        "color": "red",
        "linestyle": "-",
        "fmt": "1",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue": {
        "color": "red",
        "linestyle": "-",
        "fmt": "+",
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffTrue": {
        "color": "red",
        "linestyle": "-",
        "fmt": "x",
    },
}

fullscheme_note = {  # profile: label for legend
    "hydrostatic": None,
    "approx_drhod_dz": "H$_{no-vapour}$",
    "exner_novapour": "$\u03A0$",
    "exner_novapour_constrho": "$\u03A0_{constant-density}$",
}

cleo_datasets_note = {
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffFalse": None,
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse": "CLEO, with $E_{coal}$, various \u03B1",
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffFalse": None,
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffTrue": None,
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue": "CLEO, various \u03B1",
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffTrue": None,
}

pysdm_datasets_note = {
    "is_precipTrue_numconc50p000_nsupers256_alpha0p000_fixedeffTrue": None,
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffTrue": "PySDM, various \u03B1",
    "is_precipTrue_numconc50p000_nsupers256_alpha1p000_fixedeffTrue": None,
}

fig, axs = plt.subplots(nrows=1, ncols=2, width_ratios=[24, 1], figsize=(7, 4))

for key, ds in fullscheme_datasets.items():
    if key in fullscheme_plot_kwargs:
        add_surfprecip_cumulative_to_plot(
            axs,
            ds,
            plot_kwargs=fullscheme_plot_kwargs[key],
            note=fullscheme_note[key],
        )
for key, ds in cleo_datasets.items():
    if key in cleo_datasets_plot_kwargs:
        add_surfprecip_cumulative_to_plot(
            axs,
            ds,
            plot_kwargs=cleo_datasets_plot_kwargs[key],
            note=cleo_datasets_note[key],
        )
for key, ds in pysdm_datasets.items():
    if key in pysdm_datasets_plot_kwargs:
        add_surfprecip_cumulative_to_plot(
            axs,
            ds,
            plot_kwargs=pysdm_datasets_plot_kwargs[key],
            note=pysdm_datasets_note[key],
        )

ylims = [0.0, 2.0]
axs[0].spines[["right", "top"]].set_visible(False)
axs[0].set_xlim([1000, 3600])
axs[0].set_ylim(ylims)
axs[0].set_xlabel("time / s")
axs[0].set_ylabel("accumulated precipitation / mm")

axs[1].set_ylim(ylims)
axs[1].set_xlim([-0.25, 1])
axs[1].spines[["right", "top", "bottom", "left"]].set_visible(False)
axs[1].set_xticks([])
axs[1].set_yticks([])

plt.tight_layout()
plt.savefig(
    args.path4figs / "accumulated_precip_profiles_alpha_ecoal.pdf",
    format="pdf",
    bbox_inches="tight",
)
plt.show()
# %%
nsupers_datasets_plot_kwargs = {
    "is_precipTrue_numconc50p000_nsupers8_alpha0p500_fixedeffFalse": {
        "color": "orange",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers32_alpha0p500_fixedeffFalse": {
        "color": "chocolate",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers64_alpha0p500_fixedeffFalse": {
        "color": "maroon",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers128_alpha0p500_fixedeffFalse": {
        "color": "red",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse": {
        "color": "blue",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers1024_alpha0p500_fixedeffFalse": {
        "color": "purple",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 0.6,
    },
    "is_precipTrue_numconc50p000_nsupers4096_alpha0p500_fixedeffFalse": {
        "color": "black",
        "linestyle": "-",
        "fmt": "+",
        "alpha": 1.0,
        "zorder": -1,
    },
}

nsupers_datasets_nsupers = {
    "is_precipTrue_numconc50p000_nsupers8_alpha0p500_fixedeffFalse": 8,
    "is_precipTrue_numconc50p000_nsupers32_alpha0p500_fixedeffFalse": 32,
    "is_precipTrue_numconc50p000_nsupers64_alpha0p500_fixedeffFalse": 64,
    "is_precipTrue_numconc50p000_nsupers128_alpha0p500_fixedeffFalse": 128,
    "is_precipTrue_numconc50p000_nsupers256_alpha0p500_fixedeffFalse": 256,
    "is_precipTrue_numconc50p000_nsupers1024_alpha0p500_fixedeffFalse": 1024,
    "is_precipTrue_numconc50p000_nsupers4096_alpha0p500_fixedeffFalse": 4096,
}

fig, axs = plt.subplots(nrows=1, ncols=2, width_ratios=[6, 4])

for key, ds in nsupers_datasets.items():
    if key in nsupers_datasets_plot_kwargs:
        add_surfprecip_cumulative_to_plot(
            axs,
            ds,
            plot_kwargs=nsupers_datasets_plot_kwargs[key],
            nsupers=nsupers_datasets_nsupers[key],
        )

ylims = [0.0, 0.25]
axs[0].spines[["right", "top"]].set_visible(False)
axs[0].set_xlim([1000, 3600])
axs[0].set_ylim(ylims)
axs[0].set_xlabel("time / s")
axs[0].set_ylabel("accumulated precipitation / mm")

axs[1].set_ylim(ylims)
axs[1].set_xlabel("log$_{2}$|N$_{SD}$|")
axs[1].spines[["right", "top", "left"]].set_visible(False)
axs[1].set_yticks([])
# axs[1].set_xticks([])

plt.tight_layout()
plt.savefig(
    args.path4figs / "accumulated_precip_nsupers.pdf", format="pdf", bbox_inches="tight"
)
plt.show()
# %%
