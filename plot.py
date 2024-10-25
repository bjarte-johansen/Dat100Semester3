import pandas as pd
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.collections as mc
import calendar

# import application specific modules
from defs import *
from data_functions import (extract_data_interval, generate_grid_samples, get_estimated_value_at_point)


# Make markers at fixed and user-selected locations
def plot_location_markers():
    def create_patch_dot(xy: tuple[int, int]):
        return mpatches.Circle(xy, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)

    def create_patch_circle(xy: tuple[int, int], user_color: str):
        circle = mpatches.Circle(xy, UI.marker_size, fill=True, linewidth=UI.marker_stroke_size, color=user_color)
        circle.set_edgecolor(user_color + UI.marker_edge_alpha)
        circle.set_facecolor(user_color + UI.marker_face_alpha)
        return circle

    def add_marker(ax, loc_arg):
        # add marker if there are coordinates
        if loc_arg.coordinates is not None:
            ax.add_patch( create_patch_dot(loc_arg.coordinates) )
            ax.add_patch( create_patch_circle(loc_arg.coordinates, loc_arg.color) )

    # could make/use all_locations but we do it in two steps for clarity
    for loc in fixed_locations:
        add_marker(ax_city_map, loc)

    add_marker(ax_city_map, loc_user)


# Todo: make linspace follow actual days in year
def plot_labels_and_ticks(axis, num_days):
    # generate a list of months between start and end dates (inclusive)
    def get_month_range_names_abbr(start_date:datetime, end_date:datetime):
        months = pd.date_range(start=start_date, end=end_date, freq='MS').strftime("%b").tolist()
        months = [month.capitalize() for month in months]
        return months

    def get_day_range_values(start_date:datetime, end_date:datetime):
        days = pd.date_range(start=start_date, end=end_date, freq='D').strftime("%d").tolist()
        return days

    def get_months_between(start_date, end_date):
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

    def get_days_in_month(year, month):
        return calendar.monthrange(year, month)[1]

    start_month = app.date_range.start_date.month
    days_in_start_month = get_days_in_month(app.get_current_year(), start_month)
    #months_in_interval = get_months_between(app.date_range.start_date, app.date_range.end_date)
    #print("months_interval", months_in_interval)

    use_auto_date_locator = False

    if num_days <= MAX_DAYS_TO_RENDER_WITH_DAYS_TICKS:
        day_range_values = get_day_range_values(app.date_range.start_date, app.date_range.end_date)

        xlabels = list(day_range_values)
        xticks = np.linspace(0, num_days, len(xlabels))

        use_auto_date_locator = True
    else:
        xlabels = get_month_range_names_abbr(app.date_range.start_date, app.date_range.end_date)
        xticks = np.linspace(0, num_days, len(xlabels))

    axis.set_xticks(xticks)
    axis.set_xticklabels(xlabels)

    if use_auto_date_locator:
        axis.xaxis.set_major_locator(mdates.AutoDateLocator())
# END draw_label_and_ticks


# plot data for a location, allowing shadowing parameters
def plot_data(axis, day_index_list_arg, loc, data, data_key):

    # for unknown reason, this stopped working, as it allways claims loc.data_lines[data_key] is
    # not None after a code change. we didnt dvelve into the matter, but this code was much
    # more performant than the allways creating new lines-method. We believe the reason is our
    # changed clearing of axis
    if True:
        if loc.data_lines[data_key] is not None:
            print("rendering to existing data_lines", data_key, loc.data_lines[data_key])
            loc.data_lines[data_key].set_data(day_index_list_arg, data)
            return loc.data_lines[data_key]
        else:
            loc.data_lines[data_key] = axis.plot(day_index_list_arg, data, color = loc.color)[0]
            return loc.data_lines[data_key]

    return axis.plot(day_index_list_arg, data, color = loc.color)[0]


def plot_user_selected_location(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key):
    # extract data, plot and draw horisontal average line for user-selected location
    if loc_user.coordinates is not None:
        # allocate data_view
        loc_user.data_view[data_key] = np.empty(number_of_days_to_plot, dtype=int)

        # iterate over days
        for i in range(0, number_of_days_to_plot):
            # take measurement value
            for loc in fixed_locations:
                loc.measurement_value = loc.data_view[data_key][i]

            # compute estimated value at point
            loc_user.data_view[data_key][i] = get_estimated_value_at_point(fixed_locations, loc_user.coordinates)

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

# ----- grid sampling functions -----

def invalidate_grid_samples():
    get_grid_samples.invalidate = True

def get_grid_samples():
    # force re-calculation of grid samples due to bug
    # Todo: remove this when bug is fixed
    get_grid_samples.invalidated = True

    if not hasattr(get_grid_samples, "invalidated"):
        get_grid_samples.invalidated = True

    if get_grid_samples.invalidated:
        get_grid_samples.result = generate_grid_samples(
            app.map_dimensions,
            app.grid_resolutions,
            fixed_locations,
            )
        get_grid_samples.invalidated = False

    return get_grid_samples.result

