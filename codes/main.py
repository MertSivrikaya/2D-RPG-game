import pygame, sys
from settings import * 
from scene import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
   
        self.current_scene = Scene() # scene to display on the surface    
    def run(self):
        while True: # game loop
            for event in pygame.event.get(): # event loop
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000 # turns it into seconds
            
            self.current_scene.load(dt)
            pygame.display.update()
   
if __name__ == "__main__":
    game = Game()
    game.run()  
