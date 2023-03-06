### functions related to calculating histograms
# (probability) distributions from SDs data

import numpy as np
from . import pyzarr

def gaussian_kernel_smoothing(hist, hcens, sig):

    smoothhist = []
    for h in range(len(hist)):
        kernel = 1/(np.sqrt(2*np.pi)*sig)*np.exp(-(hcens - hcens[h])**2/(2*sig**2))
        kernel = kernel/np.sum(kernel)
        smoothhist.append(np.sum(hist*kernel))  

    smoothhist = np.asarray(smoothhist)
    smoothhist = np.where(smoothhist<1e-16, 0, smoothhist)  

    return smoothhist, hcens

def logr_distribution(rspan, nbins, radius, wghts,
                      perlogR=False, smooth=False):
  ''' get distribution of data with weights 'wghts' against 
  logr. Uses np.histogram to get frequency of a particular
  value of data that falls in each log(r) -> log(r) + dlog(r) bin.
  Apply gaussian kernel smoothing if wanted '''

  # create lnr bins (linearly spaced in lnr)
  hedgs = np.linspace(np.log(rspan[0]), np.log(rspan[1]), nbins+1)  # edges to lnr bins
  hwdths = hedgs[1:]- hedgs[:-1]                               # lnr bin widths
  hcens = (hedgs[1:]+hedgs[:-1])/2                             # lnr bin centres

  # get number frequency in each bin
  hist, hedgs = np.histogram(np.log(radius), bins=hedgs, 
                              weights=wghts, density=None)
  
  if perlogR == True: # get frequency / bin width
      hist = hist/hwdths

  if smooth:
    hist, hcens = gaussian_kernel_smoothing(hist, hcens, smooth)

  return hist, np.exp(hedgs), np.exp(hcens) # units of hedgs and hcens [microns]

def radius_distribution(radius, rspan, nbins, wghts,
                        perR=False, smooth=False):
  ''' get distribution of data with weights 'wghts' against radius.
  Uses np.histogram to get frequency of a particular
  value of data that falls in each r -> r + dr bin.
  Apply gaussian kernel smoothing if wanted '''

  # create r bins linearly spaced in log10(r)
  hedgs = np.logspace(np.log10(rspan[0]), np.log10(rspan[1]), nbins+1)  # edges to lnr bins
  hwdths = hedgs[1:]- hedgs[:-1]                               # lnr bin widths
  hcens = (hedgs[1:]+hedgs[:-1])/2                             # lnr bin centres

  # get number frequency in each bin
  hist, hedgs = np.histogram(radius, bins=hedgs, 
                             weights=wghts, density=None)
  
  if perR == True: # get frequency / bin width
      hist = hist/hwdths

  if smooth:
    hist, hcens = gaussian_kernel_smoothing(hist, hcens, smooth)

  return hist, hedgs, hcens # units of hedgs and hcens [microns]

def domain_mtotdens_distrib(radius, m_sol, eps, rspan, nbins, domainvol,
                            SDprops, smooth=False):
    
    mtot = SDprops.mass(radius, m_sol) # [g]
  
    wght = eps * mtot / domainvol

    hist, hedges, hcens = logr_distribution(rspan, nbins,
                                              radius, wght,
                                              perlogR=True,
                                              smooth=smooth)

    return hist, hedges, hcens

def coord3radius_2Ddistribs(tplt, rspan, c3span, nbins2d, time, sddata,
                            realdrops=True):
  ''' plot the total mass (water+solute) in real droplets over log(r)
  from all the droplets in the domain at each time in tplt list '''
  
  attrs2sel = ["radius", "coord3", "eps"]
  selsddata = pyzarr.select_manytimes_from_sddata(sddata, time, tplt, attrs2sel)
  
  freqs = []
  for t in range(len(tplt)):

    radius = np.asarray(selsddata["radius"][t])
    coord3 = np.asarray(selsddata["coord3"][t]) # [m]

    # create lnr bins (linearly spaced in lnr)
    redgs = np.logspace(np.log10(rspan[0]), np.log10(rspan[1]), nbins2d[0]+1)  # edges to lnr bins
    rwdths = redgs[1:]- redgs[:-1]                               # lnr bin widths
    rcens = (redgs[1:]+redgs[:-1])/2                             # lnr bin centres
    
    # create lnr bins (linearly spaced in lnr)
    c3edgs = np.linspace(c3span[0], c3span[1], nbins2d[1]+1)  # edges to lnr bins
    c3wdths = c3edgs[1:]- c3edgs[:-1]                               # lnr bin widths
    c3cens = (c3edgs[1:]+c3edgs[:-1])/2                             # lnr bin centres

    # get number frequency in each bin
    if realdrops:
      wght = np.asarray(selsddata["eps"][t])
    else:
      wght = None

    freq, redgs, c3edgs = np.histogram2d(radius, coord3, bins=[redgs, c3edgs],
                                          weights=wght, density=False)

    freqs.append(freq.T)

  return freqs, redgs, c3edgs # [%]