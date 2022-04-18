from itertools import cycle
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import tifffile
from tqdm.notebook import tqdm, trange

channel_names = ["ATF6", "BetaTubulin", "ConcanavalinA", "DAPI", "GOLPH4", "HSP60", "Nucleolin", "Phalloidin", "Sortilin", "TOM20", "WGA"]

def read_tiff_files(sub_data_path, channel_names=channel_names):
    total_files = []
    for chan in channel_names:
        tif_files_temp = [name for name in sorted(glob.glob(os.path.join(f"{sub_data_path}", "*.tif"))) if name.find(chan) != -1][0]
        if len(tif_files_temp) > 0:
            total_files.append(tif_files_temp)
    return(tifffile.imread(total_files))


    
def display_list_image(image_list, name_images=None, figsize=(32, 16), height_ratios=[5,1], tight_layout=True, cmap=None, save_path=None, vmin=None, vmax=None, is_colorbar=True):
    """
    Display a list of images (gray or rgb) with their histograms
    
    Parameters
    -------
        image_list : list of np.ndarray(dtype=np.uint8)
            Input grayscale image list or 3 channel RGB image list
            
        name_images : list of str (default=None)
            List of the titles to display (must be same lenght as the image_list)
        
        figsize : tuple (default=(12, 16))
            Size of the figure
        
        height_ratios : list (Default=[5, 1])
            Ratio of the image and histogram heights
        
        tight_layout : bool (default=True)
            Tight_layout of plt.imshow
        
        cmap : str (default='gray')
            Color map
            
        save_path : str (default=None)
            If not None, will save the images at the save_path path
            
        vmin : int or float (default=None)
            Minimal value of the colormap
        
        vmax : int or float (default=None)
            Maximal value of the colormap
        
        is_colorbar : bool (default=True)
            If True, display the colorbar
        
    Returns:
    
    """
    is_cmap = True
    if cmap is None:
        cmap = ['gray']
        is_cmap = False
    fig, axs = plt.subplots(2, len(image_list), figsize=figsize, tight_layout=tight_layout, gridspec_kw={'height_ratios':height_ratios})
    for i in trange(len(image_list)):
        if is_cmap is False:
            cmap.append('gray')

        if vmin is not None or vmax is not None:
            pos = axs[0, i].imshow(image_list[i].copy(), cmap=cmap[i], vmax=vmax, vmin=vmin)
        else:
            pos = axs[0, i].imshow(image_list[i].copy(), cmap=cmap[i])
        if is_colorbar and image_list[i].ndim == 2:
            cbar = fig.colorbar(pos, ax=axs[0, i],  extend="both", orientation="horizontal")
            cbar.minorticks_on()
        
        if name_images is not None:
            axs[0, i].set_title(name_images[i])
        axs[1, i].hist(image_list[i].copy().ravel(), 255)         
    if save_path is not None:
        plt.savefig(save_path)
    plt.show()
    

    

    