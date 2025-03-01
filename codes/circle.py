import pygame
from math import sqrt
from geometry import Geometry

class Circle:
    def __init__(self, center : pygame.math.Vector2, radius : float, angle : tuple = (0,360)): # do half circle with start and end point
        self.center = center
        self.radius = radius
        self.angle = angle

    def __get_distance_to_rect_from_center(self, target_rect : pygame.rect.Rect) -> float: # only works if the circle center is outside the rect center
        nearest_point_of_rect = self.__get_nearest_point_of_rect(target_rect)
        
        distance_between_circle_center_and_nearest_point_of_rect = self.center.distance_to(nearest_point_of_rect)

        return distance_between_circle_center_and_nearest_point_of_rect

    def __get_nearest_point_of_rect(self, target_rect : pygame.rect.Rect) -> pygame.math.Vector2:
        nearest_point_of_rect_pos = (0,0) 

        if self.center.x > target_rect.right: 
            if self.center.y < target_rect.topright[1]: # if the circle center is inside quadrant 1
                nearest_point_of_rect_pos = target_rect.topright
            elif self.center.y > target_rect.bottomright[1]: # if the circle center is inside quadrant 4
                nearest_point_of_rect_pos = target_rect.bottomright
            else: # # if the circle center is inside section D
                nearest_point_of_rect_pos = (target_rect.right, self.center.y)

        elif self.center.x < target_rect.left:
            if self.center.y < target_rect.topleft[1]: # if the circle center is inside quadrant 2
                nearest_point_of_rect_pos = target_rect.topleft
            elif self.center.y > target_rect.bottomleft[1]: # if the circle center is inside quadrant 3
                nearest_point_of_rect_pos = target_rect.bottomleft
            else: # # if the circle center is inside section B
                nearest_point_of_rect_pos = (target_rect.left, self.center.y)

        else:
            if self.center.y < target_rect.top: # # if the circle center is inside section A
                nearest_point_of_rect_pos = (self.center.x, target_rect.top)
        
            elif self.center.y > target_rect.bottom: # # if the circle center is inside section C
                nearest_point_of_rect_pos = (self.center.x, target_rect.bottom)

        return pygame.math.Vector2(nearest_point_of_rect_pos)

        """
                 |          |
     Quadrant 2  |    A     |   Quadrant 1
                 |          |
                 |          |
        ---------++++++++++++-----------
                 +          +
           B     +   Rect   +     D
                 +          +
                 +          +
        ---------++++++++++++-----------
                 |          |
     Quadrant 3  |    C     |   Quadrant 4    
                 |          |
                 |          |
        
        """

    def is_colliding_rect(self, target_rect : pygame.rect.Rect) -> bool:
        if self.__is_circle_center_inside_of_rectangle(target_rect):
            return True
        else:
            if self.__get_distance_to_rect_from_center(target_rect) <= self.radius: # collision
                if self.angle == (0,360):
                    return True
                
                else:
                    nearest_point_of_rect = self.__get_nearest_point_of_rect(target_rect)

                    if (nearest_point_of_rect.x, nearest_point_of_rect.y) in [target_rect.bottomleft, target_rect.bottomright, target_rect.topleft, target_rect.topright]: # if the nearest point of the rect is one of its corner / if the circle is on of the quadrants.
                
                        angle_in_degrees = Geometry.get_positive_angle_of_line(self.center, nearest_point_of_rect)
                        print(angle_in_degrees)
                    
                        if self.angle[0] < self.angle[1]:
                            if angle_in_degrees >= self.angle[0] and angle_in_degrees <= self.angle[1]:
                                return True
                            else:
                                return False
                            
                        else:
                            if angle_in_degrees >= self.angle[0] or angle_in_degrees <= self.angle[1]:
                                return True
                            else:
                                return False
                            
                    else: # if the circle is in region A,B,C or D
            
                        if self.center.y < target_rect.top: # Region A
                            corners_to_look_for = [pygame.Vector2(target_rect.topright), pygame.Vector2(target_rect.topleft)]
                           
                        elif self.center.y > target_rect.bottom: # Region C
                            corners_to_look_for = [pygame.Vector2(target_rect.bottomleft), pygame.Vector2(target_rect.bottomright)]
                          
                        elif self.center.x < target_rect.left: # Region B
                            corners_to_look_for = [pygame.Vector2(target_rect.topleft), pygame.Vector2(target_rect.bottomleft)]
                           
                        elif self.center.x > target_rect.right: # Region D
                            corners_to_look_for = [pygame.Vector2(target_rect.bottomright), pygame.Vector2(target_rect.topright)]
                        
                        points_to_look_for = []

                        for corner_to_look_for_index ,corner_to_look_for in enumerate(corners_to_look_for):
                            if self.does_contain_point(corner_to_look_for):
                                points_to_look_for.append(corner_to_look_for.copy())

                            else:
                                if corners_to_look_for[0].y == corners_to_look_for[1].y: # horizontal edge
                                    intersection_points = self.__get_intersection_points_with_line(None, corner_to_look_for.y)
                                else:
                                    intersection_points = self.__get_intersection_points_with_line(corner_to_look_for.x, None)
                                
                                intersection_points_on_rect_edge = [point for point in intersection_points if Geometry.is_point_on_line_segment(point, corners_to_look_for[0], corners_to_look_for[1])]
                                #print(intersection_points)

                                if len(intersection_points_on_rect_edge) == 2:
                                    points_to_look_for.append(intersection_points_on_rect_edge[corner_to_look_for_index])
                                else:
                                    points_to_look_for.append(intersection_points_on_rect_edge[0])  

                        average_point = (points_to_look_for[0] + points_to_look_for[1]) / 2     

                        average_angle = Geometry.get_positive_angle_of_line(self.center, average_point)

                        if self.angle[0] < self.angle[1]:
                            if self.angle[0] <= average_angle and average_angle <= self.angle[1]:
                                return True
                            else:
                                return False
                            
                        else:
                            if average_angle >= self.angle[0] or average_angle <= self.angle[1]:
                                return True
                            else:
                                return False
            
            else:
                return False
        
    def __is_circle_center_inside_of_rectangle(self, target_rect: pygame.rect.Rect) -> bool:
        if self.center.x >= target_rect.left and self.center.x <= target_rect.right:
            if self.center.y >= target_rect.top and self.center.y <=  target_rect.bottom: # if the center of the circle is inside the rectangle:
                return True
            
    def does_contain_point(self, point : pygame.math.Vector2) -> bool:
        if self.center.distance_to(point) <= self.radius:
            return True
        else:
            return False
        
    def __is_point_on_arc(self, point : pygame.Vector2) -> bool:
        if self.center.distance_to(point) == self.radius:
            return True
        else: 
            return False

    def __get_intersection_points_with_line(self, x = None, y = None) -> list: # x = k or y = k
        intersection_points = []
     
        if x: # Vertical line
            x -= self.center.x # making the center relative to origin
            if x <= self.radius and x >= - self.radius:
                intersection_points.append(pygame.Vector2(x + self.center.x, (sqrt(self.radius ** 2 - x ** 2) + self.center.y)))
                intersection_points.append(pygame.Vector2(x + self.center.x, (-sqrt(self.radius ** 2 - x ** 2) + self.center.y)))

        else: # Horizontal line
            y -= self.center.y # making the center relative to origin
            if y <= self.radius and y >= - self.radius:
                intersection_points.append(pygame.Vector2((sqrt(self.radius ** 2 - y ** 2) + self.center.x), y + self.center.y))
                intersection_points.append(pygame.Vector2((-sqrt(self.radius ** 2 - y ** 2) + self.center.x), y + self.center.y))

        if len(intersection_points) == 2:
            if intersection_points[0].x == intersection_points[1].x and intersection_points[0].y == intersection_points[1].y:
                del intersection_points[-1]

        return intersection_points

  


