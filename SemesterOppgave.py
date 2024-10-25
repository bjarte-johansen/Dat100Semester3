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

        #TODO: Dont know if this will be in our final project, but we include the comment
            "We have also added a new get_estimated_value_at_point_ext function that uses a
            different weighting function."

    Problems:
        - We have not focused highly performance, nor have we tested the application with
        large datasets. Originally we designer itfor performance but we
        removed some of the performance optimizations to make the code more readable and
        maintainable.

        - Our views are not optimized for showing all ranges of days/months
        intervals, as we have focused on other areas of the code base. Matplotlib is a
        big library and we have not had time to learn all the features and best practices
        when it comes to plotting data with correct labels and ticks etc. We thought about
        padding the data on start and end to fit any dayrange into a whole or several whole
        months, but decided not to and went for drawing days if the range is less than roughly
        65 days (subject to change)

    Coding:
        - One keypoint to take away is that we use location-objects to store fixed- and
        user-selected point data. Each location has historical_data, data_view
        and measurement_value fields to facilitate for code reuse (read below)

        - another is that location-object historical_data and data_view are dictionaries with keys
        for NOX and APD data,and we can easily add more data types in the future without changing code
        in plotting functions. Our plotting functions have a data_key parameter to select which data to
        plot or process.

        - these two combined allows us to easily extend the application with more data types and
        locations and we can easily iterate over locations and data types in the plotting functions.
        Our locations can be put into a list and we can easily iterate over them to plot data for
        all locations.

    Functionality:
        - MINIMUM_VALUE_FOR_HEIGHTMAP_BOXED is a variable (default 0.5) to filter out
        values that are too low to be shown in the "Verdibokser" plot. This can be used for
        "brukerhistorie" to find areas that should be avoided due to high NOX / APD values.
        A slider or text-input would be useful for this feature to control the value. We
        have chosen to set it in the code to 0.5 for simplicity.

        - Enter start and end date in "Data start/Dato slutt" inputs, press enter for change to
        register. Graphs and map plots will automaticly update, output must be examined for
        any error messages as we have chosen not to use popups for error messages.

        - Select "År", "1. Kvartal" etc in "Interval" inputs to use reasonable intervalls for
        data viewing.

        - We have contour-line plotting of user-selectedable NOX / APD data (uses 2d grid sampling)
            - user selectable folding function to reduce array of data into single value for get_estimated_value_at_point
            - click "Kontur" on "Plot" inputs, change "Funksjon" to see changes
            - we have chosen not to render colorbar to reduce GUI clutter

        - We have low-res heightmap plotting of user-selectedable NOX / APD data (uses 2d grid sampling)
            - user selectable folding function to reduce array of data into single value for get_estimated_value_at_point
            - click "Verdibokser" on "Plot" inputs, change "Funksjon" to see changes
            - we have chosen not to render colorbar to reduce GUI clutter

        - Our "Kartfunksjon", switchable NOX / APD view is accessible via "Kartfunksjon" inputs
"""
from time import strptime

# ---------- imports ----------

from matplotlib.widgets import RadioButtons

# import application specific modules
from defs import *
from plot import plot_app



# ---------- Event handlers ----------

def on_click(event) :
    if ax := event.inaxes:
        if ax == ax_city_map:
            loc_user.coordinates = (event.xdata, event.ydata)

            app.invalidate_graph_axis()

            app.render()



#---------- UI construction / helpers ----------

def invalidate_locations_data_lines():
    for loc in all_locations:
        for data_key in loc.data_lines:
            loc.data_lines[data_key] = None
            print("cleared data lines for", loc.name, data_key, loc.data_lines)

    print(all_locations[0].data_lines)

app.plot_gui_callback = plot_app
app.on_date_range_change = invalidate_locations_data_lines



# ---------- Declare text helpers ----------------

from ui import init_gui, uihelper

init_gui()

#print('uihelper.text_input_map', uihelper.text_input_map)

# update date range for text inputs from app
uihelper.text_input_map['start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
uihelper.text_input_map['end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

# plot and go
app.render()

plt.show()