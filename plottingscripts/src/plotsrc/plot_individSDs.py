import numpy as np
import matplotlib.pyplot as plt

def maxmin_radii_label(r, allradii):
  ''' if radius, r, is biggest or smallest
  out of allradii, return appropraite label'''

  label = None
  if r == np.amin(allradii):
      label = '{:.2g}\u03BCm'.format(r)
      label = 'min r0 = '+label
  elif r == np.amax(allradii):
      label = '{:.2g}\u03BCm'.format(r)
      label = 'max r0 = '+label

  return label

def plot_individ_radiusgrowths(fig, ax, time, radii):
  ''' plots of droplet radii growth given array of radii
  of shape [time, SDs] '''

  lines = [] 
  for i in range(radii.shape[1]):
    label = maxmin_radii_label(radii[0,i], radii[0,:])
    line = ax.plot(time, radii[:,i], linewidth=0.8, label=label)
    lines.append(line)

  ax.set_xlabel('time /s')
  ax.set_yscale('log')
  ax.set_ylabel('droplet radius /\u03BCm')
  ax.legend(fontsize=13)

  fig.tight_layout()

  return lines

def plot_individ_radiusgrowths_with_supersat(fig, ax, time, radii, supersat):
  '''plots of droplet radii growth against height
   with supersaturatio curve superimposed on top'''
  
  lines = plot_individ_radiusgrowths(fig, ax, time, radii)
  ax.legend(fontsize=13, loc="upper left")

  axb = ax.twinx()
  axb.plot(time, supersat[:,0], linewidth=1.5, color='k', label='s')
  axb.hlines(0, np.amin(time), np.amax(time), color='gray', linestyle='--') 
  axb.set_ylabel('supersaturation, s')
  axb.legend(fontsize=13)

  fig.tight_layout()
  
  return fig, [ax, axb], lines

def plot_individ_multiplicities(fig, ax, time, epss, radii):
  ''' plots of droplet multiplicty (eps) evolution given array of radii
  of shape [time, SDs] '''
  
  lines = [] 
  for i in range(epss.shape[1]):
    label = maxmin_radii_label(radii[0,i], radii[0,:]) 
    line = ax.plot(time, epss[:,i], label=label, linewidth=0.8)
    lines.append(line)

  ax.set_xlabel('time /s')
  ax.set_ylabel('multiplicity, \u03BE')
  ax.legend(fontsize=13)

  fig.tight_layout()

  return lines

def plot_individ_m_sols(fig, ax, time, m_sols, radii):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(m_sols.shape[1]):
    label = maxmin_radii_label(radii[0,i], radii[0,:]) 
    line = ax.plot(time, m_sols[:,i], label=label, linewidth=0.8)
    lines.append(line)
     
  ax.set_xlabel('time /s')
  ax.set_ylabel('solute mass /g')
  ax.legend(fontsize=13)
  
  fig.tight_layout()

  return lines

def plot_individ_zcoords(fig, ax, time, zcoords, radii):
  ''' plots of droplet radii growth '''
  
  lines = []
  for i in range(zcoords.shape[1]):
    label = maxmin_radii_label(radii[0,i], radii[0,:]) 
    line = ax.plot(time, zcoords[:,i]/1000, label=label, linewidth=0.8)
    lines.append(line)
     
  ax.set_xlabel('time /s')
  ax.set_ylabel('superdroplet height, z /km')
  ax.legend(fontsize=13)
  
  fig.tight_layout()

  return lines
