import pymunk
import numpy as np

class Food:
    MASS = 1
    RADIUS = 10
    COLLISION_TYPE = 2
    def __init__(self, x: float = None, y:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> None:
        moment = pymunk.moment_for_circle(self.MASS, 0, self.RADIUS)          
        circle_body = pymunk.Body(self.MASS, moment)  
        if x is None:
            x = generator.uniform(-generation_range, generation_range)
        if y is None:
            y = generator.uniform(-generation_range, generation_range)
        circle_body.position = x, y
        circle_body.velocity = 0, 0
        circle_shape = pymunk.Circle(circle_body, self.RADIUS)
        circle_shape.elasticity = 0.8
        circle_shape.friction = 1.0
        circle_shape.collision_type = self.COLLISION_TYPE
        circle_shape.food = self
        self.shape = circle_shape
        self.sprite = None
        self.amount = 0.1
    
    def get_position(self) -> pymunk.Vec2d:
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite