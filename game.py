import os
import sys
import math
import pygame as pg
import client
import threading

#Game Vars
caption = ''
screen_size = (700, 650)
level_size = (700, 1200)

name = 'Player'

direct_dict = {pg.K_UP : (0, -1),
               pg.K_DOWN : (0, 1),
               pg.K_RIGHT : (1, 0),
               pg.K_LEFT : (-1, 0),
               pg.K_w : (0, -1),
               pg.K_s : (0, 1),
               pg.K_d : (1, 0),
               pg.K_a : (-1, 0)}

level_dict = {1 : {'normal': {'background': 'levels/one.background.png', 'mask': 'levels/one.mask.png'},
                   'reverse': {'background': 'levels/one.reverse.background.png', 'mask': 'levels/one.revers.mask.png'}} }
weapons_dict = {'rifle': 'weapons/rifle.png',
                'cross': 'weapons/cross.png',
                'bullets': {'plain': 'weapons/bullet.png'}}

global_objects = []

#When ready, open and read users file here.

#
# PLAYER CLASS
#

class Player(pg.sprite.Sprite):
    def __init__(self, image, punch_image, location, speed, name, font):
        self.image = pg.image.load(image).convert_alpha()
        self.image_copy = self.image
        self.punch_image = pg.image.load(punch_image)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=location)
        self.name = name
        self.font = font

        self.speed = speed
        self.lives = 20
        self.dead = False
        self.punching = False
        self.rifle = rifle(self.rect.center)

    def update(self, level_mask, keys):
        #moving
        move = self.check_keys(keys)
        self.check_collisions(move, level_mask)

        if self.lives <= 0:
            self.dead = True
    def check_keys(self, keys):
        move = [0, 0]
        for key in direct_dict:
            if keys[key]:
                for i in (0, 1):
                    move[i] += direct_dict[key][i]*self.speed
        
        return move

    def check_collisions(self, move, level_mask):
        x_change = self.collision_detail(move, level_mask, 0)
        self.rect.move_ip((x_change,0))

        
        y_change = self.collision_detail(move, level_mask, 1)
        self.rect.move_ip((0,y_change))

        #Check Borders

        if self.rect.x <= 0:
            self.rect.move_ip((-(self.rect.x), 0))
        
        if self.rect.x >= level_size[0] - 60:
            self.rect.move_ip(-(self.rect.x - level_size[0] + 60), 0)

        if self.rect.y + 15 <= 0:
            self.rect.move_ip(0, -(self.rect.y+ 15))
        
        if self.rect.y >= level_size[1] - 52:
            self.rect.move_ip(0, -(self.rect.y - level_size[1] + 52))



        if 360 - 135 < self.rifle.angle < 360 - 45:
            self.image_copy = pg.transform.rotate(self.image, -90)

        if 45 < self.rifle.angle < 135:
            self.image_copy = pg.transform.rotate(self.image, 90)

        if 135 < self.rifle.angle < 360 - 135:
            self.image_copy = pg.transform.rotate(self.image, 180)
            
        if 45 > self.rifle.angle > 0 or 360 > self.rifle.angle > 360 - 45:
            self.image_copy = pg.transform.rotate(self.image, 0)

    def collision_detail(self, move, level_mask, index):
        test_offset = list(self.rect.topleft)
        test_offset[index] += move[index]
        while level_mask.overlap_area(self.mask, test_offset):
            move[index] += (1 if move[index]<0 else -1)
            test_offset = list(self.rect.topleft)
            test_offset[index] += move[index]
        return move[index]

    def draw(self, surface, viewport):
        self.rifle.update(self.rifle, self.rect, viewport)
        self.rifle.draw(self.rifle, surface, viewport)
        surface.blit(self.image_copy, self.rect)

        text_pos = [self.rect.x, self.rect.y - 25]
        
        label = self.font.render(self.name, 1, (0, 0, 0))
        surface.blit(label, text_pos)        

#
# Weapons Classes
#

class rifle(pg.sprite.Sprite):
    def __init__(self, location):
        self.location = location
        self.image = pg.image.load(weapons_dict['rifle'])
        x_offset, y_offset = (-30, -35)
        self.rect = self.image.get_rect(center=location)
        self.angle = 0
        self.image_copy = self.image.copy()
        self.cross = pg.image.load(weapons_dict['cross'])
        self.cross_loc = pg.mouse.get_pos()

    def update(self, null, player_rect, viewport):
        x_offset, y_offset = (-20, 5)

        mouse_pos = pg.mouse.get_pos()
        apparent_mouse_pos = (mouse_pos[0] + viewport.x, mouse_pos[1] + viewport.y)
        self.angle = self.get_angle(apparent_mouse_pos)
        self.image_copy = pg.transform.rotate(self.image, float(self.angle))
        self.location = (player_rect.centerx + x_offset, player_rect.centery + y_offset)
        self.rect = self.image_copy.get_rect(center=self.location)


    def get_angle(self, mouse):
        centerx, centery = self.rect.center

        offset = (mouse[1]-centery, mouse[0]-centerx)
        angle = 270-math.degrees(math.atan2(*offset))
        self.cross_loc = (mouse[0] - 15, mouse[1] - 15)
        
        return angle

    def get_event(self, event, objects):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            objects.add(Bullet(self.rect.center, self.angle))
            client.add_obj(self.rect.center, round(self.angle, 5))
            
    def draw(self, null, surface, viewport):
        surface.blit(self.image_copy, self.rect)
        surface.blit(self.cross, self.cross_loc)

