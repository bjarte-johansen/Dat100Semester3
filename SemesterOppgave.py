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
from plot import plot_map, plot_graphs



#---------- Helper functions ----------

def set_data_processing_func_from_str(str_func):
    # update processing func
    app.set_data_processing_func(str_func)

    # plot graph
    plot_app()

def set_days_interval_from_str(str_period):
    # update date range
    tmp = string_to_date_interval_map[str_period]
    app.set_date_range(tmp['start_date'], tmp['end_date'])

    # reset user-selected point
    loc_user.coordinates = None

    text_input_map['text_input_start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
    text_input_map['text_input_end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))

    # plot graph
    plot_app()

def on_click(event) :
    if ax := event.inaxes:
        if ax == axCityMap:
            loc_user.coordinates = (event.xdata, event.ydata)
            plot_app()


# date range text inputs
text_inputs = []
text_input_map = {}


def plot_app():
    global text_inputs

    # plot NOX graphs
    plot_graphs(axGraph, KEY_NOX)

    # plot map (change key to plot APD or NOX)
    plot_map(KEY_NOX)

    # draw the plot
    plt.draw()

# ---------- Radio button groups ----------

# we have hardcoded values because we dont consider this to be very important
# in the case of radiobuttons

def create_radio_button_panel(ax, list_options, on_clicked):
    num_options = len(list_options)
    list_fonts = [10] * num_options
    list_colors = ['#333333'] * num_options
    button_face_colors = ['#000000'] * num_options  # White face color for the radio buttons
    button_edge_colors = ['#000000'] * num_options  # Black edge color for better visibility
    radio_button = RadioButtons(
        ax,
        list_options,
        label_props = {'color': list_colors, 'fontsize' : list_fonts},
        radio_props={'facecolor': button_face_colors, 'edgecolor': button_edge_colors}
        )
    radio_button.on_clicked(on_clicked)
    return radio_button
# END create_radio_button_panel

def create_radio_button_panel_for_processing_func():
    ax = plt.axes([0.4, 0.6, 0.1, 0.2], facecolor=UI.RadioGroup.bg_color)  # First radio button group
    ax.set_zorder(10)

    radio_button = create_radio_button_panel(
        ax,
        list(string_to_data_process_func_map.keys()),
        set_data_processing_func_from_str
        )
    plt.draw()
    return radio_button

def create_radio_button_panel_for_interval():
    ax = plt.axes([0.4, 0.375, 0.1, 0.2], facecolor=UI.RadioGroup.bg_color)  # Second radio button group

    radio_button = create_radio_button_panel(
        ax,
        list(string_to_date_interval_map.keys()),
        set_days_interval_from_str
        )
    plt.draw()
    return radio_button

radio_buttons = [
    create_radio_button_panel_for_processing_func(),
    create_radio_button_panel_for_interval()
]

def validate_date_input(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def create_date_text_inputs(ax):
    # returns the bounding box of a text object in data coordinates
    def get_bounding_box(text_obj):
        renderer = fig.canvas.get_renderer()
        bbox = text_obj.get_window_extent(renderer=renderer)  # Get in display (pixel) coordinates
        bbox_data = bbox.transformed(ax.transData.inverted())  # Convert to data coordinates
        return bbox_data

    text_input_helpers = [
        SimpleNamespace(
            text='2024-02-01',
            bounds=None,
            title="Dato start: ",
        ),
        SimpleNamespace(
            text='2024-04-01',
            bounds=None,
            title="Dato slutt: ",
        )
    ]

    # Display initial text
    text_inputs = [
        ax.text(0.0125, 0.85, text_input_helpers[0].title + text_input_helpers[0].text, horizontalalignment='left', verticalalignment='center', fontsize=12),
        ax.text(0.0125, 0.7, text_input_helpers[1].title + text_input_helpers[1].text, horizontalalignment='left', verticalalignment='center', fontsize=12)
        ]
    text_input_map = {
        'text_input_start_date': text_inputs[0],
        'text_input_end_date': text_inputs[1],
    }

    text_input_helpers[0].bounds = get_bounding_box(text_inputs[0])
    text_input_helpers[1].bounds = get_bounding_box(text_inputs[1])

    text_input_current = {
        'index': 0,
        'obj': text_inputs[0]
    }

    def on_click(event):
        print("log: clicked at ", event.xdata, event.ydata)

        text_input_current['index'] = -1
        text_input_current['obj'] = None

        for i in range(len(text_input_helpers)):
            # exit if no xdata or ydata
            if event.xdata is None or event.ydata is None:
                continue

            if text_inputs[i] is None:
                continue

            # get bounds and test
            bounds = text_input_helpers[i].bounds #(text_input_current['obj'])
            if bounds.contains(event.xdata, event.ydata):
                text_input_current['index'] = i
                text_input_current['obj'] = text_inputs[i]

                print("log: clicked on text input ", text_input_current['index'])
        pass

    def update_date_range(start, end):
        app.set_date_range(start, end)
        plot_app()

    def on_submit(input_index, text):
        new_date = datetime.strptime(text, '%Y-%m-%d')

        if input_index == 0:
            update_date_range(new_date, app.date_range.end_date)
        elif input_index == 1:
            update_date_range(app.date_range.start_date, new_date)

    def on_key(event):
        o = text_input_current['obj']
        i = text_input_current['index']
        input_helper = text_input_helpers[i]

        if i < 0 or i >= len(text_inputs):
            print("invalid text input index")
            return

        if event.key == 'backspace':
            input_helper.text = input_helper.text[:-1]
            o.set_text(input_helper.title + input_helper.text)
        elif event.key == 'enter':
            text = input_helper.text
            on_submit(i, text)
            return
        else:
            input_helper.text += event.key
            o.set_text(input_helper.title + input_helper.text)

        print(input_helper.text)
        plt.draw()

    # Connect the keyboard event to handle input
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('key_press_event', on_key)

    return text_inputs, text_input_map


text_inputs, text_input_map = create_date_text_inputs(axInputPane)

text_input_map['text_input_start_date'].set_text("Dato start: " + app.date_range.start_date.strftime('%Y-%m-%d'))
text_input_map['text_input_end_date'].set_text("Dato slutt: " + app.date_range.end_date.strftime('%Y-%m-%d'))


# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

# plot and go
plot_app()

plt.show()