from skimage import io
#from skimage import filters
#from matplotlib import pyplot as plt
import cv2
import numpy as np
import os


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

#Open U/V component vector matrices and raw data
Ustack = io.imread("test/U.tif")
Vstack = io.imread("test/V.tif")
#raw = io.imread("test/sub.tif")

#Median blur to avoid extreme values from noise
Ustack = cv2.medianBlur(Ustack,5)
Vstack = cv2.medianBlur(Vstack,5)

nframes, frame_width, frame_height = Ustack.shape
ncols, nrows = 20, 20
scale = 20



outStack = np.zeros(Ustack.shape, np.uint8)

for i in xrange(Ustack.shape[0]):
    frame = outStack[i]
    Uframe = Ustack[i]
    Vframe = Vstack[i]
    fromCoords = makeFromCoorinates(ncols, nrows, frame_width, frame_height)
    toCoords = makeToCoordinates(fromCoords, Uframe, Vframe, scale)

    drawArrows(frame, fromCoords, toCoords, 255, 1, tipLength=0.1)
    outStack[i]=frame


#plt.imshow(dst, cmap='viridis')
#plt.xticks([]), plt.yticks([])
#plt.imsave('testsave.tif', Mstack, cmap='viridis', format='tif')
#plt.show()
io.imsave('testsave.tif', outStack)