"""
    Note:
        - The original application has been heavily refactored to use a more object-oriented
        approach. get_estimated_value_at_point has been refactored/rewritten to use a more
        advanced weighting function, that mimics the original, it is not perfect but it
        is probably not the main goal of the assignment.

        - We have focused on code quality and functionality instead of the design
        of the UI (see Coding section below). This makes it easier to develop the app
        further (we should have used tkinter or similar, it would have made it easier !!)

        - We have changed the application to use start/end date instead of relying on
        fixed 90/180/270 etc due to problems with different days in months, leap years etc.


    Problems:
        - Allthough we have grouped a lot of code in files and or objects, like data_functions.py,
        plot.py and ui.py, constants.py, utils.py, DateRange.py etc, all the code is not optimally
        grouped togheter. We have not put everything into logical groups as we had some issues
        to iron out, matplot lib is a big library and didnt have the time to learn all the features
        and how to use it properly in a short time.

        - We have not focused too much on performance, nor have we tested the application with
        large datasets. Originally we designed it for performance but we removed some of the
        performance optimizations to make the code more readable and maintainable.

        - We decided, late, to switch to using plot(..) with date_range instead of days_intervals,
        as this avoids some problems, but we have not had the time to perfect this.

        - Matplotlib is a big library and we have not had time to learn all the features
        and best practices when it comes to plotting data with correct labels and ticks (in
        this case month-ticks and days-ticks etc


    Coding:
        - One keypoint to take away is that we use location-objects to store fixed- and
        user-selected point data. Each location has historical_data, data_view and measurement_value
        fields to facilitate for code reuse (read below)

        - another is that location-object historical_data and data_view are dictionaries with keys
        for NOX and APD data,and we can easily add more data types in the future without changing code
        in plotting functions. Our plotting functions have a data_key parameter to select which data to
        plot or process.

        - these two combined allows us to easily extend the application with more data types and
        locations and we can easily iterate over locations and data types in the plotting functions.
        Our locations can be put into a list and we can easily iterate over them to plot data for
        all locations.

        - constants.py MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED is a variable (default 0.5) to
        filter out values that are too low to be shown in the "Verdibokser" plot.
        We have chosen to set it in the code to 0.5 for simplicity. The feature
        be used for "brukerhistorie" to find areas that should be avoided due to high NOX /
        APD values. A slider or text-input would be useful for this feature to control the value.


    How to use:
        - Enter start and end date in "Data start/Dato slutt" inputs, press enter for change to
        register. Graphs and map plots will automaticly update, output must be examined for
        any error messages as we have chosen not to use popups for error messages.

        - Select "År", "1. Kvartal" etc in "Interval" inputs to use reasonable intervalls for
        data viewing.

        - "Reduksjon", for kontur, heatmap and low-res heatmap,  is a function that is applied
        to data that goes into "Kart Bergen". It is a user-selectable function that reduces
        array of data into single value for get_estimated_value_at_point.

        - For "Kontur", "Verdibokser" and "Heatmap" described below the following information
        should be noted:
            - we have chosen not to render colorbar to reduce GUI clutter

            - "Reduksjon" selects folding function used to reduce array of data into single value
            for getting estimated value for a grid of points for the 2d plots

            - "Kartfunksjon" option switches between NOX / APD view

        - "Kontur", Contour-line plotting of user-selectedable NOX / APD data
            - click "Kontur" on "Plot" inputs, change "Reduksjon" to see changes

        - "Verdibokser"
            - click "Verdibokser" on "Plot" inputs, change "Reduksjon" to see changes

            - low-res heatmap that shows where data_key (NOX/APD etc) exceeds a
            threshold given in constants.py. This can be used to tell where you
            dont want to live/be if u need to avoid high concentrations of NOX/APD/etc

        - "Heatmap", High-res heightmap plotting of user-selectedable NOX / APD data (uses 2d grid sampling)
            - click "Heatmap" on "Plot" inputs, change "Reduksjon" to see changes
"""
from time import strptime

# ---------- imports ----------

from matplotlib.widgets import RadioButtons

# import application specific modules
from defs import *
from plot import plot_app
from ui import init_gui, uihelper
from locations import loc_user, all_locations, loc_nordnes


# ---------- Event handlers ----------

def invalidate_locations_data_lines():
    for loc in all_locations:
        for data_key in loc.data_lines:
            loc.data_lines[data_key] = None
    print("line2d objects invalidated")

def invalidate_graphs():
    # invalidate axis
    ax_nox.clear()
    ax_apd.clear()

    # invalidate line2d objects
    invalidate_locations_data_lines()


def on_click(event) :
    if ax := event.inaxes:
        if ax == ax_city_map:
            print("clicked")

            # update location
            app.user_location.coordinates = (event.xdata, event.ydata)

            # invalidate graphs
            invalidate_graphs()

            # render
            app.render()



#---------- UI construction / helpers ----------

# configure application
app.user_location = loc_user
app.plot_gui_callback = plot_app
app.invalidate_graphs_callback = invalidate_graphs

# initialize gui
init_gui()

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)


# plot and go
app.render()

