### generic functions for plotting data nicely ###
import numpy as np
import matplotlib.pyplot as plt

def save_figure(fig, savedir, savename, show=True):

    fig.savefig(savedir+savename, 
            dpi=400, bbox_inches="tight", 
            facecolor='w', format="png")
    print("Figure .png saved as: "+savedir+savename)

    if show:
        plt.show()

def ticks_withinlims(ticks, ticklabels, lims):
  
  ticklabels = np.where(ticks>=lims[0], ticklabels, "")
  ticklabels = np.where(ticks<=lims[1], ticklabels, "")
  
  ticks = ticks[ticks>=lims[0]]
  ticks = ticks[ticks<=lims[1]]

  return ticks, ticklabels[ticklabels!=""]

def remove_spines_set_fontsize(axs, labels, ticks, legend):


  for a, ax in enumerate(axs):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    

    xlims = ax.get_xlim() 
    ylims = ax.get_ylim() 

    xticks, xticklabels = ticks_withinlims(ax.get_xticks(),
                                           ax.get_xticklabels(), xlims) 
    yticks, yticklabels = ticks_withinlims(ax.get_yticks(),
                                           ax.get_yticklabels(), ylims) 
    
    ax.set_xlim(xlims), ax.set_ylim(ylims)
    ax.set_xticks(xticks, xticklabels, fontsize=ticks)
    ax.set_yticks(yticks, yticklabels, fontsize=ticks)

    ax.set_xlabel(ax.get_xlabel(), fontsize=labels)
    ax.set_ylabel(ax.get_ylabel(), fontsize=labels) 

    if ax.get_legend():
      ax.legend(fontsize=legend)
