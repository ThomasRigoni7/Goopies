import pymunk
import math
import numpy as np
from food import Food

class Goopie:
    MASS = 1
    RADIUS = 30
    COLLISION_TYPE = 1
    def __init__(self, x: float = None, y:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> None:
        moment = pymunk.moment_for_circle(self.MASS, 0, self.RADIUS)          
        circle_body = pymunk.Body(self.MASS, moment)  
        if x is None:
            x = generator.uniform(-generation_range, generation_range)
        if y is None:
            y = generator.uniform(-generation_range, generation_range)
        circle_body.position = x, y
        circle_body.velocity = 0, 0
        circle_body.angle = generator.uniform(-math.pi, math.pi)
        circle_shape = pymunk.Circle(circle_body, self.RADIUS)
        circle_shape.elasticity = 0.8
        circle_shape.friction = 1.0
        circle_shape.collision_type = self.COLLISION_TYPE
        circle_shape.goopie = self
        self.shape = circle_shape
        self.sprite = None
        self.energy = 1
    
    def get_position(self):
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite

    def eat(self, food: Food):
        self.energy += food.amount
        food.delete()