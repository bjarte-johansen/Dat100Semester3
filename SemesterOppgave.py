import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

from datetime import datetime
import calendar

from TimerUtils import Timer

#Generater random data for a year
# centervals are values average values for each month
# samedata = false, new data each time program is called
import random
from random import randint

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

kron_nox_year = GenereateRandomYearDataList(intensity=1.0, seed = 2)
nord_nox_year = GenereateRandomYearDataList(intensity=.3, seed = 1)




from types import SimpleNamespace

class UI:
    marker_stroke_color:str = "#333333AA"
    marker_stroke_size:int = 2
    marker_size:int = 60

    class Colors:
        alpha:str = "CC"
        kronstad:str = "#c02f1e" + alpha
        nordnes:str = "#1A6390" + alpha
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

coordinates_Nordnes = (100, 100)
coordinates_Kronstad = (1300, 1400)
days_interval = (1,365)
marked_point = (0,0)


# ui-markers
uiMarkerNordnes = None
uiMarkerKronstad = None
uiMarkerUser = None

# Initialize l3 as a global variable outside the function
nordnesNoxLines = None
kronstadNoxLines = None
userNoxLines = None
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
    global nordnesNoxLines, kronstadNoxLines, userNoxLines

    days_interval = (start, end)

    nordnesNoxLines = None
    kronstadNoxLines = None
    userNoxLines = None

def set_days_interval_from_str(kvartal):
    global marked_point
    axNok.cla()

    kvartal_string_to_interval_map = {
        'År'        : (1, 365),
        '1. Kvartal': (1, 90),
        '2. Kvartal': (91, 181),
        '3. Kvartal': (182, 273),
        '4. Kvartal': (274, 365),
    }

    r = kvartal_string_to_interval_map[kvartal]
    set_days_interval(r[0], r[1])

    marked_point = (0, 0)
    plot_graph()

def on_click(event) :
    global marked_point
    if ax := event.inaxes:
        if ax == axBergen:
            marked_point = (event.xdata, event.ydata)
            plot_graph()


#estimate NOX value based on the two measuring stations
def calc_point_value(valN, valK):
    dist_nordnes = math.dist(coordinates_Nordnes, marked_point)
    dist_kronstad = math.dist(coordinates_Kronstad, marked_point)
    dist_nordnes_kronstad = math.dist(coordinates_Nordnes, coordinates_Kronstad)
    val = (1 - dist_kronstad / (dist_kronstad + dist_nordnes)) * valK  + (1 - dist_nordnes /(dist_kronstad + dist_nordnes))* valN
    val = val * ( dist_nordnes_kronstad / (dist_nordnes + dist_kronstad) ) ** 4

    return val

def create_patch_circle(xy:tuple[float,float], radius:float, user_linewidth:int=4, user_color:str="#000000"):
    circle = mpatches.Circle(xy, radius, fill=True, linewidth=user_linewidth, color=user_color)
    circle.set_edgecolor(UI.marker_stroke_color)
    circle.set_facecolor(user_color)
    return circle

# Make markers markerNordnes, markerUser, markerKronstad
def draw_circles_stations():
    global uiMarkerNordnes, uiMarkerUser, uiMarkerKronstad

    if uiMarkerNordnes is None:
        uiMarkerNordnes = create_patch_circle((100, 100), UI.marker_size, user_linewidth=UI.marker_stroke_size, user_color=UI.Colors.nordnes)
        axBergen.add_patch(uiMarkerNordnes)

    if uiMarkerUser is None:
        uiMarkerUser = create_patch_circle((300, 400), UI.marker_size, user_linewidth=UI.marker_stroke_size, user_color=UI.Colors.picked)
        axBergen.add_patch(uiMarkerUser)

    if uiMarkerKronstad is None:
        uiMarkerKronstad = create_patch_circle((1300, 1400), UI.marker_size, user_linewidth=UI.marker_stroke_size, user_color=UI.Colors.kronstad)
        axBergen.add_patch(uiMarkerKronstad)

def draw_label_and_ticks():
    def mod_slice(arr, start, stop, step=1):
        length = len(arr)
        indices = range(start, stop, step)

        # Wrap each index using modulo
        wrapped_indices = [(i % length) for i in indices]

        # Use list comprehension to get the elements
        return [arr[i] for i in wrapped_indices]

    def get_days_in_month(year, month) -> int:
        while month > 12:
            month = month - 12
        return calendar.monthrange(year, month)[1]

    global days_interval

    num_labels = 13
    xlabels = ['Jan' ,'Feb' ,'Mar' ,'Apr' ,'Mai' ,'Jun', 'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Des', 'Jan']
    xticks = np.linspace(0, 365, num_labels)

    if is_quarter_period():
        first_month = int ((days_interval[0] / 90) * 3)
        days_acc:int = 0
        xticks = [0,1,2,3]
        for x in xticks:
            xticks[x] = days_acc
            days_acc += get_days_in_month(current_year, first_month + 1 + x)

        xlabels = mod_slice(xlabels, first_month, first_month + 4)

    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels)

def plot_graph():
    global img
    global userNoxLines
    global kronstadNoxLines
    global nordnesNoxLines
    global redraw_bergen

    def print_functions(obj):
        functions = [func for func in dir(obj) if callable(getattr(obj, func))]
        for func in functions:
            print(func)


    def plot_data(lines_obj, list_days_arg, data, color):
        if lines_obj is None:
            lines_obj, = axNok.plot(list_days_arg, data, color = color)
        else:
            lines_obj.set_data(list_days_arg, data)
        return lines_obj

    interval_end = days_interval[1]
    if is_quarter_period():
        interval_end = days_interval[0] + (days_interval[1] - days_interval[0])

    nord_nox = nord_nox_year[days_interval[0] : interval_end]
    kron_nox = kron_nox_year[days_interval[0] : interval_end]

    days = len(nord_nox)
    list_days = np.arange(1, days + 1)
    #list_days = np.linspace(1, days, days)

    #draw the marked point & the orange graph
    if marked_point != (0,0):
        nox_point = [calc_point_value(nord_nox[i], kron_nox[i]) for i in range(days)]

        # set/update user-point NOX values
        userNoxLines = plot_data(userNoxLines, list_days, nox_point, UI.Colors.picked)

        if uiMarkerUser is not None:
            uiMarkerUser.set_center(marked_point)

    nordnesNoxLines = plot_data(nordnesNoxLines, list_days, nord_nox, color=UI.Colors.nordnes)
    kronstadNoxLines = plot_data(kronstadNoxLines, list_days, kron_nox, color=UI.Colors.kronstad)

    axNok.set_title("NOX verdier")
    axInterval.set_title("Intervall")

    lines = [kronstadNoxLines, nordnesNoxLines] if userNoxLines is None else [kronstadNoxLines, nordnesNoxLines, userNoxLines]
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

    plt.draw()

plot_graph()

# draw radiobutton interval
listFonts = [12] * 5
listColors = ['yellow'] * 5
radio_button = RadioButtons(axInterval,
(
    'År',
    '1. Kvartal',
    '2. Kvartal',
    '3. Kvartal',
    '4. Kvartal'
    ),
    label_props = {'color': listColors, 'fontsize' : listFonts},
    radio_props = {'facecolor': listColors,  'edgecolor': listColors},
    )
axInterval.set_facecolor('darkblue')

radio_button.on_clicked(set_days_interval_from_str)

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

plt.show()

