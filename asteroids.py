from LCD_1inch14 import LCD_1inch14
from machine import Pin,SPI,PWM, Timer
import framebuf, math
import utime
from random import randint, randrange
from sys import exit
import _thread, array
import gc


class Point():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.ax = 0
        self.ay = 0
        self.c = 0
        self.exp = 0

class Ship():
    def __init__(self,ptdeg,ptrad,pts,tumble,x,y,size):
        self.x = x #randint(10,230)
        self.y = y #randint(10,125) 
        self.ax = randint(-2,2)/5
        self.ay = randint(-2,2)/5
        self.deg = 0
        self.size = size
        self.coll = self.size*5
        self.exp = 0
        self.damage = True
        self.pt = []
        self.ptrad = ptrad   # radius - points
        self.ptdeg = ptdeg   # degrees - points
        self.pts = pts       # number of points
        self.tumble = tumble # degress added for tumbling
        
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
LCD = LCD_1inch14()

m = []         # missile point list
p = []         # point list
a = []         # asteroid point list
e = []         # explode point list
asteroid = []  # big asteroids
t=[]           # title letters
let_rad= []
let_deg= []
let_deg.append([54,270,126,90,54])                      # A
let_rad.append([17,18,17,4,17])
let_deg.append([306,270,234,54,90,126])                 # S
let_rad.append([17,18,17,17,18,17])
let_deg.append( [234, 306, 270, 90] )                   # T   
let_rad.append( [17, 17, 12, 14] )
let_deg.append( [306, 234, 0, 126, 54] )                # E
let_rad.append( [17, 17, 0, 17, 17] )
let_deg.append( [0, 306, 270, 234, 126, 191, 0, 60] )   # R
let_rad.append( [0, 17, 16, 17, 17, 10, 0, 16] )       
let_deg.append( [306, 270, 234, 126, 90, 54, 306] )     # O
let_rad.append( [17, 16, 17, 17, 16, 17, 17] )         
let_deg.append( [306, 270, 234, 270, 90, 54, 90, 126] ) # I
let_rad.append( [17, 16, 17, 14, 14, 17, 16, 17] )
let_deg.append( [234, 270, 0, 90, 126, 234] )           # D
let_rad.append( [17, 14, 10, 14, 17, 17] )
let_deg.append([306,270,234,54,90,126])                 # S
let_rad.append([17,18,17,17,18,17])



token = 0      # muli-thread nonesense
gticks = 0
rfire = 0
threaded = False
num_asteroids=3 # number of asteroids to start

isin=array.array('i',range(0,361))
icos=array.array('i',range(0,361))

def timed_function(f, *args, **kwargs):  # for timing defs
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def init_isin():            # integer sin lookup table    
    for i in range(0,361):
        isin[i]=int(math.sin(math.radians(i))*100000)
        

def init_icos():            # integer cos lookup table 
    for i in range(0,361):
        icos[i]=int(math.cos(math.radians(i))*100000)
     
def init_title():
    for i in range(0,9):
        t.append(init_obj(let_deg[i],let_rad[i],len(let_deg[i]),1,10+i*26,50,1))
        t[i].ax=0
        t[i].ay=0
        draw_object(t[i])
    while (key0.value() != 0):
        for i in t:
            draw_object(i)
        LCD.show()
    for i in t:
        init_explode(i,50,.5)
        while len(e)>5:
            explode()           
            LCD.show()
        explode_cleanup()
        i.size=0
        draw_object(i)
        #LCD.show()
    LCD.fill(LCD.black)
    

def init_obj(ptdeg,ptrad,pts,tumble,x,y,size):
    obj = Ship(ptdeg,ptrad,pts,tumble,x,y,size)                    #reset obj
    for i in range(0,obj.pts*3):
        obj.pt.append(Point())
    return obj

def init_ast():                      # old dot asteroids
    for i in range(0,6):             # 6 number of asteriod dots
        a.append(Point())
        a[i].x=randint(0,240)        # random location
        a[i].y=randint(0,135)
        a[i].ax=randint(-10,10)/30   # set speed
        a[i].ay=randint(-10,10)/30 

