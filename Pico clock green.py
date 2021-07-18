import machine
import time, utime
from machine import Timer, Pin, I2C, WDT, ADC
from random import randint
import _thread
from rp2 import PIO, StateMachine, asm_pio
import array
from usys import exit

class Ball:
    def __init__(self):
        self.x = 2
        self.y = 1
        self.ax = 1
        self.ay = 1

ball = Ball()

set_func=machine.Pin(2,machine.Pin.IN,machine.Pin.PULL_UP)
up=machine.Pin(17,machine.Pin.IN,machine.Pin.PULL_UP)
down=machine.Pin(15,machine.Pin.IN,machine.Pin.PULL_UP)
clk=machine.Pin(10,machine.Pin.OUT) # shift data into reg
sdi=machine.Pin(11,machine.Pin.OUT) # data
le=machine.Pin(12,machine.Pin.OUT) # present full shift reg
A0=machine.Pin(16,machine.Pin.OUT) # row address line
A1=machine.Pin(18,machine.Pin.OUT) # row address line
A2=machine.Pin(22,machine.Pin.OUT) # row address line
OE=machine.Pin(13,machine.Pin.OUT) # turn on display
adc=machine.ADC(26)
temp_raw=machine.ADC(4)
address = 0x68
register = 0x00
NowTime = b'\x00\x08\x18\x06\x14\x05\x21'
w  = ["SUN","Mon","Tues","Wed","Thur","Fri","Sat"];
bus = I2C(1,scl=Pin(7),sda=Pin(6))

#1 09 17   1234 5678   1111 1111   1111 1111
#2 10 18
#3 11 19
#4 12 20
#5 13 21
#6 14 22
#7 15 23

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func


