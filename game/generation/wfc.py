from __future__ import annotations

import tcod
import numpy as np
from PIL import Image


from enum import Enum, auto
from typing import Optional, Literal, Union, TYPE_CHECKING
import math
import copy
import random


#Types

#Currently, a tile is represented by a tuple (r,g,b) of its color in the training image,
#or None if the 'tile' is out of bounds (This will allow us to create edge constraints).
#TODO: instead of a tuple, a tile should be represented by an Enum representing its type.
Tile = Optional[int] 

Color = tuple[int, int, int]

Center = tuple[Literal[0], Literal[0]]
Up = tuple[Literal[0], Literal[1]]
Down = tuple[Literal[0], Literal[-1]]
Left = tuple[Literal[-1], Literal[0]]
Right = tuple[Literal[1], Literal[0]]
TopRight = tuple[Literal[1], Literal[1]]
BottomRight = tuple[Literal[1], Literal[-1]]
TopLeft = tuple[Literal[-1], Literal[1]]
BottomLeft = tuple[Literal[-1], Literal[-1]]
Direction = TopLeft | Up | TopRight | Left | Center | Right | BottomLeft | Down | BottomRight

Coordinates = tuple[int,int]
Size = tuple[int, int]

Weights = dict[Tile, int]
Superposition = tuple[set[Tile], set[Tile], set[Tile], set[Tile], set[Tile], set[Tile], set[Tile], set[Tile], set[Tile]]
Pattern = tuple[Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile]

CENTER = (0, 0)
UP = (0, 1)
RIGHT = (1, 0)
DOWN = (0, -1)
LEFT = (-1, 0)
TOPRIGHT = (1, 1)
BOTTOMRIGHT = (1, -1)
BOTTOMLEFT = (-1, -1)
TOPLEFT = (-1, 1)

DIRECTIONS = (
    TOPLEFT,
    UP,
    TOPRIGHT,
    LEFT,
    CENTER,
    RIGHT,
    BOTTOMLEFT,
    DOWN,
    BOTTOMRIGHT
)

def reverse_direction(direction: Direction) -> Direction:
    dx, dy = direction
    return (-dx, -dy)

