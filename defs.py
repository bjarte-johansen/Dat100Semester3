import locale

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import RadioButtons

from types import SimpleNamespace

# import application specific modules
from DateRange import *
from data_functions import *



# ---------- configure UI settings ----------

class UI:
    marker_size:int = 60                    # size of "disc" around marker
    marker_stroke_size:int = 3              # width of stroke around marker
    marker_face_alpha = "77"                # hex, alphavalue of "disc" around marker
    marker_edge_alpha = "AA"                # hex, alphavalue of "disc" around marker
    marker_dot_radius:int = 4               # radius of "dot" in marker
    marker_dot_color = "#000000"            # color of "dot" in marker
    contour_levels = 5                     	# number of contour levels

    class RadioGroup:
        bg_color = '#FFFFFFCC'              # background color of radio button group

    class Colors:
        kronstad:str = "#c02f1e"            # color of kronstad
        nordnes:str = "#1A6390"             # color of nordnes
        bryggen: str = "#6a994e"            # color of bryggen
        user:str = "#C453FF"                # color of user-selected point



# ---------- utility functions ----------

class EmptyClass:
    pass



"""
def map_to_range(value, min_in, max_in, min_out, max_out):
    if max_in == min_in:
        raise ValueError("min_in and max_in cannot be the same value")

    return min_out + (value - min_in) * (max_out - min_out) / (max_in - min_in)
"""

# function to hide axis graphics
def hide_axis_graphics(ax, hide_ticks=True, hide_spines=True):
    if hide_ticks:
        ax.set_xticks([])
        ax.set_yticks([])

    if hide_spines:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)



# ---------- setup environment ----------

# define keys for data
KEY_NOX = 'NOX'
KEY_APD = 'APD'

# setup norwegian locale
locale.setlocale(locale.LC_ALL, 'nb_NO.UTF-8')

#create figure and 3 axis

# Create a figure and multiple subplots (2 rows, 2 columns)
#fig, axs = plt.subplots(1, 3, figsize=(10, 8))  # 2x2 grid of subplots

class AUI:
    class Axis:
        class InputPane:
            height = 0.175

# ---------- setup environment ----------


fig = plt.figure(figsize=(18, 7))

# set window size
def set_window_size(new_x:int, new_y:int, width:int, height:int):
    fig.canvas.manager.window.wm_geometry(f"{width}x{height}+{new_x}+{new_y}")

set_window_size(1950, 50, 1600, 700)

# create axis for input pane
ax_input_pane = fig.add_axes((0.05, 0.8125, 0.9, AUI.Axis.InputPane.height))
ax_input_pane.set_facecolor('#00000000')
hide_axis_graphics(ax_input_pane)


# create 3 axis for graphs + map
ax_nox = fig.add_axes((0.05, 0.05, 0.25, 0.5957))
ax_nox.set_facecolor('#FFFFFF77')

ax_apd = fig.add_axes((0.35, 0.05, 0.25, 0.5957))
ax_apd.set_facecolor('#FFFFFF77')

ax_city_map = fig.add_axes((0.65, 0.05, 0.30, 0.65))



# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')



# ---------- define constants ----------

MAX_DAYS_TO_RENDER_WITH_DAYS_TICKS = 65         # maximum number of days to render with days ticks
MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED = 0.5         # threshold for heightmap boxed rendering



# ---------- define maps, used by radio button / checkbox groups ----------

# define string -> date range
string_to_date_interval_map = {
    'År':           {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2025, 1, 1)},
    '1. Kvartal':   {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2024, 4, 1)},
    '2. Kvartal':   {'start_date': datetime(2024, 4, 1), 'end_date': datetime(2024, 7, 1)},
    '3. Kvartal':   {'start_date': datetime(2024, 7, 1), 'end_date': datetime(2024, 10, 1)},
    '4. Kvartal':   {'start_date': datetime(2024, 10, 1), 'end_date': datetime(2025, 1, 1)},
    'En måned':   {'start_date': datetime(2024, 10, 10), 'end_date': datetime(2024, 11, 10)},

}

# define string -> data fold func
string_to_data_fold_func_map = {
    'min': np.min,
    'max': np.max,
    'mean': np.mean,
    'median': np.median,
    'default': np.mean,
}

#define string -> render option
string_to_render_option_map = {
    'Ingen': 'none',
    'Kontur': 'plot_countour_lines',
    'Verdibokser': 'plot_heightmap_boxed',
}

# define string -> map overlay
string_to_map_overlay_map = {
    'NOX': KEY_NOX,
    'APD': KEY_APD,
}



# ---------- Application class ----------

