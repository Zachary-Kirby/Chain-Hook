#I use a system of comments to breakup the code into somthing more manageable while staying more freeform
#of course the downside is that every now and then I might need to reevaluate what needs to be done

#tags are

#CURRENT

#I also use regions a lot (they cut up the code into collapesable regions)

import pygame as pg
import pygame.freetype as freetype
from sys import exit

import math
import time
import random
from levelObjects   import *
from mathFunctions  import *
from rectFunctions  import *
from fileHandler    import *
from text           import *
from levelClass     import *
from window         import *
from playerCode     import *
import controls
import os

class Fade():
  def __init__(self, time, variant = 0):
    #fading just means that there is a transition to black
    self.time = time
    self.timer = self.time
    self.play_direction = 1
    self.bounce = 0
    self.variant = variant
  def playForward(self):
    self.play_direction = 1
  def playBackward(self):
    self.play_direction = -1
  def playBounce(self):
    self.bounce += 2
  def playBack(self):
    #plays from dark to light
    self.timer = 0
    self.play_direction = 1
  def playStart(self):
    #plays from light to dark
    self.timer = self.time
    self.play_direction = -1
  def setTime(self, time):
    self.time = time
    self.timer = min(self.timer, time)
  def draw(self, window, window_dim):
    if self.timer != self.time:
      if self.variant == 0:
        s = self.timer / self.time
        window.fill((255*s,255*s,255*s), special_flags = pg.BLEND_RGB_MULT)
    self.timer = min(max(self.timer + self.play_direction, 0), self.time)
    if self.bounce > 0:
      if self.play_direction == 1:
        if self.timer == self.time:
          self.play_direction = -self.play_direction
          self.bounce -= 1
      else:
        if self.timer == 0:
          self.play_direction = -self.play_direction
          self.bounce -= 1
    
class CheckpointLightBeam():
  def __init__(self):
    self.pos = [0,0]
    self.color = [64,128,64]
    self.width = 16
    self.timer = 0
    self.time = 20
  def draw(self, display, Camera):
    percent = self.timer/self.time
    self.timer -= 1
    display.fill(self.color, [self.pos[0]-self.width/2*percent-Camera[0], self.pos[1]-200*percent-Camera[1], self.width/2*percent*percent, 400*percent], pg.BLEND_RGB_ADD)

def actionGetInfo(action):
  return int(action[2])

def HSV(hue, saturation, value):
  #hue goes from 0 to 360
  #saturation goes from 0 to 1
  #value goes from 0 to  1
  PI = math.pi
  TAU = math.tau
  x = hue / 360
  #hue of 0 is red. hue of 180 is light blue
  #saturation is a interpolation between color to max component for all
  #value is a interpolation between color to black
  step = TAU/3
  color = (math.cos(TAU*x)*127+127, math.cos(TAU*x+step)*127+127, math.cos(TAU*x+step*2)*127+127)
  maxValue = max(color)
  color = (
    lerp(maxValue, color[0], saturation),
    lerp(maxValue, color[1], saturation),
    lerp(maxValue, color[2], saturation))
  color = (
    lerp(0, color[0], value),
    lerp(0, color[1], value),
    lerp(0, color[2], value))
  return color

class Sounds():
  def __init__(self):
    pg.mixer.init()
    self.Noise = pg.mixer.Sound("Sound_Effects/noise.ogg")
    self.Noise.set_volume(0.2)
    self.Step = pg.mixer.Sound("Sound_Effects/step.ogg")
    self.Step.set_volume(0.2)
    self.Jump = self.Step
    self.Moved = pg.mixer.Sound("Sound_Effects/moved.ogg")
    self.Moved.set_volume(0.01)
    self.Hookshot = pg.mixer.Sound("Sound_Effects/Hookshot.ogg")
    self.Hookshot.set_volume(0.04)
    self.Hookshot_shoot = pg.mixer.Sound("Sound_Effects/Hookshot_shoot.ogg")
    self.Hookshot_shoot.set_volume(0.02)
    self.Test = pg.mixer.Sound("Sound_Effects/test_noise.ogg")
    self.Test.set_volume(0.2)
    self.Ping = pg.mixer.Sound("Sound_Effects/ping.ogg")
    self.Ping.set_volume(0.04)
    self.Pickup = pg.mixer.Sound("Sound_Effects/pickup.ogg")
    self.Pickup.set_volume(0.2)
    self.Checkpoint = pg.mixer.Sound("Sound_Effects/Checkpoint.ogg")

