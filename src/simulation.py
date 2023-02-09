import pymunk
from goopie import Goopie
from food import Food
import numpy as np
import math

class Simulation:
    def __init__(self, num_goopies, num_food, space_size, test: bool = False) -> None:
        super().__init__()
        # create all the goopies, food and walls together with pymunk objects for everything
        self.space_size = space_size
        self.test = test
        self.generator = np.random.default_rng()
        self.space: pymunk.Space = pymunk.Space()
        collision_handler = self.space.add_collision_handler(Goopie.COLLISION_TYPE, Food.COLLISION_TYPE)
        collision_handler.begin = self.goopie_food_collision
        
        self.create_walls()

        self.goopies :list[Goopie] = []
        for _ in range(num_goopies):
            if test:
                goopie = Goopie(0, 0, math.pi/4)
            else:
                goopie = Goopie(generation_range=space_size * 0.8)
            self.space.add(goopie.shape.body, goopie.shape)
            self.goopies.append(goopie)
        
        self.foods :list[Food] = []
        for _ in range(num_food):
            if test:
                food = Food(50, 50)
            else:
                food = Food(generation_range=space_size * 0.9)
            self.space.add(food.shape.body, food.shape)
            self.foods.append(food)

    def goopie_food_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        food:Food = arbiter.shapes[1].food
        if food in self.foods:
            if goopie.eat(food):
                self.remove_food(food)
        return False
    
    def create_walls(self):
        self.walls = [
            pymunk.Segment(self.space.static_body, (self.space_size, self.space_size), (self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (self.space_size, -self.space_size), (-self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, -self.space_size), (-self.space_size, self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, self.space_size), (self.space_size, self.space_size), 10)
        ]
        if self.test:
            self.walls.append(pymunk.Segment(self.space.static_body, (130, 90), (200, 0), 10))

        for wall in self.walls:
            wall.elasticity = 0.8
            wall.friction = 1.0
            self.space.add(wall)

    def remove_goopie(self, goopie: Goopie):
        self.goopies.remove(goopie)
        self.space.remove(goopie.shape.body)
        self.space.remove(goopie.shape)
        if goopie.sprite is not None:
            goopie.sprite.kill()

    def remove_food(self, food: Food):
        self.foods.remove(food)
        self.space.remove(food.shape.body)
        self.space.remove(food.shape)
        if food.sprite is not None:
            food.sprite.kill()

    def step(self):
        dt = 0.01

        self.space.step(dt)
        for goopie in self.goopies:
            goopie.step(dt)
            if not goopie.is_alive():
                self.remove_goopie(goopie)
        
    def run(self, headless: bool = False):
        from window import GameWindow
        update_rate = 1e-5 if headless else 1/60
        self.window = GameWindow(self, update_rate)
        self.window.run()