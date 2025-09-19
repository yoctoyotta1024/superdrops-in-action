"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: perform_1dkid_test_case.py
Project: test_case_1dkid
Created Date: Monday 2nd September 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Wednesday 4th June 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
interface called by a test to run the 1-D KiD and then plot the results.

"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from .run_1dkid import run_1dkid
from libs.utility_functions import plot_utilities
from libs.thermo import formulae


def perform_1dkid_test_case(
    z_min,
    z_max,
    z_delta,
    time_end,
    timestep,
    thermo_init,
    microphys_scheme,
    advect_hydrometeors,
    figpath,
    run_name,
):
    """
    Run test case for a 1-D KiD rainshaft model.

    This function runs a 1-D KiD rainshaft model with a specified microphysics scheme and
    KiD dynamics given the initial thermodynamics. The data is then saved/plotted in the
    figpath directory using the run_name as a label.

    Args:
        z_min (float): Lower limit of 1-D column (max half-cell) (m).
        z_max (float): Upper limit of 1-D column (max half-cell) (m).
        z_delta (float): Grid spacing of 1-D column (m).
        time_end (float): End time for the simulation (s).
        timestep (float): Timestep for the simulation (s).
        thermo_init (Thermodynamics): Initial thermodynamics.
        microphys_scheme: Microphysics scheme to use in test run.
        figpath (str): Path to the directory where data/plots will be saved.
        run_name (str): Name of the test run (used for labeling output).

    Raises:
        AssertionError: If the specified figpath does not exist or if run_name is empty.

    Returns:
        None

    """

    print("\n--- Running 1-D KiD Rainshaft Model ---")
    out = run_1dkid(
        z_min,
        z_max,
        z_delta,
        time_end,
        timestep,
        thermo_init,
        microphys_scheme,
        advect_hydrometeors,
    )
    print("--------------------------------")

    print("--- Plotting Results ---")
    assert Path(figpath).exists(), "The specified figpath does not exist."
    assert run_name, "The run_name cannot be empty."
    plot_1dkid_moisture(out, z_delta, z_max, figpath, run_name)
    print("------------------------")

    return out


def plot_1dkid_moisture(out, z_delta, z_max, figpath, run_name):
    """
    Plots the 1D Kinematic Driver (KID) results and saves the plots.

    Parameters:
        out: OutputThermodynamics
            The dataset containing the output variables to plot (qvap, qcond, temp, press).
        z_delta: float
            The vertical resolution of the model.
        z_max: float
            The maximum height of the model domain.
        figpath: str
            The path where the plot images will be saved.
        run_name: str
            The name of the run, used for labeling the plots and the output file name.

    Returns:
        None

    """
    assert Path(figpath).exists()
    assert run_name
    print("plotting " + run_name + " and saving plots in: " + str(figpath))

    fig, axs = plt.subplots(
        nrows=6,
        ncols=2,
        figsize=(9, 16),
        width_ratios=[3, 1],
        height_ratios=[27, 1] * 3,
    )
    figname = run_name + "_moisture.png"

    # %% plot results
    label = f"{out.qvap.name} / g/kg"
    plot_kid_result(
        fig,
        axs[0, 0],
        axs[1, 0],
        axs[0, 1],
        out.qvap.values,
        out.time.values,
        z_delta,
        z_max,
        label,
        mult=1e3,
        threshold=1e-3,
        cmap="gray",
    )

    label = f"({out.qcond.name} + {out.qrain.name})/ g/kg"
    plot_kid_result(
        fig,
        axs[2, 0],
        axs[3, 0],
        axs[2, 1],
        out.qcond.values + out.qrain.values,
        out.time.values,
        z_delta,
        z_max,
        label,
        mult=1e3,
        threshold=1e-3,
        cmap="gray",
    )

    supersat = formulae.supersaturation(
        out.temp.values, out.press.values, out.qvap.values
    )
    label = "supersaturation / %"
    plot_kid_result(
        fig,
        axs[4, 0],
        axs[5, 0],
        axs[4, 1],
        supersat,
        out.time.values,
        z_delta,
        z_max,
        label,
        mult=100,
        rng=(-0.25, 0.75),
        cmap="gray_r",
    )

    for ax in [axs[2, 0], axs[4, 0]]:
        ax.sharex(axs[0, 0])
    for ax in axs[0::2, :]:
        ax[0].sharey(axs[0, 0])
        ax[1].sharey(axs[0, 0])
    for ax in axs[1::2, 1]:
        ax.remove()

    fig.tight_layout()
    plot_utilities.save_figure(fig, figpath, figname)