ZIKU=[
0x06,0x09,0x09,0x09,0x09,0x09,0x06,#0
0x04,0x06,0x04,0x04,0x04,0x04,0x0E,#1
0x06,0x09,0x08,0x04,0x02,0x01,0x0F,#2
0x06,0x09,0x08,0x06,0x08,0x09,0x06,#3
0x08,0x0C,0x0A,0x09,0x0F,0x08,0x08,#4
0x0F,0x01,0x07,0x08,0x08,0x09,0x06,#5
0x04,0x02,0x01,0x07,0x09,0x09,0x06,#6
0x0F,0x09,0x04,0x04,0x04,0x04,0x04,#7
0x06,0x09,0x09,0x06,0x09,0x09,0x06,#8
0x06,0x09,0x09,0x0E,0x08,0x04,0x02,#9
0x06,0x09,0x09,0x0F,0x09,0x09,0x09,#A
0x07,0x09,0x09,0x07,0x09,0x09,0x07,#B
0x06,0x09,0x01,0x01,0x01,0x09,0x06,#C
0x07,0x09,0x09,0x09,0x09,0x09,0x07,#D
0x0F,0x01,0x01,0x0F,0x01,0x01,0x0F,#E
0x0F,0x01,0x01,0x0F,0x01,0x01,0x01,#F
0x09,0x09,0x09,0x0F,0x09,0x09,0x09,#H
0x01,0x01,0x01,0x01,0x01,0x01,0x0F,#L
0x09,0x09,0x0B,0x0D,0x09,0x09,0x09,#N
0x07,0x09,0x09,0x07,0x01,0x01,0x01,#P
0x09,0x09,0x09,0x09,0x09,0x09,0x06,#U
0x00,0x03,0x03,0x00,0x03,0x03,0x00,#: #2×7
0x01,0x0C,0x12,0x02,0x02,0x12,0x0C,#摄氏度符号，5×7
0x01,0x1E,0x02,0x1E,0x02,0x02,0x02,#华氏度符号
0x00,0x00,0x00,0x00,0x00,0x00,0x00,#消隐
0x1F,0x04,0x04,0x04,0x04,0x04,0x04,#T,5*7
0x00,0x00,0x00,0x00,0x00,0x00,0x01,#"."，1×7
0x00,0x00,0x00,0x03,0x00,0x00,0x00,#"-"，2×7
0x00,0x11,0x1B,0x15,0x11,0x11,0x11,0x11,#"M"，5×7
0x00,0x04,0x04,0x02,0x02,0x02,0x01,0x01,#"/"，3×7
0x00,0x01,0x0C,0x12,0x02,0x02,0x12,0x0C,#摄氏度符号，5×7
0x00,0x01,0x1E,0x02,0x1E,0x02,0x02,0x02,#华氏度符号
#0x11,0x11,0x11,0x11,0x11,0x0A,0x04, #"V"，5×7
#0x11,0x11,0x11,0x15,0x15,0x1B,0x11, #"W"，5×7
#以下是数码管字体
0x0F,0x09,0x09,0x09,0x09,0x09,0x0F, #0
0x08,0x08,0x08,0x08,0x08,0x08,0x08, #1
0x0F,0x08,0x08,0x0F,0x01,0x01,0x0F, #2
0x0F,0x08,0x08,0x0F,0x08,0x08,0x0F, #3
0x09,0x09,0x09,0x0F,0x08,0x08,0x08, #4
0x0F,0x01,0x01,0x0F,0x08,0x08,0x0F, #5
0x0F,0x01,0x01,0x0F,0x09,0x09,0x0F, #6
0x0F,0x08,0x08,0x08,0x08,0x08,0x08, #7
0x0F,0x09,0x09,0x0F,0x09,0x09,0x0F, #8
0x0F,0x09,0x09,0x0F,0x08,0x08,0x0F, #9
0x0F,0x09,0x09,0x0F,0x09,0x09,0x09, #A
0x01,0x01,0x01,0x0F,0x09,0x09,0x0F, #B
0x0F,0x01,0x01,0x01,0x01,0x01,0x0F, #C
0x08,0x08,0x08,0x0F,0x09,0x09,0x0F, #D
0x0F,0x01,0x01,0x0F,0x01,0x01,0x0F, #E
0x0F,0x01,0x01,0x0F,0x01,0x01,0x01, #F
0x09,0x09,0x09,0x0F,0x09,0x09,0x09, #H
0x01,0x01,0x01,0x01,0x01,0x01,0x0F, #L
0x0F,0x09,0x09,0x09,0x09,0x09,0x09, #N
0x0F,0x09,0x09,0x0F,0x01,0x01,0x01, #P
0x09,0x09,0x09,0x09,0x09,0x09,0x0F, #U
0x00,0x03,0x03,0x00,0x03,0x03,0x00, #: #2×7
0x01,0x1E,0x02,0x02,0x02,0x02,0x1E, #摄氏度符号，5×7
0x01,0x1E,0x02,0x1E,0x02,0x02,0x02, #华氏度符号
0x00,0x00,0x00,0x00,0x00,0x00,0x00, #消隐
0x1F,0x04,0x04,0x04,0x04,0x04,0x04, #T,5*7
0x00,0x00,0x00,0x00,0x00,0x00,0x01, #"."，2×7
0x00,0x00,0x00,0x03,0x00,0x00,0x00, #"-"，2×7
0x00,0x11,0x1B,0x15,0x11,0x11,0x11,0x11, #"M"，5×7
0x00,0x04,0x04,0x02,0x02,0x02,0x01,0x01, #"/"，3×7
0x00,0x01,0x0C,0x12,0x02,0x02,0x12,0x0C, #摄氏度符号，5×7
0x00,0x01,0x1E,0x02,0x1E,0x02,0x02,0x02] #华氏度符号
#0x11,0x11,0x11,0x11,0x11,0x11,0x1F, #"V"，5×7
#0x11,0x11,0x11,0x15,0x15,0x1B,0x11, #"W"，5×7
# };

Z = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','H','L','N','P','U',':',' ',' ',' ','T','.','-','M','/',' ',' ']

