# empty class object to allow us to set custom attributes
class EmptyClass:
    pass


# get a successive random seeds starting at 1
def get_next_rand_seed():
    if not hasattr(get_next_rand_seed, "counter"):
        get_next_rand_seed.counter = 0  # Static variable

    # Increment the static variable
    get_next_rand_seed.counter += 1
    return get_next_rand_seed.counter


# function to hide axis graphics, choose to hide ticks and/or spines
def hide_axis_graphics(ax, hide_ticks=True, hide_spines=True):
    if hide_ticks:
        ax.set_xticks([])
        ax.set_yticks([])

    if hide_spines:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)


"""
# function to map a value from one range to another
def map_to_range(value, min_in, max_in, min_out, max_out):
    if max_in == min_in:
        raise ValueError("min_in and max_in cannot be the same value")

    return min_out + (value - min_in) * (max_out - min_out) / (max_in - min_in)
"""