import pandas as pd
import matplotlib.patches as mpatches
from dateutil.relativedelta import relativedelta

# import application specific modules
from defs import *
from data_functions import (extract_data_interval, generate_grid_samples, get_estimated_value_at_point)


# Make markers at fixed and user-selected locations
def draw_circles_stations():
    def create_patch_circle_dot(xy: tuple[int, int]):
        return mpatches.Circle(xy, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)

    def create_patch_circle(xy: tuple[int, int], user_color: str):
        circle = mpatches.Circle(xy, UI.marker_size, fill=True, linewidth=UI.marker_stroke_size, color=user_color)
        circle.set_edgecolor(user_color + UI.marker_edge_alpha)
        circle.set_facecolor(user_color + UI.marker_face_alpha)
        return circle

    def add_marker(ax, loc_arg):
        # add marker if there are coordinates
        if loc_arg.coordinates is not None:
            ax.add_patch( create_patch_circle_dot(loc_arg.coordinates) )
            ax.add_patch( create_patch_circle(loc_arg.coordinates, loc_arg.color) )

    for loc in fixed_locations:
        add_marker(axCityMap, loc)

    add_marker(axCityMap, loc_user)



# Todo: make linspace follow actual days in year
def plot_labels_and_ticks(axis, num_days):
    # generate a list of months between start and end dates (inclusive)
    def get_month_range_names_abbr(start_date:datetime, end_date:datetime):
        months = pd.date_range(start=start_date, end=end_date, freq='MS').strftime("%b").tolist()
        months = [month.capitalize() for month in months]
        return months

    # add extra month to include month data last untill
    #xlabels = get_month_range_names_abbr(app.date_range.start_date, app.date_range.end_date + relativedelta(months=1))
    xlabels = get_month_range_names_abbr(app.date_range.start_date, app.date_range.end_date)
    xticks = np.linspace(0, num_days, len(xlabels))

    axis.set_xticks(xticks)
    axis.set_xticklabels(xlabels)
# END draw_label_and_ticks


# plot data for a location, allowing shadowing parameters
def plot_data(axis, day_index_list_arg, loc_arg, data):
    return axis.plot(day_index_list_arg, data, color = loc_arg.color)[0]


def plot_user_selected_location(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key):
    # extract data, plot and draw horisontal average line for user-selected location
    if loc_user.coordinates is not None:
        # calc data-points for each day
        loc_user.data_view[data_key] = np.empty(number_of_days_to_plot, dtype=int)
        for i in range(0, number_of_days_to_plot):
            # take measurement value
            for loc in fixed_locations:
                loc.measurement_value = loc.data_view[data_key][i]

            # compute estimated value at point
            loc_user.data_view[data_key][i] = get_estimated_value_at_point(fixed_locations, loc_user.coordinates)

        # set/update user-point NOX values
        legend_lines.append( plot_data(axis, day_index_list, loc_user, loc_user.data_view[data_key]) )

        # draw horisontal average line
        axis.axhline(np.mean(loc_user.data_view[data_key]), color=UI.Colors.user, linestyle='--', linewidth=1)
# END plot_user_selected_location


def plot_fixed_locations(axis, legend_lines, number_of_days_to_plot, day_index_list, data_key):
    # extract data, plot and draw horisontal average line for fixed locations
    for loc in fixed_locations:
        # extract into data-view
        loc.data_view[data_key] = extract_data_interval(loc.historical_data[data_key], app.days_interval[0], app.days_interval[0] + number_of_days_to_plot)

        # plot data for fixed locations, add to legend
        legend_lines.append( plot_data(axis, day_index_list, loc, loc.data_view[data_key]) )

        # draw horisontal average line
        axis.axhline(np.mean(loc.data_view[data_key]), color=loc.color, linestyle='--', linewidth=1)
# END plot_fixed_locations


def plot_contour_lines(data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_processing_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = generate_grid_samples(
        app.map_dimensions,
        app.grid_resolutions,
        fixed_locations,
        )

    #x = np.linspace(0, app.map_dimensions[0], app.grid_resolutions[0])
    #y = np.linspace(0, app.map_dimensions[1], app.grid_resolutions[1])
    #X, Y = np.meshgrid(x, y)

    # Optionally smooth the data using a Gaussian filter
    #Z_smooth = moving_average(result, kernel_size=3)

    # Now overlay the contour plot (assuming 'result' is your 2D array for contour)
    #contour = axCityMap.contourf(result, levels=20, cmap='terrain', extent=[0, 2000, 0, 1500], alpha=0.3)
    contour = axCityMap.contour(result, levels=20, cmap='terrain', extent=[0, 2000, 0, 1500])

    #contour = axCityMap.contour(X, Y, Z_smooth, levels=20, cmap='terrain', extent=[0, 2000, 0, 1500])

    # Add the colorbar linked to the contour plot
    #plt.colorbar(contour, ax=axCityMap, label='Elevation')
# END show_contour_lines

def plot_map(data_key):
    # clear axis
    axCityMap.cla()

    # plot map of city
    axCityMap.set_title("Kart Bergen")
    axCityMap.axis('off')
    axCityMap.imshow(city_map_image, extent=[0, 2000, 1500, 0])

    # Fix the axis limits to avoid auto-scaling
    axCityMap.set_xlim(0, app.map_dimensions[0])  # Example limits, adjust as needed
    axCityMap.set_ylim(app.map_dimensions[1], 0)

    # Equal scaling on both axes
    axCityMap.set_aspect('equal', 'box')

    # plot map markers for locations and user-selected point
    draw_circles_stations()

    # plot map contour lines
    plot_contour_lines(data_key)
pass

def plot_graphs(axis, data_key):
    # clear axis
    axis.cla()

    # declare variables
    legend_lines = []
    number_of_days_to_plot = app.get_days_interval_duration()   # add 1 to include last day

    # arange is end-exclusive but we allready adding 1
    day_index_list = np.arange(0, number_of_days_to_plot)

    print(number_of_days_to_plot, len(day_index_list), app.date_range.start_date, app.date_range.end_date)

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