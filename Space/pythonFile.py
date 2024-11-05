import pygame, sys
import random
import time
import numpy as np
import math
from pygame.locals import *
import math
import webbrowser

# Initialize Pygame
pygame.init()

# Screen dimensions
screenProperties={
    "W":1000,
    "H":600
}

score=0

player={# these vause will be set each game 
    "direction":0,      # direction that the player spins  
    "turn speed":0,     #how fast the player turns
    "slowDown":0,       #how fast the momentem of the player turn slows down

    "charge":0,         #the current charge of the player attack
    "chargespeed":0,    #how much it increses 
    "maxDamage":0,      #max charge

    "Maxfuel":0,        #max amount of fuel
    "fuel":0,           #the current fuel

    "maxHP":0,          #max amount of hp
    "hp":0,             #the current hp
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Create the display surface
WINDOW = pygame.display.set_mode((screenProperties["W"], screenProperties["H"]))
pygame.display.set_caption("Asteroid Belt")
#sprite groups 
all_sprites_list = pygame.sprite.Group()
object_List = pygame.sprite.Group()
star_list = pygame.sprite.Group()
hpPow_list = pygame.sprite.Group()
Pow_list = pygame.sprite.Group()
shootlist = pygame.sprite.Group()

# Define cube vertices with a scale of 1
vertices = [
    [1, 1, 1],
    [1, -1, 1],
    [-1, -1, 1],
    [-1, 1, 1],
    [1, 1, -1],
    [1, -1, -1],
    [-1, -1, -1],
    [-1, 1, -1],
]
# edges that connect the vertices
edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 0],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 4],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7],
]
# faces that connect the vertices
face=[
    [0,1,2,3],
    [0,3,7,4],
    [4,5,1,0,],
    [4,5,6,7],
    [6,5,1,2],
    [6,2,3,1],
]

# angles[x rotation , y rotation, z rotation]
playing=True
events = list(pygame.event.get())


#this is called in every loop prevent a runtime error 
def ext():
    global playing
    global events
    events = list(pygame.event.get())
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            playing=False