def init_asteroids():
    global num_asteroids
    for i in range(0,num_asteroids):   
        asteroid.append(init_obj([0,60,120,180,240,300,0],[7]+[randint(6,9) for _ in range(5)]+[7],7,randint(-3,3),randint(10,230),randint(10,125),3))

def draw_object(obj):
    global token
    token = 0
    for i in range(0,obj.pts-1):
        LCD.line(obj.pt[i].x,obj.pt[i].y,obj.pt[i+1].x,obj.pt[i+1].y,LCD.black) # erase old obj
    if (obj.exp == 0 and obj.tumble==0) or (obj.size>0 and obj.tumble!=0):
        move_object(obj)
        if ship.damage==False:
            c=LCD.red
        else:
            c=LCD.green
        for i in range(0,obj.pts-1):
            LCD.line(obj.pt[i].x,obj.pt[i].y,obj.pt[i+1].x,obj.pt[i+1].y,c) # draw new obj
    token = 1

def slow_ship():
    if ship.ax > 0:                         # slow ship down automatically 
        ship.ax=ship.ax - 0.01
    if ship.ay > 0:
        ship.ay=ship.ay - 0.01
    if ship.ax < 0:
        ship.ax=ship.ax + 0.01
    if ship.ay < 0:
        ship.ay=ship.ay + 0.01
    if ship.ax < 0.01 and ship.ax > -0.01:  # if very slow then stop
        ship.ax = 0
    if ship.ay < 0.01 and ship.ay > -0.01:
        ship.ay = 0


def move_object(obj):
    obj.x+=obj.ax                   # add accel to x,y
    obj.y=obj.y+obj.ay
    if obj.x > 240:                 # wrap around if out of bounds
        obj.x = 0
    if obj.x < 0:
        obj.x = 240
    if obj.y > 135:
        obj.y = 0
    if obj.y < 0:
        obj.y = 135
    obj.deg+=obj.tumble             # add tumble to deg
    if obj.deg>359:
        obj.deg-=360
    if obj.deg<0:
        obj.deg+=360

    for i in range(0,obj.pts):
#         rad=math.radians(obj.deg+obj.ptdeg[i])
#         obj.pt[i].x=int(obj.ptrad[i]*math.cos(rad)+obj.x)  # point i of obj
#         obj.pt[i].y=int(obj.ptrad[i]*math.sin(rad)+obj.y)
        
        deg=int(obj.deg+obj.ptdeg[i])
        if deg>359:
            deg-=360
        obj.pt[i].x=int(obj.ptrad[i]*obj.size*icos[deg]/100000+obj.x)   
        obj.pt[i].y=int(obj.ptrad[i]*obj.size*isin[deg]/100000+obj.y)



def thrust():
#     rad=math.radians(ship.deg)
#     ship.ax=ship.ax+math.cos(rad)/15   # add accel in direction ship is pointed
#     ship.ay=ship.ay+math.sin(rad)/15

    ship.ax=ship.ax+icos[ship.deg]/100000/15   # add accel in direction ship is pointed
    ship.ay=ship.ay+isin[ship.deg]/100000/15
    


def buttons():
    global rfire
    if(key0.value() == 0):             # rotate ship CW
        ship.deg+=5
        if ship.deg>359:
            ship.deg=0
    if(key1.value() == 0):             # rotate ship CCW
        ship.deg-=5
        if ship.deg<0:
            ship.deg=359
    if(key2.value() == 0):
        thrust()
    if(key3.value() == 0):              
        rfire+=1
        if rfire == 8:
            rfire=0
            fire()
   
def fire():
    if len(m)<10:            # number of missiles on screen
        m.append(Point())
        i=len(m)-1
        m[i].x=ship.pt[0].x              # start missile at tip of ship
        m[i].y=ship.pt[0].y
#         rad=math.radians(ship.deg)
#         m[i].ax=ship.ax+math.cos(rad)*2  # missile accel of ship + 2x
#         m[i].ay=ship.ay+math.sin(rad)*2
        m[i].ax=ship.ax+icos[ship.deg]/100000*3  # missile accel of ship + 3x
        m[i].ay=ship.ay+isin[ship.deg]/100000*3



