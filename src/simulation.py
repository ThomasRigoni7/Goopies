import pymunk
from goopie import Goopie
from food import Food
import numpy as np
import math


class Simulation:
    def __init__(self, num_goopies, num_food, space_size) -> None:
        super().__init__()
        # create all the goopies, food and walls together with pymunk objects for everything
        self.space_size = space_size
        self.generator = np.random.default_rng()
        self.space: pymunk.Space = pymunk.Space()
        
        self.create_walls()

        self.goopies :list[Goopie] = []
        for _ in range(num_goopies):
            circle_shape = self.create_random_circle_body(Goopie.MASS, Goopie.RADIUS)
            goopie = Goopie(circle_shape)
            self.goopies.append(goopie)
        
        self.foods :list[Food] = []
        for _ in range(num_food):
            circle_shape = self.create_random_circle_body(Food.MASS, Food.RADIUS)
            food = Food(circle_shape)
            self.foods.append(food)

    def create_walls(self):
        walls = [
            pymunk.Segment(self.space.static_body, (self.space_size, self.space_size), (self.space_size, -self.space_size), 2),
            pymunk.Segment(self.space.static_body, (self.space_size, -self.space_size), (-self.space_size, -self.space_size), 2),
            pymunk.Segment(self.space.static_body, (-self.space_size, -self.space_size), (-self.space_size, self.space_size), 2),
            pymunk.Segment(self.space.static_body, (-self.space_size, self.space_size), (self.space_size, self.space_size), 2)
        ]
        for wall in walls:
            wall.elasticity = 0.8
            wall.friction = 1.0
            self.space.add(wall)

    def create_random_circle_body(self, mass: float = 1.0, radius: float = 30.0):
        moment = pymunk.moment_for_circle(mass, 0, radius)          
        circle_body = pymunk.Body(mass, moment)  
        x = self.generator.uniform(-self.space_size*0.8, self.space_size*0.8)
        y = self.generator.uniform(-self.space_size*0.8, self.space_size*0.8)
        circle_body.position = x, y
        circle_body.velocity = 0, 0
        circle_body.angle = self.generator.uniform(-math.pi, math.pi)
        circle_shape = pymunk.Circle(circle_body, radius)
        circle_shape.elasticity = 0.8
        circle_shape.friction = 1.0
        self.space.add(circle_body, circle_shape)
        return circle_shape

    def step(self):
        self.space.step(0.01)
        

    def run(self, headless: bool = False):
        from window import GameWindow
        update_rate = 1e-5 if headless else 1/60
        self.window = GameWindow(self, update_rate)
        self.window.run()