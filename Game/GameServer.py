#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 08:38:01 2020

@author: jean-louquetin (j-l.quetin@hotmail.fr)
"""

import time
import socket as st
import numpy as np
import cv2
import _thread
from myFunctions import inBox,resize,sendImage, inlay,fitSize
from Chess import ChessGame

    
def recvPos(socket,color): # Action after receiving clicked position from the player
    global game,Im1,Im2,Board1,Board2
    global music1_socket,music2_socket,musicPlaying
    while True:
        # Receiving click position
        x = socket.recv(1024)
        if not x:
            socket.close()
            break
        x = int(x.decode())
        print("x : ", x)
        y = socket.recv(1024)
        if not y:
            socket.close()
            break
        y = int(y.decode())
        print("y : ", y)
            
        # According to the clicked position, an action is taken
        if inBox(x,y,resetBox1,resetBox2): 
            game = ChessGame()
            game.placeGame()
            Im1,Im2 = UpdateImage(game,game.Board1,game.Board2)
            print("Reset Game")
        elif inBox(x,y,returnBox1,returnBox2): # cancel a move
            if game.returnOK == 1:
                game.returnToPred()
                Im1,Im2 = UpdateImage(game,game.Board1,game.Board2)
            print("Return to previous state")
        elif inBox(x,y,musicBox1,musicBox2):
            if musicPlaying == 0: # if music was not playing, resumes music
                musicPlaying = 1
                play = str(1)
                play = play.encode("Utf8")
                music1_socket.send(play)
                music2_socket.send(play)
                print(color+" have started the music !")
                Im1,Im2 = UpdateImage(game,game.Board1,game.Board2)
            else: # if music was already playing, then the displayed button is paused, so the music is paused
                musicPlaying = 0
                play = str(2)
                play = play.encode("Utf8")
                music1_socket.send(play)
                music2_socket.send(play)
                print(color+" have paused music.")
                Im1,Im2 = UpdateImage(game,game.Board1,game.Board2)
        elif inBox(x,y,stopBox1,stopBox2):
            musicPlaying = 0
            play = str(0)
            play = play.encode("Utf8")
            music1_socket.send(play)
            music2_socket.send(play)
            print(color+" have stopped music :(")
            Im1,Im2 = UpdateImage(game,game.Board1,game.Board2)
        else: # the click was either on the board to move a piece or somewhere
              # else, taken care of by the addPointers function
            if game.player == color:
                x = int(x/(size_factor))
                y = int(y/(size_factor))
                Board1,Board2 = game.addPointers((x,y))
                Im1,Im2 = UpdateImage(game,Board1,Board2)
    
def UpdateImage(game,Board1,Board2):
    global musicPlaying,size_factor
    global HEIGHT,WIDTH

    background = 255*np.ones(shape=(HEIGHT,WIDTH,3), dtype=np.uint8)
    cv2.putText(background, 'Waiting for '+str.lower(game.player)+' to play !',(background.shape[0]+int(50*size_factor),int(60*size_factor)), cv2.FONT_HERSHEY_SIMPLEX, 1*size_factor,(0,0,0),2)
    
    # Game buttons (reset and return)
    background[resetBox1[1]:resetBox1[1]+hr,resetBox1[0]:resetBox1[0]+wr] = reset
    if game.returnOK==1: # add the return button if possible to return
        background[returnBox1[1]:returnBox2[1],returnBox1[0]:returnBox2[0]]=returnButton
    
    # Cemetery display
    cv2.putText(background, 'Cemetery',(returnBox2[0]+int(10*size_factor),int((returnBox1[1]+(returnBox2[1]-returnBox1[1])*2/3))), cv2.FONT_HERSHEY_SIMPLEX, 1*size_factor,(0,0,0),2)
    cemetery= resize(game.cemetery,size_factor*100)
    hc,wc = cemetery.shape[:2]
    background[HEIGHT-hc:HEIGHT,WIDTH-wc:WIDTH] = cemetery
    
    # Music buttons
    if musicPlaying == 0:
        inlay(background,playButton,musicBox1[0],musicBox1[1],0)
    else:
        inlay(background,pause,musicBox1[0],musicBox1[1],0)
    inlay(background,stop,stopBox1[0],stopBox1[1],0)
    
    # Board display
    # (both images use the same background, but the game board is different)
    im1 = background
    im2 = np.copy(background)
    
    Board1 = fitSize(Board1,(HEIGHT,WIDTH))
    hd,wd = Board1.shape[0],Board1.shape[1]
    im1[0:hd,0:wd] = Board1
    
    Board2 = fitSize(Board2,(HEIGHT,WIDTH))
    hd,wd = Board2.shape[0],Board2.shape[1]
    im2[0:hd,0:wd] = Board2
    
    return im1,im2

def initGameSocket():
 
    HOST = '' # reading through all adresses of the server (local, network, etc)
 
    PORT = 41222
    game_socket = st.socket(st.AF_INET,st.SOCK_STREAM)           # Socket creation
    game_socket.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1)    # Allows to reuse port
    game_socket.bind((HOST,PORT))                                # Allows to receive connections
    game_socket.listen(2)                                        # Waits for 2 connections (the 2 players)
    
    PORT=41223
    send_image_socket = st.socket(st.AF_INET,st.SOCK_STREAM)
    send_image_socket.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1)    
    send_image_socket.bind((HOST,PORT))
    send_image_socket.listen(2)
    
    PORT=41224
    music_socket = st.socket(st.AF_INET,st.SOCK_STREAM)
    music_socket.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1) 
    music_socket.bind((HOST,PORT))
    music_socket.listen(2)
    
    print("Waiting for players")
    
    # When first player connects :
    client1,adresse1 = game_socket.accept() 
    send_image1_socket,addr=send_image_socket.accept()
    music1_socket,addr=music_socket.accept()
    print("Player 1 (",adresse1,") just arrived !")
    
    # Second player connects :
    client2,adresse2 = game_socket.accept() 
    send_image2_socket,addr=send_image_socket.accept() 
    music2_socket,addr=music_socket.accept()
    print("Player 2 (",adresse2,") just arrived !")
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    
    return encode_param,client1,send_image1_socket,music1_socket,client2,send_image2_socket,music2_socket


if __name__ == "__main__":  # execute only if run as a script
      
    # Parameters initialization
    musicPlaying = 0 # not playing  music initially
    size_factor = 0.6 # to modify the size of the displayed window (smaller makes the game faster)
    
    # Loading necessary images
    playButton = resize(cv2.imread('images/play.png'),int(size_factor*35))
    reset = resize(cv2.imread('images/reset.png'),int(size_factor*7))
    returnButton = resize(cv2.imread('images/retour.png'),int(size_factor*11))
    pause = resize(cv2.imread('images/pause.png'),int(size_factor*17.5))
    stop = resize(cv2.imread('images/stop.png'),int(size_factor*9))
    
    # Images sizes definition (w = width, h = height)
    wm = playButton.shape[1]
    hm = playButton.shape[0]
    wr = reset.shape[1]
    hr = reset.shape[0]
    wret = returnButton.shape[1]
    hret = returnButton.shape[0]
    wp = pause.shape[1]
    hp = pause.shape[0]
    ws = stop.shape[1]
    hs = stop.shape[0]
    
    # Positions of the images to display
    HEIGHT = 720 # HEIGHT et WIDTH are the dimensions of the game window
    WIDTH = 1280
    (HEIGHT,WIDTH) = int(HEIGHT*size_factor),int(WIDTH*size_factor)
    musicBox1 = (int(WIDTH*0.9),int(HEIGHT*0.15)) # bouton play et pause
    musicBox2 = (musicBox1[0]+wm,musicBox1[1]+hm)
    stopBox1 = (musicBox1[0],musicBox1[1]+hp+5) # bouton stop
    stopBox2 = (stopBox1[0]+ws,stopBox1[1]+hs)
    resetBox1 = (int(WIDTH*0.57),int(HEIGHT*0.5-hr)) # bouton reset
    resetBox2 = (resetBox1[0]+wr,resetBox1[1]+hr)
    returnBox1 = (resetBox2[0]+10,resetBox1[1]) # bouton retour au coup précédent
    returnBox2 = (returnBox1[0]+wret,returnBox1[1]+hret)
    
    # Chess game initialization
    game = ChessGame()
    game.placeGame()
    Board1 = game.Board1
    Board2 = game.Board2
    print("Game initiated")
        
    # Sockets initialization : connection with players
    encode_param,player1,send_image1_socket,music1_socket,player2,send_image2_socket,music2_socket = initGameSocket()
    print("Connection with both players acquired")
    
    # Players color : Whites for the first connected player
    color = "Whites"
    color = color.encode("Utf8")
    player1.send(color)
    color = "Blacks"
    color = color.encode("Utf8")
    player2.send(color)
    
    # Starting threads for players'moves reception
    _thread.start_new_thread(recvPos,(player1,'Whites')) 
    _thread.start_new_thread(recvPos,(player2,'Blacks')) 
    
    # Im1 and Im2 initialization
    Im1,Im2 = UpdateImage(game,Board1,Board2)
     
    print("You can start !")
        
    while 1: 
        sendImage(Im1,send_image1_socket,encode_param)
        sendImage(Im2,send_image2_socket,encode_param)
        time.sleep(0.2)
    
    
        
        
    
        
    
