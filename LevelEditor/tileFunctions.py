
def get_collision_clip(tile_size, tile_id, collision_atlas):
    return [tile_id % (collision_atlas.get_width() // tile_size) * tile_size, tile_id // (collision_atlas.get_width() // tile_size) * tile_size, tile_size, tile_size]

class COLLISION_RECTS:
  tile_size = 16
  collision_tile_colors = [(0,0,0), (255,255,255), (255,255,255), (255,255,255), (255,255,255), (255,255,255), (255, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (127, 127, 127), (255, 0, 255)]
