import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

def axplt(ax, x, y, xlab=None, ylab=None, lab="_nolegend_",
          c="k", l='-', lw=1):
    
    if type(c)==type(0):
        c= 'C'+str(c)
    
    l = ax.plot(x, y, label=lab, color=c, linestyle=l, linewidth=lw)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    return l[0]

def axplt2d(ax, xxh, zzh, var, cmap, norm, lab):
    
    var2d = np.mean(var, axis=(0,1)) # avg over time and y axes
    if norm:
        pcm = ax.pcolormesh(xxh[:,:], zzh[:,:], var2d, cmap=cmap, norm=norm)
    else:
        pcm = ax.pcolormesh(xxh[:,:], zzh[:,:], var2d, cmap=cmap)
    plt.colorbar(pcm, ax=ax, location="top", label=lab)
    
    return pcm

def plot_kinetics_against_time(fig, axs, time, press, temp, qvap, qcond,
                               relh, supersat, dry_adia):

    axs = axs.flatten()
    
    line0 = axplt(axs[0], time, press, ylab='Pressure /mbar', c=0)

    line1 = axplt(axs[1], time, dry_adia, lab='dry adiabat', c=2, l='--')
    line2 = axplt(axs[1], time, temp, ylab='T /K', lab='temp', c=3)

    line3 = axplt(axs[2], time, qvap+qcond, lab='total', c=7, l='--')
    line4 = axplt(axs[2], time, qvap, lab='vapour', c=5)
    line5 = axplt(axs[2], time, qcond, xlab="time /s", ylab='Water Content',
          lab='liquid', c=6)

    line6 = axplt(axs[3], time, relh, xlab="time /s", ylab='relative humidity',
                  lab="relh", c=4)
    line7 = axplt(axs[3].twinx(), time, supersat, 
                  ylab="supersaturation", lab="supersat", c=4, l='--')

    axs[1].legend(fontsize=11, loc='upper right', handles=[line1, line2])
    axs[2].legend(fontsize=11, loc='upper right', handles=[line3, line4, line5])
    axs[3].legend(fontsize=11, loc='upper right', handles=[line6, line7])
    axs[0].set_yscale("log")

    fig.tight_layout()

    return [line0, line1, line2, line3, line4, line5, line6, line7]


def plot_kinetics_against_pressure(fig, axs, press, temp, qvap, qcond,
                                   theta, pv, psat, relh, supersat, dry_adia, dry_adia_theta, displacement):

    axs = axs.flatten()
    lines = []

    line0 = axplt(axs[0], displacement/1000, press,
          'displacement, z /km', 'P /mbar', c=0)

    line1 = axplt(axs[1], dry_adia, press, lab='dry adiabat', c=2, l='--')
    line2 = axplt(axs[1], temp, press, 'T /K', lab='temp', c=3)

    line3 = axplt(axs[2], dry_adia_theta, press, lab='dry adiabat', c=2, l='--')
    line4 = axplt(axs[2], theta, press, '\u03B8 /K', lab='\u03B8', c=1)

    line5 = axplt(axs[3], psat/100, press, lab='saturation p', c=2, l='--')
    line6 = axplt(axs[3], pv/100, press, xlab='Water Vapour Pressure /mbar',
          ylab="P /mbar", lab="vapour p", c=4)

    line7 = axplt(axs[4], qvap+qcond, press, lab='total', c=7, l='--')
    line8 = axplt(axs[4], qcond, press, lab='liquid', c=6)
    line9 = axplt(axs[4], qvap, press, xlab='Water Content', lab='vapour', c=5)

    line10 = axplt(axs[5], supersat, press, xlab='Supersaturation', 
                  lab="supersat", c=4, l='--')
    line11 = axplt(axs[5].twiny(), relh, press, xlab='Relative Humidity', 
                  lab="relh", c=4)

    for ax in axs:
        ax.set_yscale('log')
        ax.invert_yaxis()

    axs[2].legend(fontsize=11, loc='upper right', handles=[line3, line4])
    axs[3].legend(fontsize=11, loc='upper right', handles=[line5, line6])
    axs[4].legend(fontsize=11, loc='upper right', handles=[line7, line8, line9])
    axs[5].legend(fontsize=11, loc='upper right', handles=[line10, line11])

    fig.tight_layout()

    lines = [line0, line1, line2, line3, line4, line5, line6, 
                  line7, line8, line9, line10, line11]

    return lines

