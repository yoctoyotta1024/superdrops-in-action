import matplotlib.pyplot as plt

def axplt(ax, x, y, xlab=None, ylab=None, lab="_nolegend_",
          c=0, l='-', lw=1):
    
    if type(c)==type(0):
        c= 'C'+str(c)
    
    line = ax.plot(x,y, label=lab, color=c, linestyle=l, linewidth=lw)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    return line

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

    handles=[line1[0]]+[line2[0]]
    axs[1].legend(fontsize=11, loc='upper right', handles=handles)
    
    handles=[line3[0]]+[line4[0]]+[line5[0]]
    axs[2].legend(fontsize=11, loc='upper right', handles=handles)
    
    handles=[line6[0]]+[line7[0]]
    axs[3].legend(fontsize=11, loc='upper right', handles=handles)

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

    handles=[line3[0]]+[line4[0]]
    axs[2].legend(fontsize=11, loc='upper right', handles=handles)

    handles=[line5[0]]+[line6[0]]
    axs[3].legend(fontsize=11, loc='upper right', handles=handles)
    
    handles=[line7[0]]+[line8[0]]+[line9[0]]
    axs[4].legend(fontsize=11, loc='upper right', handles=handles)

    handles=[line10[0]]+[line11[0]]
    axs[5].legend(fontsize=11, loc='upper right', handles=handles)

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
