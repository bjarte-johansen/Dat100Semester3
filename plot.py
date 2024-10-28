import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
#from fontTools.designspaceLib.types import clamp
#from matplotlib.patches import Rectangle
#from matplotlib.colors import LinearSegmentedColormap
#import matplotlib.collections as mc
from ui import uihelper
import time

# import application specific modules
from defs import *
from locations import *
from plot_grid import *
from plot_graphs import plot_graphs
from utils import clog


# plot markers for all locations
def plot_location_markers():
    def create_patch_dot(xy: tuple[int, int]):
        return mpatches.Circle(xy, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)

    def create_patch_circle(xy: tuple[int, int], user_color: str):
        circle = mpatches.Circle(xy, UI.marker_size, fill=True, linewidth=UI.marker_stroke_size, color=user_color)
        circle.set_edgecolor(user_color + UI.marker_edge_alpha)
        circle.set_facecolor(user_color + UI.marker_face_alpha)
        return circle

    def add_marker(ax, loc):
        # add marker if there are coordinates
        if (loc is not None) and (loc.coordinates is not None):
            ax.add_patch( create_patch_dot(loc.coordinates) )
            ax.add_patch( create_patch_circle(loc.coordinates, loc.color) )

    # could make/use all_locations but we do it in two steps for clarity
    for loc in all_locations:
        add_marker(ax_city_map, loc)
#END plot_location_markers


# plot city map
def plot_city_map(data_key):
    # clear axis
    ax_city_map.cla()

    # plot map of city
    ax_city_map.set_title("Kart Bergen")
    ax_city_map.axis('off')
    ax_city_map.imshow(city_map_image, extent=[0, 2000, 1500, 0])

    # fix the axis limits to avoid auto-scaling
    ax_city_map.set_xlim(0, app.map_dimension[0])  # Example limits, adjust as needed
    ax_city_map.set_ylim(app.map_dimension[1], 0)

    # equal scaling on both axes
    ax_city_map.set_aspect('equal', 'box')

    # plot map markers for locations and user-selected point
    plot_location_markers()

    # 2d plot methods
    if app.plot_grid_countour_lines:
        # plot map contour lines
        plot_grid_contour_lines(ax_city_map, data_key)

    if app.plot_grid_threshold_heatmap:
        # plot heatmap thresholded
        plot_grid_threshold_heatmap(ax_city_map, data_key)

    if app.plot_grid_heatmap:
        # plot heatmap boxed
        plot_grid_heatmap(ax_city_map, data_key)
#END plot_city_map


def plot_pollution_display():
    keys = [KEY_NOX, KEY_APD]
    for key in keys:
        # calculate pollution percentage
        ratio = np.mean(loc_nordnes.data_view[key]) / np.mean(loc_kronstad.data_view[key])
        val = ratio * 100
        val = f"{val:.2f}%"

        # set text input values
        key = key.lower() + "_pollution_percentage"
        uihelper.text_input_map[key].set_text( val )
# END plot_pollution_display


def plot_app():
    clog("plot_app")

    # plot NOX graphs
    plot_graphs(ax_nox, KEY_NOX)

    # plot NOX graphs
    plot_graphs(ax_apd, KEY_APD)

    # plot map (change key to plot APD or NOX)
    plot_city_map(app.map_overlay_key)

    # plot pollution display
    plot_pollution_display()

    # draw the plot
    plt.draw()

    # show plot
    plt.show()
# END plot_app