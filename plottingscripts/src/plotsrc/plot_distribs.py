import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

from ..handlesrc import histos, pyzarr
from ..handlesrc.pyzarr import select_from_attr

plt.rcParams.update({'font.size': 14})

def timelabel(times, t):
  
  ind = np.argmin(abs(times-t))
  tlab = 't = {:.2f}s'.format(times[ind])

  return tlab

def get_weights(weights, n):
  
  if type(weights) == type(None):
    return None
  
  else:
    return weights[n]

def ensemble_radiusrange(datasets):
  ''' return smallest and largest radius value in ensemble '''
  

  maxr, minr = 0, np.inf
  for dataset in datasets.flatten():
    radius = pyzarr.get_rawdataset(dataset).radius.values
    maxr = max(maxr, np.nanmax(radius))
    minr = min(minr, np.nanmin(radius))
      
  return [minr, maxr]

def plot_distrib(ax, hist, hedges, hcens, time, t2sel, c="k",
                  smooth=False, bar=False, ylog=False):
    ''' plot a distirbution over log(r) using the
    weights for each time in tplt list then plot it on axis "ax" '''

    tlab = timelabel(time, t2sel)
    
    if bar:
        hwdths = hedges[1:] - hedges[:-1]
        line = ax.bar(hcens, hist, hwdths, label=tlab, color=c)
    if smooth:
        line = ax.plot(hcens, hist, label=tlab, color=c) 
    else:
        line = ax.step(hcens, hist, label=tlab, where='mid', color=c)

    ax.legend()
    ax.set_xlabel("radius, r, /\u03BCm")
    ax.set_xscale('log')

    if ylog:
        ax.set_yscale('log')

    plt.tight_layout()

    return line

def calc_distrib_plotonaxis(ax, tplt, rspan, nbins, time, radius, weights,
                        perlogR=False, smooth=False, bar=False, ylog=False):
    ''' calculate a distirbution over log(r) using the
    weights for each time in tplt list then plot it on axis "ax" '''

    lines = []
    for n in range(len(tplt)): 

      wght = get_weights(weights, n)
      hist, hedges, hcens = histos.logr_distribution(rspan, nbins,
                                                     radius[n], wght,
                                                     perlogR=perlogR,
                                                     smooth=smooth)
      
      lines.extend(plot_distrib(ax, hist, hedges, hcens, time, tplt[n], c='C'+str(n),
                   smooth=smooth, bar=bar, ylog=ylog))

    return lines


def plot_domain_superdroplets_distrib(fig, ax, tplt, rspan, nbins, times,
                                      sddata, bar=False, ylog=False):
    ''' plot the superdroplet number distirbution over log(r)
    for all the superdroplets in the domain at each time in tplt list '''

    weights = None
    radius = select_from_attr(sddata["radius"], times, tplt)
  
    lines = calc_distrib_plotonaxis(ax, tplt, rspan, nbins, times,
                        radius, weights, perlogR=False, smooth=False,
                        bar=bar, ylog=ylog)
    ax.set_ylabel("No. Superdroplets")

    return lines


def plot_domain_realdroplet_numconc_distrib(fig, ax, tplt, rspan, nbins, times,
                                            sddata, domainvol, bar=False, ylog=False):
    ''' plot the real droplet number conc distirbution over log(r)
    for all the droplets in the domain at each time in tplt list '''

    sel_data = pyzarr.select_manytimes_from_sddata(sddata, times, tplt, ["eps", "radius"])
  
    weights = sel_data["eps"]/domainvol
    radius = sel_data["radius"]
 
    lines = calc_distrib_plotonaxis(ax, tplt, rspan, nbins, times,
                        radius, weights, perlogR=False, smooth=False,
                        bar=bar, ylog=ylog)
    
    ax.set_ylabel("Real Droplet Concentration /m$^{-3}$")

    return lines


def plot_domain_realdroplet_numconc_difference(fig, ax, tplt, rspan, nbins, times,
                                               sddata, domainvol, bar=False, ylog=False):
    ''' plot the difference between the real droplet number conc 
    distirbution over log(r) at each time in the tplt realtive to t=0 '''

    weights0 = sddata["eps"][0]/domainvol
    hist0 = histos.logr_distribution(rspan, nbins, sddata["radius"][0], weights0)[0]

    sel_data = pyzarr.select_manytimes_from_sddata(sddata, times, tplt, ["eps", "radius"])
    
    lines = []
    for n in range(len(tplt)):
      tlab = timelabel(times, tplt[n])
      c = 'C'+str(n)

      weights = sel_data["eps"][n]/domainvol
      hist, hedges, hcens = histos.logr_distribution(rspan, nbins,
                                                      sel_data["radius"][n], weights)

      if bar:
        hwdths = hedges[1:] - hedges[:-1]
        line = ax.bar(hcens, hist-hist0, hwdths, label=tlab, color=c)
      else:
        line = ax.step(hcens, hist-hist0, label=tlab, where='mid', color=c)

      lines.append(line)

    # ax.legend()
    ax.set_ylabel("\u0394 /m$^{-3}$")
    ax.set_xlabel("radius, r, /\u03BCm")
    ax.set_xscale('log')

    if ylog:
        ax.set_yscale('log')

    plt.tight_layout()

    return lines

