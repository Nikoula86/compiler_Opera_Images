import numpy as np
from tifffile import imread, imsave
import glob, os, struct, string, tqdm
from imagej_fun import imagej_metadata_tags, make_lut

def compilePEimages_TL(path, channel_order, luts_name, dT, **kwargs):
    # find all tiff files in the folder
    flist = glob.glob(os.path.join(path,'*.tiff'))
    flist.sort()

    # find out all positions (the first 6 characters, e.g.: r01c01 )
    pos = list(set( [os.path.split(f)[-1][:6] for f in flist] ))
    pos.sort()

    # define well id to convert e.g. r01c01 into A01
    d = dict(enumerate(string.ascii_uppercase, 1))

    wells_list = []
    if 'pos_list' not in kwargs.keys():
        for p in pos:
            wells_list.append( d[int(p[1:3])]+p[4:6] )
    else:
        wells_list = kwargs['pos_list']

    pos_process = []
    for p in pos:
        well = d[int(p[1:3])]+p[4:6]
        if well in wells_list:
            pos_process.append(p)

    pbar = tqdm.tqdm(pos_process)
    for p in pbar:
        well = d[int(p[1:3])]+p[4:6]

        pbar.set_description(p + ' ' + well)
        pbar.update()
        
        outpath = os.path.join(os.path.split(path)[0],'compiled',well)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

            # extract all files from this well
            flist = glob.glob(os.path.join(path,p+'*.tiff'))
            flist.sort()

            # find timepoints
            timepoints = list(set([f[f.index('sk')+2:f.index('fk')] for f in flist]))
            timepoints = np.array([int(t) for t in timepoints])
            timepoints.sort()
            timepoints = timepoints[::dT]

            # for each timepoint
            for timepoint in tqdm.tqdm(timepoints):

                # extract all files from this timepoint
                channels_list = glob.glob(os.path.join(path,p+'*'+'sk'+str(timepoint)+'fk*.tiff'))
                channels_list.sort()

                # find channels
                channels = list(set([f[f.index('-ch')+3:f.index('-ch')+4] for f in channels_list]))
                channels = np.array([int(ch) for ch in channels])
                channels.sort()

                stacks = []
                # for each channel
                for channel in channels:
                    # extract all files from this channel
                    stack_list = glob.glob(os.path.join(path,p+'*-ch'+str(channel)+'*sk'+str(timepoint)+'fk*.tiff'))
                    stack_list.sort()

                    stack = []
                    # create 3D stack
                    for f in stack_list:
                        stack.append(imread(f))
                    stack = np.array(stack)
                    # if just 2D, drop a dimension
                    if stack.shape[0]==1:
                        stack = stack[0]

                    # append the channel stack to the multichannel array
                    stacks.append(stack)

                stacks = np.array(stacks).astype(np.uint16)

                # order channels according to input
                stacks = np.array([stacks[ch] for ch in channel_order]).astype(np.uint16)

                if stacks.ndim==4:
                    stacks = np.swapaxes(stacks,0,1)
                
                # create imagej metadata with LUTs
                luts_dict = make_lut()
                ijtags = imagej_metadata_tags({'LUTs': [luts_dict[i] for i in luts_name]}, '>')

                # create filename
                outname = well+'_tp%05d.tif'%(timepoint-1)

                # save array
                imsave(os.path.join(outpath,outname),stacks, byteorder='>', imagej=True,
                                metadata={'mode': 'composite'}, extratags=ijtags)

###############################################################################

if __name__=='__main__':
    paths = [   
                os.path.join(
                    'Y:',os.sep,'Germaine_Aalderink','raw_data',
                    '2020-07-21_GA_Bra2i_150-250cells_120h_I__2020-07-21T16_43_22-Measurement 1',
                    'Images'
                    ),
            ]

    # this is to, for instance, arrange BF in first channel and GFP in second channel
    # available LUTS: gray, red, green, blue, magenta, cyan, yellow
    channel_order = [1,0]
    luts_name = ['gray', 'green']

    # use >1 to comile fewer images (e.g. for testing)
    dT = 1

    for path in tqdm.tqdm(paths):
        compilePEimages_TL(path, channel_order, luts_name, dT)
