'''

type of two parameter obstacles

1) steps = number of steps, total height
2) slope steps = slope length, height of step
3) curved step = step height, radius of curve
- curve at top
- curve at bottom
- curve at both
4) two slopes = height of two slopes
5) curved slope


'''

from math import sqrt

def make2d(heights, grid_size):
    return heights*grid_size

def heights4steps(height, number):
    heights = [height*(i+1) for i in range(number)]
    return heights

def flattop_slope(height, slope_length):
    grid_size = 51
    flat_length = grid_size - slope_length
    jump = height/slope_length
    heights = [jump*i for i in range(slope_length)] +[height]*flat_length
    return heights, grid_size

def double_slope(slope1,slope2):
    grid_size=11
    height = 0
    heights = []
    for i in range(grid_size):
        heights += [height]
        if i%2 == 0:
            height += slope1
        else:
            height += slope2
    total = height - slope1
            
    return heights, grid_size, total

def curvedStepConverter(step_m, radius, topOrbot):
    step_2cm = step_m*50
    if topOrbot == 1:
        heights_2cm, grid_size=curvedtop_step(step_2cm,radius)
    else:
        heights_2cm, grid_size=curvedbottom_step(step_2cm,radius)
    heights = [h/50 for h in heights_2cm]

    return heights, grid_size

def curvedtop_step(step,radius):
    heights = [0]
    grid_size = 51
    for i in range(radius+1):
        h = step - radius + sqrt(radius**2-(radius-i)**2)
        heights += [h]
    heights += [step]*(grid_size-radius -2)
    return heights, grid_size



def curvedbottom_step(step,radius):
    heights = [0]
    grid_size = 51
    for i in range(radius+1):
        h = radius - sqrt(radius**2-(i)**2)
        heights += [h]
    heights += [step]*(grid_size-radius -2)
    return heights, grid_size

#doesnt work
def smoothing_slopes1D(data):
    new_heights = []
    data_len = len(data)
    if data_len < 4:
        print("data too short")
    else:
        new_heights += find_smooth(0,data[0],data[1],data[2])
        for i in range(data_len-3):
            new_heights += find_smooth(data[i],data[i+1],data[i+2],data[i+3])
        new_heights += find_smooth(data[-3],data[-2],data[-1],0)
        new_heights += [data[-1]]

    return new_heights, data_len*3-5
        

from math import tanh

def find_smooth(y1,y2,y3,y4):
    
    effect1 = tanh(2*y2-y1-y3)
    effect2 = tanh(2*y3-y2-y4)

    d = (y3-y2)/3
    p1 = y2+d*(1+effect1)
    p2 = y3-d*(1-effect2)
    
    return [y2, p1, p2]

'''
def find_cubic(h1,h2,d1,d2,n):
    #y = ax^3+bx^2+cx+d
    d = h1
    c = d1
    b = -3*h1+3*h2-2*d1-d2
    a = d1+d2+2*h1-2*h2
    f = lambda x : a*x**3+b*x**2+c*x+d
    heights = [h1]
    for i in range(1,n+1):
        heights += [f(i/n+1)]
    heights += [h2]
    
    return heights

    '''
    

    
    
