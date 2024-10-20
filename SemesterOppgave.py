import math

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

import calendar

from types import SimpleNamespace

from typing import Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import random
from random import randint


#Generater random data for a year
# centervals are values average values for each month
# samedata = false, new data each time program is called
# known bugs:
# - Fixed error that caused function to only generate 364 data points
# - 2024 is a leap year so we generate 365 data points
def GenereateRandomYearDataList(intensity:float, seed:int=0) -> list[int]:
    """
    :param intensity: Number specifying size, amplitude
    :param seed: If given, same data with seed is generated
    :return:
    """
    if seed != 0:
        random.seed(seed)
    centervals = [200,150,100, 75,75,75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intensity for x in centervals]
    nox = centervals[0]
    inc = True
    nox_list = []
    for index in range(0,366):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, nox / center ))
        nox =  nox + randint(1,5) / dx if inc else nox - randint( 1, 5) * dx
        nox = max(10, nox)
        nox_list.append(nox)
    return nox_list
# END GenereateRandomYearDataList


def ExtractDataInterval(data, start, end):
    result = data[start : end]
    print("extracting data from ", start, " to ", end, " length: ", len(result))
    print("extracted data length: ", len(result))
    return result


# class to simplify/configure UI settings
class UI:
    marker_stroke_color:str = "#333333AA"
    marker_stroke_size:int = 3
    marker_size:int = 60
    marker_face_alpha = "66"
    marker_dot_radius = 4
    marker_dot_color = "#000000"

    class RadioGroup:
        bg_color = '#FFFFFFCC'

    class Colors:
        alpha:str = "CC"
        kronstad:str = "#c02f1e" + alpha
        nordnes:str = "#1A6390" + alpha
        bryggen: str = "#937aff" + alpha
        picked:str = "#FFc843" + alpha


#create figure and 3 axis
fig = plt.figure(figsize=(13, 5))

axNok = fig.add_axes((0.05, 0.05, 0.45, 0.9))
axInterval = fig.add_axes((0.4, 0.5, 0.1, 0.25))
axInterval.patch.set_alpha(0.3)
axBergen = fig.add_axes((0.5, 0.05, 0.5, 0.9))


days_interval = (1,365)

marked_point_origin = (-500,-500)

date_interval_type_to_string_map = {
    'År'        : 'year',
    'Kvartal'   : 'quarter',
    'Måned'     : 'month',
    'Day'       : 'day',
}

#def get_days_per_year(year) -> int:
#    return 366 if calendar.isleap(year) else 365

def get_days_in_month(year, month) -> int:
    month = (month - 1) % 12 + 1
    return calendar.monthrange(year, month)[1]

def get_days_between_dates(start_date, end_date) -> int:
    return (end_date - start_date).days

class DateInterval:
    def __init__(self, type_id, year, start, length):
        self.type_id = type_id
        self.year = year
        self.start = start
        self.length = length

    def convert_dates_to_days_interval(self, start_date, end_date, zero_based = False) -> Tuple[int, int]:
        zbo = 0 if zero_based else 1
        start_of_year_date = datetime(self.year, 1, 1)
        days_into_year = get_days_between_dates(start_of_year_date, start_date) + zbo - 1

        print(f"type_id: {self.type_id}")
        print(f"start days into year: {days_into_year}")
        print(f"start_date: {start_date}, end_date, {end_date}")
        print(f"days between dates: {get_days_between_dates(start_date, end_date)}")

        return (days_into_year, days_into_year + get_days_between_dates(start_date, end_date))

    def to_days_interval(self, zero_based = False) -> Tuple[int, int]:
        zbo = 0 if zero_based else 1

        # convert to days interval
        if self.type_id == 'year':
            start_date = datetime(self.year, 1, 1)
            end_date = start_date + relativedelta(months=12)
            return self.convert_dates_to_days_interval(self, start_date, end_date, zero_based)

        if self.type_id == 'quarter':
            start_date = datetime(self.year, self.start, 1)
            end_date = start_date + relativedelta(months=3)
            return self.convert_dates_to_days_interval(self, start_date, end_date, zero_based)

        if self.type_id == 'month':
            start_date = datetime(self.year, self.start, 1)
            end_date = start_date + relativedelta(months=self.length)
            return self.convert_dates_to_days_interval(self, start_date, end_date, zero_based)

        if self.type_id == 'day':
            start_date = datetime(self.year, self.start, 1)
            end_date = start_date + timedelta(days=self.length)
            return self.convert_dates_to_days_interval(self, start_date, end_date, zero_based)

        raise ValueError("Unknown date interval type")
