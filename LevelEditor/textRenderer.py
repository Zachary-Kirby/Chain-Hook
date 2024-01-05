import pygame as pg
import fileHandler

class my_font_class():
  char_ids = fileHandler.load("charIds.json")
  def __init__(self, scale):
    self.image = pg.image.load("../Graphics/font.bmp")
    self.image = pg.transform.scale(self.image, [self.image.get_width() * scale, self.image.get_height() * scale])
    self.image.set_colorkey((0,0,0))
    self.text_width = 8*scale
    self.text_height = 8*scale
  def draw(self, Window, pos, text):
    for i in range(len(text)):
      if text[i]!=" ":
        
        Window.blit(self.image, (pos[0]+self.text_width*i, pos[1]), (self.char_ids[text[i]]*self.text_width, 0, self.text_width, self.text_height))

def draw_text(Window, pixel_font, pos, text:str):
  lines = text.splitlines()
  for i in range(len(lines)):
    width = len(lines[i]) * pixel_font.text_width
    Window.fill((128,128,128), (pos[0], pos[1]+i*pixel_font.text_height, width, pixel_font.text_height), pg.BLEND_RGB_MULT)
    pixel_font.draw(Window, (pos[0], pos[1]+i*pixel_font.text_height), lines[i])
