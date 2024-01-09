import os

os.chdir("LevelEditor")
import math
from json import dumps, loads
from sys import exit

import pygame as pg
from pygame import Vector2
from classes        import *
from functions      import *
from textRenderer   import *
from tileGridClass  import TileGrid, create_grid
from windowClass    import *
from mathFunctions  import *

PI = math.pi

class ToolBar:
  def __init__(self, rect: pg.Rect):
    self.rect = pg.Rect(rect)
    self.offset = Vector2(0, 0)

def main():
  window = Window()
  
  #region tiles
  tileAtlas       = pg.image.load("../Graphics/tile_atlas.png").convert_alpha()
  collisionAtlas  = pg.image.load("../Graphics/Collision_sheet.png")
  tileGrid = TileGrid([int(64*window.scale), int(0), int((400-64)*window.scale), int(240*window.scale)],
                      tileAtlas,
                      16, 
                      collisionAtlas)
  collision_assignments = {}
  if os.path.exists("collision_assignments.json"):
    with open("collision_assignments.json", "r") as file:
      collision_assignments = loads(file.read())
  else:
    print("COLLISION_ASSIGNMENTS_FAILED_TO_LOAD")

  tileDefs = create_tile_definitions(tileGrid.tileSize, tileAtlas.get_size())
  originalTileDefs = tileDefs.copy()
  tileAnimations = [[20, 96, 97, 98, 99], [10, 80, 81, 82], [10, 10, 11], [10, 67, 68, 69], [10, 160, 161, 162, 163], [5, 165, 166, 167, 168]]
  #endregion
  
  pg.font.init()
  font = pg.font.SysFont("segoeuisemibold", int(12*window.scale))
  smallFont = my_font_class(window.scale)
  
  tileSelect = tile_select([int(0),int(0),int(64*window.scale),int(64*window.scale)],tileAtlas,tileGrid.tileSize, collisionAtlas)
  
  objectSystem = ObjectSystem(window)
  allTextFields = [objectSystem.idField, objectSystem.storedField, objectSystem.activationGroupField]
  selectedField = None
  
  toolBar = ToolBar([0,0,int(64*window.scale), window.dim[1]])

  mouseEvent = MouseEvent()
  Clock = pg.time.Clock()
  
  levelFile = "../Levels/Level0.level"
  tileGrid.load(levelFile, objectSystem)
  
  tool = "tile"
  clickStartPos = [0,0]
  selectedTile = 1
  selectedLayer = 0
  showCameraArea = True
  
  keyButtons = KeyButtons()
  Frame = 0
  Exit = 0
  
  while Exit == 0:
    for event in pg.event.get():
      if event.type == pg.QUIT:
        Exit = 1
      if event.type == pg.VIDEORESIZE:
        window.resizeScale = window.dimOriginal[1]/event.h
        window.dim[0] = event.h * 1/window.aspectRatio
        window.dim[1] = event.h
        pg.display.set_mode(window.dim, pg.RESIZABLE)
      if event.type == pg.MOUSEWHEEL:
        if pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos):
          selectedLayer += event.y
          selectedLayer = min(max(selectedLayer,0), tileGrid.grid_layers-1)
        if toolBar.rect.collidepoint(mouseEvent.pos):
          toolBar.offset.y = min(toolBar.offset.y + event.y * 4,0)
      if event.type == pg.KEYDOWN:
        if selectedField == None: #where all the hardcoded input is (things like object mode, lights on, collision_grid_display_toggle, or save)
          if event.key == pg.K_c: showCameraArea = not showCameraArea
          if event.key == pg.K_o: tool = "object"
          if event.key == pg.K_t: tool = "tile"
          if event.key == pg.K_s: saveLevel(levelFile, tileGrid, tileAnimations, originalTileDefs, objectSystem, collision_assignments)
          if event.key == pg.K_f: floodFill(tileGrid, getTileGridPos(mouseEvent.pos, tileGrid), selectedLayer, selectedTile)
        textFieldInput(event, allTextFields, selectedField)
    keyButtons.update()
    mouseEvent.update()
    mouseEvent.pos = [int(mouseEvent.pos[0]*window.resizeScale), int(mouseEvent.pos[1]*window.resizeScale)]
    mouseEvent.prePos = [int(mouseEvent.prePos[0]), int(mouseEvent.prePos[1])]
    for i in range(5):
      if keyButtons.getPressedRisingEdge(pg.K_0+i): toggleLayer(tileGrid, i)
    
    tileSelect.opening(keyButtons, mouseEvent)
    tileSelect.closing(keyButtons, mouseEvent)
    
    arrowKeyScrolling(tileGrid, keyButtons)
    
    placingAtEdgeScroll(mouseEvent, tileGrid)
    
    middleMouseScroll(mouseEvent, tileGrid)
    
    selectedField = textFieldSelect(mouseEvent, allTextFields, selectedField)
    if keyButtons.getPressed(pg.K_LALT ): 
      selectedTile = mousePicking(mouseEvent, tileGrid, selectedLayer, selectedTile)
    if keyButtons.getPressed(pg.K_LCTRL): 
      clickStartPos = mouseRangeFill(mouseEvent, tileGrid, selectedTile, selectedLayer, clickStartPos)
    
    mouseInTileSelect = pg.Rect(tileSelect.rect).collidepoint(mouseEvent.pos)
    mouseInTileGrid   = pg.Rect(tileGrid.rect).collidepoint(mouseEvent.pos)
    #tile select
    if mouseInTileSelect and tileSelect.enabled:
      selectedTile = tileSelect.mouseInput(mouseEvent, selectedTile)
      tool = "tile"
    #placing
    if mouseInTileGrid and not mouseEvent.pressed[1]:
      rel = [mouseEvent.pos[0] - tileGrid.rect[0] + tileGrid.offset[0], mouseEvent.pos[1] - tileGrid.rect[1] + tileGrid.offset[1]]
      if   tool == "tile"  :
        if mouseEvent.pressed[0]:
          if selectedLayer == 4:
            for i in range(1, 3):
              tile = tileGrid.get_tile(convert_to_tile_coords(rel, tileGrid.tileSize), i)
              if tile!=0:
                collision_assignments[str(tile)] = selectedTile
          else:
            if str(selectedTile) in collision_assignments.keys() and selectedLayer != 0:
              tileGrid.place_tile(convert_to_tile_coords(rel, tileGrid.tileSize), collision_assignments[str(selectedTile)], 4)
          mousePlaceTile(mouseEvent, rel, selectedTile, selectedLayer, tileGrid)
        elif mouseEvent.pressed[2]:
          if keyButtons.getPressed(pg.K_LSHIFT):
            for i in range(1, tileGrid.grid_layers):
              tileGrid.place_tile(convert_to_tile_coords(rel, tileGrid.tileSize), 0, i)
          else:
            tileGrid.place_tile(convert_to_tile_coords(rel, tileGrid.tileSize), 0, selectedLayer)
      elif tool == "object":
        if mouseEvent.pressed[2]:
          removeObject(rel, objectSystem.objects)
        objectSystem.handleInput(mouseEvent, rel, keyButtons, tileGrid.tileSize, selectedLayer)
    
    if selectedLayer == tileGrid.Collison_layer:
      tileSelect.mode = "collision"
    else:
      tileSelect.mode = "tile"
    
    for animation in tileAnimations:
      tileDefs = animate_tile(tileDefs, animation, Frame)
    
    window.window.fill((16,16,32))
    drawInTileGrid(window, tileGrid, tileDefs, mouseEvent, showCameraArea)
    window.display.set_clip(toolBar.rect)
    drawTextInfo(window, font, selectedLayer, tileGrid, mouseEvent, tool, toolBar.offset)
    drawTextFields(window, allTextFields, smallFont, toolBar.offset)
    drawTIG(window, allTextFields, font, toolBar.offset)
    window.display.set_clip()
    drawObjects(window, tileGrid, objectSystem, mouseEvent, font)
    tileSelect.draw(window, mouseEvent, tileGrid.tileSize)
    
    window.window.set_clip()
    
    window.display.blit(pg.transform.scale(window.window, window.dim), (0,0))
    pg.display.update()
    
    Clock.tick(144)
    Frame += 1

main()
pg.quit()
exit()