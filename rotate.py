from LCD_3inch5 import LCD_3inch5
import framebuf
from math import sin,cos,pi
from time import sleep_ms, sleep_us, ticks_diff, ticks_us, sleep
from micropython import const
from uctypes import addressof
import array

SCREEN_WIDTH = const(350)
SCREEN_HEIGHT = const(220)
SPRITE_WIDTH=const(100)
SPRITE_HEIGHT=const(100)


class Sprite():
    def __init__(self):
        self.x = 100
        self.y = 100
        self.ax = 1
        self.ay = 1
        self.dir = 1
        self.control = array.array('i',[200, 200,0,0])
        self.buf = bytearray(SPRITE_WIDTH*SPRITE_HEIGHT*2)
        self.buf2 = bytearray(SPRITE_WIDTH*SPRITE_HEIGHT*2)
        self.sprite = framebuf.FrameBuffer(self.buf, SPRITE_WIDTH , SPRITE_HEIGHT, framebuf.RGB565)
        self.sprite2 = framebuf.FrameBuffer(self.buf2, SPRITE_WIDTH , SPRITE_HEIGHT, framebuf.RGB565)
        self.dum1 = self.sprite.line(5,5,50,95,0xffff)
        self.dum2 = self.sprite.line(50,95,95,5,0xa0ff)
        self.dum3 = self.sprite.line(5,5,95,5,0xd0ff)
        self.dum4 = self.sprite.fill_rect(40,40,40,40,0x20d0)
        self.dum5 = self.copy_asm(self.sprite,self.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
    def move(self):
        self.x = self.x + self.ax
        self.y = self.y + self.ay
        if self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
            self.ax = - self.ax
            if self.ax<0:
                self.rotate(2)
        if self.x < 0:
            self.x = 0
            self.ax = - self.ax
            if self.ax>0:
                self.rotate(3)   
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT
            self.ay = - self.ay
            if self.ay<0:
                self.rotate(4) #
        if self.y < 0:
            self.y = 0
            self.ay = - self.ay
            if self.ay>0:
                self.rotate(1) #

    @staticmethod
    @micropython.asm_thumb
    def rot_asm(r0,r1,r2): # r0=source address, r1=dest address,r2 (width, height)    
        label(START)
        ldr(r3, [r2, 4])  # r3 = working height from control
        label(HLOOP)      # height loop
        mov(r4,r1)        # r4 = working dest
        sub(r4,r4,r3)     # sub height to dest
        ldr(r5, [r2, 0])  # r5 = perm width from control
        mov(r6,r5)        # r6 = working width
        label(WLOOP)      # width loop
        ldrh(r7, [r0, 0]) # r7 = load data from source
        add(r4,r4,r5)     # add perm width to working dest
        strh(r7, [r4, 0]) # store data to working dest
        add(r0,2)         # inc next source
        sub(r6,2)         # dec working width 
        bgt(WLOOP)
        sub(r3,2)         # dec working height
        bgt(HLOOP)
    @staticmethod
    @micropython.asm_thumb
    def copy_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words     
        label(start)
        label(LOOP)
        ldrh(r3, [r0, 0]) # load data from source
        strh(r3, [r1, 0]) # store data to dest
        add(r0, 2)        # add n to source address
        add(r1, 2)        # sub n from dest address
        sub(r2, 1)        # dec number of words
        bgt(LOOP)         # branch if not done
    @staticmethod
    @micropython.asm_thumb
    def flip_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words    
        label(start)
        add(r1,r1,r2)     # set r1 to end of array
        add(r1,r1,r2)     # 4 * words
        label(LOOP)
        ldrh(r3, [r0, 0]) # load data from source
        strh(r3, [r1, 0]) # store data to dest
        add(r0, 2)        # add n to source address
        sub(r1, 2)        # sub n from dest address
        sub(r2, 1)        # dec number of words
        bgt(LOOP)         # branch if not done
    def rotate(self,new_dir):
        while(1):
            if self.dir == new_dir:
                return
            if self.dir == 4:
                self.dir = 1    
                self.flip_asm(s.sprite,s.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
                if self.dir == new_dir:
                    return
            if self.dir == 1:
                self.dir = 2    
                self.rot_asm(self.sprite2,self.sprite,self.control)
                self.flip_asm(self.sprite,self.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
                if self.dir == new_dir:
                    return
            if self.dir == 2:
                self.dir = 3        
                self.copy_asm(self.sprite,self.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
                if self.dir == new_dir:
                    return
            if self.dir == 3:
                self.dir = 4            
                self.rot_asm(self.sprite2,self.sprite,self.control)
                self.flip_asm(self.sprite,self.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
                self.copy_asm(self.sprite2,self.sprite,SPRITE_WIDTH*SPRITE_HEIGHT)


        
        
s=Sprite()

color = 0
lcd = LCD_3inch5()
lcd.bl_ctrl(50)
lcd.Fill(lcd.BLACK)

@micropython.native
def rotate(deg):
    rad=deg*pi/180
    r1=range(99)
    for y in r1:
        r2=range(99)
        for x in r2:
            c=s.sprite.pixel(x,y)
            if c:
                rot_math(deg,x,y,c)
                #x3=x
                #y3=y
                #x2=int(x3*cos(rad)+y3*sin(rad))
                #y2=int(y3*cos(rad)-x3*sin(rad))
                #x2 = int(50 + cos(rad) * (x - 50) - sin(rad) * (y - 50))
                #y2 = int(50 + sin(rad) * (x - 50) + cos(rad) * (y - 50))
                #sprite2.pixel(x2,y2,c)

@micropython.native
def rot_math(deg,x,y,c):
    radians = deg*pi/180
    offset_x = 50
    offset_y = 50
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = cos(radians)
    sin_rad = sin(radians)
    qx = int(offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y)
    qy = int(offset_y - sin_rad * adjusted_x + cos_rad * adjusted_y)
    s.sprite2.pixel(qx,qy,c)

def rot_test():
    x1=100
    y1=100
    for i in range(0,190,10):
        s.sprite2.fill(0)
        rotate(i)
        lcd.show_xy(x1,y1,x1+SPRITE_WIDTH-1,y1+SPRITE_HEIGHT-1,s.sprite2)            

@micropython.asm_thumb
def fill_asm(r0,r1,r2,r3): # r0=address, r1= # of words, r2,r3=data
    label(LOOP)
    strb(r2, [r0, 0]) # store r2 in address of r0
    strb(r3, [r0, 1]) # store r3 in address of r0+1
    add(r0, 2)        # add 2 to address (next word)
    sub(r1, 1)        # dec number of words
    bgt(LOOP)         # branch if not done

@micropython.asm_thumb
def flip_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words    
    label(start)
    add(r1,r1,r2)     # set r1 to end of array
    add(r1,r1,r2)     # 4 * words
    label(LOOP)
    ldrh(r3, [r0, 0]) # load data from source
    strh(r3, [r1, 0]) # store data to dest
    add(r0, 2)        # add n to source address
    sub(r1, 2)        # sub n from dest address
    sub(r2, 1)        # dec number of words
    bgt(LOOP)         # branch if not done
    
@micropython.asm_thumb
def rot_asm(r0,r1,r2): # r0=source address, r1=dest address,r2 (width, height)    
    label(START)
    ldr(r3, [r2, 4])  # r3 = working height from control
    label(HLOOP)      # height loop
    mov(r4,r1)        # r4 = working dest
    sub(r4,r4,r3)     # sub height to dest
    ldr(r5, [r2, 0])  # r5 = perm width from control
    mov(r6,r5)        # r6 = working width
    label(WLOOP)      # width loop
    ldrh(r7, [r0, 0]) # r7 = load data from source
    add(r4,r4,r5)     # add perm width to working dest
    strh(r7, [r4, 0]) # store data to working dest
    add(r0,2)         # inc next source
    sub(r6,2)         # dec working width 
    bgt(WLOOP)
    sub(r3,2)         # dec working height
    bgt(HLOOP)


def fill_tests(test):
    gticks=ticks_us()
    sprite2.fill(lcd.RED)
    #lcd.show_xy(100,100,199,199,sprite)
    r=range(100)
    for i in r:
        if test==0:
            sprite2.fill(lcd.WHITE)
        elif test==1:
            fill_asm(sprite2,10_000,0xf0,0xff)
        elif test==2:           
            flip_asm(sprite,sprite2,10_000) # r0=source address, r1=dest address, r2= # of words
        elif test==3:
            control = array.array('i',[200, 200,0,0])
            rot_asm(sprite,sprite2,control)
        lcd.show_xy(200,100,200+SPRITE_WIDTH-1,100+SPRITE_HEIGHT-1,sprite2)
    delta = ticks_diff(ticks_us(), gticks)
    f0=(delta/1000000)
    print(f0)
    gticks=ticks_us()
    

def bounce():
    s.move()
    lcd.show_xy(s.x,s.y,s.x+SPRITE_WIDTH-1,s.y+SPRITE_HEIGHT-1,s.sprite2)
    #lcd.show_xy(0,0,SPRITE_WIDTH-1,SPRITE_HEIGHT-1,s.sprite)
    

rot_test()
        
#fill_tests(0)
#fill_tests(1)
#fill_tests(3)
while(1):
    bounce()
