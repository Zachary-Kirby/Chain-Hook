from fileHandler import load
import levelClass
from mathFunctions import *
from rectFunctions import *
import playerCode
import controls
import random
import pygame as pg

class Flip():
  def __init__(self, pos, Tile_size, layer, tile):
    self.rect = [pos[0]//Tile_size*Tile_size, pos[1]//Tile_size*Tile_size, Tile_size, Tile_size]
    self.layer = layer
    self.tile = tile

class pressure_plate():
  def __init__(self, pos, action_group):
    self.rect = [pos[0], pos[1]+14, 16, 2]
    self.action_group = action_group

class door():
  def __init__(self, pos1, pos2):
    self.rect1 = [pos1[0], pos1[1], 16, 16]
    self.rect2 = [pos2[0], pos2[1], 16, 16]

class npc():
  def __init__(self,pos, speech_ref, type):
    self.type = type
    self.rect = [pos[0]+4,pos[1]+1,8,15]
    self.speech_ref = speech_ref
    self.colliding_with_player = False
    self.facing = "right"
  def draw(self, Window, Sprite_atlas, Npc_defs, Camera):
    Window.blit(Sprite_atlas, sub_pos(self.rect, Camera), Npc_defs[self.type+"_"+self.facing])
    if self.colliding_with_player:
      Window.blit(Sprite_atlas, (self.rect[0]+self.rect[2]-Camera[0], self.rect[1]-7-Camera[1]), Npc_defs["bubble"])

class red_gem_bubble():
  type = "red_gem_bubble"
  def __init__(self, pos):
    self.rect = [pos[0], pos[1], 16, 16]
    self.image_rect = [16 * 2, 16 * 7, 16, 16]
    self.offset = [0,0]
  def draw(self, Window, Sprite_sheet, Camera):
    Window.blit(Sprite_sheet, add_pos(sub_pos(self.rect,Camera), self.offset), self.image_rect)

class ladder():
  def __init__(self, topleft, botright, data):
    self.topleft = topleft
    self.botright = botright
    self.rect = [topleft[0], topleft[1], botright[0]-topleft[0], botright[1]-topleft[1]]
    self.data = data
 
class camera_zone():
  def __init__(self, type, topleft, botright):
    self.type = type
    self.rect = [topleft[0], topleft[1], botright[0]-topleft[0], botright[1]-topleft[1]]

class sign():
  def __init__(self,pos,sign_name):
    self.pos = pos
    self.sign_name = sign_name
    self.chars = 0

class onoff():
  def __init__(self, pos, timer, time, layer):
    self.pos = pos
    self.timer = timer
    self.time = time
    self.layer = layer
    self.stored = [0, 0, 0, 0, 0, 0]

class room():
  def __init__(self, topleft, botright, room_id):
    self.rect = [topleft[0], topleft[1], botright[0]-topleft[0], botright[1]-topleft[1]]
    self.room_id = room_id

class armorer_boss():
  def __init__(self, pos):
    self.rect = [pos[0], pos[1], 10, 13]
    self.sprite_defs = load("armorer_boss_defs.json")
    
    self.movement_point = [[0,0], [0,0], pos]
    self.movement_point_index = 2
    self.movement_target = pos
    self.vel = [0, 0]
    
    self.spear_pos = [pos[0]+16,pos[1]]
    self.spear_angle = 0
    self.spear_vel = [0,0]
    self.spear_throw_timer = 0
    self.spear_throw_time = 60*2
    self.spear_speed = 40/60*16
    self.spear_stuck_timer = 0
    self.spear_stuck_time = 60*2
    self.spear_state = "throwing"
    self.spear_return_timer = 0
    self.spear_return_time = 60*5
    self.spear_back_timer = 0
    self.spear_back_time = 10
    self.spear_offset = [0,0]
    
    self.sword_points = [[0,0], [0,0]]
    self.sword_targets = []
    self.sword_target_index = 0
    self.sword_state = "floating"
    self.sword_swipe_charge_time = 60*5
    self.sword_swipe_charge_timer = self.sword_swipe_charge_time
    self.sword_charge_time = 10
    self.sword_charge_timer = self.sword_charge_time
    self.sword_back_time = 10
    self.sword_back_timer = self.sword_back_time
    self.sword_dash_time = 8
    self.sword_dash_timer = self.sword_dash_time
    self.sword_stuck_time = 60
    self.sword_stuck_timer = 0
    self.sword_target = [0,0]
    self.sword_pos = [pos[0], pos[1]]
    self.sword_offset = [0,0]
    self.sword_vel = [0,0]
    self.sword_speed = 40/60*16
    self.sword_acceleration = 40/60/60*16
    self.sword_angle = 90
    
    self.ball_pos = [0,0]
    self.ball_vel = [0,0]
    self.ball_target_vel = [0,1]
    self.ball_state = "swinging"
    self.ball_length = 32
    
  def draw(self, Window, Sprite_atlas, Camera):
    spear_img = pg.Surface(self.sprite_defs["spear"][2:])
    spear_img.set_colorkey((0,0,0))
    spear_img.blit(Sprite_atlas, (0,0), self.sprite_defs["spear"])
    spear_img = pg.transform.rotate(spear_img, -self.spear_angle+90)
    center = spear_img.get_rect().center
    Window.blit(spear_img, add_pos(sub_pos(sub_pos(self.spear_pos, Camera), center), self.spear_offset))
    
    sword_img = pg.Surface(self.sprite_defs["sword"][2:])
    sword_img.set_colorkey((0,0,0))
    sword_img.blit(Sprite_atlas, (0,0), self.sprite_defs["sword"])
    sword_img = pg.transform.rotate(sword_img, -self.sword_angle+90)
    center = sword_img.get_rect().center
    Window.blit(sword_img, add_pos(sub_pos(sub_pos(self.sword_pos, Camera), center), self.sword_offset))
    
    ball_img = pg.Surface(self.sprite_defs["chain_ball"][2:])
    ball_img.set_colorkey((0,0,0))
    ball_img.blit(Sprite_atlas, (0,0), self.sprite_defs["chain_ball"])
    Window.blit(ball_img, sub_pos(self.ball_pos, Camera))
    sub_pos(self.ball_pos, Camera)
    Window.blit(Sprite_atlas, sub_pos(self.rect, Camera), self.sprite_defs["boss"]["default"])

class skin_doll():
  animations = {"left"  : [[0, 32, 16, 32], [16, 32, 16, 32], [32, 32, 16, 32], [48, 32, 16, 32], [64, 32, 16, 32]],
                "right" : [[0, 64, 16, 32], [16, 64, 16, 32], [32, 64, 16, 32], [48, 64, 16, 32], [64, 64, 16, 32]]}
  def __init__(self, pos):
    self.rect = [pos[0], pos[1], 16, 32]
    self.vel  = [0, 0]
    self.facing = 'left'
    self.frame = 0
    self.frame_timer = 0
    self.frame_time  = 8
    self.functions = ["move_to_player", "slowed_by_walls", "deals_damage", "slowed_by_darkness", "random_slowness"] #this might be ok to deal with
  def draw(self, window, sprite_atlas, camera):
    
    if self.vel[0] > 0:
      self.facing = "right"
    elif self.vel[0] < 0:
      self.facing = "left"
    
    animation_type = self.facing
    
    if self.frame_timer == self.frame_time:
      self.frame += 1
      self.frame_timer = 0
    else:
      self.frame_timer += 1
    
    window.blit(sprite_atlas, sub_pos(self.rect, camera), self.animations[animation_type][self.frame % len(self.animations[animation_type])])

class pull_chain():
  chain_clip = [112, 0, 6, 6]
  ring_clip  = [3*16, 6*16, 16, 16]
  def __init__(self, origin, end, pull_down_time, pull_up_time, group):
    self.origin = origin
    self.end = end
    self.pos = origin
    self.pre_pull_percent = 0
    self.pull_percent = 0
    self.pull_down_time = pull_down_time
    self.pull_up_time = pull_up_time
    self.group = group
    self.pulling = False
  def draw(self, Window, Sprite_atlas, Camera):
    
    length = get_dist(self.origin, self.pos)
    if length > 4:
      direction = [(self.origin[0] - self.pos[0])/length, (self.origin[1] - self.pos[1])/length]
      for i in range(0, int(length), 4):
        Window.blit(Sprite_atlas, 
        [self.origin[0] - direction[0]*i-self.chain_clip[2]/2 - Camera[0], 
       self.origin[1] - direction[1]*i-self.chain_clip[3]/2 - Camera[1]], 
        self.chain_clip)
      
    Window.blit(Sprite_atlas, 
    [self.pos[0] - self.ring_clip[2]/2 - Camera[0],
     self.pos[1] - self.ring_clip[3]/2 - Camera[1]], 
    self.ring_clip)

def updateCollidables(level, checkpointEffects, player):
  checkpointEffects.colliding = False
  for collideable in level.collideables:
    type = collideable[0]
    match type:
      case "flip":
        #rect, pre_state, state
        obj = collideable[1]
        if collide_rects(player.rect, obj.rect):
          level.pixel_place_tile(obj.rect, obj.tile+1, obj.layer)
        else:
          level.pixel_place_tile(obj.rect, obj.tile, obj.layer)
      case "pressure_plate":
        #rect, action group
        obj = collideable[1]
        if collide_rects(player.rect, obj.rect):
          activateGroups += [obj.action_group]
      case "checkpoint":
        pos = collideable[1]
        
        
        if collide_point_in_rect(pos, player.rect):
          
          checkpointEffects.colliding = True
          level.checkpoint = round_to_topleft_of_tile(pos, level.tile_ize)

def updateInteractables(window, windowInput, camera, level : levelClass.Level, fade, player, hookshot : playerCode.Hookshot):
  for interactable in level.interactables:
    type = interactable[0]
    match type:
      case "door":
        obj = interactable[1]
        if controls.interact in windowInput.buttonsRisingEdge:
          if collide_rects(player.rect, obj.rect2):
            player.rect[0] = obj.rect1[0] + player.rect[2] / 2
            player.rect[1] = obj.rect1[1]
            player.pre_rect[0] = obj.rect1[0] + player.rect[2] / 2
            player.pre_rect[1] = obj.rect1[1]
            camera[0] += (player.rect[0]-window.dimOriginal[0]//2 - camera[0])
            camera[1] += (player.rect[1]-window.dimOriginal[1]//2 - camera[1])
            hookshot.enabled = False
            fade.playBack()
            fade.setTime(10)
          elif collide_rects(player.rect, obj.rect1):
            player.rect[0] = obj.rect2[0] + player.rect[2] / 2
            player.rect[1] = obj.rect2[1]
            player.pre_rect[0] = obj.rect2[0] + player.rect[2] / 2
            player.pre_rect[1] = obj.rect2[1]
            camera[0] += (player.rect[0]-window.dimOriginal[0]//2 - camera[0])
            camera[1] += (player.rect[1]-window.dimOriginal[1]//2 - camera[1])
            hookshot.enabled = False
            fade.playBack()
            fade.setTime(10)
      case "ladder":
        obj = interactable[1]
        if controls.up in windowInput.buttonsRisingEdge or controls.down in windowInput.buttonsRisingEdge:
          if collide_rects(player.rect, obj.rect):
            player.climbing = True
            if obj.data != "1":
              player.rect[0] = rect_centerx(obj.rect)-player.rect[2]/2+1
            player.vel[0] = 0
            player.vel[1] = 0
            ladderRect = obj.rect

def updateOnOffs(level : levelClass.Level):

  for obj in level.onoffs:
    if obj.time % obj.timer == 0:
      tiles = obj.stored.copy()
      for layer in range(obj.layer, 5):
        obj.stored[layer] = level.pixel_get_tile(obj.pos, layer)
        level.pixel_place_tile(obj.pos, tiles[layer], layer)
    obj.time += 1 

def updatePullChain(level : levelClass.Level, hookshot : playerCode.Hookshot):
  for pull_chain in level.pull_chains:
    pull_chain.pos = lerp2(pull_chain.origin, pull_chain.end, pull_chain.pull_percent)
    
    if not hookshot.enabled:
      pull_chain.pulling = False
    if pull_chain.pulling:
      hookshot.pos = pull_chain.pos.copy()
      pull_chain.pull_percent = min(pull_chain.pull_percent + 1 / pull_chain.pull_down_time,1)
    else:
      pull_chain.pull_percent = max(pull_chain.pull_percent - 1 / pull_chain.pull_up_time, 0)
    
    if pull_chain.pull_percent != 0 and pull_chain.pre_pull_percent == 0:
      activateGroups += [pull_chain.group]
    if pull_chain.pull_percent == 0 and pull_chain.pre_pull_percent != 0:
      activateGroups += [pull_chain.group]
    pull_chain.pre_pull_percent = pull_chain.pull_percent

def updateEntities(level : levelClass.Level, player : playerCode.Player, frame):
  for entity in level.entities:
        
        if "collision_activate" in entity.functions:
          if collide_rects(player.rect, entity.rect):
            activateGroups += [entity.action_group]
            entity.colliding = True
          else:
            entity.colliding = False 
        if "velocity" in entity.functions:
          entity.rect[0] += entity.vel[0]
          entity.rect[1] += entity.vel[1]
        if "move_to_player" in entity.functions:
          d = get_dist(rect_center(player.rect), rect_center(entity.rect))
          entity.vel[0] = (rect_centerx(player.rect) - rect_centerx(entity.rect)) / d * 2
          entity.vel[1] = (rect_centery(player.rect) - rect_centery(entity.rect)-4) / d * 2
        if "slowed_by_walls" in entity.functions:
          tile = level.get_tile(convert_to_tile_coords(rect_center(entity.rect), level.tileSize))
          if tile != 0:
            entity.vel[0] *= 0.2
            entity.vel[1] *= 0.2
        if "slowed_by_darkness" in entity.functions:
          if not player.light_on:
            entity.vel[0] *= 0.2
            entity.vel[1] *= 0.2
        if "random_slowness" in entity.functions:
          entity.vel[0] *= 0.75-math.sin(2*math.pi*frame/30)/4
          entity.vel[1] *= 0.75-math.sin(2*math.pi*frame/30)/4

def updateNpcs(player : playerCode.Player, level : levelClass.Level, windowInput):
  for npc in level.npcs:
    npc.colliding_with_player = collide_rects(player.rect, npc.rect)
    if npc.colliding_with_player and controls.interact in windowInput.buttonsRisingEdge:
      gameState = "text_box"

def updateActionGroups(level : levelClass.Level, activateGroups, sounds):
  for group in activateGroups:
    if group!="none":
      for action in level.action_groups[group]:
        topleft   = action[0]
        botright  = action[1]
        type      = action[2]
        data      = action[3]
        layer     = action[4]
        match type:
          case "place":
            level.pixel_place_tile(topleft, int(data), layer)
            sounds.Moved.play()
          case "flip_all":
            if data == "":
              action[3] = [0,0,0,0,0,0]
            for i in range(layer, 5):
              tile = level.pixel_get_tile(topleft, i)
              level.pixel_place_tile(topleft, action[3][i], i)
              action[3][i] = tile
  activateGroups = []

def updateBosses(level : levelClass.Level, player : playerCode.Player, sounds, frame):
  for thing in level.bosses:
    type = thing[0]
    boss = thing[1]
    match type:
      case "armorer":
        
        #region armorer body
        d = get_dist(boss.rect, boss.movement_point[boss.movement_point_index])
        if d <= 4: 
          boss.movement_point_index = (boss.movement_point_index+1) % 3
        boss.movement_target = boss.movement_point[boss.movement_point_index]
        boss.rect[0] += boss.vel[0]
        boss.rect[1] += boss.vel[1]
        
        direction = normalize([boss.movement_target[0] - boss.rect[0], boss.movement_target[1] - boss.rect[1]])
        boss.vel[0] = direction[0] * 1
        boss.vel[1] = direction[1] * 1
        #endregion
        
        #region armorer sword
        
        boss.sword_pos[0] += boss.sword_vel[0]
        boss.sword_pos[1] += boss.sword_vel[1]
        
        if boss.sword_state != "swiping":
          boss.sword_swipe_charge_timer -= 1
          if boss.sword_swipe_charge_timer == 0:
            boss.sword_swipe_charge_timer = boss.sword_swipe_charge_time
            boss.sword_state = "swiping"
            boss.sword_targets = []
            boss.sword_targets = boss.sword_points[:]
            random.shuffle(boss.sword_targets)
            boss.sword_targets = [boss.rect[:2]] + boss.sword_targets
            
        if len(boss.sword_targets) == 0 and boss.sword_state == "swiping":
            boss.sword_state = "floating"
        if boss.sword_state == "swiping" and len(boss.sword_targets)!=0:
          
          boss.sword_angle = frame / 60 * 360 * 10
          
          boss.sword_vel = multiply_vec(get_direction(boss.sword_pos, boss.sword_targets[0]), boss.sword_speed/2)
          
          d = get_dist(boss.sword_pos, boss.sword_targets[0])
          if d <= 4:
            boss.sword_targets.pop(0)
            
        
        
        if boss.sword_state == "back":
          boss.sword_vel = [-math.cos(math.radians(boss.sword_angle))*2, -math.sin(math.radians(boss.sword_angle))*2]
          boss.sword_back_timer -= 1
          if boss.sword_back_timer == 0:
            sounds.Ping_sound.play()
            boss.sword_back_timer = boss.sword_back_time
            boss.sword_state = "dashing"
            
            #boss.sword_vel = multiply_vec(get_direction(boss.sword_pos, rect_center(Player.rect)), boss.sword_speed)
            boss.sword_vel = [math.cos(math.radians(boss.sword_angle))*boss.sword_speed, math.sin(math.radians(boss.sword_angle))*boss.sword_speed]
        
        if boss.sword_state == "stuck":
          if (boss.sword_stuck_timer % (boss.sword_stuck_timer//8+1))==0:
            boss.sword_offset = [random.randrange(-2, 2), random.randrange(-2, 2)]
          
          boss.sword_stuck_timer -= 1
          if boss.sword_stuck_timer <= 0:
            boss.sword_offset = [0,0]
            boss.sword_stuck_timer = 0
            boss.sword_state = "floating"
            
        
        if boss.sword_state == "dashing":
          d = get_dist(rect_center(player.rect), add_pos(boss.sword_pos, [math.cos(math.radians(boss.sword_angle))*15, math.sin(math.radians(boss.sword_angle))*15]))
          if d <= 8:
            player.dead = True
            player.dead_timer = player.dead_time
            player.vel[0] = -playerCode.getPlayerFacing(player)*10
            player.vel[1] = -5
          
          tile = level.pixel_get_tile(add_pos(boss.sword_pos, [math.cos(math.radians(boss.sword_angle))*15, math.sin(math.radians(boss.sword_angle))*15]))
          if tile != 0:
            boss.sword_vel = [0,0]
            boss.sword_stuck_timer = boss.sword_stuck_time
            boss.sword_state = "stuck"
          
          boss.sword_dash_timer -= 1
          if boss.sword_dash_timer <= 0:
            boss.sword_dash_timer = boss.sword_dash_time
            boss.sword_state = "floating"
          
            
        
        #if boss.sword_state == "charging":
        #  boss.sword_charge_timer -= 1
        if boss.sword_charge_timer <= 0:
            boss.sword_charge_timer = boss.sword_charge_time
            boss.sword_state = "back"
            a = angle_to(rect_center(player.rect), boss.sword_pos)
            boss.sword_angle = a
        
        if boss.sword_state == "floating":
          d = get_dist(rect_center(player.rect), boss.sword_pos)
          if d > 32:
            boss.sword_vel = multiply_vec(get_direction(boss.sword_pos, rect_center(player.rect)), 1)
            boss.sword_charge_timer = boss.sword_charge_time
          else:
            boss.sword_vel = [0,0]
            boss.sword_charge_timer = countdownTimer(boss.sword_charge_timer)
        
          if boss.sword_state != "back":
            boss.sword_angle = 90 + boss.sword_vel[0]*4 + math.sin(2*3.14/60*frame)*10
          
          d = get_dist(boss.sword_pos, rect_center(player.rect))
          if d <= 48:
            boss.sword_angle += frame/60*360*4
        
        #endregion
        
        #region armorer spear
        tile = level.pixel_get_tile(add_pos(boss.spear_pos, [math.cos(math.radians(boss.spear_angle))*15, math.sin(math.radians(boss.spear_angle))*15]))
        if tile != 0 and boss.spear_state != "stuck":
          boss.spear_vel = [0,0]
          boss.spear_stuck_timer = boss.spear_stuck_time
          boss.spear_state = "stuck"
        
        if boss.spear_stuck_timer != 0:
          boss.spear_stuck_timer -= 1
          if boss.spear_stuck_timer % (boss.spear_stuck_timer//8+1)==0:
            boss.spear_offset = [random.randrange(-2, 2), random.randrange(-2, 2)]
        elif boss.spear_state == "stuck":
          boss.spear_offset = [0,0]
          boss.spear_state = "return"
          boss.spear_return_timer = boss.spear_return_time
        
        if boss.spear_state == "return":
          d = get_dist(rect_center(player.rect), boss.spear_pos)
          a = angle_to(rect_center(player.rect), boss.spear_pos)
          boss.spear_angle = a
          target = add_pos(rect_center(boss.rect), [math.cos(math.radians(a))*32, math.sin(math.radians(a))*16])
          boss.spear_pos[0] -= (boss.spear_pos[0] - target[0])/10
          boss.spear_pos[1] -= (boss.spear_pos[1] - target[1])/10
          boss.spear_return_timer = countdownTimer(boss.spear_return_timer)
          if boss.spear_return_timer == 0:
            boss.spear_state = "back"
            boss.spear_back_timer = boss.spear_back_time
        
        if boss.spear_state == "back":
          d = get_dist(rect_center(player.rect), boss.spear_pos)
          a = angle_to(rect_center(player.rect), boss.spear_pos)
          boss.spear_angle = a
          target = add_pos(rect_center(boss.rect), [-math.cos(math.radians(a))*32, -math.sin(math.radians(a))*16])
          boss.spear_pos[0] -= (boss.spear_pos[0] - target[0])/10
          boss.spear_pos[1] -= (boss.spear_pos[1] - target[1])/10
          boss.spear_back_timer = countdownTimer(boss.spear_back_timer)
          if boss.spear_back_timer == 0:
            sounds.Test.play()
            boss.spear_state = "throwing"
            boss.spear_throw_timer = 0
          
        
        boss.spear_pos[0] += boss.spear_vel[0]
        boss.spear_pos[1] += boss.spear_vel[1]
        if boss.spear_state == "throwing":
          
          d = get_dist(rect_center(player.rect), add_pos(boss.spear_pos, [math.cos(math.radians(boss.spear_angle))*15, math.sin(math.radians(boss.spear_angle))*15]))
          if d <= 8:
            player.dead = True
            player.dead_timer = player.dead_time
            player.vel[0] = -playerCode.getPlayerFacing(player)*10
            player.vel[1] = -5
          if boss.spear_throw_timer == 0:
            boss.spear_pos = boss.rect[0:2]
            d = get_dist(rect_center(player.rect), boss.spear_pos)
            a = angle_to(add_pos(rect_center(player.rect), multiply_vec(player.vel, d/boss.spear_speed*0.8)), boss.spear_pos)
            boss.spear_angle = a
            boss.spear_throw_timer = boss.spear_throw_time
            
            boss.spear_vel[0] = math.cos(boss.spear_angle/360*6.28)*boss.spear_speed
            boss.spear_vel[1] = math.sin(boss.spear_angle/360*6.28)*boss.spear_speed
        
          boss.spear_throw_timer = countdownTimer(boss.spear_throw_timer)
        #endregion


