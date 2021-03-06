import cv2
import numpy as np
import tifffile as tiff
import time
from histogramGenerator import *

t0 = time.time()
inDirectory = "/Volumes/HDD/Huygens_SYNC/_SYNC/CollectiveMigrationAnalysis/Examplemovies/"
outDirectory = "/Volumes/HDD/Huygens_SYNC/_SYNC/CollectiveMigrationAnalysis/Examplemovies/test"
filenames = ["160112_H2B_noStarve_Pos_000_005_Median_3_frames.tif",
             "160115_H2B_Starve_serumFree_T0_10min_Pos_003_003_Median_3_frames.tif",
             "160126_H2B_T0_1h_3ml_serum_Pos_002_005_Median_3_frames.tif"]

def makeFromCoorinates(ncols, nrows, frame_width, frame_height):
    """
    Generates a list of ncols*nrows evenly spaced x/y coordinates.
    Args:
        ncols: (int) Number of horizontal arrows
        nrows: (int) Number of vertical arrows
        frame_width: (int) with of image in pixels
        frame_height: (int) height of image in pixels

    Returns:
        list of tuples containing origin x/y coordinates for velocity vectors

    """


    dx = frame_width/float(ncols)
    dy = frame_height/float(nrows)
    out = []
    x = int(round(dx/2.0))

    for c in xrange(ncols):
        y = int(round(dy/2.0))
        for r in xrange(nrows):
            out.append((int(round(x)),int(round(y))))
            y += dy

        x += dx
    return out

def makeToCoordinates(fromCoords, Uframe, Vframe, scale):
    """
    Picks and the values from the component vector matrixes at fromCoords
    :param fromCoords: list of from coordinates
    :param Umatrix: U (x) component vector matrix
    :param Vmatrix: V (y) component vector matrix
    :param scale: scalar to multiply u/v values with
    :return: list of tuples containing x/y coordinates
    """

    out = []

    for e in fromCoords:
        x = e[0]
        y = e[1]
        toX = Uframe[x][y]
        toY = Vframe[x][y]
        out.append((int(round(x+toX*scale)),int(round(y+toY*scale))))

    return out

def drawArrows(frame, fromCoords, toCoords, color, thickness, **kwargs):
    """
    Draws arrows on an image
    :param frame: image to draw arrows on
    :param fromCoords: list of tuples containing from x/y coorinates
    :param toCoords:  list of tuples containing to x/y coorinates
    :param color: color of arrows
    :param thickness: arrow thicknes in pixels
    :param **kwargs: extra aruments passed to cv2.arrowedLine
    :return: None, edits image in place
    """
    for i in xrange(len(toCoords)):
        fromX,fromY = fromCoords[i]
        toX, toY = toCoords[i]
        cv2.arrowedLine(frame, (fromX,fromY), (toX,toY), color, thickness, **kwargs)

for filename in filenames:

    raw = tiff.imread(inDirectory + filename)
    nframes, frame_width, frame_height = raw.shape
    ncols, nrows = 15, 15
    scale = 15
    outStack = np.zeros((nframes-1, frame_width, frame_height), dtype='uint8')

    for i in xrange(nframes-1):
        t1 = time.time()
        print "Start frame "+str(i)+"..."+filename
        frame = raw[i]
        next_frame = raw[i+1]
        flow = cv2.calcOpticalFlowFarneback(frame, next_frame, None, 0.5, 3, 9, 3, 5, 1.2, 0)
        Uframe = flow[...,0]
        Vframe = flow[...,1]

        velocityFrame = np.sqrt((Uframe**2+Vframe**2))
        directionFrame = np.arcsin((Vframe/velocityFrame)

        fromCoords = makeFromCoorinates(ncols, nrows, frame_width, frame_height)
        toCoords = makeToCoordinates(fromCoords, Uframe, Vframe, scale)
        drawArrows(outStack[i], fromCoords, toCoords, 255, 1, tipLength=0.2, line_type=cv2.LINE_AA)



        print "Finish frame "+str(i)+" in "+str(time.time()-t1)+" s."

    #print outStack.shape
    tiff.imsave(filename+'_vectors.tif', outStack)


print "All done in "+str(time.time()-t0)+" s"
