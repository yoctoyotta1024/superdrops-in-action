### generic functions for plotting data nicely ###

import matplotlib.pyplot as plt

def save_figure(fig, savedir, savename, show=True):

    fig.savefig(savedir+savename, 
            dpi=400, bbox_inches="tight", 
            facecolor='w', format="png")
    print("Figure .png saved as: "+savedir+savename)

    if show:
        plt.show()
    
def axplt(ax, x, y, xlab=None, ylab=None, lab="_nolegend_",
          c=0, l='-', lw=1):
    
    if type(c)==type(0):
        c= 'C'+str(c)
    
    line = ax.plot(x,y, label=lab, color=c, linestyle=l, linewidth=lw)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    return line
