from __future__ import annotations

import tcod
import numpy as np
from PIL import Image


from enum import Enum, auto
from typing import Optional, Tuple, TYPE_CHECKING
import copy
import random

directions = (
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0)
)

def totuple(a):
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a
    
def reverse_direction(direction_tuple: tuple):
    x, y = direction_tuple
    return (-x, -y)

#Stores the data about which possible tiles an entropic tile can be
class WFC_TileOptions():
    def __init__(self, tile_options: list[tuple] = [], tile_weights: list[tuple] = []) -> None:
        self.tile_options: list[tuple] = tile_options
        self.tile_weights: list[float] = tile_weights

    #Equivalence function. Will return true if two TileOptions have the same options and weights,
    #regardless of their internal order in their lists
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, WFC_TileOptions): 
            return False
        
        for i, self_o in enumerate(self.tile_options):
            flag = False
            for j, other_o in enumerate(value.tile_options):
                if self_o == other_o:
                    if self.tile_weights[i] == value.tile_weights[j]:
                        flag = True
                    else:
                        return False
            if not flag:
                return False
        return True
                    
    def add(self, option: tuple, weight: float = 1):
        if option in self.tile_options:
            self.tile_weights[self.tile_options.index(option)] += weight
        else:
            self.tile_options.append(option)
            self.tile_weights.append(weight)
    
    def combine(self, other_options: WFC_TileOptions):
        for i, option in enumerate(other_options.tile_options):
            if option in self.tile_options:
                self.tile_weights[self.tile_options.index(option)] += other_options.tile_weights[i]
            else:
                self.tile_options.append(option)
                self.tile_weights.append(other_options.tile_weights[i])

    def restrict(self, other_options: WFC_TileOptions):
        new_options = []
        new_weights = []
        for other_option in other_options.tile_options:
            if other_option in self.tile_options:
                new_options.append(other_option)
                new_weights.append(self.tile_weights[self.tile_options.index(other_option)] + other_options.tile_weights[other_options.tile_options.index(other_option)])
        
        self.tile_options = new_options
        self.tile_weights = new_weights
    
    def printme(self):
        print("----------------")
        print(self.tile_options)
        print(self.tile_weights)
        print("----------------")


           

        

class WFC_RuleData():
    def __init__(self, direction: tuple, tile_type: tuple, count: int = 1) -> None:
        self.direction = direction
        self.tile_type = tile_type
        self.count = count

class WFC_Ruleset():
    def __init__(self, rules: dict[tuple, list[WFC_RuleData]]) -> None:
        self.rules = rules

    @staticmethod
    def printrules(rules: dict[tuple, list[WFC_RuleData]]):
        for key in rules.keys():
            print(f"Rules for {key}:")
            for direction in directions:
                print(f"Direction: {direction}")
                for rule in rules[key]:
                    if rule.direction == direction:
                        print(f"{rule.tile_type} : {rule.count}")


    @staticmethod 
    def build_rules(training_image_path: str) -> tuple[dict[tuple, list[WFC_RuleData]], dict[tuple, int]]:
        training_image = Image.open(training_image_path).convert('RGB')
        rules: dict[tuple, list[WFC_RuleData]] = {}
        default_options = WFC_TileOptions([],[])
        
        width, height = training_image.size
        pixels = np.asarray(training_image)
        
        for y, row in enumerate(pixels):
            for x, pixel in enumerate(row):
                pixel_t = totuple(pixel)

                #Count this pixel for the default option
                default_options.add(pixel_t)

                for direction in directions:
                    
                    d_x, d_y = direction
                   
                    if x + d_x < 0 or y + d_y < 0:
                        continue
                    elif x + d_x >= width or y + d_y >= height:
                        continue 

                    other_tile = totuple(pixels[y+d_y][x+d_x])

                    if pixel_t in rules:
                       
                        current_rules = rules[pixel_t]
                        flag = True
                        for rule in current_rules:
                            if rule.tile_type == other_tile and rule.direction == direction:
                                flag = False
                                rule.count += 1
                        if flag:
                            current_rules.append(WFC_RuleData(direction, other_tile))
                            
                    else:
                        rules[pixel_t] = [WFC_RuleData(direction, other_tile)]
        return (rules, default_options)

    @staticmethod
    def get_options(ruleset: WFC_Ruleset, tile_type: tuple, direction: tuple) -> WFC_TileOptions:
        tile_rules = ruleset.rules[tile_type]
        options = []
        weights = []
        for rule in tile_rules:
            if direction == rule.direction:
                options.append(rule.tile_type)
                weights.append(rule.count)

        return WFC_TileOptions(options, weights)







