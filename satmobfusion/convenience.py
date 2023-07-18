import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

f_size = matplotlib.rcParams['font.size'] #used as fontsize
t_size = matplotlib.rcParams['font.size'] #used as ticksize
t_rotation = "horizontal" #used as tick rotation
l_scilim = -5 #10^(l_scilim) used as left scilimit
r_scilim = 5 #10^(r_scilim) used as right scilimit
xl_scilim = l_scilim
xr_scilim = r_scilim
yl_scilim = l_scilim
yr_scilim = r_scilim

pad_inches = 0.05


## Add reverse geocoding functions here

def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)
    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

def get_rectangular_polygon_from_bounding_box(lon_min, lon_max, lat_min, lat_max):
    # return [(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny),(minx,maxy)]
    return [(lon_min,lat_max),(lon_max,lat_max),(lon_max,lat_min),(lon_min,lat_min),(lon_min,lat_max)]


def plot(x, y, ey=[], ex=[], frame=[], kind="scatter", marker_option=".",
         ls="-", lw=1, label="", color="royalblue", zorder=1, alpha=1.,
         output_folder="", filename=""):
    """
    Erstellt einen Plot (plot, scatter oder errorbar).

    Parameters
    ----------
    x : array-like
        x-Werte
    y : array-like
        y-Werte
    ey : array_like
        Fehler auf die y-Werte
    ex : array_like
        Fehler auf die x-Werte
    kind : string
        Die Art des plots
        Möglich sind "plot" (default), "scatter" und "errorbar".
    marker_option : string
        Definiert die Option marker bei Plottyp "plot" oder "scatter" sowie
        die Option fmt bei Plottyp "errorbar".
    ls : string
        linestyle
    lw : float
        linewidth
    zorder : int
        Die "Ebene" der zu plottenden Daten

    return frame
    """
    #error arrays
    if len(ex)==1:
        ex = np.ones(len(x))*ex[0]
    elif ex==[]:
        ex = np.zeros(len(x))
    if len(ey)==1:
        ey = np.ones(len(y))*ey[0]

    #plotting
    fig, plot = plt.subplots(1,1) if frame == [] else frame
    if kind=="plot":
        plot.plot(x, y, color=color, marker=marker_option, ls=ls, lw=lw, label=label, zorder=zorder, alpha=alpha)
    elif kind=="scatter":
        plot.scatter(x, y, color=color, marker=marker_option, lw=lw, label=label, zorder=zorder, alpha=alpha)
    elif kind=="errorbar":
        plot.errorbar(x, y, ey, ex, color=color, fmt=marker_option, ls="", lw=lw, label=label, zorder=zorder, alpha=alpha)
    elif kind=="bar":
        plot.bar(x, y, color=color, label=label, zorder=zorder, alpha=alpha)

    #saving plot
    if filename!="":
        fig.savefig(output_folder+filename,bbox_inches='tight',pad_inches=pad_inches)

    return [fig,plot]

