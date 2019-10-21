# -*- coding: utf-8 -*-
'''
                VIDEO CUT
The script for cut, resize and recode video files.
Intended to be used as a helper for a variety of video analysing tools,
just to reduce the input data size.

Look for Settings section to adjust parameters.

Prerequisites: py-opencv, numpy
'''

import cv2

####################################
def decodeFourcc(cc):
    return ''.join([chr((int(cc) >> 8 * i) & 0xff) for i in range(4)]).upper()
####################################
def printStats(fileName):
    cap = cv2.VideoCapture(fileName)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    expectedFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print('File: ', fileName)
    print(
        decodeFourcc(cap.get(cv2.CAP_PROP_FOURCC)), '@', '%.0f FPS'%cap.get(cv2.CAP_PROP_FPS),
        ':', width, 'x', height
    )
    print('Frames: ', expectedFrames)
    cap.release()
####################################
def resize(fromFile, toFile, encoding, scale=1, fps=30, w=None, h=None, firstFrame=None, lastFrame=None):
    cap = cv2.VideoCapture(fromFile)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)*scale)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)*scale)
    if not w is None and not h is None:
        width=w
        height=h
        
    width = width&~1
    height = height&~1
    
    fourcc = cv2.VideoWriter_fourcc(*encoding)

    print('Writing file: ', toFile)
    print(decodeFourcc(fourcc), '@', '%.0f FPS'%fps, ':', width, 'x', height)
    
    out = cv2.VideoWriter(toFile, fourcc, fps, (width, height))
    
    imgCnt = 0
    savedFrames = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        
        if (firstFrame is None or imgCnt >= firstFrame) and (lastFrame is None or imgCnt <= lastFrame):
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            out.write(frame)
            savedFrames +=1
        imgCnt += 1
        
    cap.release()
    out.release()
    
    print ('Written', savedFrames, 'of', imgCnt, 'frames')
####################################
if __name__ == '__main__':

    # ------- Settings -------
    # Input and output file names
    # Note that output file extension can matter for some codecs
    inFile = 'input/22/stb.mp4'
    outFile = 'out.mp4'
    
    # Output video incoding
    # In theory can accept FourCC of video codec
    # In practice it depends on your system
    encoding = 'h264'
    #encoding = 'MJPG'
    #encoding = 'XVID'

    # Output video size. None values means "use scaled input".
    # Note that not every encoding correctly support every frame size.
    # Try to change the size in case of saving troubles
    outSize = (860, 480)
    #outSize = (640, 480)
    #outSize = (None, None)
    
    # Scale factor for video size.
    # Only used if outSize have None values
    outScale = 1
    #outScale = 0.5
    
    # Output file framerate
    outFPS = 30

    # Saving region of frame indices: (FIRST_FRAME, LAST_FRAME).
    # None value means "from the beginning" or "to the end".
    # It's recommended first to run the script with justPrintStats = True
    # to see total number of frames in the input file.
    frameRegion=(None, None)
    #frameRegion=(80, 400)
    
    # If True, doesn't write anything: just prints the input file metadata
    justPrintStats = False
    #justPrintStats = True
    # ------- End of settings -------

    printStats(inFile)
    if not justPrintStats:
        resize(
            inFile, 
            outFile,
            encoding,
            scale=outScale,
            fps=outFPS,
            w=outSize[0], 
            h=outSize[1],
            firstFrame=frameRegion[0],
            lastFrame=frameRegion[1]
        )
    
    cv2.destroyAllWindows()
    print('Done.')