def move_miss():  # !!! OLD !!!
    i=0                                                             # i index of missile m
    while len(m)>0 and i< len(m):                                   # have #miss and index<#miss
        if m[i].x >-1 and m[i].x<241 and m[i].y>-1 and m[i].y<136:  # check miss inbounds
            LCD.pixel(int(m[i].x),int(m[i].y),LCD.black)            # erase old miss 
            m[i].x=m[i].x+m[i].ax                                   # calc new miss
            m[i].y=m[i].y+m[i].ay
            LCD.pixel(int(m[i].x),int(m[i].y),LCD.white)            # draw new miss
            j=0                                                     # j index of asteroid a
            while len(a)>0 and j< len(a) and len(m)>0 and i<len(m): # have ast, indx<ast, have miss, indx<miss
                if m[i].x < a[j].x+3 and m[i].x > a[j].x-3 and m[i].y < a[j].y+3 and m[i].y > a[j].y-3 and a[j].exp == 0: # check collision
                    LCD.pixel(int(m[i].x),int(m[i].y),LCD.black)
                    LCD.pixel(int(a[j].x),int(a[j].y),LCD.black)
                    explode_cleanup()
                    init_explode(a[j],10,3)
                    a[j].exp=1
                    d=m.pop(i)   # delete missile                    
                j+=1
        else:
            d=m.pop(i)   # delete missile
        i+=1

def move_miss_new():
    i=0                                                             # i index of missile m
    while len(m)>0 and i< len(m):                                   # have #miss and index<#miss
        if m[i].x >-1 and m[i].x<241 and m[i].y>-1 and m[i].y<136:  # check miss inbounds
            LCD.pixel(int(m[i].x),int(m[i].y),LCD.black)            # erase old miss 
            m[i].x=m[i].x+m[i].ax                                   # calc new miss
            m[i].y=m[i].y+m[i].ay
            LCD.pixel(int(m[i].x),int(m[i].y),LCD.white)            # draw new miss
            j=0                                                     # j index of asteroid a
            while len(asteroid)>0 and j< len(asteroid) and len(m)>0 and i<len(m): # have ast, indx<ast, have miss, indx<miss
                if m[i].x < asteroid[j].x+asteroid[j].coll and m[i].x > asteroid[j].x-asteroid[j].coll and m[i].y < asteroid[j].y+asteroid[j].coll and m[i].y > asteroid[j].y-asteroid[j].coll and asteroid[j].size>0 : # check collision
                    LCD.pixel(int(m[i].x),int(m[i].y),LCD.black)
                    asteroid[j].size-=1
                    asteroid[j].coll-=3
                    asteroid.append(init_obj([0,60,120,180,240,300,0],[7,6,7,6,7,6,7],7,randint(-3,3),asteroid[j].x+randint(-20,20),asteroid[j].y+randint(-20,20),asteroid[j].size))
                    draw_object(asteroid[j])
                    explode_cleanup()
                    init_explode(asteroid[j],10,3)
                    asteroid[j].exp=1
                    d=m.pop(i)   # delete missile                    
                j+=1
        else:
            d=m.pop(i)   # delete missile
        i+=1


def move_ast():    # !!! OLD !!! move dot asteroids
    i=0
    while i<len(a):
        LCD.pixel(int(a[i].x),int(a[i].y),LCD.black)
        a[i].x=a[i].x+a[i].ax
        a[i].y=a[i].y+a[i].ay
        if ship.exp == 0 and ship.x < a[i].x+5 and ship.x > a[i].x-5 and ship.y < a[i].y+5 and ship.y > a[i].y-5 and a[i].exp == 0:
            ship.exp = 2
        if a[i].x<0:
            a[i].x=239
        if a[i].x>239:
            a[i].x=0
        if a[i].y<0:
            a[i].y=134
        if a[i].y>134:
            a[i].y=0        
        if a[i].exp == 0:
            LCD.pixel(int(a[i].x),int(a[i].y),LCD.white)
        else:
            explode()
            if len(e) == 0:
                d=a.pop(i)
        i+=1
        
