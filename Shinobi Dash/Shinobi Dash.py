#TAIMUR SHAIKH
#SHINOBI DASH

'''
CONTROLS:
A and D = Move Left/Right
W = Jump
S = Slide
Left Shift = Block
'''
import pygame,sys,time,random,os
from pygame.locals import *
import pygame.image as image
from win32api import GetSystemMetrics

os.environ['SDL_VIDEO_CENTERED'] = '1' #Centers window on screen
pygame.init()
pygame.mixer.music.load(os.path.join("Shinobi Dash Files","Sounds", "Shinobi Dash Theme.ogg"))

DISPLAY_WIDTH = GetSystemMetrics(0)
DISPLAY_HEIGHT = GetSystemMetrics(1)

WINDOW_WIDTH = int(DISPLAY_WIDTH//1.5)
WINDOW_HEIGHT = int(DISPLAY_HEIGHT//3)
#print(WINDOW_WIDTH,WINDOW_HEIGHT)
BLACK = (0,0,0)
WHITE= (255,255,255)
RED = (255,0,0)
BLUE = (0,50,220)
PURPLE = (75,20,130)

SHOW_HITBOX = 0
MUSIC = 1

gameFont = pygame.font.Font(os.path.join("Shinobi Dash Files", "Font.ttf") , 25)


screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))

pygame.display.set_caption("Shinobi Dash")



idleList = [image.load(os.path.join('Shinobi Dash Files', 'Player Sprites','p' +str(x) + '.png')) for x in [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]*2]
runningList = [image.load(os.path.join('Shinobi Dash Files','Player Sprites', 'R' +str(x) + '.png')) for x in [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]*2]
enemyRunningList = [image.load(os.path.join('Shinobi Dash Files','Enemy Sprites', 'E' +str(x) + '.png')) for x in [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]*2]
idleSprite = idleList[0]
runningSprite = runningList[0] #Used only to calculate width of ninja on instantiation
slideSprite = pygame.transform.rotate(idleSprite,90)
kunaiRight = image.load((os.path.join('Shinobi Dash Files','kunai.png')))
kunaiLeft = pygame.transform.flip(kunaiRight,True,False)
ninjaAlert = pygame.transform.scale(image.load((os.path.join('Shinobi Dash Files','Ninja Alert.png'))),(128,128))
ninjaBlock = image.load(os.path.join('Shinobi Dash Files', 'Ninja Block.png'))
icon = image.load((os.path.join('Shinobi Dash Files','icon.png')))
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
fps = 32
speed = fps

class Sprite(pygame.sprite.Sprite):
    def __init__(self,imageFilePrefix = 0, x = 0,y =0):
        self.x = x
        self.y = y
        self.spriteList = [image.load(os.path.join('Shinobi Dash Files','Player Sprites', imageFilePrefix +str(x) + '.png')) for x in [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]*2]
        self.rect=self.spriteList[0].get_bounding_rect()
        self.rect.x=x
        self.rect.y=y
        self.displaySize=pygame.display.get_surface().get_size()

