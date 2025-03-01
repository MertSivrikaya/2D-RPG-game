import pygame
from settings import *

class Tool:
    def __init__(self, name, image, animation_play_speed = 6 ):
        self.name = name
        self.image = image
        self.animation_play_speed = animation_play_speed
        
class MeleeWeapon(Tool): # subclass of 'Tool' class (it is also an instance of a Tool class)
    def __init__(self, name, image, attack_damage = 0, melee_attack_radius = 0, max_level = 3, attack_cooldown_duration = 1000, attack_speed = 6):
        super().__init__(name, image, attack_speed)
        
        self.attack_damage = attack_damage
        self.melee_attack_radius = melee_attack_radius * SCALE_RATIO # as pixels
        self.level = 1
        self.max_level = max_level
        self.attack_cooldown_duration = attack_cooldown_duration

class RangedWeapon(Tool):
    def __init__(self, name, image, attack_speed = 6):
        super().__init__(name, image, attack_speed)

class Sword(MeleeWeapon):
    attack_cooldown_duration = 500 # Class variable, which is shared among all the instances of Sword() class
    attack_speed = 8 # attack_animation_speed

    def __init__(self, attack_damage = 0, melee_attack_radius = 0, max_level = 3):
        sword_surf = pygame.image.load("./graphics/tools/sword.png").convert_alpha()
        super().__init__("sword", sword_surf, attack_damage, melee_attack_radius, max_level, self.attack_cooldown_duration, self.attack_speed)
        



        