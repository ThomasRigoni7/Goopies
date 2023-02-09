import pymunk
import math
import numpy as np
from food import Food
import time

class Goopie:
    MASS = 0.05
    RADIUS = 30
    COLLISION_TYPE = 1
    def __init__(self, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> None:
        
        self.shape = self.create_shape(x, y, angle, generation_range, generator)
        self.sprite = None

        self.energy = 1
        self.alive = True
        self.max_turn = 0.05
        self.max_acceleration = 20
        self.max_speed = 200
    
    def create_shape(self, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> pymunk.Circle:
        moment = pymunk.moment_for_circle(self.MASS, 0, self.RADIUS)          
        circle_body = pymunk.Body(self.MASS, moment)  
        if x is None:
            x = generator.uniform(-generation_range, generation_range)
        if y is None:
            y = generator.uniform(-generation_range, generation_range)
        circle_body.position = x, y
        circle_body.velocity = 0, 0
        circle_body.velocity_func = self.limit_velocity
        if angle is not None:
            circle_body.angle = angle
        else:
            circle_body.angle = generator.uniform(-math.pi, math.pi)
        circle_shape = pymunk.Circle(circle_body, self.RADIUS)
        circle_shape.elasticity = 0.4
        circle_shape.friction = 1.0
        circle_shape.collision_type = self.COLLISION_TYPE
        circle_shape.goopie = self
        return circle_shape

    def limit_velocity(self, body: pymunk.Body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        body.angular_velocity = 0
        if body.velocity.length > self.max_speed:
            scale = self.max_speed / body.velocity.length
            body.velocity *= scale

    def get_position(self):
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite

    def eat(self, food: Food) -> bool:
        """
        The goopie is colliding with food, does it eat it? What happens?
        Returns True if the goopie eats the food, False otherwise.
        """
        self.energy += food.amount
        return True

    def is_alive(self):
        return self.alive

    def step(self, dt: float):
        self.energy -= 0.1*dt
        if self.energy <= 0:
            self.alive = False

        # make the goopie move
        self.movement_step(1, 1)


    def movement_step(self, turn: float, acceleration: float):
        """
        Updates the goopies velocity and angle based on its acceleration. Velocity will always be in the front, never laterally.
        """
        angle = self.shape.body.angle
        angle += self.max_turn * turn
        speed = self.shape.body.velocity.length
        
        velocity = speed * math.cos(angle), speed * math.sin(angle)
        self.shape.body.angle = angle
        self.shape.body.velocity = velocity

        

        self.shape.body.apply_force_at_local_point((acceleration * self.max_acceleration, 0), (0,0))

