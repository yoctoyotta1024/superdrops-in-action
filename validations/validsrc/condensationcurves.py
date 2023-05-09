import numpy as np
import matplotlib.pyplot as plt


def kohler_curve(r, m_sol, temp, ionic, Mr_sol, criticalpoints=False):
    '''returns size and solute dependent 
    equilibrium saturation ratio, s_eq,
    for droplet according to kohler theory.
    Equations from An Introduction to Clouds 
    by Lohmann, Luond and Mahrt, 1st edition'''

    r = r/1e6 # convert from micron to m
    m_sol = m_sol/1000 # convert from g to Kg

    # eqn [6.24]
    a = 3.3e-7 / temp

    # eqn [6.22]
    b = 4.3e-6 * ionic * m_sol / Mr_sol

    # eqn [6.25]
    s_eq = (a/r) - (b/(r**3))

    if criticalpoints:
        rcrit = np.sqrt(3*b/a)
        scrit = 2*a/(3*rcrit)
        return s_eq, rcrit, scrit
    else:
        return s_eq


def plot_kohlercurve_with_criticalpoints(ax, r, solutemass,
                                         temperature, IONIC, MR_SOL):

    rkoh = np.linspace(np.amin(r), np.amax(r), 300)
    s_eq, rcrit, scrit = kohler_curve(rkoh, solutemass, temperature, IONIC,
                                      MR_SOL, criticalpoints=True)
    ax.plot(rkoh, s_eq*100, label="K\u00F6hler curve",
            color="grey", linestyle="-", linewidth=3, zorder=-1)
    ax.scatter(rcrit, scrit*100, marker="x",
               color="darkred", s=100, zorder=-2)


def condensation_validation_subplots(axs, time, radius, supersat, zprof,
                                     lwdth=1, lab=""):
    '''adds the subplots of displacement, supersaturation 
    and radial growth from Figure 5 of "On the CCN (de)activation 
    nonlinearities" S. Arabas and S. Shima 2017'''

    hlf = len(time)//2
    qtr = len(time)//4

    lab_a = "ascent "+lab
    col_a, lstyle_a = "k", "-"

    lab_b = "descent"
    col_b, lstyle_b = "orange", "--"

    axs[0].plot(supersat[:hlf]*100, zprof[:hlf], label=lab_a,
                color=col_a, linestyle=lstyle_a, linewidth=lwdth)
    axs[0].plot(supersat[hlf:]*100, zprof[hlf:], label=lab_b,
                color=col_b, linestyle=lstyle_b, linewidth=lwdth)
    axs[0].set_xlabel("supersaturation /%")
    axs[0].set_ylabel("displacement /m")

    axs[1].plot(radius[:hlf], supersat[:hlf]*100,
                color=col_a, linestyle=lstyle_a, linewidth=lwdth)
    axs[1].plot(radius[hlf:], supersat[hlf:]*100,
                color=col_b, linestyle=lstyle_b, linewidth=lwdth)
    axs[1].set_xlabel("radius /\u03BCm")
    axs[1].set_ylabel("supersaturation /%")

    axs[2].plot(radius[:qtr], zprof[:qtr],
                color=col_a, linestyle=lstyle_a, linewidth=lwdth)
    axs[2].plot(radius[3*qtr:], zprof[3*qtr:],
                color=col_b, linestyle=lstyle_b, linewidth=lwdth)
    axs[2].set_xlabel("radius /\u03BCm")
    axs[2].set_ylabel("displacement /m")

    return axs


def condensation_validation_figure(time, eps, radius, m_sol, temp, supersat,
                                 zprof, SDprops, setup, numconc):
    ''' plots the same plots as in Figure 5 of 
    "On the CCN (de)activation nonlinearities"
    S. Arabas and S. Shima 2017 to check radius 
    growth due to condensation is correct '''

    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(12, 5))

    plot_kohlercurve_with_criticalpoints(axs[1], radius, m_sol[0], temp[0],
                                        SDprops.IONIC, SDprops.MR_SOL)

    axs = condensation_validation_subplots(axs, time, radius, supersat, zprof)

    axs[0].legend(loc="lower right")
    axs[1].legend(loc="upper left")

    textlab = "N = "+str(numconc)+"cm$^{-3}$\n" +\
              "r$_{dry}$ = "+"{:.2g}\u03BCm\n".format(radius[0]) +\
              "<w> = {:.1f}".format(float(setup["W_AVG"])*100)+"cm s$^{-1}$"
    axs[0].text(0.03, 0.82, textlab, transform=axs[0].transAxes)

    axs[0].set_xlim([-1, 1])
    for ax in axs[1:]:
        ax.set_xlim([0.125, 10])
        ax.set_xscale("log")

    axs[0].set_ylim([0, 150])
    axs[1].set_ylim([-1, 1])
    axs[2].set_ylim([0, 75])

    fig.tight_layout()

    return fig, axs
