import numpy as np
import matplotlib.pyplot as plt

def massmom1dsnapshots(fig, axs, t2plts, time, massmom, norm, zfull,
                      xlab=None, xlims=[None, None], xlog=False,
                      color=None, alpha=0.2):

  z = zfull / 1000

  lines= []
  for i, t2plt in enumerate(t2plts):
    
    t = np.argmin(abs(time.mins-t2plt))
    
    meanmom = np.mean(massmom.mean[t,:,:]/norm, axis=0) 
    std = np.mean(massmom.stderr[t,:,:]/norm, axis=0)  
    l = axs[i].plot(meanmom, z, color=color)[0]
    axs[i].fill_betweenx(z, meanmom-std, meanmom+std,
                         alpha=alpha, edgecolor=None,
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

def plot_meantimeseries_with_shading(ax, time, mean, err,
                                    q1=[], q3=[], color=None,
                                    linestyle="-", alpha=0.5):

  l = ax.plot(time, mean, color=color, linestyle=linestyle)[0]
  ax.fill_between(time, mean-err, mean+err, alpha=alpha,
                  edgecolor=None, facecolor=color)
  
  if np.any(q1):
    ax.plot(time, q1, color=color, linestyle="--", alpha=alpha)
  if np.any(q3):
    ax.plot(time, q3, color=color, linestyle="--", alpha=alpha)
  
  return l

def plot_totprecip(fig, axs, time, precip, iqr, color=None):
  
  lines = []
  for k, key in enumerate(["totrate", "totaccum"]):
    
    mean, err = precip[key].mean, precip[key].stderr
    
    if iqr:
      q1, q3 = precip[key].q1, precip[key].q3
      l = plot_meantimeseries_with_shading(axs[k], time.mins, mean, err,
                                   q1=q1, q3=q3, color=color)
    else:
      l = plot_meantimeseries_with_shading(axs[k], time.mins, mean, err,
                                   color=color)
    
    lines.append(l)

    axs[k].set_xlim([0, time.mins[-1]])
    axs[k].set_xlabel("time /min")

  axs[0].set_ylabel("precipitation rate / mm hr$^{-1}$")
  axs[1].set_ylabel("accumulated precipitation / mm")

  fig.tight_layout()
  
  return lines