#
def plot_contour_lines(axis, data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_fold_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = get_grid_samples()

    #x = np.linspace(0, app.map_dimensions[0], app.grid_resolutions[0])
    #y = np.linspace(0, app.map_dimensions[1], app.grid_resolutions[1])
    #X, Y = np.meshgrid(x, y)

    # Optionally smooth the data using a Gaussian filter
    #Z_smooth = moving_average(result, kernel_size=3)

    # Now overlay the contour plot (assuming 'result' is your 2D array for contour)
    #contour = axCityMap.contourf(result, levels=10, cmap='terrain', extent=[0, 2000, 0, 1500], alpha=0.3)
    contour = axis.contour(result, levels=10, cmap='terrain', extent=[0, 2000, 0, 1500])

    #contour = axCityMap.contour(X, Y, Z_smooth, levels=20, cmap='terrain', extent=[0, 2000, 0, 1500])

    # Add the colorbar linked to the contour plot
    #plt.colorbar(contour, ax=axCityMap, label='Elevation')
# END show_contour_lines


def plot_heightmap_boxed(axis, data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_fold_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = get_grid_samples()

    # calculate box width and height
    box_width = app.map_dimensions[0] // app.grid_resolutions[0]
    box_height = app.map_dimensions[1] // app.grid_resolutions[1]

    # define a custom colormap from green to red
    cmap = LinearSegmentedColormap.from_list("GreenRed", ["green", "red"])

    # normalize the value to fit the colormap range
    result_min = result.min()
    result_max = result.max()
    result_range = result_max - result_min

    # storage for rectangles
    #rectangles = np.empty(app.grid_resolutions[1] * app.grid_resolutions[0], dtype=Rectangle)
    rectangles = []

    # iterate over virtual boxes
    for i in range(app.grid_resolutions[1]):
        for j in range(app.grid_resolutions[0]):
            # Get the corner values of the current box
            box_corners = [
                result[i, j],
                result[i, min(j + 1, app.grid_resolutions[1])],
                result[i, 0 if j - 1 < 0 else j - 1],
                result[i, min(j + 1, app.grid_resolutions[1])]
            ]

            # Get the max or min of the corner values (choose either min or max)
            box_value = np.mean(box_corners)  # Change to min(box_corners) if needed

            # normalize the value to fit the colormap range
            norm_value = (box_value - result_min) / result_range

            # Get the color from the colormap
            color = cmap(norm_value)
            if norm_value < MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED:
                continue

            # get color
            color = cmap(norm_value)

            # Create a rectangle for the box
            rect = Rectangle((j * box_height - 1, i * box_width - 1), box_height - 1, box_width - 1, color=color, alpha=0.3)

            # Add the rectangle to the plot
            # axis.add_patch(rect)
            #rectangles[i * (int(app.grid_resolutions[0])) + j] = rect
            rectangles.append(rect)

    collection = mc.PatchCollection(rectangles, match_original=True)
    axis.add_collection(collection)

def plot_map(data_key):
    # clear axis
    ax_city_map.cla()

    # plot map of city
    ax_city_map.set_title("Kart Bergen")
    ax_city_map.axis('off')
    ax_city_map.imshow(city_map_image, extent=[0, 2000, 1500, 0])

    # fix the axis limits to avoid auto-scaling
    ax_city_map.set_xlim(0, app.map_dimensions[0])  # Example limits, adjust as needed
    ax_city_map.set_ylim(app.map_dimensions[1], 0)

    # equal scaling on both axes
    ax_city_map.set_aspect('equal', 'box')

    # plot map markers for locations and user-selected point
    plot_location_markers()

    # rendering methods that require grid samples
    if app.plot_countour_lines or app.plot_heightmap_boxed:
        invalidate_grid_samples()

        if app.plot_countour_lines:
            # plot map contour lines
            plot_contour_lines(ax_city_map, data_key)

        if app.plot_heightmap_boxed:
            # plot heightmap boxed
            plot_heightmap_boxed(ax_city_map, data_key)


def plot_graphs(axis, data_key):
    # clear axis
    # axis.cla()

    # declare variables
    legend_lines = []
    number_of_days_to_plot = app.get_days_interval_duration()   # add 1 to include last day

    # arange is end-exclusive but we allready adding 1
    day_index_list = np.arange(0, number_of_days_to_plot)

    #print(number_of_days_to_plot, len(day_index_list), app.date_range.start_date, app.date_range.end_date)

    # plot graph for fixed locations
    plot_fixed_locations(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key)

    # plot graph user-selected location
    plot_user_selected_location(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key)

    # plot graph labels and ticks
    plot_labels_and_ticks(axis, number_of_days_to_plot - 1)

    # set graph title, legend, grid and autoscale etc
    axis.set_title(data_key + " verdier")
    axis.legend(legend_lines, [loc.name for loc in fixed_locations] + [loc_user.name])
    axis.grid(linestyle='dashed')

    #axis.relim()
    #axis.autoscale_view()


def plot_app():
    # plot NOX graphs
    plot_graphs(ax_nox, KEY_NOX)

    # plot NOX graphs
    plot_graphs(ax_apd, KEY_APD)

    # plot map (change key to plot APD or NOX)
    plot_map(app.map_overlay_key)

    # draw the plot
    plt.draw()