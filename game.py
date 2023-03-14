import pygame
import random 
import numpy as np
import math
import time


pygame.init()

SPEED=40
BLACK = (0,0,0)
WHITE = (255,255,255)
V0 = 85
font = pygame.font.Font('arial.ttf', 25)

class GunGameAI:

    def __init__(self, w=1000, h=640):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Archer Game')
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("bg1.png").convert()
        self.base = pygame.image.load("base.jpg").convert()
        player = pygame.image.load("playergun.png").convert_alpha()
        self.player = pygame.transform.scale(player, (75, 150))
        target = pygame.image.load("target.png").convert_alpha()
        self.target = pygame.transform.scale(target, (75, 150))
        self.reset()
        

    def reset(self):
        self.score = 0
        self.angle = 45
        self.frame_iteration = 0
        self.gravity = random.uniform(3.5, 10.5)
        self.xp = random.randint(30,250)
        self.xt = random.randint(610,850)
        self.y1 = random.randint(285,500)
        self.y2 = random.randint(285,500)
         
    
    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            

        result = self._action(action)

        reward = 0
        game_over = False
        if self.frame_iteration > 30:
            game_over = True
            reward = -10
            return reward, game_over, self.score
        if result == 3:
            game_over = True
            reward = -10
            return reward, game_over, self.score
        if result == 2:
            self.score += 1
            self.frame_iteration = 0
            self.next_level()
            reward = 10 

        self._update_ui()
        self.clock.tick(SPEED)
        

        return reward, game_over, self.score


    def _update_ui(self):
        self.display.blit(self.bg, [0, 0])
        self.display.blit(self.base, (30, self.y1))  
        self.display.blit(self.base, (600, self.y2))
        self.display.blit(self.player, (self.xp, self.y1 - 145))
        self.display.blit(self.target, (self.xt, self.y2 - 125))
        angle = font.render("Angle: " + str(self.angle), True, BLACK)
        self.display.blit(angle, [0, 0])
        gravity = font.render("Gravity: " + str('%.2f'%(self.gravity)), True, BLACK)
        self.display.blit(gravity, [800, 0])
        score = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(score, [400, 0])
        self.trajectory()
        pygame.display.flip()
        
    def _action(self, action):
        
        # [up, down, shoot]
        if np.array_equal(action,[1, 0, 0]):
            if(self.angle<75):
                self.angle+=3
        elif np.array_equal(action, [0, 1, 0]):
            if(self.angle>-15):
                self.angle-=3
        else:  #[0,0,1]
            i=0

            while(True):
                result = self.animation(i)
                i +=1
                if result == 2: 
                    #time.sleep(1)
                    return 2 
                if result == 3: 
                    #time.sleep(1)
                    return 3

    def next_level(self):
        self.xp = random.randint(30,250)
        self.xt = random.randint(650,800)
        self.y1 = random.randint(285,500)
        self.y2 = random.randint(285,500)
        self.gravity = random.uniform(3.5, 10.5)

    def animation(self, t):
        x = ((V0*(t/5))) *np.cos((self.angle)*(math.pi/180))
        y = ((V0*(t/5))*np.sin((self.angle)*(math.pi/180)))-((0.5*self.gravity)*((t/5)**2))
        pygame.draw.circle(self.display, BLACK,(x + self.xp + 80, self.y1 - 110 -y),5)
        pygame.display.flip()
        if x + self.xp + 80 < self.xt:
            return 1
        if x + self.xp + 80 >= self.xt + 15 and x + self.xp + 80 <= self.xt + 35:
            if self.y1 - 110 -y <= self.y2 - 25 and self.y1 - 110 -y >= self.y2 - 135:
                return 2
            else: 
                return 3
        
    def trajectory(self):
        for t in range(0,3):
            x = ((V0*(t/3))) *np.cos((self.angle)*(math.pi/180))
            y = ((V0*(t/3))*np.sin((self.angle)*(math.pi/180)))-((0.5*self.gravity)*((t/3)**2))
            pygame.draw.circle(self.display, BLACK,(x + self.xp + 80, self.y1 - 110 -y),5)
            pygame.draw.circle(self.display, WHITE,(x + self.xp + 80, self.y1 - 110 -y),4)
        pygame.display.flip()
        