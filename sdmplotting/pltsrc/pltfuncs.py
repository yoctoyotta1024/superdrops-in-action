### generic functions for plotting data nicely ###

import matplotlib.pyplot as plt

def save_figure(fig, savedir, savename, show=True):

    fig.savefig(savedir+savename, 
            dpi=400, bbox_inches="tight", 
            facecolor='w', format="png")
    print("Figure .png saved as: "+savedir+savename)

    if show:
        plt.show()

def remove_spines_set_fontsize(axs, labels, ticks, legend):

  for a, ax in enumerate(axs):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel(ax.get_xlabel(), fontsize=labels)
    ax.set_ylabel(ax.get_ylabel(), fontsize=labels) 
    
    xticks, yticks = ax.get_xticks(), ax.get_yticks()
    xticklabels, yticklabels = ax.get_xticklabels(), ax.get_yticklabels()
    ax.set_xticks(xticks, xticklabels, fontsize=ticks)
    ax.set_yticks(yticks, yticklabels, fontsize=ticks)

    if ax.get_legend():
      ax.legend(fontsize=legend)
