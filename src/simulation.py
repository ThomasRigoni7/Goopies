import pymunk
from goopie import Goopie
from food import Food
import numpy as np


class Simulation:
    def __init__(self, num_goopies, num_food, space_size) -> None:
        super().__init__()
        # create all the goopies, food and walls together with pymunk objects for everything
        self.space_size = space_size
        self.generator = np.random.default_rng()
        self.space: pymunk.Space = pymunk.Space()
        collision_handler = self.space.add_collision_handler(Goopie.COLLISION_TYPE, Food.COLLISION_TYPE)
        collision_handler.begin = self.goopie_food_collision

        
        self.create_walls()

        self.goopies :list[Goopie] = []
        for _ in range(num_goopies):
            goopie = Goopie(generation_range=space_size * 0.8)
            self.space.add(goopie.shape.body, goopie.shape)
            self.goopies.append(goopie)
        
        self.foods :list[Food] = []
        for _ in range(num_food):
            food = Food(generation_range=space_size * 0.9)
            self.space.add(food.shape.body, food.shape)
            self.foods.append(food)

    def goopie_food_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        food:Food = arbiter.shapes[1].food
        print("FOOD!")
        if food in self.foods:
            goopie.eat(food)
            self.foods.remove(food)
        return False
    
    def create_walls(self):
        self.walls = [
            pymunk.Segment(self.space.static_body, (self.space_size, self.space_size), (self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (self.space_size, -self.space_size), (-self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, -self.space_size), (-self.space_size, self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, self.space_size), (self.space_size, self.space_size), 10)
        ]
        for wall in self.walls:
            wall.elasticity = 0.8
            wall.friction = 1.0
            self.space.add(wall)

    def step(self):
        self.space.step(0.01)
        

    def run(self, headless: bool = False):
        from window import GameWindow
        update_rate = 1e-5 if headless else 1/60
        self.window = GameWindow(self, update_rate)
        self.window.run()