def ds3231SetTime():
    bus.writeto_mem(int(address),int(register),NowTime)

def ds3231ReadTime():
    return bus.readfrom_mem(int(address),int(register),7)

@asm_pio(set_init=PIO.OUT_HIGH,autopull=True, pull_thresh=12, out_shiftdir=PIO.SHIFT_RIGHT) # high = off
def led_dimmed():
    label("main loop")
    pull()                 # wait for input from upython
    out(x,12)               # transfer to X, 12 bits
    jmp(not_x,"bright")    # if zero jump to bright
    #set(x,31)             # x=0 test force dimm
    label("dim loop")
    jmp(not_x,"skip")      # if zero jump to skip
    set(pins, 0) [1]       # turn on LEDs
    jmp(x_dec, "dim loop") #x-1 and loop
    set(pins, 1)           # turn off LEDs
    jmp("main loop")       # start over
    label("skip")         
    set(pins, 1)           # turn off LEDs
    jmp("main loop")       # start over
    label("bright")
    set(pins, 0)           #turn on leds
    jmp("main loop")
    
 

sm1 = StateMachine(1, led_dimmed, freq=10_000_000, set_base=Pin(13))
sm1.active(1)

@asm_pio(sideset_init=(PIO.OUT_LOW), out_init=(PIO.OUT_LOW), autopull=True, pull_thresh=31, out_shiftdir=PIO.SHIFT_RIGHT) # high = off
def led_row():

    label("loop")
    out(pins,1)        .side(1)
    nop()              .side(0)
    jmp("loop")
    

sm4 = StateMachine(2, led_row, freq=40_000_000, out_base=Pin(11),  sideset_base=Pin(10)) #10=clk, 11=data
sm4.active(2)


def clr():       
    sdi.value(0)
    for cnt in range(0,8):
        for _ in range(0,24):
            clk.value(1)
            clk.value(0)   
        le.value(1)
        le.value(0)        
        

def send_data(data):               # shift 8 bits into line
    for _ in range(0,8):        
        clk.value(0)
        sdi.value(0)
        if data & 0x01:
            sdi.value(1)           # load bit into fifo
        data>>=1
        clk.value(1)               # shift fifo 

def send_line():
    global CS_cnt,dark,layer,strobe
    #OE.value(1)                    # turn off display during bit changing        
    sm1.put(0x001)                      #<--/
    le.value(1)                    # show fifo, row of display
    le.value(0)
    if CS_cnt&0x01 :               # set row
        A0.value(1)
    else:
        A0.value(0)
    if CS_cnt&0x02 :
        A1.value(1)
    else:
        A1.value(0)
    if CS_cnt&0x04 :
        A2.value(1)
    else:
        A2.value(0)
    if dark > 0 :
        sm1.put(dark) #(31 << 27)          #  1-0xfff=dimmed
        
    else:
        sm1.put(0) # (1<<(strobe+4))           # 0=bright       
        #strobe=7-CS_cnt        
        
def init_disp_buf():
    for _ in range(0,112):
        disp_buf.append(0x00)
        temp_buf.append(0x00)
    
    for _ in range(0,10):
        disp_bufs.append(list(0x00 for _ in range(112)))


def clr_disp_buf():
    for i in range(0,len(disp_buf)-1):
        disp_buf[i] = 0x00
    
def display_char(x,dis_charSTR):
    dis_char=0x00
    j=int(x/8)                       #To display the number of the dot matrix
    k=x%8                            #Start to display at which bit
    dis_char= Z.index(dis_charSTR)   #lookup char position
    for i in range(1,8):
        if (k>0):
            disp_buf[8*j+i]=(disp_buf[8*j+i]&(0xff>>(8-k)))|((ZIKU[dis_char*7+i-1])<<k) #Reserve the required data bits
            if (j<(int(len(disp_buf)/8))-1):
                disp_buf[8*j+8+i]=(disp_buf[8*j+8+i]&(0xff<<(8-k)))|((ZIKU[dis_char*7+i-1])>> (8-k))
        else:
            disp_buf[8*j+i]=(ZIKU[dis_char*7+i-1])


