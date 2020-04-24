#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:04:42 2020

@author: jean-louquetin

Define functions used by the GameServer and Chess.py
"""

import cv2
import time
import pickle
import struct

# Check if the coordinates (x,y) are located in the rectangle defined by its 
# top left corner tl and its botton right corner br
def inBox(x,y,tl,br):
    if x >= tl[0] and x <= br[0] and y >= tl[1] and y <= br[1]:
        return True
    else:
        return False

# Resize the image 'frame' with a factor scale_percent
def resize(frame,scale_percent):
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    return cv2.resize(frame,(width, height), interpolation = cv2.INTER_AREA)

# Resize the image i1 to fit into the dimensions shape2 of another image
def fitSize(i1,shape2):
    h1,w1,_ = i1.shape
    h2,w2 = shape2
    nh = int(h2/h1*100)
    nw = int(w2/w1*100)
    return resize(i1,min(nh,nw))
    
# Send the image 'im' through 'socket' with encoding parameters 'param'
def sendImage(im,socket,param):
    result, frame = cv2.imencode('.jpg', im, param)
    data = pickle.dumps(frame, 0)
    size = len(data)
    socket.sendall(struct.pack(">L", size) + data)
    
# Inlay the image im into the image background
def inlay(background,im,dx,dy,pasFond):
    width = im.shape[1]
    height = im.shape[0]
    if pasFond:
        for i in range(width):
            for j in range(height):
                if im[j,i,3]>0:
                    background[dy+j,dx+i,0]= im[j,i,0]
                    background[dy+j,dx+i,1]= im[j,i,1]
                    background[dy+j,dx+i,2]= im[j,i,2]
    else:
        for i in range(width):
            for j in range(height):
                if im[j,i,0]<20 and im[j,i,1]<20 and im[j,i,2]<20:
                    background[dy+j,dx+i,0]= im[j,i,0]
                    background[dy+j,dx+i,1]= im[j,i,1]
                    background[dy+j,dx+i,2]= im[j,i,2]