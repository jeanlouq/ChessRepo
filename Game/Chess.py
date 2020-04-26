#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 09:59:34 2020

@author: jean-louquetin (j-l.quetin@hotmail.fr)
"""

import cv2
import numpy as np
from myFunctions import resize,inlay

class ChessGame:
    
    # Board and chess piece images
    damier = resize(cv2.imread('images/damier3.jpg'),68) #68
    roib  = cv2.imread('images/pieces/320/WhiteKing.png',-1)
    dameb = cv2.imread('images/pieces/320/WhiteQueen.png',-1)
    foub  = cv2.imread('images/pieces/320/WhiteBishop.png',-1)
    cavab = cv2.imread('images/pieces/320/WhiteKnight.png',-1)
    tourb = cv2.imread('images/pieces/320/WhiteRook.png',-1)
    pionb = cv2.imread('images/pieces/320/WhitePawn.png',-1)
    roin  = cv2.imread('images/pieces/320/BlackKing.png',-1)
    damen = cv2.imread('images/pieces/320/BlackQueen.png',-1)
    foun  = cv2.imread('images/pieces/320/BlackBishop.png',-1)
    cavan = cv2.imread('images/pieces/320/BlackKnight.png',-1)
    tourn = cv2.imread('images/pieces/320/BlackRook.png',-1)
    pionn = cv2.imread('images/pieces/320/BlackPawn.png',-1)
    
    # x0 and y0 define the chess grid starting point (top left)
    x0 = 64
    y0 = 64
    # dx and dy define the size of a chess case
    dx = 69
    dy = 69

    # This function initializes the game
    def __init__(self):
        # Pieces initialization
        self.Whites = initWhites()
        self.Blacks = initBlacks()
        self.WhiteQueenCounter = 1
        self.BlackQueenCounter = 1
        self.hasMovedWKing = 0
        self.hasMovedBKing = 0

        # Player's action initialization
        self.player = 'Whites'
        self.selectedPos = (-1,-1)
        self.selectedType = "ROI" # random initialization

        # Board setup
        self.Board1 = self.damier
        self.Board2 = self.damier
        self.occupTable = np.zeros((8,8),dtype=int)
        for n,(j,i) in self.Whites.items():
            self.occupTable[j][i] = 1
        for n,(j,i) in self.Blacks.items():
            self.occupTable[j][i] = -1
        self.possibilities = [] 
        
        # Cemetery display
        self.cemetery = 200*np.ones(shape=(340,570,3), dtype=np.uint8) 
        self.whiteIndexCimet = 0
        self.blackIndexCimet = 0
        
        # for the return function
        self.returnOK = 0 # possibility to get back to the previous move
        self.oldWhites = self.Whites
        self.oldBlacks = self.Blacks
        self.oldWhiteQueenCounter = 1
        self.oldBlackQueenCounter = 1
        self.oldHasMovedWKing = 0
        self.oldHasMovedBKing = 0
        self.oldBoard1 = np.copy(self.Board1)
        self.oldBoard2 = np.copy(self.Board2)
        self.oldOccupTable = np.copy(self.occupTable)
        self.oldCemetery = 200*np.ones(shape=(340,570,3), dtype=np.uint8)
        self.oldWhiteIndexCimet = 0
        self.oldBlackIndexCimet = 0
        
     
    # this function computes the move of the piece 'name' by the current player
    # ('color') at the location 'place'
    def move(self,color,name,place):
        x0,y0 = self.x0, self.y0
        dx,dy = self.dx,self.dy
        copyDamier = np.copy(self.damier)
        copyDamier2 = cv2.rotate(np.copy(self.damier),cv2.ROTATE_180) 
        if color == 'Whites' and name == 'ROI' and place[1]==2 :
            self.move('Whites','TOUR1',(7,3))
        if color == 'Whites' and name == 'ROI' and place[1]==6 :
            self.move('Whites','TOUR2',(7,5))
        if color == 'Blacks' and name == 'ROI' and place[1]==1 :
            print('Petit roc')
            self.move('Blacks','TOUR2',(7,2))
        if color == 'Blacks' and name == 'ROI' and place[1]==5 :
            self.move('Blacks','TOUR1',(7,4))
            print('Grand roc')
        res = np.copy(self.Board1)     
        res2 = np.copy(self.Board2)
        hd,wd = res2.shape[0],res.shape[1]
        
        if color == 'Whites': # Whites play
            y,x = self.Whites[name]
            self.occupTable[y][x] = 0
            res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
            res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]
            # En passant capture
            if name[0] == 'P' and y == 3 and (place == (y-1,x-1) or place == (y-1,x+1)) and self.occupTable[place[0]][place[1]] == 0 and self.occupTable[place[0]+1][place[1]]==-1:
                for n,p in (self.Blacks.copy()).items():
                    if p==(place[0]+1,place[1]):
                        y,x = p
                        self.occupTable[y][x] = 0
                        res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
                        res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]                        
                        del self.Blacks[n]
                        self.oldCemetery = np.copy(self.cemetery)
                        if n =='DAME' or n == 'DAME2' or n == 'DAME3':
                            deletedPiece = cv2.resize(self.damen, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='FOU1' or n == 'FOU2':
                            deletedPiece = cv2.resize(self.foun, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='CAV1' or n == 'CAV2':
                            deletedPiece = cv2.resize(self.cavan, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='TOUR1' or n == 'TOUR2':
                            deletedPiece = cv2.resize(self.tourn, (dx,dy), interpolation = cv2.INTER_AREA)
                        else:
                            deletedPiece = cv2.resize(self.pionn, (dx,dy), interpolation = cv2.INTER_AREA)
                        i = self.whiteIndexCimet
                        if i < 8:
                            inlay(self.cemetery[0:dy,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                        else:
                            i = i-8
                            inlay(self.cemetery[dy:2*dy,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                        self.whiteIndexCimet += 1 
                        break  
            # General situation
            self.Whites[name]=place
            y,x = place
            self.occupTable[y][x] = 1
            for n,p in (self.Blacks.copy()).items():
                if place==p:
                    y,x = p
                    res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
                    res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]
                    del self.Blacks[n]
                    self.oldCemetery = np.copy(self.cemetery)
                    if n =='DAME' or n == 'DAME2' or n == 'DAME3':
                        deletedPiece = cv2.resize(self.damen, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='FOU1' or n == 'FOU2':
                        deletedPiece = cv2.resize(self.foun, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='CAV1' or n == 'CAV2':
                        deletedPiece = cv2.resize(self.cavan, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='TOUR1' or n == 'TOUR2':
                        deletedPiece = cv2.resize(self.tourn, (dx,dy), interpolation = cv2.INTER_AREA)
                    else:
                        deletedPiece = cv2.resize(self.pionn, (dx,dy), interpolation = cv2.INTER_AREA)
                    i = self.whiteIndexCimet
                    if i < 8:
                        inlay(self.cemetery[0:dy,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                    else:
                        i = i-8
                        inlay(self.cemetery[dy:2*dy,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                    #if self.whiteIndexCimet == self.oldWhiteIndexCimet:
                    self.whiteIndexCimet += 1
                    # else:
                    #     self.whiteIndexCimet += 1
                    #     self.oldWhiteIndexCimet += 1
                    break
                
            if name =='ROI':
                piece = cv2.resize(self.roib, (dx,dy), interpolation = cv2.INTER_AREA)
                if self.hasMovedWKing ==0:
                    self.hasMovedWKing = 1
                else:
                    self.oldHasMovedWKing = 1
            elif name =='DAME' or name == 'DAME2' or name == 'DAME3':
                piece = cv2.resize(self.dameb, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='FOU1' or name == 'FOU2':
                piece = cv2.resize(self.foub, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='CAV1' or name == 'CAV2':
                piece = cv2.resize(self.cavab, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='TOUR1' or name == 'TOUR2':
                piece = cv2.resize(self.tourb, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name[0] == 'P':
                if y == 0: # the pawn becomes a queen when it reaches the other camp
                    self.WhiteQueenCounter += 1
                    self.Whites["DAME"+str(self.cWhiteQueenCounter)] = place
                    del self.Whites[name]
                    piece = cv2.resize(self.dameb, (dx,dy), interpolation = cv2.INTER_AREA)
                else:
                    piece = cv2.resize(self.pionb, (dx,dy), interpolation = cv2.INTER_AREA)
            inlay(res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx],piece,0,0,1)
            inlay(res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)],piece,0,0,1)

        else: # Blacks playing
            y,x = self.Blacks[name]
            self.occupTable[y][x] = 0
            res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
            res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]
            # # En passant capture
            if name[0] == 'P' and y == 4 and (7-place[0] == y+1 and (7-place[1]== x-1 or 7-place[1]==x+1)) and self.occupTable[7-place[0]][7-place[1]] == 0 and self.occupTable[7-place[0]-1][7-place[1]]==1:
                for n,p in (self.Whites.copy()).items():
                    if p==(7-place[0]-1,7-place[1]):
                        y,x = p
                        self.occupTable[y][x] = 0
                        res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
                        res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]
                        del self.Whites[n]
                        self.oldCemetery = np.copy(self.cemetery)
                        if n =='DAME' or n == 'DAME2' or n == 'DAME3':
                            deletedPiece = cv2.resize(self.dameb, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='FOU1' or n == 'FOU2':
                            deletedPiece = cv2.resize(self.foub, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='CAV1' or n == 'CAV2':
                            deletedPiece = cv2.resize(self.cavab, (dx,dy), interpolation = cv2.INTER_AREA)
                        elif n =='TOUR1' or n == 'TOUR2':
                            deletedPiece = cv2.resize(self.tourb, (dx,dy), interpolation = cv2.INTER_AREA)
                        else:
                            deletedPiece = cv2.resize(self.pionb, (dx,dy), interpolation = cv2.INTER_AREA)
                        i = self.blackIndexCimet
                        if i < 8:
                            inlay(self.cemetery[2*dy+5:3*dy+5,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                        else:
                            i = i-8
                            inlay(self.cemetery[3*dy+5:4*dy+5,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                        if self.blackIndexCimet == self.oldBlackIndexCimet:
                            self.blackIndexCimet += 1
                        else:
                            self.blackIndexCimet += 1
                            self.oldBlackIndexCimet += 1
                        break  
            # General situation
            self.Blacks[name]=7-place[0],7-place[1]
            y,x = 7-place[0],7-place[1]
            self.occupTable[y][x] = -1
            for n,p in (self.Whites.copy()).items():
                if (7-place[0],7-place[1])==p:
                    y,x = p
                    res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx] = copyDamier[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx]
                    res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)] = copyDamier2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)]
                    del self.Whites[n]
                    self.oldCemetery = np.copy(self.cemetery)
                    if n =='DAME' or n == 'DAME2' or n == 'DAME3':
                        deletedPiece = cv2.resize(self.dameb, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='FOU1' or n == 'FOU2':
                        deletedPiece = cv2.resize(self.foub, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='CAV1' or n == 'CAV2':
                        deletedPiece = cv2.resize(self.cavab, (dx,dy), interpolation = cv2.INTER_AREA)
                    elif n =='TOUR1' or n == 'TOUR2':
                        deletedPiece = cv2.resize(self.tourb, (dx,dy), interpolation = cv2.INTER_AREA)
                    else:
                        deletedPiece = cv2.resize(self.pionb, (dx,dy), interpolation = cv2.INTER_AREA)
                    i = self.blackIndexCimet
                    if i < 8:
                        inlay(self.cemetery[2*dy+5:3*dy+5,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                    else:
                        i = i-8
                        inlay(self.cemetery[3*dy+5:4*dy+5,i*dx:(i+1)*dx],deletedPiece,0,0,1)
                    if self.blackIndexCimet == self.oldBlackIndexCimet:
                        self.blackIndexCimet += 1
                    else:
                        self.blackIndexCimet += 1
                        self.oldBlackIndexCimet += 1
                    break
            
            if name =='ROI':
                piece = cv2.resize(self.roin, (dx,dy), interpolation = cv2.INTER_AREA)
                if self.hasMovedBKing ==0:
                    self.hasMovedBKing = 1
                else:
                    self.oldHasMovedBKing = 1
            elif name =='DAME' or name == 'DAME2' or name == 'DAME3':
                piece = cv2.resize(self.damen, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='FOU1' or name == 'FOU2':
                piece = cv2.resize(self.foun, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='CAV1' or name == 'CAV2':
                piece = cv2.resize(self.cavan, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name =='TOUR1' or name == 'TOUR2':
                piece = cv2.resize(self.tourn, (dx,dy), interpolation = cv2.INTER_AREA)
            elif name[0] == 'P': 
                if y == 7: # the pawn becomes a queen when it reaches the other camp
                    self.BlackQueenCounter += 1
                    self.Blacks["DAME"+str(self.BlackQueenCounter)] = place
                    del self.Blacks[name]
                    piece = cv2.resize(self.damen, (dx,dy), interpolation = cv2.INTER_AREA)
                else:
                    piece = cv2.resize(self.pionn, (dx,dy), interpolation = cv2.INTER_AREA)
            inlay(res[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx],piece,0,0,1)
            inlay(res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)],piece,0,0,1)
            
        self.Board1 = res
        self.Board2 = res2
        print(self.occupTable)
        return res,res2
    
    def placeGame(self):
        global roib,dameb,foub,cavab,tourb,pionb
        global roin,damen,foun,cavan,tourn,pionn
        x0,y0 = self.x0, self.y0
        dx,dy = self.dx,self.dy
        res1 = np.copy(self.damier)
        hd,wd = res1.shape[0],res1.shape[1]
        res2 = cv2.rotate(np.copy(self.damier),cv2.ROTATE_180)
        for n,(y,x) in self.Whites.items():
            if n =='ROI':
                piece = cv2.resize(self.roib, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='DAME' or n == 'DAME2' or n == 'DAME3':
                piece = cv2.resize(self.dameb, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='FOU1' or n == 'FOU2':
                piece = cv2.resize(self.foub, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='CAV1' or n == 'CAV2':
                piece = cv2.resize(self.cavab, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='TOUR1' or n == 'TOUR2':
                piece = cv2.resize(self.tourb, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n in ['P1','P2','P3','P4','P5','P6','P7','P8']:
                piece = cv2.resize(self.pionb, (dx,dy), interpolation = cv2.INTER_AREA)
            inlay(res1[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx],piece,0,0,1)
            inlay(res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)],piece,0,0,1)
        for n,(y,x) in self.Blacks.items():
            if n =='ROI':
                piece = cv2.resize(self.roin, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='DAME' or n == 'DAME2' or n == 'DAME3':
                piece = cv2.resize(self.damen, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='FOU1' or n == 'FOU2':
                piece = cv2.resize(self.foun, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='CAV1' or n == 'CAV2':
                piece = cv2.resize(self.cavan, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n =='TOUR1' or n == 'TOUR2':
                piece = cv2.resize(self.tourn, (dx,dy), interpolation = cv2.INTER_AREA)
            elif n in ['P1','P2','P3','P4','P5','P6','P7','P8']:
                piece = cv2.resize(self.pionn, (dx,dy), interpolation = cv2.INTER_AREA)
            inlay(res1[y0+y*dy:y0+(y+1)*dy,x0+x*dx:x0+(x+1)*dx],piece,0,0,1) 
            inlay(res2[hd-1-(y0+(y+1)*dy):hd-1-(y0+y*dy),wd-1-(x0+(x+1)*dx):wd-1-(x0+x*dx)],piece,0,0,1)
        self.Board1 = res1
        self.Board2 = res2
        
    def addPointers(self,clickedPos):
        x0,y0 = self.x0, self.y0
        dx,dy = self.dx,self.dy
        x,y = clickedPos[0], clickedPos[1]
        i,j = (int((x-x0)/dx),int((y-y0)/dy))
        if self.player == 'Whites':
            pos1 = (x0+i*dx,y0+j*dy)
            pos2 = (x0+(i+1)*dx,y0+(j+1)*dy)
            res = np.copy(self.Board1)
           
            if self.selectedPos == (-1,-1):
                self.selectedPos = pos1
                items = self.Whites.items()
                for n,(k,l) in items:
                    if (k,l) == (j,i):
                        print('Selection : ',(i,j))
                        self.selectedType = n
                        res,self.possibilities = self.dispPossibilities(res,x,y,dx,dy,x0,y0,n,self.player)
                cv2.rectangle(res,pos1,pos2, (0,0,255), 4)
                res1 = res
                res2 = self.Board2
            else:
                l = len(self.possibilities)
                if l!=0:
                    for k in range(l):
                        if (self.possibilities[k][0],self.possibilities[k][1]) == (i,j):
                            print('Move :',(i,j))
                            self.returnOK = 1
                            self.oldWhites = self.Whites.copy()
                            self.oldBlacks = self.Blacks.copy() 
                            self.oldWhiteQueenCounter = self.WhiteQueenCounter
                            self.oldBlackQueenCounter = self.BlackQueenCounter
                            self.oldHasMovedWKing = self.hasMovedWKing
                            self.oldHasMovedBKing = self.hasMovedBKing
                            
                            self.oldBoard1 = np.copy(self.Board1)
                            self.oldBoard2 = np.copy(self.Board2)
                            self.oldOccupTable = np.copy(self.occupTable)
                            self.oldCemetery = self.cemetery
                            self.oldWhiteIndexCimet = self.whiteIndexCimet
                            self.oldBlackIndexCimet = self.blackIndexCimet
                            res1,res2 = self.move(self.player,self.selectedType,(j,i))
                            if self.player == 'Whites':
                                self.player = 'Blacks'
                            else:
                                self.player = 'Whites'
                            break
                    self.possibilities = []
                self.selectedPos = (-1,-1)
                res1 = self.Board1
                res2 = self.Board2
        else:
            ir = 7-i
            jr = 7-j
            pos1 = (x0+i*dx,y0+j*dy)
            pos2 = (x0+(i+1)*dx,y0+(j+1)*dy)
            res = np.copy(self.Board2)
            if self.selectedPos == (-1,-1):
                self.selectedPos = pos1
                items = self.Blacks.items()
                for n,(k,l) in items:
                    if (k,l) == (jr,ir):
                        print('Selection : ',(i,j))
                        self.selectedType = n
                        res,self.possibilities = self.dispPossibilities(res,x,y,dx,dy,x0,y0,n,self.player)                
                cv2.rectangle(res,pos1,pos2, (0,0,255), 4)
                res1 = self.Board1
                res2 = res
            else:
                l = len(self.possibilities)
                if l!=0:
                    for k in range(l):
                        if (self.possibilities[k][0],self.possibilities[k][1]) == (i,j):
                            print('Move :',(i,j))
                            self.returnOK = 1
                            self.oldWhites = self.Whites.copy()
                            self.oldBlacks = self.Blacks.copy() 
                            self.oldWhiteQueenCounter = self.WhiteQueenCounter
                            self.oldBlackQueenCounter = self.BlackQueenCounter
                            self.oldHasMovedWKing = self.hasMovedWKing
                            self.oldHasMovedBKing = self.hasMovedBKing
                            
                            self.oldBoard1 = np.copy(self.Board1)
                            self.oldBoard2 = np.copy(self.Board2)
                            self.oldOccupTable = np.copy(self.occupTable)
                            self.oldCemetery = self.cemetery
                            self.oldWhiteIndexCimet = self.whiteIndexCimet
                            self.oldBlackIndexCimet = self.blackIndexCimet

                            res1,res2 = self.move(self.player,self.selectedType,(j,i))
                            if self.player == 'Whites':
                                self.player = 'Blacks'
                            else:
                                self.player = 'Whites'
                            break
                    self.possibilities = []
                self.selectedPos = (-1,-1)
                res1 = self.Board1
                res2 = self.Board2
        return res1,res2
    
    def dispPossibilities(self,im,x,y,dx,dy,x0,y0,n,color):
        li = []
        lj = []
        posslist = []
        i = int((x-x0)/dx)
        j = int((y-y0)/dy)
        if color == 'Blacks':
            i = 7-i
            j = 7-j
        if n == "CAV1" or n == 'CAV2':
                li += [i-1,i+1,i-2, i-2,i+2,i+2,i-1,i+1]
                lj += [j-2,j-2,j-1,j+1,j-1,j+1,j+2,j+2]
        elif n == "FOU1" or n == 'FOU2':
            for s in range(1,8):
                li+=[i+s]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and i+s>=0 and i+s<=7 and not(self.occupTable[j+s][i+s]==0):
                    break    
            for s in range(1,8):
                li+=[i-s]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and i-s>=0 and i-s<=7 and not(self.occupTable[j+s][i-s]==0):
                    break
            for s in range(1,8):
                li+=[i+s]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and i+s>=0 and i+s<=7 and not(self.occupTable[j-s][i+s]==0):
                    break
            for s in range(1,8):
                li+=[i-s]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and i-s>=0 and i-s<=7 and not(self.occupTable[j-s][i-s]==0):
                    break
        elif n == "TOUR1" or n == 'TOUR2':
            for s in range(1,8):
                li+=[i]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and not(self.occupTable[j+s][i]==0):
                    break    
            for s in range(1,8):
                li+=[i]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and not(self.occupTable[j-s][i]==0):
                    break
            for s in range(1,8):
                li+=[i+s]
                lj+=[j]
                if i+s >= 0 and i+s<=7 and not(self.occupTable[j][i+s]==0):
                    break
            for s in range(1,8):
                li+=[i-s]
                lj+=[j]
                if i-s >= 0 and i-s<=7 and not(self.occupTable[j][i-s]==0):
                    break
        elif n == 'DAME' or n == 'DAME2' or n == 'DAME3':
            for s in range(1,8):
                li+=[i]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and not(self.occupTable[j+s][i]==0):
                    break    
            for s in range(1,8):
                li+=[i]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and not(self.occupTable[j-s][i]==0):
                    break
            for s in range(1,8):
                li+=[i+s]
                lj+=[j]
                if i+s >= 0 and i+s<=7 and not(self.occupTable[j][i+s]==0):
                    break
            for s in range(1,8):
                li+=[i-s]
                lj+=[j]
                if i-s >= 0 and i-s<=7 and not(self.occupTable[j][i-s]==0):
                    break
            for s in range(1,8):
                li+=[i+s]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and i+s>=0 and i+s<=7 and not(self.occupTable[j+s][i+s]==0):
                    break    
            for s in range(1,8):
                li+=[i-s]
                lj+=[j+s]
                if j+s >= 0 and j+s<=7 and i-s>=0 and i-s<=7 and not(self.occupTable[j+s][i-s]==0):
                    break
            for s in range(1,8):
                li+=[i+s]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and i+s>=0 and i+s<=7 and not(self.occupTable[j-s][i+s]==0):
                    break
            for s in range(1,8):
                li+=[i-s]
                lj+=[j-s]
                if j-s >= 0 and j-s<=7 and i-s>=0 and i-s<=7 and not(self.occupTable[j-s][i-s]==0):
                    break
        elif color == 'Blacks' and n == 'ROI':
            lir = [i-1,i-1,i-1,i,i,i,i+1,i+1,i+1]
            ljr = [j-1,j,j+1,j-1,j,j+1,j-1,j,j+1]
            for k in range(len(lir)):
                if ljr[k]>=0 and ljr[k] <=7 and lir[k]>=0 and lir[k] <=7 and not(self.occupTable[ljr[k]][lir[k]]==-1):
                    li+=[lir[k]]
                    lj+=[ljr[k]]
            if not(self.hasMovedBKing) and 'TOUR1' in self.Blacks and self.Blacks['TOUR1'] == (0,0) and self.occupTable[0][1]==0 and self.occupTable[0][2]==0 and self.occupTable[0][3]==0 :
                li += [i-2]
                lj += [j]
            if not(self.hasMovedBKing) and 'TOUR2' in self.Blacks and self.Blacks['TOUR2'] == (0,7) and self.occupTable[0][5]==0 and self.occupTable[0][6]==0 :
                li += [i+2]
                lj += [j]
        elif color == 'Blacks': # Black pawn
                if j==1:
                    li += [i  ,i  ]
                    lj += [j+1,j+2]
                else:
                    li += [i  ]
                    lj += [j+1]
                if j+1 >= 0 and j+1<=7 and i-1>=0 and i-1<=7 and self.occupTable[j+1][i-1]==1:
                    li += [i-1]
                    lj += [j+1]
                if j+1 >= 0 and j+1<=7 and i+1>=0 and i+1<=7 and self.occupTable[j+1][i+1]==1:
                    li += [i+1]
                    lj += [j+1]
                if j == 4 and i-1>=0 and self.occupTable[j][i-1]==1 and not(self.occupTable[j+1][i-1]==-1):
                    li += [i-1]
                    lj += [j+1]
                if j == 4 and i+1<=7 and self.occupTable[j][i+1]==1 and not(self.occupTable[j+1][i+1]==-1):
                    li += [i+1]
                    lj += [j+1]
                        
        elif n == 'ROI': # White king
                lir = [i-1,i-1,i-1,i,i,i,i+1,i+1,i+1]
                ljr = [j-1,j,j+1,j-1,j,j+1,j-1,j,j+1]
                for k in range(len(lir)):
                    if ljr[k]>=0 and ljr[k] <=7 and lir[k]>=0 and lir[k] <=7 and not(self.occupTable[ljr[k]][lir[k]]==1):
                        li+=[lir[k]]
                        lj+=[ljr[k]]
                if not(self.hasMovedWKing) and 'TOUR1' in self.Whites and self.Whites['TOUR1'] == (7,0) and self.occupTable[7][1]==0 and self.occupTable[7][2]==0 and self.occupTable[7][3]==0 :
                    li += [i-2]
                    lj += [j]
                if not(self.hasMovedWKing) and 'TOUR2' in self.Whites and self.Whites['TOUR2'] == (7,7) and self.occupTable[7][5]==0 and self.occupTable[7][6]==0 :
                    li += [i+2]
                    lj += [j]
        else : # White pawn
            if j==6:
                li += [  i,  i]
                lj += [j-1,j-2]
            else:
                li += [i  ]
                lj += [j-1]
            if j-1 >= 0 and j-1<=7 and i-1>=0 and i-1<=7 and self.occupTable[j-1][i-1]==-1:
                li += [i-1]
                lj += [j-1]
            if j-1 >= 0 and j-1<=7 and i+1>=0 and i+1<=7 and self.occupTable[j-1][i+1]==-1:
                li += [i+1]
                lj += [j-1]
            if j == 3 and i-1>=0 and self.occupTable[j][i-1]==-1:
                li += [i-1]
                lj += [j-1]
            if j == 3 and i+1<=7 and self.occupTable[j][i+1]==-1:
                li += [i+1]
                lj += [j-1]
                        
        for s in range(len(li)):
            if color == 'Blacks':
                if li[s]>=0 and li[s]<=7 and lj[s]>=0 and lj[s]<=7 and not(self.occupTable[lj[s]][li[s]]==-1):
                    li[s] = 7-li[s]
                    lj[s] = 7-lj[s]
                    im = cv2.rectangle(im,(x0+li[s]*dx,y0+lj[s]*dy),(x0+li[s]*dx+dx,y0+lj[s]*dy+dy), (0,255,0), 4) 
                    posslist += [(li[s],lj[s])] 
            else:
                if li[s]>=0 and li[s]<=7 and lj[s]>=0 and lj[s]<=7 and not(self.occupTable[lj[s]][li[s]]==1):
                    im = cv2.rectangle(im,(x0+li[s]*dx,y0+lj[s]*dy),(x0+li[s]*dx+dx,y0+lj[s]*dy+dy), (0,255,0), 4) 
                    posslist += [(li[s],lj[s])] 
        return im,posslist  

    def returnToPred(self):
        self.Whites = self.oldWhites.copy()
        self.Blacks = self.oldBlacks.copy()
        self.WhiteQueenCounter = self.oldWhiteQueenCounter
        self.BlackQueenCounter = self.oldBlackQueenCounter
        self.hasMovedWKing = self.oldHasMovedWKing
        self.hasMovedBKing = self.oldHasMovedBKing
        self.Board1 = np.copy(self.oldBoard1)
        self.Board2 = np.copy(self.oldBoard2)
        if self.player == 'Blacks':
            self.player = 'Whites'
        else:
            self.player = 'Blacks'
        self.selectedPos = (-1,-1)
        self.selectedType = "ROI" # no use, for initialization only
        self.possibilities = []
        self.occupTable = np.copy(self.oldOccupTable)
        print(self.occupTable)
        self.cemetery = self.oldCemetery
        self.whiteIndexCimet = self.oldWhiteIndexCimet
        self.blackIndexCimet = self.oldBlackIndexCimet
        self.returnOK = 0
  
def initBlacks():
    a = {}
    a["ROI"]   = (0,4)
    a["DAME"]  = (0,3)
    a["FOU1"]  = (0,2)
    a["FOU2"]  = (0,5)
    a["CAV1"]  = (0,1)
    a["CAV2"]  = (0,6)
    a["TOUR1"] = (0,0)
    a["TOUR2"] = (0,7)
    a["P1"] = (1,0)
    a["P2"] = (1,1)
    a["P3"] = (1,2)
    a["P4"] = (1,3)
    a["P5"] = (1,4)
    a["P6"] = (1,5)
    a["P7"] = (1,6)
    a["P8"] = (1,7)
    return a

def initWhites():
    a = {}
    a["ROI"]   = (7,4)
    a["DAME"]  = (7,3)
    a["FOU1"]  = (7,2)
    a["FOU2"]  = (7,5)
    a["CAV1"]  = (7,1)
    a["CAV2"]  = (7,6)
    a["TOUR1"] = (7,0)
    a["TOUR2"] = (7,7)
    a["P1"] = (6,0)
    a["P2"] = (6,1)
    a["P3"] = (6,2)
    a["P4"] = (6,3)
    a["P5"] = (6,4)
    a["P6"] = (6,5)
    a["P7"] = (6,6)
    a["P8"] = (6,7)
    return a


    