def plot_domain_msolutedens_distrib(fig, ax, tplt, rspan, nbins, times, 
                             sddata, domainvol, SDprops,
                             smooth=False, bar=False, ylog=False):
  ''' plot the solute mass distirbution over log(r) in realdroplets
  from all the superdroplets in the domain at each time in tplt list '''

  attrs2sel = ["radius", "m_sol", "eps"]
  selsddata = pyzarr.select_manytimes_from_sddata(sddata, times, tplt, attrs2sel)
  
  weights = []
  for t in range(len(tplt)):
    m_sol = np.asarray(selsddata["m_sol"][t]) # [g]
    weights.append(selsddata["eps"][t] * m_sol / domainvol)

  radius = selsddata["radius"]
  lines = calc_distrib_plotonaxis(ax, tplt, rspan, nbins, times, radius, weights, 
                                    perlogR=True, smooth=smooth, bar=bar, ylog=ylog)
  
  ax.set_ylabel("Solute Mass Distribution \n /g m$^{-3}$ /unit lnR")

  return lines

def plot_domain_mwaterdens_distrib(fig, ax, tplt, rspan, nbins, times, 
                                    sddata, domainvol, SDprops,
                                    smooth=False, bar=False, ylog=False):
  ''' plot the water mass distirbution over log(r) for the real droplets
  from all the superdroplets in the domain at each time in tplt list '''

  attrs2sel = ["radius", "m_sol", "eps"]
  selsddata = pyzarr.select_manytimes_from_sddata(sddata, times, tplt, attrs2sel)
  
  weights = []
  for t in range(len(tplt)):
    mwater = SDprops.m_water(np.asarray(selsddata["radius"][t]), 
                      np.asarray(selsddata["m_sol"][t])) # [g]
  
    weights.append(selsddata["eps"][t] * mwater / domainvol)
  
  radius = selsddata["radius"]
  lines = calc_distrib_plotonaxis(ax, tplt, rspan, nbins, times, radius, weights, 
                                    perlogR=True, smooth=smooth, bar=bar, ylog=ylog)
  
  ax.set_ylabel("Droplet Water Mass Distribution \n /g m$^{-3}$ / unit lnR")

  return lines

def plot_domain_mtotdens_distribs(fig, ax, tplt, rspan, nbins, time, 
                                sddata, domainvol, SDprops,
                                smooth=False, bar=False, ylog=False):
  ''' plot the total mass (water+solute) in real droplets over log(r)
  from all the droplets in the domain at each time in tplt list '''
  
  attrs2sel = ["radius", "m_sol", "eps"]
  selsddata = pyzarr.select_manytimes_from_sddata(sddata, time, tplt, attrs2sel)
  
  lines = []
  for t in range(len(tplt)):

    radius = np.asarray(selsddata["radius"][t])
    m_sol = np.asarray(selsddata["m_sol"][t])
    eps = selsddata["eps"][t]
    hist, hedges, hcens = histos.domain_mtotdens_distrib(radius, m_sol, eps, 
                                                         rspan, nbins, domainvol,
                                                         SDprops, smooth=smooth)
    
    lines.extend(plot_distrib(ax, hist, hedges, hcens, time, tplt[t],
                              c='C'+str(t), smooth=smooth, bar=bar, ylog=ylog))

  ax.set_ylabel("Total Droplet Mass Distribution,"+\
                  " \n g(lnR), /g m$^{-3}$ / unit lnR")

  return lines

def plot_coord3radius_2Ddistrib(fig, ax, freq, redgs, c3edgs, 
                                cmap, norm=None):
    
    if not norm:
      n = (np.amax(freq) - np.amin(freq))//5
      bounds = np.arange(np.amin(freq), np.amax(freq), n)
      norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend="max")
      
    cmap = cmap.copy()
    cmap.set_under('w')

    xx, yy = np.meshgrid(redgs, c3edgs)
    pcolor = ax.pcolormesh(xx, yy/1000, freq, cmap=cmap, norm=norm)
    cbar = fig.colorbar(pcolor, ax=ax)

    ax.set_xlabel("radius, r, /\u03BCm")
    ax.set_ylabel("z / km")
    cbar.set_label('Frequency')
    
    return [pcolor, cbar]