import pygame as pg
import json
import os
import tileFunctions
import classes

class TileGrid():
  Collison_layer = 4
  Object_layer = 6
  def __init__(self, rect, tileAtlas : pg.Surface, tileSize, collision_atlas):
    self.rect = rect
    self.offset = [0,0]
    self.metaW = 32
    self.metaH = 32
    
    #idk if a quad tree would be better \('/')/
    self.meta_grid = create_grid(self.metaW, self.metaH, -1)
    self.gridW = 16
    self.gridH = 16
    self.grid_layers = 7
    self.object_layers = 1
    self.grids = []
    self.drawn_grids = []
    self.meta_tile_pixel_w = tileSize * self.gridW
    self.meta_tile_pixel_h = tileSize * self.gridH
    self.enabledLayers = [0, 1, 2, 3, 4, 5]
    
    self.tile_atlas = tileAtlas
    self.tile_dark_atlas = tileAtlas.copy()
    self.tile_dark_atlas.fill((128,128,128), special_flags=pg.BLEND_RGB_MULT)
    self.atlas = None
    self.tile_atlas_size = tileAtlas.get_size()
    self.tileSize = tileSize
    self.collision_atlas = collision_atlas
    self.collision_atlas.set_colorkey((0,0,0))
    
  def create_grid(self, meta_x, meta_y):
    self.meta_grid[meta_x][meta_y] = len(self.grids)
    for z in range(self.grid_layers):
      self.grids += [create_grid(self.gridW, self.gridH)]
    #TODO OBJECTS
    self.grids += []
  def place_tile(self, tile_pos, id, layer = 0):
    meta_x = tile_pos[0] // self.gridW
    meta_y = tile_pos[1] // self.gridH
    rel_tile_x = tile_pos[0] % self.gridW
    rel_tile_y = tile_pos[1] % self.gridH
    if meta_x in range(0, self.metaW) and meta_y in range(0, self.metaH):
      grid_id = self.meta_grid[meta_x][meta_y]
      if grid_id == -1:
        grid_id = len(self.grids)
        self.create_grid(meta_x, meta_y)
      
      self.grids[grid_id+layer][rel_tile_x][rel_tile_y] = id
  def get_tile(self, tile_pos, layer = 0):
    meta_x = tile_pos[0] // self.gridW
    meta_y = tile_pos[1] // self.gridH
    rel_tile_x = tile_pos[0] % self.gridW
    rel_tile_y = tile_pos[1] % self.gridH
    if meta_x not in range(0, self.metaW) or meta_y not in range(0, self.metaH):
      return 0
    grid_id = self.meta_grid[meta_x][meta_y]
    if grid_id == -1:
      return 0
    return self.grids[grid_id+layer][rel_tile_x][rel_tile_y]
  def draw_tile(self, window, tile_id, pos, rect):
    window.blit(self.atlas, pos, rect)
  def draw_collision(self, window, tile_id, pos, rect):
    window.blit(self.collision_atlas, pos, tileFunctions.get_collision_clip(self.tileSize, tile_id, self.collision_atlas))
  def draw(self, window, tile_defs, selected_layer = 0):
    """
    get the meta grid bounds
    loop through the meta tiles
      get the chunk bounds
      loop through the chunk tiles
        draw them
    
    the reason to do it this way is becuase the alternative for looping through a meta grid like this (the only other solution I know) uses lots of checks
    
    I was inspired by how rasterizing a triange works
    also I've done this before in my other project crimson crawler
    """
    self.drawn_grids = []
    window.set_clip(self.rect)
    meta_top  =max(self.offset[1] // self.meta_tile_pixel_h,0)
    meta_left =max(self.offset[0] // self.meta_tile_pixel_w,0)
    meta_bot  =min((self.offset[1]+self.rect[3]) // self.meta_tile_pixel_h+1, self.metaH)
    meta_right=min((self.offset[0]+self.rect[2]) // self.meta_tile_pixel_w+1, self.metaW)
    for z in self.enabledLayers:
      if z >= selected_layer:
        self.atlas = self.tile_atlas
      else:
        self.atlas = self.tile_dark_atlas
      if z in range(0, 4):
        draw_routine = self.draw_tile
      elif z == self.Collison_layer:
        draw_routine = self.draw_collision
      else:
        continue
      for meta_x in range(meta_left, meta_right):
        for meta_y in range(meta_top, meta_bot): #idk why I want to type this, but yes it goes from top to bottom.
          grid_id = self.meta_grid[meta_x][meta_y]
          
          if grid_id==-1:
            continue
          
          self.drawn_grids += [grid_id]
          
          meta_pixel_top = meta_y * self.meta_tile_pixel_h
          meta_pixel_left= meta_x * self.meta_tile_pixel_w
          #what tile are the edges of the canvas touching
          #this is whatever tile pos it is relitive to the grid its in
          top   = (self.offset[1] // self.tileSize) - meta_y*self.gridH
          left  = (self.offset[0] // self.tileSize) - meta_x*self.gridW
          bot   = top  + self.rect[3] // self.tileSize
          right = left + self.rect[2] // self.tileSize
          
          top     = max(top, 0)
          left    = max(left, 0)
          bottom  = min(bot+1, self.gridH) #the plus one is so you don't see the tiles loading in due to rounding
          right   = min(right+1, self.gridW)
          
          grid = self.grids[grid_id+z]
          for x in range(left, right):
            for y in range(top, bottom):
              tile_id = grid[x][y]
              if tile_id != 0:
                rect = tile_defs[tile_id]
                pos = [x*self.tileSize-self.offset[0]+self.rect[0]+meta_pixel_left, y*self.tileSize-self.offset[1]+self.rect[1]+meta_pixel_top]
                draw_routine(window, tile_id, pos, rect)
    window.set_clip()
  def load(self, levelFile, objectSystem: classes.ObjectSystem):
    if os.path.exists(levelFile):
      with open(levelFile, "r") as lvl:
        text = lvl.read()
        level = json.loads(text)
        self.grids     =  level["grids"]    
        self.meta_grid =  level["meta_grid"]
        self.gridW    =  level["grid_w"]   
        self.gridH    =  level["grid_h"]   
        self.metaW    =  level["meta_w"]   
        self.metaH    =  level["meta_h"]
        objectSystem.objects =  level["objects"]
        self.offset    =  level["editor_camera"]

def create_grid(w, h, defualt_id = 0):
  return [[defualt_id for n in range(h)] for n in range(w)]

