# THE EXTREMELY FAST LINE ALGORITHM Variation E (Addition Fixed Point PreCalc)
# Copyright 2001-2, By Po-Han Lin
@micropython.viper
def draw_line( x:int, y:int, x2:int, y2:int , color:int ): 
    yLonger=False 
    shortLen=y2-y #int
    longLen=x2-x #int
    if (abs(shortLen)>abs(longLen)):
        swap=shortLen # int
        shortLen=longLen
        longLen=swap
        yLonger=True

    decInc=0 #int
    if (longLen==0):
        decInc=0
    else:
        decInc = (shortLen << 16) // longLen

    if (yLonger):
        if (longLen>0):
            longLen+=y
            j=0x8000+(x<<16) 
            while y<=longLen:
                y+=1
                LCD.draw_point(j >> 16,y,color)
                j+=decInc
                #print(0)
            return

        longLen+=y
        j=0x8000+(x<<16)
        while y>=longLen:
            y-=1
            LCD.draw_point(j >> 16,y,color)
            j-=decInc
            #y-=1
            #print(1)
        return

    if (longLen>0):
        longLen+=x
        j=0x8000+(y<<16)
        while x<=longLen:
            x+=1
            LCD.draw_point(x,j >> 16,color)
            j+=decInc
            #x+=1
            #print(2)
        return
    
    longLen+=x
    j=0x8000+(y<<16)
    while x>=longLen:
        x-=1
        LCD.draw_point(x,j >> 16,color)
        j-=decInc
    #print(3)
        
def vline(screen,x,y,length,color): #x, y, length, color
    screen.FillRectangle(x, y, length, 1, color, True)

