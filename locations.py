from types import SimpleNamespace

# import application specific modules
from constants import *
from ui import UI
from utils import get_next_rand_seed
from data_functions import generate_sample_data



#----- define location objects

# make locations objects for enabling iteration over stations and
# user-selected points by later putting them in an iterable

loc_kronstad = SimpleNamespace(
    name = "Kronstad",
    coordinates = (1250,1400),
    historical_data = {
		KEY_NOX: generate_sample_data(intensity=1.0, seed=get_next_rand_seed(), num_points=367),
		KEY_APD: generate_sample_data(intensity=0.5, seed=get_next_rand_seed(), num_points=367, offset=20),
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
		KEY_APD: generate_sample_data(intensity=0.6, seed=get_next_rand_seed(), num_points=367, offset=20),
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
		KEY_APD: generate_sample_data(intensity=0.4, seed=get_next_rand_seed(), num_points=367, offset=20),
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
fixed_locations = [
	loc_nordnes,
	loc_kronstad,
	loc_bryggen
	]
all_locations = fixed_locations + [loc_user]