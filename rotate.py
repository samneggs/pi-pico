from LCD_3inch5 import LCD_3inch5
import framebuf
from math import sin,cos,pi, radians
from time import sleep_ms, sleep_us, ticks_diff, ticks_us, sleep
from micropython import const
from uctypes import addressof
import array

SCREEN_WIDTH = const(350)
SCREEN_HEIGHT = const(220)
SPRITE_WIDTH=const(100)
SPRITE_HEIGHT=const(100)
CTL_SIN=const(0)
CTL_COS=const(4)
CTL_WIDTH=const(8)
CTL_HEIGHT=const(12)
CTL_DEG=const(16)
CTL_M1=const(20)
CTL_M2=const(24)

class Sprite():
    def __init__(self):
        self.x = 100
        self.y = 100
        self.ax = 1
        self.ay = 1
        self.dir = 1
        self.control = array.array('i',[0,0,200,200,359,500,10_000]) # sin,cos,w,h,deg,m1,m2
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
        ldr(r3, [r2, CTL_HEIGHT])  # r3 = working height from control
        label(HLOOP)               # height loop
        mov(r4,r1)                 # r4 = working dest
        sub(r4,r4,r3)              # sub height to dest
        ldr(r5, [r2, CTL_WIDTH])   # r5 = perm width from control
        mov(r6,r5)                 # r6 = working width
        label(WLOOP)               # width loop
        ldrh(r7, [r0, 0])          # r7 = load data from source
        add(r4,r4,r5)              # add perm width to working dest
        strh(r7, [r4, 0])          # store data to working dest
        add(r0,2)                  # inc next source
        sub(r6,2)                  # dec working width 
        bgt(WLOOP)
        sub(r3,2)                  # dec working height
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


def init_isin():            # integer sin lookup table    
    for i in range(0,361):
        isin[i]=int(sin(radians(i))*8192) # 2<<12
        #print(i,isin[i])
    s.control[0]=addressof(isin)
    
        

def init_icos():            # integer cos lookup table 
    for i in range(0,361):
        icos[i]=int(cos(radians(i))*8192)
    s.control[1]=addressof(icos)
          
        
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
                #rot_math(deg,x,y,c)
                irot_math(deg,x,y,c) # *1000
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
    
@micropython.native
def irot_math(deg,x,y,c):
    offset_x = 50 #50_000
    offset_y = 50 #50_000
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = icos[deg]
    sin_rad = isin[deg]
    qx = int(offset_x + cos_rad * adjusted_x//8192 + sin_rad * adjusted_y//8192)
    qy = int(offset_y - sin_rad * adjusted_x//8192 + cos_rad * adjusted_y//8192)
    s.sprite2.pixel(qx,qy,c) # //1000

def rot_test():
    x1=100
    y1=100
    for i in range(0,180,1):
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
    ldr(r3, [r2, CTL_HEIGHT])  # r3 = working height from control
    label(HLOOP)      # height loop
    mov(r4,r1)        # r4 = working dest
    sub(r4,r4,r3)     # sub height to dest
    ldr(r5, [r2, CTL_WIDTH])  # r5 = perm width from control
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

 
@micropython.asm_thumb
def rot2_asm(r0,r1,r2): # r0=source address, r1=dest address,r2 (width, height, addr sin, addr cos)    
    label(START)
    ldr(r3, [r2, CTL_HEIGHT])  # r3 = working height from control
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
    



isin=array.array('i',range(0,361))
icos=array.array('i',range(0,361))
init_isin()
init_icos()


#rot_test()
        
#fill_tests(0)
#fill_tests(1)
#fill_tests(3)

@micropython.asm_thumb       #                                              0         4    8     12     16       20            24
def test_asm(r0,r1,r2)->int: # r0=source address, r1=dest address,r2 (addr sin, addr cos,width, height, deg, multiplier, multiplier2 10_000)    
    label(START)
    
    ldr(r3, [r2, CTL_HEIGHT]) # r3 = height
    label(HLOOP)
    ldr(r4, [r2, CTL_WIDTH])  # r4 = width
    label(WLOOP)
    #push({r3, r4})            # save r3,r4
    bl(ADJUSTED_X)             # jump adjusted_x
    bl(SIN)                    # jump sin
    mul(r5,r6)                 # r5 = adjusted_x * sin
    mov(r6,12)                 # r6 = 1
    lsr(r5,r6)                 # r5 >> 12    
    #pop({r4, r3})             # restore r4,r3
    sub(r4,2)
    bgt(WLOOP)
    sub(r3,1)
    bgt(HLOOP)
    b(EXIT)                  # exit   


    label(ADJUSTED_X)       # uses r5,r6 and returns adjusted_x in r5
    ldr(r5, [r2, CTL.WIDTH]) # r5 = width (200)
    mov(r6, 1)              # r6 = 1
    lsr(r5,r6)              # r5 >> 1  (offsetx)
    sub(r5,r3,r5)           # r5 =     (x - offsetx)
    bx(lr)
    
    label(SIN)              # uses r6,r7 and returns sin in r6 
    ldr(r6, [r2, CTL_SIN])  # r6 = sin addr
    ldr(r7, [r2, CTL_DEG])  # r7 = degrees
    add(r7,r7,r7)
    add(r7,r7,r7)           # x4 for word aligned
    add(r6,r6,r7)           # sin addr + deg offset 
    ldr(r6, [r6,  0])       # r3 = sin(degrees)
    bx(lr)
    
    label(COS)              # uses r6,r7 and returns cos in r6 
    ldr(r6, [r2, CTL_COS])  # r5 = cos addr
    ldr(r7, [r2, CTL_DEG])  # r7 = degrees
    add(r7,r7,r7)
    add(r7,r7,r7)           # x4 for word aligned
    add(r6,r6,r7)           # cos addr + deg offset 
    ldr(r6, [r6,  0])       # r6 = cos(degrees)
    bx(lr)
    
    label(EXIT) 

#     offset_x = 50
#     offset_y = 50
#     adjusted_x = (x - offset_x)
#     adjusted_y = (y - offset_y)
#     cos_rad = icos[deg]
#     sin_rad = isin[deg]
#     qx = int(offset_x + (cos_rad * adjusted_x)>>12 + (sin_rad * adjusted_y)>>12)
#     qy = int(offset_y - (sin_rad * adjusted_x)>>12 + (cos_rad * adjusted_y)>>12)
#     s.sprite2.pixel(qx,qy,c) 

    

#print(isin[359])
#s.control[0]=addressof(isin)
print(test_asm(s.sprite,s.sprite2,s.control))
exit()


while(1):
    bounce()
