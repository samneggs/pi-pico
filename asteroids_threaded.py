from LCD_1inch14 import LCD_1inch14
from machine import Pin,SPI,PWM, Timer, reset, WDT
import framebuf, math
import utime
from random import randint, randrange
from sys import exit
import _thread, array
import gc, micropython


class Point():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.ax = 0
        self.ay = 0
        self.c = 0
        self.exp = 0
        self.deg = 0
        self.active = 0

class Ship():
    def __init__(self,ptdeg,ptrad,pts,tumble,x,y,size):
        self.x = x # 230000 
        self.y = y # 125000 
        self.ax = randint(-40,40)*10 # accel x
        self.ay = randint(-40,40)*10 # accel y 
        self.deg = 0                 # degrees obj is pointing
        self.size = size             # size of obj
        self.coll = self.size*5      # collision h and w
        self.exp = 0                 # explode progression
        self.damage = True           # ship can take damage
        self.pt = []                 # active points
        self.ptrad = ptrad           # radius - points
        self.ptdeg = ptdeg           # degrees - points
        self.pts = pts               # number of points
        self.tumble = tumble         # degress added for tumbling
        self.active = True           # show on screen, move...
        
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
LCD = LCD_1inch14()

r= [-3,-2,-1,1,2,3] # tumble, removed zero
m = []              # missile point list
p = []              # point list
a = []              # asteroid point list
e = []              # explode point list
asteroid = []       # big asteroids
t=[]                # title letters
let_rad= []         # intro letters radii
let_deg= []         # intro letters degrees
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



token = 1      # 1 is show
gticks = 0
rfire = 0
threaded = False
num_asteroids=4 # number of asteroids to start
active_asteroids = num_asteroids
asteroid_count = 0
explode_clean_token = False

isin=array.array('i',range(0,361))
icos=array.array('i',range(0,361))
shades=array.array('i',range(0,32))

def init_shades():
    for i in range(0,32):        
        c=i<<11|i<<6|i       # red shifted 11 bits, green shifted 6,  blue
        shades[i]=c>>8|c<<8  # swap low and high bytes
#         LCD.fill_rect(i*7,0,7,100,shades[i])
#     LCD.show()
#     exit()    


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
        isin[i]=int(math.sin(math.radians(i))*10000)
        

def init_icos():            # integer cos lookup table 
    for i in range(0,361):
        icos[i]=int(math.cos(math.radians(i))*10000)
     
def init_title():
    for i in range(0,9):
        t.append(init_obj(let_deg[i],let_rad[i],len(let_deg[i]),1,10000+i*26000,50000,1000))
        t[i].ax=0
        t[i].ay=0
        draw_object(t[i])             # draw letters
    LCD.show()
    for i in range(0,100000):     # pause 
        pass
    while (key0.value() != 0):
        for i in t:
            draw_object(i)
        LCD.show()
    for i in t:
        init_explode(i,50,1)
        while i.exp<10:
            explode()           
            LCD.show()
            i.exp+=1
        explode_cleanup()
        i.size=0
        draw_object(i)
    LCD.fill(LCD.black)
    
#@timed_function
def init_obj(ptdeg,ptrad,pts,tumble,x,y,size):
    obj = Ship(ptdeg,ptrad,pts,tumble,x,y,size)                    #reset obj
    for i in range(0,obj.pts*3):
        obj.pt.append(Point())
    return obj


def init_asteroids():
    global num_asteroids
    for j,i in enumerate(range(0,20)): #num_asteroids):   
        asteroid.append(init_obj([0,60,120,180,240,300,0],[7]+[randint(6,9) for _ in range(5)]+[7],7,r[randint(0,5)],randint(10000,230000),randint(10000,125000),3000))
        if j>=num_asteroids:
            asteroid[j].active = False

