import cv2
import numpy as np
import tifffile as tiff
import time
from skimage import io

t0 = time.time()
filename = "med_raw.tif"

def makeFromCoorinates(ncols, nrows, frame_width, frame_height):
    """
    Generates a list of ncols*nrows evenly spaced x/y coordinates.
    :param ncols: Number of horizontal arrows
    :param nrows: Number of vertical arrows
    :param frame_width: with of image in pixels
    :param frame_height: heightof image in pixels
    :return: list of tuples containing origin x/y coordinates for velocity vectors
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


raw = tiff.imread(filename)
print raw.shape
nframes, frame_width, frame_height = raw.shape
ncols, nrows = 150, 150
scale = 20


Ustack = np.zeros((frame_width, frame_height,), dtype='float32')
Vstack = np.zeros((frame_width, frame_height,), dtype='float32')
for i in xrange(nframes-6):
    t1 = time.time()
    print "Start frame "+str(i)+"..."
    frame = raw[i]
    next_frame = raw[i+1]
    flow = cv2.calcOpticalFlowFarneback(frame, next_frame, None, 0.5, 3, 9, 3, 5, 1.2, 0)
    Ustack = np.append(Ustack, flow[0])
    Vstack = np.append(Vstack, flow[1])
    print Ustack.shape, flow.dtype
    #fromCoords = makeFromCoorinates(ncols, nrows, frame_width, frame_height)
    #toCoords = makeToCoordinates(fromCoords, Uframe, Vframe, scale)
    #drawArrows(frame, fromCoords, toCoords, 255, 1, tipLength=0.4)
    #outStack[i]=frame
    print "Finish frame "+str(i)+" in "+str(time.time()-t1)+" s."

Ustack = Ustack.reshape((6,frame_width, frame_height))
tiff.imsave('testsave.tif', Ustack)
print "All done in "+str(time.time()-t0)+" s"