def plot_kid_result(
    fig,
    ax0,
    cax0,
    ax1,
    var,
    time,
    z_delta,
    z_max,
    label,
    mult=1.0,
    threshold=None,
    rng=None,
    cmap="copper",
    rasterized=False,
):
    """
    Function extracted from pyMPDATA-examples Shipway and Hill 2012 plot.py script for a1-D KiD rainshaft.

    Parameters:
    fig : matplotlib.figure.Figure
        The figure object to plot on.
    ax0 : matplotlib.axes.Axes
        The first axes object for pcolormesh plot.
    cax0 : matplotlib.axes.Axes
        The axes object for the colorbar of ax0.
    ax1 : matplotlib.axes.Axes
        The second axes object for cross-section plot.
    var : numpy.ndarray
        The variable to be plotted, dimensions [time, height]
    time : float
        The time data to plot (will be coarsened by 'fctr', see code)
    z_delta : float
        The vertical resolution of the data.
    z_max : float
        The maximum vertical extent of the data (max half-cell).
    label : str
        The label for variable on the plot, e.g. for colourbar.
    mult : float, optional
        A multiplicative factor to apply to 'var' data values (default is 1.0).
    threshold : float, optional
        A threshold value for the data to plot (default is None).
    rng : [float, float], optional
        The range of data to plot (default is None).
    cmap : str, optional
        The colormap to be used for plotting (default is "copper").
    rasterized : bool, optional
        Whether to rasterize the plot (default is False).

    See Also:
    https://github.com/open-atmos/PyMPDATA/blob/main/examples/PyMPDATA_examples/Shipway_and_Hill_2012/plot.py
    for the original source code.

    """
    lines = {3: ":", 6: "--", 9: "-", 12: "-."}
    colors = {3: "crimson", 6: "orange", 9: "navy", 12: "green"}
    fctr = 5

    coarse_dt = (time[1] - time[0]) * fctr
    tgrid = np.concatenate(((time[0] - coarse_dt / 2,), time[0::fctr] + coarse_dt / 2))
    tgrid = tgrid / 60  # [minutes]

    assert z_max % z_delta == 0, "z limit is not a multiple of the grid spacing."
    nz = int(z_max / z_delta)
    zgrid = np.linspace(0, z_max, nz + 1, endpoint=True)
    zgrid = zgrid / 1000  # [km]

    var = var * mult
    time_steps = var.shape[0] - 1
    assert (
        time_steps % fctr == 0
    ), "number of timesteps must be divisible by coarsening factor"

    # coarsen temporal part by 'fctr' transpose var for plotting
    tmp = var[1:, :]
    tmp = tmp.reshape(-1, fctr, tmp.shape[1])
    tmp = tmp.mean(axis=1)
    tmp = np.concatenate(((var[0, :],), tmp)).T

    if threshold is not None:
        tmp = np.where(tmp < threshold, np.nan, tmp)
    mesh = ax0.pcolormesh(
        tgrid,
        zgrid,
        tmp,
        cmap=cmap,
        rasterized=rasterized,
        vmin=None if rng is None else rng[0],
        vmax=None if rng is None else rng[1],
    )

    ax0.set_xlabel("time / min")
    ax0.set_xticks(list(lines.keys()))
    ax0.set_ylabel("z / km")
    ax0.grid()

    cbar = fig.colorbar(mesh, cax=cax0, shrink=0.8, location="bottom")
    cbar.set_label(label)

    ax1.set_xlabel(label)
    ax1.grid()
    if rng is not None:
        ax1.set_xlim(rng)

    last_t = -1
    for i, t in enumerate(time):
        t = t / 60  # [minutes]
        d = var[i, :]
        z = (zgrid[1:] + zgrid[:-1]) / 2
        params = {"color": "black"}
        for line_t, line_s in lines.items():
            if last_t < line_t <= t:
                params["ls"] = line_s
                params["color"] = colors[line_t]
                ax1.step(d, z, where="mid", **params)
                ax0.axvline(t, **params)
        last_t = t