class Application:
    def __init__(self):
        #self.current_year = datetime.now().year         # year
        self.data_fold_func = np.mean             # reduce array -> value (for get_estimated_value_at_point)
        self.grid_resolutions = (20 * 2, 15 * 2)        # resolution of grid for contour/heightmap etc
        self.map_dimensions = (2000, 1500)              # dimensions of map
        self.date_range = DateRange(None, None)         # date range
        self.days_interval = (0, 0)
        self.on_date_range_change = None                # callback for date range change

        self.plot_countour_lines = False                # plot contour lines
        self.plot_heightmap_boxed = False               # plot heightmap as boxed

        self.plot_gui_callback = None                   # callback to plot gui

        self.map_overlay_key = KEY_NOX                  # data_key to display contour / heightmap etc

        tmp = string_to_date_interval_map['År']
        self.set_date_range(tmp['start_date'], tmp['end_date'])

    def invalidate_graph_axis(self, render:bool=False):
        ax_nox.clear()
        ax_apd.clear()

        if self.on_date_range_change:
            self.on_date_range_change()

        """
        for loc in all_locations:
            for data_key in loc.data_lines:
                loc.data_lines[data_key] = None
        """

        if render:
            print("attempt to call render via ", __name__)
            self.render()

    def get_current_year(self):
        # not static global method for logical grouping of code
        return datetime.now().year

    # self-explanatory
    def get_days_interval_duration(self):
        return self.days_interval[1] - self.days_interval[0] + 1

    # self-explanatory
    def set_date_range(self, start_date:datetime, end_date:datetime):
        print(f"set_date_range called, start: {start_date}, end: {end_date}")
        #raise NotImplementedError("set_date_range not implemented")

        self.invalidate_graph_axis()

        # validate input
        if start_date is None: print("Ugyldig startdato"); return
        if end_date is None: print("Ugyldig startdato"); return
        if start_date > end_date: print("Startdato må være før sluttdato"); return

        self.date_range.start_date = start_date
        self.date_range.end_date = end_date

        self.days_interval = self.date_range.to_days_interval()

        # fire on_date_range_change callback
        if self.on_date_range_change:
            self.on_date_range_change()

        # render app
        self.render()


    # update function for reduce array -> value, default to np.mean
    def set_data_fold_callback(self, str_func_name):
        default_data_reduction_func = string_to_data_fold_func_map.get('default', np.mean)
        self.data_fold_func = string_to_data_fold_func_map.get(str_func_name, default_data_reduction_func)

        # render app
        self.render()

    # render app
    def render(self):
        # allways force re-calculation of grid samples, its not implemented thoroughly
        # invalidate_grid_samples()

        if self.plot_gui_callback is not None:
            self.plot_gui_callback()

# END Application

# create application instance
app = Application()



#----- utility functions and objects

# get a successive random seeds starting at 1
def get_next_rand_seed():
    if not hasattr(get_next_rand_seed, "counter"):
        get_next_rand_seed.counter = 0  # Static variable

    # Increment the static variable
    get_next_rand_seed.counter += 1
    return get_next_rand_seed.counter


#----- define location objects

# make locations objects for enabling iteration over stations and
# user-selected points by later putting them in an iterable

loc_kronstad = SimpleNamespace(
    name = "Kronstad",
    coordinates = (1250,1400),
    historical_data = {
		KEY_NOX: generate_sample_data(intensity=1.0, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.04, seed=get_next_rand_seed(), num_points=367, offset=20),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    data_lines = {KEY_NOX: None, KEY_APD: None},
    measurement_value = 0,
    color = UI.Colors.kronstad,
)

loc_nordnes = SimpleNamespace(
    name = "Nordnes",
    coordinates = (350,100),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.3, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.015, seed=get_next_rand_seed(), num_points=367, offset=20),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    data_lines = {KEY_NOX: None, KEY_APD: None},
    measurement_value = 0,
    color = UI.Colors.nordnes,
)

loc_bryggen = SimpleNamespace(
    name = "Bryggen",
    coordinates = (550,500),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.7, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.025, seed=get_next_rand_seed(), num_points=367, offset=20),
	},
	data_view = {KEY_NOX: [], KEY_APD: []},
    data_lines = {KEY_NOX: None, KEY_APD: None},
    measurement_value = 0,
    color = UI.Colors.bryggen,
)

loc_user = SimpleNamespace(
    name = "Valgt punkt",
    coordinates = None,
    historical_data = {KEY_NOX: [], KEY_APD: []},
    data_view = {KEY_NOX: [], KEY_APD: []},
    data_lines = {KEY_NOX: None, KEY_APD: None},
    measurement_value = 0,
    color = UI.Colors.user,
)

# make locations arrays for enabling iteration over stations
# fixed* = fixed locations, all* = fixed* + loc_user
fixed_locations = [loc_nordnes, loc_kronstad, loc_bryggen]
all_locations = [loc_nordnes, loc_kronstad, loc_bryggen, loc_user]