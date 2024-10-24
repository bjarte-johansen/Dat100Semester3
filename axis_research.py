"""
class AxisRectangle:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x * width
        self.y = height - y * height
        self.width = width
        self.height = height

    def min_x(self):
        return self.x
    def max_x(self):
        return self.x + self.width
    def min_y(self):
        return self.y
    def max_y(self):
        return self.y + self.height

    def to_array(self):
        return [self.min_x(), self.min_y(), self.max_x(), self.max_y()]
"""
# Get figure size in pixels
"""
def get_axis_bounding_box(axis):
    # Get figure size in pixels and inches
    fig_size_inch = fig.get_size_inches()
    fig_size_pixels = fig.get_size_inches() * fig.dpi
    print("fig_size_inch: ", fig_size_inch, ", fig_size_pixels: ", fig_size_pixels)

    # get axis extents, transform figure-relative coordinates (normalized)
    bbox = axis.get_window_extent()
    bb = bbox.transformed(fig.dpi_scale_trans.inverted())

    bb_norm = [
        bb.x0 / fig_size_inch[0],
        bb.y0 / fig_size_inch[1],
        bb.width / fig_size_inch[0],
        bb.height / fig_size_inch[1]
    ]

    bb_pixel = [
        bb_norm[0]  * fig_size_pixels[0],
        (1 - bb_norm[1]) * fig_size_pixels[1],
        bb_norm[2] * fig_size_pixels[0],
        bb_norm[3] * fig_size_pixels[1],
    ]

    print("bb_norm", *bb_norm)
    print("bb_pixel", *bb_pixel)
# END get_axis_bounding_box
"""
"""
axInputPane = fig.add_axes((0.05, 0.725, 0.9, 0.015))
axInputPane.set_facecolor('red')
hide_axis_graphics(axInputPane)
"""