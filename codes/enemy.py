import pygame
from pygame.sprite import AbstractGroup
from settings import *
from entity import *
from math import sqrt
from timers import Timer
from circle import Circle
from player import Player

class Enemy(Entity):
    def __init__(self, entity_name : str, pos :tuple, sprite_groups : list, animation_frames : dict, starting_direction : str, hitbox_inflate_values : tuple, walking_speed : int, walking_speed_while_attacking : int, max_health : int, detect_player_radius : float, player : Player, attack_radius : float, attack_speed : int, attack_cooldown_duration : int, damage : int, max_distance_to_player_to_start_attack_animation : float, default_animation_play_speed : float, image_scale_ratio = SCALE_RATIO):
        super().__init__(entity_name, pos, sprite_groups, animation_frames, starting_direction, hitbox_inflate_values, walking_speed, walking_speed_while_attacking, default_animation_play_speed, max_health, image_scale_ratio)
        
        # Player Detection
        self.player = player
        self.detect_player_radius = detect_player_radius * SCALE_RATIO

        self.is_alert = False # if the enemy has detected the player

        # Attack
        self.attack_radius = attack_radius * SCALE_RATIO
        self.max_distance_to_player_to_start_attack_animation = max_distance_to_player_to_start_attack_animation * SCALE_RATIO

        self.deal_damage_circle = Circle(self.pos, self.attack_radius) # if the player hitbox is inside of that circle during attack_phase, the player will take damage
        self.get_close_to_player_to_start_attack_animation_circle = Circle(self.pos, self.max_distance_to_player_to_start_attack_animation) # the enemy will move until this circle collides with the player hitbox and then, the enemy will start the attack (the player hitbox must be colliding with this circle for enemy to start the atttack)

        self.attack_speed = attack_speed
        self.attack_cooldown_duration = attack_cooldown_duration

        self.damage = damage

        self.default_animation_play_speed = default_animation_play_speed
        self.animation_play_speed = self.default_animation_play_speed

        # Private Variables
        self.__player_pos_before_getting_knocbkack = pygame.math.Vector2()

        # Timers
        self.timers = {
            "attack_animation" : Timer(Entity.get_animation_duration("attack", self.attack_speed, self.animation_frames), self.end_attack_animation),
            "attack_cooldown" : Timer(self.attack_cooldown_duration),
            "deal_damage_after" : Timer(Entity.get_animation_duration("attack", self.attack_speed, self.animation_frames) / 2, self.start_can_damage_player_phase),
            "can_damage_player" : Timer(Entity.get_animation_duration("attack", self.attack_speed, self.animation_frames) / 4),
            "flash" : Timer(self.flash_duration),
            "knockback" : Timer(200, self.__start_motionless_after_knockback_phase, lambda: self.__take_knock_back(120)), # we must send a function to this argument, not the value returned from it
            "motionless_after_knockback" : Timer(150, self.__end_motionless_after_knockback_phase, self.__stay_motionless_after_knockback)
        }

    def detect_player(self):
        distance_to_player = self.get_distance_to_player()
        
        if distance_to_player <= self.detect_player_radius:
            self.is_alert = True
        else:
            self.is_alert = False
            self.direction_vector = pygame.math.Vector2()

    def get_distance_to_player(self):
        player_pos = pygame.math.Vector2(self.player.rect.center)
        
        distance_to_player = self.pos.distance_to(player_pos)
        return distance_to_player

    def get_distance_vector_to_player(self):
        player_pos = pygame.math.Vector2(self.player.rect.center)

        distance_vector = player_pos - self.pos
        return distance_vector

    def update_direction(self):
        if not self.timers["knockback"].active and not self.timers["motionless_after_knockback"].active:
            
            if not self.is_alert: # on not alert
                self.direction_vector = pygame.math.Vector2()
            
            else: # on alert (move_towards_player)
                if not self.get_close_to_player_to_start_attack_animation_circle.is_colliding_rect(self.player.hitbox) and not self.timers["attack_animation"].active: 
                    self.direction_vector = self.get_distance_vector_to_player()
                        
                    if self.direction_vector.magnitude() > 0:
                        self.direction_vector.normalize_ip()
                    self.direction_vector *= self.velocity

                    # Change the direction/facing way of the enemy 
                    if self.direction_vector.x > 0:
                        self.direction = "right"
                    else:
                        self.direction = "left"
                else:
                    self.direction_vector = pygame.math.Vector2()
    
    def move(self, dt):
        self.pos += self.direction_vector * dt

        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        self.hitbox.center = self.rect.center

        if self.get_close_to_player_to_start_attack_animation_circle.is_colliding_rect(self.player.hitbox):
            if self.hitbox.colliderect(self.player.hitbox): # if colliding with the player
                self.deal_damage_to_player()

            if not self.timers["attack_animation"].active and not self.timers["attack_cooldown"].active and not self.timers["knockback"].active and not self.timers["motionless_after_knockback"].active:
                self.start_attack_animation()

    def start_attack_animation(self):
        self.action = "attack"
        self.animation_frame_index = 0
        self.animation_play_speed = self.attack_speed

        self.timers["attack_animation"].activate()
        self.timers["deal_damage_after"].activate()

    def start_can_damage_player_phase(self):
        self.timers["can_damage_player"].activate()
    
    def end_attack_animation(self):
        self.action = "idle"
        self.animation_frame_index = 0
        self.animation_play_speed = self.default_animation_play_speed

        self.timers["attack_animation"].deactivate() 

        self.timers["attack_cooldown"].activate()

    def update_state(self):
        if not self.timers["attack_animation"].active:
            if self.direction_vector.magnitude() == 0 or self.timers["knockback"].active: # player's direction vector is already zero on motionless_after_knockback so we don't need to add an extra statemnt to check that
                self.action = "idle"
            else:
                self.action = "walk"

        self.state = self.action + "_" + self.direction

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def deal_damage_to_player(self):
        self.player.take_damage(self.damage)

    def take_damage(self, damage):
        super().take_damage(damage)
        self.timers["flash"].activate()
        
        if self.timers["attack_animation"].active:
            self.end_attack_animation()

        self.__player_pos_before_getting_knocbkack = self.player.pos
        self.timers["knockback"].activate()

    def __take_knock_back(self, magnitude):
        knock_back_vector = self.pos - self.__player_pos_before_getting_knocbkack

        if knock_back_vector.magnitude() > 0:
            knock_back_vector.normalize_ip()
        knock_back_vector *= magnitude

        self.direction_vector = knock_back_vector
        self.animation_play_speed = 0

    def __start_motionless_after_knockback_phase(self):
        self.timers["motionless_after_knockback"].activate()

    def __stay_motionless_after_knockback(self):
        self.direction_vector = pygame.math.Vector2()

    def __end_motionless_after_knockback_phase(self):
        self.animation_play_speed = self.default_animation_play_speed

    def draw_gizmos(self, display_surface : pygame.Surface, display_offset : pygame.math.Vector2):
        offsetted_hitbox = self.hitbox.copy()
        offsetted_hitbox.center += display_offset
        
        if self.is_alert:
            offsetted_player_hitbox = self.player.hitbox.copy()
            offsetted_player_hitbox.center += display_offset

            pygame.draw.line(display_surface, "Black", offsetted_hitbox.center, offsetted_player_hitbox.center)
            
        pygame.draw.circle(display_surface, "Red", offsetted_hitbox.center, self.attack_radius, 1)
        pygame.draw.circle(display_surface, "Blue", offsetted_hitbox.center, self.max_distance_to_player_to_start_attack_animation, 1)

        pygame.draw.rect(display_surface, "Green", offsetted_hitbox, 1)

    def update(self, dt):
        self.detect_player()
        self.update_timers()
        self.update_direction()
        self.update_state()

        self.move(dt)

        self.animate(dt, self.state, self.timers["flash"].active)

        if self.timers["can_damage_player"].active and self.deal_damage_circle.is_colliding_rect(self.player.hitbox) and self.action == "attack":
            self.deal_damage_to_player()
            self.timers["can_damage_player"].deactivate()

        if pygame.key.get_pressed()[pygame.K_q]:
            self.take_damage(1)

