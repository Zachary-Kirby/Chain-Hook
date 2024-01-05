import math

class Vector2():
  def __init__(self, x, y):
    self.x = x
    self.y = y
  def add(self, vec):
    self.x += vec.x
    self.y += vec.y
  def as_tuple(self):
    return (self.x, self.y)

def cast_down(line, x):
  w = line[2] - line[0]
  t = (x - line[0])/w
  return lerp(line[1], line[3], t)

def lerp(a, b, t):
  return a + (b - a)*t

def lerp2(a, b, t):
  return [a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t]

def get_dist(pos1, pos2):
  return math.dist(pos1[:2], pos2[:2])

def get_len(vec):
  return (vec[0]*vec[0] + vec[1] * vec[1])**0.5

def normalize(vec):
  d=get_len(vec)
  return [vec[0]/d, vec[1]/d]

def angle_to(pos, pos2):
  dif = pos[0]-pos2[0], pos[1]-pos2[1]
  if pos[0] > pos2[0]:
    norm = normalize(dif)
    a = math.degrees(math.atan(norm[1]/norm[0]))
    return a % 360
  else:
    norm = normalize(dif)
    a = math.degrees(math.atan(norm[1]/norm[0]))+180
    return a % 360

def multiply_vec(vec, m):
  return [vec[0]*m, vec[1]*m]

def min_mag(vec1, vec2):
  m1 = get_len(vec1)
  m2 = get_len(vec2)
  m = min(m1, m2)
  return m

def complex_multiply(vec, rvec):
  return [vec[0]*rvec[0]-vec[1]*rvec[1], vec[0]*rvec[1]+rvec[0]*vec[1]]

def vec_dot(a, b):
  return a[0]*b[0]+a[1]*b[1]

def vec_normal(v, handed = 1):
  """
  1  is right handed
  -1 is left handed
  """
  return [v[1]*handed, -v[0]*handed]

def vec_scale(vec, scale):
  return [vec[0]*scale, vec[1]*scale]

def add_pos(pos1, pos2):
  """
  also takes rects that are in the form [x,y,w,h]
  """
  return [pos1[0]+pos2[0],pos1[1]+pos2[1]]

def sub_pos(pos1, pos2):
  """
  pos1 - pos2
  also takes rects that are in the form [x,y,w,h]
  """
  return [pos1[0]-pos2[0],pos1[1]-pos2[1]]

def get_direction(pos1, pos2):
  return normalize(sub_pos(pos2, pos1))

def round_to_topleft_of_tile(pos,tile_size):
  return [pos[0]//tile_size*tile_size, pos[1]//tile_size*tile_size]

def round_to_botright_of_tile(pos,tile_size):
  return [pos[0]//tile_size*tile_size+tile_size, pos[1]//tile_size*tile_size+tile_size]

def convert_to_tile_coords(pos, tile_size=16):
  return int(pos[0]//tile_size), int(pos[1]//tile_size)

def countdownTimer(timer):
  if timer!=0:
      timer -= math.copysign(1, timer)
  return timer
