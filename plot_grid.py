from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.collections as mc


# import application specific modules
from defs import *
from locations import *

# contour plot
def plot_grid_contour_lines(axis, data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_fold_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = generate_grid_samples(app.map_dimension, app.grid_resolution, fixed_locations, app.get_estimated_value_at_point_func)

    # Now overlay the contour plot (assuming 'result' is your 2D array for contour)
    #contour = axis.contourf(result, levels=10, cmap='terrain', extent=[0, 2000, 0, 1500], alpha=0.3)
    contour = axis.contour(result, levels=10, cmap='terrain', extent=[0, 2000, 0, 1500])

    #contour = axCityMap.contour(X, Y, Z_smooth, levels=20, cmap='terrain', extent=[0, 2000, 0, 1500])

    # Add the colorbar linked to the contour plot
    #plt.colorbar(contour, ax=axis, label='Verdio')
# END show_contour_lines


def plot_grid_heatmap(axis, data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_fold_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = generate_grid_samples(app.map_dimension, app.grid_resolution, fixed_locations,
                                   app.get_estimated_value_at_point_func)

    # show as heatmap
    axis.imshow(result, cmap='Reds', interpolation='nearest', aspect='auto', extent=[0, 2000, 1500, 0], alpha=0.3)

    # fix the axis limits to avoid auto-scaling
    ax_city_map.set_xlim(0, app.map_dimension[0])  # Example limits, adjust as needed
    ax_city_map.set_ylim(app.map_dimension[1], 0)

    # equal scaling on both axes
    ax_city_map.set_aspect('equal', 'box')


# heightmap boxed, that is, a low-res heightmap
def plot_grid_threshold_heatmap(axis, data_key):
    # update locations measurement_value
    for loc in fixed_locations:
        loc.measurement_value = app.data_fold_func(loc.data_view[data_key])

    # generate grid samples for contour plot
    result = generate_grid_samples(app.map_dimension, app.grid_resolution, fixed_locations,
                                   app.get_estimated_value_at_point_func)

    # calculate box width and height
    box_width = app.map_dimension[0] // app.grid_resolution[0]
    box_height = app.map_dimension[1] // app.grid_resolution[1]

    # define a custom colormap from green to red
    cmap = LinearSegmentedColormap.from_list("GreenRed", ["green", "red"])

    # normalize the value to fit the colormap range
    result_min = result.min()
    result_max = result.max()
    result_range_multiplier = 1 / (result_max - result_min + 1e-06)

    # storage for rectangles
    rectangles = np.empty(app.grid_resolution[1] * app.grid_resolution[0], dtype=Rectangle)
    rectangles_length = 0

    # iterate over virtual boxes
    for i in range(0, app.grid_resolution[1]):
        for j in range(0, app.grid_resolution[0]):
            # Get the corner values of the current box
            box_corners = [
                result[i, j],
                result[i, min(j + 1, app.grid_resolution[1])],
                result[i, 0 if j - 1 < 0 else j - 1],
                result[i, min(j + 1, app.grid_resolution[1])]
            ]

            # Get the max or min of the corner values (choose either min or max)
            box_value = np.mean(box_corners)  # Change to min(box_corners) if needed

            # normalize the value to fit the colormap range
            norm_value = (box_value - result_min) * result_range_multiplier

            # Skip if the value is below a certain threshold
            if norm_value < MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED:
                continue

            # Get the color from the colormap
            color = cmap(norm_value)

            # Create a rectangle for the box, append to our list
            rect = Rectangle((j * box_height - 1, i * box_width - 1), box_height - 1, box_width - 1, color=color, alpha=0.3)

            # add to rectangles
            rectangles[rectangles_length] = rect
            rectangles_length += 1

    collection = mc.PatchCollection(rectangles[:rectangles_length], match_original=True)
    axis.add_collection(collection)