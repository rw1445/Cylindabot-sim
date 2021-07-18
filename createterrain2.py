# interace for creating terrain

'''
Each terrain tile is design to be a square.
The terrain tile is defined by two feature:
    1) is it made of steps or slopes (height fields or cubiods)
    2) an array of heights which define the shape of the tile
Of course its position and size is also important but these are more obvious
'''

try:
    import vrep
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time

clientID=0

from math import *
from numpy import *
from time import sleep
import csv
from random import *
from terrain_heightsNew import *
from designing_terrain import *

slope_heights = [Easy_slopes,Medium_slopes,Hard_slopes,Pyramid_egypt,Pit]
step_heights = [Easy_steps,Medium_steps,Hard_steps,Pyramid_aztec,Walls]


default_heights = [random()*0.3 for k in range(25)]


def callSingleStep(height,size,x,y):
    #Call a function in lua
    vrep.simxCallScriptFunction(clientID,"StartTile",
                                vrep.sim_scripttype_childscript,
                                'make_single_step',
                                [],[height,size,x,y],[],bytearray(),
                                vrep.simx_opmode_blocking)

def gridSteps(heights, grid, size, x, y):
    #for a set of heights
    i_size = size/grid
    x_start, y_start = x + (i_size - size)/2, y + (i_size - size)/2
    for i in range(grid**2):
        i_height = heights[i]
        i_x = x_start + (i%grid)*i_size
        i_y = y_start + (i//grid)*i_size
        callSingleStep(i_height,i_size,i_x,i_y)
    

def callHeightField(heights,grid,size,x_pos,y_pos):
    # call a function in lua to create a height field
    min_h = min(heights)
    max_h = max(heights)
    pos_z = min_h + (min_h + max_h)/2
    vrep.simxCallScriptFunction(clientID,"StartTile",
                                vrep.sim_scripttype_childscript,
                                'make_height_field',
                                [],[grid,size,x_pos,y_pos,pos_z]+heights,[],bytearray(),
                                vrep.simx_opmode_blocking)


def zeroEdge(heights_in, grid_in):
    #makes the field of height bigger so that the edge can be zero
    rows = []
    for i in range(grid_in):
        rows += [heights_in[grid_in*i:grid_in*i+grid_in]]
    grid_out = grid_in + 2
    heights_out = [0.0]*grid_out
    for i in range(grid_in):
        heights_out += [0.0] + rows[i] + [0.0]
    heights_out += [0.0]*grid_out
    
    return heights_out, grid_out

def randomHeights(min_h,range_h,grid):
    #creates a random set of heights
    return [round(random()*range_h+min_h,5) for k in range(grid**2)]

def setupTerrainRandom (h,t):
    #creates random terrain
    grid = 5
    size = 1
    heights = randomHeights(0,h,grid) 
    if t == 1:
        #slopes
        heights2,grid = zeroEdge(heights,grid)
        callHeightField(heights2,grid,size,1,0)
    elif t == 2:
        #steps
        gridSteps(heights,grid,size,1,0)

def plinth_grid(heights_in,grid_in):
    rows = []
    for i in range(grid_in):
        temp_row = []
        for j in range(grid_in):
            temp_row += [heights_in[grid_in*i+j]]
            temp_row += [heights_in[grid_in*i+j]]
        rows += [temp_row]
    grid_out = grid_in*2 + 2
    heights_out = [0.0]*grid_out
    for i in range(grid_in*2):
        heights_out += [0.0] + rows[i//2] + [0.0]
    heights_out += [0.0]*grid_out
    
    return heights_out, grid_out

def setupVariableGrid(g,h,t):
    #creates random terrain
    grid = g
    size = 1.001 #temp change should be 1
    heights = randomHeights(0,h,grid) 
    if t == 1:
        #slopes
        heights2,grid = zeroEdge(heights,grid)
        callHeightField(heights2,grid,size,1,0)
    elif t == 2:
        #steps
        gridSteps(heights,grid,size,1,0)
    elif t == 3:
        heights2,grid = plinth_grid(heights,grid)
        callHeightField(heights2,grid,size,1,0)
    return heights
        


def setupTerrain10(t,n,pos_x,pos_y):
    grid = 5
    size = 1
    #heights = randomHeights(0,h,grid) 
    if t == 1:
        heights2,grid = zeroEdge(slope_heights[n],grid)
        callHeightField(heights2,grid,size,pos_x,pos_y)
    elif t == 2:
        gridSteps(step_heights[n],grid,size,pos_x,pos_y)
    else:
        callSingleStep(0,size,pos_x,pos_y)

def setupMap(grid_size, tile_list):
    for x in range(grid_size):
        for y in range(grid_size):
            [t,n] = tile_list[x][y]
            setupTerrain10(t,n,x,y)

def randomMap(grid_size):
    tile_list = []
    for x in range(grid_size):
        current_row = []
        for y in range(grid_size):
            t,n = randint(1,4),randint(0,4)
            current_row += [[t,n]]
        tile_list += [current_row]

    tile_list[0][0] = [0,0]
    tile_list[-1][-1] = [0,0]
    return tile_list
        
def make_steps(height,grid_size,pos_x,pos_y):
    step_heights = make2d(heights4steps(height,grid_size),grid_size)
    size = 1
    gridSteps(step_heights,grid_size,size,pos_x,pos_y)

def make_flattop_slope(height,slope_length,pos_x,pos_y):
    size = 1
    heights, grid_size = flattop_slope(height, slope_length)
    heights = make2d(heights,grid_size)
    callHeightField(heights,grid_size,size,pos_x,pos_y)

def make_doubleSlope(slope1,slope2,pos_x,pos_y):
    size = 1
    heights, grid_size, total = double_slope(slope1,slope2)
    heights = make2d(heights,grid_size)
    callHeightField(heights,grid_size,size,pos_x,pos_y)

def make_curvedStep(step,radius,topOrbot,pos_x,pos_y):
    size = 1
    heights, grid_size = curvedStepConverter(step,radius,topOrbot)
    heights = make2d(heights,grid_size)
    callHeightField(heights,grid_size,size,pos_x,pos_y)

def simpleObstacle(t,h):
    size = 1
    err, EndTile = vrep.simxGetObjectHandle(clientID, "Endtile", vrep.simx_opmode_blocking)
    if t == 1:
        #slopes
        grid = 3
        heights = [0,h/2,h]*3
        callHeightField(heights,grid,size,1,0)
    elif t == 2:
        #steps
        heights = [h]
        gridSteps(heights,1,size,1,0)
    vrep.simxSetObjectPosition(clientID,EndTile,-1,[2,0,h-0.05],vrep.simx_opmode_oneshot)

def make2Dfrom1D(heights,t,x,y):
    #Given a 1D set of height makes a 3D obstacle
    #types 1:slopes, 2:steps, 3:plinths
    grid = len(heights)
    size = 1
    if t == 3:
        grid *= 2
        heights = [heights[i//2] for i in range(grid)]
    heights = [[heights]]*grid
    if t == 1 or t == 3:
        #slopes
        heights,grid = zeroEdge(heights,grid)
        callHeightField(heights,grid,size,1,0)
    elif t == 2:
        #steps
        gridSteps(heights,grid,size,1,0)
        
       

def calibrate10tiles(heights,t):
    #creates random terrain
    grid = 5
    size = 1
    if t == 1:
        #slopes
        heights2,grid = zeroEdge(heights,grid)
        callHeightField(heights2,grid,size,1,0)
    elif t == 2:
        #steps
        gridSteps(heights,grid,size,1,0)

def tileCheckerBoard():
    #random order of tiles l = [[i//5,i%5] for i in range(5,15)], random.shuffle(l)
    r = [[1, 4], [1, 1], [1, 0], [2, 1], [2, 4], [2, 3], [2, 2], [1, 3], [2, 0], [1, 2]]
    z = [0,0]
    full_list = [[z,z,r[0],z,z],[z,r[1],z,r[2],z],[r[3],z,r[4],z,r[5]],[z,r[6],z,r[7],z],[z,z,r[8],z,z]]
    return full_list

if __name__ == "__main__":
    print ('Program started')
    #used for testing this library on its own
    vrep.simxFinish(-1) # just in case, close all opened connections
    clientID=vrep.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP
    #checks error in connection
    if clientID != -1:
        pass
    
        
    else:
        print ('Failed connecting to remote API server')
    
        
    print ('Program ended')



