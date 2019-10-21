# -*- coding: utf-8 -*-
'''
                TIME WARP
The script swaps one of spacial axes of the input video with its time axis
and saves the result to output.

Look for Settings section to adjust parameters.

Prerequisites: py-opencv, numpy
'''

import cv2
import numpy as np;
####################################
def appendFrame(tensor, frame, ind):
    try:
        if not type(tensor) == np.ndarray:
            w = frame.shape[1]
            h = frame.shape[0]
            proposedFrmCnt = w
            tensor = np.ndarray((proposedFrmCnt, h, w, 3), dtype=np.uint8)
            
        if tensor.shape[0] > ind:
            tensor[ind] = frame
        else:
            tensor = np.append(tensor, [frame], axis=0)
        return tensor
    except:
        print('Error appending frame')
        return None
####################################
def timeWarp(tensor, axis='x'):
    try:
        if axis.lower() == 'x':
            return np.transpose(tensor, (2, 1, 0, 3))
        if axis.lower() == 'y':
            return np.transpose(tensor, (1, 0, 2, 3))
    except:
        pass
    
    print ('Error warping time')
    return tensor
####################################
def decodeFourcc(cc):
    return ''.join([chr((int(cc) >> 8 * i) & 0xff) for i in range(4)]).upper()
####################################
def readTensor(fileName, scale=1):
    cap = cv2.VideoCapture(fileName)
    frmCnt = 0
    
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        expectedFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print('Reading file: ', fileName)
        print(
            decodeFourcc(cap.get(cv2.CAP_PROP_FOURCC)), '@', '%.0f FPS'%cap.get(cv2.CAP_PROP_FPS),
            ':', width, 'x', height
        )
        print('Expected frames: ', expectedFrames)
        
        if not scale == 1:
            width = int(scale*width)
            height = int(scale*height)
            
        width = width&~1
        height = height&~1
    
        tensor = np.ndarray((expectedFrames, height, width, 3), dtype=np.uint8)
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                break
            if scale == 1:
                tensor = appendFrame(tensor, frame, frmCnt)
            else:
                tensor = appendFrame(tensor, cv2.resize(frame, (width, height)), frmCnt)
            frmCnt += 1
    except:
        print('Error reading file: ', fileName)
    cap.release()

    if (tensor.shape[0] > frmCnt):
        tensor = tensor[:frmCnt]

    print('Read frames: ', frmCnt)
    return tensor
####################################
def writeTensor(fileName, encoding, tensor, fps, display=False, writeFile=True, scale=(1, 1)):
    if not type(tensor) == np.ndarray or not len(tensor.shape) == 4:
        print ('Error saving: wrong tensor format');
        return
    isScaling = not scale[0] == 1 or not scale[1] == 1
    width = tensor.shape[2]
    height = tensor.shape[1]
    
    if isScaling:
        width = int(scale[0]*width)
        height = int(scale[1]*height)
        
    width = width&~1
    height = height&~1
    
    fourcc = cv2.VideoWriter_fourcc(*encoding)

    print('Writing file: ', fileName)
    print(
        decodeFourcc(fourcc), '@', '%.0f FPS'%fps,
        ':', width, 'x', height
    )
    print('Planned frames: ', tensor.shape[0])
    
    frmCnt = 0
    try:
        out = cv2.VideoWriter(fileName, fourcc, fps, (width, height))
        
        for i in range(tensor.shape[0]):
            frm = tensor[i] if not isScaling else cv2.resize(tensor[i], (width, height), interpolation=cv2.INTER_CUBIC)
            if display:
                cv2.imshow('frame', frm)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                
            if writeFile:
                out.write(frm)
                
            frmCnt += 1
    except:
        print('Error writing file: ', fileName)
    out.release()
    print('Written frames: ', frmCnt)
####################################
if __name__ == '__main__':

    # ------- Settings -------
    # Input and output file names
    # Note that output file extension can matter for some codecs
    inFile = 'in.mp4'
    outFile = 'out.mp4'
    
    # Output video incoding
    # In theory can accept FourCC of video codec
    # In practice it depends on your system
    encoding = 'h264'
    #encoding = 'MJPG'
    #encoding = 'XVID'
    
    # Spacial axis to be swapped with time. Can be 'x' or 'y'.
    # In practice for most scenes you can film either X will result
    # in an interesting result or none.
    swapAxis = 'x'
    
    # Output video scale along X and Y axes. Usially the time-swapped axis
    # needs to be aditionally scaled just to make more common frame proportions
    outScale=(2, 1)

    # Output file framerate
    outFPS = 30
    
    # Output flags. What to do with the resulting time-warped video
    # Note that displaying works always, while the file writing can fail
    # some on frame sizes using some encodings.
    # Press 'q' during the displaying to stop video.
    doDisplay = False
    doWrite = True
    # ------- End of settings -------
    
    tensor = readTensor(inFile, scale=1)
    print (tensor.shape)
    tensor = timeWarp(tensor, swapAxis)
    print (tensor.shape)
    writeTensor(
            outFile, 
            encoding,
            tensor, 
            outFPS, 
            display=doDisplay,
            writeFile=doWrite, 
            scale=outScale
    )
    
    cv2.destroyAllWindows()
    print('Done.')
