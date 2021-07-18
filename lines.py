from LCD_1inch14 import LCD_1inch14
from machine import Pin,SPI,PWM,Timer
import framebuf, math
import utime
from random import randint
from sys import exit
import _thread


class Point():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.ax = 1
        self.ay = 1
        self.c = 0


        
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

p = []
token = 0
c=0
gticks = 0
cores = 1    # 1 or 2

LCD = LCD_1inch14()

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def init_point():
    for i in range(0,100):
        p.append(Point())
    p[0].x = 100
    p[0].y = 100
    p[0].ax = 3
    p[0].ay = 4
    p[1].x = randint(0,240)
    p[1].y = randint(0,135)
    p[1].ax = 4
    p[1].ay = 3


def p_list():    
    for i in range(len(p)-4,0,-2):
        print(i,p[i].x,p[i+1].x)


#@timed_function
def lines():
    global token, c
    for i in range(len(p)-4,0,-2):
        p[i].x = p[i-2].x
        p[i].y = p[i-2].y
        p[i+1].x = p[i-1].x
        p[i+1].y = p[i-1].y        
    for i in range(0,2):
        p[i].x += p[i].ax
        p[i].y += p[i].ay
        if p[i].x > 240:
            p[i].x = 240
            p[i].ax = -p[i].ax
        if p[i].x < 0:
            p[i].x = 0
            p[i].ax = -p[i].ax
        if p[i].y > 135:
            p[i].y = 135
            p[i].ay = -p[i].ay
        if p[i].y < 0:
            p[i].y = 0
            p[i].ay = -p[i].ay
    #LCD.fill(LCD.black)
    c += 1
    if c<50:
        color = LCD.red
    elif c<100:
        color = LCD.green
    elif c<150:
        color = LCD.blue
    else:
        c = 0
        color = LCD.red       
    LCD.line(p[0].x,p[0].y,p[1].x,p[1].y,color)
    LCD.line(p[90].x,p[90].y,p[91].x,p[91].y,LCD.black)

def show_display():
    global token
    while True:
        LCD.show()
        token = 0

if cores == 2:
    _thread.start_new_thread(show_display, ())


if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535
    LCD.fill(LCD.black)    
    #LCD.show()
    
    key0 = Pin(15,Pin.IN)
    key1 = Pin(17,Pin.IN)
    key2 = Pin(2 ,Pin.IN)
    key3 = Pin(3 ,Pin.IN)

    init_point()

    c=0
    x1=100
    y1=50
    x2=130
    y2=80
    deg=90
    while(1):
        if cores == 1:
            LCD.show()
        if token == 0 or cores==1:
            lines()
            token =1
        while token == 1 and cores == 2:
            pass
        delta = utime.ticks_diff(utime.ticks_us(), gticks)
        print(1_000_000/delta)
        gticks = utime.ticks_us()
        