class Slime(Enemy):
    animation_frames = {
            "idle_right" : [],
            "idle_left" : [],
            "walk_right" : [],
            "walk_left" : [],
        }
    def __init__(self, pos, sprite_groups):
        super().__init__("slime", pos, sprite_groups, self.animation_frames, "left", (1,1), 50, 50, 20) 


class RedHood(Enemy):
    animation_frames = {
            "idle_right" : [],
            "idle_left" : [],
            "walk_right" : [],
            "walk_left" : [],
            "attack_left" : [],
            "attack_right" : []
        }
    def __init__(self, pos : tuple, sprite_groups : list, player : Player):
        super().__init__(
            entity_name = "red_hood", 
            pos = pos, # start position
            sprite_groups = sprite_groups, 
            animation_frames = self.animation_frames,
            starting_direction = "left", 
            hitbox_inflate_values = (14,6), 
            walking_speed = 100, 
            walking_speed_while_attacking = 100, 
            max_health = 100, 
            detect_player_radius = 100, 
            player = player,
            attack_radius = 20, 
            attack_speed = 8,
            attack_cooldown_duration = 500, # milliseconds
            damage = 10, 
            max_distance_to_player_to_start_attack_animation = 14,
            default_animation_play_speed = 6,
            image_scale_ratio = SCALE_RATIO / 1.2 
        )