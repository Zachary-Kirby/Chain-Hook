import pygame as pg

class KeyButtons():
  def __init__(self):
    self.prePressed = pg.key.get_pressed()
    self.pressed = pg.key.get_pressed()
  def update(self):
    self.prePressed = self.pressed
    self.pressed = pg.key.get_pressed()
  def getPressed(self, key):
    return self.pressed[key]
  #in case you don't know rising edge means when the signal goes from false to true
  def getPressedRisingEdge(self, key):
    return self.prePressed[key] == 0 and self.pressed[key] == 1
  #in case you don't know falling edge means when the signal goes from true to false
  def getPressedFallingEdge(self, key): 
    return self.prePressed[key] == 1 and self.pressed[key] == 0

class MouseEvent():
  def __init__(self):
    self.pressed = [0,0,0]
    self.prePressed = [0,0,0]
    self.pos = [0,0]
    self.prePos = [0,0]
    self.risingEdge = [0,0,0]
    self.fallingEdge = [0,0,0]
  def update(self):
    self.prePressed = self.pressed.copy()
    self.pressed = list(pg.mouse.get_pressed())
    self.risingEdge[0] = self.prePressed[0] == 0 and self.pressed[0] == 1
    self.risingEdge[1] = self.prePressed[1] == 0 and self.pressed[1] == 1
    self.risingEdge[2] = self.prePressed[2] == 0 and self.pressed[2] == 1
    self.fallingEdge[0] = self.prePressed[0] == 1 and self.pressed[0] == 0
    self.fallingEdge[1] = self.prePressed[1] == 1 and self.pressed[1] == 0
    self.fallingEdge[2] = self.prePressed[2] == 1 and self.pressed[2] == 0
    self.prePos = [self.pos[0], self.pos[1]]
    self.pos = list(pg.mouse.get_pos())

class Window():
  def __init__(self):
    self.scale = 3
    self.resizeScale = 1
    self.dim = [400*self.scale, 240*self.scale]
    self.dimOriginal = self.dim.copy()
    self.aspectRatio = self.dim[1] / self.dim[0]
    self.window = pg.Surface(self.dim)
    self.display = pg.display.set_mode(self.dim, pg.RESIZABLE)