class Player(Sprite):
    def __init__(self,x,y,width,height,velocity):
        super().__init__('R')
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.jumping = False
        self.sliding = False
        self.blocking = False
        self.animationFrame = 0
        self.jumpCount = 10
        self.rect = self.spriteList[0].get_rect()

    def draw(self, screen):
        self.hitbox = pygame.Rect(self.x+self.rect.width//3,self.y+self.rect.height*(1/9), self.rect.width//2.4 ,self.rect.height *(7/8)) #Adjusting sprite rect to get more 'realistic' hitbox
        self.currentSprite = self.spriteList[self.animationFrame]

        if self.animationFrame >= fps -1:
            self.animationFrame = 0

        if self.sliding and not self.jumping:
            self.hitbox.w = slideSprite.get_height()
            self.hitbox.h = slideSprite.get_width()//3
            self.hitbox.x -= 50
            self.hitbox.y = (WINDOW_HEIGHT - self.hitbox.h) ##Making hitbox smaller and lower when sliding
            screen.blit(slideSprite,(self.x,self.y+35))

        elif self.blocking and not self.sliding:

            screen.blit(self.currentSprite, (self.x,self.y))
            screen.blit(ninjaBlock,(self.x+ninjaBlock.get_width(),self.y))
            self.animationFrame += 1
        else:
            screen.blit(self.currentSprite, (self.x,self.y))
            self.animationFrame += 1


    def slide(self,slideVelocity,prevX):
        self.x += slideVelocity

    def alert(self,surface):
        surface.blit(ninjaAlert,(self.hitbox.x + (self.hitbox.w//3.5),self.y-(ninjaAlert.get_width()//1.8)))


class Enemy(Player):

    def __init__(self,x,y,width,height,velocity):
        super().__init__(x,y,width,height,velocity)
        self.spriteList = [pygame.transform.flip(x,True,False) for x in enemyRunningList]

    def draw(self,screen):
        self.hitbox = pygame.Rect(self.x+self.rect.width//4.25,self.y+self.rect.height*(1/9), self.rect.width//2 ,self.rect.height *(7/8))
        self.currentSprite = self.spriteList[self.animationFrame]
        if self.animationFrame >= fps-1:
            self.animationFrame = 0

        screen.blit(self.currentSprite,(self.x,self.y))
        self.animationFrame +=1

    def collided(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False


class Projectile(Sprite):
    def __init__(self,x,y,velocity):
        self.x = x
        self.y = y
        self.rect = kunaiRight.get_bounding_rect()
        self.width = self.rect.w
        self.height = self.rect.h
        self.velocity = velocity

    def draw(self,surface,direction,startingX,startingY):
        self.hitbox = pygame.Rect(self.x,self.y+self.rect.h-8,self.rect.w,self.rect.h)

        if direction == 'RIGHT':
            #self.velocity = 70
            surface.blit(kunaiRight,(self.x,self.y))
        else:
            #self.velocity = 30
            surface.blit(kunaiLeft,(self.x,self.y))

    def collided(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False


class groundSpike():
    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = (x,y,width,height)

    def draw(self,surface):
        self.hitbox = (self.x +10,self.y,self.width -10, self.height)
        pygame.draw.rect(surface, PURPLE, self.hitbox)

    def collided(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False


class ceilingSpike(groundSpike):

    def collided(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] < self.hitbox[3]:
                return True
        return False
    def halt(self):
        self.kill()


def GameOver():
    global running
    print("GAME OVER")
    running = False

def mainMenu():
    while True:
        screen.fill(BLUE)

        startText = gameFont.render("START",True,RED)
        startTextRect = startText.get_rect(center = (WINDOW_WIDTH//2,WINDOW_HEIGHT//2))
        pygame.draw.rect(screen,WHITE,(startTextRect.x-5,startTextRect.y,startTextRect.w +10,startTextRect.h))
        screen.blit(startText,startTextRect)

        mouse= pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if mouse[0]:
                mouseX, mouseY = pygame.mouse.get_pos()
                if mouseX > startTextRect.x and mouseX < startTextRect.x + startTextRect.w and mouseY > startTextRect.y and mouseY < startTextRect.y + startTextRect.h:
                    return


        pygame.display.update()

def textToScreen(text,color,coords = 0):
    screenText = gameFont.render(text, True,color)
    textRect = screenText.get_rect(center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    screen.blit(screenText,coords)

def offScreen(obj):
    if obj.x > WINDOW_WIDTH or obj.x < 0 - obj.width:
        return True
    else:
        return False

def colourChange(pos):
    if pos <= 0: return BLACK
    shift = (pos * (255/(WINDOW_WIDTH - ninja.width)))//1
    return (shift ,0,0) if shift <= 255 else RED  #Makes the text appear more red as the pos increases

def scoreMultiplier(pos):
    if pos <= 0: return 1
    multiplier = (pos * (2/(WINDOW_WIDTH - ninja.width))) #generates a number between 1 and 2 depending on player x that is multiplied with score

    if multiplier < 1:
        multiplier = 1
    elif multiplier >2:
        multiplier = 2
    return multiplier

def playMusic():
    global MUSIC
    if MUSIC: pygame.mixer.music.play(-1)

#Main update function
def displayUpdate():
    screen.fill(BLUE)

    for projectile in playerProjectiles:
            projectile.draw(screen,'RIGHT',0,0)
            if SHOW_HITBOX:
                pygame.draw.rect(screen,RED,projectile.hitbox,2)

    for projectile in enemyProjectiles:

        startingX = projectile.x
        startingY = projectile.y

        ninja.alert(screen)

        projectile.draw(screen,'LEFT',startingX, startingY)

        if SHOW_HITBOX:
            pygame.draw.rect(screen,RED,projectile.hitbox,2)

    ninja.draw(screen)

    if SHOW_HITBOX:
        pygame.draw.rect(screen,RED,ninja.hitbox,2)

    for obstacle in obstacles:
        obstacle.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

        if SHOW_HITBOX:
                pygame.draw.rect(screen,RED,enemy.hitbox,2)


    textToScreen("SC0RE: " + str(int(score//1)), colourChange(ninja.x),(0,0)) #Ensures score is not increasing too fast

    pygame.display.update()



#MAIN PROGRAM
ninja = Player(20,WINDOW_HEIGHT-(runningSprite.get_height()-5), runningSprite.get_width(),runningSprite.get_height(),WINDOW_WIDTH//(WINDOW_WIDTH//15)) #Creates Player Object for Ninja sprite

playerProjectiles = []
enemyProjectiles = []
obstacles = []
enemies = []
scrollSpeed = 10 #Initial speed of game
speedIncrease = 0.005
running = True
sliding = False
pygame.time.set_timer(USEREVENT+2, random.randrange(2000,4000))  #For OBSTACLES
pygame.time.set_timer(USEREVENT+3, random.randrange(5000,8000)) #For ENEMIES
pygame.time.set_timer(USEREVENT+4,random.randrange(9000,12000)) #For ENEMY PROJECTILES
pygame.mouse.set_visible(True)


score = 0
mainMenu()
playMusic()
##GAME LOOP##
while running:

    for obstacle in obstacles:
        if obstacle.collided(ninja.hitbox):
            pygame.time.delay(500)
            GameOver()

        obstacle.x -= scrollSpeed

        if obstacle.x < obstacle.width*-1:
            obstacles.remove(obstacle)

    for enemy in enemies:

        if enemy.collided(ninja.hitbox) and enemy.x < WINDOW_WIDTH - enemy.width:
            pygame.time.delay(500)
            GameOver()

        enemy.x -= enemy.velocity

        for projectile in playerProjectiles:
            if enemy.collided(projectile.hitbox):
                enemies.remove(enemy)
                playerProjectiles.remove(projectile)

        if enemy.x < enemy.width *-1:
            enemies.remove(enemy)


        enemy.velocity += speedIncrease//2

    for projectile in playerProjectiles:
        if projectile.x < WINDOW_WIDTH and projectile.x >0:
            projectile.x += projectile.velocity
        else: #For bullets off the screen
            playerProjectiles.remove(projectile)

    for projectile in enemyProjectiles:

        if projectile.collided(ninja.hitbox):
            if ninja.blocking:
                enemyProjectiles.remove(projectile)
            else:
                GameOver()

        if projectile.x >0:
            projectile.x -= projectile.velocity

        else:
            enemyProjectiles.remove(projectile)



    ##EVENT LOOP##
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #If there are no enemies or projectiles:
        if event.type == USEREVENT+2 and False not in [offScreen(enemy) for enemy in enemies] and False not in [offScreen(projectile) for projectile in enemyProjectiles] and False not in [offScreen(obstacle) for obstacle in obstacles]:
            picker  = random.randrange(0,2)
            if not picker:
                obstacles.append(groundSpike(WINDOW_WIDTH+10,WINDOW_HEIGHT-ninja.height//3,random.choice([50,75]),WINDOW_HEIGHT-ninja.height//3))
            elif picker == 1:
                obstacles.append(ceilingSpike(WINDOW_WIDTH+10,-10,random.choice([50,75]),WINDOW_HEIGHT//1.25))

        #If there are no obstacles or projectiles:
        elif event.type == USEREVENT+3 and False not in [offScreen(obstacle) for obstacle in obstacles] and False not in [offScreen(projectile) for projectile in enemyProjectiles]:
            enemies.append(Enemy(WINDOW_WIDTH,WINDOW_HEIGHT-(runningSprite.get_height()-5), runningSprite.get_width(),runningSprite.get_height(),WINDOW_WIDTH//(WINDOW_WIDTH//10)))

        #If there is currently no obstacle and no enemy onscreen:
        elif event.type == USEREVENT+4 and False not in [offScreen(obstacle) for obstacle in obstacles] and False not in [offScreen(enemy) for enemy in enemies]:
            enemyProjectiles.append(Projectile(WINDOW_WIDTH, round(ninja.y + ninja.height//2 -5),WINDOW_WIDTH//50))

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_s:
                ninja.sliding = False

            if event.key == pygame.K_LSHIFT:
                ninja.blocking = False

    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()

    if mouse[0] or keys[pygame.K_SPACE] and not ninja.sliding and not ninja.blocking:
        if len(playerProjectiles) < 1:
                playerProjectiles.append(Projectile(round(ninja.x +ninja.width//2), round(ninja.y + ninja.height//2 -5), WINDOW_WIDTH//10))

    if keys[pygame.K_a] and ninja.x > 0 and not ninja.sliding:
        ninja.x -= ninja.velocity

    elif keys[pygame.K_d] and ninja.x < WINDOW_WIDTH-ninja.width and not ninja.sliding:
        ninja.x += ninja.velocity


    #Handling Sliding#
    if keys[pygame.K_s] and not ninja.jumping and ninja.x < WINDOW_WIDTH-ninja.width:

        ninja.sliding = True
        ninja.slide(ninja.velocity * 2,ninja.x)

    if keys[pygame.K_LSHIFT] and not ninja.sliding:
        if not ninja.blocking:
            ninja.blocking = True



    #Handling Jumping#
    if not(ninja.jumping):

        if keys[pygame.K_w]:
            ninja.jumping = True
            ninja.animationFrame = 0
    else:
        if ninja.jumpCount >= -10:
            neg = 1
            if ninja.jumpCount < 0:
                neg = -1
            ninja.y -= (ninja.jumpCount ** 2)*0.3 * neg
            ninja.jumpCount -= 1
        else:
            ninja.jumping = False
            ninja.jumpCount = 10




    clock.tick(fps)
    score += 0.1 * scoreMultiplier(ninja.x)
    scrollSpeed += speedIncrease

    displayUpdate()

pygame.quit()
