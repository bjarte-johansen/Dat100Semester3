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



# ---------- setup environment ----------

# define keys for data
KEY_NOX = 'NOX'
KEY_APD = 'APD'

# setup norwegian locale
locale.setlocale(locale.LC_ALL, 'nb_NO.UTF-8')

#create figure and 3 axis
fig = plt.figure(figsize=(13, 9))

axInputPane = fig.add_axes((0.05, 0.85, 0.9, 0.1))

axGraph = fig.add_axes((0.05, 0.05, 0.45, 0.7))
# Fix the axis limits to avoid auto-scaling
#axGraph.set_xlim(0, 300)  # Example limits, adjust as needed
#axGraph.set_ylim(0, 300)

axCityMap = fig.add_axes((0.5, 0.15, 0.5, 0.7))

# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')

# define string -> date range
string_to_days_interval_map = {
    'År':           {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2025, 1, 1)},
    '1. Kvartal':   {'start_date': datetime(2024, 1, 1), 'end_date': datetime(2024, 4, 1)},
    '2. Kvartal':   {'start_date': datetime(2024, 4, 1), 'end_date': datetime(2024, 7, 1)},
    '3. Kvartal':   {'start_date': datetime(2024, 7, 1), 'end_date': datetime(2024, 10, 1)},
    '4. Kvartal':   {'start_date': datetime(2024, 10, 1), 'end_date': datetime(2025, 1, 1)},
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
        self.user_point_origin = (500, 500)
        self.date_range = DateRange(None, None)
        self.days_interval = (0, 0)

        tmp = string_to_days_interval_map['År']
        self.set_date_range(tmp['start_date'], tmp['end_date'])

    def get_days_interval_duration(self):
        return self.days_interval[1] - self.days_interval[0] + 1

    def set_date_range(self, start_date:datetime, end_date:datetime):
        self.date_range.start_date = start_date
        self.date_range.end_date = end_date

        self.days_interval = self.date_range.to_days_interval()
        print(self.days_interval)


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



#----- define location objects


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

# make fixed locations array
fixed_locations = [loc_nordnes, loc_kronstad, loc_bryggen]