# END DateInterval

"""
print("-- convert_dates_to_days_interval --")
di1 = DateInterval('year', 2024, 1, 1)
print(di1.to_days_interval())
print("-- end convert_dates_to_days_interval --\n")

print("-- convert_dates_to_days_interval --")
di1 = DateInterval('month', 2024, 1, 1)
print(di1.to_days_interval())
print("-- end convert_dates_to_days_interval --\n")

print("-- convert_dates_to_days_interval --")
di1 = DateInterval('day', 2024, 1, 1)
print(di1.to_days_interval())
print("-- end convert_dates_to_days_interval --\n")
"""

#----- define string to days interval map
string_to_days_interval_map = {
    'År': (1, 365),
    '1. Kvartal': (1, 90),
    '2. Kvartal': (91, 181),
    '3. Kvartal': (182, 273),
    '4. Kvartal': (274, 365),
    # TODO add month 2 + month 3
}

#----- define string to days interval map
string_to_data_process_func = {
    'min': np.min,
    'max': np.max,
    'mean': np.mean,
    'median': np.median,
    'default': np.mean,
}


# define application main-class
class Application:
    def __init__(self):
        self.data_processing_func = np.mean
        self.grid_resolutions = (10, 10)
        self.current_year = 2024
        self.coordinate_dimensions = (2000, 1500)

    # update processing function, default to np.mean
    def set_data_processing_func(self, str_func_name):
        self.data_processing_func = string_to_data_process_func.get(
            str_func_name,
            string_to_data_process_func.get('default', np.mean)
        )
        print(f"data processing func: {str_func_name}, {self.data_processing_func}")
# END Application

# create application instance
app = Application()
app.grid_resolutions = (20, 15)         # grid resolution for contour plot etc
app.current_year = datetime.now().year  # set current year

#----- define location objects

loc_kronstad = SimpleNamespace(
    name = "Kronstad",
    coordinates = (1300,1400),
    nox_year = GenereateRandomYearDataList(intensity=1.0, seed = 2),
    marker = None,
    marker_dot = None,
)

loc_nordnes = SimpleNamespace(
    name = "Nordnes",
    coordinates = (100,100),
    nox_year = GenereateRandomYearDataList(intensity=.3, seed = 1),
    marker = None,
    marker_dot = None,
)

loc_bryggen = SimpleNamespace(
    name = "Nordnes",
    coordinates = (300,400),
    nox_year = GenereateRandomYearDataList(intensity=.5, seed = 3),
    marker = None,
    marker_dot = None,
)

loc_user = SimpleNamespace(
    name = "Valgt punkt",
    coordinates = marked_point_origin[:],
    nox_year = [],
    marker = None,
    marker_dot = None,
)


#
redraw_bergen = True

# flag to say if day interval has changed

# read image of bergen
city_map_image = None

def get_days_interval_duration():
    return days_interval[1] - days_interval[0] + 1

"""
def is_quarter_period():
    return get_days_interval_duration() != 365
"""

def is_year_period():
    return get_days_interval_duration() == 365

def set_days_interval_from_str(kvartal):
    global days_interval

    # set days interval from string_to_days_interval_map[kvartal]
    days_interval = string_to_days_interval_map[kvartal][:]

    # reset user-selected point
    loc_user.coordinates = marked_point_origin[:]
    if loc_user.marker is not None:
        loc_user.marker.set_center(loc_user.coordinates)
        loc_user.marker_dot.set_center(loc_user.coordinates)

    axNok.cla()
    plot_graph()

def on_click(event) :
    if ax := event.inaxes:
        if ax == axBergen:
            loc_user.coordinates = (event.xdata, event.ydata)
            plot_graph()


#estimate NOX value based on the two or more measuring stations
# - valN: NOX value at Nordnes
# - valK: NOX value at Kronstad
# - pt: point to estimate NOX value at
def get_estimated_value_at_point(valN, valK, pt):
    dist_nordnes = math.dist(loc_nordnes.coordinates, pt)
    dist_kronstad = math.dist(loc_kronstad.coordinates, pt)
    dist_nordnes_kronstad = math.dist(loc_nordnes.coordinates, loc_kronstad.coordinates)

    total_dist = dist_kronstad + dist_nordnes

    val = ((1 - dist_kronstad / total_dist) * valK +
           (1 - dist_nordnes / total_dist) * valN)

    val = val * (dist_nordnes_kronstad / total_dist) ** 4

    return val
