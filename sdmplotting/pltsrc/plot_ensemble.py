def massmom1dsnapshots(fig, axs, t2plts, massmom, norm, zfull,
                      xlab=None, xlims=[None, None], xlog=False):

  z = zfull / 1000

  lines= []
  for i, t2plt in enumerate(t2plts):
    
    t = np.argmin(abs(time.mins-t2plt))
    
    meanmom = np.mean(massmom.mean[t,:,:]/norm, axis=0) 
    std = np.mean(massmom.std[t,:,:]/norm, axis=0)  
    l = axs[i].plot(meanmom, z)
    axs[i].fill_betweenx(z, meanmom-std, meanmom+std, alpha=0.5)
    
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