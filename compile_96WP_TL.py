'''
This script combines images of a 96WP acquired by PE.
Inputs:
- paths: a list of strings containing the path t the experiment folder. Has to point to the "Images" folder
- channels_orders: a list, same length of paths. Each element contains the order in which the channels have to be arranged in the output images.
            E.g. if PE acquires GFP first and BF next, and you want BF-GFP, then the order is [1,0]
- luts_names: list of colors to be used to show the channels
- remove_list: for every experiment, remove selected wells (e.g. if sample is lost)
- dT: integer, can be used to downsample in time the dataset.

Output:
- a "compiled" folder, containing the a subfolder for every well, containing 1 multichannel tif file for every timepoint

NOTE:
This script assume the experiment contains just one FOV per well! And one focal plane! E.g. everything 2D
'''import numpy as np
from tifffile import imread, imsave
import glob, os, struct, string, tqdm
from tqdm.utils import _term_move_up
import sys
sys.path.append(os.path.join('funcs'))
from _00_compile_PE_images_TL import compilePEimages_TL

##########################################################################################
paths = [   
            os.path.join(
                '2021-02-09_braGFP_2i_96-120hpa_TL',
                'Images'
                ),
        ]

# this is to, for instance, arrange BF in first channel and GFP in second channel
# available LUTS: gray, red, green, blue, magenta, cyan, yellow
channel_orders = [ 
        [1,0] 
    ]
luts_names = [ 
        ['gray', 'green'] 
    ]

# use >1 to comile fewer images (e.g. for testing)
dT = 1

# select only certain wells:
remove_list = []

pos_list = [
        [l+'%02d'%i for i in range(1,13) for l in string.ascii_uppercase[:8] 
    ]
i=0
for rm in remove_list:
    for remove in rm:
        pos_list[i].remove(remove)
    i+=1
print(pos_list)


for i in range(len(paths)):
    path = paths[i]
    channel_order = channel_orders[i]
    luts_name = luts_names[i]

    compilePEimages_TL(path, channel_order, luts_name, dT, pos_list=pos_list[0])
