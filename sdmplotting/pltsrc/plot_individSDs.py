import numpy as np
import matplotlib.pyplot as plt
import random

from ..datsrc import pyzarr

def plot_individ_radiusgrowths(fig, ax, time, radii):
  ''' plots of droplet radii growth given array of radii
  of shape [time, SDs] '''

  lines = [] 
  for i in range(radii.shape[1]):
    line = ax.plot(time, radii[:,i], linewidth=0.8)
    lines.append(line)

  ax.set_xlabel('time /min')
  ax.set_yscale('log')
  ax.set_ylabel('droplet radius /\u03BCm')

  fig.tight_layout()

  return lines

def plot_individ_radiusgrowths_with_supersat(fig, ax, time, radii, supersat):
  '''plots of droplet radii growth against height
   with supersaturatio curve superimposed on top'''
  
  lines = plot_individ_radiusgrowths(fig, ax, time, radii)

  axb = ax.twinx()
  axb.plot(time, supersat[:,0], linewidth=1.5, color='k', label='s')
  axb.hlines(0, np.amin(time), np.amax(time),
             color='gray', linestyle='--', label="s=0") 
  axb.set_ylabel('supersaturation, s')
  axb.legend(fontsize=13)

  fig.tight_layout()
  
  return fig, [ax, axb], lines

def plot_individ_multiplicities(fig, ax, time, epss):
  ''' plots of droplet multiplicty (eps) evolution given array of radii
  of shape [time, SDs] '''
  
  lines = [] 
  for i in range(epss.shape[1]):
    line = ax.plot(time, epss[:,i], linewidth=0.8)
    lines.append(line)

  ax.set_xlabel('time /min')
  ax.set_ylabel('multiplicity, \u03BE')

  fig.tight_layout()

  return lines

def plot_individ_m_sols(fig, ax, time, m_sols):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(m_sols.shape[1]):
    line = ax.plot(time, m_sols[:,i], linewidth=0.8)
    lines.append(line)
     
  ax.set_xlabel('time /min')
  ax.set_ylabel('solute mass /g')
  
  fig.tight_layout()

  return lines

def plot_individ_coords(fig, ax, time, coords, coordlab):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(coords.shape[1]):
    line = ax.plot(time, coords/1000, linestyle="", marker=".", markersize=0.4)
    lines.append(line)
     
  ax.set_xlabel('time /min')
  ax.set_ylabel(coordlab+' /km')
  
  fig.tight_layout()

  return lines

def plot_superdrop_zxmotion(fig, ax, xcoords, zcoords,  arrows=True):

  lines = ax.plot(xcoords, zcoords, linestyle="", marker=",")[0]

  if arrows:
    n2plt = min(300, xcoords.shape[1])
    drops2arrow = random.sample(list(range(0, xcoords.shape[1], 1)), n2plt)
    for n in drops2arrow: # must loop over drops to get nice positioning of arrows
      x = xcoords[:,n][np.logical_not(np.isnan(xcoords[:,n]))]
      z = zcoords[:,n][np.logical_not(np.isnan(zcoords[:,n]))]
      
      u = np.diff(x)
      w = np.diff(z)
      norm = np.sqrt(u**2+w**2) 
      pos_x = x[:-1] + u/2
      pos_z = z[:-1] + w/2
      
      sl = list(range(0, len(pos_x), 100))
      ax.quiver(pos_x[sl], pos_z[sl], (u/norm)[sl], (w/norm)[sl],
              angles="xy", zorder=5, pivot="mid", scale=50)

  ax.set_xlabel("x / km")
  ax.set_ylabel("z / km")

  fig.tight_layout()

  return lines

def randomsample_plotsupers(fig, axs, time, sddata, nsample):
  
  minid, maxid = 0, sddata.totnsupers[0] # largest value of ids to sample
  ids2plot = random.sample(list(range(minid, maxid, 1)), nsample)
  
  radii = pyzarr.attrtimeseries_for_superdropssample(sddata, "radius", ids=ids2plot) 
  m_sols = pyzarr.attrtimeseries_for_superdropssample(sddata, "m_sol", ids=ids2plot)
  epss = pyzarr.attrtimeseries_for_superdropssample(sddata, "eps", ids=ids2plot)
  zcoords = pyzarr.attrtimeseries_for_superdropssample(sddata, "coord3", ids=ids2plot) 
  xcoords = pyzarr.attrtimeseries_for_superdropssample(sddata, "coord1", ids=ids2plot) 
  ycoords = pyzarr.attrtimeseries_for_superdropssample(sddata, "coord2", ids=ids2plot) 

  lines = []
  axs = axs.flatten()
  lines.extend(plot_individ_radiusgrowths(fig, axs[0], time.mins, radii))
  lines.extend(plot_individ_multiplicities(fig, axs[1], time.mins, epss))
  lines.extend(plot_individ_m_sols(fig, axs[2], time.mins, m_sols))
  lines.extend(plot_individ_coords(fig, axs[3], time.mins, zcoords, "z coord"))
  lines.extend(plot_individ_coords(fig, axs[4], time.mins, xcoords, "x coord"))
  lines.extend(plot_individ_coords(fig, axs[5], time.mins, ycoords, "y coord"))

  fig.tight_layout()

  return lines

def randomsample_plotsuperdrop_zxmotio(fig, ax, sddata, nsample):
  
  n2plt = min(nsample, sddata.totnsupers[0])
  ids2plot = random.sample(list(range(0, sddata.totnsupers[0], 1)), n2plt)
  zcoords = pyzarr.attr_timeseries_for_nsuperdrops_sample(sddata, "coord3", ids=ids2plot) / 1000  #[km]
  xcoords = pyzarr.attr_timeseries_for_nsuperdrops_sample(sddata, "coord1", ids=ids2plot)  / 1000 #[km]

  lines = plot_superdrop_zxmotion(fig, ax, xcoords, zcoords,  arrows=False)

  return lines