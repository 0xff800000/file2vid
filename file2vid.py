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
    repeat_size = 0
    if repeat_size:
        nb_frames = int(np.ceil(data.shape[0]/(width/repeat_size*height/repeat_size*3)))
        padding_size = (width/repeat_size*height/repeat_size*3*nb_frames) - data.shape[0]
        padding = np.zeros(int(padding_size))
        data = np.concatenate((data,padding))
        data = data.reshape((nb_frames,int(height/repeat_size),int(width/repeat_size),3))

        data = data.repeat(repeat_size,axis=1).repeat(repeat_size,axis=2)
    else:
        nb_frames = int(np.ceil(data.shape[0]/(width*height*3)))
        padding_size = (width*height*3*nb_frames) - data.shape[0]
        padding = np.zeros(int(padding_size))
        data = np.concatenate((data,padding))
        data = data.reshape((nb_frames,int(height),int(width),3))



#    plt.imshow(data[0])

    print(data.shape)
    skvideo.io.vwrite("{}.mkv".format(path),data,
#            outputdict={
#                "-r":str(FPS)
#                }
            )
    #return data

def vid2file(path):
    data = skvideo.io.vread(path)
    print(data.shape)

    # decode
    data = np.rint(data/255).astype("uint8")
    data = data.reshape((-1))
    data = np.packbits(data)

    #data.tofile(path+"decoded")
    f = open(path+"decoded","wb")
    f.write(data)
    f.close()

    #return data

def reassamble(data):
    return

FPS = 2
width = 256
height = 144
#width = 4
#height = 4
data_i = file2vid(sys.argv[1],FPS,width,height)
data_o = vid2file(sys.argv[1]+".mkv")
#plt.imshow(data_i[0])
#plt.show()
#plt.imshow(data_o[0])
#plt.show()
#print(np.rint(data_i[0]/255) == np.rint(data_o[0]/255))
#pdb.set_trace()



