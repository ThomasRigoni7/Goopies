import pymunk

class Food:
    MASS = 1
    RADIUS = 10
    def __init__(self, shape: pymunk.Shape) -> None:
        self.shape = shape

    def get_position(self):
        return self.shape.body.position