# END get_estimated_value_at_point

# Make markers at fixed and user-selected locations
# we store markers in loc_nordnes.marker, loc_kronstad.marker, loc_user.marker, etc
def draw_circles_stations():
    def create_patch_circle(xy: tuple[float, float], user_color: str):
        circle = mpatches.Circle(xy, UI.marker_size, fill=True, linewidth=UI.marker_stroke_size, color=user_color)
        circle.set_edgecolor(user_color)
        circle.set_facecolor(user_color[0:7] + UI.marker_face_alpha)
        return circle
    # END create_patch_circle

    if loc_nordnes.marker is None:
        loc_nordnes.marker_dot = mpatches.Circle(loc_nordnes.coordinates, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)
        axBergen.add_patch(loc_nordnes.marker_dot)

        loc_nordnes.marker = create_patch_circle(loc_nordnes.coordinates, UI.Colors.nordnes)
        axBergen.add_patch(loc_nordnes.marker)

    if loc_kronstad.marker is None:
        loc_kronstad.marker_dot = mpatches.Circle(loc_kronstad.coordinates, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)
        axBergen.add_patch(loc_kronstad.marker_dot)

        loc_kronstad.marker = create_patch_circle(loc_kronstad.coordinates, UI.Colors.kronstad)
        axBergen.add_patch(loc_kronstad.marker)

    if loc_user.marker is None:
        loc_user.marker_dot = mpatches.Circle(loc_user.coordinates, UI.marker_dot_radius, fill=True, color=UI.marker_dot_color)
        axBergen.add_patch(loc_user.marker_dot)

        loc_user.marker = create_patch_circle(loc_user.coordinates, UI.Colors.picked)
        axBergen.add_patch(loc_user.marker)
# END draw_circles_stations


def draw_label_and_ticks():
    def get_days_in_month(year, month) -> int:
        month = (month - 1) % 12 + 1
        return calendar.monthrange(year, month)[1]
    # END get_days_in_month

    num_labels = 13
    xlabels = ['Jan' ,'Feb' ,'Mar' ,'Apr' ,'Mai' ,'Jun', 'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Des', 'Jan']
    xticks = np.linspace(0, 365, num_labels)

    # compute xticks and xlabels correctly
    # we take into account number of days per month
    # TODO: get number of monhts in interval and adapt ticks and labels to this
    #   - right now we just do the fixed quarters
    if not is_year_period():
        # compute first month
        first_month = int ((days_interval[0] / 90) * 3) + 1

        # compute xticks, accumulative ticks per month based on days
        acc = 0
        xticks = [0,1,2,3]
        for x in xticks:
            xticks[x] = acc
            acc += get_days_in_month(app.current_year, first_month + x)

        # extract labelnames from xlabels
        xlabels = xlabels[(first_month - 1) : (first_month - 1 + 4)]

    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels)
# END draw_label_and_ticks

