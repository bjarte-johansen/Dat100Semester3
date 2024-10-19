import math

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

from datetime import datetime
import calendar

#from TimerUtils import Timer

from types import SimpleNamespace

import random
from random import randint


#Generater random data for a year
# centervals are values average values for each month
# samedata = false, new data each time program is called
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
    for index in range(1,365):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, nox / center ))
        nox =  nox + randint(1,5) / dx if inc else nox - randint( 1, 5) * dx
        nox = max(10, nox)
        nox_list.append(nox)
    return nox_list
# END GenereateRandomYearDataList


# class to simplify/configure UI settings
class UI:
    marker_stroke_color:str = "#333333AA"
    marker_stroke_size:int = 3
    marker_size:int = 60
    marker_face_alpha = "66"
    marker_dot_radius = 4
    marker_dot_color = "#000000"

    class Colors:
        alpha:str = "CC"
        kronstad:str = "#c02f1e" + alpha
        nordnes:str = "#1A6390" + alpha
        bryggen: str = "#937aff" + alpha
        picked:str = "#FFc843" + alpha

#print(UI.Colors.kronstad)  # Outputs: #c02f1eaa

# define year
current_year = 2024

#create figure and 3 axis
fig = plt.figure(figsize=(13, 5))

axNok = fig.add_axes((0.05, 0.05, 0.45, 0.9))
axInterval = fig.add_axes((0.4, 0.5, 0.1, 0.25))
axBergen = fig.add_axes((0.5, 0.05, 0.5, 0.9))

axInterval.patch.set_alpha(0.3)

coordinate_dimensions = (2000, 1500)

days_interval = (1,365)

marked_point_origin = (-500,-500)
#marked_point = marked_point_origin[:]

#----- define string to days interval map

string_to_days_interval_map = {
    'År': (1, 365),
    '1. Kvartal': (1, 90),
    '2. Kvartal': (91, 181),
    '3. Kvartal': (182, 273),
    '4. Kvartal': (274, 365),
    # TODO add month 2 + month 3
}


#----- define location objects

# coordinates_kronstad = (1300, 1400)
#loc_kronstad.nox_year = GenereateRandomYearDataList(intensity=1.0, seed = 2)
loc_kronstad = SimpleNamespace(
    name = "Kronstad",
    coordinates = (1300,1400),
    nox_year = GenereateRandomYearDataList(intensity=1.0, seed = 2),
    marker = None,
    marker_dot = None,
    lines_obj = None,
)

#coordinates_nordnes = (100, 100)
#loc_nordnes.nox_year = GenereateRandomYearDataList(intensity=.3, seed = 1)
loc_nordnes = SimpleNamespace(
    name = "Nordnes",
    coordinates = (100,100),
    nox_year = GenereateRandomYearDataList(intensity=.3, seed = 1),
    marker = None,
    marker_dot = None,
    lines_obj = None,
)

loc_user = SimpleNamespace(
    name = "Valgt punkt",
    coordinates = marked_point_origin[:],
    nox_year = [],
    marker = None,
    marker_dot = None,
    lines_obj = None,
)


#
redraw_bergen = True

# flag to say if day interval has changed

# read image of bergen
img = mpimg.imread('Bergen.jpg')

def get_days_interval_duration():
    return days_interval[1] - days_interval[0] + 1

def is_quarter_period():
    return get_days_interval_duration() != 365

def set_days_interval(start, end):
    global days_interval
    #global nordnesNoxLines, kronstadNoxLines, userNoxLines, bryggenNoxLines

    days_interval = (start, end)

    # "reset" lines_obj by setting ref to None
    loc_nordnes.lines_obj = None
    loc_kronstad.lines_obj = None
    loc_user.lines_obj = None

def set_days_interval_from_str(kvartal):

    r = string_to_days_interval_map[kvartal]
    set_days_interval(r[0], r[1])

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


#estimate NOX value based on the two measuring stations
def calc_point_value(valN, valK, pt):
    dist_nordnes = math.dist(loc_nordnes.coordinates, pt)
    dist_kronstad = math.dist(loc_kronstad.coordinates, pt)
    dist_nordnes_kronstad = math.dist(loc_nordnes.coordinates, loc_kronstad.coordinates)

    total_dist = dist_kronstad + dist_nordnes

    val = ((1 - dist_kronstad / total_dist) * valK +
           (1 - dist_nordnes / total_dist) * valN)

    val = val * (dist_nordnes_kronstad / total_dist) ** 4

    return val


