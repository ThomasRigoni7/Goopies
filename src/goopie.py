import pymunk
import math
import numpy as np
from food import Food
import torch
from brain import Brain
from abc import ABC, abstractmethod
from vision import Vision, WideVision, ClosestVision
from brain import Brain, CNNBrain, NeatBrain

class Goopie(ABC):
    MASS = 0.05
    RADIUS = 30
    COLLISION_TYPE = 1
    def __init__(self, simulation, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> None:
        
        self.simulation = simulation
        self.create_shapes(x, y, angle, generation_range, generator)
        self.sprite = None
        self.vision_arc = None
        self.age = 0

        self.energy = 0.5
        self.alive = True
        self.max_turn = 1
        self.max_acceleration = 20
        self.max_speed = 200
        self.fitness: float = 0.0
        self.vision : Vision = None 
        self.brain : Brain = None
    
    def create_shapes(self, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()):
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
        shape = pymunk.Circle(circle_body, self.RADIUS)
        shape.elasticity = 0.4
        shape.friction = 1.0
        shape.collision_type = self.COLLISION_TYPE
        shape.goopie = self 
        self.shape = shape
        # create the vision shape
        vision_shape = pymunk.Circle(circle_body, Vision.VISION_RADIUS)
        vision_shape.collision_type = Vision.VISION_COLLISION_TYPE
        vision_shape.sensor = True
        vision_shape.goopie = self
        self.vision_shape = vision_shape

    def limit_velocity(self, body: pymunk.Body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        body.angular_velocity = 0
        if body.velocity.length > self.max_speed:
            scale = self.max_speed / body.velocity.length
            body.velocity *= scale

    def get_position(self) -> pymunk.Vec2d:
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite

    def eat(self, food: Food) -> bool:
        """
        The goopie is colliding with food, does it eat it? What happens?
        Returns True if the goopie eats the food, False otherwise.
        """
        amount = min(1 - self.energy, food.amount)
        self.energy += amount 
        self.fitness += amount
        print(self.energy)
        return True

    def is_alive(self):
        return self.alive

    def reset_vision(self):
        self.vision.reset()

    def update_vision(self, shape: pymunk.Shape, type: str):
        self.vision.update(shape, type)


    @abstractmethod
    def step(self, dt: float):
        """
        Abstract function that implements the logic for a step.

        Parameters
        ----------
        dt : float
            delta time
        """
        ...


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

    def mutate(self, mutation_prob: float, mutation_amount: float):
        self.brain.mutate(mutation_prob, mutation_amount)

    def save(self, path: str):
        # for now save only the brain
        torch.save(self.brain.state_dict(), path)

    @abstractmethod
    def reproduce(self):
        ...

class CNNGoopie(Goopie):

    def __init__(self, simulation,  x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()):
        super().__init__(simulation, x, y, angle, generation_range, generator)

        self.vision = WideVision(self)
        self.brain = CNNBrain(self.vision.VISION_BUFFER_WIDTH, 3).requires_grad_(False)
    
    def step(self, dt: float):
        self.energy -= 0.1*dt
        self.simulation.biomass += 0.1*dt
        self.age += dt
        if self.energy <= 0:
            self.alive = False

        # forward in the brain
        turn, accelerate = self.brain(self.vision.visual_buffer, self.energy, self.shape.body.velocity.length / self.max_speed)

        # make the goopie move
        self.movement_step(turn, accelerate)

    def reproduce(self):
        if self.age > 3 and self.energy > 0.8:
            print(self.energy)
            child = CNNGoopie(self.simulation, self.get_position().x, self.get_position().y)

            child.brain.load_state_dict(self.brain.state_dict())
            child.mutate(self.simulation.mutation_prob, self.simulation.mutation_amount)
            child.energy = 0.4
            self.energy -= 0.4
            return child
        return None
            

class NEATGoopie():
    pass