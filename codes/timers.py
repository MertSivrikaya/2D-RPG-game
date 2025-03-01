from pygame.time import get_ticks

class Timer():
    """A class representing a timer to be used in timed tasks

    Attributes:
        active (bool): Whether the timer is currently active
    
    
    
    """
    def __init__(self, duration, end_func = None, update_func = None ): # the amount of time the timer will be active as milliseconds, the function to call when the timer becomes deactive (optional)
        self.duration = duration
        self.end_func = end_func
        self.update_func = update_func
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        if self.active:
            self.active = False
            self.start_time = 0 # we want to make sure that the timer will not update itself
            
            if self.end_func: # if this func exists
                self.end_func()

    def update(self):
        if self.active: # if the timer is active
            if self.update_func:
                self.update_func()
            
            current_time = get_ticks()
            if current_time - self.start_time >= self.duration: # deactivate the timer
                self.deactivate()
                
               
                 

    