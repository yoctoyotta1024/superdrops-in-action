"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: distribs.py
Project: src
Created Date: Monday 22nd December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
helper functions to plot droplet distributions from CLEO superdroplets data
"""


from plotcleo import pltdist


def plot_dists(
    ax,
    distribcalc,
    superdroplet_timeslice,
    vol,
    rspan,
    nbins,
    plot_kwargs,
    masscalc=None,
    smoothsig=False,
    perlogR=True,
    ylog=False,
):
    for t in range(len(superdroplet_timeslice.time())):
        radius = superdroplet_timeslice["radius"][t]
        xi = superdroplet_timeslice["xi"][t]
        if masscalc:
            msol = superdroplet_timeslice["msol"][t]
            mass = masscalc(radius, msol)
        else:
            mass = None

        hcens, hist = distribcalc(
            radius, xi, mass, vol, rspan, nbins, perlogR=perlogR, smooth=smoothsig
        )
        if smoothsig:
            ax.plot(hcens, hist, **plot_kwargs)
        else:
            ax.step(hcens, hist, where="mid", **plot_kwargs)

    if ylog:
        ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("radius / \u03BCm")

    return ax


def plot_domainnsupers_distribs(
    time,
    superdrops,
    t2plts,
    domainvol,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=True,
    ylog=False,
    fig_ax=None,
):
    fig, ax = fig_ax

    variables2slice = ["time", "radius", "xi", "msol"]
    superdrops_timeslice = superdrops.time_slice(
        t2plts, variables2slice, attach_time=True, time=time.secs, time_units="s"
    )

    plot_dists(
        ax,
        pltdist.nsupers_distrib,
        superdrops_timeslice,
        domainvol,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
    )

    if perlogR:
        ax.set_ylabel("number of superdroplets / unit lnR")
    else:
        ax.set_ylabel("number of superdroplets")

    return fig, ax


def plot_domainnumconc_distribs(
    time,
    superdrops,
    t2plts,
    domainvol,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=True,
    ylog=False,
    fig_ax=None,
):
    fig, ax = fig_ax

    variables2slice = ["time", "radius", "xi", "msol"]
    superdrops_timeslice = superdrops.time_slice(
        t2plts, variables2slice, attach_time=True, time=time.secs, time_units="s"
    )

    plot_dists(
        ax,
        pltdist.numconc_distrib,
        superdrops_timeslice,
        domainvol,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
    )

    if perlogR:
        ax.set_ylabel("real droplet concentration /cm$^{-3}$ / unit lnR")
    else:
        ax.set_ylabel("real droplet concentration /cm$^{-3}$")

    return fig, ax


def plot_domainxi_scatter(
    time,
    superdrops,
    t2plts,
    domainvol,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=True,
    ylog=False,
    fig_ax=None,
):
    fig, ax = fig_ax

    variables2slice = ["time", "radius", "xi", "msol"]
    superdrops_timeslice = superdrops.time_slice(
        t2plts, variables2slice, attach_time=True, time=time.secs, time_units="s"
    )

    def xi_distrib(radius, xi, mass, vol, rspan, nbins, perlogR, smooth):
        weights = xi  # number superdroplets []
        hist, hedges, hcens = pltdist.logr_distribution(
            rspan, nbins, radius, weights, perlogR=perlogR, smooth=smooth
        )

        return hcens, hist

    for t in range(len(superdrops_timeslice.time())):
        radius = superdrops_timeslice["radius"][t]
        xi_1e6 = superdrops_timeslice["xi"][t] / 1e6
        ax.scatter(radius, xi_1e6, **plot_kwargs)

    if ylog:
        ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("radius / \u03BCm")

    if perlogR:
        ax.set_ylabel("superdroplet multiplicity / 10$^6$ / unit lnR")
    else:
        ax.set_ylabel("superdroplet multiplicity / 10$^6$")

    return fig, ax


def plot_distribs_in_select_range(
    time,
    plot_xxx_distribs,
    var_for_range,
    range_values,
    superdrops,
    t2plts,
    volume,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=True,
    ylog=False,
    fig_ax=None,
):
    superdrops.detach_time()
    variables2select = ["radius", "xi", "msol"]
    select_superdrops = superdrops.select_range(
        var_for_range, range_values, variables2select
    )
    fig, ax = plot_xxx_distribs(
        time,
        select_superdrops,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
        fig_ax=fig_ax,
    )
    return fig, ax


def plot_numconc(
    fig,
    ax,
    csds,
    csds_time,
    coord3_range,
    t2plts,
    volume,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=True,
    ylog=True,
):
    plot_distribs_in_select_range(
        csds_time,
        plot_domainnumconc_distribs,
        "coord3",
        coord3_range,
        csds,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
        fig_ax=[fig, ax],
    )


def plot_nsupers(
    fig,
    ax,
    csds,
    csds_time,
    coord3_range,
    t2plts,
    volume,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=False,
    ylog=False,
):
    plot_distribs_in_select_range(
        csds_time,
        plot_domainnsupers_distribs,
        "coord3",
        coord3_range,
        csds,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
        fig_ax=[fig, ax],
    )


def plot_xi(
    fig,
    ax,
    csds,
    csds_time,
    coord3_range,
    t2plts,
    volume,
    rspan,
    nbins,
    plot_kwargs,
    smoothsig=False,
    perlogR=False,
    ylog=True,
):
    plot_distribs_in_select_range(
        csds_time,
        plot_domainxi_scatter,
        "coord3",
        coord3_range,
        csds,
        t2plts,
        volume,
        rspan,
        nbins,
        plot_kwargs,
        smoothsig=smoothsig,
        perlogR=perlogR,
        ylog=ylog,
        fig_ax=[fig, ax],
    )