class WFC_Board(object):

    def __init__(self, size: Size, input_image_path: str) -> None:
        self.width, self.height = size
        self.initial_board = None
        self.build_patterns(input_image_path)
        self.reset_board()
        

        

    def reset_board(self):

        if self.initial_board == None:
            self.board: list[list[dict[Pattern, int]]] = []

            for y in range(self.height):
                new_row = []
                for x in range(self.width):
                    new_row.append(self.get_initial_weight((x,y)))
                self.board.append(new_row)

            for y in range(self.height):
                for x in range(self.width):
                    self.propagate((x,y))


            self.initial_board = copy.deepcopy(self.board)

        else:
            self.board = copy.deepcopy(self.initial_board)

    def get_initial_weight(self, coords):
        x, y = coords
        weights = copy.deepcopy(self.patterns)
        for direction in DIRECTIONS:
            dx, dy = direction
            
            if direction == CENTER:
                continue

            if x + dx < 0 or x + dx >= self.width or y + dy < 0 or y + dy >= self.height:
                to_remove = []
                for pattern in weights:
                    for i, d in enumerate(DIRECTIONS):
                        if direction == d:
                            if not (pattern[i] == None):
                                to_remove.append(pattern)

                for removal in to_remove:
                    del weights[removal]

        return weights


    def __build_abstraction_dicts(self, pixel_array: np.ndarray):
        self.color_to_int: dict[Color, int] = {}
        color_num = 0
        for row in pixel_array:
            for pixel in row:
                r, g, b = (int(v) for v in pixel)
                pixel_color = (r,g,b)
                if not (pixel_color in self.color_to_int.keys()):
                    self.color_to_int[pixel_color] = color_num
                    color_num += 1   

        self.int_to_color = {v: k for k, v in self.color_to_int.items()}

    def __get_abstract_pixel_array(self, pixel_array: np.ndarray) -> list[list[Tile]]:
        new_arr = []

        for row in pixel_array:
            new_row = []
            for pixel in row:
                r, g, b = (int(v) for v in pixel)
                pixel_color = (r,g,b)
                new_row.append(self.color_to_int[pixel_color])
            new_arr.append(new_row)
        
        return new_arr
    
    def get_options(self, coords: Coordinates) -> set[Tile]:
        x, y = coords

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return {None}
        else:
            tile = self.board[y][x]
            options: set[Tile] = set()
            for pattern, count in zip(tile.keys(), tile.values()):
                if count > 0:
                    #TODO: Right now, I have the center (the possible collapse options) at pattern[0]. This is subject to change and this should not be hardcoded like this
                    options.add(pattern[4])

            return options

    
    def shannon_entropy(self, coords: Coordinates) -> float:
        x, y = coords
        
        #assert(len(self.get_options(coords)) > 0)
        if len(self.get_options(coords)) == 1:
            return 0

        sum_of_weights = 0
        sum_of_log_weights = 0
        for option in self.board[y][x].keys():
            weight = self.board[y][x][option]
            sum_of_weights += weight
            sum_of_log_weights += weight * math.log(weight)

        return math.log(sum_of_weights) - (sum_of_log_weights / sum_of_weights)
    
    def get_min_entropy_coords(self) -> Coordinates:
        min_entropy = math.inf
        min_entropy_coords = None

        for y in range(self.height):
            for x in range(self.width):
                s_e = self.shannon_entropy((x,y))
                if s_e > 0 and s_e < min_entropy:
                    min_entropy = s_e
                    min_entropy_coords = (x,y)
        
        assert(min_entropy_coords != None)
        return min_entropy_coords
    
    @property
    def fully_collapsed(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.shannon_entropy((x,y)) > 0:
                    return False
        return True

    def build_board(self):
        while not self.fully_collapsed:
            coords = self.get_min_entropy_coords()
            self.collapse(coords)
            if not self.propagate(coords):
                self.reset_board()

    
    def collapse(self, coords: Coordinates) -> None:
        x, y = coords

        choices = list(self.board[y][x].keys())
        weights = list(self.board[y][x].values())

        pick = random.choices(choices, weights, k=1)[0]

        self.board[y][x] = {pick: 1}

        print(f"Collapsed {coords} to {self.int_to_color[pick[0]]}")

    def propagate(self, coords: Coordinates) -> bool:
        
        stack = [coords]

        while len(stack) > 0:
            current_coords = stack.pop()

            curr_x, curr_y = current_coords

            current_possible_tiles = self.get_options(current_coords)

            if len(current_possible_tiles) == 0:
                return False

            #print(f"{current_coords}: {len(self.board[curr_y][curr_x].keys())}")

            for direction in self.get_valid_directions(current_coords):
                dx, dy = direction
                other_coords = (curr_x + dx, curr_y + dy)

                if len(self.get_options(other_coords)) == 0:
                    return False

                if self.shannon_entropy(other_coords) == 0:
                    continue

                other_tile_needs_refresh = self.constrain(current_coords, direction, current_possible_tiles)

                if other_tile_needs_refresh:
                    stack.append(other_coords)

        return True






    def get_valid_directions(self, coords: Coordinates):
        x, y = coords
        valid_directions = []
        for direction in DIRECTIONS:
            dx, dy = direction
            if x + dx < 0 or x + dx >= self.width or y + dy < 0 or y + dy >= self.height:
                continue
            elif direction == CENTER:
                continue
            else:
                valid_directions.append(direction)
        #print(f"coords: {coords}, valid:{valid_directions}")
        return valid_directions


    def constrain(self, coords: Coordinates, direction: Direction, tiles: set[Tile]) -> bool:
        x, y = coords
        flag = False
        to_remove = []
        for pattern in self.board[y][x].keys():
            for i, d in enumerate(DIRECTIONS):
                if direction == d:
                    if not (pattern[i] in tiles):
                        to_remove.append(pattern)
                        flag = True

        for removal in to_remove:
            del self.board[y][x][removal]

        return flag
        
    def get_overlap_offsets(self, coords1: Coordinates, coords2: Coordinates, radius: int):
        if radius != 1:
            raise NotImplementedError
        
        x1, y1 = coords1
        x2, y2 = coords2

        region1_coords = list((x1 + dx, y1 + dy) for dx, dy in DIRECTIONS)
        region2_coords = list((x2 + dx, y2 + dy) for dx, dy in DIRECTIONS)

        overlap_coords = list(set(region1_coords) & set(region2_coords))
        
        coord1_overlap_offsets = list((x - x1, y - y1) for x, y in overlap_coords)
        coord2_overlap_offsets = list((x - x2, y - y2) for x, y in overlap_coords)

        return (coord1_overlap_offsets, coord2_overlap_offsets)


    def build_patterns(self, input_image_path: str) -> None:
        input_image = Image.open(input_image_path).convert('RGB')
        pixel_array = np.asarray(input_image)

        self.__build_abstraction_dicts(pixel_array)
        clean_input = self.__get_abstract_pixel_array(pixel_array)

        input_height = len(clean_input)
        input_width = len(clean_input[0])

        self.patterns: dict[Pattern, int] = {}  

        for y, row in enumerate(clean_input):
            for x, _ in enumerate(row):
                observations = []
                for direction in DIRECTIONS:
                    dx, dy = direction
                    if x + dx < 0 or x + dx >= input_width or y + dy < 0 or y + dy >= input_height:
                        observations.append(None)
                    else:
                        observations.append(clean_input[y+dy][x+dx])

                tuple_obs = tuple(observations)

                if tuple_obs in self.patterns.keys():
                    self.patterns[tuple_obs] += 1
                else:
                    self.patterns[tuple_obs] = 1

    def save_image(self):
        pixels = []
        for row in self.board:
            r = []
            for pixel in row:
                r.append(self.int_to_color[list(pixel.keys())[0][4]])
                    
            pixels.append(r)
        
        array = np.array(pixels, dtype=np.uint8) 

        new_image = Image.fromarray(array)

        new_image.save("test.png")

    
    def make_gif(self, frames):
        new_frames = []
        for image in frames:
            assert(isinstance(image,Image.Image))
            new_frames.append(image.resize((300, 300), Image.Resampling.NEAREST))
        frame_one = new_frames[0]
        frame_one.save("test.gif", format="GIF", append_images=new_frames,
                save_all=True, duration=1, loop=0)
        
    def print_patterns(self):
        for pattern in self.patterns.keys():
            print(f"Pattern appears {self.patterns[pattern]} times:")
            for i in range(3):
                print(pattern[(i*3):((i+1)*3)])




                 





def main():
    test = WFC_Board((10,10), "data/qud.png")
    test.build_board()
    test.save_image()

if __name__ == "__main__":
    main()



# def tupleify(ndarray):
#     """
#     temp function to turn nd array to tuple
#     """
#     r = int(ndarray[0])
#     g = int(ndarray[1])
#     b = int(ndarray[2])

#     return (r, g, b)
    

# class WFC_Ruleset(object):
#     def __init__(self, training_image_path, search_depth = 1) -> None:
#         self.build_ruleset(training_image_path, search_depth)

#     def build_ruleset(self, training_image_path, search_depth = 1) -> None:
#         training_image = Image.open(training_image_path).convert('RGB')
        
#         pixel_array = WFC_Ruleset.clean_nparray(np.asarray(training_image))

#         height = len(pixel_array)
#         width = len(pixel_array[0])

#         self.ruleset: Ruleset = {}
#         self.default_weights: Weights = {}

#         #TODO: CHECK THE LOADING ORDER OF THE PIXELS
#         for y_raw in range(height):
#             y = height - 1 - y_raw
#             for x in range(width):
#                 observation = WFC_Ruleset.get_observation(pixel_array, (x,y))
#                 tile = tupleify(pixel_array[y][x])

#                 #record tile frequency for default_weight:
#                 if tile in self.default_weights:
#                     self.default_weights[tile] += 1
#                 else:
#                     self.default_weights[tile] = 1

#                 if observation in self.ruleset:
#                     weights = self.ruleset[observation]
#                     if tile in weights:
#                         weights[tile] = weights[tile] + 1
#                     else:
#                         weights[tile] = 1
#                 else:
#                     self.ruleset[observation] = {tile: 1}
    
#     def get_options_from_observation(self, observation: Observation) -> Weights:
#         options: Weights = {}

#         for rule in self.ruleset.keys():
#             if WFC_Ruleset.is_match(rule, observation):
#                 weights = self.ruleset[rule]
#                 for tile in weights.keys():
#                     if tile in options:
#                         options[tile] = options[tile] + (weights[tile])
#                     else:
#                         options[tile] = weights[tile]

#         return options

#     @staticmethod
#     def clean_nparray(arr: np.ndarray) -> list[list[Tile]]:
#         new_arr = []
#         for row in arr:
#             new_row = []
#             for tile in row:
#                 new_row.append(tupleify(tile))
#             new_arr.insert(0, new_row)

#         return new_arr

#     @staticmethod
#     def is_match(observation_a: Observation, observation_b: Observation) -> bool:
#         assert(len(observation_a) == len(observation_b) == len(DIRECTIONS))
#         for i in range(len(observation_a)):
#             if not observation_a[i].issubset(observation_b[i]):
#                 return False
#         return True

#     @staticmethod
#     def get_obs_str(observation: Observation) -> str:
#         o_arr = [
#             ["", "", ""],
#             ["", "", ""],
#             ["", "", ""],
#         ]
#         o_arr[1][1] = "#"

#         for i, dir in enumerate(DIRECTIONS):
#             x, y = dir
#             x += 1
#             y += 1
#             if observation[i] == frozenset({(np.uint8(0), np.uint8(0), np.uint8(0))}):
#                 o_arr[y][x] = "B"
#             elif observation[i] == frozenset({(np.uint8(255), np.uint8(255), np.uint8(255))}):
#                 o_arr[y][x] = "W"
#             else:
#                 o_arr[y][x] = "?"

#         ostr = ""
#         for row  in o_arr:
#             for c in row:
#                ostr += c
#             ostr += "\n" 

#         return ostr

#     @staticmethod
#     def get_observation(pixel_array: list[list[Tile]], coords: Coordinates) -> Observation:

#         x, y = coords

#         height = len(pixel_array)
#         width = len(pixel_array[0])

#         observation = []

#         for direction in DIRECTIONS:
#             dx, dy = direction

#             if x + dx < 0 or y + dy < 0 or x + dx >= width or y + dy >= height:
#                 observation.append(frozenset({None}))
#             else:
#                 observation.append(frozenset({tupleify(pixel_array[y+dy][x+dx])}))
        
#         return tuple(observation)
    
    


                

                



# class WFC_Tile(object):

#     """
#     Stores data about a single tile in the WFC_Board. 
#     """

#     def __init__(self, parent: WFC_Board, coords: Coordinates, weights: Weights) -> None:
#         self.parent: WFC_Board = parent
#         self.coords: Coordinates = coords
#         self.weights: Weights = weights
#         self.collapsed = False
#         self.previous_state = weights
#         self.new = False
#         self.attempts = []

    
#     @property
#     def shannon_entropy(self):


#         if self.collapsed:
#             return 0
        
#         return len(self.weights.keys()) / len(self.parent.ruleset.default_weights.keys())


#         # sum_of_weights = 0
#         # sum_of_log_weights = 0 

#         # #print(list(self.weights.values()))

#         # for weight in self.weights.values():
#         #     sum_of_weights += weight
#         #     sum_of_log_weights += weight * math.log(weight)
        
#         # return math.log(sum_of_weights) - (sum_of_log_weights / sum_of_weights)
    
#     @property
#     def color(self):
#         if self.new:
#             self.new = False 
#             return (0,0,255)
        
#         r = -1
#         g = -1
#         b = -1

#         assert(len(self.weights)>= 1)

#         sum_weights = sum(self.weights.values())

#         for tile in self.weights.keys():
#             tr, tg, tb = tile

#             tr *= (self.weights[tile] / sum_weights)
#             tg *= (self.weights[tile] / sum_weights)
#             tb *= (self.weights[tile] / sum_weights)

#             tr = int(tr)
#             tg = int(tg)
#             tb = int(tb)

#             if r == -1:
#                 r = tr
#                 g = tg
#                 b = tb
#             else:
#                 r += tr
#                 g += tg
#                 b += tb

#         return (r,g,b)


#     @property
#     def choice(self):
#         assert(self.collapsed)
#         return list(self.weights.keys())[0]
    
#     def collapse(self):
#         self.collapsed = True
        
#         self.previous_state = self.weights

#         options = list(self.weights.keys())
#         weights = list(self.weights.values())
#         choice = random.choices(options, weights, k=1)[0]

#         self.attempts.append(choice)

#         self.weights: dict[Tile, int] = {choice: 100}

#         self.new = True
    
#     def uncollapse(self):
#         self.collapsed = False
#         self.weights = self.previous_state

#     def reset(self):
#         self.collapsed =  False
#         self.attempts = []
#         self.weights = self.previous_state

#     def get_tile_type(self):
#         assert(self.collapsed)
#         options = list(self.weights.keys())
#         assert(len(options)) == 1
#         return options[0]
    
#     def get_options(self) -> Weights:
#         if self.collapsed:
#             return self.weights

#         x, y = self.coords

#         width = self.parent.width
#         height = self.parent.height

#         observation = []

#         for direction in DIRECTIONS:
#             dx, dy = direction

#             if x + dx < 0 or y + dy < 0 or x + dx >= width or y + dy >= height:
#                 observation.append(frozenset({None}))
#             else:
#                 observation.append(frozenset(self.parent.get_tile_at((x+dx, y+dy)).weights.keys()))
        
#         observation = tuple(observation)

#         options = self.parent.ruleset.get_options_from_observation(observation)

#         return options




        

# class WFC_Board(object):

#     """
#     Stores the state of the WFC board. The board is comprised of WFC_Tiles, which may or not be collapsed.
#     (0,0) is the bottom left corner of the board.
#     TODO: probably not an intuitive coordinate system, could be fixed
#     """

#     def __init__(self, width, height, ruleset: WFC_Ruleset) -> None:
#         self.width = width
#         self.height = height
#         self.board: list[list[WFC_Tile]] = []
#         self.ruleset: WFC_Ruleset = ruleset
        
#         self.reset_board()
        
#     def reset_board(self):
#         self.board: list[list[WFC_Tile]] = []

#         for y in range(self.height):
#             new_row = []
#             for x in range(self.width):
#                 observation = []

#                 for direction in DIRECTIONS:
#                     dx, dy = direction

#                     if x + dx < 0 or y + dy < 0 or x + dx >= self.width or y + dy >= self.height:
#                         observation.append(frozenset({None}))
#                     else:
#                         observation.append(frozenset(self.ruleset.default_weights.keys()))
                
#                 observation = tuple(observation)

#                 weights = self.ruleset.get_options_from_observation(observation)

#                 new_row.append(WFC_Tile(self, (x, y), weights))

#             self.board.insert(0, new_row)

#     def get_valid_directions(self, coords: Coordinates) -> list[Direction]:
#         x, y = coords

        
        
#         valid_directions = []

#         for direction in DIRECTIONS:
#             dx, dy = direction

#             if x + dx < 0 or y + dy < 0:
#                 continue
#             if x + dx >= self.width or y + dy >= self.height:
#                 continue

#             valid_directions.append(direction)

#         return valid_directions
    
#     @property
#     def is_fully_collapsed(self) -> bool:
#         for row in self.board:
#             for tile in row:
#                 assert(isinstance(tile, WFC_Tile))
#                 if not tile.collapsed:
#                     return False
#         return True
    
#     def get_tile_at(self, coords: Coordinates) -> WFC_Tile:
#         x, y = coords
#         y = self.height - 1 - y
#         return self.board[y][x]

#     def get_min_entropy_tile(self):
#         assert(not self.is_fully_collapsed) #If the board is fully collapsed, we dont have a min entropy tile
#         min_entropy = math.inf
#         min_entropy_tile: WFC_Tile = None
#         for row in self.board:
#             for tile in row:
#                 assert(isinstance(tile, WFC_Tile))

#                 #We don't want to return a tile that is already collapsed! (shannon_entropy = 0 when collapsed)
#                 if tile.collapsed:
#                     continue
#                 if tile.shannon_entropy < min_entropy:
#                     min_entropy = tile.shannon_entropy
#                     min_entropy_tile = tile
        
#         assert (min_entropy_tile != None) #We should not get here without having min entropy tile

#         return min_entropy_tile

#     def build_board(self):
#         images = []
#         board_states = []
#         while not self.is_fully_collapsed:
#             images.append(self.get_image())
#             if not self.iterate():
#                 images = []
#                 self.reset_board()

#         images.append(self.get_image())

#         self.make_gif(images)



#     def iterate(self) -> bool:
#         next_tile: WFC_Tile = self.get_min_entropy_tile()
#         next_tile.collapse()
#         return self.propagate(next_tile)

#     def propagate(self, tile: WFC_Tile) -> bool:

#         propagation_stack = [tile]

#         while len(propagation_stack) > 0:
#             current_tile = propagation_stack.pop()
#             x, y = current_tile.coords
#             for direction in self.get_valid_directions(current_tile.coords):
#                 dx, dy = direction

#                 other_tile: WFC_Tile = self.get_tile_at((x + dx, y + dy))

#                 if other_tile.collapsed:
#                     continue

#                 other_options = other_tile.get_options()
#                 other_weights = other_tile.weights

#                 if len(other_options.keys()) == 0:
#                     print("BAD!")
#                     return False
                
#                 #if set(other_options.keys()) != set(other_weights.keys()):
#                 if other_options != other_weights:
#                     propagation_stack.append(other_tile)
#                     other_tile.weights = other_options

                

#         return True

#     def get_image(self) -> Image.Image:
#         pixels = []
#         for row in self.board:
#             r = []
#             for pixel in row:
#                 r.append(pixel.color)
                    
#             pixels.append(r)
        
#         array = np.array(pixels, dtype=np.uint8)

#         new_image = Image.fromarray(array)

#         return new_image
    

#     def make_gif(self, frames):
#         new_frames = []
#         for image in frames:
#             assert(isinstance(image,Image.Image))
#             new_frames.append(image.resize((300, 300), Image.Resampling.NEAREST))
#         frame_one = new_frames[0]
#         frame_one.save("test.gif", format="GIF", append_images=new_frames,
#                 save_all=True, duration=1, loop=0)






# def main():
#     rules = WFC_Ruleset("data/Font.png")
#     board = WFC_Board(20, 20, rules)
#     board.build_board()
#     image = board.get_image()
#     image.save('test.png')

# if __name__ == "__main__":
#     main()

