from LCD_1inch14 import LCD_1inch14
from machine import Pin,SPI,PWM, Timer
import framebuf, math
import utime, gc
from random import randint
from usys import exit


class Clock():
    def __init__(self,t):
        self.year, self.month, self.day, self.hour, self.minute, self.second, self.week, self.d = t
    def set(self,t):
        self.year, self.month, self.day, self.hour, self.minute, self.second, self.week, self.d = t

class Numbers_Position():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.oldx = 0
        self.oldy = 0
        self.ax = 0
        self.ay = 0
        self.aax = 0
        self.aay = .005
        

t=Clock(utime.localtime())

old_mem_free=gc.mem_free()

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
LCD = LCD_1inch14()
numbers = []
pos = []

# blit_image_file borrowed then butchered from Stewart Watkiss
# http://www.penguintutor.com/programming/picodisplayanimations
def blit_image_file (filename,width,height,cw,ch): # file width, file height, char width, char height
    display_buffer = bytearray(cw*ch*2) #(width * height * 2)
    with open (filename, "rb") as file:
        file_position = 0
        char_position = 0
        while file_position < (width * height * 2):
            current_byte = file.read(1)
            # if eof
            if len(current_byte) == 0:
                break
            # copy to buffer
            display_buffer[char_position] = ord(current_byte) #and LCD.red
            char_position += 1
            file_position += 1
            if char_position == (cw * ch* 2):
                numbers.append((framebuf.FrameBuffer(display_buffer,cw,ch, framebuf.RGB565)))
                char_position = 0
                display_buffer = bytearray(cw * ch * 2)
    file.close()
    return 


def init_numbers(): # width, height
    #blit_image_file ("numbers6.bin",22,440,22,40)
    for i in range(0,9):
        LCD.blit(numbers[i],i*32,40) # position x,y
    LCD.show()

def show_time():
    LCD.fill(LCD.black)
    hour=t.hour
    if hour>12:
        hour -= 12
    if hour>9:
        LCD.blit(numbers[1],int(pos[0].x),int(pos[0].y))         # hours tens
    LCD.blit(numbers[hour%10],int(pos[1].x),int(pos[1].y))       # hours ones
    LCD.blit(numbers[10],int(pos[2].x),int(pos[2].y))            # :
    LCD.blit(numbers[t.minute//10],int(pos[3].x),int(pos[3].y))  # minutes tens        
    LCD.blit(numbers[t.minute%10],int(pos[4].x),int(pos[4].y))   # minutes ones
    LCD.blit(numbers[10],int(pos[5].x),int(pos[5].y))            # :
    LCD.blit(numbers[t.second//10],int(pos[6].x),int(pos[6].y))  # minutes tens        
    LCD.blit(numbers[t.second%10],int(pos[7].x),int(pos[7].y))   # minutes ones
    LCD.show()

def init_positions():
    j=0
    for i in range(0,8):
        pos.append(Numbers_Position(j*30,30+j))
        j+=1
        
def move_nums():
    for i in pos:
        i.x+=i.ax
        i.y+=i.ay
        i.ax+=i.aax
        i.ay+=i.aay
        if i.y > 105 or i.y < 1 :
            i.y=i.oldy
            #i.aay=-i.aay
            i.ay=-i.ay
        if abs(i.ay)>1:
            i.aay=-i.aay
        if abs(i.ax)>.2:
            i.aax=-i.aax
            
        i.oldy=i.y
        

def show_timer(timer):
    global old_mem_free
    
    t.set(utime.localtime())
    #LCD.show()
    
    #print(old_mem_free-gc.mem_free())
    old_mem_free=gc.mem_free()
    
#("numbers4.bin",30,341,30,31)
#("numbers8.bin",22,440,22,40)

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535
    LCD.fill(LCD.black)
    LCD.show()
    init_positions()
    blit_image_file ("numbers4.bin",30,341,30,31)
    tim = Timer()      #set the timer
    tim.init(freq=2, mode=Timer.PERIODIC, callback=show_timer)  # Start timing
    #LCD.fill_rect(0,30,240,40,LCD.black)
    #init_numbers()
    while(1):
        show_time()
        move_nums()
            
    
    