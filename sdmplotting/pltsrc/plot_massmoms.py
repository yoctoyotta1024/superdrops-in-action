import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors 
from matplotlib.cm import ScalarMappable

def plot_domainmassmoments(fig, axs, time, massmoms):
 
  axs = axs.flatten() 
  
  l0 = axs[0].plot(time.mins, np.sum(massmoms.mom0, axis=(1,2,3)))
  l1 = axs[1].plot(time.mins, np.sum(massmoms.mom1, axis=(1,2,3)))
  l2 = axs[2].plot(time.mins, np.sum(massmoms.mom2, axis=(1,2,3)))

  domaineffmass = np.sum(massmoms.mom2, axis=(1,2,3)) / np.sum(massmoms.mom1, axis=(1,2,3))
  l3 = axs[3].plot(time.mins, domaineffmass)

  axs[0].set_ylabel("$\u03BB^{m}_{0}$, number of  droplets")
  axs[1].set_ylabel("$\u03BB^{m}_{1}$, total droplet mass /g")
  axs[2].set_ylabel("$\u03BB^{m}_{2}$ ~Reflectivity /g$^2$")
  axs[3].set_ylabel("$\u03BB^{m}_{2}$ / $\u03BB^{m}_{1}$, droplet effective mass /g")
  
  for ax in axs:
    ax.set_xlabel("time /min")
  
  fig.tight_layout()

  return [l0, l1, l2, l3]


def plot_2dtimeslice(fig, ax, gbxs, data2d, tplt,
                    cmap="bone_r", cmapnorm=None):
  
  xx, zz = gbxs.xxh/1000, gbxs.zzh/1000
  im = ax.pcolormesh(xx, zz, data2d, cmap=cmap, norm=cmapnorm)
  txt = ax.text(0.95, 0.95, "t = {:.0f}mins".format(tplt), ha="right", 
                va="top", transform=ax.transAxes)
  txt.set_bbox(dict(facecolor='w', alpha=0.5, edgecolor="w"))
  
  ax.set_aspect("equal")
  ax.set_xlabel("x /km")
  ax.set_ylabel("z /km")
 
  fig.tight_layout()

  return im

def massmom2dsnapshots(fig, gs, t2plts, time, massmom, norm, gbxs,
                        cmap="bone_r", cmapnorm=None, cbarlab=None):
  '''mass mom has dims [time, x, z]'''

  if len(t2plts) < gs.nrows * (gs.ncols-1):
    raise ValueError(str(len(t2plts))+" t2plts not enough for gridspec")
  
  if not cmapnorm:
    dat = massmom/norm
    cmapnorm = colors.LogNorm(vmin=np.nanmin(dat[dat!=0.0]), vmax=np.nanmax(dat))

  ims = []
  i=0
  for row in range(gs.nrows):
    for col in range(gs.ncols-1):
      t = np.argmin(abs(time.mins-t2plts[i]))
      data2plt = massmom[t,:,:]/norm
    
      ax = fig.add_subplot(gs[row, col])
      im = plot_2dtimeslice(fig, ax, gbxs, data2plt, time.mins[t],
                            cmap=cmap, cmapnorm=cmapnorm)
      ims.append(im)
      i +=1

  axs = fig.get_axes()
  tcks = [0, 0.75, 1.5]
  for ax in axs:
    ax.set_xticks(tcks)
    ax.set_yticks(tcks)
    ax.set(xlabel=None, ylabel=None, xticklabels=[], yticklabels=[])
  axs = np.reshape(axs, [gs.nrows, gs.ncols-1])
  for ax in axs[:,0]:
    ax.set_ylabel("z / km")
    ax.set_yticklabels(tcks)
  for ax in axs[-1,:]:
    ax.set_xlabel("x / km")
    ax.set_xticklabels(tcks)

  cax = fig.add_subplot(gs[:, -1]) 
  cbar = fig.colorbar(ScalarMappable(norm=cmapnorm, cmap=cmap), ax=cax, cax=cax)
  cbar.set_label(cbarlab)

  fig.tight_layout()

  return ims + [cbar]