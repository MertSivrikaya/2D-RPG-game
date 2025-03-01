import pygame
from support import *
from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, entity_name, pos, sprite_groups : list, animation_frames, starting_direction, hitbox_inflate_values, walking_speed, walking_speed_while_attacking, default_animation_play_speed = 6, max_health = 100, image_scale_ratio = SCALE_RATIO) -> None:
        super().__init__(*sprite_groups)

        # Animation
        self.animation_frames = animation_frames
        self.import_graphics(entity_name, image_scale_ratio)
        self.animation_frame_index = 0

        self.default_animation_play_speed = default_animation_play_speed
        self.animation_play_speed = self.default_animation_play_speed

        # Entity State
        self.action = "idle"
        self.direction = starting_direction
        self.state = self.action + "_" + self.direction

        # Sprite Class Setup
        self.image = self.animation_frames[self.state][self.animation_frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.name = entity_name

        # Hitbox
        self.hitbox = self.rect.copy().inflate(-hitbox_inflate_values[0] * SCALE_RATIO,-hitbox_inflate_values[1] * SCALE_RATIO)

        # Health
        self.max_health = max_health
        self.health = self.max_health

        # Movement
        self.pos = pygame.math.Vector2(self.rect.center) # we must use a vector because rects in pygame cannot store float values
        self.direction_vector = pygame.math.Vector2() # (0,0)
    
        self.walking_speed = walking_speed
        self.walking_speed_while_attacking = walking_speed_while_attacking # slow down the entity movement speed during attacking

        self.velocity = self.walking_speed

        # Hit Animation Setup
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surface = self.mask.to_surface()
        self.mask_surface.set_colorkey((0,0,0)) # make the black pixels on the surface transparent(alpha = 0)

        self.flash_duration = 100

    def import_graphics(self, entity_name : str, image_scale_ratio):
        for animation_state in self.animation_frames.keys():
            path = "./graphics/" + entity_name + "/" + animation_state
            self.animation_frames[animation_state] = import_folder(path, image_scale_ratio)

    def move(self, dt):
        if self.direction_vector.magnitude() > 0:
            self.direction_vector.normalize_ip() # To normalize a vector, therefore, is to take a vector of any length and, keeping it pointing in the same direction, change its length(magnitude) to 1, turning it into what is called a unit vector.
            # This prevent the player from having a faster diagonal velocity

        # self.pos += self.direction_vector * self.velocity * dt

        # horizontal movement (seperating these to work with collisions later)
        self.pos.x  += self.direction_vector.x * self.velocity * dt
        self.rect.centerx = round(self.pos.x) # rect pos cannot take float values in pygame, it omits the decimals, so we are rounding the value to the nearest integer instead.
        self.hitbox.centerx = self.rect.centerx

        # vertical movement
        self.pos.y += self.direction_vector.y * self.velocity * dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.die()

    def die(self):
        print(self.name + " has died.")
    
    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surface = self.mask.to_surface()
        self.mask_surface.set_colorkey((0,0,0))
    
    def update_state(self):
        if self.direction_vector.magnitude() == 0:
            self.action = "idle"
        else:
            self.action = "walk"
            
        self.state = self.action + "_" + self.direction

    def animate(self, dt, state_to_look_for_animation, did_get_hit):
        self.animation_frame_index += self.animation_play_speed * dt
        if self.animation_frame_index >= len(self.animation_frames[state_to_look_for_animation]):
            self.animation_frame_index = 0
        
        self.image = self.animation_frames[state_to_look_for_animation][int(self.animation_frame_index)]

        if did_get_hit:
            if self.name == "player":
                self.play_hit_animation(dt) # overwritten method of the player needs a 'dt' argument
            else:
                self.play_hit_animation() # whereas the same method of this class shouldn't take 'dt as an argument

    def play_hit_animation(self):
        self.update_mask()
        self.image = self.mask_surface.copy()
        
    def update(self, dt): # will be deleted
        self.move(dt)
        self.update_state()
        self.animate(dt, self.state, False)

    @staticmethod
    def get_animation_duration(action_name, animation_speed, animation_frames): # gives the animation duration of the given action in milliseconds
        """
            animation_frame_count / (self.animation_play_speed * dt * 1000) = total_game_frames (dt: duration of a frame as seconds)
            total_game_frames * dt = animation_duration

            animation_duration = animation_frame_count * 1000 / self.animation_play_speed
            
        """
        state_name = action_name + "_" + "left"

        animation_frame_count = len(animation_frames[state_name])
        animation_duration = (animation_frame_count * 1000) / animation_speed
            
        return animation_duration 
