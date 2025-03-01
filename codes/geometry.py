import pygame
from math import acos, pi, sqrt

class Geometry:

    @staticmethod
    def is_point_on_line_segment(point : pygame.Vector2, line_start_point : pygame.Vector2, line_end_point : pygame.Vector2) -> bool:
        if line_start_point.y == line_end_point.y and point.y == line_start_point.y: # Horizontal line
            if line_start_point.x < line_end_point.x:
                if point.x >= line_start_point.x and point.x <= line_end_point.x:
                    return True
            else:
                if point.x >= line_end_point.x and point.x <= line_start_point.x:
                    return True
                
        elif line_start_point.x == line_end_point.x and point.x == line_start_point.x: # Vertical line
            if line_start_point.y < line_end_point.y:
                if point.y >= line_start_point.y and point.y <= line_end_point.y:
                    return True
            else:
                if point.y >= line_end_point.y and point.y <= line_start_point.y:
                    return True
                
        return False
    
    @staticmethod
    def get_positive_angle_of_line(origin : pygame.Vector2, end_point_of_line : pygame.Vector2) -> float:
        
        end_point_of_line_relative_to_origin = end_point_of_line - origin # move the origin to (0,0) and move the end point of line relative to it
        
        hypotenuse_length = origin.distance_to(end_point_of_line)
        end_point_of_line_relative_to_origin /= hypotenuse_length # making it a unit circle so that we can easily calculate the angle's trigonometric values

        angle_in_radiants = acos(end_point_of_line_relative_to_origin.x)
        angle_in_degress = (angle_in_radiants * 180) / pi # gives us a value within [0,180]

        if end_point_of_line_relative_to_origin.y > 0: # if in Quadran 3 or 4
            angle_in_degress = 360 - angle_in_degress

        return angle_in_degress 