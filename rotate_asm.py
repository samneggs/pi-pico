from LCD_3inch5 import LCD_3inch5
import framebuf
from math import sin,cos,pi, radians
from time import sleep_ms, sleep_us, ticks_diff, ticks_us, sleep
from micropython import const
from uctypes import addressof
import array
from usys import exit
import gc

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
SCALE=const(12)
SCALE2=const(13)
SCALE3=const(13)

class Sprite():
    def __init__(self):
        self.x = 100
        self.y = 100
        self.ax = 1
        self.ay = 1
        self.dir = 1
        self.control = array.array('i',[0,0,100,100,1]) # sin,cos,w,h,deg
        self.buf = bytearray(SPRITE_WIDTH*SPRITE_HEIGHT*2)
        self.buf2 = bytearray(SPRITE_WIDTH*SPRITE_HEIGHT*2)
        self.sprite = framebuf.FrameBuffer(self.buf, SPRITE_WIDTH , SPRITE_HEIGHT, framebuf.RGB565)
        self.sprite2 = framebuf.FrameBuffer(self.buf2, SPRITE_WIDTH , SPRITE_HEIGHT, framebuf.RGB565)
        self.dum1 = self.sprite.line(5,5,50,95,0xffff)
        self.dum2 = self.sprite.line(50,95,95,5,0xa0ff)
        self.dum3 = self.sprite.line(5,5,95,5,0xd0ff)
        self.dum4 = self.sprite.fill_rect(40,40,40,40,0x20d0)
        self.dum5 = self.copy_asm(self.sprite,self.sprite2,SPRITE_WIDTH*SPRITE_HEIGHT)
        self.count = 0
    def move(self):
        self.x = self.x + self.ax
        self.y = self.y + self.ay
        self.count += 1
        if self.count == 10:
            self.count = 0
            self.rotate(self.dir+1)
        if self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
            self.ax = - self.ax
            if self.ax<0:
                self.rotate(1)
        if self.x < 0:
            self.x = 0
            self.ax = - self.ax
            if self.ax>0:
                self.rotate(3)   
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT
            self.ay = - self.ay
            if self.ay<0:
                self.rotate(2) #
        if self.y < 0:
            self.y = 0
            self.ay = - self.ay
            if self.ay>0:
                self.rotate(4) #
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
    def copy_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words (h x w)    
        label(start)
        label(LOOP)
        ldr(r3, [r0, 0])  # load data from source
        str(r3, [r1, 0])  # store data to dest
        add(r0, 4)        # add 4 to source address
        add(r1, 4)        # add 4 from dest address
        sub(r2, 2)        # dec number of words
        bgt(LOOP)         # branch if not done
    @staticmethod
    @micropython.asm_thumb
    def back_to_front_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words    
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
    @staticmethod
    @micropython.asm_thumb
    def fill_asm(r0,r1,r2): # r0=address, r1= # of words, r2=data
        label(LOOP)
        strh(r2, [r0, 0]) # store data in address of r0
        add(r0, 2)        # add 2 to address (next word)
        sub(r1, 1)        # dec number of words
        bgt(LOOP)         # branch if not done
    def rotate(self,new_dir):
        if new_dir>4:
            new_dir = 1
        while(self.dir != new_dir):
            rot90_asm(s.sprite,s.sprite2,SPRITE_HEIGHT)
            copy_asm(s.sprite2,s.sprite,100*100)           
            self.dir+=1
            if self.dir==5:
                self.dir=1
            

def init_isin():            # integer sin lookup table    
    for i in range(0,360):
        isin[i]=int(sin(radians(i))*(2<<SCALE))
    s.control[0]=addressof(isin)
    
        

def init_icos():            # integer cos lookup table 
    for i in range(0,360):
        icos[i]=int(cos(radians(i))*(2<<SCALE))
    s.control[1]=addressof(icos)
          
        


