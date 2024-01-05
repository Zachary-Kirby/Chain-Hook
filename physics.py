import levelClass
from mathFunctions import *
from rectFunctions import *

class COLLISION_TYPES:
  AIR = 0
  WATER = 7
  DEADLY = [6, 8, 9, 10, 11]
  NOT_HOOKSHOTABLE = [AIR, WATER, 2] + DEADLY
  BREAKS_HOOKSHOT = [12]
  SLOPES = [32, 33]
  LEFT_UP_SLOPE = 33
  RIGHT_UP_SLOPE = 32

class COLLISION_RECTS:
  tile_size = 16
  collision_tile_colors = [(0,0,0), (255,255,255), (255,255,255), (255,255,255), (255,255,255), (255,255,255), (255, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 255)]
  collision_rects = [[0,0,0,0], [0,0,tile_size, tile_size], [0,0,tile_size,1], [0,tile_size-1,tile_size,1], [0, 0, 1, tile_size], [tile_size-1, 0, 1, tile_size], [0,0,tile_size, tile_size], [0,0,tile_size, tile_size], [0, 0, tile_size, tile_size/2], [0, tile_size/2, tile_size, tile_size/2], [0, 0, tile_size/2, tile_size], [tile_size/2, 0, tile_size/2, tile_size], [0, 0, tile_size, tile_size]]
  slopes = {32:[0,15, 15, 0],33:[0,-1,15,15]}

def getTileRect(tile_id, tile_atlas_size, tile_size = 16):
  w = (tile_atlas_size[0] // tile_size)
  return [tile_id % w * tile_size, tile_id // w * tile_size, tile_size, tile_size]

def getTileCollision(topleft, botright, level : levelClass.Level, padding = 2, layer = 4, no_collision = [0]):
  topleft = topleft[0] - padding, topleft[1] - padding
  botright = botright[0] + padding, botright[1] + padding
  
  meta_top   = max(topleft[1] // level.gridH, 0)
  meta_left  = max(topleft[0] // level.gridW, 0)
  meta_bot   = min(botright[1] // level.gridH, level.metaH-1)
  meta_right = min(botright[0] // level.gridW, level.metaW-1)
  rects = []
  for meta_x in range(meta_left, meta_right+1):
    for meta_y in range(meta_top, meta_bot+1):
      
      grid_id = level.metaGrid[meta_x][meta_y]
      if grid_id == -1:
        continue
      meta_pixel_x = meta_x * level.gridPixelW
      meta_pixel_y = meta_y * level.gridPixelH
      
      top  = max(topleft[1] - meta_y * level.gridH, 0)
      left = max(topleft[0] - meta_x * level.gridW, 0)
      bot  = min(botright[1] - meta_y * level.gridH, level.gridH)
      right= min(botright[0] - meta_x * level.gridW, level.gridW)
      
      for x in range(left, right):
        for y in range(top, bot):
          tile = level.grids[grid_id+layer][x][y]
          if tile not in no_collision:
            rect = [x*level.tileSize+meta_pixel_x, y*level.tileSize+meta_pixel_y, level.tileSize, level.tileSize, tile]
            if tile < len(COLLISION_RECTS.collision_rects):
              rect[0] += COLLISION_RECTS.collision_rects[tile][0]
              rect[1] += COLLISION_RECTS.collision_rects[tile][1]
              rect[2]  = COLLISION_RECTS.collision_rects[tile][2]
              rect[3]  = COLLISION_RECTS.collision_rects[tile][3]
            else:
              rect[0] += COLLISION_RECTS.collision_rects[1][0]
              rect[1] += COLLISION_RECTS.collision_rects[1][1]
              rect[2]  = COLLISION_RECTS.collision_rects[1][2]
              rect[3]  = COLLISION_RECTS.collision_rects[1][3]
            rects += [rect]
  
  return rects

def physicsMove(rect, pre_rect, collison_rects, axis, level : levelClass.Level, output_collision_type = False):
  
  collision_types = []
  normal = [0, 0]
  for col in collison_rects:
    if collide_rects(col, rect):
      #wall top, bot, left, right
      if col[4] > len(COLLISION_RECTS.collision_rects):
        if axis == "y":
          x = rect_centerx(rect)
          y = rect_bot(rect)
          if x >= col[0] and x <= col[0]+col[2]:
            slope = COLLISION_RECTS.slopes[col[4]].copy()
            slope[0] += col[0]
            slope[1] += col[1]
            slope[2] += col[0]
            slope[3] += col[1]
            floor_y = cast_down(slope, x)
            if y >= floor_y:
              rect[1] = floor_y - rect[3]
              normal = normalize([slope[3] - slope[1], slope[0] - slope[2]])  
      else:
        if col[4] == 12: col[4] = 1
        if col[4] in range(6): #only deal with hitting walls. Otherwise 
          enabled_cols = [[0,0,0,0], [1,1,1,1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]][col[4]] #select the collidable directions based on what the collision type is
          if axis == 'y':
            if rect_bot(rect) >= rect_top(col) and rect_bot(pre_rect) <= rect_top(col) and enabled_cols[0]:
              #going down
              normal = [0, -1]
              rect[1] = rect_top(col) - rect[3]
            elif rect_top(rect) <= rect_bot(col) and rect_top(pre_rect) >= rect_bot(col) and enabled_cols[1]:
              #going up
              normal = [0, 1]
              rect[1] = rect_bot(col)
          elif axis == 'x':
            if rect_right(rect) >= rect_left(col) and rect_right(pre_rect) <= rect_left(col) and enabled_cols[2]:
              #going right
              if level.get_tile(convert_to_tile_coords((col[0]-1, col[1]))) != COLLISION_TYPES.RIGHT_UP_SLOPE:
                normal = [-1, 0]
                rect[0] = rect_left(col) - rect[2]
              else:
                normal = [0, -1]
                rect[1] = rect_top(col) - rect[3]
              
            elif rect_left(rect) <= rect_right(col) and rect_left(pre_rect) >= rect_right(col) and enabled_cols[3]:
              #going left
              if level.get_tile(convert_to_tile_coords((col[0]+16, col[1]))) != COLLISION_TYPES.LEFT_UP_SLOPE:
                normal = [1, 0]
                rect[0] = rect_right(col)
              else:
                normal = [0, -1]
                rect[1] = rect_top(col) - rect[3]
              
        else:
          collision_types += [col[4]]
  if output_collision_type:
    return normal, collision_types #makes this code a little messy, but the alternitive is repetitive.
  else:
    return normal

def stopVel(normal, vel, axis):
  if normal!=[0,0]:
    if axis=='x':
      dot = normal[0] * vel[0] + normal[1] * vel[1]
      bounce = 1
      if abs(dot) > 4:
        bounce = 1.5
      vel[0] -= normal[0] * dot * bounce
      vel[1] -= normal[1] * dot * bounce
    if axis=='y':
      dot = normal[0] * vel[0] + normal[1] * vel[1]
      #bouncing code for the vertical axis
      #bounce = 1
      #if abs(dot) > 8:
        #bounce = 1.5
        #vel[0] -= normal[0] * dot * bounce
      vel[1] -= normal[1] * dot #* bounce
      
  return vel