def more_asteroids():
    global num_asteroids, asteroid_count
    for i in range(0,num_asteroids): #num_asteroids):
        asteroid[i].active = True
        asteroid[i].x = randint(10000,230000)
        asteroid[i].y = randint(10000,125000)
        asteroid[i].size = 3000
        asteroid[i].coll = asteroid[i].size*5
        asteroid[i].tumble = r[randint(0,5)]
        asteroid[i].exp = 0
    asteroid_count=num_asteroids

def new_ship():
    ship.exp = 0
    ship.x = randint(10000,230000)
    ship.y = randint(10000,125000)
    ship.ax = 0
    ship.ay = 0
    ship.damage=False
    tim.init(mode=Timer.ONE_SHOT, period=2000, callback=no_damage)


def init_missiles():
    for i in range(0,10):
        m.append(Point())

def init_explosion():
    for i in range(0,90):
        e.append(Point())

def line(x1,y1,x2,y2,color):
    LCD.line(x1//1000,y1//1000,x2//1000,y2//1000,color)

def pixel(x,y,color):
    LCD.pixel(int(x//1000),int(y//1000),color) 

#@timed_function
def draw_object(obj):
    global token
    token = 0
    for i in range(0,obj.pts-1):
        line(obj.pt[i].x,obj.pt[i].y,obj.pt[i+1].x,obj.pt[i+1].y,LCD.black) # erase old obj
    if (obj.exp == 0 and obj.tumble==0) or (obj.size>0 and obj.tumble!=0):  # ship not exploding or asteroid alive 
        move_object(obj)
        if ship.damage==False:
            c=LCD.red
        else:
            c=LCD.green
        for i in range(0,obj.pts-1):
            line(obj.pt[i].x,obj.pt[i].y,obj.pt[i+1].x,obj.pt[i+1].y,c) # draw new obj
    token = 1

#@timed_function
def slow_ship():
    if ship.ax > 0:                         # slow ship down automatically 
        ship.ax=ship.ax - 5
    if ship.ay > 0:
        ship.ay=ship.ay - 5
    if ship.ax < 0:
        ship.ax=ship.ax + 5
    if ship.ay < 0:
        ship.ay=ship.ay + 5
    if ship.ax < 5 and ship.ax > -5:  # if very slow then stop
        ship.ax = 0
    if ship.ay < 5 and ship.ay > -5:
        ship.ay = 0

#@timed_function
def move_object(obj):
    if not obj.active:
        return
    obj.x+=obj.ax                   # add accel to x,y
    obj.y+=obj.ay
        
    if obj.x > 240000:                 # wrap around if out of bounds
        obj.x = 0
    if obj.x < 0:
        obj.x = 240000
    if obj.y > 135000:
        obj.y = 0
    if obj.y < 0:
        obj.y = 135000
    obj.deg+=obj.tumble             # add tumble to deg
    if obj.deg>359:
        obj.deg-=360
    if obj.deg<0:
        obj.deg+=360

    for i in range(0,obj.pts):                      # go through all points of obj        
        deg=int(obj.deg+obj.ptdeg[i])
        if deg>359:
            deg-=360
        obj.pt[i].x=int(obj.ptrad[i]*obj.size*icos[deg]//10000+obj.x) # calc x,y from deg,radius
        obj.pt[i].y=int(obj.ptrad[i]*obj.size*isin[deg]//10000+obj.y)


#@timed_function
def thrust():
    ship.ax=ship.ax+icos[ship.deg]//150   # add accel in direction ship is pointed
    ship.ay=ship.ay+isin[ship.deg]//150
    

#@timed_function
def buttons():
    global rfire,threaded
    if(key0.value() == 0):             # rotate ship CW
        ship.deg+=6-(2*threaded)
        if ship.deg>359:
            ship.deg=0
    if(key1.value() == 0):             # rotate ship CCW
        ship.deg-=6-(2*threaded)
        if ship.deg<0:
            ship.deg=359
    if(key2.value() == 0):
        thrust()
    if(key3.value() == 0) and ship.damage:              
        rfire+=1
        if rfire == 8+(8*threaded):
            rfire=0
            fire()
    if(key0.value() == 0) and (key1.value() == 0): # reboot if frozen
        reset()


#@timed_function   
def fire():
    for i in m:
        if i.active == False:
            i.active = True
            i.x=ship.pt[0].x                   # start missile at tip of ship
            i.y=ship.pt[0].y
            i.ax=ship.ax+icos[ship.deg]//10*3  # missile accel of ship + 3x
            i.ay=ship.ay+isin[ship.deg]//10*3
            return
    

def spawn_asteroid(objs,last):     # find next free object in list
    i = last
    while True:
        if i==len(objs)-1:  # end of the list?
            i = 0           # start over
        else:
            i +=1           # next index
        if objs[i].active == False:
            objs[i].active = True
            objs[i].x = objs[last].x+randint(-2000,2000)
            objs[i].y = objs[last].y+randint(-2000,2000)
            objs[i].size = objs[last].size
            objs[i].coll = objs[i].size*5
            objs[i].exp = 0
            return

#@timed_function
def move_miss_new():
    global asteroid_count
    for i in range(0,10):
        if m[i].active and m[i].x >-1000 and m[i].x<241000 and m[i].y>-1000 and m[i].y<136000:    # check miss inbounds
            LCD.pixel(int(m[i].x//1000),int(m[i].y//1000),LCD.black)              # erase old miss 
#            pixel(m[i].x,m[i].y,LCD.black)                                       # erase old miss 
            m[i].x=m[i].x+m[i].ax                                                 # calc new miss
            m[i].y=m[i].y+m[i].ay
            LCD.pixel(int(m[i].x//1000),int(m[i].y//1000),LCD.white)              # draw new miss
            asteroid_count = 0
            for j in range(0,len(asteroid)-1):                                      # loop thought asteroid list
                asteroid_count+=(asteroid[j].active==True)
                if asteroid[j].active and m[i].x < asteroid[j].x+asteroid[j].coll and m[i].x > asteroid[j].x-asteroid[j].coll and m[i].y < asteroid[j].y+asteroid[j].coll and m[i].y > asteroid[j].y-asteroid[j].coll and asteroid[j].size>0 : # check collision
                    LCD.pixel(int(m[i].x//1000),int(m[i].y//1000),LCD.black)
                    asteroid[j].size-=1000
                    asteroid[j].coll-=3
                    spawn_asteroid(asteroid,j)
                    explode_clean_token = True
                    #explode_cleanup()
                    init_explode(asteroid[j],20,3)
                    asteroid[j].exp=0
                    m[i].active = False
        else:
            m[i].active = False


#@timed_function
def move_asteroid():  
    for i in range(0,len(asteroid)):  # go through list of asteroids
        if asteroid[i].active:
            draw_object(asteroid[i])   # draw/move
            if ship.damage and ship.exp == 0 and ship.x < asteroid[i].x+asteroid[i].coll and ship.x > asteroid[i].x-asteroid[i].coll and ship.y < asteroid[i].y+asteroid[i].coll and ship.y > asteroid[i].y-asteroid[i].coll and asteroid[i].exp == 0:
                ship.exp = 1                                    # asteroid collide with ship
            if asteroid[i].size<1000: # and len(e) == 0:
                asteroid[i].active = False
    
 
#@timed_function
def init_explode(objhit,n,s):  # obj, number, speed
    for i in range(0,n):
        LCD.pixel(int(e[i].x//1000),int(e[i].y//1000),LCD.black)
        e[i].active = True
        e[i].x=objhit.x
        e[i].y=objhit.y
        e[i].ax = objhit.ax+randint(-1000,1000)*10//s
        e[i].ay = objhit.ay+randint(-1000,1000)*10//s

#@timed_function
def explode():
    for i in range(0,len(e)):
        if e[i].active:
            if e[i].x >-1000 and e[i].x<241000 and e[i].y>-1000 and e[i].y<136000 and e[i].exp<51:
                LCD.pixel(int(e[i].x//1000),int(e[i].y//1000),LCD.black)
                e[i].x=int(e[i].x+e[i].ax)
                e[i].y=int(e[i].y+e[i].ay)
                color=LCD.white
                if e[i].exp>20:
                    color=shades[51-e[i].exp]
                LCD.pixel(int(e[i].x//1000),int(e[i].y//1000),color)
                e[i].exp+=1
            else:
                LCD.pixel(int(e[i].x//1000),int(e[i].y//1000),LCD.black)
                e[i].active = False
                e[i].exp=0

def explode_cleanup():
    for i in range(0,len(e)):
        if e[i].active or 0:
            LCD.pixel(int(e[i].x//1000),int(e[i].y//1000),LCD.black)
            e[i].active = False
            e[i].exp=0

def watchdog(timer):
    if(key0.value() == 0) and (key1.value() == 0): # reboot if frozen
        reset()


def no_damage(timer):
    ship.damage = True
    

def show_display():      
    micropython.alloc_emergency_exception_buf(100)
    global token,explode_clean_token
    print('core 1')
    while True:
        if True:
            if explode_clean_token:
                explode_clean_token = False
                explode_cleanup()
            explode()
            buttons()
            LCD.show()

if __name__=='__main__':
    micropython.alloc_emergency_exception_buf(100)
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

    ship=init_obj([0,140,220,0],[3,3,3,3],4,0,randint(10000,230000),randint(10000,125000),3000)
    init_explosion()    
#    init_title()
    init_asteroids()
    init_missiles()
    tim = Timer()       #set the no damage timer
    gc.collect()
    init_shades()
    wdt=machine.WDT(id=0, timeout=8000)
    
    if threaded:
        _thread.start_new_thread(show_display, ())


    try:
        while(1):
            while token == 0 or 1:
                if asteroid_count==0:
                    more_asteroids()
                    num_asteroids+=1
                    ship.damage=False
                    tim.init(mode=Timer.ONE_SHOT, period=2000, callback=no_damage)
                if ship.exp >100               : # explosion done
                    explode_clean_token = True
    #                explode_cleanup()
                    new_ship()
                move_asteroid() 
                draw_object(ship)
                slow_ship()
                move_miss_new()
                if ship.exp == 1:                # 1=init
    #                explode_clean_token = True
    #                explode_cleanup()
                    init_explode(ship,90,5)
                    ship.exp = 2
                if ship.exp > 1:                # 2+=exploding
                    #explode()
                    ship.exp+=1
                if token == 1 and not threaded:
                    move_asteroid()                  # move big asteroid
                    buttons()
                    if explode_clean_token:
                        explode_clean_token = False
                        explode_cleanup()
                    explode()
                    LCD.show()     
                delta = utime.ticks_diff(utime.ticks_us(), gticks)
                gticks = utime.ticks_us()
                fps=1_000_000//delta          # frames per second
                #print(gc.mem_free())
                #print(fps)
                #token = 1
                wdt.feed()
        
            
    except KeyboardInterrupt:
#        tim2.deinit()
        print('fps=',fps)
        print('asteroids:         ',len(asteroid),asteroid[0].x,asteroid[0].y, asteroid[0].pt[0].x,asteroid[0].pt[0].y,asteroid[0].ptdeg,asteroid[0].ptrad,asteroid[0].size)
        print('asteroid coll,exp: ',asteroid[0].coll,asteroid[0].exp)
        print('ship size,active:  ',ship.size,ship.active)
        print('explosion:         ',len(e))
        print('ship damage,exp:   ',ship.damage,ship.exp)
        print('mem free:          ',gc.mem_free())
        _thread.exit()
#     except IndexError:
#         print(len(asteroid),len(m),len(e))
        
        

