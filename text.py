import pygame as pg

class my_font_class():
  char_ids = {
    "A":1,
    "B":2,
    "C":3,
    "D":4,
    "E":5,
    'F':6,
    'G':7,
    'H':8,
    'I':9,
    'J':10,
    'K':11,
    'L':12,
    'M':13,
    'N':14,
    'O':15,
    'P':16,
    'Q':17,
    'R':18,
    'S':19,
    'T':20,
    'U':21,
    'V':22,
    'W':23,
    'X':24,
    'Y':25,
    'Z':26,
    'a':27,
    'b':28,
    'c':29,
    'd':30,
    'e':31,
    'f':32,
    'g':33,
    'h':34,
    'i':35,
    'j':36,
    'k':37,
    'l':38,
    'm':39,
    'n':40,
    'o':41,
    'p':42,
    'q':43,
    'r':44,
    's':45,
    't':46,
    'u':47,
    'v':48,
    'w':49,
    'x':50,
    'y':51,
    'z':52,
    '0':53,
    '1':54,
    '2':55,
    '3':56,
    '4':57,
    '5':58,
    '6':59,
    '7':60,
    '8':61,
    '9':62,
    '(':63,
    ')':64,
    '[':65,
    ']':66,
    '{':67,
    '}':68,
    ':':69,
    ';':70,
    '.':71,
    ',':72,
    '!':73,
    '?':74,
    '"':75,
    "'":76,
    '|':77,
    '\\':78,
    '/':79,
    '>':80,
    '<':81,
    '-':82,
    '_':83,
    '+':84,
    '=':85,
    '^':86,
    '~':87,
    '`':88,
    '@':89,
    '#':90,
    '$':91,
    '%':92,
    '&':93
    }
  def __init__(self):
    self.image = pg.image.load("Graphics/font.bmp")
    self.image.set_colorkey((0,0,0))
    self.text_width = 8
    self.text_height = 8
  def draw(self, Window, pos, text):
    for i in range(len(text)):
      if text[i]!=" ":
        
        Window.blit(self.image, (pos[0]+self.text_width*i, pos[1]), (self.char_ids[text[i]]*self.text_width, 0, self.text_width, self.text_height))

def draw_text(Window, pixel_font, pos, text:str):
  lines = text.splitlines()
  for i in range(len(lines)):
    width = len(lines[i]) * pixel_font.text_width
    Window.fill((128,128,128), (pos[0]-width/2, pos[1]+i*pixel_font.text_height, width, pixel_font.text_height), pg.BLEND_RGB_MULT)
    pixel_font.draw(Window, (pos[0]-width/2, pos[1]+i*pixel_font.text_height), lines[i])
