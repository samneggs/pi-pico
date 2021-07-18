from random import randint
from time import sleep
#from LCD_1inch14 import *

class Player:
    def __init__(self):
        self.dice = [1,2,3,4,5]
        self.keep = ["n","n","n","n","n"]
        self.turn = 1
        self.scored = [False,False,False,False,False,False]
    def roll(self):
        for i,d in enumerate(self.dice):
            if self.keep[i] != "y":
                self.dice[i] = randint(1,6)
        self.dice = sorted(self.dice)
  
class Score:
    def __init__(self,text):
        self.text = text
        self.value = 0
        self.scored = False
        

score = []
player = Player()

def score_init():
    score.append(Score("Ones  "))
    score.append(Score("Twos  "))
    score.append(Score("Threes"))
    score.append(Score("Fours "))
    score.append(Score("Fives "))
    score.append(Score("Sixes "))

def show_score(total):
    print(player.dice)
    for i in range(0,len(score)):
        if score[i].value > 0:
            print(i+1,score[i].text,score[i].value)
        else:
            print(i+1,score[i].text)
    print ("total =",total)

def new_roll():
    player.keep = ["n","n","n","n","n"]


def show_die(number,position):
    x = position*48+1
    y1 = 5
    y2 = 15
    y3 = 25
    x1 = x + y1
    x2 = x + y2
    x3 = x + y3
    dot = 9
    LCD.fill_rect(x,0,40,40,LCD.white)
    if number == 1:
        LCD.fill_rect(x2,y2,dot,dot,LCD.black)
    if number == 2:
        LCD.fill_rect(x1,y1,dot,dot,LCD.black)
        LCD.fill_rect(x3,y3,dot,dot,LCD.black)
    if number == 3:
        LCD.fill_rect(x1,y1,dot,dot,LCD.black)
        LCD.fill_rect(x2,y2,dot,dot,LCD.black)
        LCD.fill_rect(x3,y3,dot,dot,LCD.black)
    if number == 4:
        LCD.fill_rect(x1,y1,dot,dot,LCD.black)
        LCD.fill_rect(x1,y3,dot,dot,LCD.black)
        LCD.fill_rect(x3,y1,dot,dot,LCD.black)
        LCD.fill_rect(x3,y3,dot,dot,LCD.black)
    if number == 5:
        LCD.fill_rect(x1,y1,dot,dot,LCD.black)
        LCD.fill_rect(x1,y3,dot,dot,LCD.black)
        LCD.fill_rect(x3,y1,dot,dot,LCD.black)
        LCD.fill_rect(x3,y3,dot,dot,LCD.black)
        LCD.fill_rect(x2,y2,dot,dot,LCD.black)
    if number == 6:
        LCD.fill_rect(x1,y1,dot,dot,LCD.black)
        LCD.fill_rect(x1,y3,dot,dot,LCD.black)
        LCD.fill_rect(x3,y1,dot,dot,LCD.black)
        LCD.fill_rect(x3,y3,dot,dot,LCD.black)
        LCD.fill_rect(x1,y2,dot,dot,LCD.black)
        LCD.fill_rect(x3,y2,dot,dot,LCD.black)
    LCD.show()



def show_dice():
    for pos,num in enumerate(player.dice):
        show_die(num,pos)

def choose_die():
    pos = 0
    y = 48
    x = pos * y
    while (key1.value() != 0):
        if(key2.value() == 0):
            LCD.rect(x,0,y,y,LCD.black)
            x += y
            LCD.rect(x,0,y,y,LCD.green)
        if(key0.value() == 0):
            LCD.rect(x,0,y,y,LCD.black)
            x -= y
            LCD.rect(x,0,y,y,LCD.green)
        
        LCD.show()
        sleep(1)
 


score_init()
scored = 0
total = 0
pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)#max 65535
key0 = Pin(15,Pin.IN)
key1 = Pin(17,Pin.IN)
key2 = Pin(2 ,Pin.IN)
key3 = Pin(3 ,Pin.IN)

LCD = LCD_1inch14()
#color BRG
LCD.fill(LCD.black)


while player.scored.count(True) < 6:          # all scoring complete?
    new_roll()                                # reset dice
    for i in range(1,4):                      # 3 rolls
        player.roll()
        print("Roll",i)
        print(player.dice)
        show_dice()
        choose_die()
        keep = input()
        if keep == "":
            player.keep = ["y","y","y","y","y"]
        else:
            player.keep = list(keep.split())
    player.roll()
    print("Final roll")

    n=0
    scored = False
    while scored == False:
        show_score(total)
        n=int(input())
        if n>0 and n<7 and player.scored[n-1] == False:
            score[n-1].value = player.dice.count(n)*n
            player.scored[n-1] = True
            scored = player.scored.count(True)
            total += score[n-1].value
            scored = True
            show_score(total)


    