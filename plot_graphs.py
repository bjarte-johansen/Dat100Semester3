import pandas as pd
import matplotlib.dates as mdates

# import application specific modules
from plot_grid import *


# plot data for a location, allowing shadowing parameters
def plot_data(axis, loc, data_key):
	date_range = pd.date_range(start=app.date_range.start_date, end=app.date_range.end_date)

	if loc.data_lines[data_key] is not None:
		# used for debugging
		# print("reused datalines")

		loc.data_lines[data_key].set_data(date_range, loc.data_view[data_key])
		return loc.data_lines[data_key]
	else:
		loc.data_lines[data_key] = axis.plot(date_range, loc.data_view[data_key], color=loc.color)[0]
		return loc.data_lines[data_key]
# END plot_data


# plot location graph
def plot_location_graph(axis, loc, build_data_view_fn, legend_lines, number_of_days_to_plot, data_key):
	if loc is None or loc.coordinates is None:
		return

	# build data-view via callback
	build_data_view_fn(loc, data_key, number_of_days_to_plot)

	# plot data for fixed locations, add to legend
	plot_obj = plot_data(axis, loc, data_key)
	legend_lines.append( plot_obj )

	# draw horisontal average line
	axis.axhline(np.mean(loc.data_view[data_key]), color=loc.color, linestyle='--', linewidth=1)
# END plot_location_graph


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


# data view builder for variable location
def build_variable_location_data_view(loc, data_key, number_of_days_to_plot):
	loc.data_view[data_key] = np.empty(number_of_days_to_plot, dtype=int)
	for i in range(0, number_of_days_to_plot):
		# store measurement value
		for other_loc in fixed_locations:
			other_loc.measurement_value = other_loc.data_view[data_key][i]

		# compute estimated value at point
		loc_user.data_view[data_key][i] = app.get_estimated_value_at_point_func(fixed_locations, loc_user.coordinates)
# END build_variable_location_data_view


# data view builder for fixed location
def build_fixed_location_data_view(loc, data_key, number_of_days_to_plot):
	loc.data_view[data_key] = extract_data_interval(loc.historical_data[data_key], app.days_interval[0], app.days_interval[0] + number_of_days_to_plot)
# END build_fixed_location_data_view


def plot_graphs(axis, data_key):
	# declare variables
	legend_lines = []
	number_of_days_to_plot = app.get_days_interval_duration()   # add 1 to include last day

	# plot graph for all locations
	for loc in all_locations:
		if loc.type == 'fixed':
			# use builder for fixed location
			plot_location_graph(axis, loc, build_fixed_location_data_view, legend_lines, number_of_days_to_plot, data_key)
		elif loc.type == 'variable':
			# use builder for variable location
			plot_location_graph(axis, loc, build_variable_location_data_view, legend_lines, number_of_days_to_plot, data_key)

	# plot graph labels and ticks
	plot_labels_and_ticks(axis, number_of_days_to_plot - 1)

	# set graph title, legend, grid and autoscale etc
	axis.set_title(data_key + " verdier")

	# set legend
	legend_titles = [loc.name for loc in all_locations]
	axis.legend(legend_lines, legend_titles)

	axis.grid(linestyle='dashed')
# END plot_graphs