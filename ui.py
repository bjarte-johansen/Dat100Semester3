import defs
import matplotlib
import matplotlib.widgets
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons

from defs import ax_input_pane, fig, app
#from plot import *

from utils import EmptyClass, hide_axis_graphics
from constants import *
from data_functions import get_estimated_value_at_point


# ---------- configure UI colors/fonts ----------

class UI:
	marker_size:int = 60					# size of "disc" around marker
	marker_stroke_size:int = 3			  	# width of stroke around marker
	marker_face_alpha = "77"				# hex, alphavalue of "disc" around marker
	marker_edge_alpha = "AA"				# hex, alphavalue of "disc" around marker
	marker_dot_radius:int = 4			   	# radius of "dot" in marker
	marker_dot_color = "#000000"			# color of "dot" in marker
	contour_levels = 5					 	# number of contour levels

	class RadioGroup:
		bg_color = '#FFFFFFCC'			  	# background color of radio button group

	class Colors:
		kronstad:str = "#c02f1e"			# color of kronstad
		nordnes:str = "#1A6390"			 	# color of nordnes
		bryggen: str = "#6a994e"			# color of bryggen
		user:str = "#C453FF"				# color of user-selected point



# ---------- Declare text helpers ----------------

class UIHelper:
	def __init__(self):
		self.text_input_list = []
		self.text_input_map = {}
		self.radio_buttons = []

uihelper = UIHelper()


# ---------- input event handlers ----------

def set_value_estimation_func_from_str(str_id):
	# update processing func
	fn = string_to_estimate_func_map.get(str_id, get_estimated_value_at_point)
	app.get_estimated_value_at_point_func = fn

	print(app.get_estimated_value_at_point_func)

	# invalidate graph axis
	app.invalidate_graph_axis()

	# render
	app.render()

def set_data_fold_func_from_str(str_id):
	# update processing func
	app.set_data_fold_callback(str_id)

	# invalidate graph axis
	app.invalidate_graph_axis()

	# render
	app.render()


def set_render_option_from_str(str_id):
	# clear plot options
	app.plot_grid_countour_lines = False
	app.plot_grid_threshold_heatmap = False
	app.plot_grid_heatmap = False

	# update render option
	option = string_to_render_option_map.get(str_id, None)
	if option is not None:
		if hasattr(app, option):
			prev = getattr(app, option)
			setattr(app, option, not prev)

	# invalidate graph axis
	app.invalidate_graph_axis()

	# render
	app.render()


def set_date_range_from_interval_from_key_str(str_id):
	app.begin_update()

	# invalidate graph axis
	app.invalidate_graph_axis()

	# update app date range
	tmp = string_to_date_interval_map[str_id]
	app.set_date_range(tmp['start_date'], tmp['end_date'])

	# update text inputs
	uihelper.text_input_map['start_date'].set_text(uihelper.text_input_map['start_date'].custom_title + app.date_range.start_date.strftime('%Y-%m-%d'))
	uihelper.text_input_map['end_date'].set_text(uihelper.text_input_map['end_date'].custom_title + app.date_range.end_date.strftime('%Y-%m-%d'))

	app.end_update()


def set_map_overlay_key_from_str(str_id):
	# update key for map overlay
	app.map_overlay_key = string_to_map_overlay_map.get(str_id, 'NOX')

	# invalidate graph axis
	app.invalidate_graph_axis()

	# plot graph
	app.render()



# ---------- Radio button groups ----------

# we have hardcoded values because we dont consider this to be very important
# in the case of radiobuttons

def create_radio_button_panel(ax, title, list_options, on_clicked):
	num_options = len(list_options)
	list_fonts = [10] * num_options
	list_colors = ['#333333'] * num_options
	button_face_colors = ['#000000'] * num_options  # White face color for the radio buttons
	button_edge_colors = ['#000000'] * num_options  # Black edge color for better visibility
	radio_button = RadioButtons(
		ax,
		list_options,
		label_props = {'color': list_colors, 'fontsize' : list_fonts},
		radio_props={'facecolor': button_face_colors, 'edgecolor': button_edge_colors}
		)
	ax.text(0.1, 0.95, title, ha='left', va='top', transform=ax.transAxes, fontweight="bold")

	label_bottom = 0.075
	label_height = 0.125

	# Adjust the position of the radio buttons slightly lower
	for i, (circle, label) in enumerate(zip(radio_button.circles, radio_button.labels)):
		y = 0.85 - (label_bottom + i * label_height)

		# Adjust the position of the radio button circle
		circle.center = (circle.center[0], y)
		circle.set_radius(0.025)

		# Adjust the position of the label
		label.set_position((label.get_position()[0], y))

	radio_button.on_clicked(on_clicked)
	return radio_button
# END create_radio_button_panel



