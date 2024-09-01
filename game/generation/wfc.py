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
Tile = Optional[tuple] 

Up = tuple[Literal[0], Literal[1]]
Down = tuple[Literal[0], Literal[-1]]
Left = tuple[Literal[-1], Literal[0]]
Right = tuple[Literal[1], Literal[0]]
TopRight = tuple[Literal[1], Literal[1]]
BottomRight = tuple[Literal[1], Literal[-1]]
TopLeft = tuple[Literal[-1], Literal[1]]
BottomLeft = tuple[Literal[-1], Literal[-1]]
Direction = Up | Down | Left | Right | TopRight | TopLeft | BottomRight | BottomLeft

Coordinates = tuple[int,int]

Weights = dict[Tile, int]

Observation = tuple[frozenset[Tile], frozenset[Tile], frozenset[Tile], frozenset[Tile], frozenset[Tile], frozenset[Tile], frozenset[Tile], frozenset[Tile]]
Ruleset = dict[Observation, Weights]

UP = (0, 1)
RIGHT = (1, 0)
DOWN = (0, -1)
LEFT = (-1, 0)
TOPRIGHT = (1, 1)
BOTTOMRIGHT = (1, -1)
BOTTOMLEFT = (-1, -1)
TOPLEFT = (-1, 1)

DIRECTIONS = (
    UP,
    RIGHT,
    DOWN,
    LEFT,
    TOPRIGHT,
    BOTTOMRIGHT,
    BOTTOMLEFT,
    TOPLEFT
)

def tupleify(ndarray):
    """
    temp function to turn nd array to tuple
    """
    r = ndarray[0]
    g = ndarray[1]
    b = ndarray[2]

    return (r, g, b)
    

class WFC_Ruleset(object):
    def __init__(self, training_image_path, search_depth = 1) -> None:
        self.build_ruleset(training_image_path, search_depth)

    def build_ruleset(self, training_image_path, search_depth = 1) -> None:
        training_image = Image.open(training_image_path).convert('RGB')
        

        width, height = training_image.size
        pixel_array = np.asarray(training_image)

        self.ruleset: Ruleset = {}
        self.default_weights: Weights = {}

        #TODO: CHECK THE LOADING ORDER OF THE PIXELS
        for y in range(height):
            for x in range(width):
                observation = WFC_Ruleset.get_observation(pixel_array, (x,y))
                tile = tupleify(pixel_array[y][x])

                #record tile frequency for default_weight:
                if tile in self.default_weights:
                    self.default_weights[tile] += 1
                else:
                    self.default_weights[tile] = 1

                if observation in self.ruleset:
                    weights = self.ruleset[observation]
                    if tile in weights:
                        weights[tile] = weights[tile] + 1
                    else:
                        weights[tile] = 1
                else:
                    self.ruleset[observation] = {tile: 1}
    
    def get_options_from_observation(self, observation: Observation) -> Weights:
        options: Weights = {}

        for rule in self.ruleset.keys():
            if WFC_Ruleset.is_match(rule, observation):
                weights = self.ruleset[rule]
                for tile in weights.keys():
                    if tile in options:
                        options[tile] = options[tile] + weights[tile]
                    else:
                        options[tile] = weights[tile]

        return options
    
    @staticmethod
    def is_match(observation_a: Observation, observation_b: Observation) -> bool:
        assert(len(observation_a) == len(observation_b) == len(DIRECTIONS))
        for i in range(len(observation_a)):
            if not observation_a[i].issubset(observation_b[i]):
                return False
        return True

    @staticmethod
    def get_obs_str(observation: Observation) -> str:
        o_arr = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        o_arr[1][1] = "#"

        for i, dir in enumerate(DIRECTIONS):
            x, y = dir
            x += 1
            y += 1
            if observation[i] == frozenset({(np.uint8(0), np.uint8(0), np.uint8(0))}):
                o_arr[y][x] = "B"
            elif observation[i] == frozenset({(np.uint8(255), np.uint8(255), np.uint8(255))}):
                o_arr[y][x] = "W"
            else:
                o_arr[y][x] = "?"

        ostr = ""
        for row  in o_arr:
            for c in row:
               ostr += c
            ostr += "\n" 

        return ostr

    @staticmethod
    def get_observation(pixel_array: np.ndarray, coords: Coordinates) -> Observation:
        x, y = coords

        height = len(pixel_array)
        width = len(pixel_array[0])

        observation = []

        for direction in DIRECTIONS:
            dx, dy = direction

            if x + dx < 0 or y - dy < 0 or x + dx >= width or y - dy >= height:
                observation.append(frozenset({None}))
            else:
                observation.append(frozenset({tupleify(pixel_array[y-dy][x+dx])}))
        
        return tuple(observation)
    
    


                

                



