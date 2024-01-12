from pygame import Vector2

def add_pos_to_rect(rect, pos):
  return [rect[0]+pos[0], rect[1]+pos[1], rect[2], rect[3]]

def rect_bot(rect):
  return rect[1] + rect[3]

def rect_top(rect):
  return rect[1]

def rect_left(rect):
  return rect[0]

def rect_right(rect):
  return rect[0] + rect[2]

def rect_topleft(rect):
  return rect_left(rect), rect_top(rect)

def rect_botright(rect):
  return rect_right(rect), rect_bot(rect)

def rect_center(rect):
  return Vector2([rect[0] + rect[2]/2, rect[1] + rect[3] / 2])

def rect_centerx(rect):
  return rect[0] + rect[2]/2

def rect_centery(rect):
  return rect[1] + rect[3]/2

def collide_rects(rect, rect2):
  return rect_right(rect) > rect_left(rect2) and rect_left(rect) < rect_right(rect2) and rect_bot(rect) > rect_top(rect2) and rect_top(rect) < rect_bot(rect2)

def collide_rects_inclusive(rect, rect2):
  return rect_right(rect) >= rect_left(rect2) and rect_left(rect) <= rect_right(rect2) and rect_bot(rect) >= rect_top(rect2) and rect_top(rect) <= rect_bot(rect2)

def point_in_rect(pos, rect):
  return pos[0] >= rect_left(rect) and pos[0] <= rect_right(rect) and pos[1] >= rect_top(rect) and pos[1] <= rect_bot(rect)

def collide_point_in_rect(pos, rect):
  return pos[0] >= rect_left(rect) and pos[0] <= rect_right(rect) and pos[1] >= rect_top(rect) and pos[1] <= rect_bot(rect)
