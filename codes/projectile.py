import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, sprite_group, name, image, pos : pygame.Vector2, direction_vector : pygame.Vector2, life_span = -1, damage = 0, velocity = 300): # life_span = -1 : projectile will not be destroyed until collision/in the air.
        super().__init__(sprite_group)
        
        # Sprite Class Setup
        self.image = image
        self.rect = self.image.get_rect(center = pos)
        self.name = name

        # Life Span 
        self.spawn_time = pygame.time.get_ticks()
        self.life_span = life_span

        # Damage
        self.damage = damage

        # Movement
        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = velocity
        self.direction_vector = direction_vector

    def move(self, dt):
        self.pos += self.direction_vector * self.velocity * dt
        self.rect.center = self.pos
        
    def update(self, dt):
        if not self.life_span == -1: # the projectile should destroy itself.
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time >= self.life_span:
                self.kill() # removing the sprite from the group to which it belongs