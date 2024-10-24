import locale

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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



def map_to_range(value, min_in, max_in, min_out, max_out):
    if max_in == min_in:
        raise ValueError("min_in and max_in cannot be the same value")

    return min_out + (value - min_in) * (max_out - min_out) / (max_in - min_in)


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
fig = plt.figure(figsize=(13, 9))

class AxisRectangle:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x * width
        self.y = height - y * height
        self.width = width
        self.height = height

    def min_x(self):
        return self.x
    def max_x(self):
        return self.x + self.width
    def min_y(self):
        return self.y
    def max_y(self):
        return self.y + self.height

    def to_array(self):
        return [self.min_x(), self.min_y(), self.max_x(), self.max_y()]

# Get figure size in pixels

def get_axis_bounding_box(axis):
    # Get figure size in pixels (width, height)
    fig_size_inch = fig.get_size_inches()
    fig_size_pixels = fig.get_size_inches() * fig.dpi
    print("fig_size_inch: ", fig_size_inch)
    print("fig_size_pixels: ", fig_size_pixels)

    fig_size = fig.get_size_inches() * fig.dpi
    print(f"fig size: {float(fig_size[0]), float(fig_size[1])}")

    #bbox = axis.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #print(f"boox in pixel coordinates: {bbox}")

    # Transform the bounding box to figure-relative coordinates (normalized)
    bbox = axis.get_window_extent()

    bb = bbox.transformed(fig.dpi_scale_trans.inverted())
    #print(f"boox in normalized figure coords: {bb}")

    bb_norm = [
        bb.x0 / fig_size_inch[0],
        bb.y0 / fig_size_inch[1],
        bb.width / fig_size_inch[0],
        bb.height / fig_size_inch[1]
    ]
    print("bb_norm", *bb_norm)

    bb_pixel = [
        bb_norm[0]  * fig_size_pixels[0],
        (1 - bb_norm[1]) * fig_size_pixels[1],
        bb_norm[2] * fig_size_pixels[0],
        bb_norm[3] * fig_size_pixels[1],
    ]
    print("bb_pixel", *bb_pixel)
# END get_axis_bounding_box

"""
axInputPane = fig.add_axes((0.05, 0.725, 0.9, 0.015))
axInputPane.set_facecolor('red')
hide_axis_graphics(axInputPane)
"""

axInputPane = fig.add_axes((0.05, 0.75, 0.9, 0.20))
axInputPane.set_facecolor('#00000011')
hide_axis_graphics(axInputPane)

#get_axis_bounding_box(axInputPane)

#exit()

axGraph = fig.add_axes((0.05, 0.05, 0.40, 0.5957))
axGraph.set_facecolor('#FFFFFF77')

axCityMap = fig.add_axes((0.50, 0.05, 0.45, 0.7))

#axGraph.set_xlim(0, 1000)
#axGraph.set_ylim(0, 800)

# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')

# define string -> date range
string_to_date_interval_map = {
    'År':           {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2025, 1, 1)},
    '1. Kvartal':   {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2024, 4, 1)},
    '2. Kvartal':   {'start_date': datetime(2024, 4, 1), 'end_date': datetime(2024, 7, 1)},
    '3. Kvartal':   {'start_date': datetime(2024, 7, 1), 'end_date': datetime(2024, 10, 1)},
    '4. Kvartal':   {'start_date': datetime(2024, 10, 1), 'end_date': datetime(2025, 1, 1)},
    '14 dager':   {'start_date': datetime(2024, 10, 10), 'end_date': datetime(2024, 11, 10)},
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

        tmp = string_to_date_interval_map['14 dager']
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
        print(self.days_interval)

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
# END Application

# create application instance
app = Application()

#axGraph.set_xlim(0, app.map_dimensions[0])  # Example limits, adjust as needed
#axGraph.set_ylim(app.map_dimensions[1], 0)

# Equal scaling on both axes
#axGraph.set_aspect('equal', 'box')



#----- define location objects

# make locations objects for enabling iteration over stations and
# user-selected points by later putting them in an iterable

loc_kronstad = SimpleNamespace(
    name = "Kronstad",
    coordinates = (1250,1400),
    historical_data = {
		KEY_NOX: generate_sample_data(intensity=1.0, seed=2, num_points=367),
		KEY_APD: generate_sample_data(intensity=0.4, seed=2, num_points=367),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.kronstad,
)

loc_nordnes = SimpleNamespace(
    name = "Nordnes",
    coordinates = (350,100),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.3, seed=1, num_points=367),
		KEY_APD: generate_sample_data(intensity=0.15, seed=1, num_points=367),
	},
    data_view = {KEY_NOX: [], KEY_APD: []},
    measurement_value = 0,
    color = UI.Colors.nordnes,
)

loc_bryggen = SimpleNamespace(
    name = "Bryggen",
    coordinates = (550,500),
	historical_data = {
		KEY_NOX: generate_sample_data(intensity=0.7, seed=3, num_points=367),
		KEY_APD: generate_sample_data(intensity=0.25, seed=3, num_points=367),
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