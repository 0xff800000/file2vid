import sys
import cv2
import pdb
import time
import pdb
import matplotlib.pyplot as plt
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc
import skvideo.io

def file2array(path):
    f = 0
    try:
        f = open(path,'rb')
    except:
        print('Error while opening path {}'.format(path))
        return
    return list(f.read())

def file2vid(path,FPS,width,height):
    # Open and convert data
    data = file2array(path)
    data = np.array(data, dtype=np.uint8)
    #data = np.unpackbits(data)

    # Create video
    #fourcc = VideoWriter_fourcc(*'MP42')
    ##fourcc = VideoWriter_fourcc(*'X264')
    ##fourcc = VideoWriter_fourcc(*'HEVC')
    #video = VideoWriter('{}.mkv'.format(path), fourcc, float(FPS), (width, height))

    # Reshape data into frames
    repeat_size = 4
    nb_frames = int(np.ceil(data.shape[0]/(width/repeat_size*height/repeat_size*3)))
    padding_size = (width/repeat_size*height/repeat_size*3*nb_frames) - data.shape[0]
    padding = np.zeros(int(padding_size))
    data = np.concatenate((data,padding))
    data = data.reshape((nb_frames,int(height/repeat_size),int(width/repeat_size),3))

    pdb.set_trace()
    data = data.repeat(repeat_size,axis=1).repeat(repeat_size,axis=2)

#    plt.imshow(data[0])

    skvideo.io.vwrite("{}.mkv".format(path),data,
            outputdict={
                "-r":str(FPS)
                }
            )
    return data
#    for frame in data:
#        cv2.imshow('frame',frame)
#        plt.imshow(frame)
#        plt.show()
#        time.sleep(0.5)
#        video.write(frame)


#    # Convert bits to frames
#    for bit in data:
#        frame = []
#        if bit == 1:
#            frame = np.ones((height, width,3), dtype=np.uint8) * 255
#        else:
#            frame = np.zeros((height, width,3), dtype=np.uint8)
#        #cv2.imshow('frame',frame)
#        #plt.imshow(frame)
#        #plt.show()
#        #time.sleep(0.5)
#        video.write(frame)
#    video.release()

def vid2file(path):
    data = skvideo.io.vread(path)
    return data

FPS = 2
width = 256
height = 144
#width = 4
#height = 4
data_i = file2vid(sys.argv[1],FPS,width,height)
data_o = vid2file(sys.argv[1]+".mkv")
pdb.set_trace()