class WFC_Tile(object):

    """
    Stores data about a single tile in the WFC_Board. 
    """

    def __init__(self, parent: WFC_Board, coords: Coordinates, weights: Weights) -> None:
        self.parent: WFC_Board = parent
        self.coords: Coordinates = coords
        self.weights: Weights = weights
        self.collapsed = False
        self.previous_state = weights
        self.new = False
        self.attempts = []

    
    @property
    def shannon_entropy(self):


        if self.collapsed:
            return 0
        
        #return len(self.weights.keys()) / len(self.parent.ruleset.default_weights.keys())


        sum_of_weights = 0
        sum_of_log_weights = 0 

        #print(list(self.weights.values()))

        for weight in self.weights.values():
            sum_of_weights += weight
            sum_of_log_weights += weight * math.log(weight)
        
        return math.log(sum_of_weights) - (sum_of_log_weights / sum_of_weights)
    
    @property
    def color(self):
        if self.new:
            self.new = False 
            return (0,0,255)
        
        r = -1
        g = -1
        b = -1

        assert(len(self.weights)>= 1)

        sum_weights = sum(self.weights.values())

        for tile in self.weights.keys():
            tr, tg, tb = tile

            tr *= (self.weights[tile] / sum_weights)
            tg *= (self.weights[tile] / sum_weights)
            tb *= (self.weights[tile] / sum_weights)

            tr = int(tr)
            tg = int(tg)
            tb = int(tb)

            if r == -1:
                r = tr
                g = tg
                b = tb
            else:
                r += tr
                g += tg
                b += tb

        return (r,g,b)


    @property
    def choice(self):
        assert(self.collapsed)
        return list(self.weights.keys())[0]
    
    def collapse(self):
        self.collapsed = True
        
        self.previous_state = self.weights

        options = list(self.weights.keys())
        weights = list(self.weights.values())
        choice = random.choices(options, weights, k=1)[0]

        self.attempts.append(choice)

        self.weights: dict[Tile, int] = {choice: 100}

        self.new = True
    
    def uncollapse(self):
        self.collapsed = False
        self.weights = self.previous_state

    def reset(self):
        self.collapsed =  False
        self.attempts = []
        self.weights = self.previous_state

    def get_tile_type(self):
        assert(self.collapsed)
        options = list(self.weights.keys())
        assert(len(options)) == 1
        return options[0]
    
    def get_options(self) -> Weights:
        if self.collapsed:
            return self.weights

        x, y = self.coords

        width = self.parent.width
        height = self.parent.height

        observation = []

        for direction in DIRECTIONS:
            dx, dy = direction

            if x + dx < 0 or y - dy < 0 or x + dx >= width or y - dy >= height:
                observation.append(frozenset({None}))
            else:
                observation.append(frozenset(self.parent.board[y-dy][x+dx].weights))
        
        observation = tuple(observation)

        options = self.parent.ruleset.get_options_from_observation(observation)

        for attempt in self.attempts:
            if attempt in options:
                del options[attempt]

        return options




        