def move_asteroid():    # move big asteroids
    i=0
    while i<len(asteroid):
        draw_object(asteroid[i])
        if ship.damage and ship.exp == 0 and ship.x < asteroid[i].x+asteroid[i].coll and ship.x > asteroid[i].x-asteroid[i].coll and ship.y < asteroid[i].y+asteroid[i].coll and ship.y > asteroid[i].y-asteroid[i].coll and asteroid[i].exp == 0:
            ship.exp = 2
        if asteroid[i].exp > 0:
            explode()
        if len(e) == 0 and asteroid[i].size<1:
            d=asteroid.pop(i)
        i+=1
 

def init_explode(objhit,n,s):  # obj, number, speed
    for i in range(0,n):
        e.append(Point())
        e[i].x=objhit.x
        e[i].y=objhit.y
        e[i].ax = objhit.ax+randint(-10,10)/s
        e[i].ay = objhit.ay+randint(-10,10)/s

def explode():    
    i=0
    while len(e)>0 and i< len(e):    
        if e[i].x >-1 and e[i].x<241 and e[i].y>-1 and e[i].y<136 and e[i].exp<100:
            LCD.pixel(int(e[i].x),int(e[i].y),LCD.black)
            e[i].x=int(e[i].x+e[i].ax)
            e[i].y=int(e[i].y+e[i].ay)
            LCD.pixel(int(e[i].x),int(e[i].y),LCD.white)
            e[i].exp+=1
        else:
            LCD.pixel(int(e[i].x),int(e[i].y),LCD.black)
            d=e.pop(i)    # delete explosion point
            i-=1
        i+=1
  
def explode_cleanup():
    while len(e)>0:
        LCD.pixel(int(e[0].x),int(e[0].y),LCD.black)
        d=e.pop(0)

def no_damage(timer):
    ship.damage = True
    

def show_display():       # crashes after few seconds
    global token
    while True:
        if True: # token == 1:
            LCD.show()
if threaded:
    _thread.start_new_thread(show_display, ()) # no bueno :(

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535
    LCD.fill(LCD.black) 
    
    key0 = Pin(15,Pin.IN)
    key1 = Pin(17,Pin.IN)
    key2 = Pin(2 ,Pin.IN)
    key3 = Pin(3 ,Pin.IN)
    
    init_isin() 
    init_icos()

    ship=init_obj([0,140,220,0],[3,3,3,3],4,0,randint(10,230),randint(10,125),3)
    init_title()
    tim = Timer()      #set the timer
    
    
    try:
        while(1):
            if len(asteroid)==0:             # no more asteroids
                init_asteroids()
                num_asteroids+=1
                ship.damage=False
                tim.init(mode=Timer.ONE_SHOT, period=2000, callback=no_damage)
            if ship.exp == 1 and len(e) < 5: # explosion done
                explode_cleanup()
                ship.exp = 0
                ship=init_obj([0,140,220,0],[3,3,3,3],4,0,randint(10,230),randint(10,125),3)
                tim.init(mode=Timer.ONE_SHOT, period=2000, callback=no_damage)
            buttons()
            draw_object(ship)
            move_asteroid()                  # move big asteroid
            slow_ship()
            move_miss_new()
            if ship.exp == 2:                # 2=init
                explode_cleanup()
                init_explode(ship,90,1)
                ship.exp = 1
            if ship.exp == 1:                # 1=exploding
                explode()
            if token == 1 and not threaded:
                LCD.show()     
            delta = utime.ticks_diff(utime.ticks_us(), gticks)
            gticks = utime.ticks_us()
            fps=1_000_000/delta          # frames per second
            #print(gc.mem_free())
            #print(fps)
        
            
    except KeyboardInterrupt:
        print('fps=',fps)
        print('asteroids',len(asteroid),asteroid[0].x,asteroid[0].y, asteroid[0].pt[0].x,asteroid[0].pt[0].y)
        print('asteroid size',asteroid[0].size)
        print('explosion',len(e))
        