@micropython.native
def rotate(deg):
    r1=range(99)
    for y in r1:
        r2=range(99)
        for x in r2:
            c=s.sprite.pixel(x,y)
            if c:
                #rot_math(deg,x,y,c)
                irot_math(deg,x,y,c) 
                

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
    offset_x = 50 
    offset_y = 50 
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = icos[deg]
    sin_rad = isin[deg]
    qx = int(offset_x + cos_rad * adjusted_x//8192 + sin_rad * adjusted_y//8192)
    qy = int(offset_y - sin_rad * adjusted_x//8192 + cos_rad * adjusted_y//8192)
    #print(qx,offset_x,cos_rad * adjusted_x//8192,sin_rad * adjusted_y//8192)
    #exit()
    s.sprite2.pixel(qx,qy,c)
    
@micropython.viper    # 0-90 deg 1.4 seconds 100x100,  10.5 seconds using pixel()
def rot_viper(deg:int, width:int):
    sin=ptr32(isin)
    cos=ptr32(icos)
    source=ptr16(s.sprite)
    dest  =ptr16(s.sprite2)
    offset_x = width//2
    offset_y = offset_x
    cos_rad = cos[deg]
    sin_rad = sin[deg]
    y=width
    while y: 
        x=width
        while x:
            #c=s.sprite.pixel(x,y)
            i=y*width+x
            color=source[i]
            if color:
                adjusted_x = (x - offset_x)
                adjusted_y = (y - offset_y)
                qx = offset_x 
                qx+= cos_rad * adjusted_x>>SCALE2
                qx+= sin_rad * adjusted_y>>SCALE2
                if qx<0 or qx>width:
                    break
                qy = offset_y
                qy+= sin_rad * adjusted_x>>SCALE2
                qy-= cos_rad * adjusted_y>>SCALE2
                if qy<0 or qy>width:
                    break
                #s.sprite2.pixel(qx,qy,c)
                i = qy * width + qx
                dest[i]=color
            x-=1
        y-=1

@micropython.viper
def back_to_front_viper(length:int):
    start=length
    source=ptr16(s.sprite)
    dest  =ptr16(s.sprite2)
    while length:
        dest[length]=source[start-length]
        length-=1
    

def rot_test():
    x1=100
    y1=100
    lcd.show_xy(0,0,0+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite)
    j = range(0,90,1) # 90
    for i in j:
        s.sprite2.fill(0)
        rot_viper(i)
       
        #rotate(i)
        #s.control[4]=i
        #a=(test_asm(s.sprite,s.sprite2,s.control))
        
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
def fill_asm2(r0,r1,r2): # r0=address, r1= # of words, r2=data
    label(LOOP)
    strh(r2, [r0, 0]) # store data in address of r0
    add(r0, 2)        # add 2 to address (next word)
    sub(r1, 1)        # dec number of words
    bgt(LOOP)         # branch if not done

@micropython.asm_thumb
def back_to_front_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words    
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
def copy_asm(r0,r1,r2): # r0=source address, r1=dest address, r2= # of words    
    label(start)
    label(LOOP)
    ldr(r3, [r0, 0]) # load data from source
    str(r3, [r1, 0]) # store data to dest
    add(r0, 4)        # add 4 to source address
    add(r1, 4)        # add 4 from dest address
    sub(r2, 2)        # dec number of words
    bgt(LOOP)         # branch if not done

@micropython.asm_thumb # ??????
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


 
@micropython.asm_thumb # rot2 ??????
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
 
@micropython.viper
def rot90_viper(height:int):  # 5.25 second on 1000 loops at 100x100
    length=height*height
    source=ptr16(s.sprite)
    dest  =ptr16(s.sprite2)
    x = 0
    while x<height:
        y=height-1
        while y>=0:
            pos = y * height
            pos+= x
            dest[pos]=source[length]
            length-=1
            y-=1
        x+=1

@micropython.asm_thumb   # 1.07 second on 1000 loops at 100x100
def rot90_asm(r0,r1,r2): # r0=source address, r1=dest address,r2=height    
    label(START)
    mov(r3,r2)
    mul(r3,r3)        # length = height*height
    add(r3,r3,r3)
    add(r0,r0,r3)     # r0 = source add + length
    mov(r5,0)         # r5  x = 0
    label(HLOOP)      # height loop
    mov(r3,r2)
    label(WLOOP)      # width loop
    mov(r4,r2)        # r4     = height
    mul(r4,r3)        # r4 pos = height * y
    add(r4,r4,r5)     # pos+= x
    add(r4,r4,r4)     # double for 2 byte color
    add(r4,r4,r1)     # r4 x+y(height)+dest
    ldrh(r6, [r0, 0]) # r6 = source[r0]
    strh(r6, [r4, 0]) # dest[r4]    
    sub(r0,2)         # r0 length-=1 (2)
    sub(r3,1)         # r3 y-=1
    bgt(WLOOP) 
    add(r5,1)         # x+=1
    cmp(r5,r2)        # x < height
    blt(HLOOP) 
    label(EXIT)

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
    
                             # 0.96 seconds 0-90 deg 100x100
@micropython.asm_thumb       #                                              0         4    8     12     16       20            24
def test_asm(r0,r1,r2)->int: # r0=source address, r1=dest address,r2 (addr sin, addr cos,width, height, deg, multiplier, multiplier2 10_000)    
    label(START)
    bl(CLS)                    # zero out sprite        
    ldr(r3, [r2, CTL_HEIGHT])  # r3 = height or y
    label(HLOOP)
    ldr(r4, [r2, CTL_WIDTH])   # r4 = width or x
    label(WLOOP)
    
    ldr(r7, [r2, CTL_HEIGHT])  # r7 = max height
    mov(r5,r3)                 # r5 = r3 = y
    mul(r5,r7)                 # y*height
    add(r5,r5,r4)              # add x
    add(r5,r5,r5)              # double (2 for pixel color)

    add(r5,r5,r0)              # source addr + y(height)   
    ldrh(r6, [r5,0])           # load pixel color from source
    cmp(r6,0)                  # compare with zero
    beq(SKIP)                  # skip if zero (black)
    push({r6})                 # save color
    
    bl(OFFSET_Y)               # jump offset_y
    sub(r5,r3,r5)              # r5 =   adjusted_y = (y - offsety)
    bl(SIN)                    # jump sin
    mul(r5,r6)                 # r5 = adjusted_y * sin
    mov(r6,SCALE3)              # r6 = 12
    lsr(r5,r6)                 # r5 >> 12    
  
    push({r5})                 # save r5 (adjusted_y * sin)>>12
    bl(OFFSET_X)               # jump offset_x

    sub(r5,r4,r5)              # r5 =  adjusted_x = (x - offsetx)
    
    
    bl(COS)                    # jump cos
    mul(r5,r6)                 # r5 = adjusted_x * cos
    
    
    mov(r6,SCALE3)              # r6 = 1
    lsr(r5,r6)                 # r5 >> 12  (good)
    
    push({r5})                 # save r5 (adjusted_x * cos)>>12
    
    bl(OFFSET_X)               # jump adjusted_x     
    pop({r6,r7})               # retrieve (cos_rad * adjusted_x)>>12 , (sin_rad * adjusted_y)>>12
    
    
    add(r5,r5,r6)              # +(cos_rad * adjusted_x)>>12
    add(r5,r5,r7)              # +(sin_rad * adjusted_y)>>12
   
   
    bmi(POPSKIP)               # branch if negative
    ldr(r7, [r2, CTL_WIDTH])   # r4 = width or x
    cmp(r7, r5)                # is x > width?
    bmi(POPSKIP)               # too big skip
        
    push({r5})                 # save qx
    
    bl(OFFSET_Y)               # jump offset_y
    sub(r5,r3,r5)              # r5 =   adjusted_y = (y - offsety)
    bl(COS)                    # jump cos
    mul(r5,r6)                 # r5 = adjusted_y * cos
    mov(r6,SCALE3)              # r6 = 1
    lsr(r5,r6)                 # r5 >> 12
    push({r5})                 # save r5 (adjusted_y * cos)>>12
    
    bl(OFFSET_X)               # jump offset_x
    sub(r5,r4,r5)              # r5 =  adjusted_x = (x - offsetx)
    bl(SIN)                    # jump sin
    mul(r5,r6)                 # r5 = adjusted_x * sin
    mov(r6,SCALE3)              # r6 = 1
    lsr(r5,r6)                 # r5 >> 12
    push({r5})                 # save r5 (adjusted_x * sin)>>12

    bl(OFFSET_Y)               # jump offset_y
    pop({r6,r7})               # retrieve (cos_rad * adjusted_y)>>12 , (sin_rad * adjusted_x)>>12
    sub(r5,r5,r6)              # -(adjusted_x * sin)>>12
    add(r5,r5,r7)              # +(adjusted_y * cos)>>12
    bmi(POPSKIP2)              # branch if negative
    ldr(r7, [r2, CTL_WIDTH])   # r7 = max width
    cmp(r7, r5)                # is x > width?
    bmi(POPSKIP2)              # too big skip
    
    ldr(r7, [r2, CTL_HEIGHT])  # r7 = max height
    mul(r5,r7)                 # qy*height
    pop({r6})                  # get qx
    add(r5,r5,r6)              # qy*height + qx
    add(r5,r5,r5)              # double
    add(r5,r5,r1)              # dest addr + qy(height)    
    pop({r6})                  # get color
    
    strh(r6, [r5,0])           # store pixel color to dest
     
    label(SKIP)
    sub(r4,1)                  # dec x by 1
    bgt(WLOOP)
    sub(r3,1)                  # dec y by 1
    bgt(HLOOP)
    
    b(EXIT)                    # exit
    
    # ----------------------------------------------------------------------------------- subroutines   
    label(POPSKIP2)             # pop then skip
    pop({r7})
    label(POPSKIP)             # pop then skip
    pop({r7})
    b(SKIP)
    
    label(POPEXIT)             # pop then exit
    pop({r7})
    b(EXIT)
    
    label(OFFSET_X)           # uses r5,r6 and returns offset_x in r5
    ldr(r5, [r2, CTL_WIDTH])  # r5 = width 
    mov(r6, 1)                # r6 = 1
    lsr(r5,r6)                # r5 >> 1  (offsetx)
    bx(lr)
    
    label(OFFSET_Y)           # uses r5,r6 and returns offset_y in r5
    ldr(r5, [r2, CTL_HEIGHT]) # r5 = height 
    mov(r6, 1)                # r6 = 1
    lsr(r5,r6)                # r5 >> 1  (offsety)
    bx(lr)

    label(ADJUSTED_Y)         # uses r5,r6 and returns adjusted_y in r5  **deprecated **
    sub(r5,r3,r5)             # r5 =     (y - offsety)
    bx(lr)

    label(ADJUSTED_X)         # uses r5,r6 and returns adjusted_x in r5  **deprecated **
    sub(r5,r4,r5)             # r5 =     (x - offsetx)
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

    label(CLS)        # clear the screen, uses r3,r4,r5
    ldr(r3, [r2, CTL_HEIGHT])  # r3 = height or y
    mul(r3,r3)        # r3 = number of words to clear    
    mov(r4,r1)        # r4 = address
    mov(r5,0)         # r5 = data to load
    label(CLS_LOOP)
    strh(r5, [r4, 0]) # store data in address
    add(r4, 2)        # add 2 to address (next word)
    sub(r3, 1)        # dec number of words
    bgt(CLS_LOOP)         # branch if not done
    bx(lr)

    label(EXIT) 


s=Sprite()

color = 0
lcd = LCD_3inch5()
lcd.bl_ctrl(50)
lcd.Fill(lcd.BLUE)

isin=array.array('i',range(0,361))
icos=array.array('i',range(0,361))
init_isin()
init_icos()



copy_asm(s.sprite,s.sprite2,100*100)
lcd.show_xy(0,0,0+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite)
s.sprite2.fill(0)
gticks=ticks_us()    
#rot_test()
#control = array.array('i',[0,0,200,200,0,0])
control = array.array('i',[0,0,100,100,0,0])
for i in range(90):
    #rot_asm(s.sprite,s.sprite2,control)
    #back_to_front_asm(s.sprite,s.sprite2,100*100)
    #copy_asm(s.sprite,s.sprite2,100*100)
    #s.sprite2.fill(lcd.GREEN)
    #s.copy_asm(s.sprite,s.sprite2,100*100)
    #s.flip_asm(s.sprite,s.sprite2,100*100)
    #back_to_front_viper(100*100)
    s.fill_asm(s.sprite2,100*100,lcd.BLACK)
    #lcd.show_xy(200,0,200+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite2)
    #sleep(1)
    
    #s.control[4]=i
    #test_asm(s.sprite,s.sprite2,s.control)
    #fill_asm(s.sprite2,100*100,0xff,0xff)
    
    rot_viper(i,100)
    lcd.show_xy(200,0,200+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite2)
    #rot90_asm(s.sprite,s.sprite2,100)
    #copy_asm(s.sprite2,s.sprite,100*100)
    #lcd.show_xy(200,0,200+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite)
    #sleep(0.1)

delta = ticks_diff(ticks_us(), gticks)
f0=(delta/1000000)
print(f0)
lcd.show_xy(200,0,200+SPRITE_WIDTH-1,0+SPRITE_HEIGHT-1,s.sprite2) 

exit()


while(1):
    bounce()