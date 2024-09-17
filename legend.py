from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib import cm
import sys
import json
import numpy as np
import math
from scipy.interpolate import make_interp_spline

verbose = False

def n_orders(_min, _max):
    if _min < 0:
        return 0, 0
    if verbose: print(f'min={_min}, max={_max}')
    mino = int(math.log10(_min))
    maxo = int(math.log10(_max))
    return mino, maxo

def legend_helper(values, sizes, nstops=4, log_scale=True):
    if verbose:
        print(f'values=\n{values}')
        print(f'sizes=\n{sizes}')
    uvals, unique_indices = np.unique(values, return_index=True)
        
    usizes = [ sizes[i] for i in unique_indices]

    all_vals = np.array([uvals, usizes]).transpose()
    all_vals = np.sort(all_vals, axis=0)

    val_to_size = make_interp_spline(all_vals[:, 0], all_vals[:, 1])
    minv = np.min(values)
    maxv = np.max(values)
    min_order, max_order = n_orders(minv, maxv)
    val_range = maxv-minv
    vstops = []
    sstops = []
    if min_order == 0 and max_order == 0:
        log_scale = False
    if not log_scale:
        dv = val_range/(nstops-1)
        v = minv
        for i in range(nstops):
            if v > 10:
                vstops.append(int(v))
            else:
                vstops.append(v)
            sstops.append(float(val_to_size(v)))
            v += dv
    else:
        do = (max_order - min_order) // (nstops-1)
        ord = min_order 
        for i in range(nstops):
            vstops.append(math.pow(10, ord))
            ord += do
            sstops.append(val_to_size(vstops[-1]))
    
    if verbose:
        print(f'value stops: {vstops}')
        print(f'size stops: {sstops}')
    return vstops, sstops

def make_size_text(stops):
    labels = []
    if verbose: print(f'size_text: stops are {stops}')
    mino, maxo = n_orders(stops[0], stops[1])
    if mino >= 0 and maxo <= 4:
        labels= [ f'{s}' for s in stops ]
        for i, l in enumerate(labels):
            if len(l) > 4:
                labels[i] = f'{stops[i]:.1f}'
        return labels
    else:
        return [ f'{s:.1e}' for s in stops ]

def make_size_legend(values, sizes, nstops, shape='o', title='None',        
                     log_scale=True, spacing=0.5, ax=None, facecolor='white',
                     edgecolor='black', loc='upper right', offset=(1, 1),
                     show_frame=False):
    value_stops, size_stops = legend_helper(values, sizes, nstops, 
                                            log_scale=log_scale)
    size_text = make_size_text(value_stops)
    size_values = size_stops
    if verbose:
        print(f'sizes are {size_values}')
        print(f'size text is {size_text}')
    custom_circles = [ plt.Line2D(range(1), range(1), markersize=math.sqrt(s),
                                  color='white', marker=shape,
                                  markerfacecolor=facecolor,
                                  markeredgecolor=edgecolor)
                       for s in size_values ]
    heights = np.sqrt(size_values)
    # spacing will be multiplied by fontsize = 10
    dist = 0.5*(heights[-2] + heights[-1])
    spacing = 0.8*(dist)/10

    if ax is None:
        size_legend = plt.legend(custom_circles,
                         [ f"{s}" for s in size_text ],
                         title=title, title_fontproperties={'weight': 'bold'},loc=loc, bbox_to_anchor=offset,
                         labelspacing=spacing, frameon=show_frame)
    else:
        size_legend = ax.legend(custom_circles,
                         [ f"{s}" for s in size_text ],
                         title=title, title_fontproperties={'weight': 'bold'},loc=loc, bbox_to_anchor=offset,
                         labelspacing=spacing, frameon=show_frame)
    return size_legend

if __name__ == '__main__':
    data = np.random.random((100, 4))
    sizes = 500*data[:,2]
    acmap = plt.get_cmap('viridis')
    minv = np.min(data[:,2])
    maxv = np.max(data[:,2])
    fig, axes = plt.subplots(1,1,figsize=(12,6))
    axes.scatter(x=data[:,0], y=data[:,1], s=sizes, c=[acmap(v) for v in data[:,3]], edgecolor='black')

    size_legend = make_size_legend(data[:,2], sizes, 5, log_scale=False, 
                                   spacing=1.5, title='Size', facecolor=acmap(0.5), show_frame=True)
    axes.add_artist(size_legend)
    plt.title('Bubble chart of random dataset')

    plt.show()