class WFC_Tile():
    def __init__(self, parent: WFC_Board, x: int, y: int, ruleset: WFC_Ruleset, options: WFC_TileOptions, tile_type: Optional[tuple] = None) -> None:
        self.parent = parent
        self.x = x
        self.y = y
        self.ruleset = ruleset
        self.tile_type = tile_type
        self.options = copy.deepcopy(options)
        self.default_options = copy.deepcopy(options)
        self.valid = True

    @property
    def entropy(self) -> float:
        if self.tile_type:
            return 0
        else:
            return len(self.options.tile_options) / len(list(self.default_options.tile_options)) 

    @property
    def color(self):
        if self.tile_type:
            return self.tile_type
        
        tr, tg, tb = 0, 0, 0
        for i, color in enumerate(self.options.tile_options):
            r, g, b = color
            r = int(r)
            g = int(g)
            b = int(b)
            r *= self.options.tile_weights[i]
            g *= self.options.tile_weights[i]
            b *= self.options.tile_weights[i]
            tr += r
            tg += g
            tb += b
        
        tr //= sum(self.options.tile_weights)
        tg //= sum(self.options.tile_weights)
        tb //= sum(self.options.tile_weights)

        return (tr, tg, tb)

    def build_options(self):
        new_options = None
        for direction in directions:
            d_x, d_y = direction
                
            if self.x + d_x < 0 or self.y + d_y < 0:
                continue
            elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
                continue
                
            neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
            neighbor.options.printme()
            if neighbor.entropy == 1:
                continue
            neighbor_contribution = WFC_TileOptions([], [])
            for option in neighbor.options.tile_options:
                neighbor_contribution.combine(WFC_Ruleset.get_options(self.ruleset, option, reverse_direction(direction)))
            

            if new_options == None:
                new_options = neighbor_contribution
            else:
                new_options.restrict(neighbor_contribution)

        return new_options





        


        

    def validate(self) -> None:
        if self.tile_type:
            return
        
        new_options = self.build_options()
        if self.options == new_options:
            return
        else:
            self.options = new_options
        
        for direction in directions:
            d_x, d_y = direction
                
            if self.x + d_x < 0 or self.y + d_y < 0:
                continue
            elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
                continue

            neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
            if neighbor.entropy > 0:
                self.parent.queue_validation(neighbor)
              
        



        

    def collapse(self) -> None:
        
        choice = random.choices(self.options.tile_options, self.options.tile_weights)
        self.tile_type = choice[0]
        self.options = WFC_TileOptions([choice[0]], [1])

        #invalidate neigbors
        for direction in directions:
            d_x, d_y = direction
                
            if self.x + d_x < 0 or self.y + d_y < 0:
                continue
            elif self.x + d_x >= self.parent.width or self.y + d_y >= self.parent.height:
                continue 

            neighbor = self.parent.tile_at(self.x + d_x, self.y + d_y)
            if neighbor.entropy > 0:
                self.parent.queue_validation(neighbor)
            
            
        





            




class WFC_Board():
    def __init__(self, width, height, ruleset, default_options) -> None:
        self.width = width
        self.height = height
        self.ruleset = ruleset
        self.validation_queue = []
        self.board: list[list[WFC_Tile]]= []

        for y in range(height):
            row = []
            for x in range(width):
                row.append(WFC_Tile(self, x, y, copy.deepcopy(ruleset), default_options))
            self.board.append(row)
                

    def tile_at(self, x, y) -> WFC_Tile:
        return self.board[y][x]
    
    def collapse_tile(self, x, y) -> None:
        self.board[y][x].collapse()

    @property
    def total_entropy(self) -> float:
        total = 0
        for row in self.board:
            for tile in row:
                assert(isinstance(tile, WFC_Tile))
                total += tile.entropy
        return total

    @property
    def is_valid(self) -> bool:
        return len(self.validation_queue) == 0
    
    def get_next_invalid_tile(self) -> Optional[WFC_Tile]:
        if self.is_valid:
            return None
        return self.validation_queue.pop(0)

    def queue_validation(self, tile: WFC_Tile) -> None:
        if tile in self.validation_queue:
            return
        self.validation_queue.append(tile)

    def get_lowest_entropy_tiles(self) -> list[WFC_Tile]:
        if self.total_entropy == 0:
            return []
        
        lowest_tiles = []
        lowest_entropy = 1

        for row in self.board:
            for tile in row:
                assert(isinstance(tile, WFC_Tile))
                if tile.entropy == 0:
                    continue
                if tile.entropy == lowest_entropy:
                    lowest_tiles.append(tile)
                elif tile.entropy < lowest_entropy:
                    lowest_entropy = tile.entropy
                    lowest_tiles = [tile]
        return lowest_tiles


    def build_board(self):
        images = []
        while self.total_entropy > 0:
            while(not self.is_valid):
                tile = self.get_next_invalid_tile()
                tile.validate()
            choice = random.choice(self.get_lowest_entropy_tiles())
            choice.collapse()
            images.append(self.export_board())
        self.make_gif(images)

    def make_gif(self, frames):
        frame_one = frames[0]
        frame_one.save("test.gif", format="GIF", append_images=frames,
                save_all=True, duration=1, loop=0)


    def export_board(self):
        pixels = []
        for row in self.board:
            r = []
            for pixel in row:
                r.append(pixel.color)
                    
            pixels.append(r)
        
        array = np.array(pixels, dtype=np.uint8)

        new_image = Image.fromarray(array)
        return new_image





def main():
    rules, default = WFC_Ruleset.build_rules("data/Qud.png")

    WFC_Ruleset.printrules(rules)
    test_rules = WFC_Ruleset(rules)
    test_board = WFC_Board(25,25,test_rules, default)
    

    test_board.build_board()
    test_board.export_board()

if __name__ == "__main__":
    main()