class Bullet(pg.sprite.Sprite):
    """
    A class for our laser projectiles. Using the pygame.sprite.Sprite class
    this time, though it is just as easily done without it.
    """
    def __init__(self, location, angle):
        """
        Takes a coordinate pair, and an angle in degrees. These are passed
        in by the Turret class when the projectile is created.
        """
        pg.sprite.Sprite.__init__(self)
        self.original_image = pg.image.load(weapons_dict['bullets']['plain'])
        self.angle = -math.radians(angle-270)
        self.image = pg.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=location)
        self.mask = pg.mask.from_surface(self.image)
        self.move = [self.rect.x, self.rect.y]
        self.speed_magnitude = 22
        self.speed = (self.speed_magnitude*math.cos(self.angle),
                      self.speed_magnitude*math.sin(self.angle))
        self.done = False

    def update(self, screen_rect, viewport, level_mask):
        """
        Because pygame.Rect's can only hold ints, it is necessary to hold
        the real value of our movement vector in another variable.
        """
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.center = (self.move[0] - viewport.x, self.move[1] - viewport.y)
        self.remove(screen_rect, level_mask, [viewport.x, viewport.y])

    def collision(self, move, level_mask, index, viewport):
        viewport_x, viewport_y = viewport
        test_offset = [list(self.rect.center)[0] + viewport_x, list(self.rect.center)[1] + viewport_y]
        test_offset[index] += move[index]
        if level_mask.overlap_area(self.mask, test_offset):
            return 0
        else:
            return move[index]

    def remove(self, screen_rect, level_mask, viewport):
        if not self.rect.colliderect(screen_rect):
            self.kill()

        x_change = self.collision( [int( math.ceil( self.speed[0] ) ), int( math.ceil( self.speed[1] ) )], level_mask, 0, viewport)
        y_change = self.collision( [int( math.ceil( self.speed[0] ) ), int( math.ceil( self.speed[1] ) )], level_mask, 1, viewport)

        if x_change == 0 and y_change == 0:
            self.kill()

#
# LEVEL CLASS
#

class Level(object):    
    def __init__(self, background, map_image, viewport, player, font):
        self.image = pg.image.load(map_image).convert_alpha()
        self.background = pg.image.load(background).convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.player = player
        self.player.rect.center = self.rect.center
        self.viewport = viewport
        self.interface = Interface(self.player)

    def update(self, keys):
        self.player.update(self.mask, keys)
        self.update_viewport()

    def update_viewport(self):
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.rect)

    def draw(self, surface):
        new_image = self.image.copy()
        new_background = self.background.copy()
        self.player.draw(new_image, self.viewport)
        surface.blit(new_background, (0, 0), self.viewport)
        surface.blit(new_image, (0,0), self.viewport)
        self.interface.draw(surface)

class Interface(object):
    def __init__(self, player):
        self.player = player
        
        self.start_width = 200
        self.x, self.y = (250, 30)
        self.width, self.height = (self.start_width, 20)
        self.padding = 2
        
        self.lives_rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.lives_rect_back = pg.Rect(self.x - self.padding, self.y - self.padding, self.width + (self.padding * 2), self.height + (self.padding * 2))
        

    def draw(self, surface):
        self.width = self.player.lives * 10

        self.lives_rect = pg.Rect(self.x, self.y, self.width, self.height)
        
        pg.draw.rect(surface, (150, 150, 150), self.lives_rect_back)
        pg.draw.rect(surface, (255, 0, 0), self.lives_rect)
        

class Control(object):
    def __init__(self, level_num):
        self.screen = pg.display.set_mode(screen_size)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.objects = pg.sprite.Group()
        self.objects_foreign = pg.sprite.Group()

        self.font = pg.font.SysFont('monospace', 18)
        
        self.player = Player('player/blue.png', 'player/blue.punching.png', (0, 0), 6, name, self.font)

        background = level_dict[level_num]['normal']['background']
        mask = level_dict[level_num]['normal']['mask']
        
        self.level = Level(background, mask, self.screen_rect.copy(), self.player, self.font)

    def event_loop(self):
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            self.player.rifle.get_event(event, self.objects)

    def update(self):
        self.screen.fill(pg.Color("black"))
        self.level.update(self.keys)
        self.level.draw(self.screen)
        self.objects.update(self.screen_rect, self.level.viewport, self.level.mask)
        self.objects.draw(self.screen)
        self.objects_foreign.update(self.screen_rect, self.level.viewport, self.level.mask)
        self.objects_foreign.draw(self.screen)

        #Get new bullets here!!!
        if client.bullets != []:
            for i in client.bullets:
                print(i)
                self.objects_foreign.add(Bullet(i[0], i[1]))
            client.clear_bullets()

        for bullet in self.objects_foreign.sprites():
            if bullet.rect.colliderect(self.player.rect):
                self.player.lives -= 1
                bullet.done = True

    def dead(self):
        print('dead')

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            if self.player.dead:
                self.done = True
        self.dead()

def process():
    while True:
        client.loop()
