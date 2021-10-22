from machine import Pin,SPI,PWM
import framebuf
from time import sleep_ms, sleep_us, ticks_diff, ticks_us
from micropython import const,heap_lock
import ustruct,gc
from random import randint
from usys import exit

LCD_DC   = const(8)
LCD_CS   = const(9)
LCD_SCK  = const(10)
LCD_MOSI = const(11)
LCD_MISO = const(12)
LCD_BL   = const(13)
LCD_RST  = const(15)
TP_CS    = const(16)
TP_IRQ   = const(17)
_CASET = const(0x2a) # Column Address Set
_PASET = const(0x2b) # Page Address Set
_RAMWR = const(0x2c) # Memory Write
_RAMRD = const(0x2e) # Memory Read
MEMORY_BUFFER = const(200) #1024) # SPI Write Buffer
COLUMN_ADDRESS_SET = const(0x2a);PAGE_ADDRESS_SET = const(0x2b);RAM_WRITE = const(0x2c);RAM_READ = const(0x2e)

class LCD_3inch5(framebuf.FrameBuffer):
    def __init__(self, mem = 200):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000
        self.YELLOW =  0xE0FF
        self.ORANGE =  0x20FD
        
        self.width = 480
        self.height = 160 #160
        
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)
        self.temp = bytearray(1)
#        self.temp2 = bytearray(1)    

        h2=1    # set to framebuffer height
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
        gc.collect()
#        print(gc.mem_free())     
        self.buffer = bytearray(h2 * self.width * 2)
        super().__init__(self.buffer, self.width, h2, framebuf.RGB565)
        self.init_display()
        self.color_map = bytearray(b'\x00\x00\xFF\xFF')
        self.mem_buffer = bytearray(mem*2)# MEMORY_BUFFER * 2)
        self.mv_buffer = bytearray(mem*2)#MEMORY_BUFFER * 2)
        self.temp_color = bytearray(2)
#         self.red_buffer = bytearray(RECT_BUFFER*2)
#         self.yellow_buffer = bytearray(RECT_BUFFER*2)
#         self.orange_buffer = bytearray(RECT_BUFFER*2)
#         self.green_buffer = bytearray(RECT_BUFFER*2)
#         self.black_buffer = bytearray(RECT_BUFFER*2)
#         self.white_buffer = bytearray(RECT_BUFFER*2)
#         self.blue_buffer = bytearray(RECT_BUFFER*2)
#         for i in range(RECT_BUFFER):
#             self.red_buffer[2*i]=0xe0 ; self.red_buffer[2*i+1]=0x07
#             self.yellow_buffer[2*i]=0xff; self.yellow_buffer[2*i+1]=0xe0
#             self.orange_buffer[2*i]=0xfd; self.orange_buffer[2*i+1]=0x20
#             self.green_buffer[2*i]=0x1f ; self.green_buffer[2*i+1]=0x00
#             self.white_buffer[2*i]=0xff ; self.white_buffer[2*i+1]=0xff
#             self.blue_buffer[2*i]=0x00 ; self.blue_buffer[2*i+1]=0xf8
        
    def write_cmd(self, cmd):
        self.temp[0] = cmd
        self.cs(1)
        self.dc(0)
        self.cs(0)
        #self.spi.write(bytearray([cmd]))
        self.spi.write(self.temp) #(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.temp[0] = buf
        self.cs(1)
        self.dc(1)
        self.cs(0)
        #self.spi.write(bytearray([0X00]))
        #self.spi.write(bytearray([buf]))
        self.spi.write(self.temp) #(bytearray([buf]))
        self.cs(1)


    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        sleep_ms(5)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(5)
        self.write_cmd(0x21)
        self.write_cmd(0xC2)
        self.write_data(0x33)
        self.write_cmd(0XC5)
        self.write_data(0x00)
        self.write_data(0x1e)
        self.write_data(0x80)
        self.write_cmd(0xB1)
        self.write_data(0xB0)
        self.write_cmd(0x36)
        self.write_data(0x28)
        self.write_cmd(0XE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3a)
        self.write_data(0x56)
        self.write_data(0x4d)
        self.write_data(0x03)
        self.write_data(0x0a)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3e)
        self.write_data(0x0f)
        self.write_cmd(0XE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4d)
        self.write_data(0x06)
        self.write_data(0x0d)
        self.write_data(0x0b)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0f)
        self.write_cmd(0X3A)
        self.write_data(0x55)
        self.write_cmd(0x11)
        sleep_ms(120)
        self.write_cmd(0x29)
        
        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)
        
        self.write_cmd(0x36)
        self.write_data(0x28)
    def show_up(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x9f)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def show_down(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf) # 479 width
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0xA0) # 160 start height
        self.write_data(0x01)
        self.write_data(0x3f) # 319 end height
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)
    def draw_point(self,x,y,color):
        self.write_cmd(0x2A)

        
        self.write_data((x-2)>>8)
        self.write_data((x-2)&0xff)
        self.write_data(x>>8)
        self.write_data(x&0xff)
        
        self.write_cmd(0x2B)
        self.write_data((y-2)>>8)
        self.write_data((y-2)&0xff)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        for i in range(0,1): # 9
