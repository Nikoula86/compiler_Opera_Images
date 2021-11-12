'''
This script combines images of a 96WP acquired by PE.
Inputs:
- paths: a list of strings containing the path t the experiment folder. Has to point to the "Images" folder
- channels_orders: a list, same length of paths. Each element contains the order in which the channels have to be arranged in the output images.
            E.g. if PE acquires GFP first and BF next, and you want BF-GFP, then the order is [1,0]
- luts_names: list of colors to be used to show the channels
- conditions_all: for every plate and well, it should contain the conditions (control, ...)

Output:
- a "compiled" folder, containing the conditions subfolders, containing 1 multichannel tif file for every well in the experiment

NOTE:
This script assume the experiment contains just one FOV per well! And one focal plane! E.g. everything 2D
'''

import numpy as np
from skimage.io import imread, imsave
import glob, os, struct, string, tqdm
from tqdm.utils import _term_move_up
import sys, time
sys.path.append(os.path.join('funcs'))
from _00_compile_PE_images_Conditions import compilePEimages_condition

##########################################################################################

paths = [
            os.path.join(
                '2021-07-21_BraGFP_150-300-450-cells_inhibSB43_120h',
                'Images'
                ),
        ]

# this is to, for instance, arrange BF in first channel and GFP in second channel
# available LUTS: gray, red, green, blue, magenta, cyan, yellow
channel_orders = [
                    [1,0],
                ]
luts_names = [ 
                ['gray', 'green'],
            ]

# build the conditions map for every well
c1 = [
        ['init_150cells_inhib_48-72' for i in range(4)]+['init_150cells_inhib_72-96' for i in range(4)],
        ['init_150cells_inhib_48-72' for i in range(4)]+['init_150cells_inhib_72-96' for i in range(4)],
        ['init_150cells_inhib_48-72' for i in range(4)]+['init_150cells_inhib_72-96' for i in range(4)],
        ['init_150cells_inhib_48-72' for i in range(4)]+['init_150cells_inhib_72-96' for i in range(4)],
        ['init_300cells_inhib_48-72' for i in range(4)]+['init_300cells_inhib_72-96' for i in range(4)],
        ['init_300cells_inhib_48-72' for i in range(4)]+['init_300cells_inhib_72-96' for i in range(4)],
        ['init_300cells_inhib_48-72' for i in range(4)]+['init_300cells_inhib_72-96' for i in range(4)],
        ['init_300cells_inhib_48-72' for i in range(4)]+['init_300cells_inhib_72-96' for i in range(4)],
        ['init_450cells_inhib_48-72' for i in range(4)]+['init_450cells_inhib_72-96' for i in range(4)],
        ['init_450cells_inhib_48-72' for i in range(4)]+['init_450cells_inhib_72-96' for i in range(4)],
        ['init_450cells_inhib_48-72' for i in range(4)]+['init_450cells_inhib_72-96' for i in range(4)],
        ['init_450cells_inhib_48-72' for i in range(4)]+['init_450cells_inhib_72-96' for i in range(4)],
    ]

conditions_all = [
        # c1,
        c1,
    ]

for i in range(len(paths)):
    path = paths[i]
    print(path)
    channel_order = channel_orders[i]
    luts_name = luts_names[i]
    conditions = conditions_all[i]
    
    time.sleep(1)

    compilePEimages_condition(path, conditions, channel_order, luts_name)
