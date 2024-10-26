import locale
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# import constants
from constants import *
from utils import hide_axis_graphics



# ---------- setup fix and main axis ----------

fig = plt.figure(figsize=(13, 7))

# create axis for input pane
ax_input_pane = fig.add_axes((0.05, 0.8125, 0.9, 0.175))
ax_input_pane.set_facecolor('#00000000')
hide_axis_graphics(ax_input_pane)

# create 3 axis for NOX/APD and for map of Bergen City
ax_nox = fig.add_axes((0.05, 0.19, 0.25, 0.4557))
ax_nox.set_facecolor('#FFFFFF77')

ax_apd = fig.add_axes((0.35, 0.19, 0.25, 0.4557))
ax_apd.set_facecolor('#FFFFFF77')

ax_city_map = fig.add_axes((0.65, 0.12, 0.30, 0.61))


# read image of bergen
city_map_image = mpimg.imread('Bergen.jpg')


# set window size
def set_window_size(new_x:int, new_y:int, width:int, height:int):
    fig.canvas.manager.window.wm_geometry(f"{width}x{height}+{new_x}+{new_y}")

#set_window_size(1950, 50, 1600, 850)


# setup norwegian locale
locale.setlocale(locale.LC_ALL, 'nb_NO.UTF-8')



# ---------- Application class ----------

class Application:
    def __init__(self):
        #self.current_year = datetime.now().year       # year
        self.data_fold_func = np.mean                  # reduce array -> value (for get_estimated_value_at_point)
        self.get_estimated_value_at_point_func = get_estimated_value_at_point   # function to estimate value at point

        self.grid_resolution = (20 * 2, 15 * 2)        # resolution of grid for contour/heatmap etc
        self.map_dimension = (2000, 1500)              # dimensions of map
        self.date_range = DateRange(None, None)        # date range
        self.days_interval = (0, 0)

        self.plot_grid_countour_lines = False
        self.plot_grid_threshold_heatmap = False
        self.plot_grid_heatmap = False

        self.plot_gui_callback = None                   # callback to plot gui

        self.map_overlay_key = KEY_NOX                  # data_key to display contour / heightmap etc
        self.update_count = 0                           # flag for update mode, no renders are done if > 0
        self.user_location = None                       # reference to user location
        self.invalidate_graphs_callback = None          # callback for invalidating graphs

        tmp = string_to_date_interval_map['År']
        self.set_date_range(tmp['start_date'], tmp['end_date'])

    # begin batch updates (no rendering)
    def begin_update(self):
        self.update_count += 1

    # end batch updates (renders), render if update_count reaches 0
    def end_update(self, cancel:bool=False):
        self.update_count -= 1

        # render if update_count reaches 0
        if self.update_count == 0:
            # exit if user cancelled rendering
            if cancel:
                return

            # render
            self.render()

    # clear graph axis
    def invalidate_graph_axis(self, render:bool=False):
        if self.invalidate_graphs_callback:
            self.invalidate_graphs_callback()

    # self-explanatory
    def get_days_interval_duration(self):
        return self.days_interval[1] - self.days_interval[0] + 1

    # self-explanatory
    def set_date_range(self, start_date:datetime, end_date:datetime):
        print(f"set_date_range called, start: {start_date}, end: {end_date}")
        #raise NotImplementedError("set_date_range not implemented")

        # validate input
        if start_date is None: print("Ugyldig startdato"); return
        if end_date is None: print("Ugyldig startdato"); return
        if start_date > end_date: print("Startdato må være før sluttdato"); return

        self.date_range.start_date = start_date
        self.date_range.end_date = end_date

        self.days_interval = self.date_range.to_days_interval()

        # invalidate graphs
        self.invalidate_graph_axis()

        # render app
        self.render()


    # update function for reduce array -> value, default to np.mean
    def set_data_fold_callback(self, str_func_name):
        default_data_reduction_func = string_to_data_fold_func_map.get('default', np.mean)
        self.data_fold_func = string_to_data_fold_func_map.get(str_func_name, default_data_reduction_func)


    # render app
    def render(self):
        # dont render if we are in update mode
        if self.update_count > 0:
            return

        # call render callback
        if self.plot_gui_callback is not None:
            self.plot_gui_callback()

# END Application

app = Application()