class WFC_Board(object):

    """
    Stores the state of the WFC board. The board is comprised of WFC_Tiles, which may or not be collapsed.
    (0,0) is the bottom left corner of the board.
    TODO: probably not an intuitive coordinate system, could be fixed
    """

    def __init__(self, width, height, ruleset: WFC_Ruleset) -> None:
        self.width = width
        self.height = height
        self.board: list[list[WFC_Tile]] = []
        self.ruleset: WFC_Ruleset = ruleset
        
        self.reset_board()
        
    def reset_board(self):
        self.board: list[list[WFC_Tile]] = []

        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                observation = []

                for direction in DIRECTIONS:
                    dx, dy = direction

                    if x + dx < 0 or y + dy < 0 or x + dx >= self.width or y + dy >= self.height:
                        observation.append(frozenset({None}))
                    else:
                        observation.append(frozenset(self.ruleset.default_weights.keys()))
                
                observation = tuple(observation)

                weights = self.ruleset.get_options_from_observation(observation)

                new_row.append(WFC_Tile(self, (x, y), weights))

            self.board.insert(0, new_row)

    def get_valid_directions(self, coords: Coordinates) -> list[Direction]:
        x, y = coords
        
        valid_directions = []

        for direction in DIRECTIONS:
            dx, dy = direction

            if x + dx < 0 or y + dy < 0:
                continue
            if x + dx >= self.width or y + dy >= self.height:
                continue

            valid_directions.append(direction)

        return valid_directions
    
    @property
    def is_fully_collapsed(self) -> bool:
        for row in self.board:
            for tile in row:
                assert(isinstance(tile, WFC_Tile))
                if not tile.collapsed:
                    return False
        return True
    
    def get_tile_at(self, coords: Coordinates):
        x, y = coords
        return self.board[y][x]

    def get_min_entropy_tile(self):
        assert(not self.is_fully_collapsed) #If the board is fully collapsed, we dont have a min entropy tile
        min_entropy = math.inf
        min_entropy_tile: WFC_Tile = None
        for row in self.board:
            for tile in row:
                assert(isinstance(tile, WFC_Tile))

                #We don't want to return a tile that is already collapsed! (shannon_entropy = 0 when collapsed)
                if tile.collapsed:
                    continue
                if tile.shannon_entropy < min_entropy:
                    min_entropy = tile.shannon_entropy
                    min_entropy_tile = tile
        
        assert (min_entropy_tile != None) #We should not get here without having min entropy tile

        return min_entropy_tile

    def build_board(self):
        images = []
        board_states = []
        while not self.is_fully_collapsed:
            images.append(self.get_image())
            #board_states.append(copy.deepcopy(self.board))
            self.iterate()


                
            

        images.append(self.get_image())

        self.make_gif(images)



    def iterate(self):
        next_tile: WFC_Tile = self.get_min_entropy_tile()
        next_tile.collapse()
        self.propagate(next_tile)

    def propagate(self, tile: WFC_Tile) :

        propagation_stack = [tile]

        while len(propagation_stack) > 0:
            current_tile = propagation_stack.pop()
            x, y = current_tile.coords
            for direction in self.get_valid_directions(current_tile.coords):
                dx, dy = direction

                other_tile: WFC_Tile = self.get_tile_at((x + dx, y + dy))

                if other_tile.collapsed:
                    continue

                other_options = other_tile.get_options()
                other_weights = other_tile.weights

                if len(other_options.keys()) == 0:
                    return False
                
                #if set(other_options.keys()) != set(other_weights.keys()):
                if other_options != other_weights:
                    propagation_stack.append(other_tile)

                other_tile.weights = other_options

                

        return True

    def get_image(self) -> Image.Image:
        pixels = []
        for row in self.board:
            r = []
            for pixel in row:
                r.append(pixel.color)
                    
            pixels.append(r)
        
        array = np.array(pixels, dtype=np.uint8)

        new_image = Image.fromarray(array)

        return new_image
    

    def make_gif(self, frames):
        new_frames = []
        for image in frames:
            assert(isinstance(image,Image.Image))
            new_frames.append(image.resize((300, 300), Image.Resampling.NEAREST))
        frame_one = new_frames[0]
        frame_one.save("test.gif", format="GIF", append_images=new_frames,
                save_all=True, duration=1, loop=0)