def create_radio_button_panel_for_interval(cb):
	ax = plt.axes([0.3, 0.715, 0.1, 0.26], facecolor=UI.RadioGroup.bg_color)
	radio_button = create_radio_button_panel(ax, "Intervall", list(string_to_date_interval_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_processing_func(cb):
	ax = plt.axes([0.425, 0.715, 0.1, 0.26], facecolor=UI.RadioGroup.bg_color)
	radio_button = create_radio_button_panel(ax, "Reduksjon", list(string_to_data_fold_func_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_render_options(cb):
	ax = plt.axes([0.55, 0.715, 0.1, 0.26], facecolor=UI.RadioGroup.bg_color)
	radio_button = create_radio_button_panel(ax, "Plot", list(string_to_render_option_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_map_overlay_options(cb):
	ax = plt.axes([0.675, 0.715, 0.1, 0.26], facecolor=UI.RadioGroup.bg_color)
	radio_button = create_radio_button_panel(ax, "Kartfunksjon", list(string_to_map_overlay_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_value_estimation_func(cb):
	ax = plt.axes([0.8, 0.715, 0.1, 0.26], facecolor=UI.RadioGroup.bg_color)
	radio_button = create_radio_button_panel(ax, "Estimering", list(string_to_estimate_func_map.keys()), cb)
	return radio_button



# ---------- Date input text handling ----------

def str_to_datetime(date_str):
	try:
		return datetime.strptime(date_str, '%Y-%m-%d')
	except ValueError:
		return None

def create_date_text_inputs(ax):
	# returns the bounding box of a text object in data coordinates
	def get_bounding_box(text_obj):
		renderer = fig.canvas.get_renderer()
		bbox = text_obj.get_window_extent(renderer=renderer)  # Get in display (pixel) coordinates
		bbox_data = bbox.transformed(ax.transData.inverted())  # Convert to data coordinates
		return bbox_data

	ax.text(0.0125, 0.8, "Brukervalgt data intervall", horizontalalignment='left', verticalalignment='center', fontsize=10,fontweight="bold"),

	# create text fields (serves as input with custom key press code
	text_input_list = [
		ax.text(0.0125, 0.89 - 0.28, "", horizontalalignment='left', verticalalignment='center', fontsize=10),
		ax.text(0.0125, 0.89 - 0.28 - 0.17, "", horizontalalignment='left', verticalalignment='center', fontsize=10)
		]

	text_input_map = {
		'start_date': text_input_list[0],
		'end_date': text_input_list[1],
	}
	text_input_map['start_date'].custom_title = 'Dato start: '
	text_input_map['end_date'].custom_title = 'Dato slutt: '

	# use class for index so we can have it carried into local functions
	# since we cannot use global keyword, dont spam global space
	active_text_input = EmptyClass()
	active_text_input.index = -1

	def on_click(event):
		if event.xdata is None or event.ydata is None:
			return

		active_text_input.index = -1

		for i,text_input in enumerate(text_input_list):
			# get bounds and do hit-test
			bounds = get_bounding_box(text_input)
			if bounds.contains(event.xdata, event.ydata):
				active_text_input.index = i
				print("log: clicked on text input ", active_text_input.index)

	def on_submit(input_index, text):
		# convert text to date
		new_date = str_to_datetime(datetime.strptime(text, '%Y-%m-%d'))

		if new_date is None:
			print("Ugyldig dato")
			return

		# update application date range
		if input_index == 0:
			app.set_date_range(new_date, app.date_range.end_date)
		elif input_index == 1:
			app.set_date_range(app.date_range.start_date, new_date)

	def on_key(event):
		# check for valid text input
		if active_text_input.index == -1:
			print("no text input selected")
			return

		# get reference to text object
		o = text_input_list[active_text_input.index]

		# get old text by removing custom title
		text = o.get_text().replace(o.custom_title, '')

		if event.key == 'backspace':
			text = text[:-1]
			o.set_text(o.custom_title + text)
		elif event.key == 'enter':
			on_submit(active_text_input.index, text)
			return
		else:
			text = text + event.key
			o.set_text(o.custom_title + text)

		plt.draw()

	# Connect the keyboard event to handle input
	fig.canvas.mpl_connect('button_press_event', on_click)
	fig.canvas.mpl_connect('key_press_event', on_key)

	return text_input_map


# ---------- UI initialization ----------

def init_gui():
	# create text input panel
	text_input_panel = plt.axes([0.05, 0.715, 0.225, 0.26], facecolor=UI.RadioGroup.bg_color)
	hide_axis_graphics(text_input_panel, hide_ticks=True, hide_spines=False)
	text_input_panel.set_zorder(-1)

	# create text inputs
	uihelper.text_input_map = create_date_text_inputs(ax_input_pane)

	# update date range for text inputs from app
	uihelper.text_input_map['start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
	uihelper.text_input_map['end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))


	# create radio buttons / checkboxes
	uihelper.radio_buttons = [
		create_radio_button_panel_for_processing_func(set_data_fold_func_from_str),
		create_radio_button_panel_for_interval(set_date_range_from_interval_from_key_str),
		create_radio_button_panel_for_render_options(set_render_option_from_str),
		create_radio_button_panel_for_map_overlay_options(set_map_overlay_key_from_str),
		create_radio_button_panel_for_value_estimation_func(set_value_estimation_func_from_str)
	]