import cv2
import numpy as np
import tifffile as tiff
import time
from openpiv import *
import matplotlib.pyplot as plt

t0 = time.time()

inDirectory = "/Volumes/HDD/Huygens_SYNC/CollectiveMigrationAnalysis/Examplemovies/"
outDirectory = "/Volumes/HDD/Huygens_SYNC/CollectiveMigrationAnalysis/Examplemovies/test/"

filenames = ["160112_H2B_noStarve_Pos_000_005_Median_3_frames.tif",
             "160115_H2B_Starve_serumFree_T0_10min_Pos_003_003_Median_3_frames.tif",
             "160126_H2B_T0_1h_3ml_serum_Pos_002_005_Median_3_frames.tif"]

filenames = ["160126_H2B_T0_1h_3ml_serum_Pos_002_005_Median_3_frames.tif"]

def getHistorgam(array, nBins, minval, maxval):

    counts, bins = np.histogram(array, nBins, (minval, maxval))

    return counts, bins

for filename in filenames:

    raw = tiff.imread(inDirectory + filename)
    nframes, frame_width, frame_height = raw.shape
    ncols, nrows = 15, 15
    scale = 15
    velocityStack = np.zeros((nframes-1, frame_width, frame_height),
                             dtype='float')
    directionStack = np.zeros((nframes - 1, frame_width, frame_height),
                             dtype='float')



    for i in xrange(nframes-1):
        t1 = time.time()
        print "Start frame "+str(i)+"..."+filename
        frame = raw[i]
        next_frame = raw[i+1]
        flow = cv2.calcOpticalFlowFarneback(frame, next_frame, None, 0.5, 3, 9, 3, 5, 1.2, 0)
        Uframe = flow[...,0]
        Vframe = flow[...,1]

        velocityStack[i] = np.sqrt((np.add(np.square(Uframe), np.square(Vframe))))
        directionStack[i] = np.arcsin(np.divide(Vframe,velocityStack[i]))
        velocityHistCounts, velocityHistBins = np.histogram(velocityStack[i],
                                                            bins=100,
                                                            range=(0, 10),
                                                            normed=True)

        vhist = np.column_stack((velocityHistBins, velocityHistCounts))
        #np.savetxt(outDirectory+filename+str(i)+"vhist.csv", velocityHistCounts,"%.3e",',')

        if i == 0:
            np.savetxt(outDirectory + filename + str(i) + "vhist.csv", velocityHistBins,
                       "%.3e", ',')

        plt.plot(velocityHistCounts, color='black')
        plt.ylim((0,1))
        plt.savefig(outDirectory + filename[:-10] + str(i) + "_vhist.png")
        plt.close()
        print "Finish frame "+str(i)+" in "+str(time.time()-t1)+" s."

    #print outStack.shape
    #tiff.imsave(outDirectory+filename+'_velocity.tif', velocityStack)
    #tiff.imsave(outDirectory + filename + '_direction.tif', directionStack)

print "All done in "+str(time.time()-t0)+" s"