def display_timer(timer): # display one line of data
    global CS_cnt,layer,temp_buf
#    wdt.feed() #                    Watchdog timer keep alive
    if CS_cnt>7:
        CS_cnt=0
        layer+=1
        if layer>9:
            layer=0
    temp_buf = disp_buf #s[layer]
#     send_data(temp_buf[0 + CS_cnt])
#     send_data(temp_buf[8 + CS_cnt])
#     send_data(temp_buf[16+ CS_cnt])
#     send_data(temp_buf[24+ CS_cnt])
#     send_line()
    sm4.put(temp_buf[0 + CS_cnt] | temp_buf[8 + CS_cnt]<<8 | temp_buf[16+ CS_cnt]<<16 | temp_buf[24+ CS_cnt]<<24)
    #sm4.put(0b1101_1111_1111_1111_1111_1010)
    send_line()
    CS_cnt+=1

def read_clock():
    global t
    t = time.localtime()

def set_localtime():
    t = ds3231ReadTime()
    tstring=str("20%x %02x %02x %02x %02x %02x" %(t[6],t[5],t[4],t[2],t[1],t[0]))+' 0 0'
    givenTime = utime.mktime(list(map(int, tuple(tstring.split(' ')))))
    ctime=utime.localtime(givenTime)
    setup_0 = (ctime[0] << 12) | (ctime[1] << 8) | ctime[2]
    setup_1 =  (ctime[3] << 16) | (ctime[4] << 8) | ctime[5]
    setup_1 =  setup_1 |  (((ctime[6] + 1) % 7) << 24)

    # register RTC address
    rtc_base_mem = 0x4005c000
    atomic_bitmask_set = 0x2000

    machine.mem32[rtc_base_mem + 4] = setup_0
    machine.mem32[rtc_base_mem + 8] = setup_1
    machine.mem8[rtc_base_mem + atomic_bitmask_set + 0xc] = 0x10


def show_time(hr10,hr00,min10,min00):
    bounceTMR.deinit()
    clr_disp_buf()
    if hr10>0:
        display_char(1,str(hr10))
    display_char(6,str(hr00))        
    display_char(11,":")
    display_char(14,str(min10))
    display_char(19,str(min00))

def show_temp(temp):
    clr_disp_buf()
    display_char(7,str(int(temp/10)))
    display_char(12,str(int(temp%10)))
 

