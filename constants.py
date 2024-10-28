# import application specific modules
from DateRange import *
from data_functions import *



# low-res heatmap rendering, adjust for specific user to mark areas where
# NOX / APD values are above a certain threshold, todo: add to GUI

MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED = 0.5         # threshold for heightmap boxed rendering



# these keys are specific to the historical_data, data_view and data_lines dictionaries
# they tell us what kind of data we are dealing with and also is a key for the dictionary

KEY_NOX = 'NOX'
KEY_APD = 'APD'



# define axis types, for future use for cleaing specific axis thru function calls

AXIS_NONE = 0
AXIS_ALL = 1
AXIS_GRAPH = 2
AXIS_MAP = 3



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
string_to_plot_type_map = {
    'Ingen': 'none',
    'Kontur': 'plot_grid_countour_lines',
    'Verdibokser': 'plot_grid_threshold_heatmap',
    'Heatmap': 'plot_grid_heatmap',
}

# define string -> map overlay
string_to_map_overlay_map = {
    'NOX': KEY_NOX,
    'APD': KEY_APD,
}

# define string -> estimate
string_to_estimate_func_map = {
    'Weighted-1': get_estimated_value_at_point_ext,
    'Weighted-2': get_estimated_value_at_point,
}