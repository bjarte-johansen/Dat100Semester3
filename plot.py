import pandas as pd

import matplotlib.patches as mpatches

import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.collections as mc


# import application specific modules
from defs import *
from locations import *
from plot_grid import *


# Make markers at fixed and user-selected locations
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


# plot data for a location, allowing shadowing parameters
def plot_data(axis, day_index_list_arg, loc, data, data_key):
    date_range = pd.date_range(start=app.date_range.start_date, end=app.date_range.end_date)

    if loc.data_lines[data_key] is not None:
        loc.data_lines[data_key].set_data(date_range, data)
        return loc.data_lines[data_key]
    else:
        loc.data_lines[data_key] = axis.plot(date_range, data, color = loc.color)[0]
        return loc.data_lines[data_key]


def plot_user_selected_location(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key):
    # assign to a shorter variable name
    loc_user = app.user_location

    # extract data, plot and draw horisontal average line for user-selected location
    if loc_user is not None and loc_user.coordinates is not None:
        # allocate data_view
        loc_user.data_view[data_key] = np.empty(number_of_days_to_plot, dtype=int)

        # iterate over days
        for i in range(0, number_of_days_to_plot):
            # take measurement value
            for loc in fixed_locations:
                loc.measurement_value = loc.data_view[data_key][i]

            # compute estimated value at point
            loc_user.data_view[data_key][i] = app.get_estimated_value_at_point_func(fixed_locations, loc_user.coordinates)

        # set/update user-point NOX values
        legend_lines.append( plot_data(axis, day_index_list, loc_user, loc_user.data_view[data_key], data_key) )

        # draw horisontal average line
        axis.axhline(np.mean(loc_user.data_view[data_key]), color=UI.Colors.user, linestyle='--', linewidth=1)
# END plot_user_selected_location


def plot_fixed_locations(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key):
    # extract data, plot and draw horisontal average line for fixed locations
    for loc in fixed_locations:
        # extract into data-view
        loc.data_view[data_key] = extract_data_interval(loc.historical_data[data_key], app.days_interval[0], app.days_interval[0] + number_of_days_to_plot)

        # plot data for fixed locations, add to legend
        legend_lines.append( plot_data(axis, day_index_list, loc, loc.data_view[data_key], data_key) )

        # draw horisontal average line
        axis.axhline(np.mean(loc.data_view[data_key]), color=loc.color, linestyle='--', linewidth=1)
# END plot_fixed_locations


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

    # rendering methods that require grid samples
    if app.plot_grid_countour_lines or app.plot_grid_threshold_heatmap or app.plot_grid_heatmap:
        if app.plot_grid_countour_lines:
            # plot map contour lines
            plot_grid_contour_lines(ax_city_map, data_key)

        if app.plot_grid_threshold_heatmap:
            # plot heatmap thresholded
            plot_grid_threshold_heatmap(ax_city_map, data_key)

        if app.plot_grid_heatmap:
            # plot heatmap boxed
            plot_grid_heatmap(ax_city_map, data_key)


def plot_graphs(axis, data_key):
    # plot labels and ticks
    def plot_labels_and_ticks(axis, num_days):
        # Configure major and minor ticks based on the range
        if num_days <= 7:
            # For very short ranges (up to a week), show individual days as major ticks
            axis.xaxis.set_major_locator(mdates.DayLocator())
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            axis.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  # Show every 3rd day as minor tick
            axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
        elif num_days <= 60:
            # For ranges up to about 2 months, show months as major ticks and days as spaced minor ticks
            axis.xaxis.set_major_locator(mdates.MonthLocator())
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            axis.xaxis.set_minor_locator(mdates.DayLocator(interval=5))  # Show every 3rd day as minor tick
            axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
        else:
            # For longer ranges, show months as major ticks without day details
            axis.xaxis.set_major_locator(mdates.MonthLocator())
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            axis.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=1))  # Only the 1st day of each month as minor tick
            axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))

        # Adjust padding for the major tick labels (months)
        axis.tick_params(axis='x', which='major', pad=10)  # Adjust 'pad' to control spacing for major labels

        # Rotate the major tick labels to avoid overlap
        plt.setp(axis.get_xticklabels(), rotation=45, ha="right")
    # END draw_label_and_ticks

    # declare variables
    legend_lines = []
    number_of_days_to_plot = app.get_days_interval_duration()   # add 1 to include last day

    # make day index list
    day_index_list = np.arange(0, number_of_days_to_plot)

    # plot graph for fixed locations
    plot_fixed_locations(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key)

    # plot graph user-selected location
    plot_user_selected_location(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key)

    # plot graph labels and ticks
    plot_labels_and_ticks(axis, number_of_days_to_plot - 1)

    # set graph title, legend, grid and autoscale etc
    axis.set_title(data_key + " verdier")
    axis.legend(legend_lines, [loc.name for loc in all_locations])
    axis.grid(linestyle='dashed')


def plot_app():
    # plot NOX graphs
    plot_graphs(ax_nox, KEY_NOX)

    # plot NOX graphs
    plot_graphs(ax_apd, KEY_APD)

    # plot map (change key to plot APD or NOX)
    plot_city_map(app.map_overlay_key)

    # draw the plot
    plt.draw()

    # show plot
    plt.show()