#             h_color =  bytearray([color>>8])
#             l_color =  bytearray([color&0xff])
            self.temp1[0] =  color>>8
            self.temp2[0] =  color&0xff

            self.spi.write(self.temp2) #l_color)
            self.spi.write(self.temp1) #h_color)
        self.cs(1)



    def touch_get(self,both=False):
        if self.irq() == 0:
            self.spi = SPI(1,5_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))            
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0,3):
                self.temp1[0]=0xd0
                self.spi.write(self.temp1)
                self.Read_data = self.temp_color
                self.spi.readinto(self.Read_data)
                sleep_us(10)
                X_Point=X_Point+(((self.Read_data[0]<<8)+self.Read_data[1])>>3)
                self.temp1[0]=0x90
                self.spi.write(self.temp1)
                self.Read_data = self.temp_color
                self.spi.readinto(self.Read_data)
                Y_Point=Y_Point+(((self.Read_data[0]<<8)+self.Read_data[1])>>3)
            X_Point=X_Point//3
            Y_Point=Y_Point//3
            
            self.tp_cs(1) 
            self.spi = SPI(1,62_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            if both:
                return [X_Point,Y_Point]
            return X_Point
        
    def show_xy(self,x1,y1,x2,y2,buffer):
        self.write_cmd(0x2A)
        self.write_data(x1 >>8 )
        self.write_data(x1 & 0x00ff)
        self.write_data(x2 >>8 )
        self.write_data(x2 & 0x00ff)   # 479 width
        
        self.write_cmd(0x2B)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0x00ff) # 160 start height
        self.write_data(y2 >> 8)
        self.write_data(y2 & 0x00ff) # 319 end height
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buffer)
        self.cs(1)
        
    def WriteDevice(self, command, data=None):
        self.temp[0] = command
        self.dc(0)
        self.cs(0)
        self.spi.write(self.temp) #(bytearray([command]))
        self.cs(1)
        if data is not None:
            self.WriteDataToDevice(data)
            
    def WriteDataToDevice(self, data):
        self.dc(1);self.cs(0);self.spi.write(data);self.cs(1)


    def WriteBlock(self, x0, y0, x1, y1, data=None):
        self.WriteDevice(COLUMN_ADDRESS_SET,None)
        self.write_data(x0 >> 8 )
        self.write_data(x0 & 0x00ff)
        self.write_data(x1 >> 8 )
        self.write_data(x1 & 0x00ff)   # 479 width
        self.WriteDevice(PAGE_ADDRESS_SET,None)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0x00ff) # 160 start height
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0x00ff) # 319 end height
        self.WriteDevice(RAM_WRITE, data)
        
#     def ReadBlock(self, x0, y0, x1, y1, data=None):   #????
#         self.WriteDevice(COLUMN_ADDRESS_SET,None)
#         self.write_data(x0 >> 8 )
#         self.write_data(x0 & 0x00ff)
#         self.write_data(x1 >> 8 )
#         self.write_data(x1 & 0x00ff)   # 479 width
#         self.WriteDevice(PAGE_ADDRESS_SET,None)
#         self.write_data(y0 >> 8)
#         self.write_data(y0 & 0x00ff) # 160 start height
#         self.write_data(y1 >> 8)
#         self.write_data(y1 & 0x00ff) # 319 end height
# #        print(x0,y0,x1,y1)
#         return self._read(RAM_READ, (x1 - x0 + 1) * (y1 - y0 + 1) * 2)        
# 
#     def _read(self, command, count): #????
#         self.dc(0)
#         self.cs(0)
#         self.spi.write(bytearray([command]))
#         data = self.spi.read(count)
#         self.cs(1)
#         return data

    def Vline(self,x,y,h,color):
        self.FillRectangle(x, y, 1, h, color)           

    def FillRectangle(self, x, y, w, h, color=None): #:, buffer=None):        
        x = min(self.width - 1, max(0, x));y = min(320 - 1, max(0, y))
        w = min(self.width - x, max(1, w));h = min(320 - y, max(1, h))        
        if color:
            self.temp_color[0] = color & 0x00ff
            self.temp_color[1] = color >> 8 
        else:
            self.temp_color[0] = 0
            self.temp_color[1] = 0
