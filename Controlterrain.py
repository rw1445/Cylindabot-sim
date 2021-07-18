# interace for controlling a cylindabot in vrep


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

from math import *
from numpy import *
from time import sleep
import csv
from datetime import datetime

from createterrain2 import *

sign = lambda x: copysign(1, x)

obstacles_names = [["Easy_slopes","Medium_slopes","Hard_slopes","Pyramid_egypt","Pit"],
                  ["Easy_steps","Medium_steps","Hard_steps","Pyramid_aztec","Walls"]]

#keeps a global time when position was last read
current_time = 0


def setupHandles():
    global Step,Left_Motor, Right_Motor, R_limb_B, R_limb_G, R_limb_R, L_limb_B, L_limb_G, L_limb_R, Tail, Main_orientation

    #get handles of the different parts of robot
    
    #main left and right motors for the wheels
    err, Left_Motor = vrep.simxGetObjectHandle(clientID, "Left_motor", vrep.simx_opmode_blocking)
    err, Right_Motor = vrep.simxGetObjectHandle(clientID, "Right_motor", vrep.simx_opmode_blocking)

    #limbs on right wheel colour coded RGB
    err, R_limb_B = vrep.simxGetObjectHandle(clientID, "R_leg1motor", vrep.simx_opmode_blocking)
    err, R_limb_G = vrep.simxGetObjectHandle(clientID, "R_leg2motor", vrep.simx_opmode_blocking)
    err, R_limb_R = vrep.simxGetObjectHandle(clientID, "R_leg3motor", vrep.simx_opmode_blocking)

    #limbs on left wheel, colour coded RGB
    err, L_limb_B = vrep.simxGetObjectHandle(clientID, "L_leg1motor", vrep.simx_opmode_blocking)
    err, L_limb_G = vrep.simxGetObjectHandle(clientID, "L_leg2motor", vrep.simx_opmode_blocking)
    err, L_limb_R = vrep.simxGetObjectHandle(clientID, "L_leg3motor", vrep.simx_opmode_blocking)

    #tail handle
    err, Tail = vrep.simxGetObjectHandle(clientID, "Tail_motor", vrep.simx_opmode_blocking)

    #sensor handles

    err, Main_orientation = vrep.simxGetObjectHandle(clientID, "Cylindabot", vrep.simx_opmode_blocking)

    
    print("Handle setup")
    
    