def plot_graph():
    global redraw_bergen

    # plot graph data, reuse lines_obj taken by <code>lines_obj, = axis.plot(...)</code>
    # WARNING!!!, do NOT remove comma after lines_obj, its not a mistake
    def plot_data(list_days_arg, data, color):
        lines_obj, = axNok.plot(list_days_arg, data, color = color)
        return lines_obj
    # END plot_data
    """
    def plot_data(lines_obj, list_days_arg, data, color):
        if lines_obj is None:
            lines_obj, = axNok.plot(list_days_arg, data, color = color)
        else:
            lines_obj.set_data(list_days_arg, data)
        return lines_obj
    # END plot_data
    """

    def generate_grid_samples(nord_nox, kron_nox, preprocess_func):
        x_scale = (app.coordinate_dimensions[0] / app.grid_resolutions[0])
        y_scale = (app.coordinate_dimensions[1] / app.grid_resolutions[1])

        computed_nord_nox = preprocess_func(nord_nox)
        computed_kron_nox = preprocess_func(kron_nox)

        result = np.zeros((app.grid_resolutions[1], app.grid_resolutions[0]), dtype=int)

        for iy in range(0, app.grid_resolutions[1], 1):
            for ix in range(0, app.grid_resolutions[0], 1):
                pt = (
                    int(ix * x_scale),
                    int(iy * y_scale)
                )
                i = 0
                result[iy][ix] = get_estimated_value_at_point(computed_nord_nox, computed_kron_nox, pt)
        return result
    # END create_contour_data

    axNok.cla()

    legend_lines = []

    # extract nox-profiles for fixed locations
    nord_nox = ExtractDataInterval(loc_nordnes.nox_year, days_interval[0], days_interval[0] + get_days_interval_duration())
    kron_nox = ExtractDataInterval(loc_kronstad.nox_year, days_interval[0], days_interval[0] + get_days_interval_duration())

    days = len(nord_nox)
    print(f"data length: {days}, interval duration: {get_days_interval_duration()}")

    # arange is end-exclusive but we allready adding 1
    list_days = np.arange(0, days)

    # handle user-selected point
    if loc_user.coordinates != marked_point_origin:
        # calc data-points
        nox_point = [get_estimated_value_at_point(nord_nox[i], kron_nox[i], loc_user.coordinates) for i in range(0, days)]

        # set/update user-point NOX values
        lines = plot_data(list_days, nox_point, color=UI.Colors.picked)
        legend_lines.append(lines)

        # update marker position
        if loc_user.marker is not None:
            loc_user.marker.set_center(loc_user.coordinates)
            loc_user.marker_dot.set_center(loc_user.coordinates)
    # End of handle user-selected point

    # plot data for fixed locations
    lines = plot_data(list_days, nord_nox, color=UI.Colors.nordnes)
    legend_lines.append(lines)
    lines = plot_data(list_days, kron_nox, color=UI.Colors.kronstad)
    legend_lines.append(lines)

    axNok.set_title("NOX verdier")
    axInterval.set_title("Intervall")

    axNok.legend(legend_lines, ["Nordnes", "Kronstad", "Markert plass"])
    axNok.grid(linestyle='dashed')

    axNok.relim()
    axNok.autoscale_view()

    draw_label_and_ticks()

    #Plot Map of Bergen
    axBergen.axis('off')

    # image of city map
    global city_map_image
    if city_map_image is None:
        city_map_image = mpimg.imread('Bergen.jpg')
        axBergen.imshow(city_map_image)

    axBergen.set_title("Kart Bergen")
    draw_circles_stations()

    # Draw mean, or average, horizontal lines using correct styles
    axNok.axhline(np.mean(nord_nox), color=UI.Colors.nordnes, linestyle='--', linewidth=1),
    axNok.axhline(np.mean(kron_nox), color=UI.Colors.kronstad, linestyle='--', linewidth=1)

    def show_contour_lines():
        result = generate_grid_samples(nord_nox, kron_nox, app.data_processing_func)

        plt.figure(figsize=(20/2, 15/2))

        plt.contour(result, levels=20, cmap='terrain')
        plt.colorbar(label='Elevation')
        plt.title('Topological Map with Smooth Contours')
        plt.gca().invert_yaxis()
    # END show_contour_lines

    #show_contour_lines()

    plt.draw()

"""
    for line in hor_lines:
        line.remove()
"""

plot_graph()

# draw radio button group, list_options is a map
def create_radio_button_panel(ax, list_options, on_clicked):
    num_options = len(list_options)
    list_fonts = [10] * num_options
    list_colors = ['#333333'] * num_options
    radio_button = RadioButtons(
        ax,
        list_options,
        label_props = {'color': list_colors, 'fontsize' : list_fonts},
        radio_props = {'facecolor': list_colors, 'edgecolor': list_colors},
        )
    radio_button.on_clicked(on_clicked)
    return radio_button
# END create_radio_button_panel

# Create two axes for the radio buttons (stacked vertically)
axInterval1 = plt.axes([0.05, 0.6, 0.1, 0.2], facecolor = UI.RadioGroup.bg_color)  # First radio button group
axInterval2 = plt.axes([0.05, 0.2, 0.1, 0.2], facecolor = UI.RadioGroup.bg_color)  # Second radio button group

radio_data_process_func_select = create_radio_button_panel(
    axInterval1,
    list(string_to_data_process_func.keys()),
    app.set_data_processing_func
    )

radio_interval_select = create_radio_button_panel(
    axInterval2,
    list(string_to_days_interval_map.keys()),
    set_days_interval_from_str
    )

#--------- radio buttons done

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

plt.show()