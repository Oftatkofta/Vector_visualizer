from openpiv import *
import numpy as np
import tifffile as tiff
import time
from matplotlib import pyplot as plt

t0 = time.time()
inputDirectory = "/Volumes/HDD/Huygens_SYNC/_SYNC/CollectiveMigrationAnalysis/Examplemovies/"
#filenames = ["Starve_serumFree_flow_diection.tif"]
filename = "160126_H2B_T0_1h_3ml_serum_Pos_002_005_Median_3_frames.tif"

def PIVanalyzer(inputDirectory, filename, outputDirectory):
    """

    Args:
        inputDirectory: (str)
        filenames: (list) filenames to analyze and draw
        outputDirectory: (str) Where to place output

    Returns:

    """


    raw = tiff.imread(inputDirectory+filename)
    nframes, frame_width, frame_height = raw.shape
    #outstack is in RGB color so we need an extra 3 dimensions
    outStack = np.zeros((nframes-1, frame_width, frame_height, 3), dtype='uint8')

    for i in xrange(nframes-1):
        t1 = time.time()
        print "Start frame "+str(i)+"..."+filename
        frame = raw[i]
        next_frame = raw[i+1]
        flow = cv2.calcOpticalFlowFarneback(frame, next_frame, None, 0.5, 3, 8, 4, 7, 1.5, 0)
        outStack[i] = draw_hsv(flow)

        print "Finish frame "+str(i)+" in "+str(time.time()-t1)+" s."

        #print outStack.shape
    tiff.imsave(outputDirectory+filename+'_HSV.tif', outStack)

raw = tiff.imread(inputDirectory+filename)
nframes, frame_width, frame_height = raw.shape

frame_a = raw[60].astype('int32')
frame_b = raw[61].astype('int32')

u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a, frame_b, window_size=24, overlap=12, dt=720.0, search_area_size=64, sig2noise_method='peak2peak' )

x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size=24, overlap=12 )

#u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = 1.3 )

#u, v = openpiv.filters.replace_outliers( u, v, method='localmean', kernel_size=2)

u1 = plt.imshow(u)
v1 = plt.imshow(v)


#x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 96.52 )

#openpiv.tools.save(x, y, u, v, 'exp1_001.txt' )