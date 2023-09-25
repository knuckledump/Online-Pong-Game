import pygame as p
import random
import sys
import socket
import threading
from pygame.locals import *

WIDTH = 800
HEIGHT = 600
FPS = 60

BLACK = (0,0,0)
WHITE = (255,255,255)

PLAYER_SPEED = 15
BALL_SPEED = 5




class spritesheet:
    def __init__(self,file):
        self.sheet = p.image.load(file)
        
    def get_sprite(self,x,y,width,height):
        sprite = p.Surface([width,height])
        sprite.blit(self.sheet,(0,0),(x,y,width,height))
        sprite.set_colorkey(BLACK)
        return(sprite)



class left_player(p.sprite.Sprite):
    def __init__(self,g):
        #MAIN GAME CLASS ATTRIBUTES.......................................................
        self.game = g
        self._layer = 2
        self.groups = self.game.all_sprites , self.game.players
        p.sprite.Sprite.__init__(self,self.groups)

        #OBJECT DIMENSIONS ATTRIBUTES.......................................................
        self.width = 20
        self.height = 100

        #OBJECT IMAGE ATTRIBUES.............................................................
        self.img_spritesheet = spritesheet("images/player.png")
        self.image = self.img_spritesheet.get_sprite(0,0,self.width,self.height)

        #OBJECT RECTANGLE AND POSITION ATTRIBUTES............................................
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = HEIGHT//2 - self.height//2

        #OBJECT GAMEPLAY ATTRIBUTES.........................................................
        self.speed = 0

    def update(self):
        #MAIN UPDATE FUNCTION (runs each frame in the main game loop)........................
        self.keys()
        self.mouvement()

    def keys(self):
        #GETTING KEYBOARD INPUTS..............................................................
        keys = p.key.get_pressed()
        if keys[p.K_z] and self.rect.y > 0:
            self.speed = -PLAYER_SPEED
        if keys[p.K_s] and self.rect.y < HEIGHT - self.height:
            self.speed = PLAYER_SPEED

    def mouvement(self):
        #MOVING THE PLAYER EACH FRAME............................................................
        self.rect.y += self.speed
        self.speed = 0

class right_player(left_player):
    def __init__(self,g):
        left_player.__init__(self,g)
        self.image = self.img_spritesheet.get_sprite(0,20,self.width,self.height)
        self.rect.x = WIDTH - self.width - 10

    def keys(self):
        pass


