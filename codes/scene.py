import pygame
from pygame.sprite import AbstractGroup, Sprite
from settings import *
from player import Player
from timers import Timer
from random import randint, uniform
from enemy import *
from entity import *

class Scene:
    def __init__(self):
        
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # Create a sprite group for oll objects that must appear on the screen in the current scene
        self.camera_sprites = CameraGroup() # all visible sprites that move along with the screen/player, all sprites that are affected by the camera
        self.enemy_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
         # Creating the player
        BackGround(self.camera_sprites)
        self.player = Player((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), [self.camera_sprites], self) # Create a player in each scene
        RedHood((1000, 400), [self.camera_sprites, self.enemy_sprites], self.player)

    def load(self, dt):
        
        self.camera_sprites.draw(self.player)
        self.camera_sprites.update(dt)

    def get_camera_group(self):
        return self.camera_sprites
       
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.player_offset_from_center = pygame.Vector2()

        self.screen_shake_timer = Timer(200)
        self.screen_shake_magnitude = 1

    def draw(self, player : Sprite): # overwriting
        self.screen_shake_timer.update()

        self.player_offset_from_center.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.player_offset_from_center.y = player.rect.centery - SCREEN_HEIGHT / 2

        self.display_surface.fill("Black") # Otherwise, pygame automatically completes the rest of the screen 'blue', same color as the outermost sea
        
        if self.screen_shake_timer.active: # we need to do this outside the for loop in order to move every offset rect the same amount
            screen_shake_offset = self.get_screen_shake_offset()
        else:
            screen_shake_offset = pygame.Vector2()
        
        for sprite in self.sprites():
            offset_rect = sprite.rect.copy() # Actual positions of the game objects don't change, we just change the visual positions.
            offset_rect.center -= self.player_offset_from_center

            offset_rect.center += screen_shake_offset

            self.display_surface.blit(sprite.image, offset_rect)

            # Developer Mode
            total_offset = screen_shake_offset - self.player_offset_from_center

            if isinstance(sprite, Player):
                sprite.draw_gizmos(self.display_surface, total_offset)

            if isinstance(sprite, Enemy):
                sprite.draw_gizmos(self.display_surface, total_offset)

    def start_screen_shake(self, duration = 200, magnitude = 1):
        self.screen_shake_timer = Timer(duration)
        self.screen_shake_timer.activate()
        self.screen_shake_magnitude = magnitude
    
    def get_screen_shake_offset(self):
        screen_shake_offset_x = randint(-4, 4) 
        screen_shake_offset_y = randint(-4, 4)

        screen_shake_offset = pygame.math.Vector2(screen_shake_offset_x, screen_shake_offset_y)
        if screen_shake_offset.magnitude() > 0:
            screen_shake_offset.normalize_ip()
        
        screen_shake_offset *= uniform(self.screen_shake_magnitude - 0.5, self.screen_shake_magnitude + 1)

        return screen_shake_offset

# Developer Mode
class BackGround(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.name = "bg"
        self.image = pygame.image.load("./graphics/temporary_bg.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width() * SCALE_RATIO), round(self.image.get_height() * SCALE_RATIO)))
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    