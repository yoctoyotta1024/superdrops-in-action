import numpy as np
import matplotlib.pyplot as plt

def massmom1dsnapshots(fig, axs, t2plts, time, massmom, norm, zfull,
                      xlab=None, xlims=[None, None], xlog=False,
                      color=None):

  z = zfull / 1000

  lines= []
  for i, t2plt in enumerate(t2plts):
    
    t = np.argmin(abs(time.mins-t2plt))
    
    meanmom = np.mean(massmom.mean[t,:,:]/norm, axis=0) 
    std = np.mean(massmom.stderr[t,:,:]/norm, axis=0)  
    l = axs[i].plot(meanmom, z, color=color)
    axs[i].fill_betweenx(z, meanmom-std, meanmom+std,
                         alpha=0.2, edgecolor=None,
                         facecolor=color)
    
    axs[i].set_title("t = {:.0f}".format(time.mins[t]))
    lines.append(l)

  for ax in axs:
    ax.set_ylim([z[0], z[-1]])
    ax.set_xlim(xlims)
    ax.set_xlabel(xlab)
    if xlog:
      ax.set_xscale("log")
  
  axs[0].set_ylabel("z /km")
  fig.tight_layout()

  return lines

def plot_precip(fig, axs, time, precip, color=None):
  
  lines = []
  for k, key in enumerate(["rate", "accum"]):

    mean, err = precip[key].mean, precip[key].stderr

    lines.append(axs[k].plot(time.mins, mean))
    lines.append(axs[k].fill_between(time.mins, mean-err,
                                     mean+err, alpha=0.5,
                                     edgecolor=None,
                                     facecolor=color))
    
    axs[k].set_xlim([0, time.mins[-1]])
    axs[k].set_xlabel("time /min")
  
  axs[0].set_ylabel("precipitation rate / mm hr$^{-1}$")
  axs[1].set_ylabel("accumulated precipitation / mm")

  fig.tight_layout()
  return lines