def plot(x,y,c,l):   # c=0 unplot
    pos = (((x-1)//8+1)*8-7)+(y-1)
    bit = ((x-1)%8)    
    byte = 0x01<<(bit)  # 0-7
    if c == 1:
        disp_buf[pos] = disp_buf[pos] | byte
    else:
        disp_buf[pos] = disp_buf[pos] & ~byte
#     for i in range(0,l):
#         disp_bufs[i]=disp_buf[:]     
    


def bounce(timer):
    global bounce_count
    if bounce_count == 0:
        clr_disp_buf()
    if bounce_count > 70:
        bounceTMR.deinit()
        bounce_count = -1
    bounce_count+=1
    ball.x = ball.x + ball.ax
    ball.y = ball.y + ball.ay
    if ball.x < 3:
        ball.x = 3
        ball.ax = -ball.ax
    if ball.x > 24:
        ball.x = 23
        ball.ax = -ball.ax
    if ball.y < 1:
        ball.y = 2
        ball.ay = -ball.ay
    if ball.y > 6:
        ball.y = 7
        ball.ay = -ball.ay
    
    plot(ball.x,ball.y,1,9-ball.y)
    
        

def fill(byte):
    for i in range(1,8):
        disp_buf[i] = byte & 0b11111100
        disp_buf[i+8] = byte
        disp_buf[i+16] = byte

def invert():
    for i in range(1,8):
        disp_buf[i] = ~disp_buf[i] & 0b11111100
        disp_buf[i+8] = ~disp_buf[i+8]
        disp_buf[i+16] = ~disp_buf[i+16]


def dissolve():
    for _ in range(7000):        
        plot(randint(3,24),randint(1,7),randint(0,1),randint(0,10))
    clr_disp_buf()

def buttons():
    global dark,mode
    if up.value() == 0:
        dark+=1
        if dark>0xfff:
            dark=0xfff
    if down.value() == 0:
        dark-=1
        if dark<1:
            dark=1
    if set_func.value()==0:
        mode=-mode
    #print(dark, up.value(), down.value(),end='')
        
# @timed_function
def fall(timer):
    global xpos,seconds
    for i in range(3,25):
        y=xpos[i]
        if y>7:             # y>7
            if randint(0,3)==0:
                xpos[i]=1
                plot(i,1,1,1)
        elif y < 7:         # y<7
            plot(i,y,0,1)
            xpos[i]+=1                    
            plot(i,xpos[i],1,1)
        else:                     # y=7                   
            plot(i,7,0,1)
            xpos[i]+=1
    if seconds<21:
        clr_disp_buf()
        fallTMR.deinit()  


dark = 0
#wdt = WDT(timeout=8300) # Watchdog timer reset
disp_buf = []
disp_bufs = []
temp_buf = []
t = []
clr()
CS_cnt=0
seconds=0
lop = 0
bounce_count = 0
layer = 0
strobe = 0
mode = 1
xpos=bytearray(30) 

init_disp_buf()

def second_thread():    
    tim = Timer()
    tim.init(freq=400, mode=Timer.PERIODIC, callback=display_timer)      # 400 = 50Hz x 8 rows   

#tim = Timer()
#tim.init(freq=400, mode=Timer.PERIODIC, callback=display_timer)      # 400 = 50Hz x 8 rows   


bounceTMR = Timer()
#bounceTMR.init(freq=10, mode=Timer.PERIODIC, callback=bounce)          

fallTMR = Timer()
#fallTMR.init(freq=15, mode=Timer.PERIODIC, callback=fall) 

_thread.start_new_thread(second_thread, ())


t=[0,0,0,0,0]

#ds3231SetTime()  # Uncomment to set clock
set_localtime()


def loop():
    global dark,seconds,mode
    oldt=t[4]
    read_clock()
    newt=t[4]
    min10=int(t[4]/10)
    min00=t[4]%10
    if t[3]>12:
        hr=t[3]-12
    else:
        hr=t[3]
    hr10=int(hr/10)
    hr00=hr%10
    if oldt != newt :        
        show_time(hr10,hr00,min10,min00)
    #time.sleep(1)
    for i in range(100000):
        pass
    light=adc.read_u16()
    if light>60000 :
        if dark == 0 : dark = 1
    else:
        dark=0
    buttons()
    seconds+=1
    if seconds == 5:
        temp_scaled = (27 - (( (temp_raw.read_u16() * 3.3 / 65535) - 0.706)/0.001721
))*9/5+32
        show_temp(temp_scaled)
    if seconds==10:
        show_time(hr10,hr00,min10,min00)
#        seconds=0
    if seconds == 15 and mode == 1:
        seconds = 0
    if seconds==15: 
        fill(0xff)
    if seconds == 17: 
        dissolve()
    if seconds == 18:        
        bounceTMR.init(freq=15, mode=Timer.PERIODIC, callback=bounce)
    if seconds == 22:
        fallTMR.init(freq=15, mode=Timer.PERIODIC, callback=fall)
    if seconds == 24:
        seconds=4


if __name__ == '__main__':
    try:
        while True:
            
            loop() 
    # When 'Ctrl+C' is pressed, the following will be  executed.
    except KeyboardInterrupt:
        #tim.deinit()
        
        bounceTMR.deinit()
        #clr()
        print(seconds,"All done.")
          
    