def main():
    rules = WFC_Ruleset("data/Dungeon.png")
    board = WFC_Board(20, 20, rules)
    board.build_board()
    image = board.get_image()
    image.save('test.png')
    



if __name__ == "__main__":
    main()

# def totuple(a):
#     try:
#         return tuple(totuple(i) for i in a)
#     except TypeError:
#         return a
    
# def reverse_direction(direction_tuple: tuple):
#     x, y = direction_tuple
#     return (-x, -y)

# #Stores the data about which possible tiles an entropic tile can be
# class WFC_TileOptions():
#     def __init__(self, tile_options: list[tuple] = [], tile_weights: list[tuple] = []) -> None:
#         self.tile_options: list[tuple] = tile_options
#         self.tile_weights: list[float] = tile_weights

#     #Equivalence function. Will return true if two TileOptions have the same options and weights,
#     #regardless of their internal order in their lists
#     def __eq__(self, value: object) -> bool:
#         if not isinstance(value, WFC_TileOptions): 
#             return False
        
#         for i, self_o in enumerate(self.tile_options):
#             flag = False
#             for j, other_o in enumerate(value.tile_options):
#                 if self_o == other_o:
#                     if self.tile_weights[i] == value.tile_weights[j]:
#                         flag = True
#                     else:
#                         return False
#             if not flag:
#                 return False
#         return True
                    
#     def add(self, option: tuple, weight: float = 1):
#         if option in self.tile_options:
#             self.tile_weights[self.tile_options.index(option)] += weight
#         else:
#             self.tile_options.append(option)
#             self.tile_weights.append(weight)
    
#     def combine(self, other_options: WFC_TileOptions):
#         for i, option in enumerate(other_options.tile_options):
#             if option in self.tile_options:
#                 self.tile_weights[self.tile_options.index(option)] += other_options.tile_weights[i]
#             else:
#                 self.tile_options.append(option)
#                 self.tile_weights.append(other_options.tile_weights[i])

#     def restrict(self, other_options: WFC_TileOptions):
#         new_options = []
#         new_weights = []
#         for other_option in other_options.tile_options:
#             if other_option in self.tile_options:
#                 new_options.append(other_option)
#                 new_weights.append(self.tile_weights[self.tile_options.index(other_option)] + other_options.tile_weights[other_options.tile_options.index(other_option)])
        
#         self.tile_options = new_options
#         self.tile_weights = new_weights
    
#     def printme(self):
#         print("----------------")
#         print(self.tile_options)
#         print(self.tile_weights)
#         print("----------------")


           

        

# class WFC_RuleData():
#     def __init__(self, direction: tuple, tile_type: tuple, count: int = 1) -> None:
#         self.direction = direction
#         self.tile_type = tile_type
#         self.count = count



# class Markov_Layer():
#     def __init__(self, depth: int) -> None:
#         self.depth = depth
#         self.rules: dict[key_type, dict[direction_type, Union[dict[direction_type, WFC_TileOptions], Markov_Layer]]] = {}
#         pass

#     def get_possible_tiles(self, tile_types: list[key_type], direction: direction_type):

#         if self.depth == 0:
#             options = WFC_TileOptions([],[])
#             for tile_type in tile_types:



#         if isinstance(options, Markov_Layer):
#             return options.get_possible_tiles()




# class WFC_Ruleset2():
#     def __init__(self) -> None:
#         pass
        
#     def build_ruleset(training_image_path: str) -> None:
#         pass




# class WFC_Ruleset():
#     def __init__(self, rules: dict[tuple, list[WFC_RuleData]]) -> None:
#         self.rules = rules

#     @staticmethod
#     def printrules(rules: dict[tuple, list[WFC_RuleData]]):
#         for key in rules.keys():
#             print(f"Rules for {key}:")
#             for direction in directions:
#                 print(f"Direction: {direction}")
#                 for rule in rules[key]:
#                     if rule.direction == direction:
#                         print(f"{rule.tile_type} : {rule.count}")


