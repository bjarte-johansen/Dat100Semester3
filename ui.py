import defs
import matplotlib
import matplotlib.widgets
import matplotlib.pyplot as plt

from defs import axInputPane
from plot import *

# ---------- Declare text helpers ----------------

class UIHelper:
	def __init__(self):
		self.text_input_list = []
		self.text_input_map = {}
		self.radio_buttons = []

uihelper = UIHelper()


# ---------- Radio input input handling ----------

def set_data_processing_func_from_str(str_func):
	# update processing func
	app.set_data_processing_func(str_func)

	# plot graph
	plot_app()

def set_render_option_from_str(input_str):
	# update render option
	app.plot_countour_lines = False
	app.plot_heightmap_boxed = False

	option = string_to_render_option_map.get(input_str, None)
	if option is not None:
		if hasattr(app, option):
			setattr(app, option, True)

	# plot graph
	plot_app()

def set_days_interval_from_str(str_period):
	# update date range
	tmp = string_to_date_interval_map[str_period]
	app.set_date_range(tmp['start_date'], tmp['end_date'])

	# reset user-selected point
	loc_user.coordinates = None

	uihelper.text_input_map['text_input_start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
	uihelper.text_input_map['text_input_end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))

	# plot graph
	plot_app()

# ---------- Radio button groups ----------

# we have hardcoded values because we dont consider this to be very important
# in the case of radiobuttons

def create_radio_button_panel(ax, list_options, on_clicked):
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
	radio_button.on_clicked(on_clicked)
	return radio_button
# END create_radio_button_panel

def create_radio_button_panel_for_interval(cb):
	ax = plt.axes([0.4, 0.35, 0.1, 0.17], facecolor=UI.RadioGroup.bg_color)  # Second radio button group
	radio_button = create_radio_button_panel(ax, list(string_to_date_interval_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_processing_func(cb):
	ax = plt.axes([0.4, 0.175, 0.1, 0.15], facecolor=UI.RadioGroup.bg_color)  # First radio button group
	radio_button = create_radio_button_panel(ax, list(string_to_data_process_func_map.keys()), cb)
	return radio_button

def create_radio_button_panel_for_render_options(cb):
	ax = plt.axes([0.4, 0.05, 0.1, 0.10], facecolor=UI.RadioGroup.bg_color)  # Second radio button group
	radio_button = create_radio_button_panel(ax, list(string_to_render_option_map.keys()), cb)
	return radio_button




# ---------- Date input text handling ----------

def validate_date_input(date_str):
	try:
		datetime.strptime(date_str, '%Y-%m-%d')
		return True
	except ValueError:
		return False

def create_date_text_inputs(ax):
	# returns the bounding box of a text object in data coordinates
	def get_bounding_box(text_obj):
		renderer = fig.canvas.get_renderer()
		bbox = text_obj.get_window_extent(renderer=renderer)  # Get in display (pixel) coordinates
		bbox_data = bbox.transformed(ax.transData.inverted())  # Convert to data coordinates
		return bbox_data

	# Display initial text
	text_input_list = [
		ax.text(0.0125, 0.85, "", horizontalalignment='left', verticalalignment='center', fontsize=12),
		ax.text(0.0125, 0.85 - AUI.Axis.InputPane.height * 1, "", horizontalalignment='left', verticalalignment='center', fontsize=12)
		]

	text_input_map = {
		'start_date': text_input_list[0],
		'end_date': text_input_list[1],
	}
	text_input_map['start_date'].custom_title = 'Dato start: '
	text_input_map['end_date'].custom_title = 'Dato slutt: '

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

	def update_date_range(start, end):
		app.set_date_range(start, end)

		plot_app()

	def on_submit(input_index, text):
		new_date = datetime.strptime(text, '%Y-%m-%d')

		if input_index == 0:
			update_date_range(new_date, app.date_range.end_date)
		elif input_index == 1:
			update_date_range(app.date_range.start_date, new_date)

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

	return text_input_list, text_input_map

def init_gui():
	uihelper.text_input_list, uihelper.text_input_map = create_date_text_inputs(axInputPane)

	uihelper.radio_buttons = [
		create_radio_button_panel_for_processing_func(set_data_processing_func_from_str),
		create_radio_button_panel_for_interval(set_days_interval_from_str),
		create_radio_button_panel_for_render_options(set_render_option_from_str)
	]