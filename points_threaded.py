from LCD_1inch14 import LCD_1inch14
from machine import Pin,SPI,PWM, Timer
import framebuf, math
import utime, gc, _thread
from random import randint
from usys import exit

class Points():
    def __init__(self,x,y,c):
        self.x = x
        self.y = y
        self.oldx = 0
        self.oldy = 0
        self.ax = 1
        self.ay = 1
        self.aax = 0
        self.aay = 0
        self.c = c

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
LCD = LCD_1inch14()
p=[]
threaded = 1  # 1= threaded using 2 cores

token = 1

def init_points(num,c):
    for i in range(0,num):
        p.append(Points(randint(0,240),randint(0,135),c))

def move_points(start,stop):
    for j in range(start,stop):
        i=p[j]
        i.oldx=i.x
        i.oldy=i.y
        i.x+=i.ax
        i.y+=i.ay
        i.ax+=i.aax
        i.ay+=i.aay
        if i.x>240 or i.x<0:
            i.ax=-i.ax
            i.x=i.oldx
        if i.y>135 or i.y<0:
            i.ay=-i.ay
            i.y=i.oldy


def show_points(start,stop):
    for j in range(start,stop):
        i=p[j]
        LCD.pixel(i.oldx,i.oldy,LCD.black)
        LCD.pixel(i.x,i.y,i.c)


def calc_fps():
    delta = utime.ticks_diff(utime.ticks_us(), gticks)
    gticks = utime.ticks_us()
    fps=1_000_000//delta          # frames per second


def show_fps(fps):
    s1=s[fps//10]
    s2=s[fps%10]   
    LCD.fill_rect(100,40,20,10,LCD.black)
    LCD.text(s1,100,40,LCD.white)
    LCD.text(s2,110,40,LCD.white)
    LCD.text('Frames per second:',40,20,LCD.white)



def show_display():       # crashes after few seconds
    global token, gticks
    while True:
        if True: # token == 1:
            show_points(51,99)
            move_points(51,99)
            LCD.text('Two threads, 100 points',40,0,LCD.white)            
            delta = utime.ticks_diff(utime.ticks_us(), gticks)
            gticks = utime.ticks_us()
            fps=1_000_000//delta          # frames per second
            show_fps(fps)
            LCD.show()


pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)#max 65535
LCD.fill(LCD.black)
LCD.show()
old_mem_free = 0
gticks = 0
fps = 0
init_points(50,LCD.white)
init_points(50,LCD.green)
s=['0','1','2','3','4','5','6','7','8','9']


if threaded:
    _thread.start_new_thread(show_display, ())

try:
    while(1):
        show_points(0,50)
        move_points(0,50)
        if not threaded:
            show_fps(fps)
            LCD.text('One thread, 50 points',40,0,LCD.white)  
            LCD.show()
            delta = utime.ticks_diff(utime.ticks_us(), gticks)
            gticks = utime.ticks_us()
            fps=1_000_000//delta          # frames per second

        #print(old_mem_free-gc.mem_free())
        old_mem_free=gc.mem_free()
     

except KeyboardInterrupt:
    _thread.exit()
    exit()
