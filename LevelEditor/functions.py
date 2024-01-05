from mathFunctions import *
import classes
from math import pi as PI
import pygame as pg
from textRenderer import *
from tileGridClass import TileGrid
from windowClass import Window, MouseEvent
from classes import *
from json import dumps

def getTileGridPos(pos , tileGrid : TileGrid):
  return convert_to_tile_coords(sub_pos(add_pos(pos, tileGrid.offset), tileGrid.rect), tileGrid.tileSize)

def textFieldInput(event : pg.event, allTextFields, selectedField):
  if selectedField != None:
    if event.key == pg.K_BACKSPACE:
      allTextFields[selectedField].text = allTextFields[selectedField].text[:-1]
    elif event.key == pg.K_RETURN:
      selectedField = None
    else:
      allTextFields[selectedField].text += event.unicode

def move_rect(rect, pos):
  return [rect[0]+pos[0], rect[1]+pos[1], rect[2], rect[3]]

def get_tile_rect(tile_id, tile_atlas_size, tile_size):
  w = (tile_atlas_size[0] // tile_size)
  return [tile_id % w * tile_size, tile_id // w * tile_size, tile_size, tile_size]

def create_tile_definitions(tile_size, tile_atlas_size):
  defs = []
  for y in range(tile_atlas_size[1] // tile_size):
    for x in range(tile_atlas_size[0] // tile_size):
      defs += [[x*tile_size, y*tile_size, tile_size, tile_size]]
  return defs

def tile_to_pixel(tile_coord, tile_size):
  return [tile_coord[0]*tile_size, tile_coord[1]*tile_size]

def animate_tile(tile_defs, animation, frame):
  """
  Warning the way I implemented this has a bug that if you have the same frame twice in a animation it will
  replace one of the other tile definitions with a copy of that frame
  
  1, 2, 3, 4, 3 -> 3, 1, 2, 3, 3 or something like that
  
  """
  
  #animations is framewait, frame1. frame2, framen... (by frame I mean index into the tile definitions)
  if frame % animation[0]==0:
    frames = []
    for id in animation[1:]:
      frames = frames + [tile_defs[id]]
    
    shifted = frames[1:] + [frames[0]]
    
    for i in range(len(frames)):
      #the bug is there becuase when it goes back its overwriting 
      #with something else its because I'm trying to have more than one def animate
      tile_defs[animation[i+1]] = shifted[i]
    
  
  return tile_defs

def get_hue(x):
  """
  x is between 0.0 and 1.0 the color repeats after that
  color order: red green blue
  """
  return (math.sin(2*PI*x+2*PI/4)*127+127, math.sin(2*PI*x+4*PI/3+2*PI/4)*127+127, math.sin(2*PI*x+2*math.pi/3+2*PI/4)*127+127)

def draw_rainbow(window, rect):
  for x in range(rect[2]):
    c = get_hue(x/rect[2])
    pg.draw.line(window, c, (rect[0]+x, rect[1]), (rect[0]+x, rect[1]+rect[3]))

def get_dist(pos1, pos2):
  w = pos1[0] - pos2[0]
  h = pos1[1] - pos2[1]
  return math.sqrt(w*w+h*h)

def in_radius(point, pos, radius):
  return get_dist(point, pos) <= radius

def lerp(a, b, t):
  return a + (b - a)*t

def HSV(hue, saturation, value):
  #hue goes from 0 to 360
  #saturation goes from 0 to 1
  #value goes from 0 to  1
  PI = math.pi
  TAU = math.tau
  x = hue / 360
  #hue of 0 is red. hue of 180 is light blue
  #saturation is a interpolation between color to max component for all
  #value is a interpolation between color to black
  step = TAU/3
  color = (math.cos(TAU*x)*127+127, math.cos(TAU*x+step)*127+127, math.cos(TAU*x+step*2)*127+127)
  maxValue = max(color)
  color = (
    lerp(maxValue, color[0], saturation),
    lerp(maxValue, color[1], saturation),
    lerp(maxValue, color[2], saturation))
  color = (
    lerp(0, color[0], value),
    lerp(0, color[1], value),
    lerp(0, color[2], value))
  return color

def floodFill(tileGrid : TileGrid, pos, layer, tile):
  print(pos)
  replaceTile = tileGrid.get_tile(pos, layer)
  tileQueue = [pos]
  tileCount = 0
  while len(tileQueue) > 0 and tileCount < 100*100:
    currentPos = tileQueue.pop(0)
    tileGrid.place_tile(currentPos, tile, layer)
    tileCount += 1
    
    adjacentPos = [currentPos[0]-1, currentPos[1]]
    if tileGrid.get_tile(adjacentPos, layer) == replaceTile:
      tileQueue += [adjacentPos]
    
    adjacentPos = [currentPos[0]+1, currentPos[1]]
    if tileGrid.get_tile(adjacentPos, layer) == replaceTile:
      tileQueue += [adjacentPos]
    
    adjacentPos = [currentPos[0], currentPos[1]-1]
    if tileGrid.get_tile(adjacentPos, layer) == replaceTile:
      tileQueue += [adjacentPos]
    
    adjacentPos = [currentPos[0], currentPos[1]+1]
    if tileGrid.get_tile(adjacentPos, layer) == replaceTile:
      tileQueue += [adjacentPos]

def placingAtEdgeScroll(mouseEvent : MouseEvent, tileGrid : TileGrid):
  relMousePos = [mouseEvent.pos[0] - tileGrid.rect[0], mouseEvent.pos[1] - tileGrid.rect[1]]
  if mouseEvent.pressed != [0,0,0]:
      if pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos):
        if relMousePos[0] < 16:
          tileGrid.offset[0]+=-4
        if relMousePos[1] < 16:
          tileGrid.offset[1]+=-4
        if relMousePos[0] > tileGrid.rect[2]-16:
          tileGrid.offset[0]+=4
        if relMousePos[1] > tileGrid.rect[3]-16:
          tileGrid.offset[1]+=4

def arrowKeyScrolling(tileGrid : TileGrid, keyButtons : windowClass.KeyButtons):
  if keyButtons.getPressed(pg.K_RIGHT):
      tileGrid.offset[0] += tileGrid.tileSize * 2
  if keyButtons.getPressed(pg.K_LEFT):
    tileGrid.offset[0] -= tileGrid.tileSize * 2
  if keyButtons.getPressed(pg.K_UP):
    tileGrid.offset[1] -= tileGrid.tileSize * 2
  if keyButtons.getPressed(pg.K_DOWN):
    tileGrid.offset[1] += tileGrid.tileSize * 2

def middleMouseScroll(mouseEvent : MouseEvent, tileGrid : TileGrid):
  if mouseEvent.pressed[1]:
      if pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos):
        tileGrid.offset[0] = max(tileGrid.offset[0] + mouseEvent.prePos[0] - mouseEvent.pos[0], 0)
        tileGrid.offset[1] = max(tileGrid.offset[1] + mouseEvent.prePos[1] - mouseEvent.pos[1], 0)
        tileGrid.offset[0] = min(tileGrid.offset[0], tileGrid.tileSize * tileGrid.gridW * tileGrid.metaW - tileGrid.rect[2])
        tileGrid.offset[1] = min(tileGrid.offset[1], tileGrid.tileSize * tileGrid.gridH * tileGrid.metaH - tileGrid.rect[3])

def mousePicking(mouseEvent : MouseEvent, tileGrid : TileGrid, selectedLayer, selectedTile):
  if not mouseEvent.risingEdge[0]:
    return selectedTile
  
  if pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos):
    rel = [mouseEvent.pos[0] - tileGrid.rect[0] + tileGrid.offset[0], mouseEvent.pos[1] - tileGrid.rect[1] + tileGrid.offset[1]]
    return tileGrid.get_tile((rel[0]//tileGrid.tileSize, rel[1]//tileGrid.tileSize), selectedLayer)
  
def mouseRangeFill(mouseEvent : MouseEvent, tileGrid : TileGrid, selectedTile, selectedLayer, clickStartPos):
  if pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos):
    placingType = selectedTile
    if (not mouseEvent.pressed[2] and mouseEvent.prePressed[2]):
      placingType = 0
    
    if (mouseEvent.pressed[0] and not mouseEvent.prePressed[0]) or \
       (mouseEvent.pressed[2] and not mouseEvent.prePressed[2]):
      clickStartPos = [mouseEvent.pos[0] - tileGrid.rect[0] + tileGrid.offset[0], mouseEvent.pos[1] - tileGrid.rect[1] + tileGrid.offset[1]]
    
    if (not mouseEvent.pressed[0] and mouseEvent.prePressed[0]) or \
       (not mouseEvent.pressed[2] and mouseEvent.prePressed[2]):
      clickEndPos = [mouseEvent.pos[0] - tileGrid.rect[0] + tileGrid.offset[0], mouseEvent.pos[1] - tileGrid.rect[1] + tileGrid.offset[1]]
      
      l=min(clickStartPos[0], clickEndPos[0])//tileGrid.tileSize
      t=min(clickStartPos[1], clickEndPos[1])//tileGrid.tileSize
      r=max(clickStartPos[0], clickEndPos[0])//tileGrid.tileSize+1
      b=max(clickStartPos[1], clickEndPos[1])//tileGrid.tileSize+1
      print(l, t, r, b)
      for x in range(l, r):
        for y in range(t, b):
          tileGrid.place_tile((x,y), placingType, selectedLayer)
  return clickStartPos

def textFieldSelect(mouseEvent, allTextFields, selectedField):
  if mouseEvent.pressed[0] and not mouseEvent.prePressed[0]:
    selectedField = None
    for text_field_id in range(len(allTextFields)):
      text_field = allTextFields[text_field_id]
      if pg.Rect(text_field.rect).collidepoint(mouseEvent.pos):
        selectedField = text_field_id 
  return selectedField

def mousePlaceTile(mouseEvent : MouseEvent, rel, selectedTile, selectedLayer, tileGrid : TileGrid):
  rel[0] //= tileGrid.tileSize
  rel[1] //= tileGrid.tileSize
  tileGrid.place_tile(rel, selectedTile, selectedLayer)

def removeObject(pos, objects):
  for object in objects:
    object_topleft = object[0]
    object_botright = object[1]
    if get_dist(pos, object_topleft) <= 4 or get_dist(pos, object_botright) <= 4:
      objects.remove(object)

def drawInTileGrid(window : Window, tileGrid : TileGrid, tileDefs, mouseEvent : MouseEvent, showCameraArea):
  window.window.set_clip(tileGrid.rect)
  for y in range(window.dim[1]):
      backColor = HSV(
        lerp(140, 160, y/window.dim[1]), 
        lerp(1, 0.7, y/window.dim[1]), 
        1)#lerp(0.3, 1,1-(1-y/window.dim[1])**5))
      window.window.fill(backColor, [0, y, window.dim[0], 1])
  tileGrid.draw(window.window, tileDefs, 1)
  
  if showCameraArea:
    cameraDim = (640,360)
    pg.draw.rect(window.window, (255, 255, 255), [mouseEvent.pos[0]-cameraDim[0]/2, mouseEvent.pos[1]-cameraDim[1]/2, cameraDim[0], cameraDim[1]], 1)
  
  window.window.set_clip()

def drawTextInfo(window : Window, font : pg.font.Font, selectedLayer, tileGrid, mouseEvent, Tool, offset: Vector2):
  window.window.blit(font.render("layer:"+str(selectedLayer), 0, (255,255,255)), [0+offset.x, 64*window.scale+offset.y])
  mouse_tile_pos = (mouseEvent.pos[0]+tileGrid.offset[0]-tileGrid.rect[0]) // tileGrid.tileSize, (mouseEvent.pos[1]+tileGrid.offset[1]-tileGrid.rect[1]) // tileGrid.tileSize
  window.window.blit(font.render("tile_id:"+str(tileGrid.get_tile(mouse_tile_pos, selectedLayer)), 0, (255,255,255)), [0+offset.x, (64+8)*window.scale+offset.y])
  window.window.blit(font.render("tool: "+Tool, 0, (255,255,255)), [0+offset.x, (115+48)*window.scale+offset.y])

def drawTextFields(window, allTextFields, smallFont, offset: Vector2):
  for text_field in allTextFields:
    if text_field.text != "":
      draw_text(window.window, smallFont, text_field.rect, text_field.text)
    pg.draw.rect(window.window, (255,255,255), pg.Rect(text_field.rect).move(offset.x, offset.y), 1)

def drawTIG(window : Window, allTextFields, font : pg.font.Font, offset: Vector2):
  for field_id in range(len(allTextFields)):
    field = allTextFields[field_id]
    text = "tig"[field_id]
    size = font.size(text)
    window.window.blit(font.render(text, 0, (255,255,255)), [8-size[0]/2+offset.x, field.rect[1]+offset.y])

def drawObjects(window : Window, tileGrid : TileGrid, objectSystem : ObjectSystem, mouseEvent : MouseEvent, font : pg.font.Font):
  window.window.set_clip(tileGrid.rect)
  if objectSystem.visible:
    for object in objectSystem.objects:
      object_topleft  = sub_pos(add_pos(object[0],tileGrid.rect),tileGrid.offset)
      object_botright = sub_pos(add_pos(object[1],tileGrid.rect),tileGrid.offset)
      pg.draw.circle(window.window, (0, 0, 255), object_topleft,  2)
      pg.draw.circle(window.window, (255, 0, 0), object_botright, 2)
      
      if get_dist(object_topleft, mouseEvent.pos) <= 2:
        drawObjectTextDescription(window, object_topleft, font, object)
      elif get_dist(object_botright, mouseEvent.pos) <= 2:
        drawObjectTextDescription(window, object_botright, font, object)

def drawObjectTextDescription(window : Window, object_topleft, font : pg.font.Font, object):
  surface = font.render(str(object), 0, (128,255,128))
  rect = surface.get_rect()
  rect.topleft = object_topleft
  if rect.right > window.dimOriginal[0]:
    rect.right = window.dimOriginal[0]
  window.window.blit(surface, rect)

def toggleLayer(tileGrid : TileGrid, layer):
  if layer in tileGrid.enabledLayers:
    tileGrid.enabledLayers.remove(layer)
  else:
    tileGrid.enabledLayers += [layer]
    tileGrid.enabledLayers.sort()

def layerToggles(event: pg.event, tileGrid: TileGrid):
  if event.key == pg.K_0:
    toggleLayer(tileGrid, 0)
  if event.key == pg.K_1:
    toggleLayer(tileGrid, 1)
  if event.key == pg.K_2:
    toggleLayer(tileGrid, 2)
  if event.key == pg.K_3:
    toggleLayer(tileGrid, 3)
  if event.key == pg.K_4:
    toggleLayer(tileGrid, 4)

def saveLevel(levelFile, tileGrid: TileGrid, tileAnimations, originalTileDefs, objectSystem : ObjectSystem, collision_assignments: dict):
  Level = {}
  Level["grids"]            = tileGrid.grids
  Level["meta_grid"]        = tileGrid.meta_grid
  Level["grid_w"]           = tileGrid.gridW
  Level["grid_h"]           = tileGrid.gridH
  Level["meta_w"]           = tileGrid.metaW
  Level["meta_h"]           = tileGrid.metaH
  Level["tile_animations"]  = tileAnimations
  Level["tile_defs"]        = originalTileDefs
  Level["objects"]          = objectSystem.objects
  Level["editor_camera"]    = tileGrid.offset
  text = dumps(Level)
  with open(levelFile, "w") as txt:
    txt.write(text)
  
  text = dumps(collision_assignments)
  with open("collision_assignments.json", "w") as txt:
    txt.write(text)
