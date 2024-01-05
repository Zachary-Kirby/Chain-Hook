from fileHandler import *
from mathFunctions import *
import levelObjects
import pygame as pg

class Level():
  def __init__(self):
    self.reloadInfo = []
    self.rect = [0,0,0,0]
    self.start = [32, 32]
    self.grids  = []
    self.gridW = 0
    self.gridH = 0
    self.metaGrid = []
    self.metaW = 0
    self.metaH = 0
    self.gridPixelW = 0 #changes dynamically
    self.gridPixelH = 0 #changes dynamically
    self.metaPixelW = 0 #changes dynamically
    self.metaPixelH = 0 #changes dynamically
    self.tileDefs = []
    self.tileAnimations = []
    #object data
    self.init_object_data()
    #self.objects  = []
    self.lights = []
    self.layers = 4 #tile layers
    self.tileAtlas = pg.Surface([0,0])
    self.darkAtlas = pg.Surface([0,0])
    self.tileAtlasSize = self.tileAtlas.get_size() #changes dynamically
    self.tileSize = 16
  def animate_tiles(self, frame):
    for animation in self.tileAnimations:
      if frame % animation[0]==0:
        frames = []
        for id in animation[1:]:
          frames += [self.tileDefs[id]]
        frames = [frames[-1]] + frames[:-1]
        for x in range(len(animation[1:])):
          self.tileDefs[animation[x+1]] = frames[x]
  def update_values(self):
    """
    when you change a variable that has dependencies call this so those variables are accurate
    """
    self.gridPixelW = self.gridW * self.tileSize
    self.gridPixelH = self.gridH * self.tileSize
    self.tileAtlasSize = self.tileAtlas.get_size()
    self.darkAtlas = self.tileAtlas.copy()
    self.darkAtlas.fill((64,64,64), special_flags=pg.BLEND_RGB_MULT)
    self.metaPixelW = self.gridPixelW * self.metaW
    self.metaPixelH = self.gridPixelH * self.metaH
  def load_objects(self):
    
    #place objects
    for object in self.objectData:
      topleft  = object[0]
      botright = object[1]
      type     = object[2]
      data     = object[3]
      group    = object[4]
      layer    = object[5]
      match type:
        case "player":
          self.checkpoint = round_to_topleft_of_tile(topleft[:], self.tileSize)
        case "armorer":
          if data == "0":
            self.bosses += [[type, levelObjects.armorer_boss(round_to_topleft_of_tile(topleft, self.tileSize))]]
        case "camera":
          self.camera_zones += [levelObjects.camera_zone(type, round_to_topleft_of_tile(topleft, self.tileSize), round_to_botright_of_tile(botright, self.tileSize))]
        case "flip":
          tile = self.get_tile(convert_to_tile_coords(topleft, self.tileSize), layer)
          self.collideables += [[type, levelObjects.Flip(topleft, self.tileSize, layer, tile)]]
        case "pressure_plate":
          self.collideables += [[type, levelObjects.pressure_plate(round_to_topleft_of_tile(topleft, self.tileSize), data)]]
        case "checkpoint":
          self.collideables += [[type, topleft]]
        case "redgem":
          self.pickups += [levelObjects.red_gem_bubble(round_to_topleft_of_tile(topleft, self.tileSize))]
        case "sign":
          self.signs += [levelObjects.sign(round_to_topleft_of_tile(topleft, self.tileSize), data)]
        case "door":
          self.interactables += [[type, levelObjects.door(round_to_topleft_of_tile(topleft[:],self.tileSize), round_to_topleft_of_tile(botright[:],self.tileSize))]]
        case "ladder":
          self.interactables += [[type, levelObjects.ladder(round_to_topleft_of_tile(topleft, self.tileSize), round_to_botright_of_tile(botright, self.tileSize), data)]]
        case "npc":
          self.npcs += [levelObjects.npc(round_to_topleft_of_tile(topleft[:],self.tileSize), data, type)]
        case "room":
          self.rooms += [levelObjects.room(round_to_topleft_of_tile(topleft, self.tileSize), round_to_botright_of_tile(botright, self.tileSize), data)]
        case "room_hide":
          if data not in self.roomHides.keys():
            self.roomHides[data] = []
          self.roomHides[data] += [round_to_topleft_of_tile(topleft, self.tileSize)+sub_pos(round_to_botright_of_tile(botright, self.tileSize), round_to_topleft_of_tile(topleft, self.tileSize))]
        case "sky":
          left = min(topleft[0], botright[0])
          top  = min(topleft[1], botright[1])
          width = abs(topleft[0]-botright[0])
          height = abs(topleft[1]-botright[1])
          self.sky_areas += [[left, top, width, height]]
        case "onoff":
          data = data.split(",")
          data = int(data[0]), int(data[1])
          self.onoffs += [levelObjects.onoff(round_to_topleft_of_tile(topleft, self.tileSize), data[0], data[1], layer)]
        case "pull_chain":
          data = data.split(",")
          self.pull_chains += [levelObjects.pull_chain(topleft, botright, int(data[0]), int(data[1]), data[2])]
        case _:#TODO
          if group not in self.action_groups.keys():
            self.action_groups[group] = []
          self.action_groups[group] += [[topleft, botright, type, data, layer]]
    
    #add extra data to placed objects
    for object in self.objectData:
      topleft  = object[0]
      botright = object[1]
      type     = object[2]
      data     = object[3]
      group    = object[4]
      layer    = object[5]
      match group:
        case "boss":
          if type == "armorer":
            if data == "1":
              for i in range(len(self.bosses)):
                if self.bosses[i][0] == "armorer":
                  break
              self.bosses[i][1].sword_points[0] = topleft
              self.bosses[i][1].sword_points[1] = botright
            if data == "3":
              for i in range(len(self.bosses)):
                if self.bosses[i][0] == "armorer":
                  break
              self.bosses[i][1].movement_point[0] = topleft
              self.bosses[i][1].movement_point[1] = botright
  def init_object_data(self):
    self.objectData = []
    self.interactables = []
    self.collideables = []
    self.entities = []
    self.npcs = []
    self.checkpoint = [0,0]
    self.checkpoints = []
    self.bosses = []
    self.pickups = []
    self.signs = []
    self.onoffs = []
    self.camera_zones = []
    self.action_groups = {}
    self.rooms = []
    self.roomHides = {}
    self.pull_chains = []
    self.sky_areas = []
  def reload(self):
    self.init_object_data()
    loadLevel(self, self.reloadInfo[0], self.tileAtlas, self.reloadInfo[1])
  def pixel_get_tile(self, ppos, layer = 4, out_of_bound_type = 0, empty_meta_tile_type = 0):
    """
    pos is in pixel units
    out of bounds is for if the tile is outside the map
    empty meta tile type is for if its in the bounds of the map but there is no chunk (group of tiles) there.
      a chunks size here is called self.grid_w and self.grid_h (width and height)
    """
    pos = convert_to_tile_coords(ppos, self.tileSize)
    
    meta_x = pos[0] // self.gridW
    meta_y = pos[1] // self.gridH
    if meta_x in range(0, self.metaW) and meta_y in range(0, self.metaH):
      grid_id = self.metaGrid[meta_x][meta_y]
      if grid_id!=-1:
        rel_x = pos[0] % self.gridW
        rel_y = pos[1] % self.gridH
        return self.grids[grid_id+layer][rel_x][rel_y]
      else:
        return empty_meta_tile_type
    else:
      return out_of_bound_type
  def get_tile(self, pos, layer = 4, out_of_bound_type = 0, empty_meta_tile_type = 0):
    """
    pos is in tile units
    out of bounds is for if the tile is outside the map
    empty meta tile type is for if its in the bounds of the map but there is no chunk (group of tiles) there.
      a chunks size here is called self.grid_w and self.grid_h (width and height)
    """
    meta_x = pos[0] // self.gridW
    meta_y = pos[1] // self.gridH
    if meta_x in range(0, self.metaW) and meta_y in range(0, self.metaH):
      grid_id = self.metaGrid[meta_x][meta_y]
      if grid_id!=-1:
        rel_x = pos[0] % self.gridW
        rel_y = pos[1] % self.gridH
        return self.grids[grid_id+layer][rel_x][rel_y]
      else:
        return empty_meta_tile_type
    else:
      return out_of_bound_type
  def pixel_place_tile(self, pixel_pos, type, layer = 0):
    pos = int(pixel_pos[0] // self.tileSize), int(pixel_pos[1] // self.tileSize)
    meta_x = pos[0] // self.gridW
    meta_y = pos[1] // self.gridH
    if meta_x in range(0, self.metaW) and meta_y in range(0, self.metaH):
      grid_id = self.metaGrid[meta_x][meta_y]
      if grid_id!=-1:
        rel_x = pos[0] % self.gridW
        rel_y = pos[1] % self.gridH
        self.grids[grid_id+layer][rel_x][rel_y] = type
  def draw(self, window, camera_float, layer, draw_dark = False):
    camera_int = [int(camera_float[0]),int(camera_float[1])]
    meta_top  = max(camera_int[1] // self.gridPixelH,0)
    meta_left = max(camera_int[0] // self.gridPixelW,0)
    meta_bot  = min((camera_int[1]+self.rect[3]) // self.gridPixelH+1, self.metaH)
    meta_right= min((camera_int[0]+self.rect[2]) // self.gridPixelW+1, self.metaW)
    
    if draw_dark:
      atlas=self.darkAtlas
    else:
      atlas=self.tileAtlas
    
    for meta_x in range(meta_left, meta_right):
      for meta_y in range(meta_top, meta_bot): #idk why I want to type this, but yes it goes from top to bottom.
        grid_id = self.metaGrid[meta_x][meta_y]
        
        if grid_id==-1:
          continue
        
        meta_pixel_top = meta_y * self.gridPixelH
        meta_pixel_left= meta_x * self.gridPixelW
        #what tile are the edges of the canvas touching
        #this is whatever tile pos it is relitive to the grid its in
        top   = (camera_int[1] // self.tileSize) - meta_y*self.gridH
        left  = (camera_int[0] // self.tileSize) - meta_x*self.gridW
        bot   = top  + self.rect[3] // self.tileSize
        right = left + self.rect[2] // self.tileSize
        
        top     = max(top, 0)
        left    = max(left, 0)
        bottom  = min(bot+2, self.gridH) #the plus one is so you don't see the tiles loading in due to rounding
        right   = min(right+2, self.gridW)
        
        grid = self.grids[grid_id+layer]
        for x in range(left, right):
          for y in range(top, bottom):
            tile_id = grid[x][y]
            if tile_id != 0:
              rect = self.tileDefs[tile_id]
              window.blit(atlas, [x*self.tileSize-camera_int[0]+self.rect[0]+meta_pixel_left, y*self.tileSize-camera_int[1]+self.rect[1]+meta_pixel_top], rect)
    window.set_clip()

def loadLevel(level, Window_dim_original, Tile_atlas, name):
  data = load(name)
  level.rect = [0,0] + Window_dim_original
  level.reloadInfo = [Window_dim_original, name]
  level.grids    = data["grids"]
  level.metaGrid = data["meta_grid"]
  level.gridW    = data["grid_w"]
  level.gridH    = data["grid_h"]
  level.metaW    = data["meta_w"]
  level.metaH    = data["meta_h"]
  level.tileAtlas = Tile_atlas
  level.tileAnimations = data["tile_animations"]
  level.tileDefs = data["tile_defs"]
  level.objectData = data["objects"]
  level.update_values()
  level.load_objects()


