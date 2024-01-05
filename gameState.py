from playerCode import Player
from mathFunctions import countdownTimer

class gameState():
  def __init__(self):
    self.state = "main_menu"
    self.died = False
  def didPlayerDie(self):
    died = self.died
    self.died = False
    return died
  def updateGameState(self, player: Player):
    if player.dead:
      player.dead_timer = countdownTimer(player.dead_timer)
      if player.dead_timer == 0:
        self.state = "dead"
        self.died = False
        