#         if color == self.RED or color == self.GREEN or color == self.BLUE or color == self.WHITE or color == self.BLACK or color == self.YELLOW or color == self.ORANGE:        
#             if color == self.RED:
#                 self.mem_buffer=self.red_buffer
#             if color == self.YELLOW:
#                 self.mem_buffer=self.yellow_buffer
#             if color == self.ORANGE:
#                 self.mem_buffer=self.orange_buffer
#             if color == self.GREEN:
#                 self.mem_buffer=self.green_buffer
#             if color == self.BLACK:
#                 self.mem_buffer=self.black_buffer
#             if color == self.WHITE:
#                 self.mem_buffer=self.white_buffer
#             if color == self.BLUE:
#                 self.mem_buffer=self.blue_buffer
#         else:
        fill_b_array(self.mem_buffer,MEMORY_BUFFER,self.temp_color[0],self.temp_color[1])
            #for i in range(MEMORY_BUFFER):
            #    self.mem_buffer[2*i]=self.temp_color[0]; self.mem_buffer[2*i+1]=self.temp_color[1]
        
        chunks = w * h // MEMORY_BUFFER
        rest = w * h % MEMORY_BUFFER
    
        self.WriteBlock(x, y, x + w - 1, y + h - 1, None)
        if chunks:
            for count in range(chunks):
                self.WriteDataToDevice(self.mem_buffer)
        if rest != 0:
            self.mv_buffer = self.mem_buffer
            self.WriteDataToDevice(self.mv_buffer)

@micropython.asm_thumb
def fill_b_array(r0,r1,r2,r3): # r0=byte array address, r1= # of words, r2,r3=data
    label(LOOP)
    strb(r2, [r0, 0]) # store low byte
    strb(r3, [r0, 1]) # store high byte
    add(r0, 2)        # add 2 to address (next 1/2 word)
    sub(r1, 1)        # dec number of words
    bgt(LOOP)         # branch if not done

                
if __name__=='__main__':
    LCD = LCD_3inch5()
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    ymax=159
    max_x = 479
    i=ymax*10000 //max_x
    LCD.FillRectangle(0,0,480,320,LCD.BLACK)
#    print(LCD.read_point(0,0,8,1)) # x,y,w,h
#    exit()
    step = 20
    colors=[LCD.RED,LCD.YELLOW,LCD.ORANGE,LCD.GREEN,LCD.BLUE]
    while(0):
        for k in range(0,step):
            x=k
            while x<max_x:
            #for x in range(k,max_x,step):
                j=(x*i)//10000
                LCD.line(x,0,max_x,j,LCD.WHITE)
                LCD.line(max_x,j,max_x-x,ymax,LCD.WHITE)
                LCD.line(max_x-x,ymax,0,ymax-j,LCD.WHITE)
                LCD.line(0,ymax-j,x,0,LCD.WHITE)
                x+=step
            LCD.show_up()
            LCD.show_down()
            LCD.fill(LCD.BLACK)
        print(gc.mem_free())
    #delta = ticks_diff(time.ticks_us(), gticks)
    #print(delta/1000000)
    #buf=bytearray(240*160*2)
    #for i in range(65535):
    #    fill_b_array(buf,len(buf)//2,i>>8,i&0xff) # r0=byte array address, r1= # of words, r2,r3=data
    #    LCD.show_xy(0,0,240,160,buf)
    #exit()
    while(1):
        gticks=ticks_us()
        for i in range(1000):
            LCD.FillRectangle(randint(0,470),randint(0,310),20,10,colors[randint(0,4)])
            #LCD.FillRectangle(randint(0,470),randint(0,310),20,10,randint(0,65535))
            #LCD.show_up()
        #print(ticks_diff(ticks_us(), gticks)//10000)


