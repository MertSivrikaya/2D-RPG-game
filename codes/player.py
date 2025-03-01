import pygame
from tool import *
from timers import Timer
from entity import *
from circle import Circle

class Player(Entity):
    animation_frames = {
            "idle_right" : [],
            "idle_left" : [],
            "idle_down" : [],
            "idle_up" : [],
            "walk_right" : [],
            "walk_left" : [],
            "walk_down" : [],
            "walk_up" : [],
            "walk_down_right": [],
            "walk_down_left" : [],
            "walk_up_right" : [],
            "walk_up_left" : [],
            "sword_attack_right" : [],
            "sword_attack_left" : [],
            "sword_attack_down" : [],
            "sword_attack_up" : [],
            "sword_attack_down_right" : [],
            "sword_attack_down_left" : []
        } 
    
    def __init__(self, pos, sprite_groups, current_scene):
        super().__init__("player", pos, sprite_groups, self.animation_frames, "down", (22,16), 200, 80, 6, 100) # as soon as a Player() instace is created, that instance will be added to the given sprite group
        
        # Tools
        self.owned_melee_weapons = []
        self.owned_ranged_weapons = []
        self.add_tool_to_inventory(Sword(20, 16, 3))

        self.selected_melee_weapon = self.owned_melee_weapons[0] 
        self.selected_ranged_weapon = None
        
        self.tool_being_used = None

        # Hit Animation Setup
        self.invulnerable_duration = 3000 # milliseconds
        
        self.hit_animation_frame_index = 0
        self.hit_animation_play_speed = 4

        # Scene
        self.current_scene = current_scene

        # Screen Shake
        self.screen_shake_magnitude_on_take_damage = 7
        self.screen_shake_magnitude_on_deal_damage = 2

        # Timers
        self.timers = {
            "sword_attack_animation" : Timer(Entity.get_animation_duration("sword_attack", Sword.attack_speed, self.animation_frames), self.end_tool_use), # if we wrote self.deal_melee_attack_damage(), we would refer to the value returned from the function, not the function itself (which is None since it is a void function)
            "sword_cooldown" : Timer(Sword.attack_cooldown_duration),
            "deal_damage_after_sword": Timer(Entity.get_animation_duration("sword_attack", Sword.attack_speed, self.animation_frames) / 4, self.deal_melee_attack_damage),
            
            "flash" : Timer(self.flash_duration),
            "invulnerable" : Timer(self.invulnerable_duration)
        }

    def get_input(self):
        keys = pygame.key.get_pressed()
        # Movement
        if keys[pygame.K_w]:
            self.direction_vector.y = -1
            if self.action == "idle" or self.action == "walk": # # if not already attacking or using a tool (player shouldn't be able to turn during those)
                
                if keys[pygame.K_a]: # up left diagonal movement
                    self.direction = "up_left"
                elif keys[pygame.K_d]: # up right diagonal movement
                    self.direction = "up_right"
                else:
                    self.direction = "up"
        
        elif keys[pygame.K_s]:
            self.direction_vector.y = 1
            if self.action == "idle" or self.action == "walk":
                
                if keys[pygame.K_a]: # down left diagonal movement
                    self.direction = "down_left"
                elif keys[pygame.K_d]: # down right diagonal movement
                    self.direction = "down_right"
                else:
                    self.direction = "down"
        
        else:
            self.direction_vector.y = 0

        if keys[pygame.K_d]:
            self.direction_vector.x = 1
            if self.action == "idle" or self.action == "walk":
                
                if keys[pygame.K_w]: # up right diagonal movement
                    self.direction = "up_right"
                elif keys[pygame.K_s]: # down right diagonal movement
                    self.direction = "down_right"
                else:
                    self.direction = "right"
        
        elif keys[pygame.K_a]:  
            self.direction_vector.x = -1
            if self.action == "idle" or self.action == "walk":
                
                if keys[pygame.K_w]: # up left diagonal movement
                    self.direction = "up_left"
                elif keys[pygame.K_s]: # down left diagonal movement
                    self.direction = "down_left"
                else:
                    self.direction = "left"
        
        else:
            self.direction_vector.x = 0

        if self.action == "idle" or self.action == "walk": # Player shouldn't be able to attack while already attacking
            # Attack and Tool Use
            if keys[pygame.K_SPACE] and not self.timers[self.selected_melee_weapon.name + "_cooldown"].active: # Melee Attack
                self.use_tool("attack", self.selected_melee_weapon, self.walking_speed_while_attacking)

                # q : tool switch
                # x : melee attack
                # c: ranged attack

                # On tool switch, activate the cooldown timer for the switched tool so that the player cannot spam tools while switching them.

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

    def use_tool(self, action, tool_being_used : Tool, player_walk_speed_with_tool = 0): # will be called when player presses the attack or tool use buttons
        self.action = action
        self.animation_frame_index = 0
        self.animation_play_speed = tool_being_used.animation_play_speed

        self.tool_being_used = tool_being_used

        self.velocity = player_walk_speed_with_tool

        # Activate the timer for current action with the tool_being_used to play its animation
        timer_name = self.tool_being_used.name + "_" + self.action + "_animation"
        self.timers[timer_name].activate()
        
        # Activate the 'deal_damage_after_[item_name]' timer
        if isinstance(tool_being_used, MeleeWeapon):
            self.timers["deal_damage_after_" + tool_being_used.name].activate()

    def end_tool_use(self):
        self.velocity = self.walking_speed # return to normal walking speed

        # Exit attack animation
        self.action = "idle"
        self.animation_frame_index = 0
        self.animation_play_speed = self.default_animation_play_speed

        # If the latest action is melee tool use, activate the cooldown timer for that tool.
        if isinstance(self.tool_being_used, MeleeWeapon):
             self.timers[self.selected_melee_weapon.name + "_cooldown"].activate()

        # Set the bool_being_used to None so that the tool use animations will not play
        self.tool_being_used = None

    def deal_melee_attack_damage(self): # will be called at the end of 'deal_damage_after[item_name]' timer

        def is_in_attack_range(enemy_rect : pygame.Rect):
            if self.direction == "up":
                angle = (45, 135)

            elif self.direction == "down":
                angle = (225, 315)
                
            elif self.direction == "left":
                angle = (135, 225)
               
            elif self.direction == "right":
                angle = (315,45)

            elif self.direction == "down_left":
                angle = (180,270)

            elif self.direction == "down_right":
                angle = (270,360)
            
            elif self.direction == "up_left":
                angle = (90,180)

            elif self.direction == "up_right":
                angle = (0, 90)
            
            attack_circle = Circle(self.pos, self.selected_melee_weapon.melee_attack_radius, angle)
            if attack_circle.is_colliding_rect(enemy_rect):
                return True
            else:
                return False
        
        for enemy_sprite in self.current_scene.enemy_sprites.sprites():
            did_hit_any_enemy = False
            if is_in_attack_range(enemy_sprite.hitbox):
                enemy_sprite.take_damage(self.selected_melee_weapon.attack_damage)
                did_hit_any_enemy = True

            if did_hit_any_enemy:
                self.screen_shake(200, self.screen_shake_magnitude_on_deal_damage)

                print("Damage dealt to all the enemies within the weapon radius")
        
    def take_damage(self, damage): 
        if not self.timers["invulnerable"].active:
            super().take_damage(damage)
            self.screen_shake(400, self.screen_shake_magnitude_on_take_damage)
            
            if self.health > 0: # player is still alive
                self.timers["flash"].activate()
                self.timers["invulnerable"].activate()
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def update_state(self): # overwrite the parent class's method
        if self.tool_being_used: # attack or harvest
            if self.action == "attack":
                self.state = self.tool_being_used.name + "_" + self.action + "_" + self.direction

            elif self.action == "harvest":
                self.state = self.tool_being_used.name + "_" + self.action + "_" + self.direction

        else:
            if self.direction_vector.magnitude() == 0:
                self.action = "idle"
            else:
                self.action = "walk"
            
            self.state = self.action + "_" + self.direction
        
    def add_tool_to_inventory(self, tool : Tool):
        if isinstance(tool, MeleeWeapon): # If it is a melee weapon
            self.owned_melee_weapons.append(tool)
        elif isinstance(tool, RangedWeapon):
            self.owned_ranged_weapons.append(tool)
    
    def animate(self, dt):
        if self.state in self.animation_frames.keys():
            state_to_look_for_animation = self.state
        else: # if the player doesn't have a diagonal animation for that state, just play the horizontal animation for that state.
            updated_state_words = [word for word in self.state.split("_") if not word == "down" and not word == "up"]
            state_to_look_for_animation = "_".join(updated_state_words)
        
        super().animate(dt, state_to_look_for_animation, self.timers["invulnerable"].active)

    def play_hit_animation(self, dt): # Overwriting the method
        if self.timers["flash"].active:
            super().play_hit_animation()
        
        else: # Make the player disapper in certain time intervals to indicate the player is invulnerable
            alpha_values = (0,255)
            
            self.hit_animation_frame_index += self.hit_animation_play_speed * dt
            if self.hit_animation_frame_index >= len(alpha_values):
                self.hit_animation_frame_index = 0
            alpha_value = alpha_values[int(self.hit_animation_frame_index)]
            
            image_to_display = self.image.copy() # if we hadn't copy() the surface and directly assigned it,  the image surfaces' alpha values in the animation frames dict would have also changed since assigning an object to a variable points out that object's memory adress rather than creating a copy of that pbject.
            image_to_display.set_alpha(alpha_value)

            self.image = image_to_display

    def screen_shake(self, duration = 200 ,magnitude = 0.5):
        self.current_scene.get_camera_group().start_screen_shake(duration, magnitude)

    def draw_gizmos(self, display_surface : pygame.Surface, display_offset : pygame.math.Vector2):
        offsetted_hitbox = self.hitbox.copy()
        offsetted_hitbox.center += display_offset

        # Player Hitbox
        pygame.draw.rect(display_surface, "Green", offsetted_hitbox, 1)
        
        # Player Melee Attack Circle
        pygame.draw.circle(display_surface, "Red", self.pos + display_offset, self.selected_melee_weapon.melee_attack_radius, 1)
        
    def update(self, dt):
        self.get_input()
        self.move(dt)
        self.update_timers()
        self.update_state()
        self.animate(dt)
       
        #self.mask = pygame.mask.from_surface(self.image)
        #mask_surface = self.mask.to_surface()
        #mask_surface.set_colorkey((0,0,0))
        #mask_surface.fill((255,255,255,100),special_flags=pygame.BLEND_RGBA_MIN)
        #pygame.display.get_surface().blit(mask_surface, self.rect)
        
        
        #pygame.display.get_surface().blit(self.mask.to_surface(self.image,None, self.image ,"white"), self.rect)