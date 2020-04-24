#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 08:38:01 2020

@author: jean-louquetin (j-l.quetin@hotmail.fr)

This program tries to connect to the server for a chess game.
When both players are connected, the game starts with a board displayed.
The player that is not playing has no action on the board but can play/pause/stop the music

Warning : before running, please set the adress of your server
"""

import cv2 # for image visualization
import time
import _thread
import socket as st # for data exhange with server
import struct,pickle # to send images
import vlc # to play music
    
def mouseEvent(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN : #checks mouse left button down condition
        global position_socket        
        try:
            sendPosition(position_socket ,int(round(x)),int(round(y)))
            print('Move sent')
        except:
            print('Unable to send move')      

def initSocket():
    
    # Connection with the game server
    adress = '88.125.53.111'
    print("Attempting to connect to server ("+adress+") ...")
    
    # Socket to send the position clicked by the player
    port = 41222
    position_socket = st.socket(st.AF_INET,st.SOCK_STREAM) # Création du socket
    position_socket.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1)
    position_socket.connect((adress,port))
    
    # Socket to receive the board image
    port = 41223
    recv_image_socket = st.socket(st.AF_INET, st.SOCK_STREAM)
    recv_image_socket.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1)  
    recv_image_socket.connect((adress, port))
    
    #Socket for music management
    port =41224
    music_socket = st.socket(st.AF_INET, st.SOCK_STREAM)
    music_socket.connect((adress, port))

    print('Connection acquired')
    
    return position_socket,recv_image_socket,music_socket

def sendPosition(sock,x,y):
    command =str(x)
    command = command.encode("Utf8")
    sock.send(command)
    time.sleep(0.1) # a small delay is added to avoid the reception of both values in only one
    command =str(y)
    command = command.encode("Utf8")
    sock.send(command)
        
def playMusic(socket):
    # Music loading
    sheeran = vlc.MediaPlayer("./music.m4a")
    print("Music loaded")
    while True:
        go = socket.recv(1024)
        go = int(go.decode())
        if go == 1:
            print("Let's play music !")
            sheeran.play()
        elif go == 0: # go = 0 : someone stopped the music, it will then be played back to the start
            sheeran.stop()
            print("Music stopped")
        else: # go = 2 : someone paused the music
            sheeran.pause()
            print("Music paused")
        time.sleep(0.2) 
        
        
def receiveGame(connection):
    global imJeu,data  
    # Until the program is closed, thie function tries to receive images sent by the server
    while True:
        
        while len(data) < payload_size:
            data += connection.recv(4096)
            
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))
                
        while len(data) < msg_size:
            data += connection.recv(4096)
            frame_data = data[:msg_size]
        data = data[msg_size:]
            
        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        imJeu = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        time.sleep(0.2)

if __name__ == "__main__":  # execute only if run as a script
     
    # Sockets Initialisation - Connection to the game server 
    position_socket,recv_image_socket,music_socket  = initSocket()  
    print("Waiting for all the players")
    
    # Reception of the player's color (black or white)
    joueur = position_socket.recv(1024)
    joueur = joueur.decode()
    print("You play the ", joueur)
    
    # Reception of the first image
    data = b""
    payload_size = struct.calcsize(">L")
    while len(data) < payload_size:
        data += recv_image_socket.recv(4096)        
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]       
    while len(data) < msg_size:
        data += recv_image_socket.recv(4096)
        frame_data = data[:msg_size]
    data = data[msg_size:] 
    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    imJeu = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    print("Let's start !")
            
    _thread.start_new_thread(receiveGame, (recv_image_socket,))   
    _thread.start_new_thread(playMusic, (music_socket,))   
     
    # Definition of the displayed window
    cv2.namedWindow(joueur, cv2.WINDOW_NORMAL)
    # Activation of the mouse pointer
    cv2.setMouseCallback(joueur,mouseEvent) 
    while True:                
        cv2.imshow(joueur,imJeu)
        if cv2.waitKey(20) & 0xFF == 27: # if 'esc' is pressed, the window is closed and the program stops
              break
          
    cv2.destroyAllWindows()
    


