import pygame as pg

class Window():
  def __init__(self, w, h):
    self.dim = [w, h]
    self.dimOriginal = self.dim.copy()
    self.aspectRatio = self.dim[1] / self.dim[0]
    self.display = pg.display.set_mode(self.dim, pg.RESIZABLE | pg.SCALED)
    self.icon = pg.image.load("Graphics/icon.bmp")
    pg.display.set_icon(self.icon)
    pg.display.set_caption("Creep'n'Swing")

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

class WindowInput():
  def __init__(self):
    self.buttons = []
    self.buttonsRisingEdge = []
    self.buttonsFallingEdge = []
    self.mouseEvent = MouseEvent()
    self.exit = False
  def update(self,scale):
    self.buttonsFallingEdge = []
    self.buttonsRisingEdge = []
    for event in pg.event.get():
      if event.type == pg.QUIT:
        self.exit = True
      elif event.type == pg.KEYDOWN:
        if event.key not in self.buttons:
          self.buttons += [event.key]
          self.buttonsRisingEdge += [event.key]
        if event.key == pg.K_ESCAPE:
          self.exit = True
        if event.key == pg.K_F11:
          
          pg.display.toggle_fullscreen()
          
      elif event.type == pg.KEYUP:
        if event.key in self.buttons:
          self.buttons.remove(event.key)
        self.buttonsFallingEdge += [event.key]
    
    self.mouseEvent.update()
    self.mouseEvent.pos = [int(self.mouseEvent.pos[0]*scale), int(self.mouseEvent.pos[1]*scale)]
    self.mouseEvent.prePos = [int(self.mouseEvent.prePos[0]), int(self.mouseEvent.prePos[1])]