#     @staticmethod 
#     def build_rules(training_image_path: str) -> tuple[dict[tuple, list[WFC_RuleData]], dict[tuple, int]]:
#         training_image = Image.open(training_image_path).convert('RGB')
#         rules: dict[tuple, list[WFC_RuleData]] = {}
#         default_options = WFC_TileOptions([],[])
        
#         width, height = training_image.size
#         pixels = np.asarray(training_image)
        
#         for y, row in enumerate(pixels):
#             for x, pixel in enumerate(row):
#                 pixel_t = totuple(pixel)

#                 #Count this pixel for the default option
#                 default_options.add(pixel_t)

#                 for direction in directions:
                    
#                     d_x, d_y = direction
                   
#                     if x + d_x < 0 or y + d_y < 0:
#                         continue
#                     elif x + d_x >= width or y + d_y >= height:
#                         continue 

#                     other_tile = totuple(pixels[y+d_y][x+d_x])

#                     if pixel_t in rules:
                       
#                         current_rules = rules[pixel_t]
#                         flag = True
#                         for rule in current_rules:
#                             if rule.tile_type == other_tile and rule.direction == direction:
#                                 flag = False
#                                 rule.count += 1
#                         if flag:
#                             current_rules.append(WFC_RuleData(direction, other_tile))
                            
#                     else:
#                         rules[pixel_t] = [WFC_RuleData(direction, other_tile)]
#         return (rules, default_options)

#     @staticmethod
#     def get_options(ruleset: WFC_Ruleset, tile_type: tuple, direction: tuple) -> WFC_TileOptions:
#         tile_rules = ruleset.rules[tile_type]
#         options = []
#         weights = []
#         for rule in tile_rules:
#             if direction == rule.direction:
#                 options.append(rule.tile_type)
#                 weights.append(rule.count)

#         return WFC_TileOptions(options, weights)







# class WFC_Tile():
#     def __init__(self, parent: WFC_Board, x: int, y: int, tile_type: Optional[tuple] = None) -> None:
#         self.parent = parent
#         self.x = x
#         self.y = y
#         self.tile_type = tile_type

#     @property
#     def entropy(self) -> float:
#         if self.tile_type:
#             return 0
#         else:
#             return len(self.options.tile_options) / len(list(self.default_options.tile_options)) 

#     @property
#     def color(self):
#         if self.tile_type:
#             return self.tile_type
        
#         tr, tg, tb = 0, 0, 0
#         for i, color in enumerate(self.options.tile_options):
#             r, g, b = color
#             r = int(r)
#             g = int(g)
#             b = int(b)
#             r *= self.options.tile_weights[i]
#             g *= self.options.tile_weights[i]
#             b *= self.options.tile_weights[i]
#             tr += r
#             tg += g
#             tb += b
        
#         tr //= sum(self.options.tile_weights)
#         tg //= sum(self.options.tile_weights)
#         tb //= sum(self.options.tile_weights)

#         return (tr, tg, tb)

#     def build_options(self):
#         new_options = None
#         for direction in directions:
#             d_x, d_y = direction
                
#             if self.x + d_x < 0 or self.y + d_y < 0:
#                 continue
#             elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
#                 continue
                
#             neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
#             neighbor.options.printme()
#             if neighbor.entropy == 1:
#                 continue
#             neighbor_contribution = WFC_TileOptions([], [])
#             for option in neighbor.options.tile_options:
#                 neighbor_contribution.combine(WFC_Ruleset.get_options(self.ruleset, option, reverse_direction(direction)))
            

#             if new_options == None:
#                 new_options = neighbor_contribution
#             else:
#                 new_options.restrict(neighbor_contribution)

#         return new_options





        


        

#     def validate(self) -> None:
#         if self.tile_type:
#             return
        
