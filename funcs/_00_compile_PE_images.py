import numpy as np
from skimage.io import imread, imsave
import glob, os, struct, string, tqdm
import pandas as pd
from tqdm.utils import _term_move_up
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox
from imagej_fun import imagej_metadata_tags, make_lut, make_lut_old

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

def compilePEimages_multiWell_multiFields(path, 
                                          channel_order, 
                                          luts_name, 
                                          df,
                                          ffs):
    
    ffs = [ff/np.mean(ff) for ff in ffs]

    # find out all wells
    wells = df.groupby(['row','col']).size().reset_index()

    # define well id to convert e.g. r01c01 into A01
    d = dict(enumerate(string.ascii_uppercase, 1))

    pbar = tqdm.tqdm(wells.iterrows())
    for i, p in pbar:
        r = int(p.row)
        c = int(p.col)
        well = d[r]+'%02d'%c
        
        conversion = pd.DataFrame({})

        pbar.set_description(well)
        pbar.update()
        
        outpath = os.path.join(os.path.split(path)[0], 'compiled', well)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
            
        df_well = df[(df.row==r)&(df.col==c)]
        
        # find all fields inside this well
        fields = df_well.groupby(['Ypos','Xpos']).size().reset_index()
        fields = fields.sort_values(by=['Ypos','Xpos'])
        l = list(set(fields.Ypos))
        l.sort()
        fields['Yidx'] = [l.index(v) for v in fields.Ypos]
        l = list(set(fields.Xpos))
        l.sort()
        fields['Xidx'] = [l.index(v) for v in fields.Xpos]
        
        for j, f in tqdm.tqdm(fields.iterrows(), total = len(fields)):
            x = f.Xpos
            y = f.Ypos
            xidx = f.Xidx
            yidx = f.Yidx
            
            df_pos = df_well[(df_well.Xpos==x)&(df_well.Ypos==y)]

            # print('Images foudn')
            stack = []
            for k, ch in enumerate(channel_order):
                df_pos_ch = df_pos[df_pos.channel==ch]
                df_pos_ch = df_pos_ch.sort_values(by='Zpos')
                # [print(img_file) for img_file in df_pos_ch.filename]
                # print([os.path.join(folder_raw,exp_folder,'Images',img_file) for img_file in df_pos_ch.filename])
                stack_ch = np.stack([imread(os.path.join(path,img_file))/ffs[k] for img_file in df_pos_ch.filename])
                stack.append(stack_ch)

            # order channels
            stacks = np.array(stack).astype(np.uint16)
            stacks = np.swapaxes(stacks, 0, 1)

            # create imagej metadata with LUTs
            # luts_dict = make_lut(luts_name)
            luts_dict = make_lut_old()
            ijtags = imagej_metadata_tags({'LUTs': [luts_dict[lut_name] for lut_name in luts_name]}, '>')
            
            outname = 'field%03d.tif'%j

            raw = pd.DataFrame({'tile_idx':[j],
                                'filename':[outname],
                                'row_idx':[yidx],
                                'col_idx':[xidx]})
            conversion = pd.concat([conversion,raw], ignore_index=True)

            # print(outname)
            imsave(os.path.join(outpath,outname),stacks, byteorder='>', imagej=True,
                            metadata={'mode': 'composite'}, extratags=ijtags, check_contrast=False)
            
        conversion.to_csv(os.path.join(outpath, 'metadata.csv'))
            


##########################################################################################

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

