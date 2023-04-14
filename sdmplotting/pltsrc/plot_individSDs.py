import numpy as np
import matplotlib.pyplot as plt

def plot_individ_radiusgrowths(fig, ax, time, radii):
  ''' plots of droplet radii growth given array of radii
  of shape [time, SDs] '''

  lines = [] 
  for i in range(radii.shape[1]):
    line = ax.plot(time, radii[:,i], linewidth=0.8)
    lines.append(line)

  ax.set_xlabel('time /s')
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

  ax.set_xlabel('time /s')
  ax.set_ylabel('multiplicity, \u03BE')

  fig.tight_layout()

  return lines

def plot_individ_m_sols(fig, ax, time, m_sols):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(m_sols.shape[1]):
    line = ax.plot(time, m_sols[:,i], linewidth=0.8)
    lines.append(line)
     
  ax.set_xlabel('time /s')
  ax.set_ylabel('solute mass /g')
  
  fig.tight_layout()

  return lines

def plot_individ_coords(fig, ax, time, zcoords, coordlab):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(zcoords.shape[1]):
    line = ax.plot(time, zcoords[:,i]/1000, linewidth=0.8)
    lines.append(line)
     
  ax.set_xlabel('time /s')
  ax.set_ylabel(coordlab+' /km')
  
  fig.tight_layout()

  return lines
