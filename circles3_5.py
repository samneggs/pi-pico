from LCD_3inch5 import LCD_3inch5
#from machine import Pin,SPI,PWM, Timer
from gc import mem_free,collect
import time
from random import randint
from usys import exit
import array
from math import sqrt
from micropython import const, mem_info

class Point():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.oldx = 0
        self.oldy = 0
        self.ax = 0
        self.ay = 0
        self.aax = 0
        self.aay = 0
        self.c = 0

class Circle():
    def __init__(self,x,y,r,c):
        self.x = x
        self.y = y
        self.r = r
        self.c = c

LCD = LCD_3inch5()
LCD.bl_ctrl(50)
LCD.FillRectangle(0,0,480,320,LCD.BLACK,True)
# LCD.fill(LCD.BLACK)
# LCD.show_up()
# LCD.show_down()
#print(mem_free())

c=[]
color_list = [LCD.RED,LCD.GREEN+2, LCD.BLUE]
XSCREEN_MAX= const(480)
YSCREEN_MAX= const(320)
XCENTER = const(XSCREEN_MAX//2)
YCENTER = const(YSCREEN_MAX//2)


def circle(x0, y0, radius,color):
    # From Adafruit GFX Arduino library
    # Circle drawing function.  Will draw a single pixel wide circle with
    # center at x0, y0 and the specified radius.
    f = 1 - radius
    ddF_x = 1
    ddF_y = -2 * radius
    x = 0
    y = radius
    LCD.pixel(x0, y0 + radius,color)
    LCD.pixel(x0, y0 - radius,color)
    LCD.pixel(x0 + radius, y0,color)
    LCD.pixel(x0 - radius, y0,color)
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        LCD.pixel(x0 + x, y0 + y,color)
        LCD.pixel(x0 - x, y0 + y,color)
        LCD.pixel(x0 + x, y0 - y,color)
        LCD.pixel(x0 - x, y0 - y,color)
        LCD.pixel(x0 + y, y0 + x,color)
        LCD.pixel(x0 - y, y0 + x,color)
        LCD.pixel(x0 + y, y0 - x,color)
        LCD.pixel(x0 - y, y0 - x,color)

def circle2(x0, y0, radius,color):
    # From Adafruit GFX Arduino library
    # Circle drawing function.  Will draw a single pixel wide circle with
    # center at x0, y0 and the specified radius.
    f = 1 - radius
    ddF_x = 1
    ddF_y = -2 * radius
    x = 0
    y = radius
    LCD.draw_point(x0, y0 + radius,color)
    LCD.draw_point(x0, y0 - radius,color)
    LCD.draw_point(x0 + radius, y0,color)
    LCD.draw_point(x0 - radius, y0,color)
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        LCD.draw_point(x0 + x, y0 + y,color)
        LCD.draw_point(x0 - x, y0 + y,color)
        LCD.draw_point(x0 + x, y0 - y,color)
        LCD.draw_point(x0 - x, y0 - y,color)
        LCD.draw_point(x0 + y, y0 + x,color)
        LCD.draw_point(x0 - y, y0 + x,color)
        LCD.draw_point(x0 + y, y0 - x,color)
        LCD.draw_point(x0 - y, y0 - x,color)


def fill_circle(x0, y0, radius, color):
    # From Adafruit GFX Arduino library
    # Filled circle drawing function.  Will draw a filled circule with
    # center at x0, y0 and the specified radius.
    LCD.Vline(x0, y0 - radius, 2*radius + 1, color )
    f = 1 - radius
    ddF_x = 1
    ddF_y = -2 * radius
    x = 0
    y = radius
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        LCD.Vline(x0 + x, y0 - y, 2*y + 1, color+1)
        LCD.Vline(x0 + y, y0 - x, 2*x + 1, color+2)
        LCD.Vline(x0 - x, y0 - y, 2*y + 1, color+3)
        LCD.Vline(x0 - y, y0 - x, 2*x + 1, color+4)

def init_circles(num):
    for i in range(0,num):
        c.append(Circle(0,0,0,0))
    new_circles()

def new_circles():
    j=0
    for i in c:
        r=randint(5,30)
        i.x=randint(r,XSCREEN_MAX-r)
        i.y=randint(r,YCENTER-r)
        if randint(0,1):
            i.y+=YCENTER
        i.r=r
        i.c=color_list[j]
        j+=1
        if j==3:
            j=0
#        print(i.x,i.y,r)

def new_ship():
    ship.x=XCENTER
    ship.y=YCENTER
    ship.ax=0
    ship.ay=0

def show_circles(): # show on up or down buffer
    LCD.FillRectangle(0,0,480,320,LCD.BLACK)

    for i in c:
        if i.y<YSCREEN_MAX:
            fill_circle(i.x,i.y,i.r,i.c)
    #LCD.show_up()

#    LCD.fill(LCD.BLACK)
#    for i in c:
#        if i.y>YCENTER:
#            fill_circle(i.x,i.y-YCENTER,i.r,i.c)
    #LCD.show_down()
        

def calc_gravity():
    ship.aax= 0
    ship.aay= 0
    for i in c:
        distancex=(ship.x-i.x)/1000000
        distancey=(ship.y-i.y)/1000000
        if distancex != 0:
            ship.aax+=((distancex)*sqrt(abs(1/distancex)))
        if distancey != 0:
            ship.aay+=((distancey)*sqrt(abs(1/distancey)))
    #print(ship.aax,ship.aay)

def move_ship():
    i=ship
   # LCD.pixel(int(i.x),int(i.y),LCD.BLACK)
    i.x+=i.ax
    i.y+=i.ay
    i.ax-=i.aax
    i.ay-=i.aay
    if i.x>XSCREEN_MAX or i.x<0 or i.y>YSCREEN_MAX or i.y<0:
        new_ship()
        LCD.fill(LCD.BLACK)
        LCD.show_up()
        LCD.show_down()
        new_circles()
        show_circles()
    else:
        updown = (i.y>YCENTER)*YCENTER
        LCD.draw_point(int(i.x),int(i.y),LCD.WHITE)
#        LCD.pixel(int(i.x),int(i.y)-updown,LCD.WHITE)

#fill_circle(120,65,50,LCD.red)
ship = Point(XCENTER,YCENTER)
init_circles(3)
show_circles()
gticks = 0
while(1):
    move_ship()
    calc_gravity()
#     if ship.y<YCENTER:
#         LCD.show_up()
#     else:
#         LCD.show_down()
    delta = time.ticks_diff(time.ticks_us(), gticks)
    gticks = time.ticks_us()
    fps=1_000_000//delta          # frames per second
    
#    print(fps)
#    for y in range(0,YSCREEN_MAX,1):
#    for x in range(0,XSCREEN_MAX,1):
#    LCD.draw_point(100,100,LCD.WHITE) 
#    print(gc.mem_free())
#     for i in range(0,10):
#         r=50
#         circle2(randint(r,XSCREEN_MAX-r),randint(r,YSCREEN_MAX-r),r,color_list[randint(0,2)])
#     for i in range(0,10):
#         r=50
#         circle(randint(r,XSCREEN_MAX-r),randint(r,YSCREEN_MAX-r),r,color_list[randint(0,2)])
#         LCD.show_up()

#    exit()
    
        