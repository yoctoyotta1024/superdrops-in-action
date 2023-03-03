### generic functions for plotting data nicely ###

import matplotlib.pyplot as plt

def save_figure(fig, savedir, savename, show=True):

    fig.savefig(savedir+savename, 
            dpi=400, bbox_inches="tight", 
            facecolor='w', format="png")
    print("Figure .png saved as: "+savedir+savename)

    if show:
        plt.show()