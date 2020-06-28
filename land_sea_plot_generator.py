# This could have been a class, but I have decided against it for the sake of simplicity
def generate_image(input_file, output_file, show_output=False):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle

    def read_input_file(filename):
        """
        :param filename: filename location
        :return: nested list with a list of 4 positional values from the input file
        """
        with open(filename, 'r') as file:
            lines = file.readlines()
            # Reads the lines, strips whitespace, splits them into lists,
            # converts the values to floats and put them all into a list, then returns them
            # EXPECTS A CLEAN INPUT
            return [map(float, line.strip().split(" ")) for line in lines[1:]]

    def plot_rectangle(a1, a2, b1, b2):
        """
        Plots a rectangle by knowing two points
        :param a1: Left bottom point - x
        :param a2: Left bottom point - y
        :param b1: Right top point - x
        :param b2: Right top point - y
        :return:
        """
        assert b1 > a1 and b2 > a2
        b1, b2 = b1 - a1, b2 - a2
        currentAxis.add_patch(Rectangle((a1, a2), b1, b2, fill=None, alpha=1))

    currentAxis = plt.gca()
    currentAxis.set_xlim([0, 15])
    currentAxis.set_ylim([0, 15])
    plt.axis('off')

    # Read the input from the file
    rectangle_list = read_input_file(input_file)
    # Plot rectangles
    for rectangle in rectangle_list:
        a1, a2, b1, b2 = rectangle
        plot_rectangle(a1, a2, b1, b2)

    plt.savefig(output_file)
    if show_output:
        plt.show()