# give an angle and hypotenuse and returns the other sides (x,y)
def baseHeight(deg,r,ofset=False):    
    # math.cos and math.sin only take radians
    x = r * math.cos(math.radians(deg))
    y = r * math.sin(math.radians(deg))
    if ofset:
        return (x+screenProperties["W"]//2, y+screenProperties["H"]//2)

    return (x, y)


#these functions are used return an matrix 
def rotationX(xR):
    rotation_matrix_x = np.array([[1, 0, 0, 0                       ], 
                                  [0, math.cos(xR),-math.sin(xR), 0 ], 
                                  [0, math.sin(xR), math.cos(xR), 0 ],
                                  [0, 0, 0, 1                       ]])
    return rotation_matrix_x
    
def rotationY(yR):
    rotation_matrix_y = np.array([[math.cos(yR), 0, math.sin(yR), 0 ],
                                [0, 1, 0, 0                         ], 
                                [-math.sin(yR), 0, math.cos(yR), 0  ],
                                [0, 0, 0, 1                         ]])
    return rotation_matrix_y
    
def rotationZ(zR):
    rotation_matrix_z = np.array([[math.cos(zR), -math.sin(zR), 0, 0 ],
                                  [math.sin(zR), math.cos(zR), 0, 0  ],
                                  [0, 0, 1, 0                        ],
                                  [0, 0, 0, 1                        ]])
    return rotation_matrix_z



# creates a dot that goes in a direction and back to the center after a specified point 
class stars(pygame.sprite.Sprite):
    def __init__(self,deg,speed,raid,size,transparent):
        super().__init__()
        
        #self.image = pygame.transform.scale(pygame.image.load(image),(20,20))
        self.image = pygame.Surface((size,size))
        self.image.fill([245,245,245])
        self.image.set_alpha(transparent)
        self.rect = self.image.get_rect()
        self.deg=deg #flip it 
        self.r=raid
        self.speed=speed
        self.rect.x=screenProperties["W"]/4
        self.rect.y=0
        self.angle=0
        
    def update(self):
        self.r+=self.speed
        self.deg-=(player["direction"])
        self.rect.center = (baseHeight(self.deg,self.r,True))
        x,y=self.rect.center
        # if the start hits the end of the screen it goes to the center 
        if self.r>500:
            self.r=0


#this code is simmeler to the star class but it has an ofset and slowly loses transparency unlitll it dies
class boom(pygame.sprite.Sprite):

    def __init__(self,deg,speed,raid,size,offsetX,offsetY,colour,lim=40,outline=(255,255,255)):
        super().__init__()
        self.time=time.time()
        #self.image = pygame.transform.scale(pygame.image.load(image),(20,20))
        self.image = pygame.Surface((size,size))
        self.image.fill(outline)#                                           fill the box in with a colour
        self.image.fill(colour,self.image.get_rect().inflate(-1.3, -1.3))#  create a box with a smaller size to create an outline 
        self.rect = self.image.get_rect()
        self.deg=deg  
        self.r=raid
        self.speed=speed
        self.rect.x=screenProperties["W"]/4
        self.rect.y=0
        self.angle=0
        self.alpha=100
        self.Xoff=offsetX
        self.Yoff=offsetY
        self.limit=lim

    def update(self):
        self.deg-=(player["direction"])
        x,y=(baseHeight(self.deg,self.r))
        self.rect.center = (x+self.Xoff, y+self.Yoff)
        if self.r>self.limit:
            self.r=0
        self.r+=1
        self.alpha-=4
        self.image.set_alpha(self.alpha)
        if self.alpha<=0:
            self.kill()



#class to create a 3d cube
class cube(pygame.sprite.Sprite):
    # if cube is used as a player bullet the parameter power will be given
    def __init__(self,deg,speed,power=None):
        
        super().__init__()
        self.image = pygame.Surface((20,20))
        self.time=time.time()
        self.rect = pygame.Rect(3,3, 2, 3  )
        self.behind=False
        self.angles = [0, 0, 0]  
        self.hp=1.0
        self.sizeAprox=1# this is equals to the width 
        self.deg=deg 
        self.r=300
        self.speed=speed
        self.power=power
        self.cube_z = -50
        self.radius=7
        self.Colour=(120,24,154,40)
        self.linecol=(0,93,0)
        if power:
            self.power=(power/player["maxDamage"])*1.35
        self.instantKill=False

        if self.power: #for bullet 
            self.cube_z = -170
            self.radius=20
            self.linecol=(WHITE)
            self.Colour=(20,24,54,50)
            
            if self.power>1:# for yellow bullet
                self.linecol=(255, 255, 0)
                self.instantKill=True
            

        self.cube_x, self.cube_y =baseHeight(0,self.radius)
        self.allXpoints=[]
        self.allYpoints=[]


    #this function gets xyz points and makes them into xy points   
    def projectP(self,vertex,rotations):
        xR,yR,zR = rotations
        x, y, z =  vertex

        # Translation matrix to move the cube's center to the origin 
        translation_matrix_1 = np.array([
            [1, 0, 0, -self.cube_x],
            [0, 1, 0, -self.cube_y],
            [0, 0, 1, -self.cube_z],
            [0, 0, 0, 1           ]
        ])
        # Rotation matrix for x, y and z:
        rotation_matrix_x = rotationX(xR)
        rotation_matrix_y = rotationY(yR)
        rotation_matrix_z = rotationZ(zR)
        # Translation matrix to move the cube's back to its positon
        translation_matrix_2 = np.array([
            [1, 0, 0, self.cube_x],
            [0, 1, 0, self.cube_y],
            [0, 0, 1, self.cube_z],
            [0, 0, 0, 1          ]
        ])

        # Apply translations and rotations using matrix multiplication (useing numpy to make this easy)
        transformed_vertex= np.dot(translation_matrix_2,  #mutiply xyz to the orignal postion by adding xyx ofsets
                            np.dot(rotation_matrix_z,     #mutiply rotation z to match the angles rotation dregee
                            np.dot(rotation_matrix_y,     #mutiply rotation y to match the angles rotation dregee
                            np.dot(rotation_matrix_x,     #mutiply rotation x to match the angles rotation dregee
                            np.dot(translation_matrix_1,  #mutiply xyz to the center by minus the xyx ofsets 
                                
                            np.array([x, y, z, 1])        # < apply to the points given 

                            )))))

        depth = 180
        #new xyz from the transformed_vertex
        x=transformed_vertex[0]
        y=transformed_vertex[1]
        z=transformed_vertex[2]
        
        # this is used to avoid a divide by zero error 
        if depth + z==0:
            scale = depth / 399
        else:
            scale = depth / (depth + z)
        
        #remove cube object if its behind the player  
        if scale-1.3<0:
            self.behind=True
        #aply the scale 
        x2d = x * scale + screenProperties["W"] / 2
        y2d = -y * scale + screenProperties["H"] / 2

        return (x2d, y2d)
    

    # exploade the object 
    def exp(self,colour,line):
        boomX,boomY=self.rect.center

        #use the "sizeAprox" to see how intense the explostion will be (the closer the bigger)
        for i in range(int(self.sizeAprox*1.5)):
            randomDeg=random.choice([ i for i in range(0, 360,10)])
            randomraid=random.choice([ i for i in range(0, 40,3)])

            bang=boom(randomDeg,0.3,randomraid,self.sizeAprox*0.6,boomX,boomY,colour,self.sizeAprox*1.3,line)
            star_list.add(bang)
            all_sprites_list.add(bang)


    def update(self):
        global score
        if self.power:
            self.angles[0] += 4
            self.angles[1] += 1.3
            for box in object_List:# if the object colides and 
                if self.rect.colliderect(box.rect):
                    if not self.instantKill:
                        self.kill()

        else:#astroid
            for box in shootlist:                
                if self.rect.colliderect(box.rect):
                    if box.instantKill:
                        self.kill()
                    #damage the astroid
                    self.hp-=box.power
                    self.speed*=0.5

        if self.hp<=0:
            score+=1
            self.speed=0                
            self.exp(self.Colour,self.linecol)
            self.kill()

        self.cube_x, self.cube_y = baseHeight(self.deg,self.radius) #set the x and y postion to the degree  and radius
        self.deg+=player["direction"]# move the deg depending on the player

        self.angles[2]=math.radians(self.deg)# set the z rotation to make it face the center

        self.cube_z-=self.speed

        #after 10 seconds the box die 
        if self.time+10<time.time():
            self.kill()


    def drawS(self, surface):        
        #get all of the x and y points
        self.allXpoints=[]
        self.allYpoints=[]
        for point in vertices:
            Allx,Ally=self.projectP((point[0] + self.cube_x, point[1] + self.cube_y, point[2] +self.cube_z), self.angles )
            self.allXpoints.append(Allx)
            self.allYpoints.append(Ally)

        if self.behind:
            self.kill()
        else:
            for side in face:
                
                point_1 = self.projectP((vertices[side[0]][0] + self.cube_x, vertices[side[0]][1] + self.cube_y, vertices[side[0]][2] +self.cube_z), self.angles )
                point_2 = self.projectP((vertices[side[1]][0] + self.cube_x, vertices[side[1]][1] + self.cube_y, vertices[side[1]][2] +self.cube_z), self.angles )
                point_3 = self.projectP((vertices[side[2]][0] + self.cube_x, vertices[side[2]][1] + self.cube_y, vertices[side[2]][2] +self.cube_z), self.angles )
                point_4 = self.projectP((vertices[side[3]][0] + self.cube_x, vertices[side[3]][1] + self.cube_y, vertices[side[3]][2] +self.cube_z), self.angles )

                if self.behind: #re cheack if its behind every time the a xy point is made to stop large numbers 
                    return
                else:
                    pygame.draw.polygon(surface, self.Colour, (point_1,point_2,point_3,point_4))
                    #outline     
            for edge in edges:
                start_x, start_y = self.projectP((vertices[edge[0]][0] + self.cube_x, vertices[edge[0]][1] + self.cube_y, vertices[edge[0]][2] +self.cube_z),self.angles)
                end_x, end_y = self.projectP((vertices[edge[1]][0] + self.cube_x, vertices[edge[1]][1] + self.cube_y, vertices[edge[1]][2] +self.cube_z),self.angles)                

                if self.behind: 
                    return
                else:
                    pygame.draw.line(surface, self.linecol, (start_x, start_y), (end_x, end_y), 2)


            #get the width and height from the x and y points collected  
            hitBoxW = max(self.allXpoints) -min(self.allXpoints)
            hitBoxH = max(self.allYpoints)-min(self.allYpoints)
            #set the postion of the hit box 
            self.rect.topleft= (min(self.allXpoints), min(self.allYpoints)) 
            #set the width and height
            self.rect.width=hitBoxW
            self.rect.height=hitBoxH

            self.sizeAprox=hitBoxW
            self.image = pygame.Surface(  ( hitBoxW, hitBoxH )  )

           
# draws a button on the screen and a border when hover over, when clicked it will return True
def button(text,x,y):
    fontObj = pygame.font.Font(None, 55)

    outLine=10
    playText = fontObj.render(text, True, WHITE, None)
    #make it in the center
    x=x-playText.get_width()//2
    y=y-playText.get_height()//2

    btn=pygame.Rect(x,y, playText.get_rect().width+40, 35+20)

    if btn.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(WINDOW, WHITE, (x-20-outLine//2,y-10-outLine//2,playText.get_rect().width+40+outLine,35+20+outLine),2,3,3,3,)
        if pygame.mouse.get_pressed()[0] == 1 :
            return True
    pygame.draw.rect(WINDOW, WHITE, (x-20,y-10,playText.get_rect().width+40,35+20),2,3,3,3,)
    WINDOW.blit(playText,(x,y))

    return False
                
#draws the ship and detect collision of the ship 
def Ship():
    # Ship vertices
    ship_vertices = [
        [0, -50 // 2],
        [50 // 2, 50 // 2],
        [0, 50 // 3],
        [-50 // 2, 50 // 2],
    ]
    pygame.draw.polygon(WINDOW, (0,0,144), [(x + screenProperties["W"]//2, y + 500) for x, y in ship_vertices])#make the blue part of the ship (the for loop adds the coordinates form the ship_vertices with an offset)       
    pygame.draw.polygon(WINDOW, (170,0,0),[(screenProperties["W"]//2+10 , 518),(screenProperties["W"]//2, 528),(screenProperties["W"]//2-10 , 518),(screenProperties["W"]//2, 518)])
    # make white lines to add detail
    pygame.draw.line(WINDOW, WHITE,(screenProperties["W"]//2, 475),(screenProperties["W"]//2, 518),2)
    pygame.draw.line(WINDOW, WHITE,(screenProperties["W"]//2, 475),(screenProperties["W"]//2-10 , 518),2)
    pygame.draw.line(WINDOW, WHITE,(screenProperties["W"]//2, 475),(screenProperties["W"]//2+10 , 518),2)
    pygame.draw.line(WINDOW, WHITE,(screenProperties["W"]//2-10 , 518),(screenProperties["W"]//2, 528),2)
    pygame.draw.line(WINDOW, WHITE,(screenProperties["W"]//2+10 , 518),(screenProperties["W"]//2, 528),2)
    pygame.draw.polygon(WINDOW, WHITE, [(x + screenProperties["W"]//2, y + 500) for x, y in ship_vertices],2)#make a white version of the ship but bigger to make a outline  

    #player hit box
    player_rect = pygame.Rect(screenProperties["W"]//2-25,500-25,45,45)
    for obj in object_List:
        if player_rect.colliderect(obj.rect):
            obj.rect.height=0
            obj.rect.width=0
            #explode the object if it collides
            obj.exp((20,24,54,50),(WHITE))
            player["hp"]-=0.3



enemyRate = 3
start_time = time.time()
end_time = start_time + enemyRate
addDif=time.time()+10
# creates a astroid every "enemyRate" seconds  and adds 7% difucalty every 10 seconds 
def createEnemy(start=True):
    global start_time
    global end_time
    global enemyRate
    global addDif
    minSpeed=10
    maxSpeed=20     
    randomDeg=random.choice([ i for i in range(0, 360,30)])# gap of 30 deg to prevent overlaping 
    randomSpeed=random.choice([(rand/10 ) for rand in range(minSpeed,maxSpeed)])# range function does not work with floats so I made rand/10
    
    if start:
        if(end_time<time.time()):
            Obj = cube(randomDeg,randomSpeed)
            object_List.add(Obj)
            all_sprites_list.add(Obj) 

            start_time = time.time()
            end_time = start_time + enemyRate 
        
        if addDif<time.time():
            enemyRate*=0.93
            addDif=time.time()+4


# makes a bullet 
def playerSoot(power):
    player["fuel"]-=(power/player["maxDamage"])
    bulet = cube(270,-6,power)
    all_sprites_list.add(bulet) 
    shootlist.add(bulet)


# creates 3 layers of stars
def drawStars():
    star_list.empty()
    for i in range(70):
        randomDeg=random.choice([ i for i in range(0, 360,10)])
        randomraid=random.choice([ i for i in range(0, screenProperties["H"],3)])# less of a gap for the more far 
        #randomDistance=random.choice([i for i in range(0,5)])
        star=stars(randomDeg,0.1,randomraid,2,30)
        star_list.add(star)
        all_sprites_list.add(star)
    for i in range(25):
        randomDeg=random.choice([ i for i in range(0, 360,10)])
        randomraid=random.choice([ i for i in range(0, screenProperties["H"],3)])# less of a gap for the more far 
        #randomDistance=random.choice([i for i in range(0,5)])
        star=stars(randomDeg,0.2,randomraid,3,60)
        star_list.add(star)
        all_sprites_list.add(star)
    for i in range(20):
        randomDeg=random.choice([ i for i in range(0, 360,10)])
        randomraid=random.choice([ i for i in range(0, screenProperties["H"],3)])# less of a gap for the more far 
        #randomDistance=random.choice([i for i in range(0,5)])
        star=stars(randomDeg,0.8,randomraid,4,70)
        star_list.add(star)
        all_sprites_list.add(star)        


#the main game returns the result of the game
def mainGame():
    global playing
    global enemyRate 
    global score
    bgRotate=0
    charging=False
    result=""
    drawStars()
    startdelay=time.time()+3
    removefuel=time.time()+1
    
    
    fontObj = pygame.font.Font(None, 55)
    #set the valuse to start
    player["direction"]=0
    player["turn speed"]=4    
    player["slowDown"]=0.5  
    player["charge"]=0
    player["chargespeed"]=2   
    player["maxDamage"]=40
    player["Maxfuel"]=30
    player["fuel"]=30
    player["maxHP"]=3
    player["hp"]=3
    enemyRate=3
    score=0

    HPbar=player["hp"]
    object_List.empty()
    all_sprites_list.empty()
    while playing:
        ext()      
        # in the start give the player a 3 second break
        if time.time()<startdelay:
            createEnemy(False)
        else:
            createEnemy()

        #reduce the fuel as the game plays 
        if time.time()<removefuel:
            removefuel=time.time()+1
            player["fuel"]-=0.002

        pressed = pygame.key.get_pressed()
        # make the player direction negitive for left and positive for right, the objects on screen move by depending on the player direction 
        if (pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) :
            player["direction"]=-player["turn speed"]
        elif (pressed[pygame.K_LEFT] or pressed[pygame.K_a]) :
            player["direction"]=player["turn speed"]

        else:#if no key is being pressed the momentum slows down and gets closer to 0 to make movement smooth 
            if player["direction"]>0: 
                player["direction"]-=player["slowDown"]
            elif player["direction"]<0: 
                player["direction"]+=player["slowDown"]

        #HPbar is the same as player hp but decresses more slowly 
        if HPbar>player["hp"]:
            HPbar-=0.1

        #make the player charge when space is clicked and shoot when space is reslesed 
        for event in events:
            
            if event.type == pygame.KEYDOWN:                
                if event.key == pygame.K_SPACE:
                    charging = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    charging = False
                    playerSoot(player["charge"])  
                    player["charge"]=0
        #add charging if less then the max charge
        if charging:
            if player["charge"]<player["maxDamage"]:
                player["charge"]+=player["chargespeed"]
        
        #update/draw lists 
        all_sprites_list.update()
        star_list.update()
        Pow_list.update()
        hpPow_list.update()
        star_list.draw(WINDOW)
        object_List.update()
        object_List.draw(WINDOW)
        shootlist.update()
        shootlist.draw(WINDOW)
        for box in object_List:
            box.drawS(WINDOW)
        for box in shootlist:
            box.drawS(WINDOW)
        for box in hpPow_list:
            box.drawS(WINDOW)
        for box in Pow_list:
            box.drawS(WINDOW)        
        star_list.update()
        star_list.draw(WINDOW)

        pygame.display.flip()
        WINDOW.fill(BLACK)
        
        #image in the background
        bgRotate+=player["direction"]
        img=pygame.transform.rotate(  pygame.transform.scale(pygame.image.load('BGspace.png'),(1200,1200)),bgRotate)
        img_rect = img.get_rect(center=(screenProperties["W"]//2, screenProperties["H"]//2))
        rotated_rect = img.get_rect(center=img_rect.center)

        #draw screen elements (bars,score)
        pointMsg = fontObj.render(str(score), True, WHITE, None)
        WINDOW.blit(pointMsg,(screenProperties["W"]//2,40))

        pygame.draw.rect(WINDOW, (3, 255, 17), (20,30,20,400),)
        pygame.draw.rect(WINDOW, (155, 0, 17), (20,30,20,400*(1-HPbar/player["maxHP"])))# 
        pygame.draw.rect(WINDOW, WHITE, (20,30,20,400),2,3,3,3,)
        img= pygame.transform.scale(pygame.image.load("heartLogo.png"),(40,30)) 
        img_rect = img.get_rect(center=(31  ,screenProperties["H"]-150))
        WINDOW.blit(img,img.get_rect(center=img_rect.center))
 
        pygame.draw.rect(WINDOW, (0, 55, 255), (20+40,30,20,400),)
        pygame.draw.rect(WINDOW, (0,0,139), (20+40,30,20,400*(1-player["fuel"]/player["Maxfuel"])))# 
        pygame.draw.rect(WINDOW, WHITE, (20+40,30,20,400),2,3,3,3,)
        img= pygame.transform.scale(pygame.image.load("BarFuLogo.png"),(30,30)) 
        img_rect = img.get_rect(center=(69  ,screenProperties["H"]-150))
        WINDOW.blit(img,img.get_rect(center=img_rect.center))

        pygame.draw.rect(WINDOW, WHITE, (screenProperties["W"]-40,30,20,400),)
        pygame.draw.rect(WINDOW, BLACK, (screenProperties["W"]-40,30,20,400*(1-player["charge"]/player["maxDamage"])))# 
        pygame.draw.rect(WINDOW, WHITE, (screenProperties["W"]-40,30,20,400),2,3,3,3,)

        Ship()

        pygame.time.Clock().tick(60)

        #if player dies retuen the result
        if player["fuel"]<=0 or player["hp"]<=0:
            if player["fuel"]<=0 and player["hp"]<=0:
                result="OH NO !"
            elif player["fuel"]<=0:
                result="WELLDONE"
            elif player["hp"]<=0:
                result="YOU DESTROYED THE SHIP"
            return (result,score)


# the death screen returns the option the player picks 
def endGame(result,points):
    fontObj = pygame.font.Font(None, 55)
    endLoop=True
    while endLoop:
        ext()
        WINDOW.fill(BLACK)
        img= pygame.transform.scale(pygame.image.load('gameOver.png'),(screenProperties["W"], screenProperties["H"])) 
        img_rect = img.get_rect(center=(screenProperties["W"]//2-4, screenProperties["H"]//2+4))
        WINDOW.blit(img,img.get_rect(center=img_rect.center))

        if button("BACK TO MENU",screenProperties["W"]//2,screenProperties["H"]//2):
            return "another turn"
        if button("EXIT",screenProperties["W"]//2-4,screenProperties["H"]//2+214):
            return "done"

        endMsg = fontObj.render(result, True, WHITE, None)
        WINDOW.blit(endMsg,endMsg.get_rect(center=(screenProperties["W"]//2,screenProperties["H"]//2-200)))
        pointMsg = fontObj.render(str(points), True, WHITE, None)
        WINDOW.blit(pointMsg,pointMsg.get_rect(center=(screenProperties["W"]//2,screenProperties["H"]//2+100)))

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# the main game loop 
def main():
    mainLoop=True
    while mainLoop:
        ext()
        WINDOW.fill(BLACK)
        img= pygame.transform.scale(pygame.image.load('spaceShip.png'),(screenProperties["W"],screenProperties["H"])) 
        img_rect = img.get_rect(center=(screenProperties["W"]//2, screenProperties["H"]//2))
        WINDOW.blit(img,img.get_rect(center=img_rect.center))
        #play button logo
        pygame.draw.polygon(WINDOW,WHITE,((screenProperties["W"]//2 -13,    screenProperties["H"]//2-200     -15   ),
                                          (screenProperties["W"]//2+30 -13 , screenProperties["H"]//2-200+15 -15   ),
                                          (screenProperties["W"]//2 -13,    screenProperties["H"]//2-200+30  -15   )))
        #play button
        if button("   ",screenProperties["W"]//2,screenProperties["H"]//2-200):
            result,points=mainGame()
            done=endGame(result,points)
            if done=="done":
                mainLoop=False
        
        #link to the website 
        if button("?",screenProperties["W"]-50,screenProperties["H"]-50):
            mainLoop=False
            if True:
                webbrowser.open_new_tab("https://sites.google.com/education.nsw.gov.au/asteroid-belt-/how-to-play?authuser=1")
                time.sleep(4)

        if button("QUIT",screenProperties["W"]//2,screenProperties["H"]//2+208):
            mainLoop=False

        pygame.display.flip()
        pygame.time.Clock().tick(60)   

main()