#         new_options = self.build_options()
#         if self.options == new_options:
#             return
#         else:
#             self.options = new_options
        
#         for direction in directions:
#             d_x, d_y = direction
                
#             if self.x + d_x < 0 or self.y + d_y < 0:
#                 continue
#             elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
#                 continue

#             neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
#             if neighbor.entropy > 0:
#                 self.parent.queue_validation(neighbor)
              
        



        

#     def collapse(self) -> None:
        
#         choice = random.choices(self.options.tile_options, self.options.tile_weights)
#         self.tile_type = choice[0]
#         self.options = WFC_TileOptions([choice[0]], [1])

#         #invalidate neigbors
#         for direction in directions:
#             d_x, d_y = direction
                
#             if self.x + d_x < 0 or self.y + d_y < 0:
#                 continue
#             elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
#                 continue 

#             neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
#             if neighbor.entropy > 0:
#                 self.parent.queue_validation(neighbor)
            
            
        





            




# class WFC_Board():
#     def __init__(self, width, height, ruleset, default_options) -> None:
#         self.width = width
#         self.height = height
#         self.ruleset = ruleset
#         self.validation_queue = []
#         self.board: list[list[WFC_Tile]]= []

#         for y in range(height):
#             row = []
#             for x in range(width):
#                 row.append(WFC_Tile(self, x, y, copy.deepcopy(ruleset), default_options))
#             self.board.append(row)
                

#     def tile_at(self, x, y) -> WFC_Tile:
#         return self.board[y][x]
    
#     def collapse_tile(self, x, y) -> None:
#         self.board[y][x].collapse()

#     @property
#     def total_entropy(self) -> float:
#         total = 0
#         for row in self.board:
#             for tile in row:
#                 assert(isinstance(tile, WFC_Tile))
#                 total += tile.entropy
#         return total

#     @property
#     def is_valid(self) -> bool:
#         return len(self.validation_queue) == 0
    
#     def get_next_invalid_tile(self) -> Optional[WFC_Tile]:
#         if self.is_valid:
#             return None
#         return self.validation_queue.pop(0)

#     def queue_validation(self, tile: WFC_Tile) -> None:
#         if tile in self.validation_queue:
#             return
#         self.validation_queue.append(tile)

#     def get_lowest_entropy_tiles(self) -> list[WFC_Tile]:
#         if self.total_entropy == 0:
#             return []
        
#         lowest_tiles = []
#         lowest_entropy = 1

#         for row in self.board:
#             for tile in row:
#                 assert(isinstance(tile, WFC_Tile))
#                 if tile.entropy == 0:
#                     continue
#                 if tile.entropy == lowest_entropy:
#                     lowest_tiles.append(tile)
#                 elif tile.entropy < lowest_entropy:
#                     lowest_entropy = tile.entropy
#                     lowest_tiles = [tile]
#         return lowest_tiles


#     def build_board(self):
#         images = []
#         while self.total_entropy > 0:
#             while(not self.is_valid):
#                 tile = self.get_next_invalid_tile()
#                 tile.validate()
#             choice = random.choice(self.get_lowest_entropy_tiles())
#             choice.collapse()
#             images.append(self.export_board())
#         self.make_gif(images)

#     def make_gif(self, frames):
#         frame_one = frames[0]
#         frame_one.save("test.gif", format="GIF", append_images=frames,
#                 save_all=True, duration=1, loop=0)


#     def export_board(self):
#         pixels = []
#         for row in self.board:
#             r = []
#             for pixel in row:
#                 r.append(pixel.color)
                    
#             pixels.append(r)
        
#         array = np.array(pixels, dtype=np.uint8)

#         new_image = Image.fromarray(array)
#         return new_image





# def main():
#     rules, default = WFC_Ruleset.build_rules("data/Qud.png")

#     WFC_Ruleset.printrules(rules)
#     test_rules = WFC_Ruleset(rules)
#     test_board = WFC_Board(25,25,test_rules, default)
    

#     test_board.build_board()

# if __name__ == "__main__":
#     main()