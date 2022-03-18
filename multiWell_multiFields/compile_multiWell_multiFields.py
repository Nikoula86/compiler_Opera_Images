'''
This script combines images of a multiwell plate acquired by PE.
Inputs:
- paths: a list of strings containing the path to the experiment folder. Has to point to the "Images" folder
- channels_orders: a list, same length of paths. Each element contains the order in which the channels have to be arranged in the output images.
            E.g. if PE acquires GFP first and BF next, and you want BF-GFP, then the order is [1,0]
- luts_names: list of colors to be used to show the channels

Output:
- a "compiled" folder, containing the conditions subfolders, containing 1 multichannel tif file for every well in the experiment

NOTE:
This script assume the experiment contains just one FOV per well! And one focal plane! E.g. everything 2D
'''

import glob, os, struct, string, tqdm
from skimage.io import imread
import sys, time
sys.path.append(os.path.join('..','funcs'))
from _00_compile_PE_images import compilePEimages_multiWell_multiFields
from xml2csv import xml2csv
import pandas as pd

##########################################################################################

paths = [
            os.path.join(
                'Y:', os.sep, 'Joana Silva',
                '2022-03-16_joana_micromass_P4 test__2022-03-16T15_15_05-Measurement 1',
                'Images'
                ),
        ]

# this is to, for instance, arrange BF in first channel and GFP in second channel
# available LUTS: gray, red, green, blue, magenta, cyan, yellow
channel_orders = [
                    [2,1,3],
                ]
luts_names = [ 
                ['gray', 'cyan', 'green'],
            ]

# define the flat field files
ff_folder = os.path.join(
    'Y:', os.sep, 'Joana Silva',
    '2022-03-18_joana_FFtest'
    )
ff_files = [None,None,None]
            # os.path.join(ff_folder, 'DAPI.tif'),
            # os.path.join(ff_folder, 'GFP.tif')]
##############################################################################

ffs = []
for ff_file in ff_files:
    if ff_file!=None:
        ff = imread(ff_file)
    else:
        ff = 1.
    ffs.append(ff)

for i in range(len(paths)):
    path = paths[i]
    print(path)
    channel_order = channel_orders[i]
    luts_name = luts_names[i]
    time.sleep(1)

    # metadata = xml2csv(path, save=True)
    metadata = pd.read_csv(os.path.join(os.path.split(path)[0],'metadata.csv'))

    compilePEimages_multiWell_multiFields(path, 
                                          channel_order, 
                                          luts_name, 
                                          metadata,
                                          ffs)
    
    
    
    
    
    
    
