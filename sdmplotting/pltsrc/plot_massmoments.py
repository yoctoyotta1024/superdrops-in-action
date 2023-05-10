import numpy as np
import matplotlib.pyplot as plt

def plot_domainmassmoments(fig, axs, time, massmoms):
 
  axs = axs.flatten() 
  
  l0 = axs[0].plot(time.mins, np.sum(massmoms.mom0, axis=(1,2,3)))
  l1 = axs[1].plot(time.mins, np.sum(massmoms.mom1, axis=(1,2,3)))
  l2 = axs[2].plot(time.mins, np.sum(massmoms.mom2, axis=(1,2,3)))

  domaineffmass = np.sum(massmoms.mom2, axis=(1,2,3)) / np.sum(massmoms.mom1, axis=(1,2,3))
  l3 = axs[3].plot(time.mins, domaineffmass)

  axs[0].set_ylabel("$\u03BB^{m}_{0}$, number of  superdroplets")
  axs[1].set_ylabel("$\u03BB^{m}_{1}$, total droplet mass /g")
  axs[2].set_ylabel("$\u03BB^{m}_{2}$ ~Reflectivity /g$^2$")
  axs[3].set_ylabel("$\u03BB^{m}_{2}$ / $\u03BB^{m}_{1}$, droplet effective mass /g")
  
  for ax in axs:
    ax.set_xlabel("time /min")
  
  fig.tight_layout()

  return [l0, l1, l2, l3]