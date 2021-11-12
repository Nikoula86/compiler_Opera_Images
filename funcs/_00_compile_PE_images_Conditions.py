import numpy as np
from skimage.io import imread, imsave
import glob, os, struct, string, tqdm
from tqdm.utils import _term_move_up
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox
from imagej_fun import imagej_metadata_tags, make_lut

###############################################################################


def compilePEimages_condition(path, conditions, channel_order, luts_name):
    # find all tiff files in the folder
    flist = glob.glob(os.path.join(path,'*.tiff'))
    flist.sort()

    # find out all positions (the first 6 characters, e.g.: r01c01 )
    pos = list(set( [os.path.split(f)[-1][:6] for f in flist] ))
    pos.sort()

    # define well id to convert e.g. r01c01 into A01
    d = dict(enumerate(string.ascii_uppercase, 1))

    pbar = tqdm.tqdm(pos)
    for p in pbar:
        well = p[4:6]+d[int(p[1:3])]
        cond = conditions[int(p[4:6])-1][int(p[1:3])-1]

        pbar.set_description(p + ' ' + well + ' ' + cond)
        pbar.update()
        
        outpath = os.path.join(os.path.split(path)[0],'compiled',cond)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        # extract all files from this well
        flist = glob.glob(os.path.join(path,p+'*.tiff'))
        flist.sort()

        # extract all files from this timepoint
        channels_list = glob.glob(os.path.join(path,p+'*'+'sk*fk*.tiff'))
        channels_list.sort()

        # find channels
        channels = list(set([f[f.index('-ch')+3:f.index('-ch')+4] for f in channels_list]))
        channels = np.array([int(ch) for ch in channels])
        channels.sort()

        stacks = []
        for channel in channels:
            # extract all files from this channel
            stack_list = glob.glob(os.path.join(path,p+'*-ch'+str(channel)+'*sk*fk*.tiff'))
            stack_list.sort()

            stack = []
            for f in stack_list:
                stack.append(imread(f))
            stack = np.array(stack)
            if stack.shape[0]==1:
                stack = stack[0]
            stacks.append(stack)

        stacks = np.array(stacks).astype(np.uint16)

        # order channels
        stacks = np.array([stacks[ch] for ch in channel_order]).astype(np.uint16)
        if stacks.ndim == 4:
            stacks = np.moveaxis(stacks,1,0)
        # print(stacks.shape)

        # create imagej metadata with LUTs
        luts_dict = make_lut()
        ijtags = imagej_metadata_tags({'LUTs': [luts_dict[i] for i in luts_name]}, '>')

        outname = well+'.tif'
        imsave(os.path.join(outpath,outname),stacks, byteorder='>', imagej=True,
                        metadata={'mode': 'composite'}, extratags=ijtags)

##########################################################################################

if __name__=='__main__':
    path = os.path.join(
                    'Y:',os.sep,'Nicola_Gritti','raw_data',
                    '20200922_gastr_h2bmCh_GPIGFP',
                    '20200925_NG_h2bmCherry_GPIGFP_096hpa_2D',
                    'Images'
                    )

    # conditions should be arranged by column, for every one of thew 12 columns, give the condition name
    conditions = [
        'gastr_150cells',
        'gastr_150cells',
        'gastr_150cells',
        'gastr_150cells',
        'gastr_300cells',
        'gastr_300cells',
        'gastr_300cells',
        'gastr_300cells',
        'gastr_450cells',
        'gastr_450cells',
        'gastr_450cells',
        'gastr_450cells'
        ]

    # this is to, for instance, arrange BF in first channel and GFP in second channel
    # available LUTS: gray, red, green, blue, magenta, cyan, yellow
    channel_order = [1,0,2]
    luts_name = ['gray', 'green','red']

