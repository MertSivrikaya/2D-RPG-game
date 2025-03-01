from os import walk
import pygame
from settings import SCALE_RATIO

def import_folder(path, scale_ratio = SCALE_RATIO): # imports all the frames in the given folder/path and returns it as a list
    surface_list = []

    for _, __, img_files in walk(path): # (folder_name, sub_folders, file_names)
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
         
            image_surf = pygame.transform.scale(image_surf, (round(image_surf.get_width() * scale_ratio), round(image_surf.get_height() * scale_ratio)))
            surface_list.append(image_surf)

    return surface_list