import locale
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# import constants
from utils import hide_axis_graphics
from Application import Application



# ---------- setup fix and main axis ----------

fig = plt.figure(figsize=(13, 7))

# create axis for input pane
ax_input_pane = fig.add_axes((0.05, 0.8125, 0.9, 0.175))
ax_input_pane.set_facecolor('#00000000')
hide_axis_graphics(ax_input_pane)

# create 3 axis for NOX/APD/map
ax_nox = fig.add_axes((0.05, 0.19, 0.25, 0.4557))
ax_nox.set_facecolor('#FFFFFF77')

ax_apd = fig.add_axes((0.35, 0.19, 0.25, 0.4557))
ax_apd.set_facecolor('#FFFFFF77')

ax_city_map = fig.add_axes((0.65, 0.12, 0.30, 0.61))


# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')

# setup norwegian locale
locale.setlocale(locale.LC_ALL, 'nb_NO.UTF-8')

# create application instance
app = Application()

# used during development for multiscreen positioning
#set_window_size(fig, 1950, 50, 1600, 850)