def setWheelSpeed (l_speed, r_speed):
    #sets the speed of the wheels
    vrep.simxSetJointTargetVelocity(clientID, Left_Motor, -r_speed, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetVelocity(clientID, Right_Motor, l_speed, vrep.simx_opmode_oneshot)

def setRightLegs (angle):
    #sets the position of the Right legs
    angle = angle*pi/180
    vrep.simxSetJointTargetPosition(clientID, R_limb_B, angle, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetPosition(clientID, R_limb_G, angle, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetPosition(clientID, R_limb_R, angle, vrep.simx_opmode_oneshot)

def setLeftLegs (angle):
    #sets the position of the Left legs
    #0 = start position, 130 = fully out
    angle = angle*pi/180
    vrep.simxSetJointTargetPosition(clientID, L_limb_B, angle, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetPosition(clientID, L_limb_G, angle, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetPosition(clientID, L_limb_R, angle, vrep.simx_opmode_oneshot)

def setAllLegs (angle):
    setLeftLegs (angle)
    setRightLegs (angle)
    
def setTail (position):
    vrep.simxSetJointTargetPosition(clientID, Tail, position, vrep.simx_opmode_oneshot)

def getDistanceData ():
    #not sure what this returns yet
    print(vrep.simxReadProximitySensor(clientID, Laser_front_left, vrep.simx_opmode_streaming))
    #vrep.simxReadProximitySensor(clientID, Laser_front_right, vrep.simx_opmode_streaming)
    #vrep.simxReadProximitySensor(clientID, Laser_side_right, vrep.simx_opmode_streaming)
    print(vrep.simxReadProximitySensor(clientID, Laser_back_right, vrep.simx_opmode_streaming))
    #vrep.simxReadProximitySensor(clientID, Laser_back_left, vrep.simx_opmode_streaming)
    #vrep.simxReadProximitySensor(clientID, Laser_side_left, vrep.simx_opmode_streaming)

def euler2matrix(ang_x,ang_y,ang_z,shouldRound = False):
    #Matrix of rotation off these angles from wikipedia
    ang_matrix = [[cos(ang_y)*cos(ang_z), -cos(ang_x)*sin(ang_z)+sin(ang_x)*sin(ang_y)*cos(ang_z), sin(ang_x)*sin(ang_z)+cos(ang_x)*sin(ang_y)*cos(ang_z)],
              [cos(ang_y)*sin(ang_z), cos(ang_x)*cos(ang_z)+sin(ang_x)*sin(ang_y)*sin(ang_y), -sin(ang_x)*cos(ang_z)+cos(ang_x)*sin(ang_y)*sin(ang_z)],
              [-sin(ang_y), sin(ang_x)*cos(ang_y), cos(ang_x)*cos(ang_y)]]

    #for debuging rounding the numbers is useful
    if shouldRound:
        new_matrix = []
        for r in ang_matrix:
            new_r = []
            for v in r:
                new_r += [round(v,5)]
            new_matrix += [new_r]
        return new_matrix
    else:
        return ang_matrix

def getRobotOrientation ():
    err, [ang_x, ang_y, ang_z] = vrep.simxGetObjectOrientation(clientID, Main_orientation, -1, vrep.simx_opmode_streaming)
    if err == 0:
        #converts the matrix into a list of the vector of each axis
        ang_matrix = array(euler2matrix(ang_x,ang_y,ang_z))
        [x_dir, y_dir, z_dir] = ang_matrix.transpose()
        #print ([x_dir, y_dir, z_dir])
        
        #works out the compass direction relative the the y-axis
        compass = degrees(atan2(x_dir[1],x_dir[0]))

        inverted = sign(z_dir[2])
        
        return  compass,inverted
    else:
        print("orientation error")
        return 0,0


def getRobotPositionTime ():
    #gets the current position and simulation time
    global current_time
    gotReading = 0
    while not gotReading:
        err, pos = vrep.simxGetObjectPosition(clientID, Main_orientation, -1, vrep.simx_opmode_streaming)
        gotReading = not err

    gotTime = 0
    current_time = vrep.simxGetLastCmdTime(clientID)
    
    return pos, current_time

def testPosition():
    #test where the robot is and current time to end simulation
    global result
    pos, current_time = getRobotPositionTime()
    if abs(pos[0] - 2) < 0.5 and abs(pos[1]) < 0.5:
        result = "Success"
        return 0
    elif pos[0] == nan:
        result = "Physics Error"
        return 0
    #time out after 10 seconds
    elif pos[2] < -5:
        result = "Fall"
    elif current_time > 30000:
        result = "Time out"
        return 0
    else:
        return 1

data = []

def saveTestRun(if_tail,leg_angle,speed,height):
    global result, current_time, data
    data += [[result, current_time, if_tail,leg_angle,speed,height]]

def headForPoint(speed,target_pos = [2,0,0]):
    compass,inverted = getRobotOrientation ()
    
    #code for heading for a point rather than a direction
    pos, time = getRobotPositionTime ()

    target_pos = [2,0,0]

    target_angle = degrees(atan2(target_pos[1]-pos[1],target_pos[0] - pos[0]))

 
    compass = compass - (inverted * target_angle)
    #compass = compass + target_angle
    #subtracts wheel speed to direct the robot in the right direction
    
    if compass > 0:
        right_speed = speed 
        left_speed = speed - min(speed*2,speed*compass/45)
    else:
        right_speed = speed - min(speed*2,-speed*compass/45)
        left_speed = speed 
    if inverted == 1:
        setWheelSpeed(-left_speed,-right_speed)
    else:
        setWheelSpeed(left_speed,right_speed)
    

def single_test(t,h,leg_angle,tail,g=1):
    global current_time,heights_l
    #set up simulation time and robot conditions
    speed = 3
    current_time = 0
    setAllLegs(leg_angle)
    setWheelSpeed(0,0)
    setTail(tail)

    
    #loop until the simulation starts
    running = 0
    while not running:
        running = not vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)

    sleep(1)
    #setupTerrain10(t,h,1,0)
    #heights_l=setupVariableGrid(g,h,t)
    simpleObstacle(t,h)
    #setupTerrainRandom(h,t)
    #calibrate10tiles(h,t)
    #print(g)
       
    # set the step height
    sleep(0.5)
    setWheelSpeed(0,0)
    #control loop for robot
    running_test = 1
    while running_test:
        sleep(0.01)
        #test to see if simulation complete
        running_test = testPosition()
        #make the robot head towards obstacle
        headForPoint(speed)

    #stops the simulation
    while running:
        running = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)

    sleep(0.5)
    #add this test run to data
    #saveTestRun(if_tail,leg_angle,speed,round(1000*pos[2]-150))
    #sleep(1)
    #print("Run complete",leg_angle,data[-1],pos)
    return result

def one_run_beermat(t,leg_angle,tail = 0.025,grid_size = 5):
    global current_time, starting_h
    print("------------NEW RUN ---------------")
    obstacles = ['none','slopes','steps','plinths']
    print("Obstacle:",obstacles[t]," Leg Angle:",leg_angle," Tail:", tail, " Grid Size:",grid_size)

    
    fails = 0
    h = 0.05
    while fails < 10:
        result = single_test(t,h,leg_angle,tail,grid_size)
        if result != "Success":
            fails += 1
            print("First failure at " + str(h))
            h-=0.01
        else:
            h += 0.01
        print(h,"hieght")

    target_successes = 100
    successes = 0
    while successes < target_successes:
        result = single_test(t,h,leg_angle,tail, grid_size)
        if result == "Success":
            successes += 1
            print("Success at " + str(h)+" Total: "+str(successes)+"/"+str(target_successes))
            with open("data/grid size 2/Simple obstacle Beermat"+obstacles[t]+" Legangle"+str(leg_angle)+"Tail"+str(tail)+"Grid"+str(grid_size)+" Update robot Apr21.csv", 'a') as f:
                line = str(round(h,4))+","+str(current_time)+","+str(heights_l)[1:-1]+"\n"
                f.write(line)
            h +=0.001
        else:
            print("Fail at " + str(h))
            h -=0.001


def test_tile(t,n,start_angle = 0):
    for leg_angle in range(start_angle,140,10):
        print("Leg Angle = "+str(leg_angle))
        for i in range(20):
            #setupConnection()
            name = obstacles_names[t-1][n]
            result=single_test(t,n,leg_angle,0.025)
            if result == "Success":
                print("Success on " +name+" Total: "+str(i)+"/20")
                line = str("Success,"+str(current_time)+"\n")
            elif result == "Fall":
                print("Fall on " +name+" Total: "+str(i)+"/20")
                line = str("Fall,"+str(current_time)+"\n")
            else:
                print("Timeout at " +name+" Total: "+str(i)+"/20")
                line = str("Timeout,"+str(current_time)+"\n")
            
            with open("data/test tiles new/"+name+"/Tile test "+name+" Legangle"+str(leg_angle)+" new robot t315 Sep20.csv", 'a') as f:
                  f.write(line)
    
    
def setupConnection():
    global clientID
    vrep.simxFinish(-1) # just in case, close all opened connections
    clientID=vrep.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP
    print("Client started")
    setupHandles()
    if clientID == -1:
        print ('Failed connecting to remote API server')

if __name__ == "__main__":
    print ('Program started')
    
    setupConnection()
    #test_tile(2,4)

    #single_test(1,0.01,70,0.025,4)
    a = 130
    t = 1
    
    t = 3
    #for g in range(1,10):
        #one_run_beermat(t,a,0.025,g)
    

    #hieghts = randomHeights(0,0.08,5)
    #single_test(2,hieghts,80,0.025)
    
    '''
    #test_tile(1,4,40)
    for a in [0,70,130]:
        for t in range (1,4,1):
            for g in range(1,10,1):
                one_run_beermat(t,a,0.025,g)
    
    '''
    print ('Program ended')

'''
def chanceOnTerrain(heights,t):
    count = 0
    for leg_angle in range(0,140,10):
        result=single_test(t,heights,leg_angle,0.025)
        if result == "Success":
            count +=1
        print(result,leg_angle,t)
    print("Successes:",count)
    return count/14
        
def calibrate_tiles(difficulty,t,h0):
    #difficulty = [1,0.7,0.3][difficulty]
    found = 0
    h = h0
    while not found:
        heights = [h, h, h, h, h, h, 0.0, 0.0, 0.0, h, h, 0.0, 0.0, 0.0, h, h, 0.0, 0.0, 0.0, h, h, h, h, h, h]
        chance = chanceOnTerrain(heights,t)
        if chance < difficulty:
            found = 1
            print ("Found heights for ",difficulty," with h = ",h)
            print (heights)
        else:
            print (h," too easy")
        h += 0.01
    return h

'''
