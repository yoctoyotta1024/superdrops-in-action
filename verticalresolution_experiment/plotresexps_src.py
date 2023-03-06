import sys
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 40})

apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023"+\
        "/superdrops_in_action/"
sys.path.append(apath)

from sdmplotting.datsrc import *
from sdmplotting.pltsrc import *

def smoothsig(meanSDsperGBx, totnsupers):
  
  # smooth = False
  # smooth = 0.62*(meanSDsperGBx**(-1/5))
  smooth = 0.01*8192/(totnsupers)
  
  return smooth

def calc_nthradiusmoment(eps, radius=1, n=0, norm=True):

  radius = radius / 1e6                                   # radius [m] (ie. not microns)
  nthmoment = np.sum(np.multiply(radius**n, eps), axis=1) # [m^n]

  if norm:
    nthmoment = nthmoment / np.sum(eps, axis=1) # divide by 0th moment
  
  return nthmoment

def calc_nthmassmoment(eps, mass, domainvol, n=0):

  nthmoment = []
  for m, e in zip(mass, eps):
    if n==0:
      nthm = 1
    else:
      nthm = (m / 1000)**n                                              # mass [Kg] ie. not grams
    moment = np.sum(np.multiply(nthm, e))
    nthmoment.append(moment)
  nthmoment = nthmoment / domainvol                           # [Kg^n / m^3]

  return nthmoment

def plot_meandistrib_fromhists(ax, hcens, hedges, hists2avg, smooth, time, tplt, color):
  
  stderr = np.std(hists2avg, axis=0) / np.sqrt(hists2avg.shape[0])
  mean = np.mean(hists2avg, axis=0)

  if smooth:
    stderr = histos.gaussian_kernel_smoothing(stderr, np.log(hcens), smooth)[0] 
    mean = histos.gaussian_kernel_smoothing(mean, np.log(hcens), smooth)[0] 

  line = plot_distribs.plot_distrib(ax, mean, hedges, hcens, time, 
                                    tplt, c=color, smooth=smooth,
                                    ylog=False)                                        
  ax.fill_between(hcens, mean-stderr, mean+stderr, color=color, alpha=0.2)

  return line

def add_golovin_sol(ax, tplt, rspan, nbins, SDprops, colors):
  
  for k in range(len(tplt)):
    n_a = 2**(23)
    r_a = 30.531e-6
    golsol, hcens = plot_golovin.golovin_analytical(rspan, tplt[k], nbins, 
                                                    n_a, r_a, SDprops.RHO_L)
    plot_golovin.plot_golovin_analytical_solution(ax, hcens, golsol*2.077, k, colors[k])
    
    if k == 0:
      golline4leg = plot_golovin.plot_golovin_analytical_solution(ax, hcens, golsol*2.077, k, colors[k])[0]
  
  return golline4leg