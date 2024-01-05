import pygame as pg
from tileFunctions import *
import windowClass

class tile_select():
  
  def __init__(self, rect, tile_atlas : pg.Surface, tile_size, collision_atlas):
    self.rect = rect
    self.tile_atlas = tile_atlas
    self.tileAtlasSize = tile_atlas.get_size()
    self.tileSize = tile_size
    self.tile_atlas_tile_size = self.tileAtlasSize[0] // tile_size, self.tileAtlasSize[1] // tile_size
    self.offset = [0,0]
    self.mode = "tile" #modes: tile, collision
    self.collisionAtlas = collision_atlas
    self.enabled = False
  def opening(self, keyButtons : windowClass.KeyButtons, mouseEvent : windowClass.MouseEvent):
    if keyButtons.getPressedRisingEdge(pg.K_TAB):
      self.enabled = True
      self.rect[0] = mouseEvent.pos[0] - self.rect[2]/2
      self.rect[1] = mouseEvent.pos[1] - self.rect[3]/2
  def closing(self, keyButtons, mouseEvent : windowClass.MouseEvent):
    if keyButtons.getPressedFallingEdge(pg.K_TAB):
      self.enabled = False
      
  def draw(self, window : windowClass.Window, mouseEvent, tileSize):
    if self.enabled == False:
      return
    
    window.window.fill((64,0,64), self.rect)
    #draw the tiles
    if self.mode == "tile":
      for y in range(self.offset[1], self.offset[1]+self.rect[3], self.tileSize):
        for x in range(self.offset[0], self.offset[0]+self.rect[2], self.tileSize):
          window.window.blit(self.tile_atlas, [x+self.rect[0]-self.offset[0],y+self.rect[1]-self.offset[1]], [x,y,self.tileSize,self.tileSize]) 
    elif self.mode == "collision":
      for y in range(self.offset[1] // self.tileSize, (self.offset[1]+self.rect[3]) // self.tileSize):
        for x in range(self.offset[0] // self.tileSize, (self.offset[0]+self.rect[2]) // self.tileSize):
          tile_id = x + y*(self.collisionAtlas.get_width()//self.tileSize)
          pos = [x*self.tileSize+self.rect[0]-self.offset[0],y*self.tileSize+self.rect[1]-self.offset[1]]
          window.window.blit(self.collisionAtlas, pos, get_collision_clip(self.tileSize, tile_id, self.collisionAtlas))
    #draw the white square ontop of the selected tile
    if pg.Rect(self.rect).collidepoint(mouseEvent.pos):
      window.window.set_clip(self.rect)
      
      pos = mouseEvent.pos
      rel_pos = [0, 0]
      rel_pos[0] = ((pos[0] - self.rect[0] + self.offset[0] % tileSize)//tileSize)*tileSize - self.offset[0] % tileSize + self.rect[0]
      rel_pos[1] = ((pos[1] - self.rect[1] + self.offset[1] % tileSize)//tileSize)*tileSize - self.offset[1] % tileSize + self.rect[1]
      pg.draw.rect(window.window, (255,255,255), rel_pos+[tileSize, tileSize], 1)
      window.window.set_clip()
  
  def mouseInput(self, mouseEvent : windowClass.MouseEvent, selectedTile):
    if not self.enabled:
      return selectedTile
    
    self.offset[0] = max(self.offset[0] + (mouseEvent.prePos[0] - mouseEvent.pos[0])*-4, 0)
    self.offset[1] = max(self.offset[1] + (mouseEvent.prePos[1] - mouseEvent.pos[1])*-4, 0)
    relPos = mouseEvent.pos[0] - self.rect[0] + self.offset[0], mouseEvent.pos[1] - self.rect[1] + self.offset[1]
    tilePos = relPos[0] // self.tileSize, relPos[1] // self.tileSize
    if self.mode == "tile":
      tile_id = int(tilePos[0] + tilePos[1] * self.tileAtlasSize[0] // self.tileSize)
    if self.mode == "collision":
      tile_id = int(tilePos[0] + tilePos[1] * (self.collisionAtlas.get_width() // self.tileSize))
    return tile_id

class ctext_field():
  def __init__(self, rect):
    self.text = ""
    self.rect = rect
    self.offset = [0,0]

class ObjectSystem():
  def __init__(self, window):
    self.objects = []
    self.visible = True
    self.point1 = (0,0)
    self.point2 = (0,0)
    self.idField              = ctext_field([int(16*window.scale), int(0), int(48*window.scale), int(16*window.scale)])
    self.storedField          = ctext_field([int(16*window.scale), int((16)*window.scale), int(48*window.scale), int(16*window.scale)])
    self.activationGroupField = ctext_field([int(16*window.scale), int((32)*window.scale), int(48*window.scale), int(16*window.scale)])
  def handleInput(self, mouseEvent : windowClass.MouseEvent, rel, keyButtons, tileSize, selectedLayer):
    if mouseEvent.risingEdge[0]:
      #CODE TYPE OBJECTS
      self.objectPoint1 = rel[:]
      if keyButtons.getPressed(pg.K_a):
        self.objectPoint1[0] = round(self.objectPoint1[0]/tileSize*2)*tileSize/2
        self.objectPoint1[1] = round(self.objectPoint1[1]/tileSize*2)*tileSize/2
    
    if mouseEvent.fallingEdge[0]:
      #CODE TYPE OBJECTS
      objectPoint2 = rel[:]
      if keyButtons.getPressed(pg.K_a):
        objectPoint2[0] = round(objectPoint2[0]/tileSize*2)*tileSize/2
        objectPoint2[1] = round(objectPoint2[1]/tileSize*2)*tileSize/2
      
      obj_type  = self.idField.text
      obj_info  = self.storedField.text
      obj_group = self.activationGroupField.text
      
      self.objects += [[self.objectPoint1, objectPoint2, obj_type, obj_info, obj_group, selectedLayer]]

  
    
      
