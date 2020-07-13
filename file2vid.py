import sys
import pdb
import time
import pdb
import matplotlib.pyplot as plt
import numpy as np
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
    data = np.unpackbits(data) * 255
    # Black and white images
    #data = data.repeat(3,axis=0)

    # Reshape data into frames
    repeat_size = 4
    repeat_frames = 4
    nb_frames = int(np.ceil(data.shape[0]/(width/repeat_size*height/repeat_size*3)))
    padding_size = (width/repeat_size*height/repeat_size*3*nb_frames) - data.shape[0]
    padding = np.zeros(int(padding_size))
    data = np.concatenate((data,padding))
    data = data.reshape((nb_frames,int(height/repeat_size),int(width/repeat_size),3))

    writer = skvideo.io.FFmpegWriter("{}.mkv".format(path))
    for frame in data:
        if repeat_size:
            frame = frame.repeat(repeat_size,axis=0).repeat(repeat_size,axis=1)
        for i in range(repeat_frames):
            writer.writeFrame(frame)

    writer.close()

    #pdb.set_trace()
    # Repeat frames
    #frame_repeat = 24
    #data = data.repeat(frame_repeat,axis=0)


#    plt.imshow(data[0])

    print(data.shape)

def vid2file(path):
    repeat_size = 4
    repeat_frames = 4
    vidreader = skvideo.io.vreader(path)
    f = open(path+"decoded","wb")
    #print(data.shape)
    frame_i = 0
    for frame in vidreader:
        frame_i += 1
        if frame_i % repeat_frames != 0:
            continue

        data = frame[::repeat_size,::repeat_size,:]
        # decode
        data = np.rint(data/255).astype("uint8")
        data = data.reshape((-1))
        data = np.packbits(data)

        #data.tofile(path+"decoded")
        f.write(data)
    f.close()

    #return data

FPS = 2
width = 176
height = 144
#data_i = file2vid(sys.argv[1],FPS,width,height)
#data_o = vid2file(sys.argv[1]+".mkv")
data_o = vid2file(sys.argv[1])
#plt.imshow(data_i[0])
#plt.show()
#plt.imshow(data_o[0])
#plt.show()
#print(np.rint(data_i[0]/255) == np.rint(data_o[0]/255))
#pdb.set_trace()



