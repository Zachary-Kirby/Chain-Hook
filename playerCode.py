from mathFunctions import *
from rectFunctions import *
from physics import *
import levelClass
import controls
import pygame as pg

class Player():
  animations = {"standing_right" : [[0,0,16,16]], 
                "standing_left"  : [[0,16,16,16]], 
                "running_right"  : [[16,0,16,16], [32,0,16,16], [48,0,16,16], [64,0,16,16]], 
                "running_left"   : [[16,16,16,16], [32,16,16,16], [48,16,16,16], [64,16,16,16]],
                "air_right"      : [[80, 0, 16, 16]],
                "air_left"       : [[80, 16, 16, 16]],
                "wall_right"     : [[96, 0, 16, 16]],
                "wall_left"      : [[96, 16, 16, 16]],
                "dying_left" : [[16*10, 0, 16, 16], [16*11, 0, 16, 16]],
                "dying_right" : [[16*10, 16, 16, 16], [16*11, 16, 16, 16]],
                "climbing"    : [[16*14, 0, 16, 16], [16*15, 0, 16, 16]]}
  dead_frame_time = 10
  def __init__(self, rect):
    self.offset = [-4,-4]
    self.rect = rect
    self.normal = [0, -1]
    self.pre_rect = rect[:]
    self.vel = [0,0]
    self.grounded = False
    self.wall = 0
    self.frametimer = 0
    self.frametime = 3
    self.frame = 0
    self.facing = 'right'
    self.previous_animation = "None"
    jump_height = -2*16-8
    self.play_speed = 0.8 #the faster the simulation speed the higher the chance the maximum height will be in a half frame and be skipped.
    #self.jump_vel = 5.5*self.play_speed*self.play_speed
    self.grav_vec = [0, 0.4*self.play_speed]
    self.jump_vel = math.sqrt(-jump_height*self.grav_vec[1]*2) #wow calculus paid off
    self.no_wall_grab_timer = 0 
    self.no_wall_grab_time = 19 #in frames
    self.move_cancel_timer = 0
    self.wall_move_cancel_time = 25
    self.wall_slide_slowdown = 0.0
    
    #self.wall_jump_y_vel = 5*(1-self.play_speed/1.5)
    self.wall_jump_y_vel = self.jump_vel#math.sqrt(-jump_height*self.grav_vec[1]*2)
    self.wall_jump_x_vel = 64 / (2*self.wall_jump_y_vel/self.grav_vec[1]) #2*(1-self.play_speed/1.5)
    jump_width = 4*16
    self.max_walk_speed = jump_width/(2*self.jump_vel/self.grav_vec[1])
    self.x_slowdown = 0.8
    self.x_accel = self.max_walk_speed*(1/self.x_slowdown-1)*0.1
    self.Hookshot_accel = 0.25*self.play_speed
    self.light_on = True
    self.input_cancle = False
    self.climbing = False
    self.dead = False
    self.dead_timer = 0
    self.dead_time = 30
    self.swing_inversion = 1
  def draw(self, window, sprite_atlas, Camera):
    
    if self.vel[0] > 0: self.facing = "right"
    elif self.vel[0] < 0: self.facing = "left"
    
    animation_type = "standing_" + self.facing
    animation_repeats = True
    frame_wait = self.frametime
    
    if self.vel[0] <= -0.8 or self.vel[0] >= 0.8:
      animation_type = "running_" + self.facing
    
    if self.grounded == False:
      animation_type = "air_" + self.facing
    
    if self.wall > 0:
      animation_type = "wall_right"
      self.facing = "right"
    elif self.wall < 0:
      animation_type = "wall_left"
      self.facing = "left"
    
    if self.climbing:
      animation_type = "climbing"
      frame_wait = 16
    
    if self.dead:
      animation_type = "dying_" + self.facing
      animation_repeats = False
      frame_wait = self.dead_frame_time
      if "dying" not in self.previous_animation:
        self.frame = 0
    
    self.frametimer = self.frametimer + 1
    
    if "running" in animation_type:
      self.frametimer += abs(self.vel[0] // self.max_walk_speed)
    
    if self.frametimer > frame_wait:
      if animation_repeats:
        self.frame += 1
      elif self.frame < len(self.animations[animation_type]):
        self.frame = min(self.frame+1, len(self.animations[animation_type])-1)
      self.frametimer = 0
    
    
    
    self.previous_animation = animation_type
    self.frame = self.frame % len(self.animations[animation_type])
    window.blit(sprite_atlas, [self.rect[0]+self.offset[0]-Camera[0], self.rect[1]+self.offset[1]-Camera[1]]+self.rect[2:], self.animations[animation_type][self.frame])

class Hookshot():
  sprites = {"up"    :[80+32, 0, 6, 3],
             "down"  :[80+32, 2, 6, 3],
             "right" :[82+32,0,3,6],
             "left"  :[80+32,0,3,6],
             "ball"  :[80+32,0,6,6]}
  def __init__(self, pos):
    self.enabled = 0
    self.pre_enabled = 0
    self.start_pos = [0,0]
    self.pos = [0, 0]
    self.vel = [0, 0]
    self.speed = 16
    self.facing = "right"
    self.max_len = 128*2
    self.min_len = 16
    self.player_pos = [0,0]
    self.len = 0
    self.start_len = 0
    self.hooked = False
    self.pre_hooked = False
  def draw(self, window, sprite_atlas, Camera, player_pos):
    
    if not self.enabled:
      return
    
    d=get_dist(player_pos, self.pos)
    w=player_pos[0]-self.pos[0]
    h=player_pos[1]-self.pos[1]
    for t in range(0,int(d),4):
      window.blit(sprite_atlas, [self.pos[0]+w/d*t-Camera[0]-self.sprites["ball"][2]/2,self.pos[1]+h/d*t-Camera[1]-self.sprites["ball"][3]/2], self.sprites["ball"])
    
    if abs(self.vel[0]) > abs(self.vel[1]):
      if self.vel[0] > 0:
        self.facing = "right"
      elif self.vel[0] < 0:
        self.facing = "left"
    else:
      if self.vel[1] > 0:
        self.facing = "down"
      elif self.vel[1] < 0:
        self.facing = "up"
    
    window.blit(sprite_atlas, [self.pos[0]-Camera[0]-self.sprites[self.facing][2]/2, self.pos[1]-Camera[1]-self.sprites[self.facing][3]/2], self.sprites[self.facing])

def getPlayerFacing(Player):
  if Player.facing=="left":
    return -1
  if Player.facing=="right":
    return 1

def playerState(player : Player, deathScreen, ladderRect):
  player.no_wall_grab_timer = countdownTimer(player.no_wall_grab_timer)
  player.move_cancel_timer = countdownTimer(player.move_cancel_timer)    
  
  if player.climbing:
    if rect_left(player.rect) < rect_left(ladderRect):
      player.climbing = False
    if rect_right(player.rect) > rect_right(ladderRect):
      player.climbing = False
    if rect_top(player.rect) < rect_top(ladderRect):
      player.climbing = False
    if rect_bot(player.rect) > rect_bot(ladderRect):
      player.climbing = False
  
  if player.climbing:
    player.vel[0] = 0
    player.vel[1] = 0

def playerInput(player : Player, hookshot : Hookshot, windowInput, camera, sounds, level, debugMode):
  if player.dead:
    return
  
  if windowInput.mouseEvent.pressed[2] and not windowInput.mouseEvent.prePressed[2]:
    direction_vector = normalize(sub_pos(sub_pos(rect_center(player.rect), camera), windowInput.mouseEvent.pos))
    
    player.vel[0] = -direction_vector[0] * 5
    player.vel[1] = -direction_vector[1] * 5
  
  if hookshot.enabled:
    
    if not windowInput.mouseEvent.pressed[0] and windowInput.mouseEvent.prePressed[0]:
      hookshot.enabled = False
  else:
    if not windowInput.mouseEvent.prePressed[0] and windowInput.mouseEvent.pressed[0]:
      hookshot.enabled = not hookshot.enabled
      if hookshot.enabled:
        hookshot.pos = rect_center(player.rect)
        hookshot.vel = [0,0]
        direction = sub_pos(windowInput.mouseEvent.pos, sub_pos(add_pos(rect_center(player.rect), player.vel), camera))
        length = get_len(direction)
        direction = [direction[0]/length, direction[1]/length]
        hookshot.vel[0] = direction[0] * hookshot.speed + player.vel[0]
        hookshot.vel[1] = direction[1] * hookshot.speed + player.vel[1]
  
  if player.climbing:
    if controls.left in windowInput.buttons:
      player.rect[0] += -2
    if controls.right in windowInput.buttons:
      player.rect[0] +=  2
    if controls.up in windowInput.buttons:
      player.rect[1] += -2
    if controls.down in windowInput.buttons:
      player.rect[1] +=  2
  
  if controls.jump in windowInput.buttons and player.grounded:
    sounds.Jump.play()
    player.vel[0] += player.jump_vel*player.normal[0]*0.5
    player.vel[1] = -player.jump_vel#*Player.normal[1]
    player.no_wall_grab_timer = player.no_wall_grab_time
  if controls.jump in windowInput.buttonsFallingEdge and player.vel[1]<0:
    player.vel[1] *= 0.5
  
  if controls.jump in windowInput.buttonsRisingEdge and hookshot.hooked and hookshot.enabled and not player.grounded:
    hookshot.enabled = False
  
  if player.wall!=0:
    player.move_cancel_timer=0
    
  #wall jump
  if player.grounded==False and player.wall!=0:
    if player.no_wall_grab_timer==0:
      player.vel[1] *= player.wall_slide_slowdown
    if controls.jump in windowInput.buttonsRisingEdge:
      sounds.Jump.play()
      player.vel[1] = -player.wall_jump_y_vel
      player.vel[0] = player.wall_jump_x_vel*player.wall
      player.rect[0] += player.wall
      player.move_cancel_timer = math.copysign(player.wall_move_cancel_time, player.wall)
  
  #walking
  if not player.climbing:
    if player.grounded:
      if controls.left in windowInput.buttons and player.move_cancel_timer<=0: #and Player.vel[0] > -3:
        player.vel[0] = player.vel[0] + player.x_accel * player.normal[1]
        player.vel[1] = player.vel[1] - player.x_accel * player.normal[0]
      elif controls.right in windowInput.buttons and player.move_cancel_timer>=0: #and Player.vel[0] < 3:
        player.vel[0] = player.vel[0] - player.x_accel * player.normal[1]
        player.vel[1] = player.vel[1] + player.x_accel * player.normal[0]
    elif hookshot.hooked and hookshot.enabled:
      hookshot_vec = pg.Vector2(sub_pos(rect_center(player.rect), hookshot.pos))
      if controls.right in windowInput.buttonsRisingEdge or controls.left in windowInput.buttonsRisingEdge:
        player.swing_inversion = math.copysign(1, hookshot_vec.y)
      
      if hookshot_vec.length_squared() >= (hookshot.len-4) * (hookshot.len-4) and rect_centery(player.rect) >= hookshot.pos[1]:
        hookshot_normal = hookshot_vec.normalize()
        speed = get_len(player.vel)
        if controls.left in windowInput.buttons and player.move_cancel_timer<=0 and rect_centerx(player.rect) >= hookshot.pos[0]:
          player.vel[0] = player.vel[0] - player.Hookshot_accel* hookshot_normal.y * player.swing_inversion#*math.copysign(1, hookshot_vec.y)
          player.vel[1] = player.vel[1] - player.Hookshot_accel*-hookshot_normal.x * player.swing_inversion#*math.copysign(1, hookshot_vec.y)
          
        elif controls.right in windowInput.buttons and player.move_cancel_timer>=0 and rect_centerx(player.rect) <= hookshot.pos[0]:
          player.vel[0] = player.vel[0] - player.Hookshot_accel*-hookshot_normal.y * player.swing_inversion#*math.copysign(1, hookshot_vec.y)
          player.vel[1] = player.vel[1] - player.Hookshot_accel* hookshot_normal.x * player.swing_inversion#*math.copysign(1, hookshot_vec.y)
  
  if pg.K_r in windowInput.buttonsRisingEdge and pg.K_LALT not in windowInput.buttons:
    player.rect[0] = level.checkpoint[0]
    player.rect[1] = level.checkpoint[1]
  
  if debugMode:
    if pg.K_UP in windowInput.buttons:
      player.rect[1] -= level.tileSize*2
      player.vel[1] = 0
    if pg.K_DOWN in windowInput.buttons:
      player.rect[1] += level.tileSize*2
      player.vel[1] = 0
    if pg.K_LEFT in windowInput.buttons:
      player.rect[0] -= level.tileSize*2
      player.vel[1] = 0
    if pg.K_RIGHT in windowInput.buttons:
      player.rect[0] += level.tileSize*2
      player.vel[1] = 0

def playerGravity(player : Player, hookshot : Hookshot):
  if not player.climbing:
    grav_vec = player.grav_vec
    if hookshot.enabled and hookshot.hooked:
      d = get_dist(rect_center(player.rect), hookshot.pos)
      if d >= hookshot.len:
        hook_vec = sub_pos(hookshot.pos, rect_center(player.rect))
        hook_vec = [hook_vec[0]/d, hook_vec[1]/d]
        dot = grav_vec[0] * hook_vec[0] + grav_vec[1] * hook_vec[1]
        grav_vec = [grav_vec[0]-hook_vec[0]*dot, grav_vec[1]-hook_vec[1]*dot]
        player.vel[1] += grav_vec[1]
        player.vel[0] += grav_vec[0]
      else:
        player.vel[0] += grav_vec[0]
        player.vel[1] += grav_vec[1]
    else:
      player.vel[0] += grav_vec[0]
      player.vel[1] += grav_vec[1]
  

def playerCollision(player : Player, hookshot : Hookshot, level : levelClass.Level, windowInput, fade):
  move = [player.vel[0], player.vel[1]]
  
  #super smooth hookshot mode
  #deals with imprecision with the hookshot movement
  if True:
    if hookshot.hooked and hookshot.enabled:
      if get_dist(add_pos(rect_center(player.rect), move), hookshot.pos) > hookshot.len:
        
        circumfrance = hookshot.len * 2 * math.pi
        #find the starting vector of the player on the circle
        hook_vec = normalize(sub_pos(rect_center(player.rect), hookshot.pos))
        move_l = vec_dot(vec_normal(hook_vec, -1), move) #tangent movement length and direction
        #find how many radians are in the arclength and which direction the move is
        
        move_radians = move_l/circumfrance * 2 * math.pi #* move_dir
        #move the player by that many degrees around the hookshot
        hook_vec = complex_multiply(hook_vec, [math.cos(move_radians), math.sin(move_radians)]) #rotate the vector
        new_pos = add_pos(vec_scale(hook_vec, hookshot.len), hookshot.pos)
        move = sub_pos(new_pos, rect_center(player.rect))
        
        #set the velocity to itself but rotated to be tanget to the new point
        player.vel = complex_multiply(player.vel, [math.cos(move_radians), math.sin(move_radians)])
  
  player.rect[0] += move[0]
  
  tile_topleft  = convert_to_tile_coords(rect_topleft (player.rect), level.tileSize)
  tile_botright = convert_to_tile_coords(rect_botright(player.rect), level.tileSize)
  
  Level_collision = getTileCollision(tile_topleft, tile_botright, level, 1)
  
  normal, col_types = physicsMove(player.rect, player.pre_rect, Level_collision, 'x', level, output_collision_type=True) #this could be interesting
  
  player.vel = stopVel(normal, player.vel, 'x')
  
  if level.get_tile([(int(player.rect[0]-1)//level.tileSize), int((player.rect[1]+player.rect[3]/2)//level.tileSize)]) == 1 and controls.left in windowInput.buttons:
    player.wall = 1
  elif level.get_tile([(int(player.rect[0]+player.rect[2]+1)//level.tileSize), int((player.rect[1]+player.rect[3]/2)//level.tileSize)]) == 1 and controls.right in windowInput.buttons:
    player.wall = -1
  else:
    player.wall = 0
  
  player.rect[1] += move[1]
  
  tile_topleft  = convert_to_tile_coords(rect_topleft (player.rect), level.tileSize)
  tile_botright = convert_to_tile_coords(rect_botright(player.rect), level.tileSize)
  no_collision = [0]
  if player.climbing:
    no_collision += [2]
  Level_collision = getTileCollision(tile_topleft, tile_botright, level, 1, no_collision=no_collision)
  
  normal, col_types = physicsMove(player.rect, player.pre_rect, Level_collision, 'y', level, output_collision_type=True)
  
  player.vel = stopVel(normal, player.vel, 'y')
  
  player.pre_rect = player.rect.copy()
  
  if COLLISION_TYPES.WATER in col_types:
    player.vel[1] *= 0.9
    player.vel[1] -= 0.3
  if not player.dead:
    for deadly in COLLISION_TYPES.DEADLY:
      if deadly in col_types:
        player.dead = True
        player.dead_timer = player.dead_time
        player.vel[0] = 0
        player.vel[1] = 0
        fade.setTime(30)
        fade.playStart()
        break
  
  player.grounded = False
  if normal[1] < 0:
    player.normal = normal.copy()
    player.grounded = True