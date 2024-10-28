# import constants
from constants import *
from utils import hide_axis_graphics, clog, get_function_name


# ---------- Application class ----------

class Application:
    def __init__(self):
        #self.current_year = datetime.now().year       # year
        self.data_fold_func = np.mean                  # reduce array -> value (for get_estimated_value_at_point)
        self.get_estimated_value_at_point_func = get_estimated_value_at_point_ext   # function to estimate value at point

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
    def invalidate_graph_axis(self, *args):
        if self.invalidate_graphs_callback:
            self.invalidate_graphs_callback(*args)

    # self-explanatory
    def get_days_interval_duration(self):
        return self.days_interval[1] - self.days_interval[0] + 1

    # self-explanatory
    def set_date_range(self, start_date:datetime, end_date:datetime):
        clog(f"set_date_range", start_date, end_date)
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

    # set estimation function
    def set_data_estimation_callback(self, fn):
        self.get_estimated_value_at_point_func = fn

        clog("set estimation func", get_function_name(fn))

    # set function for reduce array -> value
    def set_data_fold_callback(self, fn):
        self.data_fold_func = fn

        clog("set fold func", get_function_name(fn))

    def set_plot_type(self, attr_name:str, value:bool):
        self.plot_grid_countour_lines = False
        self.plot_grid_threshold_heatmap = False
        self.plot_grid_heatmap = False

        # set plot type
        setattr(self, attr_name, value)

        clog("set plot type", attr_name, value)

    # render app
    def render(self):
        # dont render if we are in update mode
        if self.update_count > 0:
            return

        # call render callback
        if self.plot_gui_callback is not None:
            self.plot_gui_callback()
# END Application