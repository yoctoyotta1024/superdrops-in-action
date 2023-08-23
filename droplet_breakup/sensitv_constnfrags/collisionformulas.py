import numpy as np
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

def rho_w():
  return 1000 # density of water [kg/m^3]

def surft():
  return 7.28e-2 # surface tension of water [N/m]

def simmel_terminalvelocity(radius):
  """terminal velocity according
  to Simmel et al. 2002 formulation"""

  watermass = 4.0/3 * np.pi * rho_w() * radius**3 #[kg]
  mass = watermass * 1000 # [grams]
  
  alpha = np.where(radius < 1.73897e-3, 17.32, 9.17)
  beta = np.where(radius < 1.73897e-3, 1.0/6, 0.0)

  alpha = np.where(radius < 7.5582e-4, 49.62, alpha)
  beta = np.where(radius < 7.5582e-4, 1.0/3, beta)

  alpha = np.where(radius < 6.7215e-5, 4579.5, alpha)
  beta = np.where(radius < 6.7215e-5, 2.0/3, beta)

  terminalv = alpha * mass**beta #[m/s]

  return terminalv

def collision_kinetic_energy(r1, r2):

  radiiratio = r1**3 * r2**3 / (r1**3 + r2**3 )
  v1 = simmel_terminalvelocity(r1)
  v2 = simmel_terminalvelocity(r2)
  
  cke = 2.0 / 3.0 * rho_w() * np.pi * radiiratio * (v1-v2)**2

  return cke

def minsurfenergy(r1, r2):
  
  smallr = np.where(r1 < r2, r1, r2)
  
  return 4 * np.pi * surft() * smallr**2

def coalsurfenergy(r1, r2):

  coalsurfe = 4 * np.pi * surft() * (r1**3 + r2**3)**(2/3) 

  return coalsurfe

def nocoll_breakup_coal_or_rebound(r1, r2):

  cke = collision_kinetic_energy(r1, r2)
  surfe_small = minsurfenergy(r1, r2) 
  surfe_coal = coalsurfenergy(r1, r2) 
  
  coalbure = np.where(cke < 1e-30, -1, 0) # no collision = -1, rebound = 0
  coalbure = np.where(cke > surfe_small, 1, coalbure) # coalescence = 1
  coalbure = np.where(cke > surfe_coal, 2, coalbure) # breakup = 2

  return coalbure

def plot_coal_breakup_or_rebound(fig, ax, r1, r2):
    
    rr1, rr2 = np.meshgrid(r1, r2)
    coalbure = nocoll_breakup_coal_or_rebound(rr1*1e-6, rr2*1e-6)
    coalbure = np.where(rr1 > rr2, np.nan, coalbure) # ensure data only for rr1 < rr2

    levels = [-1.5,-0.5,0.5,1.5,2.5]
    levellabs = ["no collision", "rebound", "coalescence", "breakup"]
    cont = ax.contourf(rr1, rr2, coalbure, levels=levels,
                       cmap=cm.Set3)
    cols = ["gold", "lightblue", "mediumorchid", "green"]
    ax.contour(rr1, rr2, coalbure, levels=levels,
               colors=cols, linewidths=0.8)
     
    cbar = fig.colorbar(cont, ax=ax, location="right")
    cbartcks = (cbar.get_ticks()[1:] + cbar.get_ticks()[:-1])/2
    cbar.ax.set_yticks(cbartcks, levellabs)
    x = cbar.ax.get_xlim()
    cbar.ax.hlines(levels, x[0], x[1], color=cols)

    ax.fill_between(r1, r2, color="lightgrey")

    ax.set_aspect("equal")
    ax.set_xlabel("small radius /\u03BCm")
    ax.set_ylabel("large radius /\u03BCm")
    ax.set_xscale("log")
    ax.set_yscale("log")

def plot_coal_breakup_or_rebound_ondist(fig, ax, r1, r2, dist1, dist2):
    
    rr1, rr2 = np.meshgrid(r1, r2)
    dist = np.outer(dist1/np.sum(dist1), dist2/np.sum(dist2))
    dist = np.where(dist == 0, np.nan, dist)
    dist = np.where(rr1 > rr2, np.nan, dist)
    cont = ax.contourf(rr1, rr2, dist, cmap="cividis", norm=LogNorm())
    
    coalbure = nocoll_breakup_coal_or_rebound(rr1*1e-6, rr2*1e-6)
    levels = [-1.5,-0.5,0.5,1.5,2.5]
    levellabs = ["no collision", "rebound", "coalescence", "breakup"]
    cols = ["gold", "lightblue", "mediumorchid", "green"]
    coalbure = np.where(rr1 > rr2, np.nan, coalbure)
    ax.contour(rr1, rr2, coalbure, levels=levels, colors=cols)
     
    cbar = fig.colorbar(cont, ax=ax, location="right")

    ax.fill_between(r1, r2, color="lightgrey")

    ax.set_aspect("equal")    
    ax.set_xlabel("small radius /\u03BCm")
    ax.set_ylabel("large radius /\u03BCm")
    ax.set_xscale("log")
    ax.set_yscale("log")