class CheckpointEffects():
  def __init__(self):
    self.lightBeam = CheckpointLightBeam()
    self.preColliding = False
    self.colliding = False

class DeathScreen():
  def __init__(self):
    self.timer = 0
    self.time = 10 #TODO stop relying on frame timers #this line landed on the devils number at one point (line number was that)

class MainMenu():
  def __init__(self):
    self.background = pg.image.load("Graphics/main_menu.png")
    self.play_button_rect = pg.Rect([16 * 11, 16 * 10, 16 * 3, 16 * 1])
    self.quit_button_rect = pg.Rect([16 * 11, 16 * 12, 16 * 3, 16 * 1])

def main():
  
  Debug = 1
  
  window = Window(640, 360)
  Font_small = my_font_class()
  
  spriteAtlas = pg.image.load("Graphics/sprite_sheet.bmp").convert()
  spriteAtlas.set_colorkey((0,0,0))
  tileAtlas = pg.image.load("Graphics/tile_atlas.png").convert_alpha()
  level = Level()
  loadLevel(level, window.dimOriginal, tileAtlas, "Levels/Level0.level")
  level_last_accessed = os.path.getmtime(level.reloadInfo[1])
  
  hookshot = Hookshot([0,0])
  player = Player([level.checkpoint[0], level.checkpoint[1], 8,12])
  camera = [0,0]
  ladderRect = [0,0,0,0]
  activateGroups = []
  
  npcDialogue = load("Data/npc_dialogue.json")
  npcDefs     = load("Data/npc_defs.json")
  signTexts   = load("Data/signs.json")
  
  sounds = Sounds()
  clock = pg.time.Clock()
  window_input = WindowInput()
  
  checkpointEffects = CheckpointEffects()
  fade = Fade(60, 0)
  deathScreen = DeathScreen()
  mainMenu = MainMenu()
  
  scale = 1
  exit = 0
  frame = 0
  gameState = "main_menu"
  
  airParticles = [[Vector2(random.randint(0, window.dimOriginal[0]), random.randint(0, window.dimOriginal[1])), Vector2(0,0), random.randint(1, 100)] for n in range(100)]
  Wind = [1, 0]
  cancel_vel = [0,0]
  
  while exit == 0:
    
    window_input.update(scale)
    exit = window_input.exit
    
    if pg.K_LALT in window_input.buttons and pg.K_r in window_input.buttonsRisingEdge:
      level.reload()
    
    if os.path.getmtime(level.reloadInfo[1])-level_last_accessed > 1:
      level_last_accessed = os.path.getmtime(level.reloadInfo[1])
      level.reload()
      print(level_last_accessed)
    
    if gameState == "playing":
      
      updateActionGroups(level, activateGroups, sounds)
      updateCollidables(level, checkpointEffects, player)
      updateInteractables(window, window_input, camera, level, fade, player, hookshot)
      updateOnOffs(level)
      updatePullChain(level, hookshot)
      updateEntities(level, player, frame)
      updateNpcs(player, level, window_input)
      updateBosses(level, player, sounds, frame)
      
      #region player logic
      playerState(player, deathScreen, ladderRect)
      playerInput(player, hookshot, window_input, camera, sounds, level, Debug)
      playerGravity(player, hookshot)
      if (player.grounded != 0 ) or (not hookshot.hooked) or not hookshot.enabled:
        if player.grounded and not (controls.left in window_input.buttons or controls.right in window_input.buttons):
          player.vel[0] -= max(min(player.vel[0], 0.2), -0.2)
      playerCollision(player, hookshot, level, window_input, fade)
      if player.dead:
        gameState = "dead"
      
      #endregion player logic
      
      #region sounds
      if abs(player.vel[0]) > 0.5 and player.grounded and player.frame == 1:
        sounds.Step.play()
      
      if hookshot.hooked and hookshot.enabled:
        sounds.Hookshot.stop()
      elif not hookshot.enabled:
        sounds.Hookshot.stop()
      
      if hookshot.enabled and not hookshot.pre_enabled:
        sounds.Hookshot_shoot.play()
        sounds.Hookshot.play(-1, fade_ms=100)
      
      #endregion sounds
      
      #region Pickups
      for pickup in level.pickups:
        if pickup.type == "red_gem_bubble":
          pickup.offset[1] = math.sin(frame*6.28/60) * 2
          if collide_rects(player.rect, pickup.rect):
            level.pickups.remove(pickup)
            sounds.Pickup.play()
            gameState = "main_menu"
      #endregion
      
      #region HookshotLogic
      hookshot.hooked = False
      hookshot_step_count = 320
      for step in range(hookshot_step_count):
        if hookshot.enabled == 1:
          
          if hookshot.hooked == False:
            hookshot.start_pos = player.rect[:2]
          
          hookshot.player_pos = player.rect[:2]
          hookshot.pos[0] += hookshot.vel[0] / hookshot_step_count
          hookshot.pos[1] += hookshot.vel[1] / hookshot_step_count
          tile_pos = convert_to_tile_coords(hookshot.pos, level.tileSize)      
          
          if point_in_rect(tile_pos, [0,0,level.metaPixelW-1,level.metaPixelH-1]): # is it in the level
            
            tile = level.get_tile(tile_pos) #TODO get the tile from a collison tile grid
            d = get_dist(hookshot.pos, rect_center(player.rect))
            if tile in COLLISION_TYPES.BREAKS_HOOKSHOT: hookshot.enabled = False
            
            if hookshot.pre_hooked == False:
                    hookshot.len = get_dist(hookshot.start_pos, hookshot.pos)+2
                    
            
            if tile not in COLLISION_TYPES.NOT_HOOKSHOTABLE:
              
              hookshot.hooked = True
              if hookshot.pre_hooked == False:
                
                sounds.Noise.set_volume(0.1)
                sounds.Noise.play()
              hookshot.len = max(min(hookshot.len, hookshot.max_len), hookshot.min_len)
              hookshot.vel = [0,0]
            else:
              for pull_chain in level.pull_chains:
                if get_dist(hookshot.pos, pull_chain.pos) <= 8:
                  
                  hookshot.pos = pull_chain.pos.copy()
                  hookshot.hooked = True
                  hookshot.len = max(min(hookshot.len, hookshot.max_len), hookshot.min_len)
                  hookshot.vel=[0,0]
                  pull_chain.pulling = True
            
            if hookshot.enabled and hookshot.hooked:
              if d >= hookshot.len:
                  player.rect[0] = hookshot.pos[0]+(rect_centerx(player.rect)-hookshot.pos[0])/d*hookshot.len-player.rect[2]/2
                  player.rect[1] = hookshot.pos[1]+(rect_centery(player.rect)-hookshot.pos[1])/d*hookshot.len-player.rect[3]/2
                  #6[0] += -(Player.rect[0]-Hookshot.pos[0])/d*min((d-Hookshot.len), Tile_size-1) #velocity limited version
                  #Player.vel[1] += -(Player.rect[1]-Hookshot.pos[1])/d*min((d-Hookshot.len), Tile_size-1) #
                  
                  #there are two versions of the hookshot physics here
                  #one relies on real physics, one relies on the a estamate
                  hk = pg.Vector2(sub_pos(rect_center(player.rect), hookshot.pos)).normalize()
                  speed = pg.Vector2(player.vel)
                  dot = hk.dot(speed)
                  
                  cancel_vel = -hk[0]*dot, -hk[1]*dot
                  #cancel_vel = -(Player.rect[0]-Hookshot.pos[0])/d*(d-Hookshot.len), -(Player.rect[1]-Hookshot.pos[1])/d*(d-Hookshot.len)
                  player.vel[0] += cancel_vel[0]
                  player.vel[1] += cancel_vel[1]
              
            
          else:
            hookshot.hooked = False
          
          
          
          
          d = get_dist(hookshot.pos, rect_center(player.rect))
          if d > hookshot.max_len+2:
            hookshot.enabled = 0
            hookshot.len = 0
        else:
          hookshot.hooked = False
          
        if hookshot.hooked == False and hookshot.pre_hooked == True:
          hookshot.enabled = False
        hookshot.pre_hooked = hookshot.hooked
        
        hookshot.pre_enabled = hookshot.enabled
      #endregion
      
      #region Hookshot player collision cleanup
      if hookshot.enabled:
        tile_topleft  = convert_to_tile_coords(rect_topleft (player.rect), level.tileSize)
        tile_botright = convert_to_tile_coords(rect_botright(player.rect), level.tileSize)
        
        Level_collision = getTileCollision(tile_topleft, tile_botright, level, 1)
        
        pushed, col_types = physicsMove(player.rect, player.pre_rect, Level_collision, 'x', level, output_collision_type=True) #this could be interesting
        
        player.vel = stopVel(pushed, player.vel, 'x')
        
        tile_topleft  = convert_to_tile_coords(rect_topleft (player.rect), level.tileSize)
        tile_botright = convert_to_tile_coords(rect_botright(player.rect), level.tileSize)
        no_collision = [0]
        if player.climbing:
          no_collision += [2]
        Level_collision = getTileCollision(tile_topleft, tile_botright, level, 1, no_collision=no_collision)
        
        pushed, col_types = physicsMove(player.rect, player.pre_rect, Level_collision, 'y', level, output_collision_type=True)
        
        player.vel = stopVel(pushed, player.vel, 'y')
        
        player.pre_rect = player.rect.copy()
      #endregion
      
      #region CameraLogic
      Look_offset = (window_input.mouseEvent.pos[0]-window.dimOriginal[0]/2)/4, (window_input.mouseEvent.pos[1]-window.dimOriginal[1]/2)/4
      Camera_target = add_pos(sub_pos(rect_center(player.rect), [window.dimOriginal[0]//2, window.dimOriginal[1]//2]),Look_offset)
      for zone in level.camera_zones:
        if collide_rects(player.rect, zone.rect):
          if zone.type == "center":
            Camera_target[0] = rect_centerx(zone.rect) - window.dimOriginal[0]//2
            Camera_target[1] = rect_centery(zone.rect) - window.dimOriginal[1]//2
      
      camera[0] += (Camera_target[0] - camera[0])//2
      camera[1] += (Camera_target[1] - camera[1])//2
      camera[0] = max(camera[0],0)
      camera[1] = max(camera[1],0)
      
      
      
      #endregion
      
      #region Draw logic
      
      if checkpointEffects.colliding and not preCollidingWithCheckpoint:
        if checkpointEffects.LightBeam.pos != add_pos(level.checkpoint, [level.tileSize/1.5, level.tileSize/2]):
          sounds.Checkpoint.play()
          checkpointEffects.LightBeam.pos = add_pos(level.checkpoint, [level.tileSize/1.5, level.tileSize/2])
          checkpointEffects.LightBeam.timer = checkpointEffects.LightBeam.time
      preCollidingWithCheckpoint = checkpointEffects.colliding
      
      level.animate_tiles(frame)
      #endregion
      
      #region Draw
      
      
      for y in range(window.dimOriginal[1]):
        backColor = HSV(
          lerp(140, 160, y/window.dimOriginal[1]), 
          lerp(1, 0.7, y/window.dimOriginal[1]), 
          1)#lerp(0.3, 1,1-(1-y/Window_dim[1])**5))
        window.display.fill(backColor, [0, y, window.dimOriginal[0], 1])
      
      
      
      for sky in level.sky_areas:
        pg.draw.rect(window.display, (32, 100, 255), [sky[0]-camera[0], sky[1]-camera[1], sky[2], sky[3]])
      
      level.draw(window.display, camera, layer=0, draw_dark=True)
      
      for pull_chain in level.pull_chains:
        pull_chain.draw(window.display, spriteAtlas, camera)
      
      level.draw(window.display, camera, layer=1)
      hookshot.draw(window.display, spriteAtlas, camera, rect_center(player.rect))
      checkpointEffects.lightBeam.draw(window.display, camera)
      for entity in level.entities:
        entity.draw(window.display, spriteAtlas, camera)
      for obj in level.npcs:
        obj.draw(window.display, spriteAtlas, npcDefs, camera)
      for boss in level.bosses:
        boss = boss[1]
        boss.draw(window.display, spriteAtlas, camera)
      for pickup in level.pickups:
        pickup.draw(window.display, spriteAtlas, camera)
      player.draw(window.display, spriteAtlas, camera)
      level.draw(window.display, camera, layer=2)
      level.draw(window.display, camera, layer=3)
      
      r = random.randint(-10, 10)
      Wind = complex_multiply(Wind, [math.cos(math.radians(r)), math.sin(math.radians(r))])
      
      for particle in airParticles:
        particle[1].x += Wind[0]/5000
        particle[1].y += Wind[1]/5000
        particle[1].x *= 0.999
        particle[1].y *= 0.999
        particle[0].add(particle[1])
        window.display.fill((32+16*math.sin(3.14*2/60*(frame+particle[2])), 32+16*math.sin(3.14*2/60*(frame+particle[2])), 32+16*math.sin(3.14*2/60*(frame+particle[2]))), ((particle[0].x*particle[2]/10-camera[0]) % window.dimOriginal[0], (particle[0].y*particle[2]/10-camera[1]) % window.dimOriginal[1], 1, 1), pg.BLEND_RGB_ADD)
      
      for sign in level.signs:
        if collide_rects([sign.pos[0], sign.pos[1], level.tileSize, level.tileSize], player.rect):
          pos = sub_pos(sign.pos,camera)
          pos[1] -= 32
          if frame % 2:
            sign.chars += 1
          draw_text(window.display, Font_small, pos, signTexts[sign.sign_name][0:min(sign.chars, len(signTexts[sign.sign_name]))])
        else:
          sign.chars = 0
      
      collidingRooms = []
      for room in level.rooms:
        if collide_rects(player.rect, room.rect):
          if room.room_id not in collidingRooms:
            collidingRooms += [room.room_id]
      
      for hide_id in collidingRooms:
        for hide in level.roomHides[hide_id]:
          
          pg.draw.rect(window.display, (0, 0, 0), [hide[0]-camera[0], hide[1]-camera[1], hide[2], hide[3]])
      
      
      
      fade.draw(window.display, window.dimOriginal)
      
      draw_text(window.display, Font_small, [100,100], "x:"+str(round(player.vel[0],2)))
      draw_text(window.display, Font_small, [100,100+8], "y:"+str(round(player.vel[1],2)))
      draw_text(window.display, Font_small, [40,0], str(round(frame/60,1)))
      
      pg.display.update()
      
      #endregion Draw
    
    elif gameState == "dead":
      if deathScreen.timer > 0:
        deathScreen.timer -= 1
      else:
        player.rect[0] = level.checkpoint[0]
        player.rect[1] = level.checkpoint[1]
        player.pre_rect = player.rect[:]
        hookshot.enabled = False
        player.dead = False
        player.vel = [0,0]
        camera[0] += (player.rect[0]-window.dimOriginal[0]//2 - camera[0])
        camera[1] += (player.rect[1]-window.dimOriginal[1]//2 - camera[1])
        gameState = "playing"
        fade.playForward()
      
      
      window.display.fill((0,0,0))
      
      pg.display.update()
      
    elif gameState == "main_menu":
      if window_input.mouseEvent.pressed[0] == 1 and window_input.mouseEvent.prePressed[0] == 0:
        if mainMenu.play_button_rect.collidepoint(window_input.mouseEvent.pos):
          gameState = "playing"
        if mainMenu.quit_button_rect.collidepoint(window_input.mouseEvent.pos):
          exit = True
      
      window.display.fill((0,0,0))
      window.display.blit(mainMenu.background, (0,0))
      
      pg.display.update()
    
    clock.tick(60)
    frame += 1

def Credits(display, Window_dim):
  pass

main()
pg.quit()
exit()