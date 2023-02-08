import pymunk

class Goopie:
    MASS = 1
    RADIUS = 30
    def __init__(self, shape: pymunk.Shape) -> None:
        self.shape = shape
        self.sprite = None
    
    def get_position(self):
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite