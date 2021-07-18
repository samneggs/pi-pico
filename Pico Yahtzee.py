from LCD_1inch14 import *
 
if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    LCD = LCD_1inch14()
    #color BRG
    LCD.fill(LCD.black)
 
    LCD.show()
    LCD.text("Raspberry Pi Pico",60,40,LCD.red)
    LCD.text("PicoGo",60,60,LCD.green)
    LCD.text("Pico-LCD-1.14",60,80,LCD.blue)
    
    
    
    LCD.hline(10,10,220,LCD.blue)
    LCD.hline(10,125,220,LCD.blue)
    LCD.vline(10,10,115,LCD.blue)
    LCD.vline(230,10,115,LCD.blue)
    
    
    LCD.rect(12,12,20,20,LCD.red)
    LCD.rect(12,103,20,20,LCD.red)
    LCD.rect(208,12,20,20,LCD.red)
    LCD.rect(208,103,20,20,LCD.red)
    
    LCD.show()
    key0 = Pin(15,Pin.IN)
    key1 = Pin(17,Pin.IN)
    key2 = Pin(2 ,Pin.IN)
    key3 = Pin(3 ,Pin.IN)
    while(1):
        if(key0.value() == 0):
            LCD.fill_rect(12,12,20,20,LCD.red)
        else :
            LCD.fill_rect(12,12,20,20,LCD.white)
            LCD.rect(12,12,20,20,LCD.red)
            
        if(key1.value() == 0):
            LCD.fill_rect(12,103,20,20,LCD.red)
        else :
            LCD.fill_rect(12,103,20,20,LCD.white)
            LCD.rect(12,103,20,20,LCD.red)
            
        if(key2.value() == 0):
            LCD.fill_rect(208,12,20,20,LCD.red)
        else :
            LCD.fill_rect(208,12,20,20,LCD.white)
            LCD.rect(208,12,20,20,LCD.red)
            
        if(key3.value() == 0):
            LCD.fill_rect(208,103,20,20,LCD.red)
        else :
            LCD.fill_rect(208,103,20,20,LCD.white)
            LCD.rect(208,103,20,20,LCD.red)
            
            
        LCD.show()
    time.sleep(1)
    LCD.fill(0xFFFF)

