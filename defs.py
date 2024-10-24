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

class EmptyClass:
    pass


"""
def map_to_range(value, min_in, max_in, min_out, max_out):
    if max_in == min_in:
        raise ValueError("min_in and max_in cannot be the same value")

    return min_out + (value - min_in) * (max_out - min_out) / (max_in - min_in)
"""

def hide_axis_graphics(ax):
    ax.set_xticks([])
    ax.set_yticks([])
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
#fig, axs = plt.subplots(2, 2, figsize=(10, 8))  # 2x2 grid of subplots

class AUI:
    class Axis:
        class InputPane:
            height = 0.175

# ---------- setup environment ----------


fig = plt.figure(figsize=(18, 7))

def set_window_size(new_x:int, new_y:int, width:int, height:int):
    fig.canvas.manager.window.wm_geometry(f"{width}x{height}+{new_x}+{new_y}")

set_window_size(1950, 50, 1600, 700)

# Set only the x and y position, keeping the width and height the same
#manager.window.setGeometry(2300, 200, width, height)  # Set x=100, y=100

axInputPane = fig.add_axes((0.05, 0.75, 0.9, AUI.Axis.InputPane.height))
axInputPane.set_facecolor('#00000011')
hide_axis_graphics(axInputPane)


# create 3 axis for graphs + map

ax_nox = fig.add_axes((0.05, 0.05, 0.25, 0.5957))
ax_nox.set_facecolor('#FFFFFF77')

ax_apd = fig.add_axes((0.35, 0.05, 0.25, 0.5957))
ax_apd.set_facecolor('#FFFFFF77')

axCityMap = fig.add_axes((0.65, 0.05, 0.25, 0.7))



# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')

# define string -> date range
string_to_date_interval_map = {
    'År':           {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2025, 1, 1)},
    '1. Kvartal':   {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2024, 4, 1)},
    '2. Kvartal':   {'start_date': datetime(2024, 4, 1), 'end_date': datetime(2024, 7, 1)},
    '3. Kvartal':   {'start_date': datetime(2024, 7, 1), 'end_date': datetime(2024, 10, 1)},
    '4. Kvartal':   {'start_date': datetime(2024, 10, 1), 'end_date': datetime(2025, 1, 1)},
    'En måned':   {'start_date': datetime(2024, 10, 10), 'end_date': datetime(2024, 11, 10)},
    # TODO add more options if we dont do other ways of selecting date range
}

# define string -> data processing func
string_to_data_process_func_map = {
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


# flag to tell if we are in debug mode
DEBUG = True

# ---------- Application class ----------

class Application:
    def __init__(self):
        self.current_year = datetime.now().year
        self.data_processing_func = np.mean
        self.grid_resolutions = (20 * 2, 15 * 2)
        self.map_dimensions = (2000, 1500)
        self.date_range = DateRange(None, None)
        self.days_interval = (0, 0)

        self.plot_countour_lines = False
        self.plot_heightmap_boxed = False

        self.plot_gui_callback = None

        self.map_overlay_key = KEY_NOX

        tmp = string_to_date_interval_map['En måned']
        self.set_date_range(tmp['start_date'], tmp['end_date'])

    def get_days_interval_duration(self):
        return self.days_interval[1] - self.days_interval[0] + 1

    def set_date_range(self, start_date:datetime, end_date:datetime):
        print(f"set_date_range called, start: {start_date}, end: {end_date}")

        # validate input
        if start_date is None: print("Ugyldig startdato"); return
        if end_date is None: print("Ugyldig startdato"); return
        if start_date > end_date: print("Startdato må være før sluttdato"); return

        self.date_range.start_date = start_date
        self.date_range.end_date = end_date

        self.days_interval = self.date_range.to_days_interval()
        #print(self.days_interval)

        # optimally we should have a callback here or call to plot_app
        # we didnt have time to implement this, so called must call
        # plot_app explicitly after calling this function


    # update processing function, default to np.mean
    def set_data_processing_func(self, str_func_name):
        self.data_processing_func = string_to_data_process_func_map.get(
            str_func_name,
            string_to_data_process_func_map.get('default', np.mean)
        )

        if DEBUG:
            print(f"data processing func: {str_func_name}, {self.data_processing_func}")

    def update_gui(self):
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
		KEY_APD: generate_sample_data(intensity=0.04, seed=get_next_rand_seed(), num_points=367),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.kronstad,
)

loc_nordnes = SimpleNamespace(
    name = "Nordnes",
    coordinates = (350,100),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.3, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.015, seed=get_next_rand_seed(), num_points=367),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.nordnes,
)

loc_bryggen = SimpleNamespace(
    name = "Bryggen",
    coordinates = (550,500),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.7, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.025, seed=get_next_rand_seed(), num_points=367),
	},
	data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.bryggen,
)

loc_user = SimpleNamespace(
    name = "Valgt punkt",
    coordinates = None,
    historical_data = {KEY_NOX: [], KEY_APD: []},
    data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.user,
)

# make locations arrays for enabling iteration over stations
# fixed* is for stations, all* includes user-selected point
fixed_locations = [loc_nordnes, loc_kronstad, loc_bryggen]
all_locations = [loc_nordnes, loc_kronstad, loc_bryggen, loc_user]