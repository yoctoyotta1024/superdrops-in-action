"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: plot_utilities.py
Project: utility_functions
Created Date: Monday 2nd September 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Wednesday 4th September 2024
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Helpful functions for plotting

"""

from ..thermo.output_thermodynamics import OutputThermodynamics


def save_figure(fig, binpath, figname):
    """
    Save a Matplotlib figure as a PNG file with high resolution and tight bounding box.

    Args:
        fig (matplotlib.figure.Figure): The Matplotlib figure to be saved.
        binpath (Path): The directory where the figure will be saved.
        figname (str): The name of the PNG file to save in binpath directory.

    Returns:
        None

    """
    from pathlib import Path

    filename = Path(binpath) / figname
    fig.savefig(
        filename,
        dpi=400,
        bbox_inches="tight",
        facecolor="w",
        format="png",
    )
    print("Figure .png saved as: " + str(binpath) + "/" + figname)


def plot_thermodynamics_output_timeseries(ax, out: OutputThermodynamics, var: str):
    """
    Plot a variable against time on an axis.

    Args:
        ax (matplotlib.axes.Axes): The (x-y) axis on which to plot the variable.
        out (OutputThermodynamics): OutputThermodynamics containing time (x axis)
                                    and OutputVaribale "var" (y axis).
        var (str): Name of the variable to be plotted (y axis).

    Returns:
        None

    """
    ax.plot(out.time.values, out[var].values)
    ax.set_ylabel(out[var].name + " /" + out[var].units)