def fig_ax_setup(fig, suptitle=None, title=None,
                 xlabel=None, ylabel=None,
                 xlim=None, ylim=None,
                 xticks=None, yticks=None,
                 xtick_rotation=None, ytick_rotation=None,
                 xscale="linear", yscale="linear",
                 grid=True, legend_position="best", bbox_to_anchor=None, ncol=1, legend_order=None,
                 y_suptitle=1.05, x_axis_formatting=False, y_axis_formatting=False,
                 filename=None, dpi=None, transparent=0):

    """
    Defines the setup of a plot.

    Parameters
    ----------
    fig : matplotlib.Figure object (or tuple of length 2 ([fig,ax]))
        Figure object (or [fig,ax] tuple) to be set-up.
    suptitle : string
        (superordinate) title of the figure object
    title : string
        title of the axis object
    xlabel / ylabel : string
        labels/quanitities on x- and y-axis
    xlim / ylim : tuple
        axes' limits
    xticks / yticks : list
        axes' ticks
    xscale / yscale : string
        {"linear","log"}. Default is "linear".
    xtick_rotation / ytick_rotation : string or int
        Rotation of the x- and y-axis, respectively.
        Default is None.
    grid : bool
        True, if a grid is wanted. Else False.
    legend_position : None or int or string
        legend position defined by an integer or a string like "upper left".
        Choose None for no legend.
        Default is "best".
    bbox_to_anchor : None or tuple
        Position of legend box anchor.
        Use bbox_to_anchor=(1, 0.5) and legend_position="center left" to place
        legend to the right of the figure.
    ncol : int
        Number of columns in the legend.
        Default is 1.
    legend_order : list
        The order in which legend entries should appear in the legend.
        Can also be used to omit showing a subset of the legend entries.
    y_suptitle : float
        y-position of the suptitle in factors of the y-size of the figure.
        Default is 1.05.
    x_axis_formatting : bool
        Boolean whether to do axis_formatter commands on the x axis or not.
    y_axis_formatting : bool
        Boolean whether to do axis_formatter commands on the y axis or not.
    """

    #frame of figure
    if type(fig) is list or type(fig) is tuple:
        fig,ax = fig
    else: #new standard case
        ax = fig.get_axes()

    try:
        ax_arr = np.array(ax)
    except:
        ax_arr = [ax]
    n_ax = len(ax_arr)

    #suptitle and title
    if suptitle is not None:
        fig.suptitle(suptitle,y=y_suptitle)
    if title is not None:
        if n_ax!=1:
            for ax,i in zip(ax_arr,list(range(n_ax))):
                ax.set_title(title[i])
        else:
            ax_arr[0].set_title(title)

    #axes labels, limits, ticks, scilimits, and scale
    if ylabel is not None:
        try:
            ax_arr[0].set_ylabel(ylabel)
        except AttributeError:
            #TODO: this currently assumes a sharey="row" in the figure
            for i in range(np.shape(ax_arr)[0]):
                ax_arr[i][0].set_ylabel(ylabel)
    # for ax_row in ax_arr:
    for ax in ax_arr.flatten().tolist():
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        if xticks is not None:
            ax.set_xticks(xticks)
        if yticks is not None:
            ax.set_yticks(yticks)
        if xtick_rotation is not None:
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_rotation(xtick_rotation)
        if ytick_rotation is not None:
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_rotation(ytick_rotation)
        if x_axis_formatting:
            # axis_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
            ax.ticklabel_format(style="sci",axis="x",scilimits=(l_scilim,r_scilim))
            # axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            axis_formatter = matplotlib.ticker.FuncFormatter(y_fmt)
            axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            ax.xaxis.set_major_formatter(axis_formatter)
        if y_axis_formatting:
            # axis_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
            # ax.ticklabel_format(style="sci",axis="y",scilimits=(l_scilim,r_scilim))
            # axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            axis_formatter = matplotlib.ticker.FuncFormatter(y_fmt)
            axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            ax.yaxis.set_major_formatter(axis_formatter)
        if ax.get_xscale()!=xscale:
            ax.set_xscale(xscale)
        if ax.get_yscale()!=yscale:
            ax.set_yscale(yscale)

        #grid
        ax.grid(grid,zorder=0)

        #legend
        if legend_position is not None and len(ax.get_legend_handles_labels()[1])>0:
            if legend_order is None:
                ax.legend(loc=legend_position, bbox_to_anchor=bbox_to_anchor, ncol=ncol)
            else:
                handles, labels = plt.gca().get_legend_handles_labels()
                ax.legend([handles[idx] for idx in legend_order],[labels[idx] for idx in legend_order], loc=legend_position, bbox_to_anchor=bbox_to_anchor, ncol=ncol)

    #saving plot
    if filename is not None:
        save_figure(fig, filename, dpi, transparent)

def y_fmt(y, pos):
    decades = [1e9, 1e6, 1e3, 1e0, 1e-3, 1e-6, 1e-9 ]
    suffix  = ["G", "M", "k", "" , "m" , "mu", "n"  ]
    if y == 0:
        return str(0)
    for i, d in enumerate(decades):
        if np.abs(y) >=d:
            val = y/float(d)
            signf = len(str(val).split(".")[1])
            if signf == 0:
                return '{val:d} {suffix}'.format(val=int(val), suffix=suffix[i])
            else:
                if signf == 1:
                    # print(val, signf)
                    if str(val).split(".")[1] == "0":
                        return '{val:d} {suffix}'.format(val=int(round(val)), suffix=suffix[i])
                tx = "{"+"val:.{signf}f".format(signf = signf) +"} {suffix}"
                return tx.format(val=val, suffix=suffix[i])

                #return y
    return y

def save_figure(fig, filename="figure.png", dpi=None, transparent=0):
    """
    Saves a figure that has already been set-up before completely.

    Parameters
    ----------
    fig : matplotlib.Figure object (or tuple of length 2 ([fig,ax]))
        Figure object (or [fig,ax] tuple) to be saved as a file.
    TODO
    """

    #frame of figure
    if type(fig) is list or type(fig) is tuple:
        fig,ax = fig
    else: #new standard case
        ax = fig.get_axes()

    #create path if it does not exist yet
    path = "/".join(filename.split("/")[:-1])
    if not os.path.exists(path) and path!="":
        os.makedirs(path)

    if filename is not None:
        if transparent in [0,1]:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=pad_inches, transparent=transparent)
        else: #transparency with alpha between 0 and 1
            alpha = transparent
            fig.patch.set_facecolor('white'), fig.patch.set_alpha(alpha)

            try:
                ax.patch.set_facecolor('white'), ax.patch.set_alpha(alpha)
            except: #ax is in fact a list of ax objects
                for a in ax:
                    try:
                        a.patch.set_facecolor('white'), a.patch.set_alpha(alpha)
                    except: #ax is in fact a list of list of ax objects
                        for b in a:
                            b.patch.set_facecolor('white'), b.patch.set_alpha(alpha)

            # If we don't specify the edgecolor and facecolor for the figure when
            # saving with savefig, it will override the value we set earlier!