# Make markers markerNordnes, markerUser, markerKronstad
def draw_circles_stations():
    def create_patch_circle(xy: tuple[float, float], user_color: str):
        # method to create mpatches.circle at location, with radius, linewidth and color
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
    if is_quarter_period():
        first_month = int ((days_interval[0] / 90) * 3) + 1
        days_acc:int = 0
        xticks = [0,1,2,3]
        for x in xticks:
            xticks[x] = days_acc
            days_acc += get_days_in_month(current_year, first_month + x)

        # extract labelnames from xlabels
        xlabels = xlabels[(first_month - 1) : (first_month - 1 + 4)]

    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels)
# END draw_label_and_ticks

def plot_graph():
    global redraw_bergen

    # plot graph data, reuse lines_obj taken by <code>lines_obj, = axis.plot(...)</code>
    # WARNING!!!, do NOT remove comma after lines_obj, its not a mistake
    def plot_data(lines_obj, list_days_arg, data, color):
        if lines_obj is None:
            lines_obj, = axNok.plot(list_days_arg, data, color = color)
        else:
            lines_obj.set_data(list_days_arg, data)
        return lines_obj
    # END plot_data

    def generate_grid_samples(days, nord_nox, kron_nox):
        x_res = 20
        y_res = 15

        x_scale = (coordinate_dimensions[0] / x_res)
        y_scale = (coordinate_dimensions[1] / y_res)

        result = np.zeros((15, 20), dtype=int)

        for iy in range(0, y_res, 1):
            for ix in range(0, x_res, 1):
                pt = (
                    int(ix * x_scale),
                    int(iy * y_scale)
                )
                i = 0
                result[iy][ix] = calc_point_value(nord_nox[i], kron_nox[i], pt)
        return result
    # END create_contour_data

    # compute interval_end from days_interval
    interval_end = days_interval[1]
    if is_quarter_period():
        interval_end = days_interval[0] + (days_interval[1] - days_interval[0])

    # extract nox-profiles for fixed locations
    nord_nox = loc_nordnes.nox_year[days_interval[0] : interval_end]
    kron_nox = loc_kronstad.nox_year[days_interval[0] : interval_end]

    days = len(nord_nox)
    list_days = np.arange(1, days + 1)

    # handle user-selected point
    if loc_user.coordinates != marked_point_origin:
        # calc data-points
        nox_point = [calc_point_value(nord_nox[i], kron_nox[i], loc_user.coordinates) for i in range(days)]

        # set/update user-point NOX values
        loc_user.lines_obj = plot_data(loc_user.lines_obj, list_days, nox_point, UI.Colors.picked)

        # update marker position
        if loc_user.marker is not None:
            loc_user.marker.set_center(loc_user.coordinates)
            loc_user.marker_dot.set_center(loc_user.coordinates)
    # End of handle user-selected point
        

    loc_nordnes.lines_obj = plot_data(loc_nordnes.lines_obj, list_days, nord_nox, color=UI.Colors.nordnes)
    loc_kronstad.lines_obj = plot_data(loc_kronstad.lines_obj, list_days, kron_nox, color=UI.Colors.kronstad)

    axNok.set_title("NOX verdier")
    axInterval.set_title("Intervall")

    lines = [loc_kronstad.lines_obj, loc_nordnes.lines_obj] if loc_user.lines_obj is None else [loc_kronstad.lines_obj, loc_nordnes.lines_obj, loc_user.lines_obj]
    axNok.legend(lines, ["Nordnes", "Kronstad", "Markert plass"])
    axNok.grid(linestyle='dashed')

    axNok.relim()
    axNok.autoscale_view()

    draw_label_and_ticks()

    #Plot Map of Bergen
    axBergen.axis('off')

    if redraw_bergen:
        axBergen.imshow(img)
        redraw_bergen = False

    axBergen.set_title("Kart Bergen")
    draw_circles_stations()

    def show_contour_lines():
        result = generate_grid_samples(days, nord_nox, kron_nox)

        # Create a contour plot with smooth connected curves
        #x = np.linspace(0, 200, 20)
        #y = np.linspace(0, 150, 15)
        #X, Y = np.meshgrid(x, y)
        #Z = result

        plt.figure(figsize=(20/2, 15/2))

        plt.contour(result, levels=20, cmap='terrain')
        plt.colorbar(label='Elevation')
        plt.title('Topological Map with Smooth Contours')
        plt.gca().invert_yaxis()
        #axNok.show()

        print(result)
    # END show_contour_lines

    show_contour_lines()
    #if False:

    # END if False

    plt.draw()

plot_graph()

# draw radiobutton interval
listFonts = [12] * 5
listColors = ['yellow'] * 5
radio_button = RadioButtons(
    axInterval,
    list(string_to_days_interval_map.keys()),
    label_props = {'color': listColors, 'fontsize' : listFonts},
    radio_props = {'facecolor': listColors, 'edgecolor': listColors},
    )
axInterval.set_facecolor('darkblue')

radio_button.on_clicked(set_days_interval_from_str)

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

plt.show()