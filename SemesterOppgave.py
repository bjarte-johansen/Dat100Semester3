"""
NOTE:
    - We have moved some code to other files to make the code more readable and maintainable

TODO:
    - Count every year as being 365 days to avoid problems with leap years?
      This is mainly to avoid datehandling so amount of work for teacher is kept to a minimum
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
        if ax == axCityMap:
            loc_user.coordinates = (event.xdata, event.ydata)
            plot_app()


#---------- UI construction ----------

def plot_gui_callback():
    plot_app()

app.plot_gui_callback = plot_gui_callback()



# ---------- Declare text helpers ----------------

from ui import init_gui, uihelper

init_gui()

print(uihelper.text_input_list)
print(uihelper.text_input_map)


# update date range for text inputs from app
uihelper.text_input_map['start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
uihelper.text_input_map['end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))


# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

# plot and go
plot_app()

plt.show()