class ball(p.sprite.Sprite):
    def __init__(self,g):
        self.game = g
        self._layer = 2
        self.groups = self.game.all_sprites
        p.sprite.Sprite.__init__(self,self.groups)

        self.width = 20
        self.height = 20

        self.img_spritesheet = spritesheet("images/ball.png")
        self.image = self.img_spritesheet.get_sprite(0,0,self.width,self.height)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH//2 - self.width//2
        self.rect.y = HEIGHT //2 - self.height//2

        self.x_speed = 0
        self.y_speed = 0
        self.speed_add = 0.5

        self.is_launched = False

    def update(self):
        #MAIN UPDATE FUNCTION....................................................................
        self.keys()
        self.mouvement()
        self.collide()

        #SCORE CHANGEMENTS.......................................................................
        if self.rect.x <= -20:
            self.game.score["right_player"] +=1
            self.reset()
        elif self.rect.x >= WIDTH + 20:
            self.game.score["left_player"] +=1
            self.reset()


    def keys(self):
        keys = p.key.get_pressed()
        if keys[p.K_SPACE] and not self.is_launched:
            self.launch()

    def launch(self):
        self.is_launched = True
        self.game.playing = True

        #GIVING THE BALL A RANDOM LAUNCH DIRECTION.......................................................
        self.x_speed = random.choice([-1,1]) * BALL_SPEED
        self.y_speed = random.choice([-1,1]) * BALL_SPEED

    def collide(self):
        #DETECTING PLAYER COLLISION/ args = (Object, other_group, Do_Kill)................
        player_hits = p.sprite.spritecollide(self,self.game.players,False)
        if player_hits:
            self.x_speed = -self.x_speed     #INVERTING X_SPEED
            self.game.change_background()    #CHANGING BACKGROUND COLOR EACH PLAYER HIT

            #ADDING BALL SPEED EACH PLAYER HIT.............................................
            if self.x_speed <0:
                self.x_speed -=self.speed_add
            else:
                self.x_speed +=self.speed_add

            if self.y_speed <0:
                self.y_speed -=self.speed_add
            else:
                self.y_speed +=self.speed_add
        
        #DETECTING BORDER COLLISION..................................................................
        if self.rect.y <= 0 or self.rect.y >= HEIGHT - self.height:
            self.y_speed = -self.y_speed    #INVERTING Y_SPEED EACH BORDER HIT
            particle(self.game, self.rect.x - self.width//2, self.rect.y - self.height//2) #ADDING PARTICLES EACH BORDER HIT
    
    def mouvement(self):
        #MOVING THE BALL EACH FRAME...............................................................................
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

    def reset(self):
        #RESETTING BALL POSITION AND SPEED..........................................................................
        self.rect.x = WIDTH//2 - self.width//2
        self.rect.y = HEIGHT //2 - self.height//2
        self.x_speed = 0
        self.y_speed = 0
        self.is_launched = False
        self.game.playing = False




class particle:
    def __init__(self,g,x,y):
        
        self.game = g
        self.game.effects.append(self)
        
        self.width = 200
        self.height = 200
        self.image = p.Surface((self.width,self.height))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x - self.width//2
        self.rect.y = y - self.height//2

        self.particle_list = []
        self.color = (255,255,255)
        
        self.light_color = (80,20,10)
        self.life_time = 15
    
    def update(self):
        self.life_time -= 1
        if self.life_time <= 0:
            self.kill()
        
        particle = [[self.rect.x + self.width//2 ,self.rect.y + self.height//2] , [random.randint(-50,50)/3,random.randint(-50,50)/3] , random.randint(5,10)]
        self.particle_list.append(particle)
        for par in self.particle_list:
            par[0][0] += par[1][0]
            par[0][1] += par[1][1]
            par[2] -= 0.4
            if par[2] <=0:
                self.particle_list.remove(par)
        
            p.draw.circle(self.game.screen, self.color, [int(par[0][0]), int(par[0][1])], int(par[2]))
            radius = particle[2] * 1.5
            self.game.screen.blit(self.circle_surf(radius, self.light_color), (int(par[0][0] - radius), int(par[0][1] - radius)), special_flags=BLEND_RGB_ADD)
        
    def circle_surf(self,radius, color):
        
        surf = p.Surface((radius * 2, radius * 2))
        p.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def kill(self):
        self.game.effects.remove(self)


class game:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((WIDTH,HEIGHT))
        p.display.set_caption("Pong Game")
        self.clock = p.time.Clock()
        self.running = True
        self.playing = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((IP, PORT))
        self.socket.listen()
        self.client , adress = self.socket.accept()
        
    
    def new(self):

        #GAMEPLAY SPRITES HOLDERS..........................................................
        self.all_sprites = p.sprite.LayeredUpdates()
        self.players = p.sprite.LayeredUpdates()
        self.effects = []

        #GAMEPLAY ASSETS....................................................................
        self.ball = ball(self)
        self.left_player = left_player(self)        
        self.right_player = right_player(self)

        #POLISH ASSETS......................................................................
        self.score = {"left_player":0, "right_player":0}
        self.font = p.font.Font('Retro Gaming.ttf', 32)
        self.background_color = [50,50,50]
        
    
    def events(self):
        for event in p.event.get():
        #CLOSING THE GAME...................................................................
            if event.type == p.QUIT:
                self.running = False
                p.quit()
                sys.exit()

        
    def update(self):
        
             

        #UPDATING ALL SPRITES EACH FRAME.....................................................
        self.all_sprites.update()
    
        self.recv_data()
        self.send_data()

    def draw_score(self):
        #RENDERING TEXT /args = (Text, Antialias(generally True), Color)......................
        l_player_score_text = self.font.render(str(self.score["left_player"]), True, WHITE)
        r_player_score_text = self.font.render(str(self.score["right_player"]), True, WHITE)

        #BLITTING THE RENDERED TEXT ON THE SCREEN /args = (rendered_text, coords)
        self.screen.blit(l_player_score_text,(WIDTH//2 - 50 , 20))
        self.screen.blit(r_player_score_text,(WIDTH//2 + 50 - 16, 20))

    def change_background(self):
        #CHANGING RGB VALUES OF THE BACKGROUND................................................
        self.background_color[0] += random.randint(-30,30)
        if self.background_color[0]> 255:
            self.background_color[0] = 255
        elif self.background_color[0]< 0:
            self.background_color[0] = 0

        self.background_color[1] += random.randint(-30,30)
        if self.background_color[1]> 255:
            self.background_color[1] = 255
        elif self.background_color[1]< 0:
            self.background_color[1] = 0

        self.background_color[2] += random.randint(-30,30)
        if self.background_color[2]> 255:
            self.background_color[2] = 255
        elif self.background_color[2]< 0:
            self.background_color[2] = 0


    def draw_starter_text(self):
        l_player_input_text = self.font.render("Z/S TO MOVE", True, WHITE)
        r_player_input_text = self.font.render("P/M TO MOVE", True, WHITE)
        ball_input_text = self.font.render("SPACE TO START", True, WHITE)

        self.screen.blit(l_player_input_text, (175//2,HEIGHT*3//4))
        self.screen.blit(r_player_input_text, (WIDTH - 325 ,HEIGHT*3//4))
        self.screen.blit(ball_input_text, (WIDTH//2 - 160 ,HEIGHT//4))

    def draw(self):
        #DRAWING ALL GAME ASSETS...............................................................
        self.screen.fill(self.background_color)
        self.all_sprites.draw(self.screen)

        for effect in self.effects:
            effect.update()
        
        self.draw_score()

        if not self.playing:
            self.draw_starter_text()

        self.clock.tick(FPS) 
        p.display.update()

    def recv_data(self):
        data = self.client.recv(1024).decode('utf-8')
        g.right_player.rect.y = int(data)

    def send_data(self):
        data = str(self.left_player.rect.y)+'/'+str(self.ball.rect.x)+'/'+str(self.ball.rect.y)
        self.client.send(data.encode("utf-8"))

        
    def main(self):
        #MAIN GAME LOOP.........................................................................
        while self.running:
            self.events()
            self.update()
            self.draw()

IP = '0.0.0.0'
PORT = 33001 


g = game()
g.new()
g.main()


