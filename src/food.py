import pymunk

class Food:
    def __init__(self, shape: pymunk.Shape) -> None:
        self.shape = shape

    def get_position(self):
        return self.shape.body.position