def plot_moist_static_energy(fig, ax, time, mse):

    line0 = axplt(ax, time, mse, c="k",
          xlab="time /s", ylab='moist static energy / J/Kg$')
    axb = ax.twinx()

    line1 = axplt(axb, time, ((mse-mse[0])/mse[0]*100),
          ylab='% change in moist static energy', c="k")

    fig.tight_layout()

    return [line0, line1]

def domainmean_against_time(fig, axs, time, thermo):

    axs = axs.flatten()
    
    l0 = axplt(axs[0], time.mins, np.mean(thermo.press, axis=(1,2,3)),
               ylab='Pressure /mbar', c=0)
    l1 = axplt(axs[1], time.mins, np.mean(thermo.temp, axis=(1,2,3)),
               ylab='Temperature /K', lab='temp', c=3)
    
    meantotwater =  np.mean(thermo.qvap+thermo.qcond, axis=(1,2,3))
    l2 = axplt(axs[2], time.mins, meantotwater, lab='total', c=7, l='--')
    l3 = axplt(axs[2], time.mins, np.mean(thermo.qvap, axis=(1,2,3)),
               lab='vapour', c=5)
    l4 = axplt(axs[2], time.mins, np.mean(thermo.qcond, axis=(1,2,3)),
               xlab="time /min", ylab='Water Content', lab='liquid', c=6)

    l5 = axplt(axs[3], time.mins, np.mean(thermo["relh"], axis=(1,2,3)),
               xlab="time /min", ylab='relative humidity', lab="relh", c=4)
    l6 = axplt(axs[3].twinx(), time.mins, np.mean(thermo["supersat"], axis=(1,2,3)), 
               ylab="supersaturation", lab="supersat", c=4, l='--')
 
    axs[2].legend(fontsize=11, loc='upper right', handles=[l2, l3, l4])
    axs[3].legend(fontsize=11, loc='upper right', handles=[l5, l6])

    axs[0].set_yscale("log")

    fig.tight_layout()

    return [l0, l1, l2, l3, l4, l5, l6]


def domain2dmean(fig, axs, grid, thermo):

    axs = axs.flatten()
    xxh, zzh = np.meshgrid(grid["xhalf"], grid["zhalf"], indexing="ij") # dims [xdims, zdims] [m]
    xxh, zzh = [xxh/1000, zzh/1000] #[km]
 
    norms=[colors.CenteredNorm(vcenter=np.nanmin(thermo.press)),
            colors.CenteredNorm(vcenter=np.nanmin(thermo.temp)),
            colors.CenteredNorm(vcenter=np.nanmin(thermo.theta)),
            colors.CenteredNorm(vcenter=np.nanmin(thermo.qvap*1000)),
            colors.CenteredNorm(vcenter=np.nanmin(thermo.qcond*1000)),
            colors.CenteredNorm(vcenter=0.0)]        

    l0 = axplt2d(axs[0], xxh, zzh, thermo.press,
                 "PRGn", norms[0], "pressure / hPa")
    l1 = axplt2d(axs[1], xxh, zzh, thermo.temp,
                 "RdBu_r", norms[1], "temperature / K")
    l1 = axplt2d(axs[2], xxh, zzh, thermo.theta,
                 "RdBu_r", norms[2], "\u03F4$_{dry}$ / K")
    l2 = axplt2d(axs[3], xxh, zzh, thermo.qvap*1000,
                 "BrBG", norms[3], "q$_{v}$ / g/kg")
    l3 = axplt2d(axs[4], xxh, zzh, thermo.qcond*1000,
                 "BrBG", norms[4], "q$_{l}$ / g/kg")
    l4 = axplt2d(axs[5], xxh, zzh, thermo["supersat"],
                 "PuOr", norms[5], "supersaturation")
    
    for ax in axs:
        ax.set_aspect("equal")
        ax.set_xlabel("x /km")
        ax.set_ylabel("z /km")

    fig.tight_layout()

    return [l0, l1, l2, l3, l4]