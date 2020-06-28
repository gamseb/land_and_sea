from land_sea_plot_generator import generate_image
from region_counter import region_counter
import sys, os
input_file = sys.argv[1]

if (not input_file) or (not os.path.isfile(input_file)):
    print("You need to specify a file with the input. Exiting the current test run.")
    sys.exit()

generate_image(input_file, 'generated_plot.png')
regions = region_counter('generated_plot.png', 'colorized_plot.png', show_output=True)
print("The number of regions is: " + str(regions))


